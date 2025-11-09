"""Unit tests for instance recovery strategies.

Tests the Template Method pattern implementation for recovery operations.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from scripts.domain.recovery import (
    ActivityReport,
    BoundaryCheckResult,
    DiagnosticResult,
    HealthCheckResult,
    InstanceConfig,
    RecoveryContext,
)
from scripts.patterns.recovery import (
    ActivityAnalysisStrategy,
    BoundaryCheckStrategy,
    DiagnosticStrategy,
    HealthCheckStrategy,
)


@pytest.fixture
def instance_config():
    """Create a test instance configuration."""
    return InstanceConfig(
        instance_id="test_instance",
        name="Test Instance",
        paths=["test/path1", "test/path2"],
        test_markers=["test_marker"],
        dependencies=["dep1", "dep2"],
    )


@pytest.fixture
def recovery_context(instance_config):
    """Create a test recovery context."""
    return RecoveryContext(
        instance_id="test_instance",
        config=instance_config,
    )


class TestDiagnosticStrategy:
    """Tests for DiagnosticStrategy."""

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_success(self, mock_path, mock_run_command, recovery_context):
        """Test successful diagnostic data gathering."""
        # Mock git status - no uncommitted changes
        mock_run_command.side_effect = [
            (0, "", ""),  # git status
            (0, "abc123|test commit|author|2 hours ago\n", ""),  # git log
            (0, "[]", ""),  # gh pr list
            (0, "test_something.py\ntest_other.py\n", ""),  # pytest --co
            (0, "dep1 installed", ""),  # poetry show dep1
            (0, "dep2 installed", ""),  # poetry show dep2
            (0, "", ""),  # git diff --name-only --diff-filter=U
        ]

        strategy = DiagnosticStrategy()
        result = strategy.execute(recovery_context)

        assert isinstance(result, DiagnosticResult)
        assert result.instance_id == "test_instance"
        assert result.success is True
        assert len(result.recent_commits) == 1
        assert result.test_count == 2
        assert len(result.missing_dependencies) == 0
        assert len(result.merge_conflicts) == 0

    @patch("scripts.patterns.recovery.run_command")
    def test_gather_data_with_issues(self, mock_run_command, recovery_context):
        """Test diagnostic with issues detected."""
        # Mock with uncommitted changes, missing deps, and conflicts
        mock_run_command.side_effect = [
            (0, "M file1.py\nM file2.py\n", ""),  # git status - uncommitted
            (0, "", ""),  # git log - no commits
            (0, "[]", ""),  # gh pr list
            (0, "", ""),  # pytest --co
            (1, "", "Package not found"),  # poetry show dep1 - missing
            (0, "dep2 installed", ""),  # poetry show dep2
            (0, "conflict.py\n", ""),  # git diff - merge conflict
        ]

        strategy = DiagnosticStrategy()
        result = strategy.execute(recovery_context)

        assert result.success is False
        assert len(result.uncommitted_changes) > 0
        assert len(result.missing_dependencies) == 1
        assert "dep1" in result.missing_dependencies
        assert len(result.merge_conflicts) == 1

    def test_create_error_result(self, recovery_context):
        """Test error result creation."""
        strategy = DiagnosticStrategy()
        result = strategy.create_error_result(recovery_context, ["test error"])

        assert isinstance(result, DiagnosticResult)
        assert result.success is False
        assert "test error" in result.errors


class TestBoundaryCheckStrategy:
    """Tests for BoundaryCheckStrategy."""

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_no_violations(self, mock_path, mock_run_command, recovery_context):
        """Test boundary check with no violations."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = ["file1.py", "file2.py"]
        mock_path.return_value = mock_path_instance

        # Mock git diff - no changes
        mock_run_command.return_value = (0, "", "")

        strategy = BoundaryCheckStrategy()
        result = strategy.execute(recovery_context)

        assert isinstance(result, BoundaryCheckResult)
        assert result.success is True
        assert len(result.violations) == 0

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_with_violations(self, mock_path, mock_run_command, recovery_context):
        """Test boundary check with violations."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = ["file1.py"]
        mock_path.return_value = mock_path_instance

        # Mock git diff - changes in unauthorized path
        mock_run_command.return_value = (0, "unauthorized/file.py\n", "")

        strategy = BoundaryCheckStrategy()
        result = strategy.execute(recovery_context)

        assert result.success is False
        assert len(result.violations) == 1
        assert "unauthorized/file.py" in result.violations

    def test_create_error_result(self, recovery_context):
        """Test error result creation."""
        strategy = BoundaryCheckStrategy()
        result = strategy.create_error_result(recovery_context, ["test error"])

        assert isinstance(result, BoundaryCheckResult)
        assert result.success is False
        assert "test error" in result.errors


class TestActivityAnalysisStrategy:
    """Tests for ActivityAnalysisStrategy."""

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_with_activity(self, mock_path, mock_run_command, recovery_context):
        """Test activity analysis with commits and PRs."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        # Mock git log for commits
        mock_run_command.side_effect = [
            (0, "abc123|commit 1|author|2024-01-15\ndef456|commit 2|author|2024-01-15\n", ""),
            (0, '[{"number": 1, "title": "Test PR"}]', ""),  # gh pr list
            (0, "10\t5\tfile.py\n", ""),  # git log numstat for path1
            (0, "5\t2\tfile2.py\n", ""),  # git log numstat for path2
        ]

        strategy = ActivityAnalysisStrategy(days=7)
        result = strategy.execute(recovery_context)

        assert isinstance(result, ActivityReport)
        assert result.days_analyzed == 7
        assert len(result.commits_by_date) > 0
        assert "2024-01-15" in result.commits_by_date
        assert result.commits_by_date["2024-01-15"] == 2
        assert len(result.open_prs) == 1

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_no_activity(self, mock_path, mock_run_command, recovery_context):
        """Test activity analysis with no activity."""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_run_command.side_effect = [
            (0, "", ""),  # git log - no commits
            (0, "[]", ""),  # gh pr list - no PRs
            (0, "", ""),  # git log numstat - no changes path1
            (0, "", ""),  # git log numstat - no changes path2
        ]

        strategy = ActivityAnalysisStrategy(days=7)
        result = strategy.execute(recovery_context)

        assert isinstance(result, ActivityReport)
        assert len(result.commits_by_date) == 0
        assert len(result.open_prs) == 0

    def test_create_error_result(self, recovery_context):
        """Test error result creation."""
        strategy = ActivityAnalysisStrategy(days=7)
        result = strategy.create_error_result(recovery_context, ["test error"])

        assert isinstance(result, ActivityReport)
        assert "test error" in result.errors


