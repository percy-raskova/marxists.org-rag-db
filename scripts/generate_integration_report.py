#!/usr/bin/env python3
"""
Generate Integration Test Report for MIA RAG System

Processes test results and creates a comprehensive integration report.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from scripts.patterns.builders import create_integration_report


console = Console()


def parse_junit_xml(junit_file: str) -> dict:
    """Parse JUnit XML test results."""
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()

        # Extract test suite information
        testsuite = root if root.tag == "testsuite" else root.find("testsuite")

        if not testsuite:
            return {
                "tests": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "time": 0.0,
                "test_cases": [],
            }

        results = {
            "tests": int(testsuite.get("tests", 0)),
            "failures": int(testsuite.get("failures", 0)),
            "errors": int(testsuite.get("errors", 0)),
            "skipped": int(testsuite.get("skipped", 0)),
            "time": float(testsuite.get("time", 0.0)),
            "test_cases": [],
        }

        # Extract individual test cases
        for testcase in testsuite.findall(".//testcase"):
            case_info = {
                "name": testcase.get("name"),
                "classname": testcase.get("classname"),
                "time": float(testcase.get("time", 0.0)),
                "status": "passed",
            }

            # Check for failures
            failure = testcase.find("failure")
            if failure is not None:
                case_info["status"] = "failed"
                case_info["failure_message"] = failure.get("message", "")
                case_info["failure_type"] = failure.get("type", "")

            # Check for errors
            error = testcase.find("error")
            if error is not None:
                case_info["status"] = "error"
                case_info["error_message"] = error.get("message", "")
                case_info["error_type"] = error.get("type", "")

            # Check if skipped
            if testcase.find("skipped") is not None:
                case_info["status"] = "skipped"

            results["test_cases"].append(case_info)

        return results

    except Exception as e:
        console.print(f"[red]Error parsing JUnit XML: {e}[/red]")
        return {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "time": 0.0, "test_cases": []}


def parse_coverage_xml(coverage_file: str) -> dict:
    """Parse coverage XML report."""
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Extract overall coverage
        coverage_data = {
            "line_rate": float(root.get("line-rate", 0.0)),
            "branch_rate": float(root.get("branch-rate", 0.0)),
            "lines_covered": int(root.get("lines-covered", 0)),
            "lines_valid": int(root.get("lines-valid", 0)),
            "packages": [],
        }

        # Extract package-level coverage
        for package in root.findall(".//package"):
            pkg_info = {
                "name": package.get("name"),
                "line_rate": float(package.get("line-rate", 0.0)),
                "branch_rate": float(package.get("branch-rate", 0.0)),
            }
            coverage_data["packages"].append(pkg_info)

        return coverage_data

    except Exception as e:
        console.print(f"[red]Error parsing coverage XML: {e}[/red]")
        return {
            "line_rate": 0.0,
            "branch_rate": 0.0,
            "lines_covered": 0,
            "lines_valid": 0,
            "packages": [],
        }


def generate_markdown_report(
    junit_results: dict, coverage_data: dict | None, merge_report: str | None
) -> str:
    """Generate a markdown report from test results using Builder pattern."""
    return create_integration_report(junit_results, coverage_data, merge_report)


@click.command()
@click.option("--junit", required=True, help="Path to JUnit XML test results")
@click.option("--coverage", help="Path to coverage XML report")
@click.option("--merge-report", help="Merge report text")
@click.option("--output", default="integration_report.md", help="Output file path")
@click.option("--console-output", is_flag=True, help="Also print to console")
def main(junit, coverage, merge_report, output, console_output):
    """Generate integration test report from test results."""

    console.print(Panel.fit("[bold cyan]Generating Integration Report[/bold cyan]"))

    # Parse JUnit results
    console.print("Parsing JUnit results...")
    junit_results = parse_junit_xml(junit)

    # Parse coverage if provided
    coverage_data = None
    if coverage:
        console.print("Parsing coverage data...")
        coverage_data = parse_coverage_xml(coverage)

    # Generate report
    console.print("Generating report...")
    report = generate_markdown_report(junit_results, coverage_data, merge_report)

    # Write to file
    output_path = Path(output)
    output_path.write_text(report)
    console.print(f"[green] Report written to {output}[/green]")

    # Print to console if requested
    if console_output:
        console.print("\n" + "=" * 50)
        console.print(report)

    # Summary table
    console.print("\n[bold]Quick Summary:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("Status")

    total_tests = junit_results["tests"]
    passed = (
        total_tests - junit_results["failures"] - junit_results["errors"] - junit_results["skipped"]
    )

    table.add_row(
        "Tests Passed",
        f"{passed}/{total_tests}",
        "[green][/green]" if junit_results["failures"] == 0 else "[red]L[/red]",
    )

    if coverage_data:
        coverage_pct = coverage_data["line_rate"] * 100
        table.add_row(
            "Coverage",
            f"{coverage_pct:.1f}%",
            "[green][/green]" if coverage_pct >= 80 else "[yellow] [/yellow]",
        )

    table.add_row(
        "Execution Time",
        f"{junit_results['time']:.1f}s",
        "[green][/green]" if junit_results["time"] < 1800 else "[yellow] [/yellow]",
    )

    console.print(table)


if __name__ == "__main__":
    main()
