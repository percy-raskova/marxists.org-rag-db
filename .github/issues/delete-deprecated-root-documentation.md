---
title: "Documentation: Delete deprecated root-level documentation files"
labels: documentation, cleanup, technical-debt
assignees: ""
---

## Problem Statement

Multiple root-level documentation files have been **consolidated into ARCHITECTURE.md**, but the original files remain, causing confusion about which document is the source of truth.

**Current Issues:**
- **Duplicate information**: Same architecture details in 3-4 places
- **Conflicting versions**: Updates may not propagate to all copies
- **Navigation overhead**: AI agents waste time reading redundant content
- **Maintenance burden**: Changes require updating multiple files

## Files to Delete

### 1. Architecture Consolidation Targets

These files were **fully consolidated into ARCHITECTURE.md**:

```bash
# ❌ DELETE (superseded by ARCHITECTURE.md)
CLAUDE_ENTERPRISE.md              # 200GB architecture overview
CLOUD-ARCHITECTURE-PLAN.md        # GCP infrastructure details
200GB_SOLUTION_SUMMARY.md         # Executive summary
PARALLEL-DEV-ARCHITECTURE.md      # 6-instance coordination
PARALLEL-DEV-QUICKSTART.md        # Quick start (now in instance guides)
```

**Consolidation commit**: `38fb145` - "docs: update root documentation for 200GB enterprise architecture"

### 2. Other Deprecated Files

```bash
# ❌ DELETE (superseded by instance guides)
STORAGE-STRATEGY.md               # Now in INSTANCE1-STORAGE.md + docs/instances/instance1-storage/
RUNPOD_EMBEDDINGS.md              # Now in INSTANCE2-EMBEDDINGS.md + RUNPOD.md

# ❌ DELETE (superseded by formal testing strategy)
PARALLEL-TEST-STRATEGY.md         # Now in specs/06-TESTING.md

# ❌ DELETE (superseded by comprehensive TERRAFORM.md)
TERRAFORM-INFRASTRUCTURE.md       # Now fully covered in TERRAFORM.md
```

## Current Documentation Structure

**Root Level** (after cleanup):
```
README.md                         # User-facing project overview
START_HERE.md                     # Navigation hub
ARCHITECTURE.md                   # ⭐ Comprehensive architecture (NEW)
DOCUMENTATION-INDEX.md            # Master index (NEW)
CONTRIBUTING.md                   # Contribution guidelines
PROJECT-STATUS.md                 # Current status
AI-AGENT-INSTRUCTIONS.md          # Agent rules
BOUNDARIES.md                     # Instance boundaries

INSTANCE1-STORAGE.md              # ⭐ Instance quick-starts (NEW)
INSTANCE2-EMBEDDINGS.md
INSTANCE3-WEAVIATE.md
INSTANCE4-API.md
INSTANCE5-MCP.md
INSTANCE6-MONITORING.md

TERRAFORM.md                      # Infrastructure as code
RUNPOD.md                         # GPU rental strategy
```

**Detailed Docs**:
```
docs/instances/instance{1-6}/     # Detailed implementation guides
docs/architecture/                # Architecture deep-dives
docs/processes/                   # Development workflows
```

## Proposed Solution

### Phase 1: Verify No Unique Content

Before deletion, audit each file to ensure no unique information is lost:

```bash
# For each file, check if content exists in new locations
# - CLAUDE_ENTERPRISE.md → ARCHITECTURE.md
# - CLOUD-ARCHITECTURE-PLAN.md → ARCHITECTURE.md + TERRAFORM.md
# - 200GB_SOLUTION_SUMMARY.md → ARCHITECTURE.md
# - PARALLEL-DEV-ARCHITECTURE.md → ARCHITECTURE.md + BOUNDARIES.md
# - PARALLEL-DEV-QUICKSTART.md → INSTANCE{1-6}.md + START_HERE.md
# - STORAGE-STRATEGY.md → INSTANCE1-STORAGE.md + docs/instances/instance1-storage/
# - RUNPOD_EMBEDDINGS.md → RUNPOD.md + INSTANCE2-EMBEDDINGS.md
# - PARALLEL-TEST-STRATEGY.md → specs/06-TESTING.md
# - TERRAFORM-INFRASTRUCTURE.md → TERRAFORM.md
```

### Phase 2: Delete Deprecated Files

```bash
# Architecture consolidation targets
git rm CLAUDE_ENTERPRISE.md
git rm CLOUD-ARCHITECTURE-PLAN.md
git rm 200GB_SOLUTION_SUMMARY.md
git rm PARALLEL-DEV-ARCHITECTURE.md
git rm PARALLEL-DEV-QUICKSTART.md

# Instance-specific content moved
git rm STORAGE-STRATEGY.md
git rm RUNPOD_EMBEDDINGS.md
git rm PARALLEL-TEST-STRATEGY.md

# Terraform consolidation
git rm TERRAFORM-INFRASTRUCTURE.md

# Commit
git commit -m "docs: remove deprecated files consolidated into ARCHITECTURE.md and instance guides"
```

