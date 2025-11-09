#!/usr/bin/env python3
"""
Instance Identification Script for MIA RAG System

This script identifies and configures the Claude Code instance assignment.
It creates a .instance file that other scripts and tools can read.
"""

import json
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()

# Project root is parent of scripts directory
PROJECT_ROOT = Path(__file__).parent.parent
INSTANCE_FILE = PROJECT_ROOT / ".instance"
ASSIGNMENTS_FILE = PROJECT_ROOT / ".claude" / "instance-assignments.json"


def load_assignments() -> dict[str, Any]:
    """Load instance assignments configuration."""
    if not ASSIGNMENTS_FILE.exists():
        console.print(
            "[red]Error:[/red] Instance assignments file not found at:", str(ASSIGNMENTS_FILE)
        )
        sys.exit(1)

    with open(ASSIGNMENTS_FILE) as f:
        return json.load(f)


def get_current_instance() -> str | None:
    """Get the currently configured instance."""
    if INSTANCE_FILE.exists():
        return INSTANCE_FILE.read_text().strip()
    return None


def display_instance_info(instance_id: str, assignments: dict[str, Any]):
    """Display detailed information about an instance."""
    instance = assignments["instances"][instance_id]

    # Create info panel
    panel = Panel.fit(
        f"""[bold cyan]Instance Assignment: {instance_id}[/bold cyan]

[yellow]Name:[/yellow] {instance['name']}
[yellow]Description:[/yellow] {instance['description']}

[yellow]Owned Directories:[/yellow]
{chr(10).join('  • ' + d for d in instance['directories'])}

[yellow]Dependencies:[/yellow] {', '.join(instance['dependencies']) if instance['dependencies'] else 'None'}

[yellow]Poetry Extras:[/yellow] {instance['extras']}
        """,
        title=f"🤖 {instance_id.upper()}",
        border_style="cyan",
    )
    console.print(panel)


def display_all_instances(assignments: dict[str, Any]):
    """Display table of all instances."""
    table = Table(title="MIA RAG System - Instance Assignments")

    table.add_column("Instance", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Modules", style="green")
    table.add_column("Dependencies", style="yellow")

    for instance_id, info in assignments["instances"].items():
        table.add_row(
            instance_id,
            info["name"],
            ", ".join(info["modules"]),
            ", ".join(info["dependencies"]) if info["dependencies"] else "None",
        )

    console.print(table)


@click.command()
@click.option(
    "--set",
    "set_instance",
    type=click.Choice(
        ["instance1", "instance2", "instance3", "instance4", "instance5", "instance6"]
    ),
    help="Set the instance assignment",
)
@click.option("--show", is_flag=True, help="Show current instance assignment")
@click.option("--list", "list_all", is_flag=True, help="List all available instances")
@click.option(
    "--auto", is_flag=True, help="Auto-detect instance based on recent file modifications"
)
def main(set_instance: str | None, show: bool, list_all: bool, auto: bool):
    """Identify and configure Claude Code instance assignment."""

    assignments = load_assignments()

    # List all instances
    if list_all:
        display_all_instances(assignments)
        return

    # Auto-detect instance
    if auto:
        console.print("[yellow]Auto-detection not yet implemented.[/yellow]")
        console.print("Please use --set to manually set your instance.")
        return

    # Set instance
    if set_instance:
        # Save instance file
        INSTANCE_FILE.write_text(set_instance)

        # Create instance-specific .env if it doesn't exist
        env_file = PROJECT_ROOT / f".env.{set_instance}"
        if not env_file.exists():
            env_example = PROJECT_ROOT / ".env.example"
            if env_example.exists():
                env_file.write_text(env_example.read_text())
                console.print(f"[green]Created {env_file.name} from template[/green]")

        console.print(f"[green]✅ Instance set to: {set_instance}[/green]")
        display_instance_info(set_instance, assignments)

        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Install dependencies: [cyan]mise run install[/cyan]")
        console.print("2. Check boundaries: [cyan]mise run show:boundaries[/cyan]")
        console.print("3. Start work session: [cyan]mise run work:start[/cyan]")
        return

    # Show current instance (default)
    current = get_current_instance()
    if current:
        console.print(f"[green]Current instance: {current}[/green]")
        display_instance_info(current, assignments)

        # Check if environment is properly configured
        env_file = PROJECT_ROOT / f".env.{current}"
        if not env_file.exists():
            console.print(
                f"\n[yellow]Warning:[/yellow] Environment file {env_file.name} not found."
            )
            console.print("Run: [cyan]cp .env.example " + env_file.name + "[/cyan]")
    else:
        console.print("[yellow]No instance assigned yet.[/yellow]")
        console.print("\nTo set your instance, run:")
        console.print("[cyan]python scripts/identify_instance.py --set instance<N>[/cyan]")
        console.print("\nOr use Mise:")
        console.print("[cyan]mise run instance<N>:setup[/cyan]")
        display_all_instances(assignments)


if __name__ == "__main__":
    main()
