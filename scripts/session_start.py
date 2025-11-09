#!/usr/bin/env python3
"""
Start a new work session for an instance.

This script initializes a work session, sets up the environment,
and creates a session log for tracking progress.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class SessionManager:
    """Manage work sessions for instances."""

    WORK_LOGS_DIR = Path("work-logs")
    INSTANCE_FILE = Path(".instance")
    SESSION_FILE = Path(".session")

    def __init__(self):
        """Initialize session manager."""
        self.ensure_work_logs_dir()
        self.hostname = socket.gethostname()

    def ensure_work_logs_dir(self):
        """Ensure work-logs directory exists."""
        self.WORK_LOGS_DIR.mkdir(exist_ok=True)
        (self.WORK_LOGS_DIR / ".gitignore").write_text("*.log\n*.json\n!example-*.json\n")

    def detect_instance(self) -> str:
        """Detect current instance or prompt for selection."""
        # Check if already set
        if self.INSTANCE_FILE.exists():
            return self.INSTANCE_FILE.read_text().strip()

        # Check environment variable
        if "MIA_INSTANCE" in os.environ:
            return os.environ["MIA_INSTANCE"]

        # Prompt user
        print("🤖 Which instance are you?")
        print("1. Storage & Pipeline")
        print("2. Embeddings")
        print("3. Weaviate")
        print("4. API")
        print("5. MCP")
        print("6. Monitoring")

        choice = input("\nEnter instance number (1-6): ").strip()

        instance_map = {
            "1": "instance1",
            "2": "instance2",
            "3": "instance3",
            "4": "instance4",
            "5": "instance5",
            "6": "instance6",
        }

        if choice not in instance_map:
            print("❌ Invalid choice")
            sys.exit(1)

        instance = instance_map[choice]
        self.INSTANCE_FILE.write_text(instance)
        return instance

    def get_git_info(self) -> dict:
        """Get current git information."""
        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            ).stdout.strip()[:8]

            status = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
            ).stdout.strip()

            has_changes = bool(status)

            return {
                "branch": branch,
                "commit": commit,
                "has_changes": has_changes,
                "changed_files": len(status.split("\n")) if status else 0,
            }
        except subprocess.CalledProcessError:
            return {
                "branch": "unknown",
                "commit": "unknown",
                "has_changes": False,
                "changed_files": 0,
            }

    def create_session(self, instance: str, task_description: str | None = None) -> dict:
        """Create a new work session."""
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        git_info = self.get_git_info()

        session_data = {
            "session_id": session_id,
            "instance": instance,
            "hostname": self.hostname,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "task_description": task_description,
            "git": git_info,
            "files_modified": [],
            "tests_run": [],
            "commands_executed": [],
            "notes": [],
            "status": "active",
        }

        # Create session file
        session_file = self.WORK_LOGS_DIR / f"{instance}-{session_id}.json"
        session_file.write_text(json.dumps(session_data, indent=2))

        # Store current session reference
        self.SESSION_FILE.write_text(str(session_file))

        return session_data

    def setup_environment(self, instance: str):
        """Set up environment for the instance."""
        print(f"🔧 Setting up environment for {instance}...")

        # Set environment variables
        os.environ["MIA_INSTANCE"] = instance
        os.environ["MIA_ENV"] = "development"

        # Install instance-specific dependencies
        instance_map = {
            "instance1": "storage",
            "instance2": "embeddings",
            "instance3": "weaviate",
            "instance4": "api",
            "instance5": "mcp",
            "instance6": "monitoring",
        }

        extra = instance_map.get(instance)
        if extra:
            print(f"📦 Installing {extra} dependencies...")
            try:
                subprocess.run(
                    ["poetry", "install", "--with", "dev", "--extras", extra], check=True
                )
                print(f"✅ Dependencies installed for {extra}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install dependencies for {extra}")

    def create_branch(self, instance: str, feature_name: str | None = None):
        """Create a feature branch for the instance."""
        if not feature_name:
            feature_name = input("Enter feature name (e.g., batch-processor): ").strip()

        if not feature_name:
            print("⚠️  No feature name provided, staying on current branch")
            return

        branch_name = f"{instance}/{feature_name}"

        try:
            # Check if branch exists
            existing = subprocess.run(
                ["git", "branch", "--list", branch_name], capture_output=True, text=True, check=True
            ).stdout.strip()

            if existing:
                # Switch to existing branch
                subprocess.run(["git", "checkout", branch_name], check=True)
                print(f"✅ Switched to existing branch: {branch_name}")
            else:
                # Create new branch
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                print(f"✅ Created and switched to branch: {branch_name}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create/switch branch: {e}")

    def print_session_info(self, session_data: dict):
        """Print session information."""
        print("\n" + "=" * 60)
        print("🚀 Work Session Started")
        print("=" * 60)
        print(f"Instance: {session_data['instance']}")
        print(f"Session ID: {session_data['session_id']}")
        print(f"Git Branch: {session_data['git']['branch']}")
        print(f"Git Commit: {session_data['git']['commit']}")
        if session_data["task_description"]:
            print(f"Task: {session_data['task_description']}")
        print("=" * 60)

    def print_next_steps(self, instance: str):
        """Print next steps for the instance."""
        next_steps = {
            "instance1": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/storage.py for contracts",
                "3. Write tests in tests/unit/instance1_storage/",
                "4. Implement GCS storage in src/mia_rag/storage/",
                "5. Run: mise run test:instance1",
            ],
            "instance2": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/embeddings.py for contracts",
                "3. Write tests in tests/unit/instance2_embeddings/",
                "4. Implement Runpod integration in src/mia_rag/embeddings/",
                "5. Run: mise run test:instance2",
            ],
            "instance3": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/vector_db.py for contracts",
                "3. Write tests in tests/unit/instance3_weaviate/",
                "4. Implement Weaviate client in src/mia_rag/weaviate/",
                "5. Run: mise run test:instance3",
            ],
            "instance4": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/api.py for contracts",
                "3. Write tests in tests/unit/instance4_api/",
                "4. Implement FastAPI server in src/mia_rag/api/",
                "5. Run: mise run test:instance4",
            ],
            "instance5": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/mcp.py for contracts",
                "3. Write tests in tests/unit/instance5_mcp/",
                "4. Implement MCP server in src/mia_rag/mcp/",
                "5. Run: mise run test:instance5",
            ],
            "instance6": [
                "1. Review INSTANCE-BOUNDARIES.md for your scope",
                "2. Check src/mia_rag/interfaces/monitoring.py for contracts",
                "3. Write tests in tests/unit/instance6_monitoring/",
                "4. Implement monitoring in src/mia_rag/monitoring/",
                "5. Run: mise run test:instance6",
            ],
        }

        print("\n📋 Next Steps:")
        for step in next_steps.get(instance, []):
            print(f"  {step}")

        print("\n🔧 Useful Commands:")
        print(f"  mise run test:{instance}      # Run your tests")
        print("  mise run check:boundaries    # Check boundaries")
        print("  mise run update:log          # Update work log")
        print("  mise run session:end         # End session")
        print()


def main():
    """Main entry point for session start."""
    parser = argparse.ArgumentParser(description="Start a new work session for an instance")
    parser.add_argument(
        "--instance",
        help="Specify the instance (e.g., instance1)",
        choices=[f"instance{i}" for i in range(1, 7)],
    )
    parser.add_argument("--task", help="Task description for this session")
    parser.add_argument("--feature", help="Feature name for creating branch")
    parser.add_argument("--no-branch", action="store_true", help="Don't create a feature branch")
    parser.add_argument("--no-deps", action="store_true", help="Don't install dependencies")

    args = parser.parse_args()

    manager = SessionManager()

    # Detect or set instance
    if args.instance:
        instance = args.instance
        manager.INSTANCE_FILE.write_text(instance)
    else:
        instance = manager.detect_instance()

    # Create session
    session_data = manager.create_session(instance, args.task)

    # Setup environment
    if not args.no_deps:
        manager.setup_environment(instance)

    # Create branch
    if not args.no_branch:
        manager.create_branch(instance, args.feature)

    # Print session info
    manager.print_session_info(session_data)
    manager.print_next_steps(instance)

    print("✨ Happy coding! Use 'mise run session:end' when done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
