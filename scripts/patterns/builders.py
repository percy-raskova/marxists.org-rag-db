"""Builder pattern for generating markdown reports."""

from abc import ABC, abstractmethod
from datetime import datetime

from scripts.domain.metrics import CoverageMetrics, TestMetrics


class MarkdownSection(ABC):
    """Base class for report sections using Template Method pattern."""

    @abstractmethod
    def should_render(self) -> bool:
        """Determine if this section should be included."""

    @abstractmethod
    def render_content(self) -> list[str]:
        """Generate markdown lines for this section."""

    def render(self) -> list[str]:
        """Template method for rendering."""
        if not self.should_render():
            return []
        return self.render_content()


class HeaderSection(MarkdownSection):
    """Renders the report header."""

    def __init__(self, timestamp: datetime | None = None):
        self.timestamp = timestamp or datetime.now()

    def should_render(self) -> bool:
        return True

    def render_content(self) -> list[str]:
        return [
            "# Integration Test Report",
            f"\n**Generated**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
        ]


class TestSummarySection(MarkdownSection):
    """Renders test results summary."""

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics

    def should_render(self) -> bool:
        return True

    def render_content(self) -> list[str]:
        m = self.metrics
        status_icon = "✅" if not m.has_failures else "❌"
        status_text = "All Tests Passed!" if not m.has_failures else "Test Failures Detected"

        return [
            "## Test Results Summary",
            "",
            f"- **Total Tests**: {m.total}",
            f"- **Passed**: {m.passed} ({m.pass_rate:.1f}%)",
            f"- **Failed**: {m.failed}",
            f"- **Errors**: {m.errors}",
            f"- **Skipped**: {m.skipped}",
            f"- **Execution Time**: {m.execution_time:.2f} seconds",
            "",
            f"### {status_icon} {status_text}",
            "",
        ]


class CoverageSection(MarkdownSection):
    """Renders coverage summary."""

    def __init__(self, metrics: CoverageMetrics | None):
        self.metrics = metrics

    def should_render(self) -> bool:
        return self.metrics is not None

    def render_content(self) -> list[str]:
        if not self.metrics:
            return []

        m = self.metrics
        status_icon = "✅" if m.meets_threshold else "⚠️"
        status_text = (
            "Coverage Target Met (≥80%)"
            if m.meets_threshold
            else f"Coverage Below Target ({m.line_percentage:.1f}% < 80%)"
        )

        return [
            "## Coverage Summary",
            "",
            f"- **Line Coverage**: {m.line_percentage:.1f}%",
            f"- **Branch Coverage**: {m.branch_percentage:.1f}%",
            f"- **Lines Covered**: {m.lines_covered}/{m.lines_valid}",
            "",
            f"### {status_icon} {status_text}",
            "",
        ]


class MergeReportSection(MarkdownSection):
    """Renders merge report section."""

    def __init__(self, merge_report: str | None):
        self.merge_report = merge_report

    def should_render(self) -> bool:
        return self.merge_report is not None

    def render_content(self) -> list[str]:
        return ["## Branch Merge Report", "", self.merge_report or "", ""]


class FailedTestsSection(MarkdownSection):
    """Renders failed tests details."""

    MAX_FAILURES_SHOWN = 10

    def __init__(self, test_cases: list[dict]):
        self.failed_tests = [tc for tc in test_cases if tc["status"] == "failed"]

    def should_render(self) -> bool:
        return len(self.failed_tests) > 0

    def render_content(self) -> list[str]:
        lines = ["## Failed Tests", ""]

        for test in self.failed_tests[: self.MAX_FAILURES_SHOWN]:
            lines.extend(
                [
                    f"### ❌ {test['name']}",
                    f"- **Class**: {test['classname']}",
                    f"- **Type**: {test.get('failure_type', 'Unknown')}",
                    f"- **Message**: {test.get('failure_message', 'No message')}",
                    "",
                ]
            )

        if len(self.failed_tests) > self.MAX_FAILURES_SHOWN:
            remaining = len(self.failed_tests) - self.MAX_FAILURES_SHOWN
            lines.append(f"*... and {remaining} more failures*")
            lines.append("")

        return lines


class ErrorTestsSection(MarkdownSection):
    """Renders test errors details."""

    MAX_ERRORS_SHOWN = 5

    def __init__(self, test_cases: list[dict]):
        self.error_tests = [tc for tc in test_cases if tc["status"] == "error"]

    def should_render(self) -> bool:
        return len(self.error_tests) > 0

    def render_content(self) -> list[str]:
        lines = ["## Test Errors", ""]

        for test in self.error_tests[: self.MAX_ERRORS_SHOWN]:
            lines.extend(
                [
                    f"### ⚠️ {test['name']}",
                    f"- **Class**: {test['classname']}",
                    f"- **Type**: {test.get('error_type', 'Unknown')}",
                    f"- **Message**: {test.get('error_message', 'No message')}",
                    "",
                ]
            )

        if len(self.error_tests) > self.MAX_ERRORS_SHOWN:
            remaining = len(self.error_tests) - self.MAX_ERRORS_SHOWN
            lines.append(f"*... and {remaining} more errors*")
            lines.append("")

        return lines


