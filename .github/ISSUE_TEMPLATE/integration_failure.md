---
name: Integration Failure
about: Report an integration test failure between instances
title: '[INTEGRATION] '
labels: integration, test-failure
assignees: ''
---

## Integration Test Failure

### Failed Test
**Test Name**: <!-- e.g., test_storage_to_embeddings_flow -->
**Test File**: <!-- e.g., tests/integration/test_full_pipeline.py -->

### Instances Involved
<!-- Check all instances involved in the failure -->
- [ ] Instance 1 (Storage/Pipeline)
- [ ] Instance 2 (Embeddings)
- [ ] Instance 3 (Weaviate)
- [ ] Instance 4 (API)
- [ ] Instance 5 (MCP)
- [ ] Instance 6 (Monitoring)

### Failure Type
- [ ] Interface contract violation
- [ ] Data format mismatch
- [ ] Performance degradation
- [ ] Timeout
- [ ] Connection failure
- [ ] Other: ___

### Error Details
```python
# Paste the full error traceback here
```

### Test Output
```bash
# Output of: mise run test -- -m integration -k test_name -vv
```

### Recent Changes
<!-- List recent changes that might have caused the failure -->

| Instance | Recent Commits | Suspected Cause |
|----------|---------------|-----------------|
| Instance X | commit_hash | Changed X |
| Instance Y | commit_hash | Modified Y |

### Interface Versions
<!-- Current interface versions involved -->
- Storage Interface: v___
- Embeddings Interface: v___
- VectorDB Interface: v___
- API Interface: v___
- MCP Interface: v___

### Steps to Reproduce
```bash
# Commands to reproduce the failure
mise run test -- -m integration -k test_name
```

### Expected Behavior
<!-- What should happen when the test passes -->

### Actual Behavior
<!-- What actually happened -->

### Data Flow
```
Instance X → [data] → Instance Y
    ↓ (error here)
Instance Z
```

### Proposed Solution
<!-- If you have ideas on how to fix the integration -->

### Temporary Workaround
<!-- Any workarounds while the issue is being fixed -->

### Impact on Development
- [ ] Blocking all integration
- [ ] Blocking specific instances: ___
- [ ] Non-blocking (can work around)

### Coordination Needed
<!-- Which instances need to coordinate to fix this -->
- Instance ___: Action needed
- Instance ___: Action needed

### Related PRs/Issues
<!-- Link to related work -->
- PR #___
- Issue #___

### Daily Integration Run
**Date**: <!-- YYYY-MM-DD -->
**Run ID**: <!-- GitHub Actions run ID -->
**Branch**: integration/daily-YYYYMMDD

---
🤖 Detected by [Integration Testing Suite](https://github.com/percy-raskova/marxists.org-rag-db/actions)