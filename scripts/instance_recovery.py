#!/usr/bin/env python3
"""
Instance Recovery Tool for MIA RAG System

Provides advanced recovery and diagnostic tools for instance-specific issues.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


console = Console()

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


def run_command(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, check=False)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)


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
    returncode, stdout, stderr = run_command(cmd)

    commits = []
    if returncode == 0:
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 4:
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
    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0:
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return []
    return []


@click.group()
def cli():
    """Instance Recovery Tool - Advanced recovery and diagnostics for MIA RAG instances."""
    pass


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
def diagnose(instance):
    """Run comprehensive diagnostics for an instance."""
    console.print(Panel.fit(f"[bold cyan]Diagnosing {instance}[/bold cyan]"))

    config = INSTANCE_MAP[instance]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Check git status
        task = progress.add_task("Checking git status...", total=None)
        returncode, stdout, stderr = run_command(["git", "status", "--porcelain"])
        progress.remove_task(task)

        if stdout:
            console.print("\n[yellow]⚠️  Uncommitted changes detected:[/yellow]")
            for line in stdout.strip().split("\n")[:10]:
                console.print(f"  {line}")

        # Check recent commits
        task = progress.add_task("Analyzing commit history...", total=None)
        commits = get_git_log(instance)
        progress.remove_task(task)

        if commits:
            console.print(f"\n[cyan]Recent commits for {instance}:[/cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Hash", style="dim")
            table.add_column("Message")
            table.add_column("Author")
            table.add_column("Date")

            for commit in commits[:5]:
                table.add_row(
                    commit["hash"], commit["message"][:50], commit["author"], commit["date"]
                )
            console.print(table)

        # Check open PRs
        task = progress.add_task("Checking open PRs...", total=None)
        prs = get_open_prs(instance)
        progress.remove_task(task)

        if prs:
            console.print(f"\n[cyan]Open PRs for {instance}:[/cyan]")
            for pr in prs[:5]:
                console.print(f"  • PR #{pr['number']}: {pr['title']}")

        # Check test status
        task = progress.add_task("Running quick tests...", total=None)
        test_cmd = ["poetry", "run", "pytest", "-m", instance, "--co", "-q"]
        returncode, stdout, stderr = run_command(test_cmd)
        progress.remove_task(task)

        test_count = len([line for line in stdout.split("\n") if "test_" in line])
        console.print("\n[cyan]Test Status:[/cyan]")
        console.print(f"  • Found {test_count} tests for {instance}")

        # Check dependencies
        task = progress.add_task("Checking dependencies...", total=None)
        dep_issues = []
        for dep in config["dependencies"]:
            check_cmd = ["poetry", "show", dep]
            returncode, stdout, stderr = run_command(check_cmd)
            if returncode != 0:
                dep_issues.append(dep)
        progress.remove_task(task)

        if dep_issues:
            console.print("\n[red]❌ Missing dependencies:[/red]")
            for dep in dep_issues:
                console.print(f"  • {dep}")
        else:
            console.print("\n[green]✅ All dependencies installed[/green]")

        # Check for conflicts
        task = progress.add_task("Checking for conflicts...", total=None)
        conflict_cmd = ["git", "diff", "--name-only", "--diff-filter=U"]
        returncode, stdout, stderr = run_command(conflict_cmd)
        progress.remove_task(task)

        if stdout:
            console.print("\n[red]❌ Merge conflicts detected:[/red]")
            for file in stdout.strip().split("\n"):
                console.print(f"  • {file}")

    # Summary
    console.print("\n" + "=" * 50)
    console.print(Panel.fit("[bold green]Diagnosis Complete[/bold green]"))


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
@click.argument("commit")
@click.option("--dry-run", is_flag=True, help="Show what would be restored without doing it")
def restore(instance, commit, dry_run):
    """Restore an instance to a specific commit."""
    config = INSTANCE_MAP[instance]

    console.print(
        Panel.fit(
            f"[bold yellow]Restoring {instance} to {commit}[/bold yellow]\n"
            + f"Instance: {config['name']}"
        )
    )

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    # Get files that would be affected
    affected_files = []
    for path in config["paths"]:
        if Path(path).exists():
            cmd = ["git", "diff", "--name-only", commit, "HEAD", "--", path]
            returncode, stdout, stderr = run_command(cmd)
            if returncode == 0 and stdout:
                affected_files.extend(stdout.strip().split("\n"))

    if not affected_files:
        console.print("[yellow]No files to restore[/yellow]")
        return

    console.print(f"[cyan]Files to be restored ({len(affected_files)}):[/cyan]")
    for file in affected_files[:10]:
        console.print(f"  • {file}")
    if len(affected_files) > 10:
        console.print(f"  ... and {len(affected_files) - 10} more")

    if not dry_run:
        if not click.confirm("\nProceed with restore?"):
            console.print("[yellow]Restore cancelled[/yellow]")
            return

        # Perform restore
        with console.status("Restoring files..."):
            for path in config["paths"]:
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
    config = INSTANCE_MAP[instance]

    console.print(Panel.fit(f"[bold cyan]Boundaries for {instance}[/bold cyan]"))
    console.print(f"\n[bold]Instance:[/bold] {config['name']}")
    console.print("\n[bold]Owned Paths:[/bold]")

    for path in config["paths"]:
        if Path(path).exists():
            # Count files
            file_count = len(list(Path(path).rglob("*.py")))
            console.print(f"  ✅ {path} ({file_count} Python files)")
        else:
            console.print(f"  ❌ {path} (not found)")

    console.print("\n[bold]Test Markers:[/bold]")
    for marker in config["test_markers"]:
        console.print(f"  • {marker}")

    console.print("\n[bold]Dependencies:[/bold]")
    for dep in config["dependencies"]:
        console.print(f"  • {dep}")

    # Check for boundary violations in current changes
    console.print("\n[bold]Checking current changes for violations...[/bold]")
    cmd = ["git", "diff", "--name-only", "HEAD"]
    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0 and stdout:
        violations = []
        for file in stdout.strip().split("\n"):
            is_allowed = False
            for path in config["paths"]:
                if file.startswith(path):
                    is_allowed = True
                    break
            if not is_allowed and file.endswith(".py"):
                violations.append(file)

        if violations:
            console.print("[red]❌ Boundary violations detected:[/red]")
            for file in violations:
                console.print(f"  • {file}")
        else:
            console.print("[green]✅ No boundary violations[/green]")


@cli.command()
@click.argument("instance", type=click.Choice(list(INSTANCE_MAP.keys())))
@click.option("--days", default=7, help="Number of days to analyze")
def activity(instance, days):
    """Show recent activity for an instance."""
    config = INSTANCE_MAP[instance]

    console.print(
        Panel.fit(f"[bold cyan]Activity Report for {instance}[/bold cyan]\n" + f"Last {days} days")
    )

    # Get commit activity
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cmd = [
        "git",
        "log",
        f"--since={since_date}",
        f"--grep={instance}",
        "--format=%H|%s|%an|%ad",
        "--date=short",
    ]
    returncode, stdout, stderr = run_command(cmd)

    commits_by_date = {}
    if returncode == 0:
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 4:
                    date = parts[3]
                    if date not in commits_by_date:
                        commits_by_date[date] = 0
                    commits_by_date[date] += 1

    if commits_by_date:
        console.print("\n[cyan]Commit Activity:[/cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date")
        table.add_column("Commits", justify="right")
        table.add_column("Graph")

        for date in sorted(commits_by_date.keys(), reverse=True):
            count = commits_by_date[date]
            graph = "█" * min(count * 2, 20)
            table.add_row(date, str(count), f"[green]{graph}[/green]")

        console.print(table)

    # Get PR activity
    prs = get_open_prs(instance)
    if prs:
        console.print(f"\n[cyan]Open PRs ({len(prs)}):[/cyan]")
        for pr in prs[:5]:
            console.print(f"  • PR #{pr['number']}: {pr['title']}")

    # File change statistics
    console.print("\n[cyan]File Change Statistics:[/cyan]")
    for path in config["paths"]:
        if Path(path).exists():
            cmd = ["git", "log", f"--since={since_date}", "--format=", "--numstat", "--", path]
            returncode, stdout, stderr = run_command(cmd)

            if returncode == 0:
                lines_added = 0
                lines_removed = 0
                for line in stdout.strip().split("\n"):
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            try:
                                lines_added += int(parts[0])
                                lines_removed += int(parts[1])
                            except ValueError:
                                pass

                console.print(f"  {path}:")
                console.print(
                    f"    [green]+{lines_added}[/green] / [red]-{lines_removed}[/red] lines"
                )


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
    returncode, stdout, stderr = run_command(cmd)

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
    config = INSTANCE_MAP[instance]
    issues = []

    console.print(Panel.fit(f"[bold cyan]Health Check for {instance}[/bold cyan]"))

    with console.status("Running health checks..."):
        # Check if paths exist
        for path in config["paths"]:
            if not Path(path).exists():
                issues.append(f"Path does not exist: {path}")
                if fix:
                    Path(path).mkdir(parents=True, exist_ok=True)

        # Check for __init__.py files
        for path in config["paths"]:
            init_file = Path(path) / "__init__.py"
            if Path(path).exists() and not init_file.exists():
                issues.append(f"Missing __init__.py: {path}")
                if fix:
                    init_file.touch()

        # Check dependencies
        for dep in config["dependencies"]:
            cmd = ["poetry", "show", dep]
            returncode, stdout, stderr = run_command(cmd)
            if returncode != 0:
                issues.append(f"Missing dependency: {dep}")
                if fix:
                    install_cmd = ["poetry", "install", "--extras", instance]
                    run_command(install_cmd, capture=False)

    if issues:
        console.print("\n[red]Issues found:[/red]")
        for issue in issues:
            console.print(f"  ❌ {issue}")

        if fix:
            console.print("\n[yellow]Attempted fixes. Please verify.[/yellow]")
    else:
        console.print("\n[green]✅ All health checks passed![/green]")


if __name__ == "__main__":
    cli()
