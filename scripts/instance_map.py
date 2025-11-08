"""
Instance mapping utilities for MIA RAG System.

This module provides functions to map instances to their modules and directories.
Used by Mise tasks and other scripts.
"""

from typing import List, Optional

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


def get_module(instance_id: str) -> str:
    """Get the primary module name for an instance."""
    modules = INSTANCE_MODULES.get(instance_id, [])
    return modules[0] if modules else "unknown"


def get_modules(instance_id: str) -> List[str]:
    """Get all module names for an instance."""
    return INSTANCE_MODULES.get(instance_id, [])


def get_directories(instance_id: str) -> List[str]:
    """Get all directories owned by an instance."""
    return INSTANCE_DIRECTORIES.get(instance_id, [])


def get_instance_for_path(path: str) -> Optional[str]:
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