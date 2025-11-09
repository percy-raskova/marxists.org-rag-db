# Instance 4: Query & API Layer

**Quick Start Guide for AI Agent Working on API Module**

## 🎯 Your Role

You are responsible for **REST API and query processing** - exposing the RAG system via FastAPI endpoints with caching and rate limiting.

**Status**: ✅ Ready for development (waiting on Instance 3 Weaviate deployment)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/api/              # FastAPI app, endpoints, caching
tests/unit/instance4_api/     # Your unit tests
docs/instances/instance4-api/ # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**:
- Instance 3 (weaviate) for vector search
  - Uses: `VectorDBInterface.search()`, `VectorDBInterface.search_with_filter()`
- Instance 1 (storage) for document retrieval
  - Uses: `StorageInterface.download()`

**Who depends on you**:
- Instance 5 (mcp) wraps your API for Claude integration
- Instance 6 (monitoring) monitors your API health
- End users query your REST endpoints

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class QueryInterface(Protocol):
    """Contract that other instances use"""
    def semantic_search(self, query: str, limit: int) -> List[QueryResult]
    def filter_search(self, filters: QueryFilters, limit: int) -> List[QueryResult]
    def get_context(self, doc_id: str) -> DocumentContext

class CacheInterface(Protocol):
    """Caching contract"""
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: int) -> None
    def invalidate(self, pattern: str) -> None
```

### Your Deliverables

1. **FastAPI Application** (`src/mia_rag/api/app.py`)
   - REST endpoints: /search, /search/advanced, /documents/{id}
   - OpenAPI documentation (auto-generated)
   - CORS configuration
   - Health check endpoint

2. **Query Processor** (`src/mia_rag/api/query_processor.py`)
   - Parse natural language queries
   - Generate embeddings for queries
   - Call Weaviate for vector search
   - Format and rank results

3. **Caching Layer** (`src/mia_rag/api/cache.py`)
   - Redis for query result caching
   - TTL: 1 hour for queries, 24 hours for documents
   - Cache invalidation on data updates
   - LRU eviction policy

4. **Rate Limiting** (`src/mia_rag/api/rate_limit.py`)
   - 100 requests/minute per IP
   - 1000 requests/hour per IP
   - Graceful degradation (503 on limit)

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance4           # Run your tests only
mise run quality:instance4        # Lint your code
mise run api:dev                  # Start dev server (hot reload)
mise run api:test-endpoints       # Test all endpoints

# Check your boundaries
python scripts/check_boundaries.py --instance api

# Submit work
git add src/mia_rag/api/
git commit -m "feat(api): implement semantic search endpoint"
git push origin api-dev
```

---

## 📚 Essential Corpus Analysis Reading

**CRITICAL**: Query expansion and hybrid retrieval depend on corpus cross-reference patterns. Read these BEFORE API design:

### Required Reading
1. **[Knowledge Graph Spec](./specs/08-knowledge-graph-spec.md)** ⭐ ESSENTIAL
   - **Hybrid retrieval patterns**: Vector-first + graph-enhanced, graph-first + vector-filtered, multi-hop traversal
   - **Query expansion via cross-references**: ~5k-10k corpus-extracted links enable "find related works"
   - **Multi-hop query examples**:
     - "Intellectual genealogy": Find works citing Marx → works citing those works → ...
     - "Citation chains": Trace concept evolution through references
     - "Thematic exploration": Subject → related works → authors → other works by those authors
   - **Entity-based filtering**: "Find works by Lenin about imperialism" = vector search + entity filters

2. **[Subject Analysis](./docs/corpus-analysis/03-subject-section-spec.md)**
   - **Multi-dimensional taxonomy**: 8 subject categories (theoretical, economic, political, geographical, etc.)
   - **64% link to /archive/** - enables subject → author navigation
   - **19% link to /reference/** - philosophical foundations routing

3. **[Glossary Analysis](./docs/corpus-analysis/04-glossary-section-spec.md)**
   - **~2,500 entities** for query enrichment ("What is X?" definition queries)
   - **80-95% cross-references** - glossary as knowledge graph hub

**Why This Matters**: Your API should support BOTH simple semantic search ("find documents about X") AND complex graph queries ("find works by Y's contemporaries about Z"). The corpus analysis defines cross-reference patterns that enable these advanced queries.

**Implementation Hint**: Consider separate endpoints for vector-only, graph-only, and hybrid retrieval to optimize performance for different query types.

---

## 📋 Development Checklist

- [ ] **Read knowledge graph spec and subject/glossary analyses** (see Essential Reading above) ⭐
- [ ] Read `docs/instances/instance4-api/README.md` (your detailed guide)
- [ ] Read `docs/architecture/infrastructure.md` (Cloud Run deployment)
- [ ] Read `specs/04-API.md` (formal specification)
- [ ] Set up local Redis (Docker Compose)
- [ ] Implement `QueryInterface` in `src/mia_rag/api/query_processor.py`
- [ ] Implement FastAPI app in `src/mia_rag/api/app.py`
- [ ] Add Pydantic models for request/response validation
- [ ] Test endpoints with Postman/curl
- [ ] Document API contract in work logs

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/api/`
- ❌ Change `QueryInterface` without RFC
- ❌ Return raw database results (sanitize & format!)
- ❌ Skip rate limiting (prevents abuse)
- ❌ Expose internal error details to users

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Validate input with Pydantic
- ✅ Cache query results (reduces Weaviate load)
- ✅ Return structured JSON (not plain text)
- ✅ Log queries for monitoring

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance4-api/README.md` - Your detailed guide
2. `docs/architecture/infrastructure.md` - Cloud Run deployment
3. `specs/04-API.md` - Formal specification

**Reference**:
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Official docs
- `docs/architecture/storage-strategy.md` - Data schemas
- `specs/06-TESTING.md` - Testing without cloud

**Communication**:
- `work-logs/instance4/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `QueryInterface` implemented and documented
- [ ] All endpoints return 200 OK
- [ ] OpenAPI docs auto-generated
- [ ] Cache hit rate >60%
- [ ] Rate limiting works
- [ ] Work log updated

---

## 💡 Pro Tips

**Performance**:
- Cache results for 1 hour (queries rarely change)
- Use Redis pipelining for bulk cache sets
- Return top 10 results (not 100)
- Expected response time: <200ms p95

**Security**:
- Sanitize user queries (prevent injection)
- Rate limit by IP + API key
- CORS: whitelist specific domains only
- Never return raw vector embeddings

**Debugging**:
- Test with curl: `curl -X POST http://localhost:8000/search -d '{"query":"surplus value"}'`
- Check Redis: `redis-cli MONITOR`
- FastAPI docs: `http://localhost:8000/docs`

---

**Need help?** Check `docs/instances/instance4-api/troubleshooting.md`

**Last Updated**: 2025-11-08
