# 🚧 Instance Boundaries for MIA RAG System

**CRITICAL: Each instance has exclusive ownership of specific directories. Violating these boundaries will cause merge conflicts and break the parallel development workflow.**

## 📍 Instance Ownership Map

### Instance 1: Storage & Pipeline

**Owner**: Storage and data pipeline orchestration
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/storage/
src/mia_rag/pipeline/
tests/unit/instance1_storage/
tests/unit/instance1_pipeline/
docs/instance1/

❌ CANNOT MODIFY:
Any other directories
```

**Responsibilities**:

- GCS bucket management
- Storage lifecycle policies
- Data pipeline orchestration
- Raw data → Processed markdown flow
- Archive management

**Dependencies**: None (first in chain)

**Produces**:

- Processed markdown files in GCS
- Storage metadata
- Pipeline status reports

---

### Instance 2: Embeddings

**Owner**: Embedding generation and management
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/embeddings/
tests/unit/instance2_embeddings/
docs/instance2/

❌ CANNOT MODIFY:
Any other directories
```

**Responsibilities**:

- Runpod GPU orchestration
- Batch embedding generation
- Parquet file creation
- Checkpointing and resume
- Embedding storage in GCS

**Dependencies**: Instance 1 (storage)

**Consumes**:

- Processed markdown from Instance 1

**Produces**:

- Embedding vectors in Parquet format
- Checkpoint files
- Processing metrics

---

### Instance 3: Weaviate Vector DB

**Owner**: Vector database management
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/vectordb/
tests/unit/instance3_weaviate/
docs/instance3/

❌ CANNOT MODIFY:
Any other directories
```

**Responsibilities**:

- Weaviate deployment on GKE
- Schema management
- Batch import of vectors
- Query optimization
- Index management

**Dependencies**: Instance 2 (embeddings)

**Consumes**:

- Embedding Parquet files from Instance 2

**Produces**:

- Searchable vector database
- Query interface
- Database metrics

---

### Instance 4: Query & API

**Owner**: REST API and query interface
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/api/
tests/unit/instance4_api/
docs/instance4/

❌ CANNOT MODIFY:
Any other directories
```

**Responsibilities**:

- FastAPI application
- REST endpoints
- Redis caching layer
- Rate limiting
- Query processing

**Dependencies**: Instance 3 (vectordb)

**Consumes**:

- Vector search from Instance 3

**Produces**:

- REST API endpoints
- Cached query results
- API documentation (OpenAPI)

---

### Instance 5: MCP Integration

**Owner**: Model Context Protocol server
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/mcp/
tests/unit/instance5_mcp/
docs/instance5/

❌ CANNOT MODIFY:
Any other directories
```

**Responsibilities**:

- MCP server implementation
- Tool handlers for Claude
- Context management
- Response formatting

**Dependencies**: Instance 4 (api)

**Consumes**:

- API endpoints from Instance 4

**Produces**:

- MCP tools for Claude
- Formatted responses
- Tool documentation

---

### Instance 6: Monitoring & Testing

**Owner**: System monitoring and integration testing
**Directories**:

```
✅ CAN MODIFY:
src/mia_rag/monitoring/
tests/unit/instance6_monitoring/
tests/integration/      # ONLY Instance 6
tests/scale/           # ONLY Instance 6
tests/contract/        # ONLY Instance 6
docs/instance6/

❌ CANNOT MODIFY:
Other instances' unit tests
Other instances' source code
```

**Responsibilities**:

- Prometheus metrics
- Grafana dashboards
- Integration testing
- Scale testing
- Contract testing
- System health monitoring

**Dependencies**: All instances (for monitoring/testing)

**Consumes**:

- Metrics from all instances

**Produces**:

- Dashboards
- Alerts
- Test reports
- System health status

---

## 🤝 Shared Resources (Require Coordination)

These directories require coordination between instances:

### Interfaces Directory

```
src/mia_rag/interfaces/
```

**Rules**:

- Create RFC in `docs/rfcs/` before changes
- 24-hour review period
- All dependent instances must approve
- Version interfaces if breaking changes needed

### Common Utilities

```
src/mia_rag/common/
```

**Rules**:

- Only add truly shared utilities
- Must have 2+ instances using it
- Include comprehensive tests
- Document usage patterns

### Configuration Files (Root Level)

```
pyproject.toml
.mise.toml
.pre-commit-config.yaml
.gitignore
```

**Rules**:

- Announce changes in work logs
- Test changes don't break other instances
- Prefer additive changes over modifications

### Documentation (Root Level)

```
README.md
AI-AGENT-INSTRUCTIONS.md
INSTANCE-BOUNDARIES.md (this file)
CONTRIBUTING.md
```

**Rules**:

- Update via PR with review
- Keep changes minimal and focused
- Ensure consistency across docs

### Scripts Directory

```
scripts/
```

**Rules**:

- Scripts should be instance-agnostic
- Use instance detection when needed
- Test with all instance configurations

### GitHub Workflows

```
.github/workflows/
```

**Rules**:

- Each instance has its own workflow file
- Shared workflows need approval from all
- Don't modify other instances' workflows

---

## 🔄 Interface Contracts

### Storage → Embeddings Interface

**Contract File**: `src/mia_rag/interfaces/storage_contract.py`
**Owner**: Instance 1
**Consumer**: Instance 2

```python
class StorageInterface(ABC):
    @abstractmethod
    async def list_documents(self, prefix: str) -> List[str]:
        """List all documents with given prefix."""

    @abstractmethod
    async def get_document(self, path: str) -> Document:
        """Retrieve a single document."""

    @abstractmethod
    async def get_batch(self, paths: List[str]) -> List[Document]:
        """Retrieve multiple documents."""
