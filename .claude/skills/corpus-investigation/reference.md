# Corpus Investigation Reference Guide

**Companion to**: corpus-investigation SKILL.md
**Purpose**: Quick reference, command templates, and advanced techniques

---

## Quick Start Checklist

### Before Starting Investigation

- [ ] Confirm corpus path is accessible
- [ ] Estimate total size (run `du -sh /path/to/corpus`)
- [ ] Identify corpus type (HTML, PDF, mixed, other)
- [ ] Ask user about scope constraints (if any)
- [ ] Confirm output format expectations

### During Investigation

- [ ] Phase 1: Run reconnaissance commands (10 min)
- [ ] Phase 2: Select and sample 15-25 files (20 min)
- [ ] Phase 3: Verify patterns with grep/find (15 min)
- [ ] Phase 4: Sample 5-10 edge cases (10 min)
- [ ] Phase 5: Write section analysis document (20 min)

### After Investigation

- [ ] Verify all sections of template completed
- [ ] Check confidence levels specified for patterns
- [ ] Ensure bash commands are documented
- [ ] Confirm metadata schema is code-ready
- [ ] List all open questions for user

---

## Command Templates Library

### Reconnaissance Phase

```bash
# Template: Basic section reconnaissance
SECTION_PATH="/path/to/section"

# Total size
du -sh "$SECTION_PATH"

# File counts by type
echo "HTML files: $(find "$SECTION_PATH" -type f -name "*.htm*" | wc -l)"
echo "PDF files: $(find "$SECTION_PATH" -type f -name "*.pdf" | wc -l)"
echo "Other files: $(find "$SECTION_PATH" -type f ! -name "*.htm*" ! -name "*.pdf" | wc -l)"

# Directory structure (3 levels)
find "$SECTION_PATH" -type d -maxdepth 3 | head -50

# Size distribution
du -h "$SECTION_PATH" --max-depth=2 | sort -h | tail -20

# Subdirectory sizes
du -sh "$SECTION_PATH"/*/ 2>/dev/null | sort -h
```

### Stratified Sampling Phase

```bash
# Template: Stratified file selection
SECTION_PATH="/path/to/section"

# 1. Get index pages (always read first)
find "$SECTION_PATH" -name "index.htm*" | head -10

# 2. Sample large subsections (identify first)
du -sh "$SECTION_PATH"/*/ | sort -h | tail -5

# 3. Random sample from specific directory
find "$SECTION_PATH/large-subdir" -name "*.htm*" | shuf | head -10

# 4. Sample by time period (if applicable)
find "$SECTION_PATH" -name "*1920*" | head -5
find "$SECTION_PATH" -name "*1950*" | head -5
find "$SECTION_PATH" -name "*1980*" | head -5

# 5. Sample by file depth
# Index pages (depth 0)
find "$SECTION_PATH" -maxdepth 1 -name "index.htm*"
# Category pages (depth 1-2)
find "$SECTION_PATH" -mindepth 1 -maxdepth 2 -name "index.htm*" | shuf | head -5
# Content pages (depth 3+)
find "$SECTION_PATH" -mindepth 3 -name "*.htm*" | shuf | head -10
```

### Pattern Verification Phase

