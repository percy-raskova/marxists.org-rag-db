# MIA RAG System - Specification Index (200GB Scale)

**Project:** Marxists Internet Archive RAG System
**Version:** 2.0
**Date:** 2025-11-07
**Scale:** 200GB corpus (not 38GB)
**Status:** READY FOR 6-INSTANCE PARALLEL DEVELOPMENT

## Quick Start for 6 Parallel Claude Code Instances

**CRITICAL UPDATES FOR 200GB SCALE:**

- Read **[ARCHITECTURE.md](../ARCHITECTURE.md)** for complete architecture (includes corpus foundation)
- Read **[docs/corpus-analysis/](../docs/corpus-analysis/)** ⭐ **ESSENTIAL** - 46GB systematic analysis informing all data decisions
- Read **[RUNPOD.md](../RUNPOD.md)** for GPU embedding strategy ($40-60 total!)
- Read instance guides **[INSTANCE1-6-*.md](../)** for your role

**Corpus Analysis Foundation** (READ BEFORE CODING):
- [Metadata Schema](../docs/corpus-analysis/06-metadata-unified-schema.md) - 5-layer model, 85%+ author coverage
- [Chunking Strategies](./07-chunking-strategies-spec.md) - 4 adaptive strategies from document structure analysis
- [Knowledge Graph](./08-knowledge-graph-spec.md) - ~2,500 entities, hybrid retrieval architecture

Each specification document is standalone and can be implemented independently. Follow this workflow:

1. **Choose your instance assignment** (see ARCHITECTURE.md)
2. **Read corpus analysis docs relevant to your instance** ⭐ (see instance guides for essential reading)
3. **Read the architecture spec** (00-ARCHITECTURE-SPEC.md) for system overview
4. **Read your module's spec** completely before coding
5. **Implement according to the spec** (data structures, interfaces, acceptance criteria)
6. **Test against corpus-informed acceptance criteria** using specs/06-TESTING.md
7. **Submit for integration**

## Specification Documents

### 00. Architecture Overview

**File:** `00-ARCHITECTURE-SPEC.md`  
**Read First:** YES (required for all devs)  
**Purpose:** System architecture, data flow, module interfaces, data schemas

**Key Sections:**

- System architecture diagram
- Module breakdown and responsibilities
- Data schemas (DocumentMetadata, Chunk, etc.)
- Inter-module interfaces
- Technology stack
- Directory structure

**Read this if:** You're starting any module

---

### 01. Archive Acquisition

**File:** `01-ARCHIVE-ACQUISITION-SPEC.md`  
**Status:** NOT YET CREATED (deprioritized - manual download works)  
**Dependencies:** None  
**Estimated Time:** 8 hours

**Implements:**

- Internet Archive torrent handling
- GitHub mirror cloning
- MIA JSON metadata fetching
- Archive validation

**Can skip:** Yes - users can manually download archive

---

### 02. Document Processing

**File:** `02-DOCUMENT-PROCESSING-SPEC.md`  
**Dependencies:** Architecture Spec  
**Estimated Time:** 16-24 hours  
**Priority:** **CRITICAL** (blocks ingestion)

**Implements:**

- HTML → Markdown conversion
- PDF → Markdown conversion
- Metadata extraction
- Language filtering
- Content deduplication

**Key Classes:**

- `HTMLProcessor`
- `PDFProcessor`
- `MetadataExtractor`
- `LanguageFilter`
- `DocumentProcessor` (orchestrator)

**Outputs:**

- `~/marxists-processed/markdown/` - Markdown files with frontmatter
- `~/marxists-processed/metadata/` - JSON metadata files
- `processing_report.json`

**Acceptance Criteria:** 11 items (see spec)

---

### 03. RAG Ingestion (200GB Scale)

**File:** `03-RAG-INGESTION-SPEC.md`
**Dependencies:** Architecture Spec, Document Processing Spec
**Estimated Time:** 16-20 hours + 100 hours Runpod GPU time
**Priority:** **CRITICAL** (blocks query)

**Implements:**

- Chunking strategies (semantic, section, token)
- **Embedding generation via Runpod.io GPU rental** (not Ollama)
- Vector DB abstraction layer
- **Weaviate as primary** (enterprise scale)
- ChromaDB/Qdrant as alternatives
- Batch processing with checkpointing
- **Parquet format for embedding storage**

