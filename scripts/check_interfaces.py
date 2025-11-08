#!/usr/bin/env python3
"""
Check Interface Contracts

This script verifies that interface contracts are properly implemented
and haven't been broken by recent changes.
"""

import ast
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table


console = Console()

PROJECT_ROOT = Path(__file__).parent.parent
INTERFACES_DIR = PROJECT_ROOT / "src" / "mia_rag" / "interfaces"


class InterfaceChecker(ast.NodeVisitor):
    """AST visitor to extract interface definitions."""

    def __init__(self):
        self.interfaces: dict[str, dict[str, list[str]]] = {}
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions to find ABC interfaces."""
        # Check if it's an ABC
        is_abc = any(
            (isinstance(base, ast.Name) and base.id == "ABC") or
            (isinstance(base, ast.Attribute) and base.attr == "ABC")
            for base in node.bases
        )

        if is_abc:
            self.current_class = node.name
            self.interfaces[node.name] = {
                "methods": [],
                "properties": [],
                "class_methods": []
            }

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions to extract interface methods."""
        if self.current_class:
            # Check if it's abstract
            is_abstract = any(
                isinstance(dec, ast.Name) and dec.id == "abstractmethod"
                for dec in node.decorator_list
            )

            if is_abstract:
                # Get method signature
                args = []
                for arg in node.args.args:
                    if arg.arg != "self":
                        args.append(arg.arg)

                method_sig = f"{node.name}({', '.join(args)})"
                self.interfaces[self.current_class]["methods"].append(method_sig)

        self.generic_visit(node)


def extract_interfaces(file_path: Path) -> dict[str, dict[str, list[str]]]:
    """Extract interface definitions from a Python file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())

        checker = InterfaceChecker()
        checker.visit(tree)
        return checker.interfaces
    except Exception as e:
        console.print(f"[red]Error parsing {file_path}: {e}[/red]")
        return {}


def find_implementations(interface_name: str, search_dir: Path) -> list[Path]:
    """Find files that might implement an interface."""
    implementations = []

    for py_file in search_dir.rglob("*.py"):
        # Skip interface definitions themselves
        if py_file.parent.name == "interfaces":
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                # Simple heuristic: look for class that inherits from interface
                if interface_name in content and "class " in content:
                    implementations.append(py_file)
        except Exception:
            pass

    return implementations


def check_implementation(
    interface_name: str,
    interface_def: dict[str, list[str]],
    impl_file: Path
) -> list[str]:
    """Check if a file properly implements an interface."""
    violations = []

    try:
        with open(impl_file) as f:
            tree = ast.parse(f.read())

        # Find classes that inherit from the interface
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from our interface
                inherits = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == interface_name or isinstance(base, ast.Attribute) and base.attr == interface_name:
                        inherits = True

                if inherits:
                    # Check that all interface methods are implemented
                    class_methods = {
                        n.name for n in ast.walk(node)
                        if isinstance(n, ast.FunctionDef)
                    }

                    for method_sig in interface_def["methods"]:
                        method_name = method_sig.split("(")[0]
                        if method_name not in class_methods:
                            violations.append(
                                f"{node.name} missing method: {method_sig}"
                            )

    except Exception as e:
        violations.append(f"Error checking {impl_file}: {e}")

    return violations


@click.command()
@click.option("--check-all", is_flag=True, help="Check all interfaces")
@click.option("--interface", help="Check specific interface")
@click.option("--fix", is_flag=True, help="Suggest fixes for violations")
def main(check_all: bool, interface: str | None, fix: bool):
    """Check that interface contracts are properly implemented."""

    if not INTERFACES_DIR.exists():
        console.print(f"[yellow]Interfaces directory not found: {INTERFACES_DIR}[/yellow]")
        console.print("Run this check after creating interface contracts.")
        return

    # Find all interface definition files
    interface_files = list(INTERFACES_DIR.glob("*.py"))
    if not interface_files:
        console.print("[yellow]No interface files found yet.[/yellow]")
        return

    all_interfaces = {}
    for file_path in interface_files:
        if file_path.name != "__init__.py":
            interfaces = extract_interfaces(file_path)
            all_interfaces.update(interfaces)

    if not all_interfaces:
        console.print("[yellow]No interface definitions found.[/yellow]")
        return

    # Display found interfaces
    table = Table(title="Interface Contracts")
    table.add_column("Interface", style="cyan")
    table.add_column("Methods", style="green")
    table.add_column("File", style="yellow")

    for name, definition in all_interfaces.items():
        table.add_row(
            name,
            str(len(definition["methods"])),
            "contracts.py"  # Assuming standard location
        )

    console.print(table)

    # Check implementations
    total_violations = 0
    src_dir = PROJECT_ROOT / "src" / "mia_rag"

    for interface_name, interface_def in all_interfaces.items():
        if interface and interface != interface_name:
            continue

        console.print(f"\n[cyan]Checking {interface_name}...[/cyan]")

        # Find potential implementations
        impl_files = find_implementations(interface_name, src_dir)

        if not impl_files:
            console.print("  [yellow]No implementations found[/yellow]")
            continue

        for impl_file in impl_files:
            violations = check_implementation(
                interface_name,
                interface_def,
                impl_file
            )

            if violations:
                console.print(f"  [red]❌ {impl_file.relative_to(PROJECT_ROOT)}[/red]")
                for violation in violations:
                    console.print(f"    • {violation}")
                    total_violations += len(violations)

                    if fix:
                        console.print(
                            "    [green]Fix:[/green] Implement missing methods "
                            "or update interface if signature changed"
                        )
            else:
                console.print(f"  [green]✅ {impl_file.relative_to(PROJECT_ROOT)}[/green]")

    # Summary
    if total_violations > 0:
        console.print(f"\n[red]❌ Found {total_violations} interface violations![/red]")
        console.print("\nTo fix:")
        console.print("1. Implement missing methods")
        console.print("2. Or update interface if requirements changed (needs RFC)")
        sys.exit(1)
    else:
        console.print("\n[green]✅ All interface contracts are properly implemented![/green]")


if __name__ == "__main__":
    main()
