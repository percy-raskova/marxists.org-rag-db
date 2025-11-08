#!/usr/bin/env python3
"""
Show comprehensive project status across all instances.

This script provides a holistic view of the project's development status,
showing progress, test coverage, and health for all 6 instances.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


class ProjectStatusViewer:
    """View comprehensive project status."""

    WORK_LOGS_DIR = Path("work-logs")

    INSTANCE_NAMES = {
        "instance1": "Storage & Pipeline",
        "instance2": "Embeddings",
        "instance3": "Weaviate",
        "instance4": "API",
        "instance5": "MCP",
        "instance6": "Monitoring"
    }

    def __init__(self):
        """Initialize status viewer."""
        self.project_root = Path.cwd()

    def get_git_status(self) -> dict:
        """Get current git repository status."""
        try:
            # Current branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            # Get all branches for instances
            all_branches = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip().split("\n")

            instance_branches = {}
            for b in all_branches:
                b = b.strip().replace("* ", "")
                for instance in self.INSTANCE_NAMES:
                    if instance in b:
                        if instance not in instance_branches:
                            instance_branches[instance] = []
                        instance_branches[instance].append(b)

            # Uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            # Recent commits
            recent_commits = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip().split("\n")

            return {
                "current_branch": branch,
                "instance_branches": instance_branches,
                "has_changes": bool(status),
                "changed_files": len(status.split("\n")) if status else 0,
                "recent_commits": recent_commits[:5]
            }

        except subprocess.CalledProcessError:
            return {
                "current_branch": "unknown",
                "instance_branches": {},
                "has_changes": False,
                "changed_files": 0,
                "recent_commits": []
            }

    def get_test_coverage(self, instance: str) -> dict:
        """Get test coverage for an instance."""
        coverage_file = Path("htmlcov") / f"d_{instance.replace('/', '_')}_index.html"
        coverage_xml = Path("coverage.xml")

        # Try to get coverage from last test run
        if coverage_xml.exists():
            try:
                # Simple XML parsing (would use xml.etree in production)
                content = coverage_xml.read_text()
                if f'filename="src/mia_rag/{instance}' in content:
                    # Extract coverage percentage (simplified)
                    import re
                    match = re.search(r'line-rate="([\d.]+)"', content)
                    if match:
                        return {
                            "coverage": float(match.group(1)) * 100,
                            "has_tests": True
                        }
            except:
                pass

        # Check if tests exist
        test_dir = Path(f"tests/unit/{instance}_*/")
        test_files = list(Path("tests/unit/").glob(f"{instance}_*/*.py"))

        return {
            "coverage": 0.0,
            "has_tests": len(test_files) > 0,
            "test_count": len(test_files)
        }

    def get_source_stats(self, instance: str) -> dict:
        """Get source code statistics for an instance."""
        source_patterns = {
            "instance1": ["storage", "pipeline"],
            "instance2": ["embeddings"],
            "instance3": ["weaviate"],
            "instance4": ["api"],
            "instance5": ["mcp"],
            "instance6": ["monitoring"]
        }

        patterns = source_patterns.get(instance, [])
        total_files = 0
        total_lines = 0

        for pattern in patterns:
            src_dir = Path("src/mia_rag") / pattern
            if src_dir.exists():
                py_files = list(src_dir.glob("**/*.py"))
                total_files += len(py_files)

                for file in py_files:
                    try:
                        lines = file.read_text().count("\n")
                        total_lines += lines
                    except:
                        pass

        return {
            "files": total_files,
            "lines": total_lines,
            "exists": total_files > 0
        }

    def get_work_sessions(self, instance: str = None) -> list[dict]:
        """Get work session history."""
        sessions = []

        if not self.WORK_LOGS_DIR.exists():
            return sessions

        pattern = f"{instance}-*.json" if instance else "*.json"

        for session_file in self.WORK_LOGS_DIR.glob(pattern):
            try:
                data = json.loads(session_file.read_text())
                sessions.append({
                    "instance": data.get("instance"),
                    "session_id": data.get("session_id"),
                    "start_time": data.get("start_time"),
                    "end_time": data.get("end_time"),
                    "status": data.get("status", "unknown"),
                    "task": data.get("task_description", "No description"),
                    "files_modified": len(data.get("files_modified", []))
                })
            except:
                pass

        # Sort by start time
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        return sessions

    def calculate_instance_progress(self, instance: str) -> tuple[int, str]:
        """Calculate progress percentage for an instance."""
        progress_score = 0
        status = "not_started"

        # Check if source files exist
        src_stats = self.get_source_stats(instance)
        if src_stats["exists"]:
            progress_score += 30
            status = "in_progress"

        # Check test coverage
        test_coverage = self.get_test_coverage(instance)
        if test_coverage["has_tests"]:
            progress_score += 20

        if test_coverage["coverage"] > 0:
            # Scale coverage to 0-50 points
            progress_score += int(test_coverage["coverage"] * 0.5)

            if test_coverage["coverage"] >= 80:
                status = "ready"
            elif test_coverage["coverage"] >= 50:
                status = "testing"

        # Check recent activity
        sessions = self.get_work_sessions(instance)
        if sessions:
            # Had recent activity
            latest = sessions[0]
            if latest.get("start_time"):
                start = datetime.fromisoformat(latest["start_time"])
                if datetime.now() - start < timedelta(days=7):
                    status = "active"

        return min(progress_score, 100), status

    def print_project_overview(self):
        """Print overall project status."""
        print("\n" + "="*80)
        print("🚀 MARXIST RAG SYSTEM - PROJECT STATUS")
        print("="*80)

        # Git status
        git_status = self.get_git_status()
        print("\n📦 Git Status:")
        print(f"  Current Branch: {git_status['current_branch']}")
        print(f"  Uncommitted Changes: {git_status['changed_files']} files")

        # Overall progress
        total_progress = 0
        instance_statuses = {}

        for instance in self.INSTANCE_NAMES:
            progress, status = self.calculate_instance_progress(instance)
            total_progress += progress
            instance_statuses[instance] = (progress, status)

        overall_progress = total_progress // len(self.INSTANCE_NAMES)

        # Progress bar
        bar_length = 40
        filled = int(bar_length * overall_progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\n📊 Overall Progress: [{bar}] {overall_progress}%")

        # Instance summary
        print("\n🤖 Instance Status:")
        status_emojis = {
            "not_started": "⚪",
            "in_progress": "🟡",
            "testing": "🟠",
            "active": "🟢",
            "ready": "✅"
        }

        for instance, name in self.INSTANCE_NAMES.items():
            progress, status = instance_statuses[instance]
            emoji = status_emojis.get(status, "❓")

            # Mini progress bar
            mini_bar_length = 10
            mini_filled = int(mini_bar_length * progress / 100)
            mini_bar = "▰" * mini_filled + "▱" * (mini_bar_length - mini_filled)

            print(f"  {emoji} {instance}: {mini_bar} {progress}% - {name}")

    def print_instance_details(self, instance: str):
        """Print detailed status for a specific instance."""
        if instance not in self.INSTANCE_NAMES:
            print(f"❌ Unknown instance: {instance}")
            return

        print(f"\n{'='*60}")
        print(f"📊 {instance.upper()} - {self.INSTANCE_NAMES[instance]}")
        print(f"{'='*60}")

        # Progress
        progress, status = self.calculate_instance_progress(instance)
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n📈 Progress: [{bar}] {progress}%")
        print(f"   Status: {status}")

        # Source statistics
        src_stats = self.get_source_stats(instance)
        print("\n📝 Source Code:")
        print(f"   Files: {src_stats['files']}")
        print(f"   Lines: {src_stats['lines']}")

        # Test coverage
        test_coverage = self.get_test_coverage(instance)
        print("\n🧪 Testing:")
        print(f"   Test Files: {test_coverage.get('test_count', 0)}")
        print(f"   Coverage: {test_coverage['coverage']:.1f}%")

        # Work sessions
        sessions = self.get_work_sessions(instance)
        print(f"\n📅 Work Sessions: {len(sessions)} total")

        if sessions:
            print("\n   Recent Sessions:")
            for session in sessions[:3]:
                start = datetime.fromisoformat(session["start_time"])
                formatted_date = start.strftime("%Y-%m-%d %H:%M")
                status_icon = "✅" if session["status"] == "completed" else "🔄"
                print(f"   {status_icon} {formatted_date}: {session['task'][:50]}")

        # Git branches
        git_status = self.get_git_status()
        branches = git_status["instance_branches"].get(instance, [])
        if branches:
            print("\n🌳 Git Branches:")
            for branch in branches[:5]:
                print(f"   • {branch}")

    def print_work_history(self):
        """Print work session history across all instances."""
        print("\n" + "="*60)
        print("📅 WORK SESSION HISTORY")
        print("="*60)

        sessions = self.get_work_sessions()

        if not sessions:
            print("\nNo work sessions found.")
            return

        # Group by date
        by_date = {}
        for session in sessions:
            if session.get("start_time"):
                date = session["start_time"].split("T")[0]
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(session)

        # Show recent dates
        for date in sorted(by_date.keys(), reverse=True)[:7]:
            print(f"\n📅 {date}:")
            for session in by_date[date]:
                instance = session.get("instance", "unknown")
                status_icon = "✅" if session.get("status") == "completed" else "🔄"
                print(f"  {status_icon} {instance}: {session.get('task', 'No description')[:60]}")

    def generate_health_report(self) -> dict:
        """Generate health report for the project."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "instances": {}
        }

        for instance in self.INSTANCE_NAMES:
            progress, status = self.calculate_instance_progress(instance)
            src_stats = self.get_source_stats(instance)
            test_coverage = self.get_test_coverage(instance)

            report["instances"][instance] = {
                "name": self.INSTANCE_NAMES[instance],
                "progress": progress,
                "status": status,
                "source_files": src_stats["files"],
                "source_lines": src_stats["lines"],
                "test_coverage": test_coverage["coverage"],
                "has_tests": test_coverage["has_tests"]
            }

        # Calculate overall health
        total_progress = sum(i["progress"] for i in report["instances"].values())
        report["overall_progress"] = total_progress // len(self.INSTANCE_NAMES)

        # Identify blockers
        report["blockers"] = []
        for instance, data in report["instances"].items():
            if data["progress"] < 20:
                report["blockers"].append(f"{instance} not started")
            elif data["has_tests"] and data["test_coverage"] < 50:
                report["blockers"].append(f"{instance} needs more tests")

        return report

    def export_status_json(self, output_file: Path):
        """Export status to JSON."""
        report = self.generate_health_report()
        output_file.write_text(json.dumps(report, indent=2))
        print(f"📄 Status exported to {output_file}")


