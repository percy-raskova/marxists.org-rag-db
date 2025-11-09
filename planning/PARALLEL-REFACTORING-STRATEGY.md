# Parallel Refactoring Strategy

**Goal**: Execute 8 refactoring tasks using multiple Claude Code instances in parallel

**Status**: 1/9 complete (check_boundaries.py done)

## Parallelization Analysis

### Dependency Graph

```
Script Refactoring Track (4 remaining):
├── check_conflicts.py ────────────┐
├── check_interfaces.py ───────────┤──── Can run in parallel (independent)
├── instance_map.py ───────────────┤
└── instance_recovery.py ──────────┘

Metadata Pipeline Track (4 tasks):
Unified Schema (CRITICAL PATH)
  ├─→ Multi-Source Extraction ─────┐
  └─→ Glossary Entity Linker ──────┤──── Can run in parallel after schema complete
                                    │
      Section-Specific Extractors ──┘ (blocks on Multi-Source Extraction)
```

### Parallelization Potential

**Wave 1** (4 agents in parallel):
- ✅ check_boundaries.py - COMPLETE
- 🔄 check_conflicts.py
- 🔄 check_interfaces.py
- 🔄 instance_map.py
- ⏸️ instance_recovery.py (save for later - highest complexity)

**Wave 2** (1 agent, critical path):
- 🔄 Unified Metadata Schema (BLOCKS all other metadata work)

**Wave 3** (2 agents in parallel, after schema complete):
- 🔄 Multi-Source Extraction Pipeline
- 🔄 Glossary Entity Linker

**Wave 4** (1 agent):
- 🔄 Section-Specific Extractors (needs Multi-Source Extraction)
- 🔄 instance_recovery.py (deferred from Wave 1)

---

## Parallel Execution Plan

### Wave 1: Script Refactoring (4 Parallel Agents)

**Timeline**: 6-8 hours (concurrent)

**Agent 1**: `check_conflicts.py` (4-6 hours)
- Files modified: `scripts/check_conflicts.py`, `scripts/patterns/validators.py`, `scripts/patterns/ast_utils.py`
- Pattern: Chain of Responsibility
- Estimated: 4-6 hours
- **No conflicts** with other agents

**Agent 2**: `check_interfaces.py` (6-8 hours)
- Files modified: `scripts/check_interfaces.py`, `scripts/domain/interfaces.py`, `scripts/patterns/visitors.py`, `scripts/patterns/repositories.py`
- Pattern: Visitor
- Estimated: 6-8 hours
- **Potential conflict**: `scripts/patterns/repositories.py` (unique to this agent)
- **No conflicts** with other agents

**Agent 3**: `instance_map.py` (5-7 hours)
- Files modified: `scripts/instance_map.py`, `scripts/domain/instance.py`, `scripts/patterns/commands.py`
- Pattern: Command
- Estimated: 5-7 hours
- **Shares**: `scripts/domain/instance.py` with check_boundaries.py (already exists)
- **No conflicts** with other agents

**Agent 4**: Save for Wave 4 (instance_recovery.py is complex, defer)

#### Setup Instructions (Wave 1)

```bash
# Terminal 1 - Agent 1
cd /home/user/projects/marxist-rag
git checkout -b refactor/check-conflicts
# Work on check_conflicts.py

# Terminal 2 - Agent 2
cd /home/user/projects/marxist-rag
git checkout -b refactor/check-interfaces
# Work on check_interfaces.py

# Terminal 3 - Agent 3
cd /home/user/projects/marxist-rag
git checkout -b refactor/instance-map
# Work on instance_map.py
```

#### File Conflict Matrix (Wave 1)

| File | Agent 1 | Agent 2 | Agent 3 |
|------|---------|---------|---------|
| `scripts/check_conflicts.py` | ✅ Write | - | - |
| `scripts/check_interfaces.py` | - | ✅ Write | - |
| `scripts/instance_map.py` | - | - | ✅ Write |
| `scripts/patterns/validators.py` | ✅ Create | - | - |
| `scripts/patterns/ast_utils.py` | ✅ Create | - | - |
| `scripts/patterns/visitors.py` | - | ✅ Create | - |
| `scripts/patterns/repositories.py` | - | ✅ Create | - |
| `scripts/patterns/commands.py` | - | - | ✅ Create |
| `scripts/domain/interfaces.py` | - | ✅ Create | - |
| `scripts/domain/instance.py` | - | - | ✅ Read (exists) |

