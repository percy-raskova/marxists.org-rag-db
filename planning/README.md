# Planning Directory

**Purpose**: Centralized project planning, issues, and development strategy

**Note**: This directory was moved from `.github/` to make it accessible to AI agents and easier to navigate.

---

## Structure

```
planning/
├── issues/           # Individual task issues
├── projects/         # Project tracking documents
├── PARALLEL-REFACTORING-STRATEGY.md
└── WORKFLOW-VALIDATION.md
```

---

## Quick Navigation

### 📋 Active Projects

- **[Refactoring Project](projects/refactoring-code-complexity.md)** - 9 components (1/9 complete)
  - Stream 1: Script complexity reduction (5 scripts)
  - Stream 4: Metadata pipeline refactoring (4 components)

- **[Corpus Analysis](projects/corpus-analysis.md)** - ✅ Complete
  - 46GB analyzed, 6 sections documented
  - Unified metadata schema designed

- **[Documentation Reorganization](projects/documentation-reorganization.md)** - ✅ Complete
  - Root docs consolidated
  - Instance guides created

### 🎯 Development Strategies

- **[Parallel Refactoring Strategy](PARALLEL-REFACTORING-STRATEGY.md)**
  - 4-wave execution plan
  - File conflict analysis
  - Timeline: 20-36 hours (vs 87 sequential)

- **[Workflow Validation](WORKFLOW-VALIDATION.md)**
  - CI/CD testing with `gh act`
  - Production readiness confirmation

### 📝 Issues

See [issues/](issues/) directory for individual task files.

**Refactoring Issues**:
- Scripts: [issues/refactor-*.md](issues/)
- Metadata: [issues/refactor-metadata-*.md](issues/)

**Documentation Issues**:
- [issues/delete-deprecated-root-documentation.md](issues/delete-deprecated-root-documentation.md) - ✅ Complete
- [issues/reorganize-specs-consistent-naming.md](issues/reorganize-specs-consistent-naming.md) - Partial
- [issues/update-cross-references-verify-links.md](issues/update-cross-references-verify-links.md)

---

## For AI Agents

**Start Here**:
1. Read the active project tracking document for your work area
2. Find your specific issue file in `issues/`
3. Follow the implementation steps in the issue

**Wave 1 Parallel Refactoring** (ready to start):
- Agent 1: [issues/refactor-check-conflicts-chain-of-responsibility.md](issues/refactor-check-conflicts-chain-of-responsibility.md)
- Agent 2: [issues/refactor-check-interfaces-visitor-pattern.md](issues/refactor-check-interfaces-visitor-pattern.md)
- Agent 3: [issues/refactor-instance-map-command-pattern.md](issues/refactor-instance-map-command-pattern.md)

---

## Related Documentation

- [DOCUMENTATION-INDEX.md](../DOCUMENTATION-INDEX.md) - Master documentation map
- [specs/](../specs/) - Formal specifications
- [docs/](../docs/) - Detailed documentation
