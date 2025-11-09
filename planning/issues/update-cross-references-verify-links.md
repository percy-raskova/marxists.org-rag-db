---
title: "Documentation: Update cross-references and verify all links"
labels: documentation, maintenance, good-first-issue
assignees: ""
---

## Problem Statement

After the documentation reorganization (instance guides, ARCHITECTURE.md consolidation, specs rename), **many cross-references are broken or point to deprecated files**.

**Current Issues:**
- **Broken links**: References to renamed/deleted files (e.g., `CLAUDE_ENTERPRISE.md` → `ARCHITECTURE.md`)
- **Stale paths**: Links to old spec names (e.g., `02-DOCUMENT-PROCESSING-SPEC.md` → `01-STORAGE-PIPELINE.md`)
- **Missing links**: New instance guides not cross-referenced from existing docs
- **Navigation gaps**: No clear routing between related documents

## Scope

Update cross-references across **all documentation** after:
1. ✅ Instance guide creation (`INSTANCE{1-6}-*.md`)
2. ✅ ARCHITECTURE.md consolidation
3. ⏳ Specs reorganization (pending)
4. ⏳ Deprecated file deletion (pending)

## Common Link Patterns to Update

### 1. Architecture References

**Old → New:**
```markdown
# ❌ OLD (broken after consolidation)
[CLAUDE_ENTERPRISE.md](./CLAUDE_ENTERPRISE.md)
[CLOUD-ARCHITECTURE-PLAN.md](./CLOUD-ARCHITECTURE-PLAN.md)
[200GB_SOLUTION_SUMMARY.md](./200GB_SOLUTION_SUMMARY.md)
[PARALLEL-DEV-ARCHITECTURE.md](./PARALLEL-DEV-ARCHITECTURE.md)

# ✅ NEW (consolidated)
[ARCHITECTURE.md](./ARCHITECTURE.md)
[ARCHITECTURE.md#cost-breakdown](./ARCHITECTURE.md#cost-breakdown)
[ARCHITECTURE.md#instance-coordination](./ARCHITECTURE.md#instance-coordination)
```

### 2. Spec References

**Old → New (after specs reorganization):**
```markdown
# ❌ OLD (pending rename)
[02-DOCUMENT-PROCESSING-SPEC.md](./specs/02-DOCUMENT-PROCESSING-SPEC.md)
[03-RAG-INGESTION-SPEC.md](./specs/03-RAG-INGESTION-SPEC.md)
[04-QUERY-INTERFACE-SPEC.md](./specs/04-QUERY-INTERFACE-SPEC.md)

# ✅ NEW (aligned with instances)
[01-STORAGE-PIPELINE.md](./specs/01-STORAGE-PIPELINE.md)
[02-EMBEDDINGS.md](./specs/02-EMBEDDINGS.md)
[03-VECTOR-DB.md](./specs/03-VECTOR-DB.md)
[04-API.md](./specs/04-API.md)
```

### 3. Instance Guide Cross-References

**Add navigation between instance guides:**
```markdown
# Example in INSTANCE2-EMBEDDINGS.md

**Dependencies:**
- [Instance 1 (Storage)](./INSTANCE1-STORAGE.md) - Provides markdown files

**Who depends on you:**
- [Instance 3 (Weaviate)](./INSTANCE3-WEAVIATE.md) - Consumes embeddings
```

## Proposed Solution

### Phase 1: Automated Link Detection

Use `rg` (ripgrep) to find all markdown links:

```bash
# Find all markdown links
rg '\[.*?\]\(.*?\.md.*?\)' --type md -o | sort | uniq > all_links.txt

# Find potentially broken links (files that don't exist)
while IFS= read -r link; do
  file=$(echo "$link" | sed 's/.*(\(.*\))/\1/' | sed 's/#.*//')
  if [ ! -f "$file" ]; then
    echo "BROKEN: $link"
  fi
done < all_links.txt
```

### Phase 2: Manual Verification

**Checklist by file type:**

#### Root-Level Files
- [ ] `README.md` - Update architecture links, add instance guide links
- [ ] `START_HERE.md` - Verify all navigation links work
- [ ] `DOCUMENTATION-INDEX.md` - Update all file paths after reorganization
- [ ] `CONTRIBUTING.md` - Update spec references
- [ ] `PROJECT-STATUS.md` - Update deliverable links
- [ ] `INSTANCE{1-6}-*.md` (6 files) - Cross-reference dependencies

#### Specs Directory
- [ ] `specs/INDEX.md` - Update all spec file references
- [ ] `specs/00-ARCHITECTURE.md` - Update references to other specs
- [ ] `specs/01-STORAGE-PIPELINE.md` - Update after rename
- [ ] `specs/02-EMBEDDINGS.md` - Update after split
- [ ] `specs/03-VECTOR-DB.md` - Update after split
- [ ] `specs/04-API.md` - Update after rename
- [ ] `specs/05-MCP.md` - Update after rename
- [ ] `specs/06-TESTING.md` - Update after rename

#### Docs Directory
- [ ] `docs/instances/instance{1-6}/README.md` (6 files) - Link to root instance guides
- [ ] `docs/processes/*.md` - Update workflow examples
- [ ] `docs/rfc/*.md` - Update references