def main():
    """Main entry point for status viewer."""
    parser = argparse.ArgumentParser(
        description="Show comprehensive project status"
    )
    parser.add_argument(
        "--instance",
        help="Show details for specific instance",
        choices=list(ProjectStatusViewer.INSTANCE_NAMES.keys())
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show work session history"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Generate health report"
    )
    parser.add_argument(
        "--export",
        help="Export status to JSON file",
        type=Path
    )

    args = parser.parse_args()

    viewer = ProjectStatusViewer()

    if args.export:
        viewer.export_status_json(args.export)
    elif args.instance:
        viewer.print_instance_details(args.instance)
    elif args.history:
        viewer.print_work_history()
    elif args.health:
        report = viewer.generate_health_report()
        print("\n🏥 HEALTH REPORT")
        print("="*60)
        print(f"Overall Progress: {report['overall_progress']}%")
        if report["blockers"]:
            print("\n⚠️  Blockers:")
            for blocker in report["blockers"]:
                print(f"  • {blocker}")
        else:
            print("\n✅ No blockers identified!")
    else:
        # Default: show overview
        viewer.print_project_overview()
        print("\n💡 Tips:")
        print("  • Use --instance <name> for detailed instance status")
        print("  • Use --history to see work session history")
        print("  • Use --health for a health report")

    return 0


if __name__ == "__main__":
    sys.exit(main())
