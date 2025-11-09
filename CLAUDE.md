# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL SCALE UPDATE

**Corpus Scale**: 200GB raw archive → **50GB optimized** (75% reduction through strategic filtering)

**Corpus Analysis**: ✅ **Complete** - 46GB English content analyzed (55,753 documents across 6 sections)

For architecture overview, see: **[ARCHITECTURE.md](./ARCHITECTURE.md)** (includes corpus foundation)

The architecture includes:

- **Corpus Foundation**: Systematic 46GB analysis informing all data decisions
- **Metadata Schema**: 5-layer model achieving 85%+ author coverage
- **Chunking Strategies**: 4 adaptive strategies based on document structure
- **Knowledge Graph**: ~2,500 entities forming hybrid retrieval foundation
- **Infrastructure**: Simplified GCP architecture with Weaviate + Runpod embeddings
- **Parallel Development**: 6-instance coordination strategy

## Project Overview

The Marxists Internet Archive (MIA) RAG Pipeline converts 126,000+ pages of Marxist theory (HTML + PDFs) into a queryable RAG system. This is a local, private, fully-owned knowledge base designed for material analysis research, class composition studies, and theoretical framework development.

**Note**: The reference implementation below works for small-scale testing. For production processing, see ARCHITECTURE.md for complete details.

## Architecture

The system consists of three main pipeline stages:

1. **Document Processing** (`mia_processor.py`) - Converts HTML and PDFs from the MIA archive into clean markdown with preserved metadata
2. **RAG Ingestion** (`rag_ingest.py`) - Chunks documents, generates embeddings via Ollama, and stores in vector database (Chroma or Qdrant)
3. **Query Interface** (`query_example.py`) - Provides search capabilities via CLI and Python API

### Key Data Flow

```
MIA Archive (HTML/PDF)
  → Processing (mia_processor.py)
  → Markdown + Metadata (~/marxists-processed/markdown/)
  → Ingestion (rag_ingest.py)
  → Vector DB (Chroma/Qdrant)
  → Query Interface (query_example.py)
```

### Data Structures

**DocumentMetadata** (defined in `mia_processor.py:33-44`):

- Used throughout the pipeline as the canonical metadata format
- Includes: source_url, title, author, date, language, doc_type, word_count, content_hash
- Stored as YAML frontmatter in markdown files and as JSON sidecar files

**Chunk** (defined in `rag_ingest.py:27-32`):

- Contains: content (str), metadata (Dict), chunk_id (str), chunk_index (int)
- Metadata preserves all DocumentMetadata fields plus chunk-specific info

## Corpus Analysis Foundation

**CRITICAL**: All implementation decisions must be informed by the completed corpus analysis (46GB English content, 55,753 documents).

### Essential Reading Before Coding

**Metadata & Schemas**:
- [docs/corpus-analysis/06-metadata-unified-schema.md](./docs/corpus-analysis/06-metadata-unified-schema.md) - **5-layer metadata model**
  - Achieves 85%+ author coverage through multi-source extraction
  - Section-specific rules: Archive (100% path), ETOL (85% title+keywords), EROL (95% org from title)
  - Encoding normalization: 62% ISO-8859-1 → UTF-8 conversion required

**Chunking & Document Structure**:
- [specs/07-chunking-strategies-spec.md](./specs/07-chunking-strategies-spec.md) - **4 adaptive chunking strategies**
  - 70% documents have good heading hierarchies → semantic-break chunking
  - 40% heading-less → paragraph-cluster chunking fallback
  - Glossary → entry-based chunking (special case)
  - Target: 650-750 tokens/chunk average, >70% with heading context

**Knowledge Graph & Entities**:
- [specs/08-knowledge-graph-spec.md](./specs/08-knowledge-graph-spec.md) - **Hybrid retrieval architecture**
  - ~2,500 Glossary entities form canonical node set
  - 10 node types, 14 edge types for vector + graph retrieval
  - 5k-10k cross-references extracted from corpus

### Section-Specific Analyses

When implementing processing for specific corpus sections, consult:

- **Archive** (4.3GB, 15,637 files): [docs/corpus-analysis/01-archive-section-analysis.md](./docs/corpus-analysis/01-archive-section-analysis.md)
- **History** (33GB, 33,190 files - ETOL/EROL/Other): [docs/corpus-analysis/02-history-section-spec.md](./docs/corpus-analysis/02-history-section-spec.md)
- **Subject** (8.9GB, 2,259 files): [docs/corpus-analysis/03-subject-section-spec.md](./docs/corpus-analysis/03-subject-section-spec.md)
- **Glossary** (62MB, ~2,500 entities): [docs/corpus-analysis/04-glossary-section-spec.md](./docs/corpus-analysis/04-glossary-section-spec.md)
- **Reference** (460MB, 4,867 files): [docs/corpus-analysis/05-reference-section-spec.md](./docs/corpus-analysis/05-reference-section-spec.md)

