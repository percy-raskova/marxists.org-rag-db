# MIA RAG System Architecture Specification (200GB Scale)

**Version:** 2.0
**Status:** SPECIFICATION - UPDATED FOR 200GB
**Last Updated:** 2025-11-07

## Executive Summary

Complete system for converting **200GB Marxists Internet Archive** (5-10M estimated documents) into a queryable RAG system with **Weaviate vector database on GCP** and MCP integration. Uses **Runpod.io GPU rental** for embeddings ($40-60 total cost).

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MIA RAG SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Archive    │───▶│  Processing  │───▶│   Vector DB  │ │
│  │   Sources    │    │   Pipeline   │    │   (Chroma/   │ │
│  │              │    │              │    │   Qdrant)    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │         │
│         │                    │                    │         │
│  ┌──────▼──────┐    ┌───────▼────────┐  ┌───────▼──────┐ │
│  │  Metadata   │    │   Chunking &   │  │    Query     │ │
│  │   (JSON)    │    │   Embedding    │  │  Interface   │ │
│  └─────────────┘    └────────────────┘  └──────────────┘ │
│                                                  │          │
│                                         ┌────────▼────────┐│
│                                         │  MCP Server     ││
│                                         │  Integration    ││
│                                         └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Archive Acquisition Module

**Spec Document:** `01-ARCHIVE-ACQUISITION-SPEC.md`

- Torrent download handling
- GitHub mirror cloning
- JSON metadata fetching
- Archive validation

### 2. Document Processing Module

**Spec Document:** `02-DOCUMENT-PROCESSING-SPEC.md`

- HTML → Markdown conversion
- PDF → Markdown conversion
- Metadata extraction
- Language filtering
- Content deduplication

### 3. RAG Ingestion Module

**Spec Document:** `03-RAG-INGESTION-SPEC.md`

- Chunking strategies (semantic, section, token)
- Embedding generation (Ollama)
- Vector DB population (Chroma/Qdrant)
- Batch processing

### 4. Query Interface Module

**Spec Document:** `04-QUERY-INTERFACE-SPEC.md`

- Semantic search
- Result ranking
- Metadata filtering
- Interactive CLI

### 5. MCP Integration Module

**Spec Document:** `05-MCP-INTEGRATION-SPEC.md`

- MCP server implementation
- Tool definitions
- PercyBrain integration
- Context management

### 6. Testing & Validation Module

**Spec Document:** `06-TESTING-VALIDATION-SPEC.md`

- Unit tests
- Integration tests
- Quality metrics
- Performance benchmarks

## Data Flow

```
Internet Archive Torrent (126k pages, 38k PDFs)
                │
                ▼
        [Extract Archive]
                │
                ▼
        [Filter English]
                │
                ▼
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
[HTML Files]          [PDF Files]
    │                       │
    ▼                       ▼
[BS4 Parser]         [PyMuPDF4LLM]
    │                       │
    └───────────┬───────────┘
                ▼
        [Markdown Files]
        (with metadata)
                │
                ▼
      [Chunk Strategy]
                │
                ▼
        [Text Chunks]
                │
                ▼
    [Ollama Embeddings]
                │
                ▼
      [Vector Database]
    (Chroma or Qdrant)
                │
                ▼
      [Query Interface]
                │
                ├──▶ [CLI Tool]
                ├──▶ [MCP Server]
                └──▶ [API Endpoint]
```

## Technology Stack

### Core Dependencies

- **Python:** 3.9+
- **Embedding:** Ollama (nomic-embed-text, 768d)
- **Vector DB:** ChromaDB (local) or Qdrant (local/cloud)
- **HTML Parser:** BeautifulSoup4
- **Markdown:** markdownify
- **PDF:** pymupdf4llm

### Storage Requirements

- **Source Archive:** ~15-20 GB
- **Processed Markdown:** ~8-10 GB
- **Vector DB:** ~5-8 GB
- **Total:** ~30-40 GB

### Performance Targets

- **Processing Rate:** 100 HTML/min, 10 PDF/min
- **Embedding Rate:** 50 chunks/sec (local Ollama)
- **Query Latency:** <500ms for top-5 results
- **Total Pipeline:** 4-8 hours for full archive

## Directory Structure

