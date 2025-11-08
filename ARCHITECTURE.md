# MIA RAG System Architecture (50GB Optimized)

**Consolidated architecture documentation for the Marxists Internet Archive RAG system - optimized for feasibility.**

---

## Executive Summary

- **Scale**: 50GB corpus (optimized from 200GB through strategic content filtering)
- **Infrastructure**: Simplified architecture - can use managed services or self-hosted
- **Cost**: ~$100-150 for one-time embedding generation + ~$30-50/month operational
- **Development**: Simplified from 6 to 3-4 parallel workstreams
- **Status**: ✅ Corpus optimized and ready for processing

**Key Decision**: See [ADR-001](docs/adr/ADR-001-corpus-optimization.md) for corpus optimization rationale (75% reduction)

**Quick Navigation**:
- Instance developers → See `INSTANCE{1-6}-*.md` for your role
- Architecture details → Continue reading below
- Infrastructure → See `TERRAFORM.md` and `docs/architecture/infrastructure.md`
- Testing → See `PARALLEL-TEST-STRATEGY.md`

---

## System Architecture

### High-Level Data Flow

```
Archive Sources (50GB - optimized)
    ↓
[Phase 1: Storage & Processing]
  - Local/Cloud storage options
  - HTML → Markdown conversion (priority)
  - Essential PDFs only (~10GB)
  - Output: Structured markdown with metadata
    ↓
[Phase 2: Embeddings]
  - Option A: Runpod.io GPU ($0.40/hr, ~25-30 hours = $100-120)
  - Option B: Local GPU if available
  - Option C: CPU embeddings (slower but free)
  - Model: nomic-embed-text or similar
    ↓
[Phase 3: Vector Database]
  - Option A: Weaviate (production-ready)
  - Option B: Qdrant (simpler deployment)
  - Option C: ChromaDB (local development)
  - Scale: ~1-2 million vectors (manageable)
    ↓
[Phase 4: Query Interface]
  - FastAPI or Flask API
  - Optional caching with Redis
  - MCP integration for Claude
  - Simple rate limiting
```

---

## Technology Stack

### Storage & Processing
- **Cloud Storage**: Google Cloud Storage (GCS)
  - Hot tier: gs://mia-processed-markdown/ (Parquet, Standard class)
  - Warm tier: gs://mia-raw-html/ (7-day lifecycle to Coldline)
  - Cold tier: gs://mia-archive/ (Coldline storage)
- **Format**: Apache Parquet with Snappy compression (60% size reduction)
- **Processing**: Python with `beautifulsoup4`, `pymupdf4llm`, `markdownify`

### Embeddings
- **Provider**: Runpod.io GPU rental
- **GPU**: RTX 4090 ($0.40/hour, 100-125 hours total = $40-60)
- **Model**: nomic-embed-text (768 dimensions)
- **Batch Size**: 32 documents/batch (optimal for 4090)
- **Throughput**: 1000-2000 documents/hour

### Vector Database
- **Database**: Weaviate 1.23+ (open-source, production-ready)
- **Deployment**: Google Kubernetes Engine (GKE) Autopilot
- **Index**: HNSW with ef=128, maxConnections=64
- **Scale**: Billion-scale vectors (tested to 10B+)
- **Query Speed**: <100ms p95 for semantic search

### API & Integration
- **API Framework**: FastAPI with Pydantic validation
- **Caching**: Redis (1-hour TTL for queries)
- **Rate Limiting**: 100 requests/minute per IP
- **MCP Protocol**: stdio transport for Claude integration
- **Deployment**: Cloud Run (serverless, auto-scaling)

### Monitoring & Testing
- **Metrics**: Prometheus with custom exporters
- **Dashboards**: Grafana with instance-specific views
- **Testing**: pytest with mocking for cloud services
- **CI/CD**: GitHub Actions with daily integration tests

---

## Cost Breakdown

### One-Time Costs
| Item | Cost | Notes |
|------|------|-------|
| Runpod GPU rental | $40-60 | RTX 4090, 100-125 hours for embeddings |
| **Total One-Time** | **$40-60** | |

### Monthly Operational Costs
| Service | Cost/Month | Notes |
|---------|------------|-------|
| GCS Storage (200GB) | $4 | Standard class, us-central1 |
| GKE Autopilot (Weaviate) | $120-150 | n2-standard-4, ~3 nodes |
| Cloud Run (API) | $5-10 | Minimal traffic, scales to zero |
| Redis (Memorystore) | $10-20 | 1GB instance |
| Cloud Monitoring | $5 | Logs + metrics |
| **Total Monthly** | **$144-189** | |

