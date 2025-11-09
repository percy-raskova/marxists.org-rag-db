"""
Interface Contracts for MIA RAG System

This file defines the abstract interfaces between instances.
These contracts MUST NOT be changed without an RFC and approval from all affected instances.

Version: 1.0.0
Last Modified: 2025-01-08

CRITICAL: Breaking changes to these interfaces will break the entire system.
Create an RFC in docs/rfcs/ and wait 24 hours for review before changes.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd

# ============================================================================
# DATA MODELS (Shared across all instances)
# ============================================================================


@dataclass
class Document:
    """Core document model used throughout the system."""

    id: str
    content: str
    metadata: dict[str, Any]
    source_path: str
    processed_date: datetime
    word_count: int
    content_hash: str
    doc_type: str  # "html" | "pdf" | "markdown"


@dataclass
class Embedding:
    """Embedding vector with metadata."""

    chunk_id: str
    vector: list[float]
    metadata: dict[str, Any]
    document_id: str
    chunk_index: int
    total_chunks: int


@dataclass
class SearchResult:
    """Search result from vector database."""

    document_id: str
    chunk_id: str
    score: float
    content: str
    metadata: dict[str, Any]
    highlights: list[str] | None = None


@dataclass
class QueryResponse:
    """Response from query API."""

    query: str
    results: list[SearchResult]
    total_results: int
    query_time_ms: float
    metadata: dict[str, Any]


class ProcessingStatus(Enum):
    """Status of document processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================================
# INSTANCE 1 → INSTANCE 2: Storage Interface
# ============================================================================


class StorageInterface(ABC):
    """
    Interface for storage operations (Instance 1 → Instance 2).

    Instance 1 (Storage) implements this interface.
    Instance 2 (Embeddings) consumes this interface.
    """

    @abstractmethod
    async def list_documents(
        self, prefix: str = "", limit: int = 1000, offset: int = 0
    ) -> list[str]:
        """
        List document paths in storage.

        Args:
            prefix: Path prefix to filter documents
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of document paths
        """
        pass

    @abstractmethod
    async def get_document(self, path: str) -> Document:
        """
        Retrieve a single document from storage.

        Args:
            path: Document path in storage

        Returns:
            Document object

        Raises:
            FileNotFoundError: If document doesn't exist
        """
        pass

    @abstractmethod
    async def get_batch(
        self, paths: list[str], batch_size: int = 100
    ) -> AsyncIterator[list[Document]]:
        """
        Retrieve documents in batches.

        Args:
            paths: List of document paths
            batch_size: Size of each batch

        Yields:
            Batches of Document objects
        """
        pass

    @abstractmethod
    async def get_processing_status(self) -> dict[str, Any]:
        """
        Get overall processing status.

        Returns:
            Status dictionary with counts and progress
        """
        pass

    @abstractmethod
    async def mark_processed(
        self, path: str, status: ProcessingStatus, metadata: dict[str, Any] | None = None
    ) -> bool:
        """
        Mark a document as processed.

        Args:
            path: Document path
            status: Processing status
            metadata: Optional metadata to store

        Returns:
            Success status
        """
        pass


# ============================================================================
# INSTANCE 2 → INSTANCE 3: Embeddings Interface
# ============================================================================


class EmbeddingsInterface(ABC):
    """
    Interface for embedding operations (Instance 2 → Instance 3).

    Instance 2 (Embeddings) implements this interface.
    Instance 3 (Weaviate) consumes this interface.
    """

    @abstractmethod
    async def list_embedding_files(self, prefix: str = "") -> list[str]:
        """
        List all Parquet files containing embeddings.

        Args:
            prefix: Path prefix to filter files

        Returns:
            List of Parquet file paths
        """
        pass

    @abstractmethod
    async def get_embedding_batch(self, file_path: str) -> pd.DataFrame:
        """
        Get embeddings from a Parquet file.

        Args:
            file_path: Path to Parquet file

        Returns:
            DataFrame with columns: chunk_id, embedding, metadata
        """
        pass

    @abstractmethod
    async def stream_embeddings(self, batch_size: int = 1000) -> AsyncIterator[list[Embedding]]:
        """
        Stream all embeddings in batches.

        Args:
            batch_size: Size of each batch

        Yields:
            Batches of Embedding objects
        """
        pass

    @abstractmethod
    async def get_embedding_stats(self) -> dict[str, Any]:
        """
        Get statistics about embeddings.

        Returns:
            Stats including count, dimensions, model info
        """
        pass

    @abstractmethod
    async def get_checkpoint(self) -> dict[str, Any] | None:
        """
        Get the last checkpoint for resumable processing.

        Returns:
            Checkpoint data or None if no checkpoint
        """
        pass


# ============================================================================
# INSTANCE 3 → INSTANCE 4: Vector Database Interface
# ============================================================================


