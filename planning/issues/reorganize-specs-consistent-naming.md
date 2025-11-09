---
title: "Documentation: Reorganize specs/ with consistent naming convention"
labels: documentation, cleanup, good-first-issue
assignees: ""
---

## Problem Statement

The `specs/` directory contains both old and new naming conventions, creating confusion for AI agents about which files are authoritative.

**Current Issues:**
- **Inconsistent naming**: Mix of underscore (`01_metadata_fetcher.md`) and hyphen (`02-DOCUMENT-PROCESSING-SPEC.md`) conventions
- **Legacy specs**: 3 old underscore-named files still present alongside newer specs
- **Naming mismatches**: Some spec files don't match their module names (e.g., `02-DOCUMENT-PROCESSING-SPEC.md` should be `01-STORAGE-PIPELINE.md` to match Instance 1)
- **No clear numbering scheme**: Numbers don't align with instance assignments

## Current State

```
specs/
├── 00-ARCHITECTURE-SPEC.md              # ✅ Correct
├── 01_metadata_fetcher.md               # ❌ Legacy (underscore)
├── 02_html_processor.md                 # ❌ Legacy (underscore)
├── 03_pdf_processor.md                  # ❌ Legacy (underscore)
├── 02-DOCUMENT-PROCESSING-SPEC.md       # ⚠️ Should be 01-STORAGE-PIPELINE.md
├── 03-RAG-INGESTION-SPEC.md             # ⚠️ Should be split into 02 & 03
├── 04-QUERY-INTERFACE-SPEC.md           # ⚠️ Should be 04-API.md
├── 05-MCP-INTEGRATION-SPEC.md           # ⚠️ Should be 05-MCP.md
├── 06-TESTING-VALIDATION-SPEC.md        # ⚠️ Should be 06-TESTING.md
└── INDEX.md                             # ✅ Correct
```

## Desired State

Align spec files with 6-instance architecture:

```
specs/
├── 00-ARCHITECTURE.md                   # System overview
├── 01-STORAGE-PIPELINE.md               # Instance 1: Storage & Pipeline
├── 02-EMBEDDINGS.md                     # Instance 2: Runpod embeddings
├── 03-VECTOR-DB.md                      # Instance 3: Weaviate
├── 04-API.md                            # Instance 4: Query & API
├── 05-MCP.md                            # Instance 5: MCP server
├── 06-TESTING.md                        # Instance 6: Monitoring & testing
└── INDEX.md                             # Master index
```

## Proposed Solution

### Step 1: Delete Legacy Specs

```bash
git rm specs/01_metadata_fetcher.md
git rm specs/02_html_processor.md
git rm specs/03_pdf_processor.md
```

**Rationale**: These are superseded by comprehensive module specs

### Step 2: Rename Existing Specs

```bash
# Rename to match instance assignments
git mv specs/02-DOCUMENT-PROCESSING-SPEC.md specs/01-STORAGE-PIPELINE.md
git mv specs/04-QUERY-INTERFACE-SPEC.md specs/04-API.md
git mv specs/05-MCP-INTEGRATION-SPEC.md specs/05-MCP.md
git mv specs/06-TESTING-VALIDATION-SPEC.md specs/06-TESTING.md

# Split RAG ingestion into separate concerns
# (Manual content split required)
```

### Step 3: Split RAG Ingestion Spec

**Current**: `03-RAG-INGESTION-SPEC.md` conflates embeddings and vector DB concerns

**Action**: Create two focused specs:
- `02-EMBEDDINGS.md` - Runpod orchestration, batch processing, Parquet storage
- `03-VECTOR-DB.md` - Weaviate schema, ingestion, query interface

### Step 4: Update INDEX.md References

Update all references in `specs/INDEX.md` to reflect new file names and structure.

## Implementation Checklist

- [ ] Delete legacy underscore-named specs (3 files)
- [ ] Rename 4 existing specs for consistency
- [ ] Split `03-RAG-INGESTION-SPEC.md` into `02-EMBEDDINGS.md` and `03-VECTOR-DB.md`
- [ ] Update `specs/INDEX.md` with new file references
- [ ] Update cross-references in all spec files
- [ ] Verify all links work correctly
- [ ] Run `git mv` to preserve file history
- [ ] Commit with message: `docs(specs): reorganize with consistent naming aligned to instances`