#### GitHub Templates
- [ ] `.github/ISSUE_TEMPLATE/*.md` - Update documentation links
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` - Update checklist links

### Phase 3: Add Missing Cross-References

**Enhance navigation:**

1. **Instance guides** → Add "See Also" sections:
   ```markdown
   ## See Also

   **Related Instances:**
   - [Instance 1 (Storage)](./INSTANCE1-STORAGE.md) - Upstream dependency
   - [Instance 3 (Weaviate)](./INSTANCE3-WEAVIATE.md) - Downstream consumer

   **Detailed Documentation:**
   - [docs/instances/instance2-embeddings/](./docs/instances/instance2-embeddings/) - Implementation guide
   - [specs/02-EMBEDDINGS.md](./specs/02-EMBEDDINGS.md) - Formal specification
   ```

2. **ARCHITECTURE.md** → Link to instance guides in 6-instance matrix

3. **specs/INDEX.md** → Link to corresponding instance guides

### Phase 4: Link Validation Script

Create automated validation:

```bash
#!/bin/bash
# scripts/validate_links.sh

echo "Validating markdown links..."

errors=0

# Find all markdown files
find . -name "*.md" -type f | while read -r file; do
  # Extract all local markdown links
  grep -oP '\[.*?\]\(\K[^)#]+(?=(\#[^)]*)?\.md\))' "$file" | while read -r link; do
    # Resolve relative path
    dir=$(dirname "$file")
    target=$(realpath -m "$dir/$link" 2>/dev/null)

    if [ ! -f "$target" ]; then
      echo "❌ BROKEN: $file -> $link (resolved to $target)"
      errors=$((errors + 1))
    fi
  done
done

if [ $errors -eq 0 ]; then
  echo "✅ All links valid"
  exit 0
else
  echo "❌ Found $errors broken links"
  exit 1
fi
```

## Acceptance Criteria

- [ ] All markdown links point to existing files
- [ ] No references to deleted files (CLAUDE_ENTERPRISE.md, etc.)
- [ ] Spec references use new naming convention
- [ ] Instance guides cross-reference their dependencies
- [ ] ARCHITECTURE.md links to all 6 instance guides
- [ ] DOCUMENTATION-INDEX.md has correct paths
- [ ] START_HERE.md navigation works end-to-end
- [ ] Link validation script passes (`scripts/validate_links.sh`)
- [ ] Pre-commit hook added to prevent future broken links

## Implementation Checklist

### Step 1: Update Root Files
- [ ] README.md
- [ ] START_HERE.md
- [ ] DOCUMENTATION-INDEX.md
- [ ] CONTRIBUTING.md
- [ ] PROJECT-STATUS.md
- [ ] INSTANCE1-STORAGE.md
- [ ] INSTANCE2-EMBEDDINGS.md
- [ ] INSTANCE3-WEAVIATE.md
- [ ] INSTANCE4-API.md
- [ ] INSTANCE5-MCP.md
- [ ] INSTANCE6-MONITORING.md

### Step 2: Update Specs
- [ ] specs/INDEX.md
- [ ] specs/00-ARCHITECTURE.md
- [ ] specs/01-STORAGE-PIPELINE.md (after rename)
- [ ] specs/02-EMBEDDINGS.md (after split)
- [ ] specs/03-VECTOR-DB.md (after split)
- [ ] specs/04-API.md (after rename)
- [ ] specs/05-MCP.md (after rename)
- [ ] specs/06-TESTING.md (after rename)

### Step 3: Update Docs Directory
- [ ] All files in docs/instances/
- [ ] All files in docs/processes/
- [ ] All files in docs/architecture/

### Step 4: Add Link Validation
- [ ] Create `scripts/validate_links.sh`
- [ ] Add to pre-commit hook
- [ ] Test validation script
- [ ] Run validation and fix any failures

## Files to Create

- `scripts/validate_links.sh` - Automated link validation script
- `.pre-commit-config.yaml` entry - Add link validation hook

## Files to Modify

**All markdown files** (66+ files):
- Root: 19 files
- specs/: 10 files
- docs/: 30+ files
- .github/: 7 files

**Strategy**: Update in phases to avoid overwhelming diff

## Related Issues

- Depends on: #XXXX (Reorganize specs)
- Depends on: #XXXX (Delete deprecated files)
- Part of: Documentation reorganization initiative

## Estimated Effort

**Time**: 3-4 hours
**Breakdown**:
- Automated detection: 30 minutes
- Manual verification: 2 hours
- Link validation script: 1 hour
- Testing: 30 minutes

**Complexity**: Low (tedious but straightforward)
**Priority**: High (broken links frustrate users and AI agents)

## Testing Strategy

1. **Manual spot-checks**: Click 20-30 random links in different files
2. **Automated validation**: Run `scripts/validate_links.sh`
3. **Navigation test**: Follow "typical workflows" in START_HERE.md
4. **AI agent test**: Ask AI to navigate from INSTANCE2-EMBEDDINGS.md to specs/02-EMBEDDINGS.md

## Success Metrics

- 0 broken links in validation script
- 100% of instance guides cross-reference dependencies
- All documentation entry points (README, START_HERE) navigable
- Pre-commit hook prevents future broken links

## References

- Markdown link syntax: `[text](path/to/file.md#optional-anchor)`
- Ripgrep regex for links: `\[.*?\]\(.*?\.md.*?\)`
- GitHub relative link behavior: [GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links)