class VectorDBInterface(ABC):
    """
    Interface for vector database operations (Instance 3 → Instance 4).

    Instance 3 (Weaviate) implements this interface.
    Instance 4 (API) consumes this interface.
    """

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        include_metadata: bool = True,
    ) -> list[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional metadata filters
            include_metadata: Whether to include metadata

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        query_text: str,
        query_vector: list[float] | None = None,
        limit: int = 10,
        alpha: float = 0.5,
    ) -> list[SearchResult]:
        """
        Hybrid text + vector search.

        Args:
            query_text: Text query
            query_vector: Optional query vector
            limit: Maximum number of results
            alpha: Weight between text (0) and vector (1) search

        Returns:
            List of search results
        """
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Document | None:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document or None if not found
        """
        pass

    @abstractmethod
    async def get_collection_stats(self) -> dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Stats including document count, index info
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if vector database is healthy.

        Returns:
            Health status
        """
        pass


# ============================================================================
# INSTANCE 4 → INSTANCE 5: API Interface
# ============================================================================


class APIInterface(ABC):
    """
    Interface for API operations (Instance 4 → Instance 5).

    Instance 4 (API) implements this interface.
    Instance 5 (MCP) consumes this interface.
    """

    @abstractmethod
    async def query(
        self,
        text: str,
        limit: int = 5,
        filters: dict[str, Any] | None = None,
        include_context: bool = True,
    ) -> QueryResponse:
        """
        Query the RAG system.

        Args:
            text: Query text
            limit: Maximum number of results
            filters: Optional filters
            include_context: Whether to include surrounding context

        Returns:
            Query response with results
        """
        pass

    @abstractmethod
    async def get_document_metadata(self, document_id: str) -> dict[str, Any] | None:
        """
        Get document metadata.

        Args:
            document_id: Document ID

        Returns:
            Metadata dictionary or None
        """
        pass

    @abstractmethod
    async def search_by_author(self, author: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search documents by author.

        Args:
            author: Author name
            limit: Maximum results

        Returns:
            List of document metadata
        """
        pass

    @abstractmethod
    async def search_by_date_range(
        self, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Search documents by date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum results

        Returns:
            List of document metadata
        """
        pass

    @abstractmethod
    async def get_api_stats(self) -> dict[str, Any]:
        """
        Get API usage statistics.

        Returns:
            Stats including request count, latencies
        """
        pass


# ============================================================================
# INSTANCE 6: Monitoring Interface (All instances implement)
# ============================================================================


class MonitoringInterface(ABC):
    """
    Interface for monitoring operations.

    ALL instances implement this interface.
    Instance 6 (Monitoring) consumes this interface.
    """

    @abstractmethod
    async def get_metrics(self) -> dict[str, Any]:
        """
        Get current metrics for monitoring.

        Returns:
            Metrics dictionary with Prometheus-compatible format
        """
        pass

    @abstractmethod
    async def get_health(self) -> dict[str, Any]:
        """
        Get health status.

        Returns:
            Health status with component checks
        """
        pass

    @abstractmethod
    async def get_logs(self, level: str = "INFO", limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent logs.

        Args:
            level: Minimum log level
            limit: Maximum number of logs

        Returns:
            List of log entries
        """
        pass


# ============================================================================
# VERSION MANAGEMENT
# ============================================================================


class InterfaceVersion:
    """
    Version information for interface contracts.

    Update this when making changes to interfaces.
    """

    MAJOR = 1  # Breaking changes
    MINOR = 0  # New features (backward compatible)
    PATCH = 0  # Bug fixes

    @classmethod
    def get_version(cls) -> str:
        """Get version string."""
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"

    @classmethod
    def check_compatibility(cls, required: str) -> bool:
        """
        Check if current version is compatible with required version.

        Args:
            required: Required version string (e.g., "1.0.0")

        Returns:
            True if compatible
        """
        req_major, req_minor, req_patch = map(int, required.split("."))

        # Major version must match exactly
        if req_major != cls.MAJOR:
            return False

        # Minor version must be >= required
        if req_minor > cls.MINOR:
            return False

        # Patch version doesn't affect compatibility
        return True


# ============================================================================
# INTERFACE REGISTRY
# ============================================================================

INTERFACE_REGISTRY = {
    "storage": StorageInterface,
    "embeddings": EmbeddingsInterface,
    "vectordb": VectorDBInterface,
    "api": APIInterface,
    "monitoring": MonitoringInterface,
}

INTERFACE_DEPENDENCIES = {
    "instance1": [],
    "instance2": ["storage"],
    "instance3": ["embeddings"],
    "instance4": ["vectordb"],
    "instance5": ["api"],
    "instance6": ["monitoring"],  # All instances implement monitoring
}


def get_interface(name: str) -> type:
    """Get interface class by name."""
    return INTERFACE_REGISTRY.get(name)


def get_dependencies(instance: str) -> list[str]:
    """Get interface dependencies for an instance."""
    return INTERFACE_DEPENDENCIES.get(instance, [])