```bash
# Template: Pattern verification commands
SECTION_PATH="/path/to/section"

# Meta tag analysis
echo "=== META TAG ANALYSIS ==="

# Count files with author meta tag
total_html=$(find "$SECTION_PATH" -name "*.htm*" | wc -l)
with_author=$(grep -rl '<meta name="author"' "$SECTION_PATH" | wc -l)
echo "Author meta tag: $with_author / $total_html = $(( 100 * with_author / total_html ))%"

# List all meta tag names
echo -e "\nAll meta tag names:"
grep -roh '<meta name="[^"]*"' "$SECTION_PATH" | \
  sed 's/<meta name="\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -rn

# List all meta properties (OpenGraph, etc.)
echo -e "\nAll meta properties:"
grep -roh '<meta property="[^"]*"' "$SECTION_PATH" | \
  sed 's/<meta property="\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -rn

# CSS class analysis
echo -e "\n=== CSS CLASS ANALYSIS ==="
grep -roh 'class="[^"]*"' "$SECTION_PATH" | \
  sed 's/class="\([^"]*\)".*/\1/' | \
  tr ' ' '\n' | \
  sort | uniq -c | sort -rn | head -30

# Link pattern analysis
echo -e "\n=== LINK PATTERN ANALYSIS ==="

# Internal links
echo "Internal links (top 20):"
grep -roh 'href="[^"]*"' "$SECTION_PATH" | \
  grep -v 'http' | \
  sort | uniq -c | sort -rn | head -20

# Anchor links (footnotes, citations)
echo -e "\nAnchor links (footnotes):"
grep -roh 'href="#[^"]*"' "$SECTION_PATH" | \
  sort | uniq -c | sort -rn | head -20

# External links
echo -e "\nExternal links (domains):"
grep -roh 'href="http[^"]*"' "$SECTION_PATH" | \
  sed 's|https\?://\([^/]*\).*|\1|' | \
  sort | uniq -c | sort -rn | head -10

# File naming patterns
echo -e "\n=== FILE NAMING PATTERNS ==="

# Year patterns
echo "Year patterns in filenames:"
find "$SECTION_PATH" -name "*.htm*" -o -name "*.pdf" | \
  grep -oE '(19|20)[0-9]{2}' | \
  sort | uniq -c | sort -rn

# Chapter patterns
echo -e "\nChapter patterns:"
find "$SECTION_PATH" -name "*.htm*" | \
  grep -oE 'ch[0-9]+|chapter[0-9]+' | \
  sort | uniq -c | sort -rn

# Common filename patterns
echo -e "\nTop 20 filenames:"
find "$SECTION_PATH" -name "*.htm*" | \
  sed 's/.*\///' | \
  sort | uniq -c | sort -rn | head -20

# DOCTYPE analysis
echo -e "\n=== DOCTYPE ANALYSIS ==="
grep -roh '<!DOCTYPE[^>]*>' "$SECTION_PATH" | \
  sort | uniq -c | sort -rn

# Encoding analysis
echo -e "\n=== CHARACTER ENCODING ==="
grep -roh 'charset=[^">]*' "$SECTION_PATH" | \
  sort | uniq -c | sort -rn
```

### Edge Case Detection

```bash
# Template: Edge case identification
SECTION_PATH="/path/to/section"

# 1. Largest files
echo "=== LARGEST FILES ==="
find "$SECTION_PATH" -type f \( -name "*.htm*" -o -name "*.pdf" \) | \
  xargs ls -lh 2>/dev/null | \
  sort -k5 -hr | head -10

# 2. Smallest files
echo -e "\n=== SMALLEST FILES ==="
find "$SECTION_PATH" -type f \( -name "*.htm*" -o -name "*.pdf" \) | \
  xargs ls -lh 2>/dev/null | \
  sort -k5 -h | head -10

# 3. Files with unusual names (no year, chapter, or index)
echo -e "\n=== UNUSUAL FILENAMES ==="
find "$SECTION_PATH" -name "*.htm*" | \
  grep -v 'index\|chapter\|ch[0-9]\|[0-9]\{4\}' | \
  head -20

# 4. Deepest nested files
echo -e "\n=== DEEPEST NESTED FILES ==="
find "$SECTION_PATH" -name "*.htm*" | \
  awk '{n=gsub(/\//,"/"); print n, $0}' | \
  sort -rn | head -10

# 5. Files without meta tags
echo -e "\n=== FILES WITHOUT META TAGS ==="
for file in $(find "$SECTION_PATH" -name "*.htm*" | head -100); do
  grep -q '<meta name' "$file" || echo "$file"
done | head -10

# 6. Files without links
echo -e "\n=== FILES WITHOUT LINKS ==="
for file in $(find "$SECTION_PATH" -name "*.htm*" | head -100); do
  grep -q '<a href' "$file" || echo "$file"
done | head -10

# 7. Empty or very small files (<1KB)
echo -e "\n=== EMPTY OR TINY FILES ==="
find "$SECTION_PATH" -name "*.htm*" -size -1k | head -10
```

