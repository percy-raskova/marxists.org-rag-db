# Documentation Reorganization Project

**Status**: Phase 1 Complete, Corpus Integration Complete, Phase 2 Planned
**Owner**: Shared across instances
**Priority**: MEDIUM
**Timeline**: 1 week remaining (cleanup tasks only)

---

## Project Overview

Reorganize scattered root documentation to facilitate 6 parallel AI agent workflows with clear boundaries, instance-specific entry points, and consolidated architecture documentation.

**Goal**: Transform 18+ scattered root files into organized, navigable documentation structure with instance-specific entry points.

---

## Current Status

- ✅ **Phase 1 Complete**: Instance entry points, architecture consolidation, master index
- ✅ **Corpus Integration Complete**: Corpus analysis integrated into all navigation and instance guides (115+ cross-references)
- 📋 **Phase 2 Planned**: Cleanup (delete deprecated files, fix cross-references, reorganize specs)

---

## Work Streams

### Stream 1: Instance Entry Points ✅ Complete

**Purpose**: Create clear starting points for each of 6 parallel instances

| Instance | File | Purpose | Status |
|----------|------|---------|--------|
| Instance 1 | `INSTANCE1-STORAGE.md` | Storage & Pipeline | ✅ Complete |
| Instance 2 | `INSTANCE2-EMBEDDINGS.md` | Runpod GPU Embeddings | ✅ Complete |
| Instance 3 | `INSTANCE3-VECTOR-DB.md` | Weaviate Vector DB | ✅ Complete |
| Instance 4 | `INSTANCE4-QUERY.md` | Query Interface | ✅ Complete |
| Instance 5 | `INSTANCE5-ORCHESTRATION.md` | Ray/Dask Orchestration | ✅ Complete |
| Instance 6 | `INSTANCE6-MONITORING.md` | Monitoring Stack | ✅ Complete |

**Key Features**:
- Territory maps (owned paths per instance)
- Quick-start commands
- Boundary warnings (what NOT to modify)
- Integration points with other instances
- Troubleshooting guides

### Stream 2: Architecture Consolidation ✅ Complete

**Purpose**: Single source of truth for architecture decisions

| Document | Purpose | Status |
|----------|---------|--------|
| `ARCHITECTURE.md` | Consolidated architecture | ✅ Complete |
| `DOCUMENTATION-INDEX.md` | Master documentation index | ✅ Complete |
| `START_HERE.md` | Updated with instance routing | ✅ Complete |

**Consolidated Files** (content merged into ARCHITECTURE.md):
- CLAUDE_ENTERPRISE.md
- CLOUD-ARCHITECTURE-PLAN.md
- 200GB_SOLUTION_SUMMARY.md
- RAG-IMPLEMENTATION-CHECKLIST.md
- Multiple other root files

### Stream 3: Instance Directories ✅ Complete

**Purpose**: Detailed implementation guides per instance

```
docs/instances/
├── instance1-storage/
│   └── README.md (stub, ready for expansion)
├── instance2-embeddings/
│   └── README.md
├── instance3-vector-db/
│   └── README.md
├── instance4-query/
│   └── README.md
├── instance5-orchestration/
│   └── README.md
└── instance6-monitoring/
    └── README.md
```

**Status**: Structure created, stubs in place, ready for detailed content

### Stream 4: GitHub Issues for Remaining Work ✅ Complete

**Purpose**: Track remaining cleanup tasks

| Issue | Purpose | Priority | Status |
|-------|---------|----------|--------|
| `reorganize-specs-consistent-naming.md` | Align specs/ with instance numbers | MEDIUM | 📋 Created |
| `delete-deprecated-root-documentation.md` | Remove consolidated files | MEDIUM | 📋 Created |
| `update-cross-references-verify-links.md` | Fix broken links | MEDIUM | 📋 Created |

### Stream 5: Corpus Analysis Integration ✅ Complete

**Purpose**: Integrate completed corpus analysis work into documentation navigation structure

**Completed**: 2025-11-08

**What Was Done**:

| Component | Updates | Status |
|-----------|---------|--------|
| Navigation Layer | START_HERE.md, DOCUMENTATION-INDEX.md, ARCHITECTURE.md, CLAUDE.md | ✅ Complete |
| Instance Guides | All 6 INSTANCE*.md with "Essential Corpus Analysis Reading" sections | ✅ Complete |
| Specification Index | specs/INDEX.md with specs 07-08 and dependency graph | ✅ Complete |

