# 🤖 AI Agent Instructions for MIA RAG System (200GB Scale)

**CRITICAL: READ THIS ENTIRE DOCUMENT BEFORE STARTING ANY WORK**

You are working on a 200GB RAG system with 6 parallel Claude Code instances. This document contains your rules, boundaries, and workflows.

## 🎯 Project Overview

- **Scale**: 200GB corpus (5-10 million documents)
- **Architecture**: Google Cloud Platform with Weaviate
- **Embeddings**: Runpod.io GPU rental ($40-60 total)
- **Development**: 6 parallel Claude Code web instances
- **Orchestration**: Mise (not Make) for task running

## 🚫 NEVER DO THIS (Violations = Immediate Stop)

### 1. **NEVER modify code outside your assigned instance**

```python
# ❌ WRONG (Instance 2 modifying Instance 3's code)
edit_file("src/mia_rag/vectordb/client.py")

# ✅ CORRECT (Instance 2 modifying its own code)
edit_file("src/mia_rag/embeddings/batch_processor.py")
```

Your boundaries:

- Instance 1: `src/mia_rag/storage/`, `src/mia_rag/pipeline/`
- Instance 2: `src/mia_rag/embeddings/`
- Instance 3: `src/mia_rag/vectordb/`
- Instance 4: `src/mia_rag/api/`
- Instance 5: `src/mia_rag/mcp/`
- Instance 6: `src/mia_rag/monitoring/`, `tests/integration/`

### 2. **NEVER change interface contracts without RFC**

```python
# ❌ WRONG: Changing interface signature
class StorageInterface(ABC):
    def upload(self, path: str, content: str, metadata: dict):  # Added param!
        pass

# ✅ CORRECT: Create RFC first
# docs/rfcs/001-add-metadata-to-storage-interface.md
# Then wait 24 hours for review
```

### 3. **NEVER skip tests or commit with <80% coverage**

```bash
# ❌ WRONG
git commit -m "feat: add batch processor" --no-verify

# ✅ CORRECT
mise run test  # Ensure tests pass
mise run quality  # Ensure linting passes
git commit -m "feat: add batch processor with 85% coverage"
```

### 4. **NEVER hardcode credentials or secrets**

```python
# ❌ WRONG - Hardcoded credentials
credentials = "hardcoded-secret-value"
client = ServiceClient(api_key=credentials)

# ✅ CORRECT - Use environment variables
import os
from dotenv import load_dotenv
load_dotenv(f".env.{os.getenv('INSTANCE_ID', 'instance2')}")
credentials = os.getenv("SERVICE_CREDENTIALS")  # Set in .env file
client = ServiceClient(api_key=credentials)
```

### 5. **NEVER load entire 200GB dataset into memory**

```python
# ❌ WRONG
with open("200gb_corpus.txt") as f:
    data = f.read()  # 💀 OOM crash

# ✅ CORRECT
def stream_documents(path: Path, chunk_size: int = 1024 * 1024):
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            yield process_chunk(chunk)
```

### 6. **NEVER ignore type hints**

```python
# ❌ WRONG
def process_batch(data, size):  # type: ignore
    return data[:size]

# ✅ CORRECT
from typing import List, TypeVar
T = TypeVar('T')

def process_batch(data: List[T], size: int) -> List[T]:
    return data[:size]
```

### 7. **NEVER create vague TODOs**

```python
# ❌ WRONG
# TODO: fix this
# TODO: optimize later
# FIXME

# ✅ CORRECT
# TODO(instance2): Optimize batch size after profiling - see issue #123
# TODO(instance2): Add retry logic for Runpod timeouts - blocked by instance1
# FIXME(instance2): Memory leak in batch processor - investigate by 2025-01-10
```

## ✅ ALWAYS DO THIS (Required Practices)

### 1. **ALWAYS write tests first (TDD)**

```bash
# Workflow for EVERY feature:
# 1. Write failing test
echo "def test_new_feature():
    assert new_feature() == expected" > tests/unit/test_feature.py

# 2. Run test (should fail)
mise run test

# 3. Implement minimum code to pass
echo "def new_feature():
    return expected" > src/mia_rag/module/feature.py

# 4. Run test (should pass)
mise run test

# 5. Refactor if needed
```

### 2. **ALWAYS use dataclasses for data structures**

```python
# ❌ WRONG
def process_document(doc):
    return {
        'id': doc['id'],
        'content': doc['content'],
        'metadata': doc.get('metadata', {})
    }

# ✅ CORRECT
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

def process_document(doc: Document) -> Document:
    return doc
```

### 3. **ALWAYS handle errors with retry logic**

```python
# ✅ CORRECT
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=lambda retry_state: logger.warning(
        "api_retry",
        attempt=retry_state.attempt_number,
        wait_time=retry_state.next_action.sleep
    )
)
def call_runpod_api(endpoint: str, data: dict) -> dict:
    try:
        response = requests.post(endpoint, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("api_call_failed", endpoint=endpoint, error=str(e))
        raise
```

