"""Template Method pattern for instance recovery operations.

This module implements the Template Method design pattern to handle various
instance recovery and diagnostic operations with reduced complexity.
"""

import contextlib
import json
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from scripts.domain.recovery import (
    ActivityReport,
    BoundaryCheckResult,
    DiagnosticResult,
    HealthCheckResult,
    InstanceConfig,
    RecoveryContext,
)


console = Console()

# Constants
GIT_LOG_COMMIT_PARTS = 4
MAX_FILES_DISPLAY = 10
MAX_DISPLAYED_RESULTS = 5
DEFAULT_COMMIT_LIMIT = 10


def run_command(cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode, result.stdout, result.stderr
        result = subprocess.run(cmd, check=False)
        return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)


class RecoveryStrategy(ABC):
    """Abstract template for recovery operations.

    This class defines the template method pattern for all instance
    recovery and diagnostic operations.
    """

    def execute(
        self, ctx: RecoveryContext
    ) -> DiagnosticResult | BoundaryCheckResult | ActivityReport | HealthCheckResult:
        """Template method defining the workflow.

        Steps:
        1. Validate preconditions
        2. Gather data
        3. Process results
        4. Handle errors

        Args:
            ctx: Recovery context with instance configuration

        Returns:
            Result object specific to the strategy type
        """
        try:
            # 1. Validate
            if not self.validate_preconditions(ctx):
                return self.create_error_result(ctx, ["Precondition validation failed"])

            # 2. Gather data with progress display
            result = self.gather_data(ctx)

            # 3. Process
            self.process_results(result)

            return result

        except Exception as e:
            return self.create_error_result(ctx, [str(e)])

    def validate_preconditions(self, _ctx: RecoveryContext) -> bool:
        """Validate before starting operation. Override for custom validation."""
        return True

    @abstractmethod
    def gather_data(
        self, ctx: RecoveryContext
    ) -> DiagnosticResult | BoundaryCheckResult | ActivityReport | HealthCheckResult:
        """Gather data for the operation. Must be implemented by subclass."""

    def process_results(  # noqa: B027
        self, result: DiagnosticResult | BoundaryCheckResult | ActivityReport | HealthCheckResult
    ) -> None:
        """Process and display results. Override for custom processing."""
        pass  # Default implementation does nothing - subclasses may override

    @abstractmethod
    def create_error_result(
        self, ctx: RecoveryContext, errors: list[str]
    ) -> DiagnosticResult | BoundaryCheckResult | ActivityReport | HealthCheckResult:
        """Create an error result object."""


