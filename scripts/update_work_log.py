#!/usr/bin/env python3
"""
Update work log during an active session.

This script allows adding notes, TODOs, and progress updates
to the current work session log.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class WorkLogUpdater:
    """Update work logs during active sessions."""

    SESSION_FILE = Path(".session")
    WORK_LOGS_DIR = Path("work-logs")

    def __init__(self):
        """Initialize work log updater."""
        if not self.SESSION_FILE.exists():
            print("❌ No active session found. Start with 'mise run session:start'")
            sys.exit(1)

        self.session_path = Path(self.SESSION_FILE.read_text().strip())
        if not self.session_path.exists():
            print(f"❌ Session file not found: {self.session_path}")
            sys.exit(1)

        self.session_data = json.loads(self.session_path.read_text())

    def add_note(self, note: str, category: str = "general"):
        """Add a note to the session log."""
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "note": note
        }

        if "notes" not in self.session_data:
            self.session_data["notes"] = []

        self.session_data["notes"].append(note_entry)
        self.save_session()

        print(f"✅ Note added to session log ({category})")

    def add_todo(self, todo: str, priority: str = "normal"):
        """Add a TODO item to the session."""
        todo_entry = {
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "todo": todo,
            "completed": False
        }

        if "todos" not in self.session_data:
            self.session_data["todos"] = []

        self.session_data["todos"].append(todo_entry)
        self.save_session()

        print(f"✅ TODO added ({priority} priority)")

    def mark_todo_complete(self, todo_index: int):
        """Mark a TODO as complete."""
        if "todos" not in self.session_data or not self.session_data["todos"]:
            print("❌ No TODOs in session")
            return

        if todo_index < 0 or todo_index >= len(self.session_data["todos"]):
            print(f"❌ Invalid TODO index: {todo_index}")
            return

        self.session_data["todos"][todo_index]["completed"] = True
        self.session_data["todos"][todo_index]["completed_at"] = datetime.now().isoformat()
        self.save_session()

        print(f"✅ TODO #{todo_index} marked as complete")

    def add_command(self, command: str, output: str = None, success: bool = True):
        """Log a command that was executed."""
        command_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "success": success,
            "output": output[:500] if output else None  # Limit output size
        }

        if "commands_executed" not in self.session_data:
            self.session_data["commands_executed"] = []

        self.session_data["commands_executed"].append(command_entry)
        self.save_session()

        print("✅ Command logged")

    def add_test_result(self, test_name: str, passed: bool, duration: float = None):
        """Log test execution results."""
        test_entry = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "passed": passed,
            "duration_seconds": duration
        }

        if "tests_run" not in self.session_data:
            self.session_data["tests_run"] = []

        self.session_data["tests_run"].append(test_entry)
        self.save_session()

        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    def add_file_modified(self, file_path: str, change_type: str = "modified"):
        """Track a file modification."""
        if "files_modified" not in self.session_data:
            self.session_data["files_modified"] = []

        # Avoid duplicates
        if file_path not in self.session_data["files_modified"]:
            self.session_data["files_modified"].append(file_path)
            self.save_session()
            print(f"✅ Tracked: {file_path} ({change_type})")

    def record_progress(self, milestone: str, percentage: int):
        """Record progress milestone."""
        progress_entry = {
            "timestamp": datetime.now().isoformat(),
            "milestone": milestone,
            "percentage": percentage
        }

        if "progress" not in self.session_data:
            self.session_data["progress"] = []

        self.session_data["progress"].append(progress_entry)
        self.save_session()

        # Progress bar
        bar_length = 20
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"📊 Progress: [{bar}] {percentage}% - {milestone}")

    def show_status(self):
        """Show current session status."""
        print("\n" + "=" * 60)
        print("📋 Session Status")
        print("=" * 60)
        print(f"Instance: {self.session_data['instance']}")
        print(f"Session ID: {self.session_data['session_id']}")
        print(f"Started: {self.session_data['start_time']}")

        if self.session_data.get("task_description"):
            print(f"Task: {self.session_data['task_description']}")

        # Calculate duration
        start_time = datetime.fromisoformat(self.session_data["start_time"])
        duration = datetime.now() - start_time
        hours = int(duration.total_seconds() / 3600)
        minutes = int((duration.total_seconds() % 3600) / 60)
        print(f"Duration: {hours}h {minutes}m")

        # Show statistics
        print("\n📊 Statistics:")
        print(f"  Files modified: {len(self.session_data.get('files_modified', []))}")
        print(f"  Notes: {len(self.session_data.get('notes', []))}")
        print(f"  Commands run: {len(self.session_data.get('commands_executed', []))}")
        print(f"  Tests run: {len(self.session_data.get('tests_run', []))}")

        # Show TODOs
        todos = self.session_data.get("todos", [])
        if todos:
            print("\n📝 TODOs:")
            for i, todo in enumerate(todos):
                status = "✅" if todo["completed"] else "⬜"
                priority_icon = "🔴" if todo["priority"] == "high" else "🟡" if todo["priority"] == "medium" else ""
                print(f"  {status} [{i}] {priority_icon} {todo['todo']}")

        # Show recent notes
        notes = self.session_data.get("notes", [])
        if notes:
            print("\n📝 Recent Notes:")
            for note in notes[-3:]:  # Show last 3 notes
                timestamp = datetime.fromisoformat(note["timestamp"]).strftime("%H:%M")
                print(f"  [{timestamp}] {note['category']}: {note['note'][:80]}")

        # Show progress
        progress = self.session_data.get("progress", [])
        if progress:
            latest = progress[-1]
            bar_length = 20
            filled = int(bar_length * latest["percentage"] / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\n📊 Progress: [{bar}] {latest['percentage']}%")
            print(f"  Latest: {latest['milestone']}")

        print("=" * 60)

    def run_tests(self):
        """Run tests for current instance and log results."""
        instance = self.session_data["instance"]
        print(f"🧪 Running tests for {instance}...")

        try:
            result = subprocess.run(
                ["poetry", "run", "pytest", f"tests/unit/{instance}_*/", "-v"],
                capture_output=True,
                text=True,
                timeout=60, check=False
            )

            # Parse output for test results
            output_lines = result.stdout.split("\n")
            for line in output_lines:
                if "PASSED" in line or "FAILED" in line:
                    # Extract test name
                    parts = line.split("::")
                    if len(parts) >= 2:
                        test_name = "::".join(parts[1:]).split()[0]
                        passed = "PASSED" in line
                        self.add_test_result(test_name, passed)

            self.add_command(
                f"pytest tests/unit/{instance}_*/",
                result.stdout[-500:],  # Last 500 chars
                result.returncode == 0
            )

            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print(f"❌ Some tests failed (exit code: {result.returncode})")

        except subprocess.TimeoutExpired:
            print("❌ Tests timed out")
            self.add_command(f"pytest tests/unit/{instance}_*/", "Timeout", False)
        except Exception as e:
            print(f"❌ Error running tests: {e}")

    def save_session(self):
        """Save session data to file."""
        self.session_path.write_text(json.dumps(self.session_data, indent=2))

    def interactive_update(self):
        """Interactive mode for updating the log."""
        while True:
            print("\n📝 Work Log Update Menu:")
            print("1. Add note")
            print("2. Add TODO")
            print("3. Mark TODO complete")
            print("4. Record progress")
            print("5. Run tests")
            print("6. Show status")
            print("0. Exit")

            choice = input("\nChoice: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                note = input("Note: ").strip()
                category = input("Category (general/bug/idea/review): ").strip() or "general"
                self.add_note(note, category)
            elif choice == "2":
                todo = input("TODO: ").strip()
                priority = input("Priority (low/normal/medium/high): ").strip() or "normal"
                self.add_todo(todo, priority)
            elif choice == "3":
                self.show_status()  # Show TODOs
                index = input("TODO index to complete: ").strip()
                if index.isdigit():
                    self.mark_todo_complete(int(index))
            elif choice == "4":
                milestone = input("Milestone description: ").strip()
                percentage = input("Percentage complete (0-100): ").strip()
                if percentage.isdigit():
                    self.record_progress(milestone, int(percentage))
            elif choice == "5":
                self.run_tests()
            elif choice == "6":
                self.show_status()
            else:
                print("❌ Invalid choice")


def main():
    """Main entry point for work log updater."""
    parser = argparse.ArgumentParser(
        description="Update work log during active session"
    )
    parser.add_argument(
        "--note",
        help="Add a note to the session"
    )
    parser.add_argument(
        "--todo",
        help="Add a TODO item"
    )
    parser.add_argument(
        "--complete-todo",
        type=int,
        help="Mark TODO at index as complete"
    )
    parser.add_argument(
        "--progress",
        help="Record progress milestone"
    )
    parser.add_argument(
        "--percentage",
        type=int,
        help="Progress percentage (0-100)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show session status"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run tests for current instance"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive update mode"
    )

    args = parser.parse_args()

    updater = WorkLogUpdater()

    if args.interactive:
        updater.interactive_update()
    elif args.note:
        updater.add_note(args.note)
    elif args.todo:
        updater.add_todo(args.todo)
    elif args.complete_todo is not None:
        updater.mark_todo_complete(args.complete_todo)
    elif args.progress and args.percentage is not None:
        updater.record_progress(args.progress, args.percentage)
    elif args.test:
        updater.run_tests()
    elif args.status:
        updater.show_status()
    else:
        # Default to showing status
        updater.show_status()
        print("\n💡 Tip: Use --interactive for interactive mode")

    return 0


if __name__ == "__main__":
    sys.exit(main())
