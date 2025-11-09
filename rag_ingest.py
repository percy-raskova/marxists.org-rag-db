#!/usr/bin/env python3
"""
RAG Ingestion Pipeline for MIA Processed Content

Handles chunking, embedding, and vector DB ingestion.
Supports: Chroma (local), Qdrant (local/cloud), pgvector

Usage:
    python rag_ingest.py --db chroma --markdown-dir ~/marxists-processed/markdown/
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


try:
    from tqdm import tqdm
except ImportError:
    print("Install tqdm for progress bars: pip install tqdm --break-system-packages")
    tqdm = lambda x, **kwargs: x


@dataclass
class Chunk:
    """Text chunk with metadata"""

    content: str
    metadata: dict
    chunk_id: str
    chunk_index: int


class ChunkStrategy:
    """Chunking strategies for theory texts"""

    @staticmethod
    def by_section(content: str, max_tokens: int = 512) -> list[str]:
        """Chunk by markdown sections (headers)"""
        # Split by headers
        sections = re.split(r"\n(?=#{1,3}\s)", content)

        chunks = []
        current_chunk = ""

        for section in sections:
            # If section is small enough, keep it
            if len(section.split()) <= max_tokens:
                chunks.append(section.strip())
            else:
                # Split large sections by paragraphs
                paragraphs = section.split("\n\n")
                for para in paragraphs:
                    if len((current_chunk + "\n\n" + para).split()) <= max_tokens:
                        current_chunk += "\n\n" + para
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = para

                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

        if current_chunk:
            chunks.append(current_chunk.strip())

        return [c for c in chunks if c]

    @staticmethod
    def by_semantic_breaks(content: str, max_tokens: int = 512) -> list[str]:
        """Chunk by semantic boundaries (Percy's SemBr style)"""
        # Split by double newlines (paragraphs)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para.split())

            # If adding this paragraph exceeds max, save current chunk
            if current_length + para_length > max_tokens and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    @staticmethod
    def by_token_count(content: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        """Simple token-based chunking with overlap"""
        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks


class RAGIngestor:
    """Ingest processed MIA content into vector DB"""

    def __init__(
        self,
        db_type: str = "chroma",
        chunk_strategy: str = "semantic",
        chunk_size: int = 512,
        embedding_model: str = "nomic-embed-text",
    ):
        self.db_type = db_type
        self.chunk_strategy = chunk_strategy
        self.chunk_size = chunk_size
        self.embedding_model = embedding_model

        self.db = None
        self.stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
            "errors": 0,
        }

    def setup_chroma(self, persist_directory: Path):
        """Setup ChromaDB (local)"""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            print("Install ChromaDB: pip install chromadb --break-system-packages")
            return None

        client = chromadb.Client(
            Settings(persist_directory=str(persist_directory), anonymized_telemetry=False)
        )

        collection = client.get_or_create_collection(
            name="marxist_theory", metadata={"description": "Marxists Internet Archive corpus"}
        )

        print(f"✓ ChromaDB initialized at {persist_directory}")
        return collection

    def setup_qdrant(self, path: str | None = None, url: str | None = None):
        """Setup Qdrant (local or cloud)"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
        except ImportError:
            print("Install Qdrant: pip install qdrant-client --break-system-packages")
            return None

        if url:
            client = QdrantClient(url=url)
            print(f"✓ Connected to Qdrant at {url}")
        else:
            path = path or "./qdrant_storage"
            client = QdrantClient(path=path)
            print(f"✓ Qdrant initialized at {path}")

        # Create collection if doesn't exist
        collections = client.get_collections().collections
        if "marxist_theory" not in [c.name for c in collections]:
            client.create_collection(
                collection_name="marxist_theory",
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            print("✓ Created collection 'marxist_theory'")

        return client

    def chunk_document(self, content: str) -> list[str]:
        """Chunk document using selected strategy"""
        if self.chunk_strategy == "section":
            return ChunkStrategy.by_section(content, self.chunk_size)
        elif self.chunk_strategy == "semantic":
            return ChunkStrategy.by_semantic_breaks(content, self.chunk_size)
        else:  # token
            return ChunkStrategy.by_token_count(content, self.chunk_size)

    def get_embedding(self, text: str) -> list[float]:
        """Get embedding via Ollama"""
        try:
            import requests
        except ImportError:
            print("Install requests: pip install requests --break-system-packages")
            return None

        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error getting embedding: {e}")
            print("Make sure Ollama is running: ollama serve")
            print(f"And model is pulled: ollama pull {self.embedding_model}")
            return None

    def ingest_chroma(self, chunks: list[Chunk]):
        """Ingest chunks into ChromaDB"""
        if not self.db:
            return

        for chunk in tqdm(chunks, desc="Ingesting to Chroma"):
            try:
                self.db.add(
                    documents=[chunk.content], metadatas=[chunk.metadata], ids=[chunk.chunk_id]
                )
                self.stats["embeddings_created"] += 1
            except Exception as e:
                print(f"Error ingesting chunk {chunk.chunk_id}: {e}")
                self.stats["errors"] += 1

    def ingest_qdrant(self, chunks: list[Chunk]):
        """Ingest chunks into Qdrant"""
        from qdrant_client.models import PointStruct

        if not self.db:
            return

        points = []
        for chunk in tqdm(chunks, desc="Creating embeddings"):
            embedding = self.get_embedding(chunk.content)
            if embedding:
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (10**8),  # Convert to int
                    vector=embedding,
                    payload={"content": chunk.content, **chunk.metadata},
                )
                points.append(point)
                self.stats["embeddings_created"] += 1

        # Batch insert
        if points:
            self.db.upsert(collection_name="marxist_theory", points=points)
            print(f"✓ Inserted {len(points)} points into Qdrant")

    def process_markdown_files(self, markdown_dir: Path):
        """Process all markdown files and ingest to vector DB"""
        markdown_files = list(markdown_dir.glob("*.md"))
        print(f"Found {len(markdown_files)} markdown files to process")

        all_chunks = []

        for md_file in tqdm(markdown_files, desc="Processing documents"):
            try:
                content = md_file.read_text(encoding="utf-8")

                # Extract frontmatter metadata
                metadata = self.extract_frontmatter(content)

                # Remove frontmatter from content
                content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

                # Chunk the document
                chunks = self.chunk_document(content)

                # Create Chunk objects
                for i, chunk_text in enumerate(chunks):
                    chunk = Chunk(
                        content=chunk_text,
                        metadata={
                            **metadata,
                            "source_file": str(md_file.name),
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                        },
                        chunk_id=f"{md_file.stem}_chunk_{i}",
                        chunk_index=i,
                    )
                    all_chunks.append(chunk)

                self.stats["documents_processed"] += 1
                self.stats["chunks_created"] += len(chunks)

            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                self.stats["errors"] += 1

        # Ingest to vector DB
        print(f"\nIngesting {len(all_chunks)} chunks to {self.db_type}...")

        if self.db_type == "chroma":
            self.ingest_chroma(all_chunks)
        elif self.db_type == "qdrant":
            self.ingest_qdrant(all_chunks)

        self.print_stats()

    def extract_frontmatter(self, content: str) -> dict:
        """Extract YAML frontmatter from markdown"""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}

        metadata = {}
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata

    def print_stats(self):
        """Print ingestion statistics"""
        print("\n" + "=" * 50)
        print("INGESTION COMPLETE")
        print("=" * 50)
        print(f"Documents processed: {self.stats['documents_processed']}")
        print(f"Chunks created: {self.stats['chunks_created']}")
        print(f"Embeddings created: {self.stats['embeddings_created']}")
        print(f"Errors: {self.stats['errors']}")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest MIA content into RAG vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest to local ChromaDB
  python rag_ingest.py --db chroma --markdown-dir ~/marxists-processed/markdown/

  # Ingest to local Qdrant with semantic chunking
  python rag_ingest.py --db qdrant --strategy semantic --markdown-dir ~/marxists-processed/markdown/

  # Use different embedding model
  python rag_ingest.py --db chroma --embedding-model mxbai-embed-large --markdown-dir ~/marxists-processed/markdown/
        """,
    )

    parser.add_argument(
        "--db",
        choices=["chroma", "qdrant"],
        default="chroma",
        help="Vector database to use (default: chroma)",
    )
    parser.add_argument(
        "--markdown-dir",
        type=Path,
        required=True,
        help="Directory containing processed markdown files",
    )
    parser.add_argument(
        "--strategy",
        choices=["section", "semantic", "token"],
        default="semantic",
        help="Chunking strategy (default: semantic)",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=512, help="Maximum chunk size in tokens (default: 512)"
    )
    parser.add_argument(
        "--embedding-model",
        default="nomic-embed-text",
        help="Ollama embedding model (default: nomic-embed-text)",
    )
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=Path("./vector_db"),
        help="Vector DB persistence directory (default: ./vector_db)",
    )
    parser.add_argument("--qdrant-url", type=str, help="Qdrant server URL (for remote Qdrant)")

    args = parser.parse_args()

    if not args.markdown_dir.exists():
        print(f"Error: Markdown directory does not exist: {args.markdown_dir}")
        return 1

    # Initialize ingestor
    ingestor = RAGIngestor(
        db_type=args.db,
        chunk_strategy=args.strategy,
        chunk_size=args.chunk_size,
        embedding_model=args.embedding_model,
    )

    # Setup vector DB
    if args.db == "chroma":
        args.persist_dir.mkdir(parents=True, exist_ok=True)
        ingestor.db = ingestor.setup_chroma(args.persist_dir)
    elif args.db == "qdrant":
        ingestor.db = ingestor.setup_qdrant(
            path=str(args.persist_dir) if not args.qdrant_url else None, url=args.qdrant_url
        )

    if not ingestor.db:
        print("Failed to initialize vector database")
        return 1

    # Process and ingest
    ingestor.process_markdown_files(args.markdown_dir)

    return 0


if __name__ == "__main__":
    exit(main())