### Phase 3: Update References

Grep for references to deleted files and update them:

```bash
# Find all references
rg "CLAUDE_ENTERPRISE\.md" --type md
rg "CLOUD-ARCHITECTURE-PLAN\.md" --type md
rg "PARALLEL-DEV-ARCHITECTURE\.md" --type md
# ... etc

# Update to point to new locations
# CLAUDE_ENTERPRISE.md → ARCHITECTURE.md
# STORAGE-STRATEGY.md → INSTANCE1-STORAGE.md or docs/instances/instance1-storage/
```

## Acceptance Criteria

- [ ] All 9 deprecated files deleted from repository
- [ ] No unique content lost (verified by manual audit)
- [ ] All references to deleted files updated with new paths
- [ ] `DOCUMENTATION-INDEX.md` updated to reflect deletions
- [ ] `START_HERE.md` navigation still works correctly
- [ ] `README.md` links still valid
- [ ] Git history shows `git rm` for clean removal
- [ ] Commit message explains consolidation rationale

## Pre-Deletion Verification Checklist

For each file, verify content is preserved:

- [ ] **CLAUDE_ENTERPRISE.md**
  - [ ] 200GB scale architecture → ARCHITECTURE.md
  - [ ] Ray/Dask discussion → ARCHITECTURE.md (if applicable)
  - [ ] Cost breakdown → ARCHITECTURE.md

- [ ] **CLOUD-ARCHITECTURE-PLAN.md**
  - [ ] GCP services → ARCHITECTURE.md + TERRAFORM.md
  - [ ] Infrastructure diagrams → ARCHITECTURE.md

- [ ] **200GB_SOLUTION_SUMMARY.md**
  - [ ] Executive summary → ARCHITECTURE.md
  - [ ] Key decisions → ARCHITECTURE.md

- [ ] **PARALLEL-DEV-ARCHITECTURE.md**
  - [ ] Instance coordination → ARCHITECTURE.md + BOUNDARIES.md
  - [ ] Development workflow → INSTANCE{1-6}.md

- [ ] **PARALLEL-DEV-QUICKSTART.md**
  - [ ] Quick start steps → START_HERE.md
  - [ ] Instance routing → INSTANCE{1-6}.md

- [ ] **STORAGE-STRATEGY.md**
  - [ ] GCS lifecycle policies → INSTANCE1-STORAGE.md
  - [ ] Parquet schema → docs/instances/instance1-storage/

- [ ] **RUNPOD_EMBEDDINGS.md**
  - [ ] GPU rental strategy → RUNPOD.md
  - [ ] Batch processing → INSTANCE2-EMBEDDINGS.md

- [ ] **PARALLEL-TEST-STRATEGY.md**
  - [ ] Testing without cloud → specs/06-TESTING.md
  - [ ] Mocking strategies → specs/06-TESTING.md

- [ ] **TERRAFORM-INFRASTRUCTURE.md**
  - [ ] IaC implementation → TERRAFORM.md
  - [ ] GCP resources → TERRAFORM.md

## Files to Modify

**Delete:**
- `CLAUDE_ENTERPRISE.md`
- `CLOUD-ARCHITECTURE-PLAN.md`
- `200GB_SOLUTION_SUMMARY.md`
- `PARALLEL-DEV-ARCHITECTURE.md`
- `PARALLEL-DEV-QUICKSTART.md`
- `STORAGE-STRATEGY.md`
- `RUNPOD_EMBEDDINGS.md`
- `PARALLEL-TEST-STRATEGY.md`
- `TERRAFORM-INFRASTRUCTURE.md`

**Update (if they reference deleted files):**
- `README.md`
- `START_HERE.md`
- `DOCUMENTATION-INDEX.md`
- `specs/INDEX.md`
- All `INSTANCE{1-6}.md` files
- All files in `docs/`

## Related Issues

- Part of documentation reorganization initiative
- Follows: Instance guide creation (completed)
- Follows: ARCHITECTURE.md consolidation (completed)
- Blocks: #XXXX (Update cross-references)

## Estimated Effort

**Time**: 1-2 hours (mostly verification)
**Complexity**: Low (deletion is easy, verification is critical)
**Priority**: Medium (reduces confusion, doesn't block development)

## Safety Notes

⚠️ **Before deletion**, ensure:
1. Content audit complete (no unique information lost)
2. New consolidated docs are committed
3. References updated in remaining files
4. Backup available if rollback needed

## References

- Consolidation commit: `38fb145`
- New consolidated file: `ARCHITECTURE.md`
- New instance guides: `INSTANCE{1-6}-*.md`
- Documentation index: `DOCUMENTATION-INDEX.md`
