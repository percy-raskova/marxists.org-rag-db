#!/usr/bin/env python3
"""
Check TODOs Have Context

This script ensures all TODO comments have proper context including:
- Owner (instance)
- Description
- Issue link or date
"""

import re
import sys
from pathlib import Path

import click
from rich.console import Console


console = Console()

# Patterns for valid TODOs
VALID_TODO_PATTERNS = [
    # TODO(instance1): Description - issue #123
    r"#\s*TODO\([^)]+\):\s*.+\s*-\s*(issue\s+#\d+|see\s+.+|by\s+\d{4}-\d{2}-\d{2})",
    # FIXME(instance2): Description - blocked by X
    r"#\s*FIXME\([^)]+\):\s*.+\s*-\s*(issue\s+#\d+|blocked by .+|by\s+\d{4}-\d{2}-\d{2})",
    # NOTE(instance3): Important note (less strict)
    r"#\s*NOTE\([^)]+\):\s*.+",
]

# Pattern for any TODO/FIXME/HACK
TODO_PATTERN = r"#\s*(TODO|FIXME|HACK|XXX|NOTE)(\([^)]*\))?:?\s*(.*)$"


def check_todo_context(line: str) -> tuple[bool, str]:
    """
    Check if a TODO has proper context.

    Returns:
        (is_valid, reason)
    """
    # Check if line contains TODO-like comment
    match = re.search(TODO_PATTERN, line, re.IGNORECASE)
    if not match:
        return True, "No TODO found"

    todo_type = match.group(1).upper()
    owner = match.group(2) if match.group(2) else ""
    description = match.group(3).strip() if match.group(3) else ""

    # Check for vague TODOs
    vague_patterns = [
        r"^(fix|fixme|fix this|later|optimize|refactor|clean|cleanup|remove|delete)$",
        r"^(this|here|check|test|todo|implement|add|update)$",
    ]

    for pattern in vague_patterns:
        if re.match(pattern, description, re.IGNORECASE):
            return False, f"Vague {todo_type}: '{description}'"

    # Check if it matches valid patterns
    for pattern in VALID_TODO_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True, f"Valid {todo_type}"

    # Collect validation errors for component checks
    if not owner:
        error_msg = f"{todo_type} missing owner (e.g., TODO(instance1):)"
    elif len(description) < 10:
        error_msg = f"{todo_type} description too short: '{description}'"
    elif todo_type in ["TODO", "FIXME"] and "-" not in description:
        error_msg = f"{todo_type} missing context (add '- issue #X' or '- by YYYY-MM-DD')"
    else:
        error_msg = None

    # Return validation result
    return (True, f"{todo_type} acceptable") if error_msg is None else (False, error_msg)


def check_file(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Check all TODOs in a file.

    Returns list of (line_number, line_content, error_message)
    """
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                is_valid, reason = check_todo_context(line.rstrip())
                if not is_valid:
                    violations.append((line_num, line.rstrip(), reason))
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")

    return violations


@click.command()
@click.argument("files", nargs=-1, required=True)
@click.option("--fix", is_flag=True, help="Suggest fixes for invalid TODOs")
def main(files: tuple, fix: bool):
    """Check that TODOs have proper context."""

    total_violations = 0
    file_violations = {}

    for file_path_str in files:
        file_path = Path(file_path_str)

        # Skip non-Python files
        if file_path.suffix not in [".py", ".yaml", ".yml"]:
            continue

        violations = check_file(file_path)
        if violations:
            file_violations[file_path] = violations
            total_violations += len(violations)

    # Report violations
    if file_violations:
        console.print("[red bold]❌ TODO Context Violations Found[/red bold]\n")

        for file_path, violations in file_violations.items():
            console.print(f"[cyan]{file_path}:[/cyan]")
            for line_num, line, reason in violations:
                console.print(f"  Line {line_num}: [red]{reason}[/red]")
                console.print(f"    {line.strip()}")

                if fix:
                    # Suggest fix
                    if "missing owner" in reason:
                        console.print(
                            "    [green]Suggested:[/green] "
                            "# TODO(instanceX): <description> - issue #<num>"
                        )
                    elif "too short" in reason:
                        console.print(
                            "    [green]Suggested:[/green] "
                            "Add more descriptive context about what needs to be done"
                        )
                    elif "missing context" in reason:
                        console.print(
                            "    [green]Suggested:[/green] "
                            "Add '- issue #123' or '- by 2025-01-15'"
                        )
                    elif "Vague" in reason:
                        console.print(
                            "    [green]Suggested:[/green] "
                            "# TODO(instanceX): Specific description of what to do - issue #123"
                        )

            console.print()

        console.print(f"[red]Total violations: {total_violations}[/red]")
        console.print("\n[yellow]Examples of valid TODOs:[/yellow]")
        console.print("  # TODO(instance1): Optimize batch size after profiling - issue #42")
        console.print("  # TODO(instance2): Add retry logic for API timeouts - by 2025-01-15")
        console.print("  # FIXME(instance3): Memory leak in processor - blocked by instance1")
        console.print("  # NOTE(instance4): This is a temporary workaround")

        sys.exit(1)
    else:
        console.print("[green]✅ All TODOs have proper context![/green]")


if __name__ == "__main__":
    main()
