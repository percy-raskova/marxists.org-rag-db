"""
MIA RAG System - Marxist Internet Archive Retrieval Augmented Generation

A 200GB-scale RAG system for processing and querying the Marxist Internet Archive.
"""

__version__ = "2.0.0"
__author__ = "Persphone Raskova"

# Core version info
VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_PATCH = 0

# System configuration
CORPUS_SIZE_GB = 200
ESTIMATED_DOCS = "5-10 million"
DEPLOYMENT = "Google Cloud Platform"
VECTOR_DB = "Weaviate"
EMBEDDING_SERVICE = "Runpod.io"


def get_version() -> str:
    """Get the current version string."""
    return __version__


def get_system_info() -> dict:
    """Get system information."""
    return {
        "version": __version__,
        "corpus_size": CORPUS_SIZE_GB,
        "estimated_documents": ESTIMATED_DOCS,
        "deployment": DEPLOYMENT,
        "vector_database": VECTOR_DB,
        "embedding_service": EMBEDDING_SERVICE,
    }