### 4. **ALWAYS log structured data**

```python
# ❌ WRONG
print(f"Processed document {doc_id} in {time}ms")

# ✅ CORRECT
import structlog
logger = structlog.get_logger()

logger.info(
    "document_processed",
    doc_id=doc_id,
    processing_time_ms=elapsed_ms,
    doc_size_bytes=len(content),
    instance_id=os.getenv("INSTANCE_ID"),
    chunk_count=num_chunks
)
```

### 5. **ALWAYS checkpoint long-running operations**

```python
# ✅ CORRECT: Resumable processing
from pathlib import Path
import json

class BatchProcessor:
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_file = checkpoint_dir / "checkpoint.json"

    def load_checkpoint(self) -> dict:
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {"last_processed": -1, "total": 0}

    def save_checkpoint(self, state: dict):
        self.checkpoint_dir.mkdir(exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(state, f)

    def process_batch(self, items: List[Any]):
        checkpoint = self.load_checkpoint()

        for i, item in enumerate(items):
            if i <= checkpoint['last_processed']:
                logger.debug("skipping_processed", index=i)
                continue

            try:
                self.process_item(item)
                checkpoint['last_processed'] = i

                # Save every 100 items
                if i % 100 == 0:
                    self.save_checkpoint(checkpoint)

            except Exception as e:
                logger.error("processing_failed", index=i, error=str(e))
                self.save_checkpoint(checkpoint)
                raise
```

### 6. **ALWAYS update work logs**

```bash
# Start of day
mise run work:start

# After completing a feature
mise run work:log

# End of day
mise run work:end
```

Example work log entry:

```markdown
# Work Log: Instance 2 - Embeddings
## Date: 2025-01-08
## Developer: Claude (Instance 2)

### Completed
- ✅ Implemented batch processor with checkpointing
- ✅ Added Runpod API client with retry logic
- ✅ Created Parquet writer for embeddings
- ✅ Tests: 25/25 passing, 87% coverage

### In Progress
- 🔄 Optimizing batch size for GPU utilization

### Blocked
- ⚠️ Waiting on Instance 1 for storage interface v2

### Tomorrow
- Complete batch size optimization
- Add monitoring metrics
- Start integration tests with Instance 3
```

## 📋 Standard Development Workflow

```bash
# 1. Start your work session
mise run work:start

# 2. Check your instance assignment
mise run identify

# 3. Pull latest changes
git pull origin main

# 4. Create feature branch
git checkout -b instance2-feature-name

# 5. Write tests first (TDD)
# Create test file in tests/unit/instance2_embeddings/

# 6. Run tests (should fail)
mise run test

# 7. Implement feature
# Edit files in src/mia_rag/embeddings/

# 8. Run tests (should pass)
mise run test

# 9. Check code quality
mise run quality  # Runs lint, format, typecheck

# 10. Check coverage
mise run test  # Shows coverage report

# 11. Update work log
mise run work:log

# 12. Commit with conventional commit message
git add .
git commit -m "feat(embeddings): add batch processor with checkpointing

- Implements resumable batch processing
- Adds checkpointing every 100 documents
- Handles Runpod API failures gracefully
- Achieves 100K docs/hour throughput

Closes #42

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 13. Push and create PR
git push origin instance2-feature-name
mise run pr "Add batch processor for embeddings"

# 14. End work session
mise run work:end
```

## 🎯 Confidence Levels & Decision Making

### 95-100% Confidence: Implement Directly

- Proven patterns from documentation
- Clear specifications in your module spec
- Well-established best practices

Example: Using Ray for distributed processing (proven at 200GB scale)

### 80-94% Confidence: Implement with Extra Tests

- Should work based on documentation
- Minor uncertainties about edge cases

Example: Specific Runpod API behavior under load

### 60-79% Confidence: Create Proof-of-Concept First

- Theoretical capability
- Needs validation before full implementation

```python
# Create a POC in scratch/ directory
# scratch/test_new_approach.py
def proof_of_concept():
    # Test the approach with small data
    pass

# If successful, implement properly with tests
```

### <60% Confidence: Ask for Guidance

```python
# Create an RFC or issue
"""
RFC: Uncertain about embedding batch size optimization

Current approach: Fixed batch size of 1000
Concern: GPU memory varies by model
Proposal: Dynamic batch sizing based on memory usage

Confidence: 40% - need human input
"""
```

## 🔍 Pre-Commit Checklist

Before EVERY commit, verify:

```bash
# Automated checks
mise run ci:validate

# Manual verification
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] No type errors
- [ ] No hardcoded secrets
- [ ] Documentation updated
- [ ] Work log updated
- [ ] Interface changes documented
- [ ] No TODO without context
- [ ] Follows module boundaries
- [ ] Uses mocks for external services
```

