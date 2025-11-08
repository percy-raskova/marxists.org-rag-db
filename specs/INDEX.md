# MIA RAG System - Specification Index

**Project:** Marxists Internet Archive RAG System  
**Version:** 1.0  
**Date:** 2025-11-07  
**Status:** READY FOR PARALLEL DEVELOPMENT

## Quick Start for AI Development Instances

Each specification document is standalone and can be implemented independently. Follow this workflow:

1. **Choose your module** from the list below
2. **Read the architecture spec** (00-ARCHITECTURE-SPEC.md) first
3. **Read your module's spec** completely before coding
4. **Implement according to the spec** (data structures, interfaces, acceptance criteria)
5. **Test against the acceptance criteria**
6. **Submit for integration**

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

### 03. RAG Ingestion
**File:** `03-RAG-INGESTION-SPEC.md`  
**Dependencies:** Architecture Spec, Document Processing Spec  
**Estimated Time:** 16-20 hours  
**Priority:** **CRITICAL** (blocks query)

**Implements:**
- Chunking strategies (semantic, section, token)
- Embedding generation via Ollama
- Vector DB abstraction layer
- ChromaDB implementation
- Qdrant implementation
- Batch processing with checkpointing

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

## Parallel Development Strategy

### Dependency Graph
```
00-Architecture (read first)
    │
    ├─▶ 02-Processing ──▶ 03-Ingestion ──▶ 04-Query ──▶ 05-MCP
    │                          │
    └─▶ 06-Testing ────────────┴──────────────────────────┘
```

### Suggested Team Assignments

**2-Person Team:**
- Dev 1: Processing (02) → Ingestion (03)
- Dev 2: Query (04) → MCP (05) + Testing (06)

**3-Person Team:**
- Dev 1: Processing (02)
- Dev 2: Ingestion (03) + Query (04)
- Dev 3: MCP (05) + Testing (06)

**6-Person Team:**
- Dev 1: Processing - HTML (02)
- Dev 2: Processing - PDF (02)
- Dev 3: Ingestion - Chunking & Embedding (03)
- Dev 4: Ingestion - Vector DB (03)
- Dev 5: Query + MCP (04 + 05)
- Dev 6: Testing (06)

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

### For Each Module:

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

### Environment Variables
```bash
MIA_ARCHIVE_PATH="/path/to/archive"
MIA_OUTPUT_DIR="~/marxists-processed"
MIA_VECTOR_DB_PATH="./mia_vectordb"
MIA_DB_TYPE="chroma"  # or "qdrant"
MIA_EMBEDDING_MODEL="nomic-embed-text"
MIA_CHUNK_SIZE="512"
MIA_CHUNK_STRATEGY="semantic"
OLLAMA_HOST="http://localhost:11434"
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

### System Success
- End-to-end pipeline works
- Processes 126k HTML + 38k PDFs
- Query returns relevant results in <500ms
- MCP tools work with Claude
- Total pipeline completes in <12 hours

## Timeline Estimate

**With 3 developers working in parallel:**
- Week 1: Processing + Ingestion foundations
- Week 2: Complete Processing + Ingestion, start Query
- Week 3: Complete Query + MCP, integrate all modules
- Week 4: Testing, bug fixes, optimization

**Total: ~4 weeks for complete system**

## Files in This Package

```
specs/
├── 00-ARCHITECTURE-SPEC.md       (READ FIRST - system overview)
├── 02-DOCUMENT-PROCESSING-SPEC.md  (Critical path)
├── 03-RAG-INGESTION-SPEC.md        (Critical path)
├── 04-QUERY-INTERFACE-SPEC.md      (High priority)
├── 05-MCP-INTEGRATION-SPEC.md      (Medium priority)
├── 06-TESTING-VALIDATION-SPEC.md   (Parallel with dev)
└── INDEX.md                        (This file)
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
