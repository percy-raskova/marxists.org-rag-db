"""Domain models for instance recovery operations.

This module defines the core data structures used in instance recovery,
diagnostics, and health checks.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InstanceConfig:
    """Configuration for a specific instance.

    Attributes:
        instance_id: Unique identifier (e.g., "instance1")
        name: Human-readable name
        paths: List of owned filesystem paths
        test_markers: List of pytest markers for this instance
        dependencies: List of required package names
    """

    instance_id: str
    name: str
    paths: list[str]
    test_markers: list[str]
    dependencies: list[str]


@dataclass
class DiagnosticResult:
    """Results from running diagnostics on an instance.

    Attributes:
        instance_id: Instance being diagnosed
        success: Overall diagnostic success
        uncommitted_changes: List of uncommitted file paths
        recent_commits: List of recent commit information
        open_prs: List of open pull requests
        test_count: Number of tests found for this instance
        missing_dependencies: List of missing package dependencies
        merge_conflicts: List of files with merge conflicts
        errors: List of error messages encountered
        timestamp: When the diagnostic was run
    """

    instance_id: str
    success: bool = True
    uncommitted_changes: list[str] = field(default_factory=list)
    recent_commits: list[dict[str, str]] = field(default_factory=list)
    open_prs: list[dict[str, Any]] = field(default_factory=list)
    test_count: int = 0
    missing_dependencies: list[str] = field(default_factory=list)
    merge_conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BoundaryCheckResult:
    """Results from checking instance boundary violations.

    Attributes:
        instance_id: Instance being checked
        success: Whether boundaries are clean
        owned_paths: List of paths owned by this instance with file counts
        violations: List of files violating boundary rules
        errors: List of error messages
    """

    instance_id: str
    success: bool = True
    owned_paths: list[dict[str, Any]] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ActivityReport:
    """Results from analyzing instance activity.

    Attributes:
        instance_id: Instance being analyzed
        days_analyzed: Number of days in the analysis window
        commits_by_date: Mapping of date to commit count
        open_prs: List of open pull requests
        file_changes: Mapping of path to lines added/removed
        errors: List of error messages
    """

    instance_id: str
    days_analyzed: int
    commits_by_date: dict[str, int] = field(default_factory=dict)
    open_prs: list[dict[str, Any]] = field(default_factory=list)
    file_changes: dict[str, dict[str, int]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class HealthCheckResult:
    """Results from health check operations.

    Attributes:
        instance_id: Instance being checked
        success: Whether all health checks passed
        issues_found: List of issue descriptions
        issues_fixed: List of issues that were auto-fixed
        paths_checked: Number of paths verified
        dependencies_checked: Number of dependencies verified
        errors: List of error messages
    """

    instance_id: str
    success: bool = True
    issues_found: list[str] = field(default_factory=list)
    issues_fixed: list[str] = field(default_factory=list)
    paths_checked: int = 0
    dependencies_checked: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecoveryContext:
    """Context information for recovery operations.

    Attributes:
        instance_id: Instance to recover
        config: Instance configuration
        backup_path: Optional path to backup file
        target_state: Target git commit/state
        auto_fix: Whether to automatically fix issues
        created_at: When this context was created
    """

    instance_id: str
    config: InstanceConfig
    backup_path: Path | None = None
    target_state: str = "HEAD"
    auto_fix: bool = False
    created_at: datetime = field(default_factory=datetime.now)
