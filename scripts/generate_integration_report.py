#!/usr/bin/env python3
"""
Generate Integration Test Report for MIA RAG System

Processes test results and creates a comprehensive integration report.
"""

import click
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def parse_junit_xml(junit_file: str) -> Dict:
    """Parse JUnit XML test results."""
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()

        # Extract test suite information
        testsuite = root if root.tag == 'testsuite' else root.find('testsuite')

        if not testsuite:
            return {
                'tests': 0,
                'failures': 0,
                'errors': 0,
                'skipped': 0,
                'time': 0.0,
                'test_cases': []
            }

        results = {
            'tests': int(testsuite.get('tests', 0)),
            'failures': int(testsuite.get('failures', 0)),
            'errors': int(testsuite.get('errors', 0)),
            'skipped': int(testsuite.get('skipped', 0)),
            'time': float(testsuite.get('time', 0.0)),
            'test_cases': []
        }

        # Extract individual test cases
        for testcase in testsuite.findall('.//testcase'):
            case_info = {
                'name': testcase.get('name'),
                'classname': testcase.get('classname'),
                'time': float(testcase.get('time', 0.0)),
                'status': 'passed'
            }

            # Check for failures
            failure = testcase.find('failure')
            if failure is not None:
                case_info['status'] = 'failed'
                case_info['failure_message'] = failure.get('message', '')
                case_info['failure_type'] = failure.get('type', '')

            # Check for errors
            error = testcase.find('error')
            if error is not None:
                case_info['status'] = 'error'
                case_info['error_message'] = error.get('message', '')
                case_info['error_type'] = error.get('type', '')

            # Check if skipped
            if testcase.find('skipped') is not None:
                case_info['status'] = 'skipped'

            results['test_cases'].append(case_info)

        return results

    except Exception as e:
        console.print(f"[red]Error parsing JUnit XML: {e}[/red]")
        return {
            'tests': 0,
            'failures': 0,
            'errors': 0,
            'skipped': 0,
            'time': 0.0,
            'test_cases': []
        }


def parse_coverage_xml(coverage_file: str) -> Dict:
    """Parse coverage XML report."""
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Extract overall coverage
        coverage_data = {
            'line_rate': float(root.get('line-rate', 0.0)),
            'branch_rate': float(root.get('branch-rate', 0.0)),
            'lines_covered': int(root.get('lines-covered', 0)),
            'lines_valid': int(root.get('lines-valid', 0)),
            'packages': []
        }

        # Extract package-level coverage
        for package in root.findall('.//package'):
            pkg_info = {
                'name': package.get('name'),
                'line_rate': float(package.get('line-rate', 0.0)),
                'branch_rate': float(package.get('branch-rate', 0.0)),
            }
            coverage_data['packages'].append(pkg_info)

        return coverage_data

    except Exception as e:
        console.print(f"[red]Error parsing coverage XML: {e}[/red]")
        return {
            'line_rate': 0.0,
            'branch_rate': 0.0,
            'lines_covered': 0,
            'lines_valid': 0,
            'packages': []
        }


