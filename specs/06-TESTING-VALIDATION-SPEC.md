# Testing & Validation Module Specification

**Version:** 1.0  
**Status:** SPECIFICATION  
**Module:** `tests/`  
**Dependencies:** All module specs

## Overview

Comprehensive testing strategy for MIA RAG system, including unit tests, integration tests, and quality metrics.

## Test Structure

```
tests/
├── unit/
│   ├── test_html_processor.py
│   ├── test_pdf_processor.py
│   ├── test_chunking.py
│   ├── test_embedding.py
│   └── test_vectordb.py
├── integration/
│   ├── test_end_to_end.py
│   ├── test_mcp_integration.py
│   └── test_query_quality.py
├── fixtures/
│   ├── sample_documents/
│   ├── expected_outputs/
│   └── test_data.json
└── conftest.py
```

## Unit Test Requirements

### Document Processing
- [ ] HTML → Markdown conversion preserves structure
- [ ] PDF → Markdown extraction works
- [ ] Metadata extraction is accurate (>70% for author)
- [ ] Language filtering has >95% precision
- [ ] Content hashing is deterministic

### Chunking
- [ ] Semantic chunking respects boundaries
- [ ] Section chunking preserves headers
- [ ] Token chunking doesn't exceed limits
- [ ] Overlap works correctly

### Embedding & Vector DB
- [ ] Embeddings are 768-dimensional
- [ ] Vector DB insert/search works
- [ ] Batch operations handle errors
- [ ] Checkpointing enables resume

## Integration Test Requirements

### End-to-End Pipeline
```python
def test_full_pipeline():
    """Test complete pipeline on sample data"""
    # 1. Process sample archive (10 docs)
    processor = DocumentProcessor(sample_archive, test_output)
    processor.process_archive()
    
    # 2. Ingest to vector DB
    ingestor = IngestionOrchestrator(test_output / "markdown", vectordb, ...)
    ingestor.ingest()
    
    # 3. Query
    searcher = Searcher(vectordb, embedder)
    results = searcher.search("What is dialectical materialism?")
    
    # 4. Verify results
    assert len(results) > 0
    assert any("dialectical" in r.content.lower() for r in results)
```

### Query Quality
```python
def test_query_quality():
    """Test query returns relevant results"""
    test_queries = [
        ("What is surplus value?", ["marx", "capital", "labor"]),
        ("How to organize vanguard party?", ["lenin", "party", "organization"]),
        ("Theory of imperialism", ["imperialism", "monopoly", "finance"])
    ]
    
    for query, expected_keywords in test_queries:
        results = searcher.search(query, n_results=5)
        
        # Check at least one result contains expected keywords
        assert any(
            all(kw in r.content.lower() for kw in expected_keywords)
            for r in results
        )
```

## Quality Metrics

### Processing Quality
- **Metadata Completeness:** % of documents with author, title, date
- **Language Filter Accuracy:** Precision/recall on English detection
- **Conversion Quality:** Manual review of 100 random conversions

### RAG Quality
- **Retrieval Accuracy:** Top-5 contains relevant result (manual eval on 50 queries)
- **Semantic Similarity:** Average cosine similarity of top results
- **Response Time:** P50, P95, P99 query latency

### Test Coverage Targets
- **Unit Test Coverage:** >80%
- **Integration Test Coverage:** >60%
- **Critical Path Coverage:** 100%

## Performance Benchmarks

```python
def benchmark_processing():
    """Benchmark processing speed"""
    # Target: >100 HTML/min, >10 PDF/min
    pass

def benchmark_embedding():
    """Benchmark embedding generation"""
    # Target: >50 chunks/sec
    pass

def benchmark_query():
    """Benchmark query latency"""
    # Target: <500ms for top-5 results
    pass
```

## Test Data

### Sample Documents (fixtures/)
- `marx_manifesto.htm` - Clean HTML
- `lenin_state.html` - Complex structure
- `capital_vol1.pdf` - Scanned PDF
- `luxemburg_mass_strike.htm` - Theory text
- `gramsci_prison_notebooks.pdf` - Dense theory

### Expected Outputs
- Markdown conversions
- Metadata JSON
- Query result sets for validation

## Continuous Integration

### Pre-commit Hooks
- [ ] Run linters (black, flake8, mypy)
- [ ] Run unit tests
- [ ] Check test coverage

### CI Pipeline
```yaml
name: Test MIA RAG

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit -v
      - name: Run integration tests
        run: pytest tests/integration -v
      - name: Check coverage
        run: pytest --cov=src --cov-report=term-missing
```

## Acceptance Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage >80%
- [ ] Performance benchmarks met
- [ ] Query quality validated
- [ ] No memory leaks
- [ ] Error handling works

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |

---

**Implementation Priority:** MEDIUM (parallel with development)