class DiagnosticStrategy(RecoveryStrategy):
    """Strategy for running comprehensive diagnostics on an instance."""

    def gather_data(self, ctx: RecoveryContext) -> DiagnosticResult:
        """Gather diagnostic information."""
        result = DiagnosticResult(instance_id=ctx.instance_id)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Check git status
            task = progress.add_task("Checking git status...", total=None)
            self._check_git_status(result)
            progress.remove_task(task)

            # Check recent commits
            task = progress.add_task("Analyzing commit history...", total=None)
            self._check_commit_history(result, ctx.instance_id)
            progress.remove_task(task)

            # Check open PRs
            task = progress.add_task("Checking open PRs...", total=None)
            self._check_open_prs(result, ctx.instance_id)
            progress.remove_task(task)

            # Check test status
            task = progress.add_task("Running quick tests...", total=None)
            self._check_test_status(result, ctx.instance_id)
            progress.remove_task(task)

            # Check dependencies
            task = progress.add_task("Checking dependencies...", total=None)
            self._check_dependencies(result, ctx.config)
            progress.remove_task(task)

            # Check for conflicts
            task = progress.add_task("Checking for conflicts...", total=None)
            self._check_merge_conflicts(result)
            progress.remove_task(task)

        # Set overall success
        result.success = not (
            result.missing_dependencies or result.merge_conflicts or result.errors
        )
        return result

    def _check_git_status(self, result: DiagnosticResult) -> None:
        """Check git status for uncommitted changes."""
        returncode, stdout, _ = run_command(["git", "status", "--porcelain"])
        if returncode == 0 and stdout:
            result.uncommitted_changes = stdout.strip().split("\n")[:MAX_FILES_DISPLAY]

    def _check_commit_history(self, result: DiagnosticResult, instance_id: str) -> None:
        """Check recent commit history."""
        cmd = [
            "git",
            "log",
            f"--grep={instance_id}",
            "--oneline",
            f"-{DEFAULT_COMMIT_LIMIT}",
            "--format=%H|%s|%an|%ad",
            "--date=relative",
        ]
        returncode, stdout, _ = run_command(cmd)

        if returncode == 0:
            for line in stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= GIT_LOG_COMMIT_PARTS:
                        result.recent_commits.append(
                            {
                                "hash": parts[0][:7],
                                "message": parts[1],
                                "author": parts[2],
                                "date": parts[3],
                            }
                        )

    def _check_open_prs(self, result: DiagnosticResult, instance_id: str) -> None:
        """Check for open pull requests."""
        cmd = [
            "gh",
            "pr",
            "list",
            "--search",
            instance_id,
            "--json",
            "number,title,state,author,createdAt",
        ]
        returncode, stdout, _ = run_command(cmd)

        if returncode == 0:
            with contextlib.suppress(json.JSONDecodeError):
                result.open_prs = json.loads(stdout) if stdout else []

    def _check_test_status(self, result: DiagnosticResult, instance_id: str) -> None:
        """Check test status."""
        test_cmd = ["poetry", "run", "pytest", "-m", instance_id, "--co", "-q"]
        returncode, stdout, _ = run_command(test_cmd)

        if returncode == 0:
            result.test_count = len([line for line in stdout.split("\n") if "test_" in line])

    def _check_dependencies(self, result: DiagnosticResult, config: InstanceConfig) -> None:
        """Check if all dependencies are installed."""
        for dep in config.dependencies:
            check_cmd = ["poetry", "show", dep]
            returncode, _, _ = run_command(check_cmd)
            if returncode != 0:
                result.missing_dependencies.append(dep)

    def _check_merge_conflicts(self, result: DiagnosticResult) -> None:
        """Check for merge conflicts."""
        conflict_cmd = ["git", "diff", "--name-only", "--diff-filter=U"]
        returncode, stdout, _ = run_command(conflict_cmd)

        if returncode == 0 and stdout:
            result.merge_conflicts = stdout.strip().split("\n")

    def process_results(self, result: DiagnosticResult) -> None:
        """Display diagnostic results."""
        if result.uncommitted_changes:
            console.print("\n[yellow]⚠️  Uncommitted changes detected:[/yellow]")
            for line in result.uncommitted_changes:
                console.print(f"  {line}")

        if result.recent_commits:
            console.print(f"\n[cyan]Recent commits for {result.instance_id}:[/cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Hash", style="dim")
            table.add_column("Message")
            table.add_column("Author")
            table.add_column("Date")

            for commit in result.recent_commits[:MAX_DISPLAYED_RESULTS]:
                table.add_row(
                    commit["hash"], commit["message"][:50], commit["author"], commit["date"]
                )
            console.print(table)

        if result.open_prs:
            console.print(f"\n[cyan]Open PRs for {result.instance_id}:[/cyan]")
            for pr in result.open_prs[:MAX_DISPLAYED_RESULTS]:
                console.print(f"  • PR #{pr['number']}: {pr['title']}")

        console.print("\n[cyan]Test Status:[/cyan]")
        console.print(f"  • Found {result.test_count} tests for {result.instance_id}")

        if result.missing_dependencies:
            console.print("\n[red]❌ Missing dependencies:[/red]")
            for dep in result.missing_dependencies:
                console.print(f"  • {dep}")
        else:
            console.print("\n[green]✅ All dependencies installed[/green]")

        if result.merge_conflicts:
            console.print("\n[red]❌ Merge conflicts detected:[/red]")
            for file in result.merge_conflicts:
                console.print(f"  • {file}")

    def create_error_result(self, ctx: RecoveryContext, errors: list[str]) -> DiagnosticResult:
        """Create error diagnostic result."""
        return DiagnosticResult(instance_id=ctx.instance_id, success=False, errors=errors)