**Result**: ✅ **NO CONFLICTS** - All agents write to different files!

---

### Wave 2: Unified Metadata Schema (1 Agent, Critical Path)

**Timeline**: 12-16 hours (sequential, blocks Wave 3)

**Agent 1**: `Unified Metadata Schema`
- Files modified: `mia_processor/metadata/schema.py`, `mia_processor/metadata/validators.py`, `mia_processor/metadata/migration.py`, `mia_processor.py`
- Estimated: 12-16 hours
- **Blocks**: Multi-Source Extraction, Glossary Entity Linker, Section-Specific Extractors

#### Setup Instructions (Wave 2)

```bash
# Terminal 1 - Agent 1
cd /home/user/projects/marxist-rag
git checkout -b refactor/metadata-unified-schema
# Work on metadata schema implementation
```

**Why Sequential**: All other metadata work needs the 5-layer schema defined first.

---

### Wave 3: Metadata Pipeline (2 Parallel Agents)

**Timeline**: 16-20 hours (concurrent, after Wave 2 complete)

**Agent 1**: `Multi-Source Extraction Pipeline` (16-20 hours)
- Files modified: `mia_processor/extractors/base.py`, `mia_processor/extractors/author.py`, `mia_processor/extractors/date.py`, `mia_processor/extractors/keywords.py`, `mia_processor/extractors/section_rules.py`, `mia_processor.py`
- Pattern: Strategy
- Estimated: 16-20 hours
- **Depends on**: Unified Schema (Wave 2)
- **No conflicts** with Agent 2

**Agent 2**: `Glossary Entity Linker` (10-14 hours)
- Files modified: `mia_processor/glossary/index_builder.py`, `mia_processor/glossary/entity_linker.py`, `mia_processor/glossary/cross_referencer.py`, `mia_processor.py`
- Pattern: Index + Fuzzy Matching
- Estimated: 10-14 hours
- **Depends on**: Unified Schema (Wave 2)
- **No conflicts** with Agent 1

#### Setup Instructions (Wave 3)

```bash
# Terminal 1 - Agent 1
cd /home/user/projects/marxist-rag
git checkout -b refactor/extraction-pipeline
# Work on multi-source extraction

# Terminal 2 - Agent 2
cd /home/user/projects/marxist-rag
git checkout -b refactor/glossary-linker
# Work on entity linking
```

#### File Conflict Matrix (Wave 3)

| File | Agent 1 (Extraction) | Agent 2 (Glossary) |
|------|----------------------|--------------------|
| `mia_processor.py` | ⚠️ Modify | ⚠️ Modify |
| `mia_processor/extractors/base.py` | ✅ Create | - |
| `mia_processor/extractors/author.py` | ✅ Create | - |
| `mia_processor/extractors/date.py` | ✅ Create | - |
| `mia_processor/extractors/keywords.py` | ✅ Create | - |
| `mia_processor/extractors/section_rules.py` | ✅ Create | - |
| `mia_processor/glossary/index_builder.py` | - | ✅ Create |
| `mia_processor/glossary/entity_linker.py` | - | ✅ Create |
| `mia_processor/glossary/cross_referencer.py` | - | ✅ Create |

**⚠️ CONFLICT**: Both agents modify `mia_processor.py`

**Mitigation**:
1. Agent 1 modifies `extract_metadata_from_html()` function
2. Agent 2 adds entity linking call AFTER extraction
3. Define integration point beforehand:

```python
# Agent 1 adds extraction pipeline
metadata = extraction_pipeline.extract(soup, file_path)

# Agent 2 adds entity linking (separate function)
metadata = enrich_metadata_with_entities(metadata, entity_linker)
```

**Alternative**: Run sequentially (Agent 1 → Agent 2) if coordination is risky.

---

### Wave 4: Final Tasks (2 Agents)

**Timeline**: 8-12 hours (concurrent or sequential)

**Agent 1**: `Section-Specific Extractors` (8-12 hours)
- Files modified: `mia_processor/extractors/section_base.py`, `mia_processor/extractors/archive_extractor.py`, `mia_processor/extractors/etol_extractor.py`, etc.
- Pattern: Template Method
- Estimated: 8-12 hours
- **Depends on**: Multi-Source Extraction (Wave 3 Agent 1)