**Key Classes:**

- `ChunkStrategy` (abstract)
- `SemanticChunkStrategy`
- `SectionChunkStrategy`
- `TokenChunkStrategy`
- `Embedder`
- `VectorDB` (abstract)
- `ChromaVectorDB`
- `QdrantVectorDB`
- `IngestionOrchestrator`

**Outputs:**

- Vector database at configured path
- Embeddings for all chunks
- Ingestion statistics

**Acceptance Criteria:** 10 items (see spec)

---

### 04. Query Interface

**File:** `04-QUERY-INTERFACE-SPEC.md`  
**Dependencies:** Architecture Spec, RAG Ingestion Spec  
**Estimated Time:** 8-12 hours  
**Priority:** HIGH

**Implements:**

- Semantic search
- Metadata filtering
- Result formatting
- Interactive CLI
- Python API

**Key Classes:**

- `Searcher`
- `SearchResult`
- `MetadataFilter`
- `ResultFormatter`
- `InteractiveCLI`

**Outputs:**

- CLI tool for queries
- Python API for programmatic access

**Acceptance Criteria:** 5 items (see spec)

---

### 05. MCP Integration

**File:** `05-MCP-INTEGRATION-SPEC.md`  
**Dependencies:** Architecture Spec, Query Interface Spec  
**Estimated Time:** 8-12 hours  
**Priority:** MEDIUM (can be done after core system works)

**Implements:**

- MCP server
- Tool definitions (search_marxist_theory, find_author_works, get_work_context)
- PercyBrain integration
- Context management

**Key Components:**

- MCP server implementation
- Tool handlers
- Configuration for Claude integration

**Outputs:**

- MCP server Python file
- mcp_config.json template

**Acceptance Criteria:** 4 items (see spec)

---

### 06. Testing & Validation

**File:** `06-TESTING-VALIDATION-SPEC.md`  
**Dependencies:** All module specs  
**Estimated Time:** Ongoing (parallel with development)  
**Priority:** MEDIUM (but should start early)

**Implements:**

- Unit tests for all modules
- Integration tests
- Performance benchmarks
- Quality metrics
- CI/CD pipeline

**Key Components:**

- Unit test suite
- Integration test suite
- Test fixtures
- Benchmark suite
- Quality validation

**Outputs:**

- Complete test suite
- Test coverage reports
- Performance benchmarks
- Quality metrics

**Acceptance Criteria:** 8 items (see spec)

---

### 07. Chunking Strategies

**File:** `07-chunking-strategies-spec.md`
**Dependencies:** Corpus analysis (docs/corpus-analysis/)
**Estimated Time:** Implementation integrated into 02-Processing
**Priority:** **CRITICAL** (informs Instance 2 embeddings quality)

**Implements:**

- 4 adaptive chunking strategies based on document structure
- Automatic strategy selection algorithm
- Document structure detection
- Quality metrics and targets

**Key Strategies:**

- **Semantic Breaks** (70% of corpus): Respects heading hierarchies
- **Paragraph Clusters** (40% fallback): For heading-less documents
- **Entry-Based** (Glossary): Specialized for entity definitions
- **Token-Based** (failsafe): Fixed token count when structure detection fails

**Quality Targets:**

- Average chunk size: 650-750 tokens
- >70% chunks with heading context
- Proper handling of edge cases (index pages, multi-article files, long paragraphs)

**Corpus Foundation:** Based on systematic analysis of 55,753 documents identifying structural patterns

**Acceptance Criteria:** Target metrics from corpus analysis (see spec)

---

### 08. Knowledge Graph Architecture

**File:** `08-knowledge-graph-spec.md`
**Dependencies:** Corpus analysis (docs/corpus-analysis/), 04-Query
**Estimated Time:** 40-60 hours (optional enhancement)
**Priority:** MEDIUM (enables hybrid retrieval, not required for v1)

**Implements:**

- Knowledge graph schema (10 node types, 14 edge types)
- Hybrid retrieval (vector + graph)
- Entity extraction from Glossary (~2,500 entities)
- Cross-reference network (5k-10k edges)
- Multi-hop query patterns

**Key Components:**

- **Entity Nodes**: People, terms, organizations, events, periodicals, places
- **Relationship Edges**: Authorship, structural, mentions, thematic
- **Hybrid Retrieval Patterns**: Vector-first + graph-enhanced, graph-first + vector-filtered
- **Query Types**: Intellectual genealogy, citation chains, thematic exploration