---

## HTML Structure Extraction Template

When reading a sampled HTML file, extract only this structure:

```python
# Pseudo-code for structure extraction
def extract_html_structure(file_path):
    """Extract structure without reading full content."""

    structure = {
        # DOCTYPE and encoding
        "doctype": extract_doctype(),
        "charset": extract_charset(),

        # Meta tags
        "meta_tags": {
            tag.name: tag.content
            for tag in find_all('meta')
        },

        # Title
        "title": find('title').text,

        # Headings (structure only)
        "headings": [
            {"level": h.name, "text": h.text}
            for h in find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        ],

        # CSS classes (unique list)
        "css_classes": list(set([
            cls
            for elem in find_all(class_=True)
            for cls in elem['class']
        ])),

        # First paragraph only
        "first_paragraph": find('p').text if find('p') else None,

        # Link counts (don't extract all links)
        "link_count": len(find_all('a')),
        "internal_links": len([a for a in find_all('a') if not a.get('href', '').startswith('http')]),
        "external_links": len([a for a in find_all('a') if a.get('href', '').startswith('http')]),
        "anchor_links": len([a for a in find_all('a') if a.get('href', '').startswith('#')]),

        # Other elements (counts only)
        "image_count": len(find_all('img')),
        "table_count": len(find_all('table')),
        "list_count": len(find_all(['ul', 'ol'])),

        # Word count estimate (from body text)
        "word_count": len(find('body').text.split()) if find('body') else 0,
    }

    return structure
```

---

## Metadata Schema Template

Define metadata schema using this 5-layer template:

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DocumentMetadata:
    """Unified metadata schema for corpus section."""

    # === LAYER 1: File System Metadata ===
    section: str                    # Top-level section name
    subsection: Optional[str]       # Secondary categorization
    file_path: str                  # Relative path from corpus root
    file_extension: str             # .htm, .html, .pdf
    file_size_bytes: int            # File size

    # Path-derived fields (customize per corpus structure)
    author: Optional[str]           # Extracted from /archive/{author}/
    year: Optional[int]             # Extracted from path or filename
    work_slug: Optional[str]        # Work identifier from path
    chapter_number: Optional[int]   # Extracted from ch##.htm

    # === LAYER 2: HTML Meta Tags ===
    title: Optional[str]            # <title> or <meta name="title">
    meta_author: Optional[str]      # <meta name="author">
    description: Optional[str]      # <meta name="description">
    classification: Optional[str]   # <meta name="classification">
    keywords: Optional[List[str]]   # <meta name="keywords">

    # === LAYER 3: Breadcrumb Navigation ===
    breadcrumb: List[str]           # Navigation trail
    category_path: Optional[str]    # Categorical location

    # === LAYER 4: Semantic CSS Classes ===
    curator_context: Optional[str]  # class="context" content
    provenance: Optional[str]       # class="information" content
    annotations: List[str]          # Other semantic annotations

    # === LAYER 5: Content-Derived ===
    word_count: int                 # Document length
    has_footnotes: bool             # Presence of anchor links
    has_images: bool                # Presence of images
    has_tables: bool                # Presence of tables
    reading_time_minutes: int       # word_count / 250
    language: str                   # Detected language (default "en")

    # === Cross-referencing ===
    internal_links: List[str]       # Links within corpus
    external_links: List[str]       # Links outside corpus
    anchor_ids: List[str]           # Named anchors in document
```

---

## Section Analysis Document Template

Complete template for synthesis phase:

```markdown
# {Section Name} Analysis

**Section Path**: /absolute/path/to/section/
**Total Size**: {X}GB ({Y} MB)
**File Count**: {N} HTML files, {M} PDFs
**Investigation Date**: YYYY-MM-DD
**Investigator**: Claude Code (corpus-investigation skill)

---

## 1. Executive Summary

[2-3 paragraphs covering:]
- Section purpose and scope
- Size and composition
- Key organizational patterns
- Main findings and recommendations

## 2. Directory Structure

### 2.1 Hierarchy Diagram

