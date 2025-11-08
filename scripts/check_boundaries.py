#!/usr/bin/env python3
"""
Check Instance Boundaries Script

This script checks if files being modified respect instance boundaries.
Used as a pre-commit hook and can be run manually.
"""

import os
import subprocess
import sys
from enum import Enum
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from domain.boundaries import FilePath
from instance_map import get_instance_for_path, is_shared_path
from patterns.boundary_specifications import InSharedPath, create_boundary_rules


console = Console()

PROJECT_ROOT = Path(__file__).parent.parent
INSTANCE_FILE = PROJECT_ROOT / ".instance"


class CheckResult(Enum):
    """Result of boundary check."""

    OK = "ok"
    WARNING = "warning"
    VIOLATION = "violation"


def get_current_instance() -> str | None:
    """Get the currently configured instance."""
    if INSTANCE_FILE.exists():
        return INSTANCE_FILE.read_text().strip()

    # Try environment variable
    return os.getenv("INSTANCE_ID")


def get_modified_files() -> list[str]:
    """Get list of modified files in git."""
    try:
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        staged = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Get modified but not staged files
        result = subprocess.run(
            ["git", "diff", "--name-only"], capture_output=True, text=True, check=True
        )
        modified = result.stdout.strip().split("\n") if result.stdout.strip() else []

        return [f for f in staged + modified if f]
    except subprocess.CalledProcessError:
        return []


def check_file_boundaries(
    file_path_str: str,
    instance_id: str,
    project_root: Path = PROJECT_ROOT,
) -> tuple[CheckResult, str]:
    """
    Check if a file can be modified by the given instance using Specification pattern.

    Args:
        file_path_str: File path to check
        instance_id: Instance ID doing the modification
        project_root: Project root directory

    Returns:
        (CheckResult, reason)
    """
    # Create FilePath value object
    file_path = FilePath.from_path(
        file_path_str,
        project_root,
        owner_resolver=get_instance_for_path,
        shared_checker=is_shared_path,
    )

    # Create boundary rules specification
    boundary_spec = create_boundary_rules(instance_id)

    # Check if modification is allowed
    if boundary_spec.is_satisfied_by(file_path):
        # Check if it's a shared path (warning)
        if InSharedPath().is_satisfied_by(file_path):
            return CheckResult.WARNING, "Shared resource (coordinate changes)"
        return CheckResult.OK, boundary_spec.reason()

    # Violation
    return CheckResult.VIOLATION, f"Owned by {file_path.instance_owner}"


@click.command()
@click.argument("files", nargs=-1)
@click.option("--instance", help="Override instance ID")
@click.option("--strict", is_flag=True, help="Fail on any boundary violation")
@click.option("--auto", is_flag=True, help="Check git modified files automatically")
def main(files: tuple, instance: str | None, strict: bool, auto: bool):
    """Check if files respect instance boundaries."""
    # Get instance ID
    instance_id = instance or get_current_instance()
    if not instance_id:
        _handle_no_instance(strict)
        return

    # Get files to check
    files_to_check = _get_files_to_check(files, auto)
    if not files_to_check:
        console.print("[green]No files to check.[/green]")
        return

    # Check files and categorize results
    results = _check_files(files_to_check, instance_id)

    # Display results
    _display_results(instance_id, results)

    # Handle violations
    if results["violations"] and strict:
        sys.exit(1)


def _handle_no_instance(strict: bool):
    """Handle case where no instance is assigned."""
    console.print("[yellow]Warning: No instance assigned. Run:[/yellow]")
    console.print("[cyan]python scripts/identify_instance.py --set instance<N>[/cyan]")
    if strict:
        sys.exit(1)


def _get_files_to_check(files: tuple, auto: bool) -> list[str]:
    """Get list of files to check based on CLI arguments."""
    if auto or not files:
        return get_modified_files()
    return list(files)


def _check_files(files_to_check: list[str], instance_id: str) -> dict:
    """Check all files and categorize by result type."""
    violations = []
    warnings = []
    ok_files = []

    for file_path in files_to_check:
        result, reason = check_file_boundaries(file_path, instance_id)

        if result == CheckResult.VIOLATION:
            violations.append((file_path, reason))
        elif result == CheckResult.WARNING:
            warnings.append((file_path, reason))
        else:
            ok_files.append((file_path, reason))

    return {"violations": violations, "warnings": warnings, "ok_files": ok_files}


def _display_results(instance_id: str, results: dict):
    """Display check results in a rich table with summary."""
    violations = results["violations"]
    warnings = results["warnings"]
    ok_files = results["ok_files"]

    # Create table
    table = Table(title=f"Boundary Check for {instance_id}")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Reason")

    for file_path, reason in ok_files:
        table.add_row(file_path, "✅ OK", reason)
    for file_path, reason in warnings:
        table.add_row(file_path, "⚠️  Warning", reason)
    for file_path, reason in violations:
        table.add_row(file_path, "❌ Violation", reason, style="red")

    console.print(table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  ✅ OK: {len(ok_files)} files")
    console.print(f"  ⚠️  Warnings: {len(warnings)} files")
    console.print(f"  ❌ Violations: {len(violations)} files")

    # Detailed violation info
    if violations:
        _display_violations(instance_id, violations)

    # Warning info
    if warnings:
        _display_warnings()


def _display_violations(instance_id: str, violations: list):
    """Display detailed violation information."""
    console.print("\n[red bold]Boundary Violations Detected![/red bold]")
    console.print(f"\n{instance_id} modified files outside its boundaries:")
    for file_path, reason in violations:
        console.print(f"  • {file_path} ({reason})")

    console.print("\n[yellow]Please revert changes to files outside your boundaries.[/yellow]")
    console.print("Or coordinate with the owning instance if changes are needed.")


def _display_warnings():
    """Display warning information for shared resources."""
    console.print("\n[yellow]Warnings:[/yellow]")
    console.print("You're modifying shared resources. Please ensure:")
    console.print("  • Changes are documented in work logs")
    console.print("  • Other instances are notified")
    console.print("  • Changes don't break other instances")


if __name__ == "__main__":
    main()