**Storage Options:**

- Neo4j (recommended for complex graph)
- NetworkX (simpler, Python-native)
- SQLite (hybrid SQL+graph)

**Corpus Foundation:** Based on Glossary analysis (~2,500 entities with 80-95% cross-reference completeness)

**Acceptance Criteria:** Entity extraction accuracy, cross-reference coverage, query performance (see spec)

---

## Parallel Development Strategy

### Dependency Graph

```
Corpus Analysis (docs/corpus-analysis/) ⭐ FOUNDATION
    │
    ├─▶ 06-Metadata Schema ──────┐
    ├─▶ 07-Chunking Strategies ──┤
    └─▶ 08-Knowledge Graph ───────┤
                                  ▼
00-Architecture (read first) ◀────┘
    │
    ├─▶ 02-Processing ──▶ 03-Ingestion ──▶ 04-Query ──▶ 05-MCP
    │        │                  │              │
    │        │                  │              └──▶ 08-Knowledge Graph
    │        └──▶ 07-Chunking   │
    │                            │
    └─▶ 06-Testing ──────────────┴──────────────────────────┘

**Key**:
- ⭐ Corpus analysis (46GB, 55,753 docs) informs all data architecture decisions
- Specs 06, 07, 08 are corpus-derived specifications
- Spec 02 implements metadata + chunking
- Spec 08 is optional (v2 enhancement for hybrid retrieval)
```

### 6-Instance Parallel Development (REQUIRED for 200GB)

**Instance Assignments:**

- **Instance 1 (storage):** Storage & Data Pipeline - GCS management, lifecycle policies
- **Instance 2 (embeddings):** Runpod GPU Embeddings - $40-60 total cost!
- **Instance 3 (weaviate):** Weaviate Vector DB - 10M+ vectors, GKE deployment
- **Instance 4 (api):** Query & API Layer - REST API, caching
- **Instance 5 (mcp):** MCP Integration - Claude tools
- **Instance 6 (monitoring):** Monitoring & Testing - Prometheus, Grafana, integration tests

**Cloud Resources per Instance:**

- Each instance gets isolated GCS bucket prefix
- Dedicated Terraform workspace
- Isolated test environment
- No resource conflicts (see BOUNDARIES.md)

### Integration Points

After individual modules are complete:

1. **Processing → Ingestion:**  
   Verify markdown files have correct frontmatter format

2. **Ingestion → Query:**  
   Verify vector DB schema matches query expectations

3. **Query → MCP:**  
   Verify query API matches MCP tool interface

4. **All → Testing:**  
   Run full integration test suite

## Development Workflow

### For Each Module

1. **Read Architecture Spec** (00-ARCHITECTURE-SPEC.md)
2. **Read Module Spec** (your assigned spec)
3. **Set up development environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create module structure** (as defined in spec)
5. **Implement core classes** (follow spec data structures)
6. **Write unit tests** (as you code)
7. **Test against acceptance criteria**
8. **Document any deviations from spec**
9. **Submit for integration**

### Code Style

- Python 3.9+
- Type hints for all functions
- Docstrings (Google style)
- Black formatting
- Max line length: 100
- Use dataclasses for data structures

### Git Workflow (if using version control)

```bash
# Create feature branch
git checkout -b module-processing

# Make commits
git commit -m "feat(processing): implement HTMLProcessor"

# Push for review
git push origin module-processing
```

## Common Pitfalls to Avoid

1. **Don't implement features not in spec** - stick to requirements
2. **Don't skip error handling** - specs define error strategies
3. **Don't hardcode paths** - use configuration
4. **Don't skip tests** - acceptance criteria are mandatory
5. **Don't deviate from data schemas** - they're the integration contract

## Data Schema Reference

### DocumentMetadata

```python
source_url: str
title: str
author: Optional[str]
date: Optional[str]
language: str = "en"
doc_type: str  # "html" | "pdf"
original_path: str
processed_date: str  # ISO 8601
content_hash: str  # SHA256 first 16 chars
word_count: int
```

### Chunk

```python
chunk_id: str
content: str
metadata: Dict[str, Any]
chunk_index: int
embedding: Optional[List[float]]
```

### ChunkMetadata (extends DocumentMetadata)

