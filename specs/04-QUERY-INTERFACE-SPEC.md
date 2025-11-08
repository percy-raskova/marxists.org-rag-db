# Query Interface Module Specification

**Version:** 1.0  
**Status:** SPECIFICATION  
**Module:** `src/query/`  
**Dependencies:** Architecture Spec 1.0, RAG Ingestion Spec 1.0

## Overview

Provides interfaces for querying the vector database, including CLI, Python API, and preparation for MCP integration.

## Responsibilities

1. Semantic search via embeddings
2. Metadata filtering and ranking
3. Result formatting and display
4. Interactive CLI interface
5. Programmatic Python API

## Module Structure

```
src/query/
├── __init__.py
├── search.py           # Core search logic
├── cli.py              # Interactive CLI
├── filters.py          # Metadata filtering
└── formatters.py       # Result formatting
```

## Core Classes

### Searcher
```python
class Searcher:
    """Main search interface"""
    
    def __init__(self, vectordb: VectorDB, embedder: Embedder):
        self.vectordb = vectordb
        self.embedder = embedder
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               filters: Optional[Dict] = None) -> List[SearchResult]:
        """
        Semantic search
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            filters: Metadata filters (author, date, etc.)
            
        Returns:
            List of SearchResult objects
        """
        # Generate query embedding
        query_embedding = self.embedder.embed(query)
        
        # Search vector DB
        raw_results = self.vectordb.search(query_embedding, n_results * 2)
        
        # Apply filters
        if filters:
            raw_results = self._apply_filters(raw_results, filters)
        
        # Convert to SearchResult objects
        results = [SearchResult.from_dict(r) for r in raw_results[:n_results]]
        
        return results
    
    def search_by_author(self, author: str, n_results: int = 10) -> List[SearchResult]:
        """Search works by specific author"""
        pass
    
    def search_by_date_range(self, start_date: str, end_date: str) -> List[SearchResult]:
        """Search works within date range"""
        pass
```

## CLI Interface

```bash
# Interactive mode
python cli.py --interactive

# Single query
python cli.py --query "What is surplus value?"

# With filters
python cli.py --query "organizing tactics" --author "Lenin" --results 10
```

## Acceptance Criteria

- [ ] Search returns relevant results
- [ ] Query latency <500ms
- [ ] CLI is user-friendly
- [ ] Filters work correctly
- [ ] Results are well-formatted

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |
