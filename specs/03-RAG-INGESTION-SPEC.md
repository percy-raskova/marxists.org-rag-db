# RAG Ingestion Module Specification

**Version:** 1.0  
**Status:** SPECIFICATION  
**Module:** `src/ingestion/`  
**Dependencies:** Architecture Spec 1.0, Document Processing Spec 1.0

## Overview

Converts processed markdown documents into vector embeddings and stores them in a queryable vector database. Handles chunking strategies, embedding generation via Ollama, and batch ingestion.

## Responsibilities

1. Chunk documents using configurable strategies
2. Generate embeddings via local Ollama
3. Populate vector database (Chroma or Qdrant)
4. Handle batch processing and checkpointing
5. Track ingestion progress and statistics

## Module Structure

```
src/ingestion/
├── __init__.py
├── chunker.py          # Chunking strategies
├── embedder.py         # Embedding generation via Ollama
├── vectordb.py         # Vector DB abstraction layer
├── ingestion_main.py   # Orchestration & CLI
└── checkpointer.py     # Progress tracking for resume
```

## Data Structures

### Chunk (dataclass)
```python
@dataclass
class Chunk:
    """Text chunk with metadata"""
    chunk_id: str                # Unique identifier: {doc_id}_chunk_{index}
    content: str                 # Chunk text content
    metadata: Dict[str, Any]     # Document metadata + chunk metadata
    chunk_index: int             # Position in document (0-based)
    embedding: Optional[List[float]] = None  # 768d vector for nomic-embed-text
    
    def to_dict(self) -> dict:
        """Serialize for vector DB insertion"""
        return {
            'id': self.chunk_id,
            'content': self.content,
            'metadata': self.metadata,
            'embedding': self.embedding
        }
```

### ChunkMetadata (dict structure)
```python
{
    "document_id": str,           # Source document hash
    "source_file": str,           # Original .md filename
    "chunk_index": int,           # Position in document
    "total_chunks": int,          # Total chunks in document
    "chunk_size": int,            # Size of this chunk in tokens
    
    # Inherited from document metadata
    "title": str,
    "author": Optional[str],
    "date": Optional[str],
    "source_url": str,
    "language": str,
    "doc_type": str,
    "word_count": int
}
```

### IngestionStats (dataclass)
```python
@dataclass
class IngestionStats:
    """Statistics for ingestion run"""
    documents_processed: int = 0
    chunks_created: int = 0
    embeddings_generated: int = 0
    embeddings_cached: int = 0      # If caching enabled
    vector_db_inserts: int = 0
    errors: int = 0
    start_time: float = field(default_factory=time.time)
    
    def elapsed_time(self) -> float:
        pass
    
    def chunks_per_second(self) -> float:
        pass
    
    def to_dict(self) -> dict:
        pass
```

## Core Classes

### ChunkStrategy (Abstract Base Class)
```python
class ChunkStrategy(ABC):
    """Abstract base class for chunking strategies"""
    
    def __init__(self, max_tokens: int = 512, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap
    
    @abstractmethod
    def chunk(self, content: str) -> List[str]:
        """
        Chunk document content
        
        Args:
            content: Full document text (markdown)
            
        Returns:
            List of text chunks
        """
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (words * 1.3)
        
        Note: Not perfect but fast. Use tiktoken for accuracy.
        """
        return int(len(text.split()) * 1.3)
```

