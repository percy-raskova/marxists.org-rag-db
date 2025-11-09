# Active Projects

This directory tracks major work streams for the Marxist RAG project. Each project has its own tracking document with milestones, dependencies, and status.

**Last Updated**: 2025-11-08

---

## Project Overview

| Project | Status | Priority | Timeline | Owner |
|---------|--------|----------|----------|-------|
| [Corpus Analysis](#corpus-analysis) | 🔄 In Progress (Phase 2) | HIGH | 3-4 weeks | Shared |
| [Code Refactoring](#code-refactoring) | 🔄 In Progress (1/5) | HIGH | 2-3 weeks | Shared |
| [Documentation](#documentation-reorganization) | 🔄 Phase 1 Complete | MEDIUM | 1 week | Shared |

---

## Corpus Analysis

**File**: `corpus-analysis.md`
**Status**: 🔄 In Progress (Phase 2/4)
**Priority**: HIGH

### Quick Summary

Systematic investigation of 121GB Marxists Internet Archive to understand structure and design RAG architecture.

**Progress**:
- ✅ Phase 1: Archive section (4.5GB) fully analyzed
- ✅ Phase 2: Methodology and overview complete
- 🔄 Phase 3: Remaining sections (History 46GB, Subject 9.1GB, Glossary 62MB)
- 📋 Phase 4: Integration specifications

**Key Deliverables**:
- ✅ Investigation methodology specification (~12k tokens)
- ✅ Full corpus overview (121GB breakdown)
- ✅ Archive section analysis (ready for RAG implementation)
- 📋 History, Subject, Glossary section analyses (planned)
- 📋 Unified metadata schema (planned)
- 📋 Processing pipeline spec (planned)

**Blockers**:
- User decision needed: Include History periodicals (43GB)?
- User decision needed: Include Peking Review (8.5GB)?

**Next Steps**:
1. Await scope decisions from user
2. Investigate History section (labor periodicals)
3. Investigate Subject section (thematic collections)
4. Investigate Glossary section (encyclopedia)
5. Create unified metadata schema

---

## Code Refactoring

**File**: `refactoring-code-complexity.md`
**Status**: 🔄 In Progress (1/5 complete)
**Priority**: HIGH

### Quick Summary

Refactor scripts with complexity violations using design patterns to improve maintainability.

**Progress**:
- ✅ 1/5 Scripts Complete: `check_boundaries.py` (Specification pattern)
- ✅ Pytest configuration fixed (INI → TOML)
- 📋 4/5 Scripts Remaining: instance_map, check_conflicts, check_interfaces, instance_recovery

**Key Deliverables**:
- ✅ Specification pattern implementation (0 violations)
- ✅ FilePath value object and domain models
- ✅ 15 passing unit tests
- 📋 Command pattern (instance_map.py - 21 branches)
- 📋 Chain of Responsibility (check_conflicts.py - 17 branches)
- 📋 Visitor pattern (check_interfaces.py - 16 branches)
- 📋 Template Method (instance_recovery.py)

**Blockers**:
None - all blockers resolved

**Next Steps**:
1. Refactor `instance_map.py` (worst offender, 21 branches)
2. Refactor `check_conflicts.py` (17 branches)
3. Refactor `check_interfaces.py` (16 branches)
4. Refactor `instance_recovery.py` (3 functions)
5. Achieve 0 complexity violations across all scripts

---

## Documentation Reorganization

**File**: `documentation-reorganization.md`
**Status**: 🔄 Phase 1 Complete, Phase 2 Planned
**Priority**: MEDIUM

### Quick Summary

Reorganize scattered root documentation to facilitate 6 parallel AI agent workflows.

**Progress**:
- ✅ Phase 1: Instance entry points, architecture consolidation
- 📋 Phase 2: Cleanup (delete deprecated, fix links, reorganize specs)

**Key Deliverables**:
- ✅ 6 instance entry point files (INSTANCE{1-6}-*.md)
- ✅ Consolidated ARCHITECTURE.md (single source of truth)
- ✅ Master DOCUMENTATION-INDEX.md
- ✅ Updated START_HERE.md with routing
- ✅ GitHub issues for remaining work
- 📋 Delete 9 deprecated files
- 📋 Reorganize specs/ naming (align with instances)
- 📋 Fix cross-references and verify links

**Blockers**:
None

**Next Steps**:
1. Delete deprecated root files (9 files)
2. Rename specs/ to align with instance numbers
3. Create link validation script
4. Fix broken cross-references
5. Verify all links working

---

## Project Dependencies

### Dependency Graph

```
Documentation Reorganization
  ↓ (enables parallel work)
Code Refactoring + Corpus Analysis (parallel)
  ↓
RAG Implementation (future)
  ↓
Production Deployment (future)
```

**Key Insights**:
- Documentation and refactoring can proceed in parallel
- Corpus analysis can proceed independently
- RAG implementation blocked until corpus analyses complete
- All projects benefit from clean documentation

---

## Resource Summary

### Token Budget Usage

| Project | Used | Planned | Total | % Complete |
|---------|------|---------|-------|------------|
| Corpus Analysis | ~27k | ~95k | ~122k | 22% |
| Code Refactoring | ~15k | ~68k | ~83k | 18% |
| Documentation | ~33k | ~5k | ~38k | 87% |
| **Total** | **~75k** | **~168k** | **~243k** | **31%** |

### Time Allocation

| Project | Spent | Remaining | Total | % Complete |
|---------|-------|-----------|-------|------------|
| Corpus Analysis | ~12h | ~18h | ~30h | 40% |
| Code Refactoring | ~6h | ~27h | ~33h | 18% |
| Documentation | ~8h | ~3h | ~11h | 73% |
| **Total** | **~26h** | **~48h** | **~74h** | **35%** |

---

## Critical Path Analysis

### Immediate Priorities (This Week)

1. **Corpus Analysis**: Await user scope decisions (History/Subject sections)
2. **Code Refactoring**: Begin instance_map.py refactoring (21 branches)
3. **Documentation**: Execute cleanup tasks (delete deprecated files)

### Medium-Term (2-3 Weeks)

1. **Corpus Analysis**: Complete History, Subject, Glossary investigations
2. **Code Refactoring**: Complete all 5 script refactorings
3. **Documentation**: Verify all links, finalize organization

### Long-Term (1+ Month)

1. **Corpus Analysis**: Integration specifications (unified schema, pipeline)
2. **Code Refactoring**: Maintain 0 violations going forward
3. **Documentation**: Keep updated as project evolves

---

## Cross-Project Synergies

### Documentation → Refactoring
- Clear docs help refactoring agents understand boundaries
- Instance-specific docs prevent cross-contamination

### Documentation → Corpus Analysis
- Separate doc tree (docs/corpus-analysis/) keeps concerns separate
- Clear methodology enables reproducible investigations

### Refactoring → Corpus Analysis
- Clean code makes processing pipeline easier to implement
- Pattern-based design easier to extend for new features

### All Projects → RAG Implementation
- Documentation: Defines architecture
- Corpus Analysis: Defines data structure
- Refactoring: Provides clean codebase
- Together: Enable smooth RAG build

---

## Risk Dashboard

### High Risks

**Corpus Analysis**:
- 🔴 User scope decisions pending (blocks History/Subject investigations)
- 🟡 PDF OCR quality variable (may need quality thresholds)

**Code Refactoring**:
- 🟢 No high risks (all blockers resolved)

**Documentation**:
- 🟢 No high risks (Phase 1 complete)

### Mitigation Strategies

**Scope Decision Risk**:
- Have recommendations ready (exclude History initially)
- Can proceed with Archive section RAG without decisions
- Subject section can be investigated while awaiting History decision

**OCR Quality Risk**:
- HTML-first strategy reduces dependency on PDFs
- Quality thresholds can filter low-confidence OCR
- Archive section (4.5GB) has high HTML coverage

---

## Success Criteria

### Corpus Analysis Project Success

- ✅ Archive section ready for RAG (Complete)
- 📋 All sections investigated with metadata schemas
- 📋 Unified schema spans all content types
- 📋 Processing pipeline specification complete
- 📋 Token-efficient methodology demonstrated

### Code Refactoring Project Success

- ✅ check_boundaries.py: 0 violations (Complete)
- 📋 All 5 scripts: 0 complexity violations
- 📋 All tests passing (100% suite)
- 📋 Coverage >80% for refactored code
- 📋 Patterns documented and reusable

### Documentation Project Success

- ✅ 6 instance entry points created (Complete)
- ✅ Consolidated architecture doc (Complete)
- 📋 0 deprecated files remaining
- 📋 0 broken links
- 📋 100% consistent naming

---

## Communication Cadence

### Weekly Updates

Each project file should be updated weekly with:
- Progress on milestones
- Blockers encountered
- Decisions needed
- Next week's priorities

### Completion Reports

When milestones complete:
- Update status in project file
- Update this README summary
- Document lessons learned
- Archive if project complete

### Escalation

Flag immediately:
- User decisions needed (corpus scope)
- Blocking dependencies discovered
- Timeline risks (slipping >1 week)
- Resource constraints (token budget)

---

## Archive Policy

When a project completes:
1. Mark status as ✅ Complete in this README
2. Add completion date to project file
3. Move to `planning/projects/archive/` subdirectory
4. Keep archived for future reference

**Archived Projects**: None yet

---

## Related Documentation

- **Root Documentation**: `START_HERE.md`, `ARCHITECTURE.md`, `DOCUMENTATION-INDEX.md`
- **Instance Docs**: `docs/instances/instance{1-6}-*/`
- **Specifications**: `specs/INDEX.md`
- **Corpus Analysis**: `docs/corpus-analysis/README.md`
- **Issues**: `planning/issues/`

---

## Quick Links

### For AI Agents

- **Starting a corpus investigation?** → `docs/corpus-analysis/00-investigation-methodology-spec.md`
- **Refactoring a script?** → `planning/projects/refactoring-code-complexity.md`
- **Looking for instance boundaries?** → `INSTANCE{1-6}-*.md` in root
- **Need architecture overview?** → `ARCHITECTURE.md`

### For Humans

- **Project status dashboard** → This file (README.md)
- **Individual project details** → Project-specific .md files
- **Overall project docs** → `START_HERE.md` in root
- **Technical specs** → `specs/INDEX.md`

---

**Maintainer Note**: This README should be updated weekly as projects progress. Each project owner should update their respective project file, and this summary should reflect current state.