```
mia-rag-system/
├── specs/                          # Specification documents
│   ├── 01-ARCHIVE-ACQUISITION-SPEC.md
│   ├── 02-DOCUMENT-PROCESSING-SPEC.md
│   ├── 03-RAG-INGESTION-SPEC.md
│   ├── 04-QUERY-INTERFACE-SPEC.md
│   ├── 05-MCP-INTEGRATION-SPEC.md
│   └── 06-TESTING-VALIDATION-SPEC.md
│
├── src/                           # Source code
│   ├── acquisition/
│   │   ├── __init__.py
│   │   ├── torrent_handler.py
│   │   └── metadata_fetcher.py
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── html_processor.py
│   │   ├── pdf_processor.py
│   │   └── metadata_extractor.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── vectordb.py
│   │
│   ├── query/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   └── cli.py
│   │
│   └── mcp/
│       ├── __init__.py
│       ├── server.py
│       └── tools.py
│
├── tests/                         # Test suite
│   ├── test_processing.py
│   ├── test_ingestion.py
│   ├── test_query.py
│   └── fixtures/
│
├── data/                          # Data directories
│   ├── raw/                       # Raw archive
│   ├── processed/                 # Processed markdown
│   ├── metadata/                  # Extracted metadata
│   └── vectordb/                  # Vector database
│
├── docs/                          # Documentation
│   ├── README.md
│   ├── INSTALLATION.md
│   └── API.md
│
├── requirements.txt
├── setup.py
└── pyproject.toml
```

## Data Schemas

### Document Metadata Schema

```json
{
  "source_url": "string",
  "title": "string",
  "author": "string | null",
  "date": "string | null",
  "language": "string (ISO 639-1)",
  "doc_type": "html | pdf",
  "original_path": "string",
  "processed_date": "string (ISO 8601)",
  "content_hash": "string (SHA256 first 16 chars)",
  "word_count": "integer",
  "chunk_count": "integer | null"
}
```

### Chunk Schema

```json
{
  "chunk_id": "string (unique)",
  "content": "string",
  "metadata": {
    "document_id": "string",
    "chunk_index": "integer",
    "total_chunks": "integer",
    "...": "inherited from document metadata"
  },
  "embedding": "float[] (768d for nomic-embed-text)"
}
```

### MIA Author Schema (from JSON)

```json
{
  "name": "string",
  "href": "string (relative URL)",
  "birth": "string | null",
  "death": "string | null",
  "nationality": "string | null"
}
```

## Inter-Module Interfaces

### Processing → Ingestion

**Input:** Directory of markdown files with frontmatter  
**Output:** None (direct file system)  
**Contract:** Each .md file has YAML frontmatter with complete metadata

### Ingestion → Query

**Input:** Vector DB path/connection  
**Output:** Query results (list of chunks with metadata)  
**Contract:** Vector DB contains "marxist_theory" collection

### Query → MCP

**Input:** Search query string  
**Output:** Formatted results for Claude context  
**Contract:** MCP tool schema compliance

## Configuration Management

### Environment Variables

```bash
MIA_ARCHIVE_PATH="/path/to/archive"
MIA_OUTPUT_DIR="~/marxists-processed"
MIA_VECTOR_DB_PATH="./mia_vectordb"
MIA_DB_TYPE="chroma"  # or "qdrant"
MIA_EMBEDDING_MODEL="nomic-embed-text"
MIA_CHUNK_SIZE="512"
MIA_CHUNK_STRATEGY="semantic"  # or "section", "token"
OLLAMA_HOST="http://localhost:11434"
```

### Config File Format (config.yaml)

```yaml
archive:
  path: "/path/to/archive"
  source: "internet_archive"  # or "github_mirror"
  
processing:
  output_dir: "~/marxists-processed"
  filter_english: true
  skip_pdfs: false
  parallel_workers: 4
  
ingestion:
  db_type: "chroma"
  db_path: "./mia_vectordb"
  chunk_strategy: "semantic"
  chunk_size: 512
  chunk_overlap: 50
  embedding_model: "nomic-embed-text"
  batch_size: 100
  
query:
  default_results: 5
  similarity_threshold: 0.7
  
mcp:
  server_name: "marxist-theory"
  tools:
    - search_theory
    - find_author
    - get_work_metadata
```

## Error Handling Strategy

### Retry Logic