**Deliverables**:
- ✅ Added "Corpus Analysis & Data Architecture" navigation section to START_HERE.md
- ✅ Added complete corpus analysis topic to DOCUMENTATION-INDEX.md with navigation patterns
- ✅ Added "Corpus Foundation: Data Architecture" section to ARCHITECTURE.md
- ✅ Added "Corpus Analysis Foundation" section to CLAUDE.md
- ✅ Added corpus-specific reading sections to all 6 instance guides:
  - INSTANCE1 → Metadata schema (5-layer model, 85%+ author coverage)
  - INSTANCE2 → Chunking strategies (4 adaptive strategies)
  - INSTANCE3 → Knowledge graph (entity schema, hybrid retrieval)
  - INSTANCE4 → Query expansion patterns (cross-references)
  - INSTANCE5 → MCP tool design (entity lookup, definitions)
  - INSTANCE6 → Quality metrics (corpus-derived targets)
- ✅ Updated specs/INDEX.md with:
  - Spec 07 (Chunking Strategies)
  - Spec 08 (Knowledge Graph Architecture)
  - Updated dependency graph showing corpus analysis as foundation

**Cross-Reference Verification**:
- ✅ Metadata schema: 19 references (target: 10+)
- ✅ Chunking strategies: 27 references (target: 8+)
- ✅ Knowledge graph: 35 references (target: 6+)
- ✅ Overall corpus analysis: 115 total references

**Navigation Tests**:
- ✅ START_HERE → corpus analysis: 1 click (target: ≤2)
- ✅ Any INSTANCE → relevant spec: 0 clicks (in Essential Reading)

**Impact**: Made 200k+ tokens of systematic corpus investigation discoverable and actionable for parallel AI agents, preserving the "streamlining and tidying" spirit of documentation reorganization.

---

## Milestones

### Milestone 1: Instance Entry Points ✅ COMPLETE
- **Completed**: 2025-11-08
- **Deliverables**: 6 instance-specific entry files created
- **Outcome**: Clear starting point for each parallel instance

**Created Files**:
- ✅ `INSTANCE1-STORAGE.md`
- ✅ `INSTANCE2-EMBEDDINGS.md`
- ✅ `INSTANCE3-VECTOR-DB.md`
- ✅ `INSTANCE4-QUERY.md`
- ✅ `INSTANCE5-ORCHESTRATION.md`
- ✅ `INSTANCE6-MONITORING.md`

### Milestone 2: Architecture Consolidation ✅ COMPLETE
- **Completed**: 2025-11-08
- **Deliverables**: ARCHITECTURE.md, DOCUMENTATION-INDEX.md, updated START_HERE.md
- **Outcome**: Single source of truth for architecture decisions

**Changes**:
- ✅ Created ARCHITECTURE.md (consolidated 9 root files)
- ✅ Created DOCUMENTATION-INDEX.md (master index)
- ✅ Updated START_HERE.md with instance routing
- ✅ Created docs/instances/ structure

### Milestone 2.5: Corpus Analysis Integration ✅ COMPLETE
- **Completed**: 2025-11-08
- **Deliverables**: Corpus analysis integrated into all navigation and instance documentation
- **Outcome**: 46GB systematic corpus investigation made discoverable to all AI agents

**Integration Work**:
- ✅ Updated 4 navigation files (START_HERE, DOCUMENTATION-INDEX, ARCHITECTURE, CLAUDE)
- ✅ Updated all 6 instance guides with Essential Corpus Analysis Reading sections
- ✅ Updated specs/INDEX.md with specs 07-08 and dependency graph
- ✅ Created 115+ cross-references to corpus analysis documentation
- ✅ Verified navigation: START_HERE → corpus analysis in 1 click
- ✅ Verified instance routing: INSTANCE → relevant spec in 0 clicks

**Key Achievement**: Corpus analysis work (metadata schema, chunking strategies, knowledge graph) is now discoverable from every entry point without AI agents needing to rediscover patterns.

### Milestone 3: Cleanup and Verification 📋 PLANNED
- **Target**: Week 1
- **Deliverables**: Delete deprecated files, fix cross-references, reorganize specs
- **Outcome**: Clean, navigable documentation structure

**Planned Tasks**:
1. 📋 Delete 9 deprecated root files (after verifying no unique content lost)
2. 📋 Rename specs/ files to align with instance numbers (01-06)
3. 📋 Update all cross-references (66+ markdown files)
4. 📋 Create link validation script
5. 📋 Run link verification across all docs

---

## Critical Path

```
Instance Entry Points (✅ Complete)
  ↓
Architecture Consolidation (✅ Complete)
  ↓
Corpus Analysis Integration (✅ Complete)
  ↓
GitHub Issues Created (✅ Complete)
  ↓
Cleanup Tasks (📋 Planned)
  ├─ Delete deprecated files
  ├─ Reorganize specs/
  └─ Fix cross-references
  ↓
Documentation Complete
```

---

## Documentation Architecture

### Before Reorganization

**Problems**:
- 18+ files in root with overlapping content
- No clear entry point for AI agents
- Mixed hyphen/underscore naming in specs/
- Broken cross-references
- No instance-specific guidance

