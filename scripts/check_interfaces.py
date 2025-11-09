#!/usr/bin/env python3
"""
Check Interface Contracts

This script verifies that interface contracts are properly implemented
and haven't been broken by recent changes.

Refactored to use the Visitor pattern for better separation of concerns
and reduced cyclomatic complexity.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from scripts.domain.interfaces import InterfaceViolation
from scripts.patterns.repositories import InterfaceRepository
from scripts.patterns.visitors import InterfaceValidator


console = Console()

PROJECT_ROOT = Path(__file__).parent.parent
INTERFACES_DIR = PROJECT_ROOT / "src" / "mia_rag" / "interfaces"


def find_implementations(interface_name: str, search_dir: Path) -> list[Path]:
    """Find files that might implement an interface.

    Args:
        interface_name: Name of the interface to search for
        search_dir: Directory to search in

    Returns:
        List of Python files that reference the interface
    """
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
            # Skip files we can't read
            pass

    return implementations


def display_interfaces_table(interfaces: dict) -> None:
    """Display a table of found interfaces.

    Args:
        interfaces: Dictionary of interface definitions
    """
    table = Table(title="Interface Contracts")
    table.add_column("Interface", style="cyan")
    table.add_column("Methods", style="green")
    table.add_column("File", style="yellow")

    for name, definition in interfaces.items():
        table.add_row(
            name,
            str(len(definition.methods)),
            "contracts.py",  # Assuming standard location
        )

    console.print(table)


def display_violations(violations: list[InterfaceViolation], impl_file: Path) -> None:
    """Display violations for a file.

    Args:
        violations: List of violations
        impl_file: Path to the implementation file
    """
    console.print(f"  [red]❌ {impl_file.relative_to(PROJECT_ROOT)}[/red]")
    for violation in violations:
        severity_color = "red" if violation.severity == "error" else "yellow"
        console.print(f"    [{severity_color}]• {violation.message}[/{severity_color}]")


def check_implementations_for_interface(
    interface_name: str,
    interface_def,
    search_dir: Path,
    validator: InterfaceValidator,
    show_fixes: bool = False,
) -> int:
    """Check all implementations of a specific interface.

    Args:
        interface_name: Name of the interface
        interface_def: Interface definition
        search_dir: Directory to search for implementations
        validator: InterfaceValidator instance
        show_fixes: Whether to show suggested fixes

    Returns:
        Number of violations found
    """
    console.print(f"\n[cyan]Checking {interface_name}...[/cyan]")

    # Find potential implementations
    impl_files = find_implementations(interface_name, search_dir)

    if not impl_files:
        console.print("  [yellow]No implementations found[/yellow]")
        return 0

    total_violations = 0

    for impl_file in impl_files:
        violations = validator.validate(impl_file)

        # Filter violations to only those related to this interface
        # (in case file implements multiple interfaces)
        relevant_violations = [
            v for v in violations
            if interface_name in str(v.message) or v.violation_type in [
                "missing_method", "missing_import", "wrong_signature"
            ]
        ]

        if relevant_violations:
            display_violations(relevant_violations, impl_file)
            total_violations += len(relevant_violations)

            if show_fixes:
                console.print(
                    "    [green]Fix:[/green] Implement missing methods "
                    "or update interface if signature changed"
                )
        else:
            console.print(f"  [green]✅ {impl_file.relative_to(PROJECT_ROOT)}[/green]")

    return total_violations


@click.command()
@click.option("--check-all", is_flag=True, help="Check all interfaces")
@click.option("--interface", help="Check specific interface")
@click.option("--fix", is_flag=True, help="Suggest fixes for violations")
@click.option("--strict", is_flag=True, help="Enable strict type checking")
def main(check_all: bool, interface: str | None, fix: bool, strict: bool):
    """Check that interface contracts are properly implemented.

    This tool validates that all classes implementing interfaces
    properly fulfill their contracts (implement all required methods,
    have correct signatures, etc.).
    """

    if not INTERFACES_DIR.exists():
        console.print(f"[yellow]Interfaces directory not found: {INTERFACES_DIR}[/yellow]")
        console.print("Run this check after creating interface contracts.")
        return

    # Initialize repository and validator
    repository = InterfaceRepository()
    repository.load()

    all_interfaces = repository.get_all_interfaces()

    if not all_interfaces:
        console.print("[yellow]No interface definitions found.[/yellow]")
        return

    # Display found interfaces
    display_interfaces_table(all_interfaces)

    # Initialize validator with type checking setting
    validator = InterfaceValidator(repository)

    # Check implementations
    total_violations = 0
    src_dir = PROJECT_ROOT / "src" / "mia_rag"

    for interface_name, interface_def in all_interfaces.items():
        # Skip if checking specific interface and this isn't it
        if interface and interface != interface_name:
            continue

        violations = check_implementations_for_interface(
            interface_name,
            interface_def,
            src_dir,
            validator,
            show_fixes=fix,
        )
        total_violations += violations

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
