#!/usr/bin/env python3
"""
Instance mapping utilities for MIA RAG System.

This module provides functions to map instances to their modules and directories.
Used by Mise tasks, GitHub Actions, and other scripts.
Can be used as a library or CLI tool.

Refactored using Command pattern for reduced complexity.
"""

import sys

import click
from scripts.patterns.instance_commands import InstanceCommandFactory


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
    # Create command invoker
    invoker = InstanceCommandFactory.create_command_invoker()

    # Determine which command to execute and create context
    command_name, context = _select_command(file, check, dirs, instance, validate)

    # Execute command
    result = invoker.execute(command_name, context)

    # Print result and exit
    if result.message:
        print(result.message)
    sys.exit(result.exit_code)


def _select_command(file, check, dirs, instance, validate):
    """
    Select appropriate command based on CLI options.

    Complexity: 5 branches (within limit of 12)
    """
    # Create base context with mappings
    shared_paths = {
        "interfaces": SHARED_RESOURCES["interfaces"],
        "configuration": SHARED_RESOURCES["configuration"],
        "documentation": SHARED_RESOURCES["documentation"],
    }

    if file or check:
        # Check file ownership
        context = InstanceCommandFactory.create_context(
            INSTANCE_MODULES,
            INSTANCE_DIRECTORIES,
            shared_paths,
            filepath=file or check,
        )
        return "check_ownership", context

    if dirs:
        # Get directories (space-separated)
        context = InstanceCommandFactory.create_context(
            INSTANCE_MODULES,
            INSTANCE_DIRECTORIES,
            shared_paths,
            instance_name=dirs,
        )
        return "get_directories", context

    if instance:
        # Get paths (newline-separated)
        context = InstanceCommandFactory.create_context(
            INSTANCE_MODULES,
            INSTANCE_DIRECTORIES,
            shared_paths,
            instance_name=instance,
        )
        return "get_paths", context

    if validate:
        # Validate mappings
        context = InstanceCommandFactory.create_context(
            INSTANCE_MODULES,
            INSTANCE_DIRECTORIES,
            shared_paths,
        )
        return "validate_mappings", context

    # Show help (default)
    click_ctx = click.get_current_context()
    context = InstanceCommandFactory.create_context(
        INSTANCE_MODULES,
        INSTANCE_DIRECTORIES,
        shared_paths,
        help_text=click_ctx.get_help(),
    )
    return "show_help", context


if __name__ == "__main__":
    main()