### Cost Optimization Strategies
1. **Storage**: Lifecycle policies auto-delete intermediate files after 7 days
2. **Compute**: GKE Autopilot scales down during low usage
3. **API**: Cloud Run scales to zero when idle
4. **Embeddings**: Runpod spot instances (if available) can save 50%

---

## 6-Instance Parallel Development Architecture

### Instance Ownership Matrix

| Instance | ID | Owned Paths | Dependencies | Entry Point |
|----------|----|-----------|--------------| ------------|
| 1 | storage | `src/mia_rag/storage/`, `src/mia_rag/pipeline/` | None | [INSTANCE1-STORAGE.md](./INSTANCE1-STORAGE.md) |
| 2 | embeddings | `src/mia_rag/embeddings/` | Instance 1 | [INSTANCE2-EMBEDDINGS.md](./INSTANCE2-EMBEDDINGS.md) |
| 3 | weaviate | `src/mia_rag/vectordb/` | Instance 2 | [INSTANCE3-WEAVIATE.md](./INSTANCE3-WEAVIATE.md) |
| 4 | api | `src/mia_rag/api/` | Instance 3 | [INSTANCE4-API.md](./INSTANCE4-API.md) |
| 5 | mcp | `src/mia_rag/mcp/` | Instance 4 | [INSTANCE5-MCP.md](./INSTANCE5-MCP.md) |
| 6 | monitoring | `src/mia_rag/monitoring/`, `tests/integration/` | All | [INSTANCE6-MONITORING.md](./INSTANCE6-MONITORING.md) |

### Coordination Mechanisms

**Interface Contracts** (`src/mia_rag/interfaces/contracts.py`):
- Shared Protocol classes define instance boundaries
- Changes require RFC with 24-hour review window
- Enforced by pre-commit hooks

**Async Communication**:
- Work logs in `work-logs/instance{1-6}/`
- RFCs in `docs/rfc/` (use RFC-TEMPLATE.md)
- Daily integration tests verify compatibility

**Conflict Prevention**:
- Pre-commit hook checks instance boundaries
- Automated merge conflict detection
- Instance-specific git branches

---

## Data Schemas

### DocumentMetadata (YAML Frontmatter)

```yaml
---
source_url: https://www.marxists.org/archive/marx/works/1867-c1/
title: Capital, Volume I
author: Karl Marx
date: 1867
language: en
doc_type: book
word_count: 195847
content_hash: sha256:abc123...
---
```

### Embedding Parquet Schema

```python
schema = pa.schema([
    ("doc_id", pa.string()),           # Unique document identifier
    ("chunk_id", pa.string()),          # Chunk identifier within doc
    ("chunk_index", pa.int32()),        # Sequential chunk number
    ("embedding", pa.list_(pa.float32(), 768)),  # 768d vector
    ("text", pa.string()),              # Original text chunk
    ("metadata", pa.struct([           # Nested metadata
        ("author", pa.string()),
        ("title", pa.string()),
        ("date", pa.int32()),
        ("word_count", pa.int32())
    ]))
])
```

### Weaviate Collection Schema

```python
{
    "class": "MarxistTheory",
    "vectorizer": "none",  # We provide our own embeddings
    "vectorIndexConfig": {
        "ef": 128,
        "maxConnections": 64,
        "efConstruction": 128
    },
    "properties": [
        {"name": "author", "dataType": ["string"], "indexSearchable": True},
        {"name": "title", "dataType": ["string"]},
        {"name": "date", "dataType": ["int"], "indexSearchable": True},
        {"name": "source_url", "dataType": ["string"]},
        {"name": "text", "dataType": ["text"]},
        {"name": "language", "dataType": ["string"], "indexFilterable": True}
    ]
}
```

---

## Infrastructure Components

### Google Cloud Platform Setup

**Project**: `mia-rag-production`
**Region**: `us-central1` (cheapest)

**Key Services**:
1. **Cloud Storage** - Document and embedding storage
2. **GKE Autopilot** - Weaviate vector database cluster
3. **Cloud Run** - Serverless API deployment
4. **Memorystore (Redis)** - Query result caching
5. **Cloud Monitoring** - Logs, metrics, alerts

**Service Accounts**:
- `storage-service@mia-rag.iam.gserviceaccount.com` - GCS access
- `weaviate-service@mia-rag.iam.gserviceaccount.com` - GKE workload identity
- `api-service@mia-rag.iam.gserviceaccount.com` - Cloud Run API

**IAM Roles**:
- Storage Admin: Instance 1
- Storage Object Viewer: Instances 2, 3
- GKE Developer: Instance 3
- Cloud Run Developer: Instance 4

### Terraform Infrastructure

See `TERRAFORM.md` for complete infrastructure as code.