class BoundaryCheckStrategy(RecoveryStrategy):
    """Strategy for checking instance boundary violations."""

    def gather_data(self, ctx: RecoveryContext) -> BoundaryCheckResult:
        """Gather boundary check information."""
        result = BoundaryCheckResult(instance_id=ctx.instance_id)

        # Check owned paths
        self._check_owned_paths(result, ctx.config)

        # Check for violations
        self._check_boundary_violations(result, ctx.config)

        result.success = not result.violations
        return result

    def _check_owned_paths(self, result: BoundaryCheckResult, config: InstanceConfig) -> None:
        """Check owned paths and count files."""
        for path in config.paths:
            if Path(path).exists():
                file_count = len(list(Path(path).rglob("*.py")))
                result.owned_paths.append({"path": path, "exists": True, "file_count": file_count})
            else:
                result.owned_paths.append({"path": path, "exists": False, "file_count": 0})

    def _check_boundary_violations(
        self, result: BoundaryCheckResult, config: InstanceConfig
    ) -> None:
        """Check current changes for boundary violations."""
        cmd = ["git", "diff", "--name-only", "HEAD"]
        returncode, stdout, _ = run_command(cmd)

        if returncode != 0 or not stdout:
            return

        for file in stdout.strip().split("\n"):
            if not file.endswith(".py"):
                continue

            is_allowed = any(file.startswith(path) for path in config.paths)
            if not is_allowed:
                result.violations.append(file)

    def process_results(self, result: BoundaryCheckResult) -> None:
        """Display boundary check results."""
        console.print(f"\n[bold]Instance:[/bold] {result.instance_id}")
        console.print("\n[bold]Owned Paths:[/bold]")

        for path_info in result.owned_paths:
            if path_info["exists"]:
                console.print(f"  ✅ {path_info['path']} ({path_info['file_count']} Python files)")
            else:
                console.print(f"  ❌ {path_info['path']} (not found)")

        console.print("\n[bold]Checking current changes for violations...[/bold]")
        if result.violations:
            console.print("[red]❌ Boundary violations detected:[/red]")
            for file in result.violations:
                console.print(f"  • {file}")
        else:
            console.print("[green]✅ No boundary violations[/green]")

    def create_error_result(self, ctx: RecoveryContext, errors: list[str]) -> BoundaryCheckResult:
        """Create error boundary check result."""
        return BoundaryCheckResult(instance_id=ctx.instance_id, success=False, errors=errors)


class ActivityAnalysisStrategy(RecoveryStrategy):
    """Strategy for analyzing instance activity over time."""

    def __init__(self, days: int = 7) -> None:
        """Initialize with number of days to analyze."""
        self.days = days

    def gather_data(self, ctx: RecoveryContext) -> ActivityReport:
        """Gather activity information."""
        result = ActivityReport(instance_id=ctx.instance_id, days_analyzed=self.days)

        # Get commit activity
        self._analyze_commit_activity(result, ctx.instance_id)

        # Get PR activity
        self._analyze_pr_activity(result, ctx.instance_id)

        # Get file change statistics
        self._analyze_file_changes(result, ctx.config)

        return result

    def _analyze_commit_activity(self, result: ActivityReport, instance_id: str) -> None:
        """Analyze commit activity."""
        since_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")
        cmd = [
            "git",
            "log",
            f"--since={since_date}",
            f"--grep={instance_id}",
            "--format=%H|%s|%an|%ad",
            "--date=short",
        ]
        returncode, stdout, _ = run_command(cmd)

        if returncode != 0:
            return

        for line in stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= GIT_LOG_COMMIT_PARTS:
                date = parts[3]
                result.commits_by_date[date] = result.commits_by_date.get(date, 0) + 1

    def _analyze_pr_activity(self, result: ActivityReport, instance_id: str) -> None:
        """Analyze PR activity."""
        cmd = [
            "gh",
            "pr",
            "list",
            "--search",
            instance_id,
            "--json",
            "number,title,state,author,createdAt",
        ]
        returncode, stdout, _ = run_command(cmd)

        if returncode == 0:
            with contextlib.suppress(json.JSONDecodeError):
                result.open_prs = json.loads(stdout) if stdout else []

    def _analyze_file_changes(self, result: ActivityReport, config: InstanceConfig) -> None:
        """Analyze file change statistics."""
        since_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        for path in config.paths:
            if not Path(path).exists():
                continue

            cmd = ["git", "log", f"--since={since_date}", "--format=", "--numstat", "--", path]
            returncode, stdout, _ = run_command(cmd)

            if returncode != 0:
                continue

            lines_added = 0
            lines_removed = 0
            for line in stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                try:
                    lines_added += int(parts[0])
                    lines_removed += int(parts[1])
                except ValueError:
                    pass

            result.file_changes[path] = {"added": lines_added, "removed": lines_removed}

    def process_results(self, result: ActivityReport) -> None:
        """Display activity report."""
        if result.commits_by_date:
            console.print("\n[cyan]Commit Activity:[/cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Date")
            table.add_column("Commits", justify="right")
            table.add_column("Graph")

            for date in sorted(result.commits_by_date.keys(), reverse=True):
                count = result.commits_by_date[date]
                graph_width = 20
                graph = "█" * min(count * 2, graph_width)
                table.add_row(date, str(count), f"[green]{graph}[/green]")

            console.print(table)

        if result.open_prs:
            console.print(f"\n[cyan]Open PRs ({len(result.open_prs)}):[/cyan]")
            for pr in result.open_prs[:MAX_DISPLAYED_RESULTS]:
                console.print(f"  • PR #{pr['number']}: {pr['title']}")

        console.print("\n[cyan]File Change Statistics:[/cyan]")
        for path, changes in result.file_changes.items():
            console.print(f"  {path}:")
            console.print(
                f"    [green]+{changes['added']}[/green] / [red]-{changes['removed']}[/red] lines"
            )

    def create_error_result(self, ctx: RecoveryContext, errors: list[str]) -> ActivityReport:
        """Create error activity report."""
        return ActivityReport(instance_id=ctx.instance_id, days_analyzed=self.days, errors=errors)