### SemanticChunkStrategy
```python
class SemanticChunkStrategy(ChunkStrategy):
    """
    Chunk by semantic boundaries (paragraphs)
    
    Strategy:
    - Respect paragraph boundaries (\n\n)
    - Combine small paragraphs up to max_tokens
    - Split large paragraphs at sentence boundaries
    - Maintain overlap for context continuity
    
    Best for: Theory texts with clear paragraph structure
    """
    
    def chunk(self, content: str) -> List[str]:
        """
        Chunk respecting semantic boundaries
        
        Algorithm:
        1. Split by double newlines (paragraphs)
        2. Accumulate paragraphs until max_tokens
        3. For oversized paragraphs, split at sentences
        4. Add overlap from previous chunk
        
        Returns:
            List of text chunks
        """
        paragraphs = self._split_paragraphs(content)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            
            # Paragraph fits in current chunk
            if current_tokens + para_tokens <= self.max_tokens:
                current_chunk.append(para)
                current_tokens += para_tokens
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                
                # Handle oversized paragraph
                if para_tokens > self.max_tokens:
                    # Split by sentences
                    chunks.extend(self._split_large_paragraph(para))
                    current_chunk = []
                    current_tokens = 0
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens
        
        # Save final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        # Add overlap
        return self._add_overlap(chunks)
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """Split by double newlines, filter empty"""
        return [p.strip() for p in content.split('\n\n') if p.strip()]
    
    def _split_large_paragraph(self, para: str) -> List[str]:
        """Split large paragraph by sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chunks = []
        current = []
        current_tokens = 0
        
        for sent in sentences:
            sent_tokens = self.estimate_tokens(sent)
            if current_tokens + sent_tokens <= self.max_tokens:
                current.append(sent)
                current_tokens += sent_tokens
            else:
                if current:
                    chunks.append(' '.join(current))
                current = [sent]
                current_tokens = sent_tokens
        
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between chunks for context"""
        if not chunks or self.overlap == 0:
            return chunks
        
        overlapped = [chunks[0]]
        
        for i in range(1, len(chunks)):
            # Get last N words from previous chunk
            prev_words = chunks[i-1].split()[-self.overlap:]
            curr_chunk = ' '.join(prev_words) + '\n\n' + chunks[i]
            overlapped.append(curr_chunk)
        
        return overlapped
```

### SectionChunkStrategy
```python
class SectionChunkStrategy(ChunkStrategy):
    """
    Chunk by markdown sections (headers)
    
    Strategy:
    - Split at header boundaries (#, ##, ###)
    - Keep entire sections together if possible
    - Split oversized sections at paragraphs
    
    Best for: Well-structured documents with clear sections
    """
    
    def chunk(self, content: str) -> List[str]:
        """
        Chunk by markdown headers
        
        Algorithm:
        1. Split at header markers (# ## ###)
        2. If section < max_tokens, keep intact
        3. If section > max_tokens, split by paragraphs
        4. Preserve header in each sub-chunk
        
        Returns:
            List of text chunks
        """
        sections = self._split_by_headers(content)
        chunks = []
        
        for section in sections:
            section_tokens = self.estimate_tokens(section)
            
            if section_tokens <= self.max_tokens:
                chunks.append(section)
            else:
                # Extract header
                header = self._extract_header(section)
                body = self._remove_header(section)
                
                # Split body by paragraphs
                para_chunks = SemanticChunkStrategy(
                    self.max_tokens - self.estimate_tokens(header),
                    self.overlap
                ).chunk(body)
                
                # Re-attach header to each chunk
                for chunk in para_chunks:
                    chunks.append(f"{header}\n\n{chunk}")
        
        return chunks
    
    def _split_by_headers(self, content: str) -> List[str]:
        """Split content at markdown headers"""
        return re.split(r'\n(?=#{1,3}\s)', content)
    
    def _extract_header(self, section: str) -> str:
        """Extract first header from section"""
        match = re.match(r'(#{1,3}\s+.*?)(?:\n|$)', section)
        return match.group(1) if match else ""
    
    def _remove_header(self, section: str) -> str:
        """Remove first header from section"""
        return re.sub(r'^#{1,3}\s+.*?(?:\n|$)', '', section, count=1)
```

### TokenChunkStrategy
```python
class TokenChunkStrategy(ChunkStrategy):
    """
    Simple fixed-size chunking by token count
    
    Strategy:
    - Split at word boundaries
    - Fixed size with overlap
    - Fastest but may break mid-thought
    
    Best for: Quick processing, less critical quality
    """
    
    def chunk(self, content: str) -> List[str]:
        """
        Chunk by fixed token count
        
        Algorithm:
        1. Split into words
        2. Group into chunks of max_tokens
        3. Add overlap words
        
        Returns:
            List of text chunks
        """
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), self.max_tokens - self.overlap):
            chunk_words = words[i:i + self.max_tokens]
            chunks.append(' '.join(chunk_words))
        
        return [c for c in chunks if c.strip()]
```

