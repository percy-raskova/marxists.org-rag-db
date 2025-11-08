# Documentation Consistency Guide

## Overview

This document ensures all documentation is consistent, non-contradictory, and crystal clear for the 6 parallel Claude Code instances working on the 200GB MIA RAG system.

## Primary Truth Sources

### Scale & Architecture
- **Corpus Size**: 200GB (NOT 38GB)
- **Document Count**: 5-10 million estimated
- **Cloud Provider**: Google Cloud Platform (primary)
- **Vector Database**: Weaviate (NOT Chroma/Qdrant for production)
- **Embeddings**: Runpod.io GPU rental (NOT Ollama)
- **Development**: 6 parallel Claude instances (NOT 3)

### Cost Targets
- **One-time Processing**: $120-200 total
  - Runpod embeddings: $40-60
  - GCP compute: $50-100
  - Temporary storage: $20
- **Monthly Operational**: $80-100
  - Storage: ~$55
  - Compute: ~$25-45
  - Networking: ~$18

## Document Hierarchy

### Tier 1: Executive Overview
1. **[200GB_SOLUTION_SUMMARY.md](./200GB_SOLUTION_SUMMARY.md)** - Start here for quick overview
2. **[CLAUDE_ENTERPRISE.md](./CLAUDE_ENTERPRISE.md)** - Complete 200GB architecture

### Tier 2: Infrastructure & Architecture
1. **[CLOUD-ARCHITECTURE-PLAN.md](./CLOUD-ARCHITECTURE-PLAN.md)** - GCP infrastructure details
2. **[TERRAFORM-INFRASTRUCTURE.md](./TERRAFORM-INFRASTRUCTURE.md)** - IaC implementation
3. **[STORAGE-STRATEGY.md](./STORAGE-STRATEGY.md)** - Storage tiers and formats

### Tier 3: Implementation Details
1. **[RUNPOD_EMBEDDINGS.md](./RUNPOD_EMBEDDINGS.md)** - GPU rental strategy
2. **[PARALLEL-DEV-ARCHITECTURE.md](./PARALLEL-DEV-ARCHITECTURE.md)** - 6-instance coordination
3. **[PARALLEL-TEST-STRATEGY.md](./PARALLEL-TEST-STRATEGY.md)** - Test infrastructure

### Tier 4: Original Specs (Updated)
1. **[specs/INDEX.md](./specs/INDEX.md)** - Updated for 200GB scale
2. **[specs/00-ARCHITECTURE-SPEC.md](./specs/00-ARCHITECTURE-SPEC.md)** - System overview
3. Other specs in `specs/` directory

## Key Decisions (Canonical)

### 1. Embedding Strategy
**Decision**: Runpod.io GPU rental with RTX 4090

**Rationale**:
- Cost: $40-60 total vs $500-1000 for APIs
- Control: Full control over process
- Privacy: Data never leaves your infrastructure
- Model: BAAI/bge-large-en-v1.5 (1024d, beats OpenAI ada-002)

