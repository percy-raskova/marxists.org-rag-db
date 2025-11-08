#!/usr/bin/env python3
"""
Instance mapping utilities for MIA RAG System.

This module provides functions to map instances to their modules and directories.
Used by Mise tasks, GitHub Actions, and other scripts.
Can be used as a library or CLI tool.
"""

import sys
from pathlib import Path

import click


# Instance to module mapping
INSTANCE_MODULES = {
    "instance1": ["storage", "pipeline"],
    "instance2": ["embeddings"],
    "instance3": ["vectordb"],
    "instance4": ["api"],
    "instance5": ["mcp"],
    "instance6": ["monitoring"],
}

# Instance to directory mapping
INSTANCE_DIRECTORIES = {
    "instance1": [
        "src/mia_rag/storage",
        "src/mia_rag/pipeline",
        "tests/unit/instance1_storage",
        "tests/unit/instance1_pipeline",
    ],
    "instance2": [
        "src/mia_rag/embeddings",
        "tests/unit/instance2_embeddings",
    ],
    "instance3": [
        "src/mia_rag/vectordb",
        "tests/unit/instance3_weaviate",
    ],
    "instance4": [
        "src/mia_rag/api",
        "tests/unit/instance4_api",
    ],
    "instance5": [
        "src/mia_rag/mcp",
        "tests/unit/instance5_mcp",
    ],
    "instance6": [
        "src/mia_rag/monitoring",
        "tests/unit/instance6_monitoring",
        "tests/integration",
        "tests/scale",
        "tests/contract",
    ],
}

# Shared resources that require coordination
SHARED_RESOURCES = {
    "interfaces": [
        "src/mia_rag/interfaces",
        "src/mia_rag/common",
    ],
    "configuration": [
        "pyproject.toml",
        ".mise.toml",
        ".gitignore",
        ".env.example",
        ".pre-commit-config.yaml",
        "pytest.ini",
    ],
    "documentation": [
        "README.md",
        "CLAUDE.md",
        "CLAUDE_ENTERPRISE.md",
        "AI-AGENT-INSTRUCTIONS.md",
        "INSTANCE-BOUNDARIES.md",
        "CONTRIBUTING.md",
        "docs",
        "specs",
    ],
}


def get_module(instance_id: str) -> str:
    """Get the primary module name for an instance."""
    modules = INSTANCE_MODULES.get(instance_id, [])
    return modules[0] if modules else "unknown"


def get_modules(instance_id: str) -> list[str]:
    """Get all module names for an instance."""
    return INSTANCE_MODULES.get(instance_id, [])


def get_directories(instance_id: str) -> list[str]:
    """Get all directories owned by an instance."""
    return INSTANCE_DIRECTORIES.get(instance_id, [])


def get_instance_for_path(path: str) -> str | None:
    """Determine which instance owns a given path."""
    for instance_id, directories in INSTANCE_DIRECTORIES.items():
        for directory in directories:
            if path.startswith(directory):
                return instance_id
    return None


def is_shared_path(path: str) -> bool:
    """Check if a path is in shared territory."""
    shared_dirs = [
        "src/mia_rag/interfaces",
        "src/mia_rag/common",
        "docs",
        "scripts",
        ".github",
        ".claude",
    ]
    return any(path.startswith(d) for d in shared_dirs)


# CLI functionality when run as script
@click.command()
@click.option("--file", help="Check ownership of a specific file")
@click.option("--check", help="Check ownership of a file (same as --file)")
@click.option("--dirs", help="Get directories for an instance (space-separated)")
@click.option("--instance", help="Get all paths for an instance (newline-separated)")
@click.option("--validate", is_flag=True, help="Validate all ownership mappings")
def main(file, check, dirs, instance, validate):
    """Instance mapping tool for file ownership."""

    if file or check:
        filepath = file or check
        owner = get_instance_for_path(filepath)

        if owner:
            print(f"Owner: {owner}")
        elif is_shared_path(filepath):
            print("Owner: shared")
            print("Requires coordination: Yes")
        else:
            print("Owner: none (unrestricted)")

    elif dirs:
        # Get directories for an instance (space-separated for shell scripts)
        paths = get_directories(dirs)
        if paths:
            print(" ".join(paths))
        else:
            print(f"Error: Unknown instance {dirs}", file=sys.stderr)
            sys.exit(1)

    elif instance:
        # Get all paths for an instance (newline-separated)
        paths = get_directories(instance)
        if paths:
            for path in paths:
                print(path)
        else:
            print(f"Error: Unknown instance {instance}", file=sys.stderr)
            sys.exit(1)

    elif validate:
        # Validate that mappings are consistent
        all_valid = True
        all_paths: set[str] = set()

        print("Validating instance ownership mappings...")

        # Check instance paths
        for instance_name, directories in INSTANCE_DIRECTORIES.items():
            print(f"\n{instance_name}:")
            for path in directories:
                if path in all_paths:
                    print(f"  ❌ {path} - DUPLICATE OWNERSHIP")
                    all_valid = False
                else:
                    all_paths.add(path)
                    if Path(path).exists():
                        print(f"  ✅ {path}")
                    else:
                        print(f"  ⚠️  {path} - does not exist yet")

        if all_valid:
            print("\n✅ All mappings are valid")
        else:
            print("\n❌ Issues found in mappings")
            sys.exit(1)

    else:
        # Show help if no options provided
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


if __name__ == "__main__":
    main()