**Modules**:
- `modules/storage/` - GCS buckets with lifecycle policies
- `modules/gke/` - GKE Autopilot cluster for Weaviate
- `modules/cloudrun/` - API deployment
- `modules/redis/` - Memorystore instance
- `modules/monitoring/` - Cloud Monitoring dashboards

---

## Security & Privacy

**Data Privacy**:
- All data public domain (Marxist Internet Archive)
- No PII or sensitive information
- Full corpus downloadable from https://www.marxists.org

**Access Control**:
- Service accounts with least-privilege IAM
- VPC firewall rules for GKE
- API key authentication (optional, not required for public deployment)

**Secrets Management**:
- Google Secret Manager for API keys
- `.env.instance{1-6}` files (gitignored) for local development
- Workload Identity for GKE service accounts

---

## Anti-Patterns & Best Practices

### ❌ NEVER
1. **Load entire 200GB into memory** - Use streaming and batching
2. **Modify code outside your instance** - Causes merge conflicts
3. **Change interface contracts without RFC** - Breaks other instances
4. **Skip tests** - <80% coverage required
5. **Hardcode credentials** - Use environment variables
6. **Deploy without local testing** - Test with sample data first

### ✅ ALWAYS
1. **Use TDD** - Write tests before implementation
2. **Batch processing** - Max 1000 items per batch
3. **Checkpoint progress** - Enable resume after failures
4. **Stream large files** - Never read full file into memory
5. **Log to work-logs/** - Async communication with other instances
6. **Run pre-commit hooks** - Boundary and quality checks

---

## Performance Characteristics

### Storage & Pipeline (Instance 1)
- **Throughput**: ~10-20k documents/hour (HTML conversion)
- **Latency**: <100ms per document
- **Total Processing Time**: 200GB in ~10-20 hours

### Embeddings (Instance 2)
- **Throughput**: 1000-2000 documents/hour (RTX 4090)
- **Cost**: $0.40/hour * 100-125 hours = $40-60
- **Total Time**: ~5 days continuous GPU rental

### Vector Database (Instance 3)
- **Query Latency**: <100ms p95 for semantic search
- **Import Speed**: ~10k vectors/second
- **Index Size**: ~3GB per million 768d vectors
- **Total Import Time**: ~5-10 hours for full corpus

### API (Instance 4)
- **Response Time**: <200ms p95 (including Weaviate)
- **Cache Hit Rate**: >60% for common queries
- **Throughput**: 1000+ queries/second (with caching)

---

## Monitoring & Observability

### Key Metrics

**Storage (Instance 1)**:
- `storage_bytes_total` - Total GCS storage used
- `pipeline_documents_processed` - Processing progress
- `pipeline_errors_total` - Processing failures

**Embeddings (Instance 2)**:
- `embeddings_cost_dollars` - Runpod costs (critical!)
- `embeddings_batch_progress` - Completion percentage
- `embeddings_vectors_generated` - Total vectors

**Weaviate (Instance 3)**:
- `weaviate_query_latency_seconds` - Query performance
- `weaviate_vectors_total` - Index size
- `weaviate_disk_usage_bytes` - Storage consumption

**API (Instance 4)**:
- `api_requests_total` - Request count
- `api_cache_hit_rate` - Cache effectiveness
- `api_error_rate` - Error percentage

---

## Related Documentation

**Instance Guides**:
- [Instance 1: Storage](./INSTANCE1-STORAGE.md)
- [Instance 2: Embeddings](./INSTANCE2-EMBEDDINGS.md)
- [Instance 3: Weaviate](./INSTANCE3-WEAVIATE.md)
- [Instance 4: API](./INSTANCE4-API.md)
- [Instance 5: MCP](./INSTANCE5-MCP.md)
- [Instance 6: Monitoring](./INSTANCE6-MONITORING.md)

**Detailed Docs**:
- [Infrastructure Details](./docs/architecture/infrastructure.md)
- [Storage Strategy](./docs/architecture/storage-strategy.md)
- [Interface Contracts](./docs/architecture/interface-contracts.md)
- [Testing Strategy](./PARALLEL-TEST-STRATEGY.md)
- [Terraform](./TERRAFORM.md)

**Specifications**:
- [Spec Index](./specs/INDEX.md)
- [Architecture Spec](./specs/00-ARCHITECTURE.md)
- [Storage Pipeline Spec](./specs/01-STORAGE-PIPELINE.md)
- [Embeddings Spec](./specs/02-EMBEDDINGS.md)
- [Vector DB Spec](./specs/03-VECTOR-DB.md)
- [API Spec](./specs/04-API.md)
- [MCP Spec](./specs/05-MCP.md)
- [Testing Spec](./specs/06-TESTING.md)

---

**Last Updated**: 2025-11-08
**Status**: ✅ Production-Ready Architecture
