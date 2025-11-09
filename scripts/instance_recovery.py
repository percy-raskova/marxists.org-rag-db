#!/usr/bin/env python3
"""
Instance Recovery Tool for MIA RAG System

Provides advanced recovery and diagnostic tools for instance-specific issues.
Refactored using Template Method pattern to reduce complexity.
"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from scripts.domain.recovery import InstanceConfig, RecoveryContext
from scripts.patterns.recovery import (
    ActivityAnalysisStrategy,
    BoundaryCheckStrategy,
    DiagnosticStrategy,
    HealthCheckStrategy,
    run_command,
)


console = Console()

# Constants
GIT_LOG_PARTS_COUNT = 4

# Instance configuration
INSTANCE_MAP = {
    "instance1": {
        "name": "Storage & Pipeline",
        "paths": ["src/mia_rag/storage/", "src/mia_rag/pipeline/"],
        "test_markers": ["instance1"],
        "dependencies": ["google-cloud-storage", "pyarrow"],
    },
    "instance2": {
        "name": "Embeddings",
        "paths": ["src/mia_rag/embeddings/"],
        "test_markers": ["instance2"],
        "dependencies": ["runpod", "sentence-transformers"],
    },
    "instance3": {
        "name": "Weaviate",
        "paths": ["src/mia_rag/vectordb/"],
        "test_markers": ["instance3"],
        "dependencies": ["weaviate-client"],
    },
    "instance4": {
        "name": "API",
        "paths": ["src/mia_rag/api/"],
        "test_markers": ["instance4"],
        "dependencies": ["fastapi", "uvicorn"],
    },
    "instance5": {
        "name": "MCP",
        "paths": ["src/mia_rag/mcp/"],
        "test_markers": ["instance5"],
        "dependencies": ["mcp"],
    },
    "instance6": {
        "name": "Monitoring",
        "paths": ["src/mia_rag/monitoring/", "tests/integration/"],
        "test_markers": ["instance6", "integration"],
        "dependencies": ["prometheus-client", "grafana-api"],
    },
}


def get_instance_config(instance_id: str) -> InstanceConfig:
    """Convert instance map to InstanceConfig domain object."""
    config_dict = INSTANCE_MAP[instance_id]
    return InstanceConfig(
        instance_id=instance_id,
        name=config_dict["name"],
        paths=config_dict["paths"],
        test_markers=config_dict["test_markers"],
        dependencies=config_dict["dependencies"],
    )


def get_git_log(instance: str, limit: int = 10) -> list[dict]:
    """Get recent git commits for an instance."""
    cmd = [
        "git",
        "log",
        f"--grep={instance}",
        "--oneline",
        f"-{limit}",
        "--format=%H|%s|%an|%ad",
        "--date=relative",
    ]
    returncode, stdout, _stderr = run_command(cmd)

    commits = []
    if returncode == 0:
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= GIT_LOG_PARTS_COUNT:
                    commits.append(
                        {
                            "hash": parts[0][:7],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                        }
                    )
    return commits


def get_open_prs(instance: str) -> list[dict]:
    """Get open PRs for an instance."""
    cmd = [
        "gh",
        "pr",
        "list",
        "--search",
        instance,
        "--json",
        "number,title,state,author,createdAt",
    ]
    returncode, stdout, _stderr = run_command(cmd)

    if returncode == 0:
        try:
            return json.loads(stdout)
        except Exception:
            return []
    return []


@click.group()
def cli():
    """Instance Recovery Tool - Advanced recovery and diagnostics for MIA RAG instances."""


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
def diagnose(instance):
    """Run comprehensive diagnostics for an instance."""
    console.print(Panel.fit(f"[bold cyan]Diagnosing {instance}[/bold cyan]"))

    # Create context and execute strategy
    config = get_instance_config(instance)
    ctx = RecoveryContext(instance_id=instance, config=config)
    strategy = DiagnosticStrategy()
    result = strategy.execute(ctx)

    # Summary
    console.print("\n" + "=" * 50)
    if result.success:
        console.print(Panel.fit("[bold green]Diagnosis Complete[/bold green]"))
    else:
        console.print(Panel.fit("[bold red]Diagnosis Found Issues[/bold red]"))


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
@click.argument("commit")
@click.option("--dry-run", is_flag=True, help="Show what would be restored without doing it")
def restore(instance, commit, dry_run):
    """Restore an instance to a specific commit."""
    config_dict = INSTANCE_MAP[instance]

    console.print(
        Panel.fit(
            f"[bold yellow]Restoring {instance} to {commit}[/bold yellow]\n"
            + f"Instance: {config_dict['name']}"
        )
    )

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Get files that would be affected
    affected_files = []
    for path in config_dict["paths"]:
        if Path(path).exists():
            cmd = ["git", "diff", "--name-only", commit, "HEAD", "--", path]
            returncode, stdout, stderr = run_command(cmd)
            if returncode == 0 and stdout:
                affected_files.extend(stdout.strip().split("\n"))

    if not affected_files:
        console.print("[yellow]No files to restore[/yellow]")
        return

    console.print(f"[cyan]Files to be restored ({len(affected_files)}):[/cyan]")
    max_display = 10
    for file in affected_files[:max_display]:
        console.print(f"  • {file}")
    if len(affected_files) > max_display:
        console.print(f"  ... and {len(affected_files) - max_display} more")

    if not dry_run:
        if not click.confirm("\nProceed with restore?"):
            console.print("[yellow]Restore cancelled[/yellow]")
            return

        # Perform restore
        with console.status("Restoring files..."):
            for path in config_dict["paths"]:
                if Path(path).exists():
                    cmd = ["git", "checkout", commit, "--", path]
                    returncode, stdout, stderr = run_command(cmd)
                    if returncode != 0:
                        console.print(f"[red]Error restoring {path}: {stderr}[/red]")
                        return

        console.print(f"[green]✅ Restored {instance} to {commit}[/green]")
        console.print("[yellow]Remember to commit these changes[/yellow]")


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
def boundaries(instance):
    """Show ownership boundaries for an instance."""
    console.print(Panel.fit(f"[bold cyan]Boundaries for {instance}[/bold cyan]"))

    # Create context and execute strategy
    config = get_instance_config(instance)
    ctx = RecoveryContext(instance_id=instance, config=config)
    strategy = BoundaryCheckStrategy()
    strategy.execute(ctx)

    # Display test markers and dependencies
    console.print("\n[bold]Test Markers:[/bold]")
    for marker in config.test_markers:
        console.print(f"  • {marker}")

    console.print("\n[bold]Dependencies:[/bold]")
    for dep in config.dependencies:
        console.print(f"  • {dep}")


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
@click.option("--days", default=7, help="Number of days to analyze")
def activity(instance, days):
    """Show recent activity for an instance."""
    console.print(
        Panel.fit(f"[bold cyan]Activity Report for {instance}[/bold cyan]\n" + f"Last {days} days")
    )

    # Create context and execute strategy
    config = get_instance_config(instance)
    ctx = RecoveryContext(instance_id=instance, config=config)
    strategy = ActivityAnalysisStrategy(days=days)
    strategy.execute(ctx)


@cli.command()
def status():
    """Show status of all instances."""
    console.print(Panel.fit("[bold cyan]MIA RAG System Status[/bold cyan]"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Instance")
    table.add_column("Name")
    table.add_column("Recent Commits")
    table.add_column("Open PRs")
    table.add_column("Status")

    for instance_id, config in INSTANCE_MAP.items():
        # Get recent commits
        commits = get_git_log(instance_id, 5)
        commit_count = len(commits)

        # Get open PRs
        prs = get_open_prs(instance_id)
        pr_count = len(prs)

        # Check for issues
        status = "[green]✅ Active[/green]"
        if commit_count == 0:
            status = "[yellow]⚠️ Inactive[/yellow]"

        table.add_row(instance_id, config["name"], str(commit_count), str(pr_count), status)

    console.print(table)

    # Check for integration branch
    cmd = ["git", "branch", "-r", "--list", "origin/integration/daily-*"]
    returncode, stdout, _stderr = run_command(cmd)

    if returncode == 0 and stdout:
        branches = stdout.strip().split("\n")
        if branches:
            latest = branches[-1].replace("origin/", "")
            console.print(f"\n[cyan]Latest integration branch:[/cyan] {latest}")


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
@click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
def health(instance, fix):
    """Run health check for an instance."""
    console.print(Panel.fit(f"[bold cyan]Health Check for {instance}[/bold cyan]"))

    # Create context and execute strategy
    config = get_instance_config(instance)
    ctx = RecoveryContext(instance_id=instance, config=config, auto_fix=fix)
    strategy = HealthCheckStrategy()
    strategy.execute(ctx)


if __name__ == "__main__":
    cli()
