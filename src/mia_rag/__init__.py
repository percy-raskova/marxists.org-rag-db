"""
MIA RAG System - Marxist Internet Archive Retrieval Augmented Generation

Translating revolutionary theory into the age of AI.
A RAG system for processing and querying the Marxist Internet Archive.
"""

__version__ = "0.1.0"
__author__ = "Persephone Raskova"
__email__ = "103053862+percy-raskova@users.noreply.github.com"
__license__ = "GPL-3.0-or-later"

# Core version info
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_SUFFIX = ""  # For alpha/beta/rc releases

# System configuration (optimized from 200GB to 50GB)
CORPUS_SIZE_GB = 50  # Optimized corpus size
ORIGINAL_SIZE_GB = 200  # Original before optimization
ESTIMATED_DOCS = "~1-2 million"
DEPLOYMENT = "Flexible (GCP/Local/Hybrid)"
VECTOR_DB = "Weaviate/Qdrant/ChromaDB"
EMBEDDING_SERVICE = "Runpod/Local/CPU"


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
