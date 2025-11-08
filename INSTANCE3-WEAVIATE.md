# Instance 3: Weaviate Vector Database

**Quick Start Guide for AI Agent Working on Vector DB Module**

## 🎯 Your Role

You are responsible for **Weaviate vector database deployment and management** - creating the searchable index from embeddings at 200GB scale.

**Status**: ✅ Ready for development (waiting on Instance 2 embedding Parquet files)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/vectordb/           # Weaviate client, schema, import
tests/unit/instance3_weaviate/  # Your unit tests
docs/instances/instance3-weaviate/  # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**:
- Instance 2 (embeddings) for Parquet embedding files
  - Uses: `EmbeddingInterface.read_parquet()`
- Instance 1 (storage) for metadata
  - Uses: `StorageInterface.get_metadata()`

**Who depends on you**:
- Instance 4 (api) queries your vector database
- Instance 6 (monitoring) tracks database health

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class VectorDBInterface(Protocol):
    """Contract that other instances use"""
    def index_batch(self, vectors: np.ndarray, metadata: List[dict]) -> None
    def search(self, query_vector: np.ndarray, limit: int) -> List[SearchResult]
    def search_with_filter(self, query: Query) -> List[SearchResult]
    def get_collection_stats(self) -> CollectionStats

class SchemaManager(Protocol):
    """Schema definition contract"""
    def create_collection(self, name: str, config: CollectionConfig) -> None
    def update_schema(self, changes: SchemaUpdate) -> None
    def get_schema(self) -> Schema
```

### Your Deliverables

1. **Weaviate Client** (`src/mia_rag/vectordb/weaviate_client.py`)
   - Connection management to GKE cluster
   - Batch import (1000 vectors/batch)
   - Query optimization (HNSW parameters)
   - Health monitoring

2. **Schema Manager** (`src/mia_rag/vectordb/schema.py`)
   - Collection: `MarxistTheory` with 768d vectors
   - Properties: author, title, date, language, source_url
   - Indexes: author, date (for metadata filtering)
   - HNSW config: ef=128, maxConnections=64

3. **Import Pipeline** (`src/mia_rag/vectordb/importer.py`)
   - Read Parquet embedding files from GCS
   - Batch import with checkpointing
   - Progress tracking (vectors/sec)
   - Automatic retry on failures

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance3           # Run your tests only
mise run quality:instance3        # Lint your code
mise run weaviate:start           # Start local Weaviate Docker
mise run weaviate:import-sample   # Test import with 1k vectors

# Check your boundaries
python scripts/check_boundaries.py --instance weaviate

# Submit work
git add src/mia_rag/vectordb/
git commit -m "feat(weaviate): implement batch import pipeline"
git push origin weaviate-dev
```

---

## 📋 Development Checklist

- [ ] Read `docs/instances/instance3-weaviate/README.md` (your detailed guide)
- [ ] Read `docs/architecture/infrastructure.md` (GKE deployment)
- [ ] Read `specs/03-VECTOR-DB.md` (formal specification)
- [ ] Set up Weaviate locally (Docker Compose)
- [ ] Implement `VectorDBInterface` in `src/mia_rag/vectordb/weaviate_client.py`
- [ ] Implement `SchemaManager` in `src/mia_rag/vectordb/schema.py`
- [ ] Test with 1k vectors before full import
- [ ] Benchmark query performance (<100ms p95)
- [ ] Document schema decisions in work logs

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/vectordb/`
- ❌ Change `VectorDBInterface` without RFC
- ❌ Import all vectors in one batch (use 1000/batch)
- ❌ Skip HNSW parameter tuning (affects query speed)
- ❌ Deploy to GKE without local testing

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Batch imports (1000 vectors max)
- ✅ Checkpoint every 100k vectors
- ✅ Monitor disk usage (vectors take ~3GB per million)
- ✅ Test queries before full import

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance3-weaviate/README.md` - Your detailed guide
2. `docs/architecture/infrastructure.md` - GKE deployment, Weaviate config
3. `specs/03-VECTOR-DB.md` - Formal specification

**Reference**:
- [Weaviate Docs](https://weaviate.io/developers/weaviate) - Official docs
- `docs/architecture/storage-strategy.md` - Parquet format
- `PARALLEL-TEST-STRATEGY.md` - Testing locally

**Communication**:
- `work-logs/instance3/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `VectorDBInterface` implemented and documented
- [ ] Can import 1M vectors without errors
- [ ] Query performance <100ms p95
- [ ] Schema documented in work logs
- [ ] Health checks passing

---

## 💡 Pro Tips

**Performance**:
- HNSW `ef=128` is optimal for 200GB scale
- Use `maxConnections=64` (not default 32)
- Enable persistence for crash recovery
- Expected query speed: 50-80ms p95

**Cost**:
- Use GKE Autopilot (scales automatically)
- n2-standard-4 nodes (4 vCPU, 16GB RAM)
- Expected cost: ~$150/month for 200GB index

**Debugging**:
- Check Weaviate metrics: `http://localhost:8080/v1/meta`
- Query console: `http://localhost:8080/v1/console`
- Monitor logs: `kubectl logs -f weaviate-0`

---

**Need help?** Check `docs/instances/instance3-weaviate/troubleshooting.md`

**Last Updated**: 2025-11-08