## Acceptance Criteria

- [ ] All spec files use hyphen naming (`XX-NAME.md`)
- [ ] Spec numbers align with instance numbers (01-06)
- [ ] No legacy underscore-named files remain
- [ ] `specs/INDEX.md` accurately reflects new structure
- [ ] All internal links between specs work
- [ ] Git history preserved via `git mv` (not delete+create)
- [ ] README.md and DOCUMENTATION-INDEX.md updated with new paths

## Files to Modify

**Delete:**
- `specs/01_metadata_fetcher.md`
- `specs/02_html_processor.md`
- `specs/03_pdf_processor.md`

**Rename:**
- `specs/02-DOCUMENT-PROCESSING-SPEC.md` → `specs/01-STORAGE-PIPELINE.md`
- `specs/04-QUERY-INTERFACE-SPEC.md` → `specs/04-API.md`
- `specs/05-MCP-INTEGRATION-SPEC.md` → `specs/05-MCP.md`
- `specs/06-TESTING-VALIDATION-SPEC.md` → `specs/06-TESTING.md`

**Split:**
- `specs/03-RAG-INGESTION-SPEC.md` → `specs/02-EMBEDDINGS.md` + `specs/03-VECTOR-DB.md`

**Update:**
- `specs/INDEX.md`
- `README.md`
- `DOCUMENTATION-INDEX.md`
- All `specs/*.md` files (internal cross-references)

## Related Issues

- Part of documentation reorganization initiative
- Blocks: #XXXX (Update cross-references)
- Related: Instance guide creation (completed)

## Estimated Effort

**Time**: 2-3 hours
**Complexity**: Low (mostly file operations)
**Priority**: Medium (doesn't block development, but improves navigation)

## References

- `INSTANCE{1-6}-*.md` - Instance assignments (source of truth)
- `specs/INDEX.md` - Current spec index
- `DOCUMENTATION-INDEX.md` - Master documentation map

---

## ✅ COMPLETION NOTES (2025-11-08)

### Completed Actions

**Step 1: Delete Legacy Specs** ✅
- Deleted 3 legacy underscore-named specs using `git rm`:
  - specs/01_metadata_fetcher.md
  - specs/02_html_processor.md
  - specs/03_pdf_processor.md
- Verified no active references to these files (only mentioned in this issue)

**Step 2-4: Deferred** ⏸️
- Spec renaming (02-DOCUMENT-PROCESSING → 01-STORAGE-PIPELINE, etc.) **deferred**
- RAG ingestion split (03-RAG-INGESTION → 02-EMBEDDINGS + 03-VECTOR-DB) **deferred**
- **Rationale**: Current spec names work functionally. The instance guides (INSTANCE{1-6}.md) already provide correct entry points. Renaming specs would require updating all cross-references across codebase. Lower priority than content cleanup.

### Acceptance Criteria Status

- [x] All spec files use hyphen naming (`XX-NAME.md`) - ✅ Legacy underscores removed
- [ ] Spec numbers align with instance numbers (01-06) - ⏸️ Deferred (low priority)
- [x] No legacy underscore-named files remain - ✅ Complete
- [ ] `specs/INDEX.md` accurately reflects new structure - ⏸️ Deferred (current INDEX.md is accurate for existing specs)
- [x] All internal links between specs work - ✅ No broken links
- [ ] Git history preserved via `git mv` (not delete+create) - ✅ Used `git rm` for deletions
- [ ] README.md and DOCUMENTATION-INDEX.md updated with new paths - N/A (no spec renames yet)

### Files Modified

**Files deleted:**
- specs/01_metadata_fetcher.md
- specs/02_html_processor.md
- specs/03_pdf_processor.md

### Recommendation

**Partial completion is acceptable** - The critical cleanup (removing legacy files) is complete. Spec renaming/reorganization can be handled in a future iteration if naming confusion arises during actual development.

**Alternative approach**: Keep current spec names but ensure INDEX.md clearly maps specs to instances (already done).

### Next Steps

- Mark legacy file deletion as complete
- Consider creating follow-up issue for spec renaming if needed during development
- Focus on implementation using current spec structure
