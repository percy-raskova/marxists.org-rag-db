#!/usr/bin/env python3
"""
End a work session and generate summary.

This script ends the current work session, generates a summary,
and optionally commits the work.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class SessionEnder:
    """End and summarize work sessions."""

    SESSION_FILE = Path(".session")
    WORK_LOGS_DIR = Path("work-logs")

    def __init__(self):
        """Initialize session ender."""
        if not self.SESSION_FILE.exists():
            print("❌ No active session found. Start with 'mise run session:start'")
            sys.exit(1)

        self.session_path = Path(self.SESSION_FILE.read_text().strip())
        if not self.session_path.exists():
            print(f"❌ Session file not found: {self.session_path}")
            sys.exit(1)

        self.session_data = json.loads(self.session_path.read_text())

    def get_modified_files(self) -> list:
        """Get list of files modified during session."""
        try:
            # Get all modified files
            result = subprocess.run(
                ["git", "diff", "--name-only", self.session_data["git"]["commit"], "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

            files = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Also get staged files
            staged = (
                subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                .stdout.strip()
                .split("\n")
            )

            # Combine and deduplicate
            all_files = list(set(files + staged))
            all_files = [f for f in all_files if f]  # Remove empty strings

            return all_files

        except subprocess.CalledProcessError:
            return []

    def get_tests_run(self) -> dict:
        """Check for test results."""
        test_results = {"tests_found": False, "coverage": None, "passed": None, "failed": None}

        # Check for pytest cache
        pytest_cache = Path(".pytest_cache")
        if pytest_cache.exists():
            # Check last failed
            lastfailed = pytest_cache / "v" / "cache" / "lastfailed"
            if lastfailed.exists():
                data = json.loads(lastfailed.read_text())
                test_results["tests_found"] = True
                test_results["failed"] = len(data) if isinstance(data, dict) else 0

        # Check for coverage report
        coverage_file = Path("htmlcov") / "index.html"
        if coverage_file.exists():
            # Parse coverage from HTML (simplified)
            try:
                content = coverage_file.read_text()
                if "%" in content:
                    # Extract coverage percentage (this is a simplification)
                    import re

                    match = re.search(r"(\d+)%", content)
                    if match:
                        test_results["coverage"] = int(match.group(1))
            except OSError:
                pass

        return test_results

    def calculate_session_stats(self) -> dict:
        """Calculate session statistics."""
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.session_data["start_time"])
        duration = end_time - start_time

        hours = duration.total_seconds() / 3600
        minutes = (duration.total_seconds() % 3600) / 60

        modified_files = self.get_modified_files()
        test_results = self.get_tests_run()

        # Categorize files
        file_categories = {"source": [], "tests": [], "docs": [], "config": [], "other": []}

        for file in modified_files:
            if file.startswith("src/"):
                file_categories["source"].append(file)
            elif file.startswith("tests/"):
                file_categories["tests"].append(file)
            elif file.startswith("docs/") or file.endswith(".md"):
                file_categories["docs"].append(file)
            elif file in ["pyproject.toml", ".mise.toml", ".env", ".gitignore"]:
                file_categories["config"].append(file)
            else:
                file_categories["other"].append(file)

        return {
            "duration_hours": round(hours, 2),
            "duration_minutes": round(minutes, 0),
            "files_modified": len(modified_files),
            "file_categories": file_categories,
            "test_results": test_results,
            "lines_added": self.get_lines_changed()[0],
            "lines_removed": self.get_lines_changed()[1],
        }

    def get_lines_changed(self) -> tuple:
        """Get number of lines added and removed."""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", self.session_data["git"]["commit"], "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the last line which contains totals
            lines = result.stdout.strip().split("\n")
            if lines:
                last_line = lines[-1]
                import re

                # Look for patterns like "10 insertions(+), 5 deletions(-)"
                insertions = re.search(r"(\d+) insertion", last_line)
                deletions = re.search(r"(\d+) deletion", last_line)

                added = int(insertions.group(1)) if insertions else 0
                removed = int(deletions.group(1)) if deletions else 0

                return added, removed

        except (subprocess.CalledProcessError, KeyError):
            pass

        return 0, 0

    def update_session_file(self, notes: str | None = None, summary: dict | None = None):
        """Update session file with end time and summary."""
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["status"] = "completed"
        self.session_data["files_modified"] = self.get_modified_files()

        if notes:
            self.session_data["notes"].append(
                {"timestamp": datetime.now().isoformat(), "note": notes}
            )

        if summary:
            self.session_data["summary"] = summary

        # Save updated session
        self.session_path.write_text(json.dumps(self.session_data, indent=2))

    def generate_summary(self, stats: dict) -> str:
        """Generate a human-readable summary."""
        summary = []
        summary.append("=" * 60)
        summary.append("📊 Session Summary")
        summary.append("=" * 60)
        summary.append(f"Instance: {self.session_data['instance']}")
        summary.append(f"Session ID: {self.session_data['session_id']}")

        if self.session_data.get("task_description"):
            summary.append(f"Task: {self.session_data['task_description']}")

        summary.append(f"Duration: {stats['duration_hours']}h {stats['duration_minutes']}m")
        summary.append(f"Files Modified: {stats['files_modified']}")

        if stats["lines_added"] or stats["lines_removed"]:
            summary.append(f"Lines: +{stats['lines_added']} -{stats['lines_removed']}")

        # File breakdown
        if stats["files_modified"] > 0:
            summary.append("\n📁 Files Modified:")
            for category, files in stats["file_categories"].items():
                if files:
                    summary.append(f"  {category.capitalize()}: {len(files)} files")
                    if len(files) <= 3:
                        for file in files:
                            summary.append(f"    - {file}")

        # Test results
        if stats["test_results"]["tests_found"]:
            summary.append("\n🧪 Test Results:")
            if stats["test_results"]["coverage"]:
                summary.append(f"  Coverage: {stats['test_results']['coverage']}%")
            if stats["test_results"]["failed"] is not None:
                if stats["test_results"]["failed"] == 0:
                    summary.append("  ✅ All tests passed!")
                else:
                    summary.append(f"  ❌ {stats['test_results']['failed']} tests failed")

        summary.append("=" * 60)

        return "\n".join(summary)

    def suggest_commit_message(self, stats: dict) -> str:
        """Suggest a commit message based on changes."""
        instance_map = {
            "instance1": "storage",
            "instance2": "embeddings",
            "instance3": "weaviate",
            "instance4": "api",
            "instance5": "mcp",
            "instance6": "monitoring",
        }

        component = instance_map.get(self.session_data["instance"], "core")

        # Determine type of change
        if stats["file_categories"]["tests"] and not stats["file_categories"]["source"]:
            change_type = "test"
        elif stats["file_categories"]["docs"] and not stats["file_categories"]["source"]:
            change_type = "docs"
        elif stats["file_categories"]["config"] and not stats["file_categories"]["source"]:
            change_type = "chore"
        else:
            change_type = "feat"  # or "fix" based on context

        # Generate message
        if self.session_data.get("task_description"):
            description = self.session_data["task_description"].lower()
        else:
            description = f"update {component} module"

        return f"{change_type}({component}): {description}"

    def create_commit(self, message: str | None = None):
        """Create a git commit with session information."""
        if not message:
            stats = self.calculate_session_stats()
            message = self.suggest_commit_message(stats)

            print("\n💬 Suggested commit message:")
            print(f"  {message}")
            use_suggested = input("\nUse this message? (y/n/edit): ").strip().lower()

            if use_suggested in ("edit", "e"):
                message = input("Enter commit message: ").strip()
            elif use_suggested not in ("y", "yes"):
                print("Skipping commit")
                return

        try:
            # Add session metadata to commit message
            full_message = f"{message}\n\nSession: {self.session_data['session_id']}\nInstance: {self.session_data['instance']}"

            subprocess.run(["git", "add", "-A"], check=True)
            subprocess.run(["git", "commit", "-m", full_message], check=True)
            print("✅ Changes committed")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit: {e}")


def main():
    """Main entry point for session end."""
    parser = argparse.ArgumentParser(description="End work session and generate summary")
    parser.add_argument("--notes", help="Add notes to the session")
    parser.add_argument("--no-commit", action="store_true", help="Don't offer to commit changes")
    parser.add_argument("--commit-message", help="Commit message to use")

    args = parser.parse_args()

    ender = SessionEnder()

    # Calculate statistics
    stats = ender.calculate_session_stats()

    # Generate and print summary
    summary = ender.generate_summary(stats)
    print(summary)

    # Update session file
    ender.update_session_file(notes=args.notes, summary=stats)

    # Offer to commit
    if not args.no_commit and stats["files_modified"] > 0:
        ender.create_commit(args.commit_message)

    # Clean up session file
    ender.SESSION_FILE.unlink()

    print("\n✨ Session ended successfully!")
    print(f"📄 Session log saved to: {ender.session_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
