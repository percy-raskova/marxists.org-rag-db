"""Value objects for test and coverage metrics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TestMetrics:
    """Immutable value object for test metrics."""

    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    execution_time: float

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        return (self.passed / self.total * 100) if self.total > 0 else 0.0

    @property
    def has_failures(self) -> bool:
        """Check if there are any failures or errors."""
        return self.failed > 0 or self.errors > 0

    @classmethod
    def from_junit(cls, junit_results: dict) -> "TestMetrics":
        """Create TestMetrics from JUnit XML results."""
        total = junit_results["tests"]
        failed = junit_results["failures"]
        errors = junit_results["errors"]
        skipped = junit_results["skipped"]

        return cls(
            total=total,
            passed=total - failed - errors - skipped,
            failed=failed,
            errors=errors,
            skipped=skipped,
            execution_time=junit_results["time"],
        )


@dataclass(frozen=True)
class CoverageMetrics:
    """Immutable value object for coverage metrics."""

    line_rate: float
    branch_rate: float
    lines_covered: int
    lines_valid: int

    COVERAGE_THRESHOLD = 80.0

    @property
    def line_percentage(self) -> float:
        """Get line coverage as percentage."""
        return self.line_rate * 100

    @property
    def branch_percentage(self) -> float:
        """Get branch coverage as percentage."""
        return self.branch_rate * 100

    @property
    def meets_threshold(self) -> bool:
        """Check if coverage meets the 80% threshold."""
        return self.line_percentage >= self.COVERAGE_THRESHOLD

    @classmethod
    def from_xml(cls, coverage_data: dict) -> "CoverageMetrics":
        """Create CoverageMetrics from coverage XML data."""
        return cls(
            line_rate=coverage_data["line_rate"],
            branch_rate=coverage_data["branch_rate"],
            lines_covered=coverage_data["lines_covered"],
            lines_valid=coverage_data["lines_valid"],
        )