- **Network requests:** 3 retries with exponential backoff
- **Ollama embeddings:** 3 retries with 2s delay
- **Vector DB operations:** 2 retries

### Failure Modes

1. **Partial Processing Failure:** Log error, continue with next document
2. **Embedding Service Down:** Pause ingestion, alert user
3. **Vector DB Connection Loss:** Save progress, retry connection
4. **Corrupt Archive File:** Skip file, log warning

### Logging

- **Level:** INFO for progress, WARNING for skips, ERROR for failures
- **Format:** `[TIMESTAMP] [LEVEL] [MODULE] Message`
- **Destinations:** Console + file (`mia_rag.log`)

## Security Considerations

### Local-Only Architecture

- No external API calls except Ollama (localhost)
- No data exfiltration
- Full content stored locally

### Data Privacy

- Vector DB contains full text
- Store on encrypted volume (LUKS recommended)
- No network exposure by default

### Copyright Compliance

- Respect MIA licensing (public domain + CC-BY-SA)
- Track copyright status in metadata
- User responsible for legal use

## Performance Optimization

### Processing Phase

- Parallel HTML processing (4-8 workers)
- PDF processing serialized (CPU-bound)
- Batch metadata writes

### Ingestion Phase

- Batch embedding requests (10-50 chunks)
- Async vector DB inserts
- Progress checkpointing for resume

### Query Phase

- Index-based similarity search
- Metadata pre-filtering
- Result caching (optional)

## Extensibility Points

### Custom Chunking Strategies

Implement `ChunkStrategy` interface:

```python
class CustomStrategy(ChunkStrategy):
    def chunk(self, content: str, max_tokens: int) -> List[str]:
        # Your implementation
        pass
```

### Additional Vector DBs

Implement `VectorDB` interface:

```python
class CustomVectorDB(VectorDB):
    def insert(self, chunks: List[Chunk]) -> None: pass
    def search(self, query: str, n: int) -> List[Result]: pass
```

### New Document Types

Implement `DocumentProcessor` interface:

```python
class CustomProcessor(DocumentProcessor):
    def process(self, path: Path) -> tuple[str, Metadata]: pass
```

## Dependencies Graph

```
acquisition
    └── metadata_fetcher → requests

processing
    ├── html_processor → beautifulsoup4, markdownify
    └── pdf_processor → pymupdf4llm

ingestion
    ├── embedder → requests (Ollama API)
    └── vectordb → chromadb OR qdrant-client

query
    └── search → chromadb OR qdrant-client

mcp
    └── server → query.search
```

## Acceptance Criteria

### System Level

- [ ] Process 126k HTML pages without crashes
- [ ] Process 38k PDFs without crashes
- [ ] Generate embeddings for all chunks
- [ ] Store in vector DB with metadata
- [ ] Query returns relevant results (<500ms)
- [ ] MCP server responds to tool calls
- [ ] Total pipeline completes in <12 hours

### Module Level

See individual spec documents for detailed acceptance criteria.

## Parallel Development Strategy

### Team Assignment

1. **Dev 1:** Archive Acquisition + Metadata (Spec 01)
2. **Dev 2:** Document Processing (Spec 02)
3. **Dev 3:** RAG Ingestion (Spec 03)
4. **Dev 4:** Query Interface (Spec 04)
5. **Dev 5:** MCP Integration (Spec 05)
6. **Dev 6:** Testing & Validation (Spec 06)

### Integration Points

- All devs use same data schemas (defined here)
- Modules communicate via file system or defined APIs
- Integration testing after individual module completion

### Versioning

- Each spec has version number
- Modules declare spec version compatibility
- Breaking changes require spec version bump

## References

- MIA Archive: <https://archive.org/details/dump_www-marxists-org>
- MIA GitHub Mirror: <https://github.com/emijrp/www.marxists.org>
- MIA JSON APIs: <https://www.marxists.org/admin/js/data/>
- Ollama Docs: <https://github.com/ollama/ollama/blob/main/docs/api.md>
- ChromaDB Docs: <https://docs.trychroma.com/>
- Qdrant Docs: <https://qdrant.tech/documentation/>

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |

---

**Next Steps:**

1. Review and approve architecture
2. Distribute individual spec documents to development instances
3. Begin parallel implementation
4. Integrate and test
