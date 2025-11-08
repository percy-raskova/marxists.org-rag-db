## Instance & Module

**Instance**: <!-- 1-6 -->
**Module**: <!-- storage/pipeline/embeddings/weaviate/api/mcp/monitoring -->
**Branch**: <!-- instance{N}/{module}-{feature} -->

## Summary
<!-- Brief description of changes in 1-3 sentences -->

## Changes
<!-- Bullet list of specific changes made -->
- ✅
- ✅
- ✅

## Interface Changes
<!-- Check all that apply -->
- [ ] No interface changes
- [ ] Interface changes documented in RFC #___
- [ ] Backward compatible changes
- [ ] Breaking change (requires RFC approval and 24-hour review period)

## Dependencies
<!-- List dependencies on other instances -->
- **Requires from**: Instance ___ (_____ API/format)
- **Produces for**: Instance ___ (_____ format/endpoint)
- **Blocked by**: Issue #___ (if any)

## Testing
<!-- Provide testing details -->
- **Unit tests**: _**/**_ passing
- **Coverage**: ___%
- **Integration tests**: <!-- Ready/Pending/N/A -->
- **Performance**: <!-- Within spec/Needs optimization -->

## Performance Metrics
<!-- For storage, embeddings, vectordb, or API modules -->
- **Throughput**: <!-- e.g., 100K docs/hour, 1000 req/s -->
- **Latency**: <!-- e.g., p50: 10ms, p99: 100ms -->
- **Memory usage**: <!-- e.g., peak: 2GB, average: 1.5GB -->
- **CPU usage**: <!-- e.g., 4 cores at 80% -->

## Validation Checklist
<!-- All items must be checked before merge -->
- [ ] Tests written and passing (TDD approach)
- [ ] Coverage >= 80%
- [ ] Boundary check passed (`mise run check:boundaries`)
- [ ] Interface check passed (`mise run check:interfaces`)
- [ ] Documentation updated
- [ ] Work log updated (`mise run work:log`)
- [ ] No hardcoded secrets or credentials
- [ ] Type hints complete
- [ ] Conventional commits format used
- [ ] Pre-commit hooks passing locally

## Documentation Updates
<!-- List any documentation that was updated -->
- [ ] Inline code documentation
- [ ] README updates
- [ ] API documentation
- [ ] Architecture docs
- [ ] User guides

## Migration Notes
<!-- If applicable, describe migration requirements -->

## Rollback Plan
<!-- How to rollback if this causes issues -->

## Related Issues

Closes #___
Related to #___

## Screenshots/Examples
<!-- If applicable, add screenshots or example outputs -->

---

### PR Size Guidance

- **Small**: < 100 lines (preferred)
- **Medium**: 100-500 lines
- **Large**: 500-1000 lines (requires extra review)
- **Extra Large**: > 1000 lines (should be split)

**This PR is**: <!-- Small/Medium/Large/Extra Large -->

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