```

### Embeddings → Weaviate Interface

**Contract File**: `src/mia_rag/interfaces/embeddings_contract.py`
**Owner**: Instance 2
**Consumer**: Instance 3

```python
class EmbeddingsInterface(ABC):
    @abstractmethod
    async def list_embedding_files(self) -> List[str]:
        """List all Parquet files with embeddings."""

    @abstractmethod
    async def get_embedding_batch(self, file: str) -> pd.DataFrame:
        """Get embeddings from Parquet file."""
```

### Weaviate → API Interface

**Contract File**: `src/mia_rag/interfaces/vectordb_contract.py`
**Owner**: Instance 3
**Consumer**: Instance 4

```python
class VectorDBInterface(ABC):
    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        limit: int = 10
    ) -> List[SearchResult]:
        """Search for similar vectors."""

    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Document:
        """Get document by ID."""
```

### API → MCP Interface

**Contract File**: `src/mia_rag/interfaces/api_contract.py`
**Owner**: Instance 4
**Consumer**: Instance 5

```python
class APIInterface(ABC):
    @abstractmethod
    async def query(
        self,
        text: str,
        limit: int = 5
    ) -> QueryResponse:
        """Query the RAG system."""

    @abstractmethod
    async def get_metadata(self, doc_id: str) -> Metadata:
        """Get document metadata."""
```

---

## 🚨 Boundary Violation Detection

The pre-commit hook `check-boundaries` will automatically detect violations:

```bash
# This will fail if you modify files outside your boundaries
git commit -m "feat: add new feature"

# Error example:
❌ Boundary Violation Detected!
Instance 2 modified: src/mia_rag/vectordb/client.py
This file belongs to Instance 3

Please revert changes to files outside your instance boundaries.
```

To check boundaries manually:

```bash
mise run check:boundaries
```

---

## 📝 How to Request Changes

### For Interface Changes

1. Create RFC: `docs/rfcs/XXX-description.md`
2. Include:
   - Current interface
   - Proposed changes
   - Backward compatibility plan
   - Migration strategy
3. Post in work logs
4. Wait 24 hours for review
5. Get approval from affected instances
6. Implement with version support if needed

### For Shared Resource Changes

1. Document need in work log
2. Create issue/PR with rationale
3. Tag affected instances
4. Get consensus before proceeding

### For Emergency Fixes

1. Fix the issue
2. Document in work log immediately
3. Create RFC retroactively
4. Get approval within 48 hours

---

## 🔍 Checking Your Boundaries

### Command Line

```bash
# Check what you own
mise run show:boundaries

# Check specific file
python scripts/check_ownership.py src/mia_rag/embeddings/batch.py
# Output: ✅ Instance 2 owns this file

# Check before committing
mise run check:boundaries
```

### In Code

```python
# Scripts will auto-detect your instance
import os
instance_id = os.getenv("INSTANCE_ID", "unknown")

if instance_id == "instance2":
    # You can modify embeddings code
    from mia_rag.embeddings import BatchProcessor
else:
    # You can only read/use, not modify
    from mia_rag.embeddings import BatchProcessor
```

---

## ⚖️ Conflict Resolution

If boundaries are accidentally violated:

1. **Don't Force Push** - This breaks others' work
2. **Communicate** - Post in work logs immediately
3. **Revert Changes** - Undo modifications to others' files
4. **Coordinate** - Work with file owner if changes needed
5. **Document** - Update work logs with resolution

Example:

```bash
# Accidentally modified Instance 3's file
git status
# modified: src/mia_rag/vectordb/client.py (WRONG!)

# Revert the change
git checkout -- src/mia_rag/vectordb/client.py

# Or if you need the change, coordinate:
# 1. Create RFC
# 2. Work with Instance 3 owner
# 3. They implement the change
```

---

## 🎯 Quick Reference

| Instance | Owns | Depends On | Produces For |
|----------|------|------------|--------------|
| 1 | storage, pipeline | None | Instance 2 |
| 2 | embeddings | Instance 1 | Instance 3 |
| 3 | vectordb | Instance 2 | Instance 4 |
| 4 | api | Instance 3 | Instance 5 |
| 5 | mcp | Instance 4 | End Users |
| 6 | monitoring, tests | All | All |

---

**Remember**: Respecting boundaries enables 6 parallel instances to work without conflicts. The system depends on this discipline.

*"Freedom within boundaries creates harmony in parallel development."*
