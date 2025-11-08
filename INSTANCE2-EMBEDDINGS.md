# Instance 2: Embeddings Pipeline

**Quick Start Guide for AI Agent Working on Embeddings Module**

## 🎯 Your Role

You are responsible for **embedding generation via Runpod GPU rental** - converting 200GB of text into searchable vectors for $40-60 total.

**Status**: ✅ Ready for development (waiting on Instance 1 to process markdown)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/embeddings/       # Batch processor, Runpod orchestration
tests/unit/instance2_embeddings/  # Your unit tests
docs/instances/instance2-embeddings/  # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**:
- Instance 1 (storage) for processed markdown files
  - Uses: `StorageInterface.list_files()`, `StorageInterface.download()`

**Who depends on you**:
- Instance 3 (weaviate) reads your Parquet embedding files
- Instance 6 (monitoring) tracks your batch progress

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class EmbeddingInterface(Protocol):
    """Contract that other instances use"""
    def generate_embeddings(self, texts: List[str]) -> np.ndarray
    def batch_process(self, file_paths: List[str]) -> ParquetFile
    def get_checkpoint(self) -> CheckpointState
    def resume_from_checkpoint(self, checkpoint: CheckpointState) -> None

class RunpodOrchestrator(Protocol):
    """GPU orchestration contract"""
    def start_pod(self, gpu_type: str) -> PodID
    def stop_pod(self, pod_id: PodID) -> None
    def get_pod_status(self, pod_id: PodID) -> PodStatus
```

### Your Deliverables

1. **Runpod Orchestrator** (`src/mia_rag/embeddings/runpod_client.py`)
   - Pod lifecycle management (start/stop)
   - Cost tracking ($0.40/hour for RTX 4090)
   - Automatic pod shutdown on completion
   - Error recovery and retry logic

2. **Batch Processor** (`src/mia_rag/embeddings/batch_processor.py`)
   - Process 1000 documents per batch
   - Checkpointing every 10k documents
   - Resume from last checkpoint on failure
   - Progress tracking (files/sec, ETA)

3. **Embedding Storage** (`src/mia_rag/embeddings/parquet_writer.py`)
   - Write embeddings to Parquet format
   - Schema: `[doc_id, chunk_id, embedding_vector, metadata]`
   - Compression: Snappy (60% size reduction)
   - Upload to gs://mia-embeddings/

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance2           # Run your tests only
mise run quality:instance2        # Lint your code
mise run embeddings:batch         # Test batch processing locally
mise run embeddings:cost-estimate # Estimate Runpod cost

# Check your boundaries
python scripts/check_boundaries.py --instance embeddings

# Submit work
git add src/mia_rag/embeddings/
git commit -m "feat(embeddings): implement Runpod batch processor"
git push origin embeddings-dev
```

---

## 📋 Development Checklist

- [ ] Read `docs/instances/instance2-embeddings/README.md` (your detailed guide)
- [ ] Read `RUNPOD.md` (GPU rental strategy, cost optimization)
- [ ] Read `specs/02-EMBEDDINGS.md` (formal specification)
- [ ] Set up Runpod API credentials in `.env.instance2` (see AI-AGENTS.md for env var setup)
- [ ] Implement `EmbeddingInterface` in `src/mia_rag/embeddings/generator.py`
- [ ] Implement `RunpodOrchestrator` in `src/mia_rag/embeddings/runpod_client.py`
- [ ] Test with 1GB sample (1000 docs) before full run
- [ ] Verify checkpoint/resume works
- [ ] Document cost tracking in work logs

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/embeddings/`
- ❌ Change `EmbeddingInterface` without RFC
- ❌ Process all 200GB in one batch (use batches of 1000 docs)
- ❌ Leave Runpod pod running unattended (costs $0.40/hour!)
- ❌ Skip checkpointing (crash = start over = $$$ lost)

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Checkpoint every 10,000 documents
- ✅ Auto-shutdown pod on completion
- ✅ Track costs in work logs
- ✅ Test locally with small model before Runpod

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance2-embeddings/README.md` - Your detailed guide
2. `RUNPOD.md` - GPU rental, cost optimization, pod management
3. `specs/02-EMBEDDINGS.md` - Formal specification

**Reference**:
- `docs/architecture/storage-strategy.md` - Parquet schema details
- `PARALLEL-TEST-STRATEGY.md` - Testing without GPU costs

**Communication**:
- `work-logs/instance2/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `EmbeddingInterface` implemented and documented
- [ ] Can process 1000 documents without errors
- [ ] Checkpoint/resume verified
- [ ] Cost estimate: <$60 for full 200GB
- [ ] Work log updated with progress

---

## 💡 Pro Tips

**Cost Optimization**:
- Use RTX 4090 ($0.40/hour) not A100 ($1.50/hour)
- Batch size = 32 (optimal for 4090)
- Expected: 100-125 hours @ $40-60 total
- Auto-shutdown prevents $$ waste

**Performance**:
- Use `nomic-embed-text` model (768d, fast)
- Process 1000-2000 docs/hour on 4090
- Enable mixed precision (FP16) for 2x speed

**Debugging**:
- Test with `sentence-transformers` locally first
- Monitor Runpod dashboard for pod status
- Check Parquet files: `parquet-tools show embedding.parquet`

---

**Need help?** Check `docs/instances/instance2-embeddings/troubleshooting.md`

**Last Updated**: 2025-11-08