class TestHealthCheckStrategy:
    """Tests for HealthCheckStrategy."""

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_all_healthy(self, mock_path, mock_run_command, recovery_context):
        """Test health check with all checks passing."""
        # Mock path existence
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_init_file = MagicMock()
        mock_init_file.exists.return_value = True
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_init_file)
        mock_path.return_value = mock_path_instance

        # Mock dependencies installed
        mock_run_command.side_effect = [
            (0, "dep1 installed", ""),
            (0, "dep2 installed", ""),
        ]

        strategy = HealthCheckStrategy()
        result = strategy.execute(recovery_context)

        assert isinstance(result, HealthCheckResult)
        assert result.success is True
        assert len(result.issues_found) == 0

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_with_issues_no_fix(self, mock_path, mock_run_command, recovery_context):
        """Test health check with issues but no auto-fix."""
        # Mock path doesn't exist
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        strategy = HealthCheckStrategy()
        result = strategy.execute(recovery_context)

        assert result.success is False
        assert len(result.issues_found) > 0
        assert len(result.issues_fixed) == 0

    @patch("scripts.patterns.recovery.run_command")
    @patch("scripts.patterns.recovery.Path")
    def test_gather_data_with_auto_fix(self, mock_path, mock_run_command):
        """Test health check with auto-fix enabled."""
        config = InstanceConfig(
            instance_id="test",
            name="Test",
            paths=["test/path"],
            test_markers=["test"],
            dependencies=["missing_dep"],
        )
        context = RecoveryContext(instance_id="test", config=config, auto_fix=True)

        # Mock path doesn't exist initially
        mock_path_instance = MagicMock()
        mock_path_instance.exists.side_effect = [False, True]
        mock_path_instance.mkdir = MagicMock()
        mock_path.return_value = mock_path_instance

        # Mock init file doesn't exist
        mock_init_file = MagicMock()
        mock_init_file.exists.return_value = False
        mock_init_file.touch = MagicMock()
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_init_file)

        # Mock missing dependency
        mock_run_command.side_effect = [
            (1, "", "Package not found"),  # poetry show - missing
            (0, "", ""),  # poetry install - fixes it
        ]

        strategy = HealthCheckStrategy()
        result = strategy.execute(context)

        assert len(result.issues_found) > 0
        assert len(result.issues_fixed) > 0

    def test_create_error_result(self, recovery_context):
        """Test error result creation."""
        strategy = HealthCheckStrategy()
        result = strategy.create_error_result(recovery_context, ["test error"])

        assert isinstance(result, HealthCheckResult)
        assert result.success is False
        assert "test error" in result.errors


