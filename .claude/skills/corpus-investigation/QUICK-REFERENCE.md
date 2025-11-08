# Corpus Investigation Skill - Quick Reference Card

## Activation

Just say:
- "Investigate the corpus at /path/"
- "Analyze this dataset structure"
- "Study this archive for RAG"

## 5-Phase Process

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: RECONNAISSANCE (10%)                           │
│ → Run: du -sh, find counts, tree structure              │
│ → Output: Section overview with statistics              │
├─────────────────────────────────────────────────────────┤
│ Phase 2: STRATIFIED SAMPLING (40%)                      │
│ → Sample 15-25 files (size/time/type/depth)             │
│ → Extract structure only (not full content)             │
│ → Output: Pattern catalog                               │
├─────────────────────────────────────────────────────────┤
│ Phase 3: PATTERN VERIFICATION (30%)                     │
│ → Run: grep meta tags, CSS classes, links               │
│ → Calculate confidence levels (% coverage)              │
│ → Output: Verified patterns with statistics             │
├─────────────────────────────────────────────────────────┤
│ Phase 4: EDGE CASES (10%)                               │
│ → Sample: largest, smallest, unusual files              │
│ → Output: Exception handling guide                      │
├─────────────────────────────────────────────────────────┤
│ Phase 5: SYNTHESIS (10%)                                │
│ → Compile section analysis document                     │
│ → Output: Complete specification (15 sections)          │
└─────────────────────────────────────────────────────────┘
```

## Essential Commands

### Reconnaissance
```bash
du -sh /path/to/section
find /path -name "*.html" | wc -l
du -sh /path/*/ | sort -h
```

### Verification
```bash
# Meta tags
grep -r '<meta name="author"' /path | wc -l

# CSS classes
grep -roh 'class="[^"]*"' /path | sort | uniq -c | sort -rn

# Links
grep -roh 'href="[^"]*"' /path | head -100
```

### Sampling
```bash
# Random sample
find /path -name "*.html" | shuf | head -15

# Largest files
find /path -name "*.html" | xargs ls -lh | sort -k5 -hr | head -5
```

## 5-Layer Metadata Schema

```
Layer 1: File System     → section, author, year (from paths)
Layer 2: HTML Meta Tags  → title, author, description
Layer 3: Breadcrumb      → navigation trail
Layer 4: Semantic CSS    → curator context, provenance
Layer 5: Content-Derived → word_count, has_footnotes
```

## Output Document (15 Sections)

1. Executive Summary
2. Directory Structure
3. File Type Analysis
4. HTML Patterns
5. **Metadata Schema** ← Code-ready!
6. Linking Architecture
7. Unique Characteristics
8. **Chunking Strategy** ← With rationale!
9. **RAG Integration** ← Implementation steps!
10. Edge Cases
11. Risks + Mitigations
12. Sample Files
13. Verification Commands
14. Recommendations
15. Open Questions

## Token Budget

- **Per Section**: 15,000-30,000 tokens
- **Output**: 5,000-10,000 tokens
- **Reduction**: 95% vs traditional approach

## Confidence Levels

- **100%**: Universal (all files)
- **90-99%**: Standard (rare exceptions)
- **75-89%**: Common (notable exceptions)
- **50-74%**: Frequent
- **<50%**: Occasional

## Stratified Sampling

```
Dimension 1: SIZE
  >1GB    → 10-15 files
  100MB-1GB → 5-10 files
  <100MB  → 3-5 files

Dimension 2: TEMPORAL
  Early period   → 3-5 files
  Mid period     → 3-5 files
  Late period    → 3-5 files

Dimension 3: TYPE
  HTML → 10-15 files
  PDF  → 5-10 files

Dimension 4: DEPTH
  Index    → Always read
  Category → 3-5 files
  Content  → 10-15 files
```

## Token Efficiency Tactics

1. **grep instead of read** → 95% reduction
2. **Sample not exhaust** → 95% reduction
3. **Structure not content** → Extract headings/meta only
4. **Aggregate statistics** → "95% have X" not "file1 has X..."
5. **Reference examples** → Link to files, don't reproduce

## Common Patterns to Extract

**Meta Tags**:
```bash
grep -roh '<meta name="[^"]*"' /path | sed 's/<meta name="\([^"]*\)".*/\1/' | sort | uniq -c
```

**CSS Classes**:
```bash
grep -roh 'class="[^"]*"' /path | sort | uniq -c | sort -rn | head -30
```

**File Years**:
```bash
find /path -name "*.html" | grep -oE '(19|20)[0-9]{2}' | sort | uniq -c
```

**Chapters**:
```bash
find /path -name "*.html" | grep -oE 'ch[0-9]+' | sort | uniq -c
```

## Edge Cases to Check

```bash
# Largest files
find /path -type f | xargs ls -lh | sort -k5 -hr | head -5

# Smallest files
find /path -type f | xargs ls -lh | sort -k5 -h | head -5

# Unusual names
find /path -name "*.html" | grep -v 'index\|chapter\|[0-9]\{4\}'

# Missing meta tags
for f in $(find /path -name "*.html" | head -100); do
  grep -q '<meta name' "$f" || echo "$f"
done
```

## Chunking Strategies

**Paragraph-level**: Dense theory, preserves arguments
**Section-level**: Long-form content, semantic units
**Article-level**: Journalism, independent pieces
**Entry-level**: Reference materials, definitions

**Choose based on**: Content density, semantic coherence, target chunk size

## Quality Checklist

Before completing:
- [ ] All 15 sections of template filled
- [ ] Confidence levels for all patterns
- [ ] Bash commands documented
- [ ] Metadata schema is code-ready
- [ ] Chunking has clear rationale
- [ ] Sample files listed
- [ ] Open questions noted

## Files

```
~/.claude/skills/corpus-investigation/
├── SKILL.md          ← Full methodology
├── reference.md      ← Command templates
├── README.md         ← Installation guide
└── QUICK-REFERENCE.md ← This card
```

## Help

**Not activating?** Use explicit trigger: "investigate corpus at /path/"
**Too many tokens?** Check using grep/find, not reading files
**Vague output?** Review quality checklist, ensure code-ready specs

## Version

**1.0** - Production ready, proven on 121GB corpus