**Agent 2**: `instance_recovery.py` (8-10 hours)
- Files modified: `scripts/instance_recovery.py`, `scripts/domain/recovery.py`, `scripts/patterns/recovery.py`
- Pattern: Template Method
- Estimated: 8-10 hours
- **No dependencies** (can run anytime)

#### Setup Instructions (Wave 4)

```bash
# Terminal 1 - Agent 1
cd /home/user/projects/marxist-rag
git checkout -b refactor/section-extractors
# Work on section-specific extractors

# Terminal 2 - Agent 2
cd /home/user/projects/marxist-rag
git checkout -b refactor/instance-recovery
# Work on instance recovery refactoring
```

**Result**: ✅ **NO CONFLICTS** - Completely independent work

---

## Summary: Maximum Parallelization

### Option 1: Maximum Parallelism (Aggressive)

**Total Timeline**: ~20-24 hours (wall-clock time, 8 agents total)

- **Wave 1**: 4 agents in parallel (6-8 hours) - Scripts
- **Wave 2**: 1 agent (12-16 hours) - Unified Schema
- **Wave 3**: 2 agents in parallel (16-20 hours) - Extraction + Glossary
- **Wave 4**: 2 agents in parallel (8-12 hours) - Section Extractors + Recovery

**Agent-hours**: ~87 hours (matches project estimate)
**Wall-clock hours**: ~20-24 hours (3 waves)

### Option 2: Conservative Parallelism (Safer)

**Total Timeline**: ~30-36 hours (wall-clock time, fewer conflicts)

- **Wave 1**: 3 agents in parallel (6-8 hours) - Scripts (check_conflicts, check_interfaces, instance_map)
- **Wave 2**: 1 agent (12-16 hours) - Unified Schema
- **Wave 3A**: 1 agent (16-20 hours) - Multi-Source Extraction
- **Wave 3B**: 1 agent (10-14 hours) - Glossary Entity Linker (after Wave 3A)
- **Wave 4**: 2 agents in parallel (8-12 hours) - Section Extractors + Recovery

**Agent-hours**: ~87 hours
**Wall-clock hours**: ~30-36 hours (5 waves, no mia_processor.py conflicts)

---

## Recommended Approach

**Start with Wave 1** (3 parallel agents, safe):

```bash
# Agent 1
git checkout -b refactor/check-conflicts
# Issue: planning/issues/refactor-check-conflicts-chain-of-responsibility.md

# Agent 2
git checkout -b refactor/check-interfaces
# Issue: planning/issues/refactor-check-interfaces-visitor-pattern.md

# Agent 3
git checkout -b refactor/instance-map
# Issue: planning/issues/refactor-instance-map-command-pattern.md
```

**Merge all Wave 1 branches**, then proceed to Wave 2.

---

## Integration Strategy

After each wave:

1. **Merge all branches** from the wave into `main`
2. **Run full test suite**: `poetry run pytest`
3. **Verify pre-commit hooks**: All checks pass
4. **Update project tracking**: Mark milestones complete in `planning/projects/refactoring-code-complexity.md`

---

## Risk Assessment

### Low Risk (Can Parallelize Safely)
- ✅ Wave 1 scripts (no file conflicts)
- ✅ Wave 4 tasks (completely independent)

### Medium Risk (Coordination Needed)
- ⚠️ Wave 3 (both modify `mia_processor.py` - need integration point agreement)

### High Risk (Sequential Only)
- 🔴 Wave 2 (Unified Schema) - MUST complete before Wave 3

---

## Success Criteria

- [ ] All 8 refactoring tasks completed
- [ ] 0 complexity violations remaining
- [ ] All pre-commit hooks pass
- [ ] 100% test coverage maintained
- [ ] All branches successfully merged to main
- [ ] Total wall-clock time: <36 hours (vs. ~87 hours sequential)

---

## Claude Code Instance Assignments

Based on your 6-instance architecture, you could assign:

**Instance 1** (Storage): Handle metadata refactoring (owns `mia_processor.py`)
**Instance 2-5**: Each take 1 script refactoring task
**Instance 6** (Monitoring): Code review and testing coordination

This keeps instance boundaries clean while maximizing parallelism.
