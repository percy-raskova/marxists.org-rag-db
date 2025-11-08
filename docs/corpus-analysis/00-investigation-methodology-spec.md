# Investigation Methodology Specification

**Purpose**: Define a reproducible, token-efficient, AI-agent-friendly methodology for systematically investigating large corpus sections to inform RAG architecture design.

**Version**: 1.0
**Created**: 2025-11-08
**Target Corpus**: Marxists Internet Archive (121GB, 96,637 HTML files, 21,141 PDFs)

---

## Table of Contents

1. [Overview](#overview)
2. [Investigation Framework](#investigation-framework)
3. [Stratified Sampling Strategies](#stratified-sampling-strategies)
4. [Pattern Recognition Techniques](#pattern-recognition-techniques)
5. [Metadata Extraction Protocols](#metadata-extraction-protocols)
6. [Section Analysis Template](#section-analysis-template)
7. [Token Efficiency Tactics](#token-efficiency-tactics)
8. [Verification Without Exhaustive Reading](#verification-without-exhaustive-reading)
9. [Quality Assurance Checklist](#quality-assurance-checklist)

---

## Overview

### Problem Statement

Large corpora (100GB+) cannot be exhaustively read within token budgets. We need systematic sampling and pattern recognition to understand structure, extract metadata schemas, and design chunking strategies without reading every file.

### Design Principles

1. **Reproducibility**: Any AI agent following this spec should produce equivalent analyses
2. **Token Efficiency**: Minimize tokens spent per GB of corpus analyzed
3. **Stratification**: Sample across multiple dimensions (time, type, size, author)
4. **Pattern Verification**: Use computational tools (grep, find) to verify patterns across corpus
5. **Edge Case Detection**: Explicitly sample outliers and exceptions
6. **Metadata Completeness**: Extract all metadata layers (file paths, HTML tags, content)

### Success Criteria

A successful investigation produces:

- **Directory structure documentation**: Complete hierarchy with size/count data
- **File type breakdown**: HTML vs PDF ratios, file naming conventions
- **Metadata schema**: All extractable metadata fields with examples
- **HTML structure patterns**: DOCTYPE, meta tags, CSS classes, semantic markup
- **Linking architecture**: Internal cross-references, hierarchical navigation, citations
- **Unique characteristics**: Section-specific patterns not found elsewhere
- **Chunking recommendations**: Optimal chunk boundaries for RAG ingestion
- **RAG integration strategy**: How this section fits into overall knowledge base

---

## Investigation Framework

### Phase 1: Reconnaissance (10% of tokens)

**Goal**: Understand section scope without deep reading

**Tasks**:
1. Read section index page (e.g., `/history/index.htm`)
2. Run directory structure analysis:
   ```bash
   cd /path/to/section
   tree -L 3 -h --du
   find . -type f -name "*.html" | wc -l
   find . -type f -name "*.pdf" | wc -l
   du -sh */
   ```
3. Identify subsections and size distribution
4. Document organizational hierarchy

**Output**: Section overview with size statistics

### Phase 2: Stratified Sampling (40% of tokens)

**Goal**: Sample representative files across key dimensions

**Dimensions to Stratify**:
- **Temporal**: Early, mid, late (if time-based organization)
- **Size**: Large subsections, medium, small
- **Type**: HTML vs PDF, different file naming patterns
- **Depth**: Top-level index pages, mid-level category pages, leaf content pages

**Sample Selection Algorithm**:
```python
def select_samples(section_path, target_samples=15):
    """
    Stratified sampling for corpus investigation.

    Returns:
        List of file paths to read, stratified by:
        - Size (large/medium/small subsections)
        - Depth (index/category/content)
        - Type (HTML/PDF)
        - Time period (if applicable)
    """
    samples = []

    # 1. Always read top-level index
    samples.append(f"{section_path}/index.htm")

    # 2. Sample large subsections (>1GB)
    large_dirs = get_dirs_by_size(section_path, min_size="1G")
    samples.extend(sample_from_each(large_dirs, n=2))

    # 3. Sample medium subsections (100MB-1GB)
    medium_dirs = get_dirs_by_size(section_path, min_size="100M", max_size="1G")
    samples.extend(sample_from_each(medium_dirs, n=1))

    # 4. Sample small subsections (<100MB)
    small_dirs = get_dirs_by_size(section_path, max_size="100M")
    samples.extend(random_sample(small_dirs, n=3))

    # 5. Sample different file types
    if has_pdfs(section_path):
        samples.extend(sample_pdfs(section_path, n=3))

    # 6. Sample different time periods (if time-based)
    if is_chronological(section_path):
        samples.extend(sample_by_decade(section_path, n=1))

    return samples[:target_samples]
```

**Tasks**:
1. Read sampled index pages to understand navigation structure
2. Read sampled content pages to understand HTML patterns
3. Read sampled PDFs (first page) to assess OCR quality
4. Document patterns and variations observed

**Output**: Pattern catalog with concrete examples

### Phase 3: Pattern Verification (30% of tokens)

**Goal**: Verify patterns hold across entire section using computational tools

**Verification Tasks**:
1. **Meta tag consistency**:
   ```bash
   grep -r '<meta name="author"' /path/to/section | head -20
   grep -r '<meta name="description"' /path/to/section | head -20
   ```

2. **CSS class usage**:
   ```bash
   grep -roh 'class="[^"]*"' /path/to/section | sort | uniq -c | sort -rn | head -20
   ```

3. **Link patterns**:
   ```bash
   grep -roh 'href="[^"]*"' /path/to/section | head -50
   ```

4. **File naming conventions**:
   ```bash
   find /path/to/section -type f -name "*.htm*" | sed 's/.*\///' | sort | uniq -c | sort -rn | head -20
   ```

5. **Anchor patterns**:
   ```bash
   grep -roh '<a name="[^"]*"' /path/to/section | head -50
   ```

**Tasks**:
1. Run verification commands
2. Count pattern occurrences
3. Identify exceptions and outliers
4. Document confidence levels (e.g., "90% of files follow pattern X")

**Output**: Pattern verification report with statistics

### Phase 4: Edge Case Analysis (10% of tokens)

**Goal**: Identify exceptions and unusual patterns

**Tasks**:
1. Sample largest files (top 5 by size)
2. Sample smallest files (bottom 5 by size)
3. Sample files with unusual names
4. Sample deepest nested files
5. Check files with no meta tags
6. Check files with no links

**Output**: Edge case documentation with handling recommendations

### Phase 5: Synthesis (10% of tokens)

**Goal**: Compile findings into actionable specification

**Tasks**:
1. Write section analysis document using template (see below)
2. Define metadata extraction schema
3. Recommend chunking strategy
4. Propose RAG integration approach
5. Identify risks and mitigation strategies

**Output**: Complete section analysis specification

---

## Stratified Sampling Strategies

### Size-Based Stratification

**Rationale**: Large sections dominate processing time and storage; must be well-understood.

**Strategy**:
- **>1GB sections**: Sample 10-15 files (critical to understand)
- **100MB-1GB sections**: Sample 5-10 files (important to document)
- **<100MB sections**: Sample 3-5 files (low priority, document briefly)

**Example**:
```
History Section (46GB total):
  ├── USA/pubs/ (43GB) → SAMPLE 15 files (93% of section)
  ├── USA/culture/ (4GB) → SAMPLE 10 files
  └── other/ (<1GB) → SAMPLE 5 files total
```

### Temporal Stratification

**Rationale**: Writing style, OCR quality, and metadata vary over time.

**Strategy**:
- Identify time range (e.g., 1900-2000)
- Sample 1-2 files per decade
- Oversample era boundaries (e.g., 1945, 1990)

**Example**:
```
Daily Worker periodical (1924-1926):
  Sample: 1924-01, 1924-07, 1925-01, 1925-07, 1926-01, 1926-07
  → 6 samples across 3 years
```

### Type-Based Stratification

**Rationale**: HTML and PDF require different processing pipelines.

**Strategy**:
- If section is mixed HTML/PDF, sample both
- Check for HTML-PDF pairs (same content, different format)
- Assess PDF OCR quality separately

**Example**:
```
Peking Review collection:
  ├── PR1958-01.pdf (full issue scan)
  ├── PR1958-01a.htm (article 1 extracted)
  └── PR1958-01b.htm (article 2 extracted)

  Sample both PDF and corresponding HTML to check overlap
```

### Depth-Based Stratification

**Rationale**: Index pages, category pages, and content pages have different structures.

**Strategy**:
- Sample at least 1 page from each level of hierarchy
- Top-level index (always read)
- Mid-level category pages (sample 3-5)
- Leaf-level content pages (sample 5-10)

**Example**:
```
/subject/
  ├── index.htm (DEPTH 0 - always read)
  ├── economy/
  │   ├── index.htm (DEPTH 1 - sample)
  │   └── capital.htm (DEPTH 2 - sample)
  └── women/
      └── index.htm (DEPTH 1 - sample)
```

---

## Pattern Recognition Techniques

### 1. HTML Structure Fingerprinting

**Goal**: Identify common HTML patterns without reading every file.

**Technique**: Extract and compare HTML structure skeletons.

**Method**:
```bash
# Extract DOCTYPE declarations
grep -r '<!DOCTYPE' /path/to/section | cut -d: -f2 | sort | uniq -c

# Extract meta tag schemas
grep -roh '<meta name="[^"]*"' /path/to/section | sort | uniq -c | sort -rn

# Extract common CSS classes
grep -roh 'class="[^"]*"' /path/to/section | sort | uniq -c | sort -rn | head -30

# Extract heading hierarchy
grep -roh '<h[1-6][^>]*>' /path/to/section | head -100
```

**Output**: HTML structure fingerprint showing common patterns

### 2. Metadata Schema Extraction

**Goal**: Identify all metadata fields present in section.

**Technique**: Aggregate all meta tags and extract field names.

**Method**:
```bash
# Find all meta tag names
grep -roh '<meta name="[^"]*" content="[^"]*"' /path/to/section | \
  sed 's/<meta name="\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -rn

# Find all meta property tags (OpenGraph, etc.)
grep -roh '<meta property="[^"]*"' /path/to/section | \
  sed 's/<meta property="\([^"]*\)".*/\1/' | \
  sort | uniq
```

**Output**: Complete list of metadata fields with occurrence counts

### 3. Link Topology Analysis

**Goal**: Understand internal linking structure.

**Technique**: Extract link patterns and analyze topology.

**Method**:
```bash
# Extract all internal links
grep -roh 'href="[^"]*"' /path/to/section | \
  grep -v 'http' | \
  sort | uniq -c | sort -rn | head -50

# Find cross-section links
grep -roh 'href="/[^"]*"' /path/to/section | \
  cut -d/ -f2 | \
  sort | uniq -c | sort -rn

# Find anchor links (footnotes, citations)
grep -roh 'href="#[^"]*"' /path/to/section | \
  sort | uniq -c | sort -rn | head -20
```

**Output**: Link topology map (hierarchical, cross-reference, citation)

### 4. File Naming Convention Detection

**Goal**: Understand file organization from naming patterns.

**Technique**: Extract naming patterns using regex.

**Method**:
```bash
# Extract year patterns
find /path/to/section -name "*.htm*" | \
  grep -oE '(19|20)[0-9]{2}' | \
  sort | uniq -c

# Extract volume/issue patterns
find /path/to/section -name "*.pdf" | \
  grep -oE 'v[0-9]+n[0-9]+' | \
  sort | uniq -c | head -20

# Extract chapter patterns
find /path/to/section -name "*.htm" | \
  grep -oE 'ch[0-9]+' | \
  sort | uniq -c
```

**Output**: File naming convention documentation

### 5. Content Type Classification

**Goal**: Categorize files by content type without reading.

**Technique**: Use file size, naming, and location heuristics.

**Method**:
```python
def classify_file_type(filepath):
    """
    Classify file content type from metadata.

    Returns: "index" | "article" | "chapter" | "reference" | "unknown"
    """
    filename = filepath.name
    filesize = filepath.stat().st_size

    # Index pages are usually named index.htm
    if filename == "index.htm":
        return "index"

    # Chapter files often have ch## pattern
    if re.match(r'ch\d+', filename):
        return "chapter"

    # Small files (<5KB) often navigation/reference
    if filesize < 5000:
        return "reference"

    # Medium files (5-50KB) often articles
    if filesize < 50000:
        return "article"

    # Large files (>50KB) often long-form content
    return "long_form"
```

**Output**: File type distribution statistics

---

## Metadata Extraction Protocols

### Layer 1: File System Metadata

**Source**: File paths, directory structure, filenames

**Extraction Method**: Parse file paths using regex patterns

**Fields**:
- `section`: Top-level directory (archive, subject, history)
- `subsection`: Secondary categorization
- `author`: Extracted from /archive/{author}/ paths
- `year`: Extracted from year-based directories
- `work_slug`: Work identifier from path
- `chapter`: Extracted from ch## filenames
- `file_extension`: .htm, .html, .pdf

**Example**:
```python
def extract_path_metadata(filepath: Path, corpus_root: Path) -> dict:
    """Extract metadata from file path structure."""
    relative = filepath.relative_to(corpus_root)
    parts = relative.parts

    metadata = {
        "section": parts[0] if parts else None,
        "file_extension": filepath.suffix,
    }

    # Archive section: /archive/{author}/{category}/{year}/{work}/
    if parts[0] == "archive" and len(parts) >= 2:
        metadata["author"] = parts[1].replace("-", " ").title()

        # Look for year in path
        for part in parts:
            if re.match(r'(18|19|20)\d{2}', part):
                metadata["year"] = int(part[:4])
                break

    # History section: /history/{country}/pubs/{publication}/{year}/
    elif parts[0] == "history" and len(parts) >= 5:
        metadata["country"] = parts[1]
        metadata["publication"] = parts[3]
        if re.match(r'\d{4}', parts[4]):
            metadata["year"] = int(parts[4])

    # Subject section: /subject/{topic}/
    elif parts[0] == "subject" and len(parts) >= 2:
        metadata["topic"] = parts[1]

    # Extract chapter number from filename
    if match := re.search(r'ch(\d+)', filepath.stem):
        metadata["chapter_number"] = int(match.group(1))

    return metadata
```

### Layer 2: HTML Meta Tags

**Source**: `<meta>` tags in HTML `<head>`

**Extraction Method**: Parse HTML, extract meta tags

**Standard Fields**:
- `author`: `<meta name="author" content="...">`
- `title`: `<meta name="description" content="...">` or `<title>`
- `classification`: `<meta name="classification" content="...">`
- `keywords`: `<meta name="keywords" content="...">`
- `viewport`: `<meta name="viewport" content="...">`

**Example**:
```python
from bs4 import BeautifulSoup

def extract_meta_tags(html_content: str) -> dict:
    """Extract metadata from HTML meta tags."""
    soup = BeautifulSoup(html_content, 'lxml')
    metadata = {}

    # Extract all meta tags
    for meta in soup.find_all('meta'):
        if meta.get('name'):
            metadata[meta['name']] = meta.get('content', '')
        elif meta.get('property'):
            metadata[meta['property']] = meta.get('content', '')

    # Extract title
    if title_tag := soup.find('title'):
        metadata['title'] = title_tag.get_text(strip=True)

    return metadata
```

### Layer 3: Breadcrumb Navigation

**Source**: Breadcrumb trails in HTML (usually `<p class="breadcrumb">` or similar)

**Extraction Method**: Parse breadcrumb HTML, extract hierarchy

**Fields**:
- `breadcrumb`: List of navigation levels
- `category_path`: Categorical location in knowledge structure

**Example**:
```python
def extract_breadcrumb(soup: BeautifulSoup) -> list[str]:
    """Extract breadcrumb navigation trail."""
    breadcrumb = []

    # Common breadcrumb patterns
    patterns = [
        ('p', {'class': 'breadcrumb'}),
        ('nav', {'class': 'breadcrumb'}),
        ('div', {'id': 'breadcrumb'}),
    ]

    for tag, attrs in patterns:
        if nav := soup.find(tag, attrs):
            # Extract text from links
            for link in nav.find_all('a'):
                breadcrumb.append(link.get_text(strip=True))
            break

    return breadcrumb
```

### Layer 4: Semantic CSS Classes

**Source**: CSS class attributes with semantic meaning

**Extraction Method**: Identify semantic class patterns, extract annotated content

**Semantic Classes** (MIA-specific):
- `class="context"`: Historical/editorial context annotations
- `class="information"`: Provenance and source information
- `class="quoteb"`: Block quotes
- `class="fst"`: First paragraph (often has anchor)
- `class="title"`: Work titles

**Example**:
```python
def extract_semantic_content(soup: BeautifulSoup) -> dict:
    """Extract content from semantic CSS classes."""
    semantic = {}

    # Extract context annotations
    if context := soup.find(class_='context'):
        semantic['curator_context'] = context.get_text(strip=True)

    # Extract provenance information
    if info := soup.find(class_='information'):
        semantic['provenance'] = info.get_text(strip=True)

    # Extract quotes
    quotes = [q.get_text(strip=True) for q in soup.find_all(class_='quoteb')]
    if quotes:
        semantic['block_quotes'] = quotes

    return semantic
```

### Layer 5: Content-Derived Metadata

**Source**: Analyzed from document content

**Extraction Method**: NLP, regex patterns, heuristics

**Fields**:
- `word_count`: Document length
- `language`: Detected language
- `has_footnotes`: Boolean, presence of footnote apparatus
- `has_images`: Boolean, presence of images
- `reading_time`: Estimated reading time
- `technical_level`: Estimated complexity (e.g., based on vocabulary)

**Example**:
```python
def extract_content_metadata(soup: BeautifulSoup) -> dict:
    """Extract metadata from document content."""
    text = soup.get_text(separator=' ', strip=True)

    metadata = {
        "word_count": len(text.split()),
        "has_footnotes": bool(soup.find_all('a', href=lambda h: h and h.startswith('#'))),
        "has_images": bool(soup.find_all('img')),
    }

    # Estimate reading time (250 words/minute)
    metadata["reading_time_minutes"] = metadata["word_count"] // 250

    return metadata
```

### Unified Metadata Schema

**Goal**: Combine all layers into single schema

**Schema Structure**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentMetadata:
    """Unified metadata schema for MIA documents."""

    # Layer 1: File system
    section: str  # archive, subject, history, glossary
    subsection: Optional[str]
    author: Optional[str]
    year: Optional[int]
    file_extension: str
    chapter_number: Optional[int]

    # Layer 2: HTML meta tags
    title: Optional[str]
    meta_author: Optional[str]  # May differ from path-based author
    classification: Optional[str]
    keywords: Optional[list[str]]

    # Layer 3: Breadcrumb
    breadcrumb: list[str]
    category_path: Optional[str]

    # Layer 4: Semantic content
    curator_context: Optional[str]
    provenance: Optional[str]
    block_quotes: list[str]

    # Layer 5: Content-derived
    word_count: int
    has_footnotes: bool
    has_images: bool
    reading_time_minutes: int
    language: str = "en"

    # Cross-referencing
    internal_links: list[str]
    external_links: list[str]
    anchor_ids: list[str]
```

---

## Section Analysis Template

Every section investigation should produce a document following this template:

```markdown
# {Section Name} Analysis

**Section Path**: /path/to/section/
**Total Size**: {X}GB
**File Count**: {N} HTML files, {M} PDFs
**Investigation Date**: YYYY-MM-DD
**Investigator**: [AI Agent ID or Human]

---

## 1. Executive Summary

[2-3 paragraph overview of section purpose, size, and key findings]

## 2. Directory Structure

[Document the hierarchical organization]

### 2.1 Hierarchy Diagram

```
/section/
  ├── subsection1/ ({size})
  │   ├── category/
  │   └── ...
  └── subsection2/ ({size})
```

### 2.2 Size Distribution

| Subsection | Size | HTML Count | PDF Count | % of Total |
|------------|------|------------|-----------|------------|
| ...        | ...  | ...        | ...       | ...        |

## 3. File Type Analysis

### 3.1 HTML Files

- **Count**: {N}
- **Naming Conventions**: [describe patterns]
- **Size Range**: {min} - {max}
- **Average Size**: {avg}

### 3.2 PDF Files

- **Count**: {M}
- **OCR Quality**: [assessed from samples]
- **Naming Conventions**: [describe patterns]
- **Purpose**: [scanned periodicals, books, etc.]

## 4. HTML Structure Patterns

### 4.1 DOCTYPE and Encoding

[Document common DOCTYPE declarations and character encodings]

### 4.2 Meta Tag Schema

[List all meta tag fields found, with occurrence frequencies]

### 4.3 Semantic CSS Classes

[Document CSS classes with semantic meaning]

### 4.4 HTML Element Patterns

[Common structural elements: headings, paragraphs, lists, tables]

## 5. Metadata Extraction Schema

[Define the metadata schema for this section using unified template]

### 5.1 File System Metadata

[Path-based fields specific to this section]

### 5.2 HTML Metadata

[Meta tags and their usage in this section]

### 5.3 Content Metadata

[Semantic content and derived fields]

### 5.4 Example Metadata Record

```json
{
  "section": "...",
  "title": "...",
  ...
}
```

## 6. Linking Architecture

### 6.1 Internal Link Patterns

[Describe how documents link within section]

### 6.2 Cross-Section Links

[Describe links to other sections]

### 6.3 Anchor System

[Describe anchor/footnote system if present]

### 6.4 Link Topology

[Hierarchical, cross-reference, citation patterns]

## 7. Unique Characteristics

[What makes this section different from others?]

### 7.1 Organizational Patterns

[Unique to this section]

### 7.2 Content Types

[Specific to this section]

### 7.3 Temporal Characteristics

[If time-based organization]

### 7.4 Authorship Patterns

[Single-author, multi-author, anonymous, etc.]

## 8. Content Analysis

[Based on sampled files]

### 8.1 Typical Document Structure

[Common document layout]

### 8.2 Content Density

[Words per page, reading level, technical complexity]

### 8.3 Multimedia Elements

[Images, tables, diagrams usage]

## 9. Chunking Recommendations

### 9.1 Recommended Chunk Boundary

[Where to split documents: paragraph, section, article, etc.]

### 9.2 Rationale

[Why this boundary is optimal]

### 9.3 Chunk Size Estimates

[Expected token counts per chunk]

### 9.4 Hierarchical Context Preservation

[How to preserve work → chapter → section hierarchy in metadata]

## 10. RAG Integration Strategy

### 10.1 Processing Pipeline

[Specific steps for processing this section]

### 10.2 Metadata Enrichment

[How to enhance chunks with metadata]

### 10.3 Indexing Strategy

[Vector DB collection structure, filtering fields]

### 10.4 Query Patterns

[Expected user queries for this section]

### 10.5 Cross-Section Integration

[How this section relates to others in RAG system]

## 11. Edge Cases and Exceptions

### 11.1 Unusual Files

[Document outliers]

### 11.2 Missing Metadata

[Files without expected metadata]

### 11.3 Broken Links

[Dead links, missing files]

### 11.4 Encoding Issues

[Character encoding problems]

## 12. Processing Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ...  | ...    | ...         | ...        |

## 13. Sample Files Analyzed

[List all files read during investigation with brief notes]

1. `/path/to/file1.htm` - Index page, shows navigation structure
2. `/path/to/file2.htm` - Typical content page, has footnotes
...

## 14. Pattern Verification Commands

[Document the grep/find commands used to verify patterns]

```bash
# Command 1: Verify meta tag usage
grep -r '<meta name="author"' /path/to/section | wc -l

# Command 2: Check CSS class distribution
grep -roh 'class="[^"]*"' /path/to/section | sort | uniq -c | sort -rn
```

## 15. Recommendations for RAG Implementation

[Actionable recommendations based on analysis]

### 15.1 Priority Level

[HIGH / MEDIUM / LOW for inclusion in initial RAG build]

### 15.2 Processing Complexity

[SIMPLE / MODERATE / COMPLEX]

### 15.3 Special Requirements

[OCR, translation, cleanup needed?]

### 15.4 Integration Dependencies

[Does this section require other sections to be processed first?]

## 16. Open Questions

[Questions that require user decision or further investigation]

1. [Question 1]
2. [Question 2]
...

## 17. Appendices

### Appendix A: Full Directory Listing

[Tree output for section]

### Appendix B: Sample HTML Structure

[Full HTML of 1-2 representative files]

### Appendix C: Metadata Statistics

[Aggregate statistics on metadata completeness]
```

---

## Token Efficiency Tactics

### 1. Use Computational Tools Instead of Reading

**Inefficient**:
- Read 100 files to find common meta tags
- Tokens used: ~500,000

**Efficient**:
- Use grep to extract all meta tags
- Read 5 sample files to understand context
- Tokens used: ~25,000

**Savings**: 95% token reduction

### 2. Strategic Sampling Over Exhaustive Coverage

**Inefficient**:
- Read every author's archive to understand structure
- Tokens used: 1,000,000+

**Efficient**:
- Read 3 authors (large, medium, small)
- Verify pattern with find commands
- Tokens used: ~50,000

**Savings**: 95% token reduction

### 3. Extract Structure, Not Content

**Inefficient**:
- Read entire documents to understand organization
- Tokens used: High

**Efficient**:
- Extract only headings, first paragraph, meta tags
- Tokens used: Low

**Implementation**:
```python
def extract_structure_only(html_content: str) -> dict:
    """Extract document structure without reading full content."""
    soup = BeautifulSoup(html_content, 'lxml')

    return {
        "title": soup.find('title').get_text() if soup.find('title') else None,
        "headings": [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
        "first_paragraph": soup.find('p').get_text(strip=True) if soup.find('p') else None,
        "meta_tags": {m.get('name'): m.get('content') for m in soup.find_all('meta') if m.get('name')},
        "link_count": len(soup.find_all('a')),
        "image_count": len(soup.find_all('img')),
    }
```

### 4. Aggregate Statistics Over Individual Analysis

**Inefficient**:
- Describe each file individually
- Tokens used: N * (tokens per file)

**Efficient**:
- Compute aggregate statistics
- Describe patterns, not instances
- Tokens used: Constant

**Example Output**:
```
Instead of:
  "file1.htm has 3 meta tags"
  "file2.htm has 3 meta tags"
  "file3.htm has 2 meta tags"

Write:
  "95% of files have 3 meta tags (author, description, classification)"
  "5% are missing description tag"
```

### 5. Reference Examples, Don't Reproduce

**Inefficient**:
- Include full HTML of 10 example files
- Tokens used: 50,000+

**Efficient**:
- Include 1-2 representative examples
- Reference file paths for others
- Tokens used: 5,000

### 6. Use Diffs to Show Variations

**Inefficient**:
- Show full HTML of each file type
- Tokens used: High

**Efficient**:
- Show one baseline example
- Show diffs for variations
- Tokens used: Low

---

## Verification Without Exhaustive Reading

### Principle: Trust but Verify

After identifying a pattern from samples, verify it holds across the corpus using computational tools.

### Verification Checklist

For each claimed pattern, run verification:

**Pattern**: "All Archive section files have author meta tag"

**Verification**:
```bash
# Count total HTML files
total=$(find /archive -name "*.htm*" | wc -l)

# Count files with author meta tag
with_author=$(grep -rl '<meta name="author"' /archive | wc -l)

# Calculate percentage
echo "Coverage: $with_author / $total = $(( 100 * with_author / total ))%"
```

**Confidence Levels**:
- **100%**: Pattern holds for all files → "Universal pattern"
- **90-99%**: Pattern holds for nearly all → "Standard pattern with rare exceptions"
- **75-89%**: Pattern holds for most → "Common pattern with notable exceptions"
- **50-74%**: Pattern holds for many → "Frequent pattern, not standard"
- **<50%**: Pattern is not dominant → "Occasional pattern"

### Statistical Sampling for Large Sections

For very large sections (>10GB), use statistical sampling to verify:

**Method**:
1. Randomly sample 1000 files (or 1% of total, whichever is smaller)
2. Check pattern in sample
3. Calculate 95% confidence interval

**Implementation**:
```bash
# Get random sample of 1000 files
find /path/to/section -name "*.htm*" | shuf -n 1000 > sample_files.txt

# Check pattern in sample
while read file; do
  grep -q '<meta name="author"' "$file" && echo "1" || echo "0"
done < sample_files.txt | \
  awk '{sum+=$1; count++} END {print "Coverage: " sum/count*100 "%"}'
```

### Outlier Detection

Identify files that don't match expected patterns:

```bash
# Find HTML files without author meta tag
find /archive -name "*.htm*" -exec grep -L '<meta name="author"' {} \; > no_author_tag.txt

# Sample outliers to understand why they differ
head -10 no_author_tag.txt
```

---

## Quality Assurance Checklist

Before marking a section investigation as complete, verify:

### Completeness Checklist

- [ ] **Directory structure fully documented** (all levels, with sizes)
- [ ] **File counts accurate** (HTML, PDF, other)
- [ ] **Size distribution documented** (per subsection)
- [ ] **Meta tag schema extracted** (all fields identified)
- [ ] **CSS class inventory complete** (semantic classes documented)
- [ ] **Link patterns documented** (hierarchical, cross-ref, citation)
- [ ] **Unique characteristics identified** (what makes section special)
- [ ] **Chunking strategy defined** (with rationale)
- [ ] **RAG integration approach proposed** (concrete implementation)
- [ ] **Edge cases documented** (outliers, exceptions, broken files)
- [ ] **Sample files listed** (all files read during investigation)
- [ ] **Verification commands included** (grep/find commands to verify patterns)
- [ ] **Confidence levels specified** (% of files matching each pattern)
- [ ] **Open questions documented** (decisions needed from user)

### Reproducibility Checklist

- [ ] **Sampling strategy documented** (can another agent reproduce?)
- [ ] **Bash commands included** (exact commands run for verification)
- [ ] **File paths specified** (examples use actual paths, not placeholders)
- [ ] **Timestamps included** (when investigation was performed)
- [ ] **Version control** (archive version/snapshot documented)

### Token Efficiency Checklist

- [ ] **Used grep/find instead of reading** (where applicable)
- [ ] **Sampled strategically** (not exhaustively)
- [ ] **Aggregated statistics** (not individual file descriptions)
- [ ] **Referenced examples** (not reproduced full content unnecessarily)
- [ ] **Extracted structure only** (not full content where not needed)

### Actionability Checklist

- [ ] **Metadata schema is code-ready** (can be implemented directly)
- [ ] **Chunking strategy is specific** (not vague recommendations)
- [ ] **Processing pipeline defined** (step-by-step)
- [ ] **Risks identified with mitigations** (not just problems, solutions too)
- [ ] **Priority level assigned** (HIGH/MEDIUM/LOW for RAG inclusion)

---

## Conclusion

This methodology provides a systematic, reproducible, token-efficient approach to investigating large corpus sections. By combining strategic sampling, pattern recognition, computational verification, and standardized documentation, AI agents can produce high-quality section analyses that inform robust RAG architecture design.

**Key Principles**:
1. **Sample strategically, verify computationally**
2. **Extract structure, not content**
3. **Document patterns, not instances**
4. **Specify confidence levels**
5. **Produce actionable specifications**

**Expected Output**: Complete section analysis specifications that enable:
- Metadata extraction pipeline implementation
- Chunking strategy execution
- RAG database schema design
- Query interface optimization
- Processing risk mitigation

---

**Next Steps**: Apply this methodology to investigate remaining MIA sections:
- History section (46GB) - Labor periodicals
- Subject section (9.1GB) - Thematic collections
- Glossary section (62MB) - Encyclopedia
- Language sections (28GB) - Multilingual expansion