class HealthCheckStrategy(RecoveryStrategy):
    """Strategy for running health checks on an instance."""

    def gather_data(self, ctx: RecoveryContext) -> HealthCheckResult:
        """Gather health check information."""
        result = HealthCheckResult(instance_id=ctx.instance_id)

        with console.status("Running health checks..."):
            # Check paths exist
            self._check_paths(result, ctx.config, ctx.auto_fix)

            # Check for __init__.py files
            self._check_init_files(result, ctx.config, ctx.auto_fix)

            # Check dependencies
            self._check_dependencies(result, ctx.config, ctx.auto_fix, ctx.instance_id)

        result.success = not result.issues_found or (ctx.auto_fix and result.issues_fixed)
        return result

    def _check_paths(
        self, result: HealthCheckResult, config: InstanceConfig, auto_fix: bool
    ) -> None:
        """Check if paths exist."""
        result.paths_checked = len(config.paths)

        for path in config.paths:
            if not Path(path).exists():
                issue = f"Path does not exist: {path}"
                result.issues_found.append(issue)

                if auto_fix:
                    Path(path).mkdir(parents=True, exist_ok=True)
                    result.issues_fixed.append(issue)

    def _check_init_files(
        self, result: HealthCheckResult, config: InstanceConfig, auto_fix: bool
    ) -> None:
        """Check for __init__.py files."""
        for path in config.paths:
            if not Path(path).exists():
                continue

            init_file = Path(path) / "__init__.py"
            if not init_file.exists():
                issue = f"Missing __init__.py: {path}"
                result.issues_found.append(issue)

                if auto_fix:
                    init_file.touch()
                    result.issues_fixed.append(issue)

    def _check_dependencies(
        self,
        result: HealthCheckResult,
        config: InstanceConfig,
        auto_fix: bool,
        instance_id: str,
    ) -> None:
        """Check dependencies."""
        result.dependencies_checked = len(config.dependencies)

        for dep in config.dependencies:
            cmd = ["poetry", "show", dep]
            returncode, _, _ = run_command(cmd)

            if returncode != 0:
                issue = f"Missing dependency: {dep}"
                result.issues_found.append(issue)

                if auto_fix:
                    install_cmd = ["poetry", "install", "--extras", instance_id]
                    run_command(install_cmd, capture=False)
                    result.issues_fixed.append(issue)

    def process_results(self, result: HealthCheckResult) -> None:
        """Display health check results."""
        if result.issues_found:
            console.print("\n[red]Issues found:[/red]")
            for issue in result.issues_found:
                console.print(f"  ❌ {issue}")

            if result.issues_fixed:
                console.print("\n[yellow]Attempted fixes. Please verify.[/yellow]")
        else:
            console.print("\n[green]✅ All health checks passed![/green]")

    def create_error_result(self, ctx: RecoveryContext, errors: list[str]) -> HealthCheckResult:
        """Create error health check result."""
        return HealthCheckResult(instance_id=ctx.instance_id, success=False, errors=errors)
