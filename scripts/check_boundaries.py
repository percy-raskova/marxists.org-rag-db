#!/usr/bin/env python3
"""
Check Instance Boundaries Script

This script checks if files being modified respect instance boundaries.
Used as a pre-commit hook and can be run manually.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Optional
import click
from rich.console import Console
from rich.table import Table

from instance_map import get_instance_for_path, is_shared_path

console = Console()

PROJECT_ROOT = Path(__file__).parent.parent
INSTANCE_FILE = PROJECT_ROOT / ".instance"


def get_current_instance() -> Optional[str]:
    """Get the currently configured instance."""
    if INSTANCE_FILE.exists():
        return INSTANCE_FILE.read_text().strip()

    # Try environment variable
    return os.getenv("INSTANCE_ID")


def get_modified_files() -> List[str]:
    """Get list of modified files in git."""
    try:
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        staged = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Get modified but not staged files
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        modified = result.stdout.strip().split("\n") if result.stdout.strip() else []

        return [f for f in staged + modified if f]
    except subprocess.CalledProcessError:
        return []


def check_file_ownership(file_path: str, instance_id: str) -> tuple[bool, str]:
    """
    Check if a file can be modified by the given instance.

    Returns:
        (is_allowed, reason)
    """
    # Ignore non-Python files for detailed checking
    if not file_path.endswith(('.py', '.yaml', '.yml', '.toml', '.json', '.md')):
        return True, "Non-critical file"

    # Check if it's a shared resource
    if is_shared_path(file_path):
        return True, "Shared resource (coordinate changes)"

    # Check ownership
    owner = get_instance_for_path(file_path)

    if owner is None:
        # File not in any instance's territory
        return True, "Not instance-specific"

    if owner == instance_id:
        return True, f"Owned by {instance_id}"

    return False, f"Owned by {owner}"


@click.command()
@click.argument("files", nargs=-1)
@click.option("--instance", help="Override instance ID")
@click.option("--strict", is_flag=True, help="Fail on any boundary violation")
@click.option("--auto", is_flag=True, help="Check git modified files automatically")
def main(files: tuple, instance: Optional[str], strict: bool, auto: bool):
    """Check if files respect instance boundaries."""

    # Get instance ID
    instance_id = instance or get_current_instance()
    if not instance_id:
        console.print("[yellow]Warning: No instance assigned. Run:[/yellow]")
        console.print("[cyan]python scripts/identify_instance.py --set instance<N>[/cyan]")
        if strict:
            sys.exit(1)
        return

    # Get files to check
    if auto:
        files_to_check = get_modified_files()
    elif files:
        files_to_check = list(files)
    else:
        # No files specified, check git by default
        files_to_check = get_modified_files()

    if not files_to_check:
        console.print("[green]No files to check.[/green]")
        return

    # Check each file
    violations = []
    warnings = []
    ok_files = []

    table = Table(title=f"Boundary Check for {instance_id}")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Reason")

    for file_path in files_to_check:
        is_allowed, reason = check_file_ownership(file_path, instance_id)

        if is_allowed:
            if "Shared resource" in reason:
                warnings.append((file_path, reason))
                table.add_row(file_path, "⚠️  Warning", reason)
            else:
                ok_files.append((file_path, reason))
                table.add_row(file_path, "✅ OK", reason)
        else:
            violations.append((file_path, reason))
            table.add_row(file_path, "❌ Violation", reason, style="red")

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  ✅ OK: {len(ok_files)} files")
    console.print(f"  ⚠️  Warnings: {len(warnings)} files")
    console.print(f"  ❌ Violations: {len(violations)} files")

    if violations:
        console.print("\n[red bold]Boundary Violations Detected![/red bold]")
        console.print(f"\n{instance_id} modified files outside its boundaries:")
        for file_path, reason in violations:
            console.print(f"  • {file_path} ({reason})")

        console.print("\n[yellow]Please revert changes to files outside your boundaries.[/yellow]")
        console.print("Or coordinate with the owning instance if changes are needed.")

        if strict:
            sys.exit(1)

    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        console.print("You're modifying shared resources. Please ensure:")
        console.print("  • Changes are documented in work logs")
        console.print("  • Other instances are notified")
        console.print("  • Changes don't break other instances")


if __name__ == "__main__":
    main()