### Why This Matters

- **Instance 1 (Storage)**: Metadata schema defines extraction rules, encoding normalization
- **Instance 2 (Embeddings)**: Chunking strategies optimize semantic unit quality
- **Instance 3 (Weaviate)**: Entity schema from Glossary analysis defines node structure
- **Instance 4 (API)**: Cross-reference patterns enable query expansion
- **Instance 6 (Monitoring)**: Quality targets from corpus analysis (85% author coverage, etc.)

**Don't reinvent the wheel**: These specs encode 200k+ tokens of systematic corpus investigation.

## Common Development Tasks

### Setup and Installation

```bash
# Install core dependencies
pip install -r requirements.txt --break-system-packages

# Install vector database (choose one)
pip install chromadb --break-system-packages  # For local Chroma
pip install qdrant-client --break-system-packages  # For Qdrant

# Install and setup Ollama for embeddings
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### Running the Pipeline

```bash
# Step 1: Download MIA metadata
python mia_processor.py --download-json

# Step 2: Process archive (HTML/PDF → Markdown)
python mia_processor.py --process-archive ~/Downloads/dump_www-marxists-org/ --output ~/marxists-processed/

# Step 3: Ingest to vector database
python rag_ingest.py --db chroma --markdown-dir ~/marxists-processed/markdown/ --persist-dir ./mia_vectordb/

# Step 4: Query the system
python query_example.py --db chroma --query "What is surplus value?" --persist-dir ./mia_vectordb/
python query_example.py --db chroma --interactive  # Interactive mode
```

### Testing

```bash
# Test processing on a small sample
python mia_processor.py --process-archive /path/to/sample/ --output ./test-output/

# Test ingestion with small dataset
python rag_ingest.py --db chroma --markdown-dir ./test-output/markdown/ --persist-dir ./test-vectordb/

# Test query interface
python query_example.py --db chroma --persist-dir ./test-vectordb/ --query "test query"
```

## Code Architecture Details

### Processing Pipeline (`mia_processor.py`)

**Key Classes:**

- `MIAProcessor` (line 47): Main orchestrator for document processing
- `DocumentMetadata` (line 33): Dataclass for document metadata

**Important Methods:**

- `is_english_content()` (line 118): Heuristic language detection - ~95% accurate but may need tuning
- `html_to_markdown()` (line 183): HTML conversion with boilerplate removal
- `pdf_to_markdown()` (line 215): PDF conversion using pymupdf4llm
- `extract_metadata_from_html()` (line 144): Metadata extraction - author extraction is ~70% accurate

**Output Format:**

- Markdown files with YAML frontmatter at `~/marxists-processed/markdown/`
- JSON metadata sidecar files at `~/marxists-processed/metadata/`
- Processing report at `~/marxists-processed/processing_report.json`

### Ingestion Pipeline (`rag_ingest.py`)

**Key Classes:**

- `RAGIngestor` (line 112): Main ingestion orchestrator
- `ChunkStrategy` (line 35): Static methods for different chunking strategies
- `Chunk` (line 27): Dataclass for text chunks

**Chunking Strategies:**

- `by_semantic_breaks()` (line 72): **Default** - Respects paragraph boundaries, best for theory
- `by_section()` (line 39): Chunks by markdown headers, preserves document structure
- `by_token_count()` (line 99): Fixed token count, predictable but may split mid-thought

**Vector Database Support:**

- `setup_chroma()` (line 133): Local-only ChromaDB setup
- `setup_qdrant()` (line 155): Local or remote Qdrant setup
- Collection name is always "marxist_theory"

**Embedding Generation:**

- `get_embedding()` (line 192): Calls Ollama API at localhost:11434
- Default model: "nomic-embed-text" (768 dimensions)
- Alternative: "mxbai-embed-large" (1024d) or "all-minilm" (384d)

### Query Interface (`query_example.py`)

**Key Classes:**

- `RAGQuery` (line 23): Query interface for both Chroma and Qdrant

**Query Methods:**

- `query_chroma()` (line 95): ChromaDB search
- `query_qdrant()` (line 115): Qdrant search with manual embedding
- `interactive_mode()` (line 168): Interactive CLI with example queries

## Important Implementation Notes

### Language Detection

The `is_english_content()` function (mia_processor.py:118) uses path-based heuristics with ~5% false positive rate. When working on language filtering:

- Non-English directory list is at line 123
- Default behavior is to process (line 142)
- Archive/history/reference sections assumed English (lines 135-140)

### Author Extraction

Author extraction from file paths (mia_processor.py:158) is only ~70% accurate. The pattern:

- Looks for `/archive/` in path
- Takes first path component after `/archive/`
- Converts hyphens to spaces and title-cases

### PDF OCR Quality

PDF processing (mia_processor.py:215) using pymupdf4llm has variable quality:

- Pre-1990s works may have OCR errors
- Mathematical notation often garbled
- Diagrams/images lost in text conversion

### Chunking for Theory

Semantic chunking is **strongly preferred** for Marxist texts because they have specific rhetorical structure:

1. Thesis statement
2. Historical/material evidence
3. Dialectical synthesis
4. Practical implications

Token-based chunking may split these argumentative units mid-thought (see README.md:261-270 for example).

### Embedding Requirements

The system **requires Ollama running locally**:

- Must be accessible at `http://localhost:11434`
- Model must be pre-downloaded with `ollama pull <model-name>`
- If Ollama is not running, ingestion will fail at embedding generation