```
/section/
  ├── subsection1/ ({size})
  │   ├── category-a/
  │   │   ├── index.htm
  │   │   └── content/
  │   └── category-b/
  ├── subsection2/ ({size})
  └── index.htm
```

### 2.2 Size Distribution

| Subsection | Size | HTML | PDF | % Total | Priority |
|------------|------|------|-----|---------|----------|
| subsection1 | 2.1GB | 1,234 | 567 | 45% | HIGH |
| subsection2 | 1.8GB | 890 | 234 | 38% | HIGH |
| subsection3 | 0.8GB | 456 | 89 | 17% | MEDIUM |
| **Total** | **4.7GB** | **2,580** | **890** | **100%** | - |

## 3. File Type Analysis

### 3.1 HTML Files

- **Count**: {N}
- **Naming Conventions**:
  - Pattern 1: `ch##.htm` (chapters) - 45% of files
  - Pattern 2: `index.htm` (navigation) - 5% of files
  - Pattern 3: `{work}-{year}.htm` (dated works) - 30% of files
  - Pattern 4: Other - 20% of files
- **Size Range**: {min}KB - {max}MB
- **Average Size**: {avg}KB
- **Median Size**: {median}KB

### 3.2 PDF Files

- **Count**: {M}
- **OCR Quality**: [Assessed from 10-15 samples]
  - High quality (clean text): 60%
  - Medium quality (some errors): 30%
  - Poor quality (many errors): 10%
- **Naming Conventions**: [describe patterns]
- **Purpose**: [scanned books/periodicals/supplements]
- **Size Range**: {min}MB - {max}MB
- **Average Size**: {avg}MB

## 4. HTML Structure Patterns

### 4.1 DOCTYPE and Encoding

**DOCTYPE Distribution**:
- HTML 4.0 Transitional: 85% (confidence: verified via grep)
- HTML 5: 10%
- XHTML 1.0: 5%

**Character Encoding**:
- ISO-8859-1: 70%
- UTF-8: 25%
- Other: 5%

### 4.2 Meta Tag Schema

| Meta Tag | Occurrence % | Example Value | Notes |
|----------|--------------|---------------|-------|
| author | 95% | "Karl Marx" | Universal pattern |
| description | 88% | "Chapter 1: Commodities" | Common pattern |
| classification | 65% | "Economics" | Frequent pattern |
| keywords | 45% | "surplus value, labor" | Occasional |
| viewport | 10% | "width=device-width" | Recent additions |

**Verification Command**:
```bash
grep -r '<meta name="author"' /path | wc -l
# Result: 2,453 / 2,580 = 95%
```

### 4.3 Semantic CSS Classes

| CSS Class | Occurrences | Semantic Meaning | Example Usage |
|-----------|-------------|------------------|---------------|
| quoteb | 8,234 | Block quotes | Extended quotations |
| title | 2,580 | Work titles | Document titles |
| context | 892 | Curator context | Historical annotations |
| information | 756 | Provenance | Source information |
| fst | 2,450 | First paragraph | Often has anchor |

**Verification Command**:
```bash
grep -roh 'class="[^"]*"' /path | sort | uniq -c | sort -rn | head -20
```

### 4.4 HTML Element Patterns

**Heading Hierarchy**:
- `<h1>`: Work title (1 per document) - 100%
- `<h2>`: Chapter/part title - 85%
- `<h3>`: Section title - 70%
- `<h4>`: Subsection - 40%
- `<h5>` and `<h6>`: Rare (<5%)