**NOT**:
- ~~Ollama locally~~ (won't scale to 200GB)
- ~~VertexAI~~ (too expensive at $500-1000)
- ~~OpenAI API~~ (privacy concerns, expensive)

### 2. Vector Database
**Decision**: Weaviate on GKE

**Rationale**:
- Scale: Handles 10M+ vectors easily
- Features: Hybrid search, production-grade
- Integration: Native GCP support
- Performance: <100ms p50 queries

**NOT**:
- ~~ChromaDB~~ (fine for dev, not for 200GB production)
- ~~Qdrant~~ (good alternative but Weaviate preferred)
- ~~pgvector~~ (won't handle 10M vectors)

### 3. Storage Strategy
**Decision**: GCS with lifecycle policies

**Storage Tiers**:
- Raw torrent: Archive ($2.40/month for 200GB)
- Markdown: Standard→Nearline ($1/month for 50GB)
- Embeddings: Parquet on Standard ($0.40/month for 20GB)
- Vector DB: Persistent SSD ($51/month for 3x100GB)

**NOT**:
- ~~Local storage~~ (not scalable)
- ~~S3~~ (GCS is cheaper for archive)
- ~~Uncompressed embeddings~~ (Parquet saves 60%)

### 4. Development Strategy
**Decision**: 6 parallel Claude Code instances

**Instance Assignments**:
1. Storage & Pipeline (GCS, lifecycle)
2. Embeddings (Runpod orchestration)
3. Weaviate (Vector DB deployment)
4. API (Query interface)
5. MCP (Claude integration)
6. Monitoring (Metrics, integration tests)

**NOT**:
- ~~Sequential development~~ (too slow)
- ~~3-person team~~ (insufficient for 200GB)
- ~~Single developer~~ (would take months)

## Common Confusions to Avoid

### ❌ WRONG: "Use Ollama for embeddings"
✅ **RIGHT**: Use Runpod.io GPU rental with sentence-transformers

### ❌ WRONG: "38GB corpus from Internet Archive"
✅ **RIGHT**: 200GB complete corpus

### ❌ WRONG: "ChromaDB for production"
✅ **RIGHT**: Weaviate for production, ChromaDB ok for dev/testing

### ❌ WRONG: "Run everything locally"
✅ **RIGHT**: GCP cloud infrastructure with Terraform

### ❌ WRONG: "Use the reference implementation as-is"
✅ **RIGHT**: Reference implementation needs scaling for 200GB

## File Path Conventions

### Cloud Storage Paths
```
gs://mia-raw-torrent/          # 200GB raw archive
gs://mia-processed-markdown/   # 50GB processed docs
gs://mia-embeddings/           # 20GB Parquet files
gs://mia-backups/              # Backups
```

### Local Development Paths
```
~/mia-rag-system/              # Project root
├── terraform/                 # Infrastructure code
├── src/                       # Source code
├── tests/                     # Test suites
└── docs/                      # Documentation
```

## API & Interface Contracts

### Storage Interface
```python
def upload(path: str, content: str) -> str  # Returns gs:// URL
def download(path: str) -> str              # Returns content
def list_files(prefix: str) -> List[str]    # Returns file list
```

### Embedding Interface
```python
def generate_embedding(text: str) -> List[float]  # 1024 dimensions
def batch_embeddings(texts: List[str]) -> List[List[float]]
def save_to_parquet(embeddings: List, path: str) -> bool
```

### Weaviate Interface
```python
def search(vector: List[float], limit: int) -> List[Dict]
def insert_batch(documents: List[Dict]) -> bool
def get_count() -> int
```

## Testing Standards

### Unit Tests
- No cloud dependencies
- Use mocks for external services
- Run in milliseconds
- 80% coverage minimum

### Integration Tests
- Use Docker containers locally
- TestContainers for Weaviate
- Mock Runpod API
- Run in seconds

### E2E Tests (Optional)
- Use dev GCP environment
- 1GB sample data
- Run nightly only
- Not required for PR

## Version Numbers

### Documentation Version
- Current: 2.0 (200GB scale update)
- Previous: 1.0 (38GB original)

### API Versions
- Storage API: v1
- Embedding API: v1
- Query API: v1
- MCP Protocol: v1

## Monitoring & Metrics

### Key Metrics to Track
- Documents processed: Target 5-10M
- Embeddings generated: Target 10M+
- Storage used: Target <300GB total
- Query latency: Target <100ms p50
- Monthly cost: Target <$100

### Alert Thresholds
- Cost: Alert at $80/month
- Storage: Alert at 80% quota
- Latency: Alert at >500ms p99
- Errors: Alert at >5% error rate

## Parallel Development Checklist

Before starting development, each instance should verify:

- [ ] Read CLAUDE_ENTERPRISE.md
- [ ] Read CLOUD-ARCHITECTURE-PLAN.md
- [ ] Read PARALLEL-DEV-ARCHITECTURE.md for your assignment
- [ ] Understand you're working with 200GB, not 38GB
- [ ] Know that embeddings use Runpod, not Ollama
- [ ] Know that production uses Weaviate, not ChromaDB
- [ ] Have your isolated GCS bucket prefix
- [ ] Have your Terraform workspace
- [ ] Know your interface contracts
- [ ] Have test fixtures ready

## Questions? Check These First:

1. **Scale questions** → CLOUD-ARCHITECTURE-PLAN.md
2. **Embedding questions** → RUNPOD_EMBEDDINGS.md
3. **Storage questions** → STORAGE-STRATEGY.md
4. **Development questions** → PARALLEL-DEV-ARCHITECTURE.md
5. **Testing questions** → PARALLEL-TEST-STRATEGY.md
6. **Infrastructure questions** → TERRAFORM-INFRASTRUCTURE.md

## Update Protocol

When updating any documentation:
1. Update this consistency guide first
2. Update all affected documents
3. Verify no contradictions
4. Update version numbers
5. Note changes in git commit

---

**Last Consistency Check**: 2025-11-07
**All Documents Aligned**: ✅ YES
**Ready for Parallel Development**: ✅ YES