## Formal Specifications

The `specs/` directory contains detailed formal specifications for a refactored, production-ready version:

- **00-ARCHITECTURE-SPEC.md** - System architecture overview
- **02-DOCUMENT-PROCESSING-SPEC.md** - Processing module spec
- **03-RAG-INGESTION-SPEC.md** - Ingestion module spec
- **04-QUERY-INTERFACE-SPEC.md** - Query interface spec
- **05-MCP-INTEGRATION-SPEC.md** - MCP server integration spec
- **06-TESTING-VALIDATION-SPEC.md** - Testing requirements
- **INDEX.md** - Master index with parallel development strategy

The current implementation (mia_processor.py, rag_ingest.py, query_example.py) is working but monolithic. The specs define better architecture with proper abstractions, error handling, and modularity.

## Performance Characteristics

### Processing Times (typical hardware)

- HTML processing: ~1-2 hours for 126k pages
- PDF processing: ~3-6 hours for 38k documents (OCR intensive)
- Total processing: ~4-8 hours

### Ingestion Times

- Depends on embedding model and batch size
- Use `--chunk-size` to control chunk granularity (default: 512 tokens)
- Semantic chunking is slower but produces better results

### Query Performance

- Target: <500ms for typical queries
- Depends on collection size and vector DB choice
- Qdrant generally faster than Chroma for large collections

## Integration Points

### MCP Server Integration

See `specs/05-MCP-INTEGRATION-SPEC.md` for detailed MCP server implementation plan. Key tools to expose:

- `search_marxist_theory(query, n_results)` - Semantic search
- `find_by_author(author, work_title)` - Author-specific search
- `get_historical_context(time_period, topic)` - Temporal search

### PercyBrain/Zettelkasten Integration

The system is designed to integrate with PercyBrain via MCP. Query results can cross-reference with personal Zettelkasten notes for synthesis.

## Known Limitations

1. **Author Extraction**: ~70% accuracy from file paths
2. **Language Detection**: ~5% false positive rate for non-English
3. **PDF Quality**: Variable OCR quality, especially pre-1990s
4. **Long Documents**: Works >50k words may need manual chunking review
5. **Mathematical Notation**: Often garbled in PDF conversion
6. **Nested HTML**: Some complex structures may lose formatting

## File Locations

```
~/marxists-processed/              # Default processing output
├── markdown/                      # Converted documents with frontmatter
├── metadata/                      # JSON metadata for each document
├── json/                          # Downloaded MIA metadata (authors, sections, periodicals)
└── processing_report.json         # Processing statistics

./mia_vectordb/                    # Default vector DB location
./vector_db/                       # Alternative vector DB location (configurable)
```

## Security & Privacy

**All processing is local:**

- No external API calls except to Ollama (localhost)
- Vector DB files contain full text - protect accordingly
- Store on encrypted volume for OPSEC
- No telemetry (ChromaDB anonymized_telemetry=False)

## Dependencies

Core dependencies (requirements.txt):

- requests>=2.31.0 - HTTP client for metadata download
- beautifulsoup4>=4.12.0 - HTML parsing
- markdownify>=0.11.6 - HTML to Markdown conversion
- pymupdf4llm>=0.0.10 - PDF to Markdown conversion
- lxml>=4.9.0 - XML/HTML parser

Optional dependencies:

- chromadb - Local vector database (simpler)
- qdrant-client - Local/remote vector database (better scale)
- tqdm - Progress bars for ingestion

External dependencies:

- Ollama - Local embedding generation (required)