### Embedder
```python
class Embedder:
    """Generate embeddings via Ollama API"""
    
    def __init__(self, 
                 model: str = "nomic-embed-text",
                 ollama_host: str = "http://localhost:11434",
                 batch_size: int = 10,
                 timeout: int = 30):
        self.model = model
        self.ollama_host = ollama_host
        self.batch_size = batch_size
        self.timeout = timeout
        
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """Verify Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get('models', [])
            if not any(m['name'].startswith(self.model) for m in models):
                raise ValueError(f"Model {self.model} not found. Run: ollama pull {self.model}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.ollama_host}. "
                "Make sure Ollama is running: ollama serve"
            )
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            
        Returns:
            768-dimensional vector (for nomic-embed-text)
            
        Raises:
            EmbeddingError: On API failure
        """
        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['embedding']
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {e}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Generating embeddings"):
            batch = texts[i:i + self.batch_size]
            
            for text in batch:
                try:
                    embedding = self.embed(text)
                    embeddings.append(embedding)
                except EmbeddingError as e:
                    logger.error(f"Failed to embed text (len={len(text)}): {e}")
                    embeddings.append(None)
        
        return embeddings
```

### VectorDB (Abstract Base Class)
```python
class VectorDB(ABC):
    """Abstract interface for vector databases"""
    
    @abstractmethod
    def create_collection(self, name: str, dimension: int) -> None:
        """Create a collection/index"""
        pass
    
    @abstractmethod
    def insert(self, chunks: List[Chunk]) -> None:
        """Insert chunks with embeddings"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], limit: int) -> List[dict]:
        """Search for similar vectors"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count total vectors"""
        pass
```

### ChromaDB Implementation
```python
class ChromaVectorDB(VectorDB):
    """ChromaDB implementation"""
    
    def __init__(self, persist_directory: Path, collection_name: str = "marxist_theory"):
        import chromadb
        from chromadb.config import Settings
        
        self.client = chromadb.Client(Settings(
            persist_directory=str(persist_directory),
            anonymized_telemetry=False
        ))
        
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Marxist Internet Archive corpus"}
        )
    
    def insert(self, chunks: List[Chunk]) -> None:
        """
        Insert chunks into Chroma
        
        Note: Chroma generates embeddings if not provided,
        but we provide them for control
        """
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        embeddings = [c.embedding for c in chunks]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def search(self, query_embedding: List[float], limit: int = 5) -> List[dict]:
        """Search by embedding"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        return [
            {
                'content': doc,
                'metadata': meta,
                'distance': dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def count(self) -> int:
        """Count total vectors"""
        return self.collection.count()
```

### Qdrant Implementation
```python
class QdrantVectorDB(VectorDB):
    """Qdrant implementation"""
    
    def __init__(self, 
                 path: Optional[str] = None,
                 url: Optional[str] = None,
                 collection_name: str = "marxist_theory"):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        if url:
            self.client = QdrantClient(url=url)
        else:
            self.client = QdrantClient(path=path or "./qdrant_storage")
        
        self.collection_name = collection_name
        
        # Create collection if doesn't exist
        collections = self.client.get_collections().collections
        if collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
    
    def insert(self, chunks: List[Chunk]) -> None:
        """Insert chunks into Qdrant"""
        from qdrant_client.models import PointStruct
        
        points = [
            PointStruct(
                id=hash(c.chunk_id) % (10 ** 8),  # Convert to int
                vector=c.embedding,
                payload={
                    "content": c.content,
                    **c.metadata
                }
            )
            for c in chunks
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search(self, query_embedding: List[float], limit: int = 5) -> List[dict]:
        """Search by embedding"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                'content': r.payload['content'],
                'metadata': {k: v for k, v in r.payload.items() if k != 'content'},
                'score': r.score
            }
            for r in results
        ]
    
    def count(self) -> int:
        """Count total vectors"""
        info = self.client.get_collection(self.collection_name)
        return info.points_count
```