### After Reorganization

**Structure**:
```
Project Root
├── START_HERE.md                    # Entry point with instance routing
├── ARCHITECTURE.md                  # Single source of truth
├── DOCUMENTATION-INDEX.md           # Master index
├── INSTANCE{1-6}-*.md              # Instance entry points (6 files)
├── CLAUDE.md                        # AI agent instructions
├── docs/
│   ├── instances/                   # Instance-specific details
│   │   ├── instance1-storage/
│   │   ├── instance2-embeddings/
│   │   ├── instance3-vector-db/
│   │   ├── instance4-query/
│   │   ├── instance5-orchestration/
│   │   └── instance6-monitoring/
│   └── corpus-analysis/             # Corpus investigation (✅ integrated into navigation)
├── specs/                           # Formal specifications
│   ├── INDEX.md (✅ updated with corpus specs 07-08)
│   ├── 07-chunking-strategies-spec.md (✅ corpus-derived)
│   ├── 08-knowledge-graph-spec.md (✅ corpus-derived)
│   └── [to be reorganized to 01-06 pattern]
└── [deprecated files to be deleted]
```

**Benefits**:
- Clear entry point per instance
- Single source of truth (ARCHITECTURE.md)
- Hierarchical organization (root → quick start, docs/ → details)
- Consistent naming conventions
- No broken links

---

## Success Metrics

### Organization Metrics

- ✅ 6 instance entry points created (100%)
- ✅ 1 consolidated architecture document (vs 9 scattered)
- ✅ 1 master index created
- ✅ Corpus analysis integrated (115+ cross-references)
- ✅ 2 new corpus-derived specs added (07, 08)
- 📋 0 deprecated files remaining (target)
- 📋 0 broken links (target)
- 📋 100% consistent naming in specs/

### Navigation Metrics

- ✅ AI agents can find instance entry point in 1 click (START_HERE.md)
- ✅ AI agents can find corpus analysis in 1 click (START_HERE.md)
- ✅ Instance boundaries clearly documented
- ✅ Cross-instance integration points mapped
- ✅ Corpus analysis discoverable from all instances (0 clicks from instance guides)
- 📋 All links verified working

### Maintenance Metrics

- ✅ Single source of truth prevents documentation drift
- ✅ Clear ownership per instance reduces conflicts
- 📋 Link validation script prevents future breakage

---

## Blockers and Risks

### Current Blockers

None - Phase 1 complete

### Medium Risks

1. **Stale References** (external docs may reference old file names)
   - **Mitigation**: Keep deprecated files briefly, add redirects
   - **Impact**: External tools may break temporarily

2. **Incomplete Migration** (content may be lost during consolidation)
   - **Mitigation**: Verify all unique content captured before deletion
   - **Impact**: Information loss if not careful

3. **Link Rot** (broken links after file moves)
   - **Mitigation**: Link validation script + manual verification
   - **Impact**: Navigation broken until fixed

---

## Resource Allocation

### AI Agent Time

- ✅ Instance entry points: ~4 hours (Complete)
- ✅ Architecture consolidation: ~3 hours (Complete)
- ✅ Corpus analysis integration: ~4 hours (Complete)
- ✅ GitHub issues: ~1 hour (Complete)
- 📋 Cleanup and verification: ~3 hours (Planned)

**Total Estimated**: ~15 hours (12 complete, 3 remaining)

### Token Budget

- ✅ Instance entry points: ~18,000 tokens (Used)
- ✅ Architecture consolidation: ~12,000 tokens (Used)
- ✅ Corpus analysis integration: ~30,000 tokens (Used)
- ✅ GitHub issues: ~3,000 tokens (Used)
- 📋 Cleanup and verification: ~5,000 tokens (Planned)

**Total Estimated**: ~68,000 tokens (63k used, 5k remaining)

---

## Dependencies

### External Dependencies

None

### Internal Dependencies

- **Cleanup tasks** depend on Phase 1 complete (✅ Done)
- **Link verification** depends on all files in final locations

### Cross-Project Dependencies

- **Refactoring Project**: Benefits from clear documentation
- **Corpus Analysis**: ✅ Integrated into navigation (docs/corpus-analysis/ + 115+ cross-references)
- **RAG Implementation**: Will reference ARCHITECTURE.md + corpus analysis specs

---

## Cleanup Tasks (Phase 2)

### Task 1: Delete Deprecated Root Files 📋 PLANNED

**Files to Delete** (9 files, content already in ARCHITECTURE.md):
1. CLAUDE_ENTERPRISE.md
2. CLOUD-ARCHITECTURE-PLAN.md
3. 200GB_SOLUTION_SUMMARY.md
4. RAG-IMPLEMENTATION-CHECKLIST.md
5. PROMPT-ENGINEERING-NOTES.md
6. MIA-CORPUS-ANALYSIS.md
7. COORDINATION-MATRIX.md
8. SYSTEM-INTEGRATION-MAP.md
9. PROGRESS-TRACKER.md

