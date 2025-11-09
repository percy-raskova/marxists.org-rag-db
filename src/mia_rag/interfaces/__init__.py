"""
Interface contracts for MIA RAG System.

These interfaces define the boundaries between instances and MUST NOT be changed
without an RFC and approval from all affected instances.
"""

from .contracts import (  # Registry; Data models; Version management; Interfaces
    INTERFACE_DEPENDENCIES,
    INTERFACE_REGISTRY,
    APIInterface,
    Document,
    Embedding,
    EmbeddingsInterface,
    InterfaceVersion,
    MonitoringInterface,
    ProcessingStatus,
    QueryResponse,
    SearchResult,
    StorageInterface,
    VectorDBInterface,
    get_dependencies,
    get_interface,
)

__all__ = [
    # Data models
    "Document",
    "Embedding",
    "SearchResult",
    "QueryResponse",
    "ProcessingStatus",
    # Interfaces
    "StorageInterface",
    "EmbeddingsInterface",
    "VectorDBInterface",
    "APIInterface",
    "MonitoringInterface",
    # Version management
    "InterfaceVersion",
    # Registry
    "INTERFACE_REGISTRY",
    "INTERFACE_DEPENDENCIES",
    "get_interface",
    "get_dependencies",
]

# Version of interface contracts
__version__ = InterfaceVersion.get_version()