### IngestionOrchestrator
```python
class IngestionOrchestrator:
    """Main ingestion orchestrator"""
    
    def __init__(self,
                 markdown_dir: Path,
                 vectordb: VectorDB,
                 chunker: ChunkStrategy,
                 embedder: Embedder,
                 batch_size: int = 100):
        self.markdown_dir = markdown_dir
        self.vectordb = vectordb
        self.chunker = chunker
        self.embedder = embedder
        self.batch_size = batch_size
        
        self.stats = IngestionStats()
        self.checkpointer = Checkpointer(markdown_dir / ".ingestion_checkpoint")
    
    def ingest(self) -> IngestionStats:
        """
        Ingest all markdown files
        
        Workflow:
        1. Discover markdown files
        2. For each file:
           a. Parse frontmatter metadata
           b. Extract content
           c. Chunk content
           d. Generate embeddings
           e. Create Chunk objects
        3. Batch insert to vector DB
        4. Checkpoint progress
        
        Returns:
            IngestionStats with final counts
        """
        markdown_files = sorted(self.markdown_dir.glob("*.md"))
        logger.info(f"Found {len(markdown_files)} markdown files")
        
        all_chunks = []
        
        for md_file in tqdm(markdown_files, desc="Processing documents"):
            # Skip if already processed
            if self.checkpointer.is_processed(md_file.name):
                continue
            
            try:
                # Parse document
                content, metadata = self._parse_markdown(md_file)
                
                # Chunk
                chunk_texts = self.chunker.chunk(content)
                
                # Create Chunk objects
                for i, chunk_text in enumerate(chunk_texts):
                    chunk = Chunk(
                        chunk_id=f"{md_file.stem}_chunk_{i}",
                        content=chunk_text,
                        metadata={
                            **metadata,
                            "source_file": md_file.name,
                            "chunk_index": i,
                            "total_chunks": len(chunk_texts),
                            "chunk_size": len(chunk_text.split())
                        },
                        chunk_index=i
                    )
                    all_chunks.append(chunk)
                
                self.stats.documents_processed += 1
                self.stats.chunks_created += len(chunk_texts)
                
                # Batch insert
                if len(all_chunks) >= self.batch_size:
                    self._insert_batch(all_chunks)
                    all_chunks = []
                
                # Checkpoint
                self.checkpointer.mark_processed(md_file.name)
                
            except Exception as e:
                logger.error(f"Failed to process {md_file}: {e}")
                self.stats.errors += 1
        
        # Insert remaining chunks
        if all_chunks:
            self._insert_batch(all_chunks)
        
        return self.stats
    
    def _parse_markdown(self, path: Path) -> tuple[str, dict]:
        """Parse markdown with frontmatter"""
        content = path.read_text()
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if match:
            frontmatter_text = match.group(1)
            body = match.group(2)
            
            metadata = yaml.safe_load(frontmatter_text)
            return body, metadata
        else:
            return content, {}
    
    def _insert_batch(self, chunks: List[Chunk]) -> None:
        """Generate embeddings and insert batch"""
        # Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_batch(texts)
        
        # Attach embeddings
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            if embedding:
                self.stats.embeddings_generated += 1
        
        # Filter out failed embeddings
        valid_chunks = [c for c in chunks if c.embedding is not None]
        
        # Insert to vector DB
        self.vectordb.insert(valid_chunks)
        self.stats.vector_db_inserts += len(valid_chunks)
```

## Configuration

### CLI Interface
```bash
python ingestion_main.py \
    --markdown-dir ~/marxists-processed/markdown/ \
    --db chroma \
    --persist-dir ./mia_vectordb/ \
    --strategy semantic \
    --chunk-size 512 \
    --overlap 50 \
    --embedding-model nomic-embed-text \
    --batch-size 100
```

## Testing Requirements

### Unit Tests
- [ ] Test each chunking strategy
- [ ] Test embedding generation
- [ ] Test vector DB operations
- [ ] Test checkpointing/resume

### Integration Tests
- [ ] Full pipeline on sample dataset
- [ ] Verify chunk quality
- [ ] Verify embeddings dimensions
- [ ] Verify vector DB queries work

## Performance Requirements

- **Chunking:** >1000 chunks/second
- **Embedding:** >50 chunks/second (Ollama-limited)
- **Vector DB Insert:** >100 chunks/second
- **Total Time:** <6 hours for 126k documents

## Acceptance Criteria

- [ ] Process all markdown files without crashes
- [ ] Generate embeddings for all chunks
- [ ] Insert all chunks to vector DB
- [ ] Support resume after interruption
- [ ] Query returns relevant results
- [ ] Complete ingestion in <8 hours

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |

---

**Implementation Priority:** HIGH