class TestRecoveryContext:
    """Tests for RecoveryContext domain model."""

    def test_context_creation(self, instance_config):
        """Test creating a recovery context."""
        ctx = RecoveryContext(instance_id="test", config=instance_config)

        assert ctx.instance_id == "test"
        assert ctx.config == instance_config
        assert ctx.backup_path is None
        assert ctx.target_state == "HEAD"
        assert ctx.auto_fix is False
        assert isinstance(ctx.created_at, datetime)

    def test_context_immutability(self, instance_config):
        """Test that context is immutable (frozen dataclass)."""
        ctx = RecoveryContext(instance_id="test", config=instance_config)

        with pytest.raises((AttributeError, TypeError)):  # Frozen dataclass error
            ctx.instance_id = "modified"  # type: ignore[misc]


class TestDomainModels:
    """Tests for domain model dataclasses."""

    def test_diagnostic_result_defaults(self):
        """Test DiagnosticResult default values."""
        result = DiagnosticResult(instance_id="test")

        assert result.instance_id == "test"
        assert result.success is True
        assert isinstance(result.uncommitted_changes, list)
        assert isinstance(result.recent_commits, list)
        assert isinstance(result.open_prs, list)
        assert result.test_count == 0
        assert isinstance(result.timestamp, datetime)

    def test_boundary_check_result_defaults(self):
        """Test BoundaryCheckResult default values."""
        result = BoundaryCheckResult(instance_id="test")

        assert result.instance_id == "test"
        assert result.success is True
        assert isinstance(result.owned_paths, list)
        assert isinstance(result.violations, list)

    def test_activity_report_defaults(self):
        """Test ActivityReport default values."""
        result = ActivityReport(instance_id="test", days_analyzed=7)

        assert result.instance_id == "test"
        assert result.days_analyzed == 7
        assert isinstance(result.commits_by_date, dict)
        assert isinstance(result.open_prs, list)
        assert isinstance(result.file_changes, dict)

    def test_health_check_result_defaults(self):
        """Test HealthCheckResult default values."""
        result = HealthCheckResult(instance_id="test")

        assert result.instance_id == "test"
        assert result.success is True
        assert isinstance(result.issues_found, list)
        assert isinstance(result.issues_fixed, list)
        assert result.paths_checked == 0
        assert result.dependencies_checked == 0
