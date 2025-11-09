#!/usr/bin/env python3
"""
Check for boundary violations and potential conflicts between instances.

This script ensures that each instance only modifies files within their boundaries,
preventing conflicts during parallel development.

Author: Persphone Raskova
Repository: https://github.com/percy-raskova/marxists.org-rag-db
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from patterns.ast_utils import extract_imports
from patterns.validators import (
    ValidationContext,
    create_validation_chain,
)


@dataclass
class BoundaryViolation:
    """Represents a boundary violation."""

    instance: str
    file_path: str
    violation_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str


class BoundaryChecker:
    """Check for boundary violations in the codebase."""

    # Instance boundaries definition
    INSTANCE_BOUNDARIES: ClassVar[dict[str, dict]] = {
        "instance1": {
            "owned_paths": [
                "src/mia_rag/storage/",
                "src/mia_rag/pipeline/",
                "tests/unit/instance1_storage/",
                "tests/integration/storage_pipeline/",
                "docs/instance1-storage.md",
            ],
            "allowed_imports": ["src/mia_rag/common/", "src/mia_rag/interfaces/"],
            "instance_id": "instance1-storage",
        },
        "instance2": {
            "owned_paths": [
                "src/mia_rag/embeddings/",
                "tests/unit/instance2_embeddings/",
                "tests/integration/embeddings/",
                "docs/instance2-embeddings.md",
            ],
            "allowed_imports": ["src/mia_rag/common/", "src/mia_rag/interfaces/"],
            "instance_id": "instance2-embeddings",
        },
        "instance3": {
            "owned_paths": [
                "src/mia_rag/weaviate/",
                "tests/unit/instance3_weaviate/",
                "tests/integration/weaviate/",
                "docs/instance3-weaviate.md",
            ],
            "allowed_imports": ["src/mia_rag/common/", "src/mia_rag/interfaces/"],
            "instance_id": "instance3-weaviate",
        },
        "instance4": {
            "owned_paths": [
                "src/mia_rag/api/",
                "tests/unit/instance4_api/",
                "tests/integration/api/",
                "docs/instance4-api.md",
            ],
            "allowed_imports": [
                "src/mia_rag/common/",
                "src/mia_rag/interfaces/",
                "src/mia_rag/weaviate/",  # API can use Weaviate client
            ],
            "instance_id": "instance4-api",
        },
        "instance5": {
            "owned_paths": [
                "src/mia_rag/mcp/",
                "tests/unit/instance5_mcp/",
                "tests/integration/mcp/",
                "docs/instance5-mcp.md",
            ],
            "allowed_imports": [
                "src/mia_rag/common/",
                "src/mia_rag/interfaces/",
                "src/mia_rag/weaviate/",  # MCP can use Weaviate client
            ],
            "instance_id": "instance5-mcp",
        },
        "instance6": {
            "owned_paths": [
                "src/mia_rag/monitoring/",
                "tests/unit/instance6_monitoring/",
                "tests/integration/monitoring/",
                "docs/instance6-monitoring.md",
            ],
            "allowed_imports": ["src/mia_rag/common/", "src/mia_rag/interfaces/"],
            "instance_id": "instance6-monitoring",
        },
    }

    # Shared/common paths that all instances can modify
    COMMON_PATHS: ClassVar[list[str]] = [
        "src/mia_rag/common/",
        "src/mia_rag/interfaces/",
        "tests/contracts/",
        "docs/architecture/",
        "docs/interfaces/",
        ".github/",
        "scripts/",
        "pyproject.toml",
        ".mise.toml",
        "README.md",
        "INSTANCE-BOUNDARIES.md",
        "AI-AGENT-INSTRUCTIONS.md",
    ]

    def __init__(self, auto_mode: bool = False, strict: bool = False):
        """Initialize boundary checker.

        Args:
            auto_mode: If True, automatically detect current instance
            strict: If True, treat warnings as errors
        """
        self.auto_mode = auto_mode
        self.strict = strict
        self.current_instance = self._detect_current_instance() if auto_mode else None
        self.violations: list[BoundaryViolation] = []

    def _detect_current_instance(self) -> str | None:
        """Detect current instance from .instance file or git branch."""
        # Check .instance file
        instance_file = Path(".instance")
        if instance_file.exists():
            return instance_file.read_text().strip()

        # Check git branch
        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            # Extract instance from branch name (e.g., instance1/feature-name)
            if "/" in branch:
                instance_part = branch.split("/")[0]
                if instance_part.startswith("instance"):
                    return instance_part
        except subprocess.CalledProcessError:
            pass

        return None

    def get_modified_files(self) -> list[Path]:
        """Get list of modified files in current git working directory."""
        try:
            # Get staged files
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

            # Get unstaged modified files
            unstaged = (
                subprocess.run(
                    ["git", "diff", "--name-only"], capture_output=True, text=True, check=True
                )
                .stdout.strip()
                .split("\n")
            )

            # Get untracked files
            untracked = (
                subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                .stdout.strip()
                .split("\n")
            )

            # Combine and filter empty strings
            all_files = set(staged + unstaged + untracked)
            all_files.discard("")

            return [Path(f) for f in all_files]

        except subprocess.CalledProcessError as e:
            print(f"Error getting modified files: {e}", file=sys.stderr)
            return []

    def check_file_ownership(self, file_path: Path, instance: str) -> BoundaryViolation | None:
        """Check if an instance is allowed to modify a file."""
        file_str = str(file_path)

        # Check if it's a common path - all instances can modify
        for common_path in self.COMMON_PATHS:
            if file_str.startswith(common_path):
                return None

        # Check if it's in instance's owned paths
        instance_config = self.INSTANCE_BOUNDARIES.get(instance, {})
        owned_paths = instance_config.get("owned_paths", [])

        for owned_path in owned_paths:
            if file_str.startswith(owned_path):
                return None

        # Check if it belongs to another instance
        for other_instance, config in self.INSTANCE_BOUNDARIES.items():
            if other_instance == instance:
                continue

            for other_path in config.get("owned_paths", []):
                if file_str.startswith(other_path):
                    return BoundaryViolation(
                        instance=instance,
                        file_path=file_str,
                        violation_type="ownership",
                        severity="error",
                        message=f"{instance} cannot modify {file_str} (owned by {other_instance})",
                    )

        # File is not in any defined boundary - warning
        return BoundaryViolation(
            instance=instance,
            file_path=file_str,
            violation_type="undefined",
            severity="warning",
            message=f"{file_str} is not in any defined boundary",
        )

    def check_imports(self, file_path: Path, instance: str) -> list[BoundaryViolation]:
        """Check if Python file has valid imports using AST-based validation.

        This method uses the Chain of Responsibility pattern to validate imports,
        replacing the previous string-based approach with AST parsing.

        Args:
            file_path: Path to the Python file to check
            instance: Instance ID doing the import

        Returns:
            List of BoundaryViolation objects for any invalid imports
        """
        violations = []

        # Skip non-Python files
        if file_path.suffix != ".py":
            return violations

        if not file_path.exists():
            return violations

        try:
            # Extract imports using AST
            imports = extract_imports(file_path)

            # Build validation context
            instance_config = self.INSTANCE_BOUNDARIES.get(instance, {})
            all_boundaries = {
                inst: config.get("owned_paths", [])
                for inst, config in self.INSTANCE_BOUNDARIES.items()
            }

            ctx = ValidationContext(
                instance_id=instance,
                owned_paths=set(instance_config.get("owned_paths", [])),
                allowed_imports=set(instance_config.get("allowed_imports", [])),
                all_instance_boundaries=all_boundaries,
            )

            # Create validation chain
            validator = create_validation_chain()

            # Validate each import
            for import_stmt in imports:
                import_violations = validator.handle(import_stmt, ctx)

                # Convert ImportViolation to BoundaryViolation
                for import_violation in import_violations:
                    violations.append(
                        BoundaryViolation(
                            instance=instance,
                            file_path=str(file_path),
                            violation_type="import",
                            severity=import_violation.severity,
                            message=import_violation.message,
                        )
                    )

        except SyntaxError as e:
            violations.append(
                BoundaryViolation(
                    instance=instance,
                    file_path=str(file_path),
                    violation_type="parse_error",
                    severity="warning",
                    message=f"Syntax error in file: {e}",
                )
            )
        except Exception as e:
            violations.append(
                BoundaryViolation(
                    instance=instance,
                    file_path=str(file_path),
                    violation_type="parse_error",
                    severity="warning",
                    message=f"Could not parse file: {e}",
                )
            )

        return violations

    def check_all_boundaries(self) -> tuple[list[BoundaryViolation], bool]:
        """Check all boundaries for current changes.

        Returns:
            Tuple of (violations, success)
        """
        if not self.current_instance:
            print(
                "❌ Cannot detect current instance. Please set with --instance or create .instance file"
            )
            return [], False

        print(f"🔍 Checking boundaries for {self.current_instance}...")

        modified_files = self.get_modified_files()
        if not modified_files:
            print("✅ No modified files to check")
            return [], True

        print(f"📝 Checking {len(modified_files)} modified files...")

        violations = []

        for file_path in modified_files:
            # Check file ownership
            violation = self.check_file_ownership(file_path, self.current_instance)
            if violation:
                violations.append(violation)

            # Check imports
            import_violations = self.check_imports(file_path, self.current_instance)
            violations.extend(import_violations)

        # Sort violations by severity
        violations.sort(key=lambda v: (v.severity != "error", v.file_path))

        return violations, len([v for v in violations if v.severity == "error"]) == 0

    def print_violations(self, violations: list[BoundaryViolation]):
        """Print violations in a formatted way."""
        if not violations:
            print("✅ No boundary violations found!")
            return

        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]
        infos = [v for v in violations if v.severity == "info"]

        if errors:
            print(f"\n❌ {len(errors)} ERROR(S) found:")
            for v in errors:
                print(f"  ❌ {v.message}")

        if warnings:
            print(f"\n⚠️  {len(warnings)} WARNING(S) found:")
            for v in warnings:
                print(f"  ⚠️  {v.message}")

        if infos:
            print(f"\n(i)  {len(infos)} INFO(S) found:")
            for v in infos:
                print(f"  (i)  {v.message}")

    def export_violations_json(self, violations: list[BoundaryViolation], output_file: Path):
        """Export violations to JSON for CI/CD integration."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "instance": self.current_instance,
            "total_violations": len(violations),
            "errors": len([v for v in violations if v.severity == "error"]),
            "warnings": len([v for v in violations if v.severity == "warning"]),
            "violations": [
                {
                    "instance": v.instance,
                    "file": v.file_path,
                    "type": v.violation_type,
                    "severity": v.severity,
                    "message": v.message,
                }
                for v in violations
            ],
        }

        output_file.write_text(json.dumps(data, indent=2))
        print(f"📄 Violations exported to {output_file}")