## 🚨 Common AI Agent Mistakes to Avoid

### 1. Structural Duplication

```python
# ❌ WRONG: Reimplementing existing functionality
class MyBatchProcessor:
    def process_batch(self, items):
        # 100 lines of code

# ✅ CORRECT: Check if it exists first
mise run search "batch.*process"  # Search codebase
# Found: src/common/batch_processor.py
from mia_rag.common.batch_processor import BatchProcessor
```

### 2. Breaking Dependent Code

```python
# ❌ WRONG: Changing signature without checking dependents
def upload(self, path: str, content: str, metadata: dict):  # Added param!

# ✅ CORRECT: Check who uses this
mise run check:dependents upload
# Found 5 callers - update them all in same PR
```

### 3. Over-Engineering

```python
# ❌ WRONG: Unnecessary abstraction
class AbstractFactoryBuilderStrategyPattern:
    # 500 lines of abstraction for simple task

# ✅ CORRECT: YAGNI - Start simple
def process_document(doc: str) -> str:
    return doc.strip().lower()
```

### 4. Ignoring Scale Implications

```python
# ❌ WRONG: O(n²) algorithm for 200GB
for doc1 in all_docs:
    for doc2 in all_docs:
        similarity = compare(doc1, doc2)

# ✅ CORRECT: Use appropriate algorithms
# Use vector similarity with indexed search
results = vector_db.search(query_vector, top_k=10)
```

### 5. Vague Error Messages

```python
# ❌ WRONG
raise ValueError("Invalid input")

# ✅ CORRECT
raise ValueError(
    f"Expected batch_size between 1 and 10000, got {batch_size}. "
    f"Adjust batch_size to fit within GPU memory constraints."
)
```

## 📊 Success Metrics for Your Module

Your module is successful when:

### Code Quality

- ✅ Test coverage > 80%
- ✅ All tests passing
- ✅ No linting errors
- ✅ Type checking passes
- ✅ No security issues

### Performance

- ✅ Meets spec requirements:
  - Instance 1: 10GB/hour processing
  - Instance 2: 100K docs/hour embeddings
  - Instance 3: <100ms query latency
  - Instance 4: 100+ QPS
  - Instance 5: <50ms MCP response
  - Instance 6: <1% metric loss

### Integration

- ✅ Interface contracts honored
- ✅ Integration tests pass
- ✅ No blocking issues for other instances

## 🆘 When to Ask for Human Help

Ask for help when:

1. **Interface change needed** - Create RFC and wait
2. **Performance target not achievable** - Document attempts
3. **Conflict with another instance** - Coordinate in work logs
4. **Confidence level < 60%** - Create issue
5. **Stuck for > 1 hour** - Document blockers
6. **Tests keep failing unexpectedly** - May be environment issue
7. **Need clarification on requirements** - Better to ask than guess

DO NOT:

- Guess and hope it works
- Skip tests because they're hard
- Change interfaces without approval
- Ignore failing tests
- Commit broken code

## 📚 Quick Command Reference

```bash
# Mise Commands (use these, not make!)
mise tasks              # Show all available tasks
mise run install        # Install dependencies
mise run test           # Run tests
mise run lint           # Run linting
mise run format         # Format code
mise run typecheck      # Type checking
mise run quality        # All quality checks
mise run work:start     # Start work session
mise run work:end       # End work session
mise run work:log       # Update work log
mise run sync           # Sync with main branch
mise run pr "title"     # Create pull request

# Git Commands
git status              # Check status
git add .               # Stage changes
git commit -m "..."     # Commit (hooks run automatically)
git push origin branch  # Push branch
gh pr create            # Create PR

# Python/Poetry Commands
poetry install          # Install dependencies
poetry add package      # Add new dependency
poetry run python       # Run Python with venv
poetry shell            # Activate virtual environment

# Testing Commands
pytest tests/unit/      # Run unit tests
pytest -v               # Verbose output
pytest --cov            # With coverage
pytest -k "test_name"   # Run specific test
pytest -m "instance2"   # Run instance-specific tests
```

## 🎓 Final Reminders

1. **Tests are your specification** - If tests pass, you're probably right
2. **Work logs are your communication** - Update daily
3. **Interfaces are your contracts** - Don't break them
4. **Checkpoints are your safety net** - Always make processing resumable
5. **Types are your documentation** - Use them everywhere
6. **Mise is your orchestrator** - Use it for all tasks
7. **80% coverage is your minimum** - Aim for 90%+

---

**Remember**: You're building enterprise-scale infrastructure for 200GB of data. Quality matters. Tests matter. Documentation matters. The revolution needs reliable infrastructure.

*"Code like the revolution depends on it - because it might."* 🚩