def generate_markdown_report(
    junit_results: Dict,
    coverage_data: Optional[Dict],
    merge_report: Optional[str]
) -> str:
    """Generate a markdown report from test results."""
    report = []

    # Header
    report.append("# Integration Test Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")

    # Merge Report Section
    if merge_report:
        report.append("## Branch Merge Report")
        report.append("")
        report.append(merge_report)
        report.append("")

    # Test Results Summary
    report.append("## Test Results Summary")
    report.append("")

    total_tests = junit_results['tests']
    passed = total_tests - junit_results['failures'] - junit_results['errors'] - junit_results['skipped']
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    report.append(f"- **Total Tests**: {total_tests}")
    report.append(f"- **Passed**: {passed} ({pass_rate:.1f}%)")
    report.append(f"- **Failed**: {junit_results['failures']}")
    report.append(f"- **Errors**: {junit_results['errors']}")
    report.append(f"- **Skipped**: {junit_results['skipped']}")
    report.append(f"- **Execution Time**: {junit_results['time']:.2f} seconds")
    report.append("")

    # Test Status Icon
    if junit_results['failures'] == 0 and junit_results['errors'] == 0:
        report.append("###  All Tests Passed!")
    else:
        report.append("### L Test Failures Detected")
    report.append("")

    # Coverage Summary
    if coverage_data:
        report.append("## Coverage Summary")
        report.append("")

        line_coverage = coverage_data['line_rate'] * 100
        branch_coverage = coverage_data['branch_rate'] * 100

        report.append(f"- **Line Coverage**: {line_coverage:.1f}%")
        report.append(f"- **Branch Coverage**: {branch_coverage:.1f}%")
        report.append(f"- **Lines Covered**: {coverage_data['lines_covered']}/{coverage_data['lines_valid']}")
        report.append("")

        if line_coverage >= 80:
            report.append("###  Coverage Target Met (e80%)")
        else:
            report.append(f"###   Coverage Below Target ({line_coverage:.1f}% < 80%)")
        report.append("")

    # Failed Tests Details
    failed_tests = [tc for tc in junit_results['test_cases'] if tc['status'] == 'failed']
    if failed_tests:
        report.append("## Failed Tests")
        report.append("")

        for test in failed_tests[:10]:  # Show first 10 failures
            report.append(f"### L {test['name']}")
            report.append(f"- **Class**: {test['classname']}")
            report.append(f"- **Type**: {test.get('failure_type', 'Unknown')}")
            report.append(f"- **Message**: {test.get('failure_message', 'No message')}")
            report.append("")

        if len(failed_tests) > 10:
            report.append(f"*... and {len(failed_tests) - 10} more failures*")
            report.append("")

    # Error Tests Details
    error_tests = [tc for tc in junit_results['test_cases'] if tc['status'] == 'error']
    if error_tests:
        report.append("## Test Errors")
        report.append("")

        for test in error_tests[:5]:  # Show first 5 errors
            report.append(f"### =¥ {test['name']}")
            report.append(f"- **Class**: {test['classname']}")
            report.append(f"- **Type**: {test.get('error_type', 'Unknown')}")
            report.append(f"- **Message**: {test.get('error_message', 'No message')}")
            report.append("")

        if len(error_tests) > 5:
            report.append(f"*... and {len(error_tests) - 5} more errors*")
            report.append("")

    # Instance Performance (if we can detect it)
    instance_tests = {}
    for test in junit_results['test_cases']:
        # Try to extract instance from test name or class
        for i in range(1, 7):
            if f'instance{i}' in test['classname'].lower() or f'instance{i}' in test['name'].lower():
                instance = f'instance{i}'
                if instance not in instance_tests:
                    instance_tests[instance] = {'passed': 0, 'failed': 0, 'time': 0.0}

                if test['status'] == 'passed':
                    instance_tests[instance]['passed'] += 1
                else:
                    instance_tests[instance]['failed'] += 1
                instance_tests[instance]['time'] += test['time']
                break

    if instance_tests:
        report.append("## Performance by Instance")
        report.append("")
        report.append("| Instance | Passed | Failed | Time (s) |")
        report.append("|----------|--------|--------|----------|")

        for instance in sorted(instance_tests.keys()):
            stats = instance_tests[instance]
            status = "" if stats['failed'] == 0 else "L"
            report.append(f"| {status} {instance} | {stats['passed']} | {stats['failed']} | {stats['time']:.2f} |")

        report.append("")

    # Recommendations
    report.append("## Recommendations")
    report.append("")

    if junit_results['failures'] > 0 or junit_results['errors'] > 0:
        report.append("### Immediate Actions Required:")
        report.append("")
        report.append("1. Review failed tests and identify root causes")
        report.append("2. Check integration branch for merge conflicts")
        report.append("3. Coordinate with affected instances for fixes")
        report.append("4. Re-run integration tests after fixes")
        report.append("")

    if coverage_data and coverage_data['line_rate'] * 100 < 80:
        report.append("### Coverage Improvements Needed:")
        report.append("")
        report.append("1. Add unit tests for uncovered code")
        report.append("2. Review integration test scenarios")
        report.append("3. Ensure all instances meet 80% coverage requirement")
        report.append("")

    # Footer
    report.append("---")
    report.append("*This report was automatically generated by the integration testing pipeline.*")

    return "\n".join(report)


@click.command()
@click.option('--junit', required=True, help='Path to JUnit XML test results')
@click.option('--coverage', help='Path to coverage XML report')
@click.option('--merge-report', help='Merge report text')
@click.option('--output', default='integration_report.md', help='Output file path')
@click.option('--console-output', is_flag=True, help='Also print to console')
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
        console.print("\n" + "="*50)
        console.print(report)

    # Summary table
    console.print("\n[bold]Quick Summary:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_column("Status")

    total_tests = junit_results['tests']
    passed = total_tests - junit_results['failures'] - junit_results['errors'] - junit_results['skipped']

    table.add_row(
        "Tests Passed",
        f"{passed}/{total_tests}",
        "[green][/green]" if junit_results['failures'] == 0 else "[red]L[/red]"
    )

    if coverage_data:
        coverage_pct = coverage_data['line_rate'] * 100
        table.add_row(
            "Coverage",
            f"{coverage_pct:.1f}%",
            "[green][/green]" if coverage_pct >= 80 else "[yellow] [/yellow]"
        )

    table.add_row(
        "Execution Time",
        f"{junit_results['time']:.1f}s",
        "[green][/green]" if junit_results['time'] < 1800 else "[yellow] [/yellow]"
    )

    console.print(table)


if __name__ == "__main__":
    main()