**Paragraph Patterns**:
- Average paragraphs per document: {N}
- Paragraphs with anchors: {%}
- Anchor naming pattern: `<a name="s#p##">` (section #, paragraph ##)

**Link Density**:
- Average links per document: {N}
- Internal link ratio: {%}
- Footnote links ratio: {%}

## 5. Metadata Extraction Schema

### 5.1 File System Metadata

**Path Pattern**: `/section/{subsection}/{category}/{year}/{work}/ch##.htm`

**Extracted Fields**:
- `section`: From path component 1
- `subsection`: From path component 2
- `category`: From path component 3
- `year`: From path component 4 (regex: `(19|20)\d{2}`)
- `work`: From path component 5
- `chapter`: From filename (regex: `ch(\d+)`)

**Confidence**: 90% of files follow this pattern

### 5.2 HTML Metadata

**Meta Tags** (from `<head>`):
- `author`: 95% coverage
- `title`: 88% coverage
- `classification`: 65% coverage
- `keywords`: 45% coverage

**Title Tag**:
- Present in 99% of files
- Format: "{Work Title} - {Chapter/Section}"

### 5.3 Content Metadata

**Derived Fields**:
- `word_count`: Calculated from body text
- `has_footnotes`: Boolean (check for `href="#"` links)
- `has_images`: Boolean (check for `<img>` tags)
- `has_tables`: Boolean (check for `<table>` tags)
- `reading_time`: `word_count / 250` (minutes)

**Statistical Distribution**:
- Word count range: {min} - {max}
- Average word count: {avg}
- Median word count: {median}
- Documents with footnotes: {%}
- Documents with images: {%}

### 5.4 Example Metadata Record

```json
{
  "section": "archive",
  "subsection": "marx",
  "category": "works",
  "year": 1867,
  "work": "capital-v1",
  "chapter": 1,
  "file_path": "archive/marx/works/1867/capital-v1/ch01.htm",
  "file_extension": ".htm",
  "file_size_bytes": 87654,

  "title": "Capital Volume I - Chapter 1: Commodities",
  "meta_author": "Karl Marx",
  "classification": "Economics",
  "keywords": ["commodity", "value", "labor"],

  "breadcrumb": ["MIA", "Archive", "Marx", "Capital I", "Chapter 1"],
  "category_path": "Economics/Political Economy/Marxist",

  "curator_context": "Written 1867, published 1867...",
  "provenance": "Translated by Samuel Moore and Edward Aveling...",

  "word_count": 8567,
  "has_footnotes": true,
  "has_images": false,
  "has_tables": true,
  "reading_time_minutes": 34,
  "language": "en",

  "internal_links": ["/archive/marx/works/1867/capital-v1/ch02.htm"],
  "anchor_ids": ["s1p01", "s1p02", "s1p03"]
}
```

## 6. Linking Architecture

### 6.1 Internal Link Patterns

**Hierarchical Navigation**:
- Parent links: `../index.htm` (98% of files)
- Sibling links: `ch02.htm`, `ch03.htm` (95% of multi-chapter works)
- Child links: Rare in content pages

**Sequential Navigation**:
- "Next chapter" links: 85%
- "Previous chapter" links: 85%
- Pattern: Relative paths within work directory

### 6.2 Cross-Section Links

**Links to Other Sections**:
- Archive → Glossary: 45% of files link to term definitions
- Archive → Subject: 20% of files link to thematic collections
- Archive → Archive: 30% of files link to related authors

**Link Pattern**: Absolute paths from root (`/glossary/term.htm`)

### 6.3 Anchor System

**Anchor Naming Convention**:
- Pattern: `<a name="s{section}p{paragraph}">`
- Example: `<a name="s1p05">` = Section 1, Paragraph 5
- Coverage: 75% of documents have paragraph anchors
- Purpose: Precise citation and deep linking

**Footnote Anchors**:
- Pattern: `<a name="f{number}">`
- Bidirectional: Link from text to footnote and back
- Coverage: 60% of documents have footnotes

### 6.4 Link Topology

**Graph Structure**:
- Primarily **hierarchical** (work → chapter → section)
- Secondary **cross-reference** (related works, concepts)
- Tertiary **citation** (footnotes, quotes)

**Link Density Analysis**:
- Average internal links per page: {N}
- Average cross-section links: {M}
- Average footnote links: {K}

## 7. Unique Characteristics

### 7.1 Organizational Patterns

[What makes this section's organization unique?]

### 7.2 Content Types

[Specific content types found only/primarily in this section]

### 7.3 Temporal Characteristics

[If time-based organization, describe patterns]

### 7.4 Authorship Patterns

[Single-author works, multi-author, anonymous, etc.]

## 8. Content Analysis

### 8.1 Typical Document Structure

**Common Layout**:
1. Title (h1)
2. Curator context (class="context")
3. Body content with sections (h2/h3)
4. Footnotes section (if applicable)
5. Provenance information (class="information")

### 8.2 Content Density

**Reading Metrics**:
- Average words per document: {N}
- Estimated reading level: [assessed from samples]
- Technical complexity: [low/medium/high]

**Content Distribution**:
- Prose paragraphs: {%}
- Block quotes: {%}
- Lists: {%}
- Tables: {%}

### 8.3 Multimedia Elements

**Image Usage**:
- Documents with images: {%}
- Image types: [diagrams, portraits, scans]
- Average images per document (when present): {N}

**Table Usage**:
- Documents with tables: {%}
- Table types: [data tables, comparison matrices]

## 9. Chunking Recommendations

### 9.1 Recommended Chunk Boundary

**Primary Strategy**: [Paragraph-level / Section-level / Article-level / Entry-level]

**Rationale**:
- [Why this boundary is optimal]
- [How it aligns with content structure]
- [How it preserves semantic units]

### 9.2 Alternative Strategies

**Strategy 2**: [Description]
- Use case: [When to use this instead]
- Trade-offs: [Pros and cons]

**Strategy 3**: [Description]
- Use case: [When to use this instead]
- Trade-offs: [Pros and cons]

### 9.3 Chunk Size Estimates

**Expected Token Counts**:
- Minimum chunk: {N} tokens
- Average chunk: {M} tokens
- Maximum chunk: {K} tokens
- Target chunk: {T} tokens (recommendation)

**Chunk Distribution** (estimated):
- Small chunks (<500 tokens): {%}
- Medium chunks (500-1500 tokens): {%}
- Large chunks (>1500 tokens): {%}

### 9.4 Hierarchical Context Preservation

**Metadata to Include in Each Chunk**:
```json
{
  "chunk_id": "unique-identifier",
  "chunk_index": 0,
  "hierarchy": {
    "section": "archive",
    "author": "Marx",
    "work": "Capital Volume I",
    "chapter": "Chapter 1",
    "section": "Section 1",
    "paragraph": "005"
  },
  "breadcrumb": ["MIA", "Archive", "Marx", "Capital I", "Ch1", "S1", "P5"],
  "parent_document": "/path/to/ch01.htm",
  "anchor_id": "s1p05"
}
```

## 10. RAG Integration Strategy

### 10.1 Processing Pipeline

**Step-by-step**:
1. HTML parsing (BeautifulSoup/lxml)
2. Metadata extraction (all 5 layers)
3. Content cleaning (remove navigation, boilerplate)
4. Chunking (paragraph-level with context)
5. Embedding generation (per chunk)
6. Vector DB insertion with metadata

### 10.2 Metadata Enrichment

**Enrich each chunk with**:
- File system metadata (author, year, work)
- HTML metadata (title, classification)
- Hierarchical context (work → chapter → section → paragraph)
- Semantic annotations (curator context, provenance)
- Content metadata (word_count, has_footnotes)

### 10.3 Indexing Strategy

**Vector Database Schema**:
- **Collection Name**: "{section}-{subsection}"
- **Vector Dimension**: [based on embedding model]
- **Metadata Fields** (for filtering):
  - `section`, `subsection`, `author`
  - `year`, `classification`
  - `work_title`, `chapter_number`
  - `has_footnotes`, `reading_time`

**Filtering Examples**:
```python
# Query Marx's economic works from 1860s
query_filter = {
  "author": "Karl Marx",
  "classification": "Economics",
  "year": {"$gte": 1860, "$lte": 1869}
}

# Query works with footnotes (detailed analysis)
query_filter = {
  "has_footnotes": True,
  "reading_time_minutes": {"$gte": 10}
}
```

### 10.4 Query Patterns

**Expected User Queries**:
1. Conceptual: "What is surplus value?" → Semantic search
2. Author-specific: "What did Marx say about..." → Filter by author
3. Temporal: "What were views in 1917 about..." → Filter by year
4. Comparative: "Compare Lenin and Trotsky on..." → Multi-author filter
5. Citation: "Find the passage where Marx discusses..." → Anchor-level search

### 10.5 Cross-Section Integration

**How this section relates to others**:
- Links to Glossary for term definitions
- Links to Subject for thematic context
- Links to History for historical context
- Can be queried independently or jointly

**Integration Strategy**:
- Separate vector collections per section
- Unified metadata schema across sections
- Cross-section query expansion via links

## 11. Edge Cases and Exceptions

### 11.1 Unusual Files

**Identified Outliers**:
1. `{file1}` - {reason it's unusual}
2. `{file2}` - {reason it's unusual}

**Handling**: [How to process these files]

### 11.2 Missing Metadata

**Files Without Expected Metadata**:
- {N} files missing author meta tag ({%})
- {M} files missing classification ({%})

**Mitigation**: Extract from file path or infer from context

### 11.3 Broken Links

**Dead Links Found**: {N} instances
**Common Causes**:
- Renamed files
- Moved directories
- External sites down

**Handling**: Log and skip during processing

### 11.4 Encoding Issues

**Character Encoding Problems**: {N} files ({%})
**Common Issues**:
- Mojibake (garbled characters)
- Missing characters (boxes/question marks)
- Mixed encodings within file

**Mitigation**:
- Try multiple decodings (ISO-8859-1, UTF-8, cp1252)
- Use chardet library for detection
- Manual review of problematic files

## 12. Processing Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OCR errors in PDFs | Medium | High (60% of PDFs) | HTML-first strategy, manual review samples |
| Missing metadata | Low | Medium (10-30% files) | Extract from paths, use defaults |
| Encoding issues | Medium | Low (5% files) | Multi-encoding fallback, chardet |
| Large files (>5MB) | Low | Low (2% files) | Stream processing, chunk limits |
| Broken internal links | Low | Medium (10% links) | Validate during ingestion, log broken |
| Duplicate content | Low | Unknown | Deduplication via content hash |
| Inconsistent chunking | High | Low | Validate chunk boundaries, manual review |
| Embedding timeouts | Medium | Low | Batch processing, retry logic |

## 13. Sample Files Analyzed

**Total Files Read**: {N}

### Index Pages ({N} files)
1. `/path/to/index.htm` - Top-level navigation, shows hierarchy
2. `/path/to/subdir/index.htm` - Category index, links to works

### Content Pages ({N} files)
3. `/path/to/ch01.htm` - Typical chapter, has footnotes, 8.5k words
4. `/path/to/article.htm` - Short article, 1.2k words, no footnotes
...

### PDF Files ({N} files)
23. `/path/to/scan.pdf` - High OCR quality, book scan
24. `/path/to/periodical.pdf` - Medium OCR quality, newspaper

### Edge Cases ({N} files)
45. `/path/to/huge-file.htm` - 2.3MB, 450k words, needs special handling
46. `/path/to/broken-encoding.htm` - Encoding issues, requires chardet

## 14. Pattern Verification Commands

**Meta Tag Coverage**:
```bash
# Author meta tag
grep -r '<meta name="author"' /path/to/section | wc -l
# Result: 2,453 / 2,580 = 95%

# Description meta tag
grep -r '<meta name="description"' /path/to/section | wc -l
# Result: 2,270 / 2,580 = 88%

# All meta tag names
grep -roh '<meta name="[^"]*"' /path | sed 's/<meta name="\([^"]*\)".*/\1/' | sort | uniq -c | sort -rn
```

**CSS Class Distribution**:
```bash
grep -roh 'class="[^"]*"' /path/to/section | sort | uniq -c | sort -rn | head -20
# Result: quoteb (8234), title (2580), context (892)...
```

**Link Patterns**:
```bash
# Internal links
grep -roh 'href="[^"]*"' /path | grep -v 'http' | sort | uniq -c | sort -rn | head -20

# Anchor links
grep -roh 'href="#[^"]*"' /path | sort | uniq -c | sort -rn | head -20
```

**File Naming Patterns**:
```bash
# Year patterns
find /path -name "*.htm*" | grep -oE '(19|20)[0-9]{2}' | sort | uniq -c

# Chapter patterns
find /path -name "*.htm*" | grep -oE 'ch[0-9]+' | sort | uniq -c
```

## 15. Recommendations for RAG Implementation

### 15.1 Priority Level

**Priority**: [HIGH / MEDIUM / LOW]

**Rationale**: [Why this priority?]
- Size: [% of total corpus]
- Content quality: [assessment]
- User value: [expected query frequency]
- Processing complexity: [assessment]

### 15.2 Processing Complexity

**Complexity**: [SIMPLE / MODERATE / COMPLEX]

**Factors**:
- HTML structure: [consistent / variable]
- Metadata completeness: [% coverage]
- OCR requirements: [yes / no / partial]
- Encoding issues: [minimal / moderate / significant]
- Special handling: [list requirements]

### 15.3 Special Requirements

**Requirements**:
- [ ] OCR for PDF files
- [ ] Translation (if non-English)
- [ ] Encoding normalization
- [ ] Boilerplate removal
- [ ] Link validation
- [ ] Deduplication
- [ ] Manual review samples
- [ ] Custom chunking logic

### 15.4 Integration Dependencies

**Dependencies**:
- Requires {section X} processed first (for cross-references)
- Should process before {section Y} (foundational content)
- Can process independently

**Recommended Order**: [Position in processing pipeline]

## 16. Open Questions

**User Decisions Required**:

1. [Question 1 requiring user input]
   - Context: [Why this decision is needed]
   - Options: [A, B, C]
   - Recommendation: [Suggested choice with rationale]

2. [Question 2 requiring user input]
   - Context: [...]
   - Options: [...]
   - Recommendation: [...]

**Further Investigation Needed**:

1. [Question requiring additional research]
   - Reason: [Why not answered in this investigation]
   - Approach: [How to investigate further]

## 17. Appendices

### Appendix A: Full Directory Listing

[Tree output or structured listing]

### Appendix B: Sample HTML Structure

**File**: /path/to/sample.htm

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta charset="ISO-8859-1">
  <meta name="author" content="Karl Marx">
  <meta name="description" content="Chapter 1: Commodities">
  <title>Capital Volume I - Chapter 1</title>
</head>
<body>
  <h1 class="title">Capital Volume I</h1>
  <h2>Chapter 1: Commodities</h2>
  <p class="fst"><a name="s1p01"></a>The wealth of those societies...</p>
  ...
</body>
</html>
```

### Appendix C: Metadata Statistics

**Completeness Analysis**:

| Metadata Field | Coverage % | Complete Files | Missing Files |
|----------------|------------|----------------|---------------|
| author | 95% | 2,453 | 127 |
| title | 99% | 2,554 | 26 |
| classification | 65% | 1,677 | 903 |
| year | 78% | 2,012 | 568 |
| breadcrumb | 85% | 2,193 | 387 |

**Average Metadata Completeness**: {%} (across all fields)
```

---

## Statistical Sampling Methods

When section is very large (>10GB):

```bash
# Random sampling method
SECTION_PATH="/path/to/section"
SAMPLE_SIZE=1000

# Get random sample
find "$SECTION_PATH" -name "*.htm*" | shuf -n "$SAMPLE_SIZE" > sample_files.txt

# Check pattern in sample
check_pattern() {
  local pattern="$1"
  local count=0
  while read file; do
    grep -q "$pattern" "$file" && ((count++))
  done < sample_files.txt
  echo "Coverage: $count / $SAMPLE_SIZE = $(( 100 * count / SAMPLE_SIZE ))%"
}

# Usage
check_pattern '<meta name="author"'
check_pattern '<meta name="description"'
```

---

## Notes

- This reference guide complements the main SKILL.md
- Use command templates as starting points, customize per corpus
- Always document actual commands run in investigation report
- Update templates based on experience with different corpus types
- Share improvements and new patterns discovered

**Version**: 1.0
**Last Updated**: 2025-11-08
**Maintained By**: corpus-investigation skill users