class InstancePerformanceSection(MarkdownSection):
    """Renders instance-specific performance metrics."""

    def __init__(self, test_cases: list[dict]):
        self.instance_tests = self._analyze_instance_tests(test_cases)

    def _analyze_instance_tests(self, test_cases: list[dict]) -> dict:
        instance_tests = {}
        for test in test_cases:
            for i in range(1, 7):
                instance_id = f"instance{i}"
                if instance_id in test["classname"].lower() or instance_id in test["name"].lower():
                    if instance_id not in instance_tests:
                        instance_tests[instance_id] = {"passed": 0, "failed": 0, "time": 0.0}

                    if test["status"] == "passed":
                        instance_tests[instance_id]["passed"] += 1
                    else:
                        instance_tests[instance_id]["failed"] += 1
                    instance_tests[instance_id]["time"] += test["time"]
                    break
        return instance_tests

    def should_render(self) -> bool:
        return len(self.instance_tests) > 0

    def render_content(self) -> list[str]:
        lines = [
            "## Performance by Instance",
            "",
            "| Instance | Passed | Failed | Time (s) |",
            "|----------|--------|--------|----------|",
        ]

        for instance in sorted(self.instance_tests.keys()):
            stats = self.instance_tests[instance]
            status = "✅" if stats["failed"] == 0 else "❌"
            lines.append(
                f"| {status} {instance} | {stats['passed']} | {stats['failed']} | {stats['time']:.2f} |"
            )

        lines.append("")
        return lines


class RecommendationsSection(MarkdownSection):
    """Renders recommendations based on test and coverage results."""

    def __init__(self, test_metrics: TestMetrics, coverage_metrics: CoverageMetrics | None):
        self.test_metrics = test_metrics
        self.coverage_metrics = coverage_metrics

    def should_render(self) -> bool:
        return True

    def render_content(self) -> list[str]:
        lines = ["## Recommendations", ""]

        has_recommendations = False

        if self.test_metrics.has_failures:
            has_recommendations = True
            lines.extend(
                [
                    "### Immediate Actions Required:",
                    "",
                    "1. Review failed tests and identify root causes",
                    "2. Check integration branch for merge conflicts",
                    "3. Coordinate with affected instances for fixes",
                    "4. Re-run integration tests after fixes",
                    "",
                ]
            )

        if self.coverage_metrics and not self.coverage_metrics.meets_threshold:
            has_recommendations = True
            lines.extend(
                [
                    "### Coverage Improvements Needed:",
                    "",
                    "1. Add unit tests for uncovered code",
                    "2. Review integration test scenarios",
                    "3. Ensure all instances meet 80% coverage requirement",
                    "",
                ]
            )

        if not has_recommendations:
            lines.extend(["All metrics look good! ✅", ""])

        lines.extend(
            [
                "---",
                "*This report was automatically generated by the integration testing pipeline.*",
            ]
        )

        return lines


class ReportBuilder:
    """Builder for constructing markdown reports."""

    def __init__(self):
        self.sections: list[MarkdownSection] = []

    def add_section(self, section: MarkdownSection) -> "ReportBuilder":
        """Add a section to the report."""
        self.sections.append(section)
        return self

    def build(self) -> str:
        """Construct final report as markdown string."""
        all_lines = []
        for section in self.sections:
            all_lines.extend(section.render())
        return "\n".join(all_lines)


def create_integration_report(
    junit_results: dict, coverage_data: dict | None, merge_report: str | None
) -> str:
    """Factory function to create a complete integration report."""
    test_metrics = TestMetrics.from_junit(junit_results)
    coverage_metrics = CoverageMetrics.from_xml(coverage_data) if coverage_data else None

    builder = ReportBuilder()
    builder.add_section(HeaderSection())

    if merge_report:
        builder.add_section(MergeReportSection(merge_report))

    builder.add_section(TestSummarySection(test_metrics))
    builder.add_section(CoverageSection(coverage_metrics))
    builder.add_section(FailedTestsSection(junit_results["test_cases"]))
    builder.add_section(ErrorTestsSection(junit_results["test_cases"]))
    builder.add_section(InstancePerformanceSection(junit_results["test_cases"]))
    builder.add_section(RecommendationsSection(test_metrics, coverage_metrics))

    return builder.build()
