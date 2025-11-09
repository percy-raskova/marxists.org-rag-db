# Instance 1: Storage & Data Pipeline

**Quick Start Guide for AI Agent Working on Storage Module**

## 🎯 Your Role

You are responsible for **storage and data pipeline orchestration** - the foundation layer that all other instances depend on.

**Status**: ✅ Ready for development (195GB downloaded, GCS configured)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/storage/          # GCS abstractions, lifecycle policies
src/mia_rag/pipeline/         # Data ingestion pipeline
tests/unit/instance1_storage/ # Your unit tests
tests/unit/instance1_pipeline/# Pipeline tests
docs/instances/instance1-storage/  # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**: NONE - you are the foundation layer

**Who depends on you**:
- Instance 2 (embeddings) reads your processed markdown
- Instance 3 (weaviate) reads your metadata
- Instance 6 (monitoring) observes your pipelines

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class StorageInterface(Protocol):
    """Contract that other instances use"""
    def upload(self, path: str, content: bytes) -> str
    def download(self, path: str) -> bytes
    def list_files(self, prefix: str) -> List[str]
    def get_metadata(self, path: str) -> dict

class PipelineInterface(Protocol):
    """Orchestration contract"""
    def process_batch(self, files: List[Path]) -> PipelineResult
    def get_status(self) -> PipelineStatus
```

### Your Deliverables

1. **GCS Storage Client** (`src/mia_rag/storage/gcs_client.py`)
   - Bucket operations (upload/download/list)
   - Lifecycle policy management
   - Retry logic with exponential backoff
   - Checkpointing for resume

2. **Data Pipeline** (`src/mia_rag/pipeline/orchestrator.py`)
   - HTML → Markdown conversion
   - PDF → Markdown conversion
   - Metadata extraction with YAML frontmatter
   - Batch processing (1000 files/batch)
   - Progress tracking

3. **Storage Tiers** (see docs/instances/instance1-storage/)
   - Hot tier: gs://mia-processed-markdown/ (Parquet)
   - Warm tier: gs://mia-raw-html/ (7-day lifecycle)
   - Cold tier: gs://mia-archive/ (Coldline storage)

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance1           # Run your tests only
mise run quality:instance1        # Lint your code
mise run pipeline:process         # Test pipeline locally
mise run storage:sync             # Sync to GCS

# Check your boundaries
python scripts/check_boundaries.py --instance storage

# Submit work
git add src/mia_rag/storage/
git commit -m "feat(storage): implement GCS lifecycle policies"
git push origin storage-dev
```

---

## 📚 Essential Corpus Analysis Reading

**CRITICAL**: Metadata extraction must follow the corpus-informed schema. Read these BEFORE coding:

### Required Reading
1. **[Metadata Unified Schema](./docs/corpus-analysis/06-metadata-unified-schema.md)** ⭐ ESSENTIAL
   - 5-layer metadata model (Core → Authorship → Temporal → Technical → Semantic)
   - **85%+ author coverage target** through multi-source extraction
   - Section-specific extraction rules:
     - Archive: 100% path-based (`/archive/author-name/work/`)
     - ETOL: 85% title + keywords (low meta tag accuracy)
     - EROL: 95% organization from title (not meta tags!)
   - **Character encoding**: 62% ISO-8859-1 → UTF-8 normalization required
   - Confidence scoring for all extracted metadata

2. **[Document Processing Spec v2.0](./specs/02-DOCUMENT-PROCESSING-SPEC.md)**
   - Corpus-informed extraction algorithms
   - CSS class patterns from corpus analysis (`.fst`, `.footer`, `.linkback` removal)
   - Edge case handling (index pages, multi-article files)

### Section-Specific References (Implementation Details)
- [Archive Analysis](./docs/corpus-analysis/01-archive-section-analysis.md) - 15,637 files, metadata patterns
- [History Analysis](./docs/corpus-analysis/02-history-section-spec.md) - ETOL/EROL/Other subsection differences
- [Subject Analysis](./docs/corpus-analysis/03-subject-section-spec.md) - Thematic taxonomy structure
- [Glossary Analysis](./docs/corpus-analysis/04-glossary-section-spec.md) - Entity extraction foundation
- [Reference Analysis](./docs/corpus-analysis/05-reference-section-spec.md) - 100% Git-LFS storage (must run `git lfs pull`)

**Why This Matters**: Your metadata extraction directly impacts search quality for all downstream instances. The corpus analysis provides concrete extraction strategies achieving 85%+ accuracy targets.

---

## 📋 Development Checklist

- [ ] **Read corpus analysis metadata schema** (see Essential Reading above) ⭐
- [ ] Read `docs/architecture/storage-strategy.md` (Parquet schema, lifecycle)
- [ ] Read `specs/01-STORAGE-PIPELINE.md` (formal specification)
- [ ] Set up GCS service account credentials in `.env.instance1` (see AI-AGENTS.md for setup)
- [ ] Implement `StorageInterface` in `src/mia_rag/storage/gcs_client.py`
- [ ] Implement `PipelineInterface` in `src/mia_rag/pipeline/orchestrator.py`
- [ ] Write tests (target: >80% coverage)
- [ ] Test with 1GB sample data before full 200GB run
- [ ] Document your interfaces in work logs (`work-logs/instance1/`)

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/storage/` or `src/mia_rag/pipeline/`
- ❌ Change `StorageInterface` or `PipelineInterface` without RFC
- ❌ Load entire 200GB into memory (use streaming!)
- ❌ Hardcode GCS bucket names (use environment variables)
- ❌ Skip tests or commit with <80% coverage

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Stream data in batches (1000 files max)
- ✅ Add checkpoints for resume after failures
- ✅ Log progress to `work-logs/instance1/`
- ✅ Run pre-commit hooks before committing

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance1-storage/README.md` - Your detailed guide
2. `docs/architecture/storage-strategy.md` - Storage tiers, Parquet schema
3. `specs/01-STORAGE-PIPELINE.md` - Formal specification

**Reference**:
- `ARCHITECTURE.md` - GCP infrastructure
- `TERRAFORM.md` - Infrastructure as code
- `specs/06-TESTING.md` - Testing without cloud

**Communication**:
- `work-logs/instance1/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `StorageInterface` implemented and documented
- [ ] `PipelineInterface` implemented and documented
- [ ] Can process 1GB sample data end-to-end
- [ ] Work log updated with progress
- [ ] Integration tests pass (Instance 6 will run these)

---

## 💡 Pro Tips

**Performance**:
- Use `google-cloud-storage` bulk operations (not one-by-one)
- Enable GCS request logging for debugging
- Test with MinIO locally before hitting real GCS

**Cost**:
- Use lifecycle policies to auto-delete intermediate files
- Compress markdown before upload (saves 60% storage)
- Use us-central1 region (cheapest)

**Debugging**:
- Check GCS logs: `gcloud logging read "resource.type=gcs_bucket"`
- Monitor quota: `gcloud compute project-info describe`

---

**Need help?** Check `docs/instances/instance1-storage/troubleshooting.md` or post in `work-logs/questions.md`

**Last Updated**: 2025-11-08