**Verification Steps**:
1. Grep each file for unique content not in ARCHITECTURE.md
2. If unique content found, merge into appropriate location
3. Update any external references (git grep for filename)
4. Delete file
5. Commit with clear message

**Estimated Effort**: 2-3 hours

### Task 2: Reorganize specs/ Directory 📋 PLANNED

**Current Naming** (mixed conventions):
- 00-ARCHITECTURE-SPEC.md
- 02-DOCUMENT-PROCESSING-SPEC.md
- 03-RAG-INGESTION-SPEC.md
- 04-QUERY-INTERFACE-SPEC.md
- 05-MCP-INTEGRATION-SPEC.md
- 06-TESTING-VALIDATION-SPEC.md

**Target Naming** (align with instances):
- 00-ARCHITECTURE-SPEC.md (no change)
- 01-STORAGE-PIPELINE-SPEC.md (align with Instance 1)
- 02-EMBEDDINGS-SPEC.md (align with Instance 2)
- 03-VECTOR-DB-SPEC.md (align with Instance 3)
- 04-QUERY-INTERFACE-SPEC.md (align with Instance 4)
- 05-ORCHESTRATION-SPEC.md (align with Instance 5)
- 06-MONITORING-SPEC.md (align with Instance 6)
- 07-MCP-INTEGRATION-SPEC.md (not instance-specific)
- 08-TESTING-VALIDATION-SPEC.md (not instance-specific)

**Steps**:
1. Git mv files to new names
2. Update INDEX.md in specs/
3. Update cross-references in all docs
4. Commit

**Estimated Effort**: 1 hour

### Task 3: Update Cross-References 📋 PLANNED

**Scope**: 66+ markdown files with potential cross-references

**Method**:
1. Create link validation script (Python + markdown parser)
2. Run against all .md files
3. Generate broken link report
4. Fix links manually or with sed/awk
5. Re-run validation to verify

**Estimated Effort**: 2-3 hours

**Script Pseudocode**:
```python
def validate_links(md_file):
    links = extract_markdown_links(md_file)
    for link in links:
        if is_relative(link):
            target = resolve_path(md_file, link)
            if not target.exists():
                report_broken(md_file, link, target)
```

---

## Communication

### Status Updates

- **Phase Complete**: Mark phases complete with deliverables list
- **Blockers**: Flag any stale references or missing content
- **Cleanup Progress**: Update as deprecated files deleted

### Documentation Standards

**Naming Conventions**:
- Root files: SCREAMING_SNAKE_CASE.md
- Instance files: INSTANCE{N}-{PURPOSE}.md
- Docs subdirs: lowercase-with-hyphens/
- Specs: NN-{PURPOSE}-SPEC.md (number-aligned)

**Cross-Reference Format**:
- Relative links preferred: `[text](../other/doc.md)`
- Section anchors: `[text](doc.md#section-name)`
- Always use .md extension (not .html)

---

## Related Projects

- **Corpus Analysis** - ✅ Integrated into navigation (docs/corpus-analysis/ with 115+ cross-references)
- **Refactoring** - Benefits from clear instance boundaries
- **Infrastructure** - References ARCHITECTURE.md + corpus analysis foundation

---

## Notes

- Secret scanner caused multiple false positives on credential patterns in example text
  - Fixed by using generic placeholders instead of realistic examples
  - Decided against exemptions (better to avoid triggers)

- Pytest configuration fixed in separate effort
  - INI → TOML migration enables inline comments
  - Benefits all 6 instances (shared pyproject.toml)

- Instance directories created as stubs
  - Ready for detailed content expansion
  - Each instance can own their detailed docs

---

## GitHub Issues Summary

**Issue 1**: `reorganize-specs-consistent-naming.md`
- **Problem**: Mixed naming in specs/ (02, 03, 04, 05, 06 don't align with instances)
- **Solution**: Rename to align with instance numbers (01-06)
- **Effort**: 2-3 hours
- **Priority**: MEDIUM

**Issue 2**: `delete-deprecated-root-documentation.md`
- **Problem**: 9 deprecated root files clutter navigation
- **Solution**: Delete after verifying content captured in ARCHITECTURE.md
- **Effort**: 2-3 hours
- **Priority**: MEDIUM

**Issue 3**: `update-cross-references-verify-links.md`
- **Problem**: File moves may have broken links
- **Solution**: Create validation script, fix broken links
- **Effort**: 2-3 hours
- **Priority**: MEDIUM

**Total Cleanup Effort**: 6-9 hours