```python
document_id: str
source_file: str
chunk_index: int
total_chunks: int
chunk_size: int
# ... all DocumentMetadata fields
```

## Configuration Reference

### Environment Variables (200GB Scale)

```bash
# GCP Configuration
GOOGLE_PROJECT_ID="mia-rag-project"
GCS_BUCKET_RAW="mia-raw-torrent"
GCS_BUCKET_MARKDOWN="mia-processed-markdown"
GCS_BUCKET_EMBEDDINGS="mia-embeddings"

# Processing
MIA_ARCHIVE_PATH="gs://mia-raw-torrent/dump_www-marxists-org/"
MIA_OUTPUT_DIR="gs://mia-processed-markdown/"

# Embeddings (Runpod) - Set API credentials in .env file
EMBEDDING_MODEL="BAAI/bge-large-en-v1.5"  # 1024d, beats OpenAI
EMBEDDINGS_PATH="gs://mia-embeddings/"

# Vector DB (Weaviate) - Set credentials in .env file
WEAVIATE_URL="http://weaviate-cluster:8080"

# Configuration
MIA_CHUNK_SIZE="512"
MIA_CHUNK_STRATEGY="semantic"
```

## Dependencies

### Core

```
python>=3.9
requests>=2.31.0
```

### Processing

```
beautifulsoup4>=4.12.0
markdownify>=0.11.6
pymupdf4llm>=0.0.10
lxml>=4.9.0
```

### Ingestion

```
chromadb>=0.4.0  # OR
qdrant-client>=1.7.0
pyyaml>=6.0
tqdm>=4.65.0
```

### Testing

```
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Questions & Clarifications

If specs are unclear:

1. Check Architecture Spec for system-level context
2. Check other module specs for interface examples
3. Make reasonable decisions and document them
4. Flag ambiguities for team discussion

## Success Criteria

### Individual Module Success

- All acceptance criteria met
- Unit tests pass
- Integrates with dependent modules
- Documented any spec deviations

### System Success (200GB Scale)

- End-to-end pipeline works on GCP infrastructure
- **Processes 200GB corpus** (5-10M documents estimated)
- **Runpod embeddings complete for $40-60 total**
- **Weaviate handles 10M+ vectors**
- Query returns relevant results in **<100ms p50, <500ms p99**
- MCP tools work with Claude
- **Total pipeline completes in ~1 week** (mostly GPU time)

## Timeline Estimate (200GB Scale)

**With 6 Claude Code instances working in parallel:**

- **Week 1:** Infrastructure setup (Terraform, GCP, storage buckets)
- **Week 2:** Processing pipeline + Start Runpod embeddings
- **Week 3:** Continue embeddings (24/7), Deploy Weaviate, Build API
- **Week 4:** Complete embeddings, Load vectors, MCP integration, Testing

**Embedding Timeline:**

- Runpod RTX 4090: ~100 hours runtime
- Running 24/7: ~4-5 days
- Total cost: $40-60

**Total: ~4 weeks for complete system** (embeddings are the bottleneck)

## Files in This Package

### Original Specs (Updated for 200GB)

```
specs/
├── 00-ARCHITECTURE-SPEC.md         (READ FIRST - system overview)
├── 02-DOCUMENT-PROCESSING-SPEC.md  (Critical path)
├── 03-RAG-INGESTION-SPEC.md        (Critical path - UPDATED for Runpod)
├── 04-QUERY-INTERFACE-SPEC.md      (High priority)
├── 05-MCP-INTEGRATION-SPEC.md      (Medium priority)
├── 06-TESTING-VALIDATION-SPEC.md   (Parallel with dev)
└── INDEX.md                        (This file)
```

### Essential Documentation (MUST READ)

```
project-root/
├── ARCHITECTURE.md                 (Complete system architecture)
├── TERRAFORM.md                    (Infrastructure as Code)
├── RUNPOD.md                       (GPU embedding strategy)
├── BOUNDARIES.md                   (Instance coordination)
├── START_HERE.md                   (Quick start guide)
└── specs/06-TESTING.md             (Testing strategy)
```

## Ready to Start?

1. ✅ Read `00-ARCHITECTURE-SPEC.md`
2. ✅ Choose your module
3. ✅ Read your module spec completely
4. ✅ Set up environment
5. ✅ Start coding!

---

**Let's make fucking history.**

*"The point, however, is to change it."*