def main():
    """Main entry point for boundary checking."""
    parser = argparse.ArgumentParser(description="Check for boundary violations between instances")
    parser.add_argument(
        "--instance",
        help="Specify the current instance (e.g., instance1)",
        choices=list(BoundaryChecker.INSTANCE_BOUNDARIES.keys()),
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect current instance from .instance file or git branch",
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--export", help="Export violations to JSON file", type=Path)
    parser.add_argument(
        "--list-boundaries", action="store_true", help="List all instance boundaries"
    )

    args = parser.parse_args()

    # List boundaries mode
    if args.list_boundaries:
        print("📋 Instance Boundaries:")
        print("=" * 60)
        for instance, config in BoundaryChecker.INSTANCE_BOUNDARIES.items():
            print(f"\n{instance} ({config['instance_id']}):")
            print("  Owned paths:")
            for path in config["owned_paths"]:
                print(f"    - {path}")
            print("  Can import from:")
            for path in config["allowed_imports"]:
                print(f"    - {path}")
        return 0

    # Initialize checker
    checker = BoundaryChecker(auto_mode=args.auto, strict=args.strict)

    # Override instance if specified
    if args.instance:
        checker.current_instance = args.instance

    # Check boundaries
    violations, success = checker.check_all_boundaries()

    # Print results
    checker.print_violations(violations)

    # Export if requested
    if args.export and violations:
        checker.export_violations_json(violations, args.export)

    # Return exit code
    if not success or (checker.strict and violations):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
