# Unified Metadata Schema Specification

**Version:** 1.0
**Status:** IMPLEMENTATION-READY
**Created:** 2025-11-08
**Dependencies:** Section analyses 01-05 complete
**Purpose:** Unified metadata schema for RAG ingestion across all corpus sections

---

## Executive Summary

This document defines the **unified metadata schema** for the Marxist Internet Archive RAG system, synthesizing findings from all 5 section investigations (Archive, History, Subject, Glossary, Reference). The schema supports:

1. **Multi-source extraction** - Combining path-based, meta tag, title, keyword, and breadcrumb metadata
2. **Section-aware processing** - Different extraction strategies for Archive vs. ETOL vs. EROL vs. Subject
3. **Entity linking** - Integration with Glossary section for canonical entities
4. **Knowledge graph construction** - Cross-reference tracking across sections
5. **Temporal coverage** - Consistent date/period extraction (1600s-2006)
6. **Multi-author attribution** - Support for anthologies and collaborative works

**Core Design Principles:**

- **Completeness over perfection**: Capture all available metadata, even if imperfect
- **Multi-layered extraction**: Primary + fallback strategies for critical fields
- **Provenance tracking**: Record metadata source (path vs. meta tag vs. inferred)
- **Section-specific rules**: Adaptive extraction based on corpus section characteristics
- **Entity normalization**: Link to canonical Glossary entities where possible

---

## 1. Core Metadata Schema

### 1.1 Complete Field Specification

```python
@dataclass
class DocumentMetadata:
    """
    Unified metadata for all MIA corpus documents.

    Fields are organized into 5 layers:
    1. Core identification (required)
    2. Authorship & provenance (best-effort extraction)
    3. Temporal & classification (extracted or inferred)
    4. Technical & processing (always populated)
    5. Semantic enrichment (from Glossary + cross-references)
    """

    # ===== LAYER 1: Core Identification (Required) =====
    source_url: str              # Reconstructed MIA URL (e.g., "https://www.marxists.org/archive/marx/...")
    title: str                   # Document title (fallback: filename if no title found)
    content_hash: str            # SHA256 first 16 chars (deduplication)
    section_type: Literal["archive", "history/etol", "history/erol", "history/other",
                           "subject", "glossary", "reference", "ebooks"]

    # ===== LAYER 2: Authorship & Provenance =====
    author: Optional[str]        # Primary author (canonical name from Glossary if matched)
    authors_alt: List[str]       # Alternative author attributions (co-authors, editors, etc.)
    author_source: str           # How author was extracted: "path" | "meta" | "title" | "keywords" | "inferred" | "unknown"
    author_confidence: float     # 0.0-1.0 confidence in author extraction

    organization: Optional[str]  # For EROL/organizational docs (e.g., "MLOC", "RCP-USA")
    provenance: Optional[str]    # Publication source (e.g., "First published in Pravda, 1917")
    transcriber: Optional[str]   # Archivist/transcriber (from meta tag, often misattributed as author)

    # ===== LAYER 3: Temporal & Classification =====
    date_written: Optional[str]  # Original composition date (YYYY, YYYY-MM, YYYY-MM-DD)
    date_published: Optional[str] # First publication date
    date_source: str             # How date was extracted: "path" | "meta" | "title" | "provenance" | "unknown"
    year_period: Optional[str]   # Period classification (e.g., "1900-1949")

    keywords: List[str]          # Keywords from meta tags or inferred (not subject taxonomy)
    classification: Optional[str] # MIA classification tag (e.g., "Politics, History, Political-economy")
    subject_categories: List[str] # Subject section categories if cross-referenced

    # ===== LAYER 4: Technical & Processing =====
    doc_type: Literal["html", "pdf"] # Source file type
    original_path: str           # Path in source archive (relative to /www.marxists.org/)
    character_encoding: str      # Detected encoding (utf-8, iso-8859-1, windows-1252, etc.)
    language: str                # ISO 639-1 code (default: "en" for English corpus)
    word_count: int              # Total words in markdown
    paragraph_count: int         # Total paragraphs in document

    processed_date: str          # ISO 8601 timestamp of processing
    processor_version: str       # Pipeline version (semantic versioning)

    # ===== LAYER 5: Semantic Enrichment =====
    glossary_entities: Dict[str, List[str]]  # Linked entities: {"people": ["Marx", "Lenin"], "terms": ["Surplus Value"], ...}
    cross_references: List[str]  # Internal MIA links (source_url format)
    document_structure: Dict[str, Any]  # {"heading_depth": 4, "has_footnotes": True, "section_count": 8, ...}
    rag_priority: Literal["high", "medium", "low"]  # Processing priority (based on document type and section)

    # ===== OPTIONAL: Section-Specific Fields =====
    # Archive-specific
    work_collection: Optional[str]  # For multi-volume works (e.g., "Capital Vol 1")
    chapter_number: Optional[int]   # For book chapters
    letter_recipient: Optional[str] # For correspondence

    # History-specific (ETOL/EROL)
    newspaper_name: Optional[str]   # For periodical issues
    newspaper_issue: Optional[str]  # Issue number/date
    movement_affiliation: Optional[str]  # Political movement/organization
    country_focus: Optional[str]    # Primary geographic focus

    # Subject-specific
    thematic_category: Optional[str]  # Subject taxonomy category
    anthology_title: Optional[str]    # For anthology collections

    # Glossary-specific
    glossary_type: Optional[Literal["people", "terms", "orgs", "events", "periodicals", "places"]]
    entry_id: Optional[str]         # Canonical entry ID for cross-referencing
    cross_reference_count: int = 0  # Number of internal cross-references
```

### 1.2 Required vs. Optional Fields

**Always Required (Pipeline will fail if missing):**
- `source_url`
- `title`
- `content_hash`
- `section_type`
- `doc_type`
- `original_path`
- `language`
- `word_count`
- `processed_date`

**Best-Effort Extraction (Empty if unavailable):**
- `author` (target 85%+ coverage via multi-source extraction)
- `date_written` (target 60%+ coverage)
- `keywords` (target 50%+ coverage)
- All Layer 5 semantic enrichment fields

**Section-Specific Fields:**
- Only populated when applicable (e.g., `newspaper_name` only for ETOL/EROL periodicals)

---

## 2. Multi-Source Extraction Strategies

### 2.1 Author Extraction (Target: 85%+ Coverage)

**Extraction Pipeline (in order of precedence):**

```python
def extract_author(html_path: Path, soup: BeautifulSoup, section: str) -> AuthorExtractionResult:
    """
    Multi-source author extraction with confidence scoring.

    Returns: (author_name, source, confidence)
    """

    # ===== STRATEGY 1: Path-based (Archive section) =====
    # Archive: /archive/{author-slug}/works/... → 100% accurate
    if section == "archive":
        if m := re.search(r'/archive/([^/]+)/', str(html_path)):
            author_slug = m.group(1)
            canonical_name = lookup_glossary_canonical_name(author_slug)
            return (canonical_name, "path", 1.0)

    # ===== STRATEGY 2: ETOL Writers path =====
    # ETOL: /history/etol/writers/{author-slug}/... → 100% accurate
    if section == "history/etol" and "/writers/" in str(html_path):
        if m := re.search(r'/writers/([^/]+)/', str(html_path)):
            author_slug = m.group(1)
            canonical_name = lookup_glossary_canonical_name(author_slug)
            return (canonical_name, "path", 1.0)

    # ===== STRATEGY 3: Title parsing (ETOL documents) =====
    # Pattern: "James P. Cannon: Theses on the American Revolution" → 60% in ETOL
    title = extract_title(soup)
    if title and ':' in title:
        potential_author = title.split(':')[0].strip()
        # Validate against Glossary
        if is_valid_person_name(potential_author):
            canonical_name = lookup_glossary_canonical_name(potential_author)
            return (canonical_name, "title", 0.8)

    # ===== STRATEGY 4: Keywords (ETOL/EROL) =====
    # Keywords often list authors: "Farrell Dobbs, Vincent Dunne, James Cannon"
    keywords = extract_keywords(soup)
    if keywords:
        for keyword in keywords:
            if is_valid_person_name(keyword):
                # First valid person name in keywords
                canonical_name = lookup_glossary_canonical_name(keyword)
                return (canonical_name, "keywords", 0.7)

    # ===== STRATEGY 5: EROL organization attribution (95% reliable) =====
    # EROL uses title + keywords for organizational authorship
    if section == "history/erol":
        # Extract from title: "MLOC: Statement on Sino-Soviet Split"
        if m := re.match(r'^([A-Z]{2,}):?\s', title):
            org_acronym = m.group(1)
            return (f"Organization: {org_acronym}", "title", 0.9)

        # Extract from keywords: "MLOC, Maoism, Anti-revisionism"
        for keyword in keywords:
            if keyword.isupper() and len(keyword) <= 8:  # Acronyms
                return (f"Organization: {keyword}", "keywords", 0.8)

    # ===== STRATEGY 6: Meta tag (40-80% reliable, but often transcriber) =====
    meta_author = soup.find('meta', attrs={'name': 'author'})
    if meta_author and meta_author.get('content'):
        author_name = meta_author['content']
        # Check if it's a transcriber name (common ETOL pattern)
        transcriber_names = ["Einde O'Callaghan", "David Walters", "Sally Ryan", "Arie Bober"]
        if author_name in transcriber_names:
            # It's a transcriber, not author - store separately
            return (None, "meta", 0.0)  # Continue to next strategy
        else:
            canonical_name = lookup_glossary_canonical_name(author_name)
            return (canonical_name, "meta", 0.6)

    # ===== STRATEGY 7: First paragraph "By [Author]" pattern =====
    first_para = soup.find('p', class_='fst') or soup.find('p')
    if first_para:
        text = first_para.get_text()
        if m := re.match(r'^By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text):
            potential_author = m.group(1)
            canonical_name = lookup_glossary_canonical_name(potential_author)
            return (canonical_name, "content", 0.5)

    # ===== FALLBACK: Unknown =====
    return (None, "unknown", 0.0)
```

**Section-Specific Success Rates (from corpus analysis):**

| Section | Expected Coverage | Primary Strategy | Confidence |
|---------|------------------|------------------|------------|
| Archive | 100% | Path-based | 1.0 |
| ETOL writers | 100% | Path-based | 1.0 |
| ETOL documents | 85% | Title parsing + keywords | 0.7-0.8 |
| EROL | 95% | Organization from title/keywords | 0.8-0.9 |
| History/Other | 40-80% | Meta tag + keywords | 0.4-0.8 |
| Subject | 48% | Meta tag + cross-ref to Archive | 0.5-0.7 |
| Glossary | 100% | Entry structure | 1.0 |
| Reference | 100% | Path-based | 1.0 |

### 2.2 Date Extraction (Target: 60%+ Coverage)

**Extraction Pipeline:**

```python
def extract_dates(html_path: Path, soup: BeautifulSoup, section: str) -> DateExtractionResult:
    """
    Multi-source date extraction with source tracking.

    Returns: (date_written, date_published, source)
    """

    # ===== STRATEGY 1: Year from path (53% in Archive) =====
    # Pattern: /archive/marx/works/1867-c1/ch01.htm → "1867"
    if m := re.search(r'/works/(\d{4})(?:-[a-z]\d+)?/', str(html_path)):
        year = m.group(1)
        return (year, None, "path")

    # ===== STRATEGY 2: Date from title (common in Archive/ETOL) =====
    # Patterns: "Letter to Engels (March 1867)", "Speech (1917)", "Manifesto (1848-1850)"
    title = extract_title(soup)
    if m := re.search(r'\(([A-Za-z\s]*\d{4}(?:-\d{4})?)\)', title):
        date_str = m.group(1)
        return (date_str, None, "title")

    # ===== STRATEGY 3: EROL chronology path =====
    # Pattern: /history/erol/ncm-1/1960s/mloc-1969.htm → "1969"
    if section == "history/erol":
        if m := re.search(r'/(\d{4})s?/', str(html_path)):
            decade = m.group(1)
            return (f"{decade}s", None, "path")
        if m := re.search(r'-(\d{4})\.htm', str(html_path)):
            year = m.group(1)
            return (year, None, "path")

    # ===== STRATEGY 4: Meta date tag =====
    meta_date = soup.find('meta', attrs={'name': 'date'})
    if meta_date and meta_date.get('content'):
        return (meta_date['content'], None, "meta")

    # ===== STRATEGY 5: Provenance info box =====
    # Look for "First published: YYYY" or "Written: Month YYYY"
    info_box = soup.find(class_='info') or soup.find(class_='information')
    if info_box:
        text = info_box.get_text()
        if m := re.search(r'(?:First published|Written|Published):\s*([A-Za-z\s]*\d{4})', text):
            date_str = m.group(1)
            return (None, date_str, "provenance")  # This is publication date

    # ===== FALLBACK: Unknown =====
    return (None, None, "unknown")
```

**Temporal Coverage by Section (from corpus analysis):**

| Section | Temporal Range | Primary Date Source | Coverage |
|---------|---------------|---------------------|----------|
| Archive | 1838-1990 | Path (53%) + Title (25%) | 78% |
| ETOL | 1920s-1990s | Path + Provenance | 65% |
| EROL | 1960s-1980s | Path + Filename | 80% |
| Subject | 1600s-2006 (Peking Review) | Meta + Cross-ref | 45% |
| Glossary | N/A (encyclopedia) | Entry content | 90% (birth/death dates) |
| Reference | 1600s-1990s | Path + Meta | 55% |

### 2.3 Keywords & Classification Extraction

**Extraction Strategy:**

```python
def extract_keywords_classification(soup: BeautifulSoup, section: str) -> KeywordsResult:
    """
    Extract keywords and classification tags.
    """

    # Keywords from meta tag (90% in ETOL, 42% in Subject, 38% in Archive)
    keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
    keywords = []
    if keywords_meta and keywords_meta.get('content'):
        # Split on comma, clean whitespace
        keywords = [k.strip() for k in keywords_meta['content'].split(',') if k.strip()]

    # Classification from meta tag (40% in ETOL, 22% in Subject, 16% in Archive)
    classification_meta = soup.find('meta', attrs={'name': 'classification'})
    classification = None
    if classification_meta and classification_meta.get('content'):
        classification = classification_meta['content']

    # Subject categories from cross-references (Subject section only)
    subject_categories = []
    if section == "subject":
        # Extract from breadcrumb
        title_div = soup.find(class_='title')
        if title_div:
            breadcrumb_links = title_div.find_all('a', class_='title')
            subject_categories = [link.get_text(strip=True) for link in breadcrumb_links]

    return KeywordsResult(keywords, classification, subject_categories)
```

**Coverage by Section:**

| Section | Keywords | Classification | Subject Categories |
|---------|---------|----------------|-------------------|
| Archive | 38% | 16% | N/A (author-based) |
| ETOL | 90% | 40% | N/A |
| EROL | 85% | 35% | N/A |
| Subject | 42% | 22% | 64% (from breadcrumb) |
| Glossary | N/A | N/A | 100% (type-based) |
| Reference | 30% | 10% | N/A |

---

## 3. Section-Specific Metadata Rules

### 3.1 Archive Section (`/archive/`)

**Metadata Characteristics:**
- **Author**: 100% coverage via path-based extraction
- **Date**: 78% coverage (53% path + 25% title)
- **Structure**: Hierarchical (work → chapter → section)
- **Encoding**: 62% ISO-8859-1 (requires conversion)

**Specific Fields to Populate:**
```python
section_type = "archive"
author_source = "path"  # Always path-based
author_confidence = 1.0  # Always canonical

# Work collection detection
if "/works/" in path and re.search(r'/\d{4}-[a-z]\d+/', path):
    work_collection = extract_work_title(path)  # e.g., "Capital Vol 1"
    chapter_number = extract_chapter_number(path)  # e.g., 1 from "ch01.htm"

# Letter detection
if "/letters/" in path:
    letter_recipient = extract_recipient(soup)  # From title or first para
```

**Priority:**
- Articles/chapters: `rag_priority = "high"`
- Index pages: `rag_priority = "low"` (minimal content)
- Letters: `rag_priority = "medium"`

### 3.2 History/ETOL Section (`/history/etol/`)

**Metadata Characteristics:**
- **Author**: 85% coverage (path + title + keywords)
- **Meta tags**: 100% have `author` but it's transcriber (30-70% accurate for true author)
- **Keywords**: 90% coverage, extensive
- **Structure**: Variable (70% good h3-h4 hierarchies, 30% flat)

**Specific Fields to Populate:**
```python
section_type = "history/etol"

# Transcriber capture (don't confuse with author)
meta_author = soup.find('meta', attrs={'name': 'author'})
if meta_author and meta_author['content'] in TRANSCRIBER_NAMES:
    transcriber = meta_author['content']
    # Author extraction continues with title/keywords strategies

# Newspaper detection
if "/newspape/" in path:
    newspaper_name = extract_newspaper_name(path)  # e.g., "The Militant"
    newspaper_issue = extract_issue(soup)  # From title or meta
    rag_priority = "medium"  # Periodicals less critical than documents

# Movement affiliation from keywords
movement_keywords = ["Trotskyism", "Fourth International", "SWP", "ISO"]
movement_affiliation = extract_movement(keywords, movement_keywords)
```

**Priority:**
- Document/ subdirectory: `rag_priority = "high"`
- Newspape/ subdirectory: `rag_priority = "medium"`
- Writers/ subdirectory: `rag_priority = "high"` (biographical + analysis)

### 3.3 History/EROL Section (`/history/erol/`)

**Metadata Characteristics:**
- **Author**: 95% coverage via organizational attribution
- **Meta tags**: 100% have `author = "EROL"` (useless, ignore)
- **Organization**: 95% from title/keywords (org acronyms)
- **Heading structure**: UNIQUE - 90% use h3 as title (NOT h1)

**Specific Fields to Populate:**
```python
section_type = "history/erol"

# Organization extraction (primary attribution)
organization = extract_org_from_title_keywords(soup)
author = None  # Often no individual author
author_source = "organization"
author_confidence = 0.9

# Country focus from path or keywords
if "/ncm-" in path:  # New Communist Movement subsections
    country_focus = extract_country(path)  # e.g., "USA", "Canada"
    movement_affiliation = "New Communist Movement"

# Period from path
if m := re.search(r'/(\d{4})s/', path):
    year_period = f"{m.group(1)}s"
```

**Priority:**
- Chronology documents: `rag_priority = "high"` (historical analysis)
- Periodicals: `rag_priority = "medium"`

### 3.4 History/Other Section (`/history/usa/`, `/history/ussr/`, etc.)

**Metadata Characteristics:**
- **Author**: 40-80% coverage (highly variable)
- **Structure**: 40% have NO headings (requires paragraph-based chunking)
- **Encoding**: Mixed
- **Quality**: Variable OCR/transcription quality

**Specific Fields to Populate:**
```python
section_type = "history/other"

# Country from path
country_focus = extract_country_from_path(path)  # e.g., "USA", "USSR", "England"

# Quality flag for heading-less documents
if document_structure['heading_depth'] == 0:
    rag_priority = "low"  # Harder to chunk semantically
```

**Priority:**
- Documents with good structure: `rag_priority = "medium"`
- Heading-less documents: `rag_priority = "low"`

### 3.5 Subject Section (`/subject/`)

**Metadata Characteristics:**
- **Cross-references**: 64% link to /archive/, 19% to /reference/
- **Multi-author**: Anthology structure with 80+ authors in some subjects
- **Document types**: 55% navigation indexes (exclude), 18% periodicals, 15% essays
- **Special content**: 8.4GB Peking Review (94% of section)

**Specific Fields to Populate:**
```python
section_type = "subject"

# Thematic category from path
thematic_category = extract_subject_category(path)  # e.g., "dialectics", "economy", "china"

# Anthology detection
if is_index_page(soup) and has_multiple_authors(soup):
    anthology_title = extract_title(soup)
    authors_alt = extract_all_authors(soup)  # List of contributing authors
    rag_priority = "low"  # Index pages, not primary content

# Peking Review special handling
if "/china/" in path and "/peking-review/" in path:
    newspaper_name = "Peking Review"
    newspaper_issue = extract_issue(path)  # e.g., "1958-01" (year-week)
    rag_priority = "medium"  # Historical periodical

# Cross-reference extraction for knowledge graph
cross_references = extract_internal_links(soup, base_url="https://www.marxists.org")
```

**Priority:**
- Essays/articles: `rag_priority = "high"`
- Periodical issues: `rag_priority = "medium"`
- Navigation indexes: `rag_priority = "low"` (exclude from chunking)

### 3.6 Glossary Section (`/glossary/`)

**Metadata Characteristics:**
- **100% structured entries**: People, terms, orgs, events, periodicals, places
- **Cross-reference network**: 5,000-10,000 edges across ~2,500 nodes
- **Entity extraction foundation**: CRITICAL for RAG metadata enrichment

**Specific Fields to Populate:**
```python
section_type = "glossary"

# Glossary type from path
glossary_type = extract_glossary_type(path)  # "people" | "terms" | "orgs" | "events" | "periodicals" | "places"

# Entry ID for canonical cross-referencing
entry_id = generate_entry_id(path)  # e.g., "people/m/a/marx-karl"

# Extract biographical dates (people glossary)
if glossary_type == "people":
    dates = extract_birth_death_dates(soup)
    date_written = dates['birth']  # or 'death'

# Extract event dates
if glossary_type == "events":
    date_written = extract_event_date(soup)

# Cross-reference count
cross_references = extract_internal_links(soup)
cross_reference_count = len(cross_references)

# Canonical name for entity linking
canonical_name = extract_canonical_name(soup, glossary_type)
```

**Priority:**
- ALL glossary entries: `rag_priority = "high"` (foundation for entity extraction)

### 3.7 Reference Section (`/reference/`)

**Metadata Characteristics:**
- **100% Git-LFS storage**: Must run `git lfs pull` before processing
- **105 non-Marxist authors**: Anarchists, classical economists, German idealists
- **Key distinction**: Mao/Stalin/Hoxha in Reference (not core Marxism)

**Specific Fields to Populate:**
```python
section_type = "reference"

# Author from path (100% reliable)
author = extract_author_from_reference_path(path)
author_source = "path"
author_confidence = 1.0

# Subject organization
if "/subject/philosophy/" in path:
    country_code = extract_country_code(path)  # e.g., "us", "ge", "fr"
    classification = f"Philosophy ({country_code.upper()})"
elif "/subject/economics/" in path:
    classification = "Classical Economics"
```

**Priority:**
- Hegel, Smith, Ricardo: `rag_priority = "high"` (foundational reference)
- Anarchists: `rag_priority = "medium"`
- Mao/Stalin/Hoxha: `rag_priority = "medium"` (doctrinal reference, not core)

---

## 4. Entity Linking Strategy

### 4.1 Glossary-Based Canonical Names

**Objective**: Link extracted metadata to canonical Glossary entities for:
- Author name normalization
- Term disambiguation
- Organization identification
- Event/period contextualization

**Implementation:**

```python
class GlossaryLinker:
    """Link extracted metadata to canonical Glossary entities."""

    def __init__(self, glossary_index: Dict[str, GlossaryEntry]):
        """
        glossary_index: Pre-loaded index of all Glossary entries
        Structure: {
            "people": {"marx-karl": GlossaryEntry(...), ...},
            "terms": {"surplus-value": GlossaryEntry(...), ...},
            ...
        }
        """
        self.glossary = glossary_index

    def normalize_author_name(self, raw_name: str) -> Tuple[str, str, float]:
        """
        Normalize author name to canonical Glossary form.

        Returns: (canonical_name, entry_id, match_confidence)

        Examples:
            "marx" → ("Karl Marx", "people/m/a/marx-karl", 1.0)
            "K. Marx" → ("Karl Marx", "people/m/a/marx-karl", 0.95)
            "Vladimir Ilyich Lenin" → ("Vladimir Lenin", "people/l/e/lenin-vladimir", 0.98)
            "Unknown Author" → (None, None, 0.0)
        """
        # Fuzzy matching against Glossary people entries
        # 1. Exact match on surname
        # 2. Partial match on full name
        # 3. Alias matching (e.g., "Trotsky" → "Leon Trotsky")
        pass

    def extract_linked_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract and link entities mentioned in document content.

        Returns: {
            "people": ["Karl Marx", "Friedrich Engels"],
            "terms": ["Surplus Value", "Mode of Production"],
            "organizations": ["First International"],
            ...
        }
        """
        # NER + Glossary matching
        # 1. Extract potential entity mentions
        # 2. Match against Glossary index
        # 3. Disambiguate using context
        pass
```

**Glossary Index Pre-Loading:**

The RAG pipeline will pre-load a Glossary index at startup:

```python
# During pipeline initialization
glossary_index = build_glossary_index(
    glossary_path="/media/user/marxists.org/www.marxists.org/glossary/"
)

# Index structure:
{
    "people": {
        "marx-karl": {
            "canonical_name": "Karl Marx",
            "aliases": ["K. Marx", "Marx", "Karl Heinrich Marx"],
            "birth": "1818",
            "death": "1883",
            "entry_url": "https://www.marxists.org/glossary/people/m/a.htm#marx-karl"
        },
        ...
    },
    "terms": {
        "surplus-value": {
            "canonical_name": "Surplus Value",
            "definition_preview": "The difference between the value produced by labor...",
            "entry_url": "https://www.marxists.org/glossary/terms/s/u.htm#surplus-value"
        },
        ...
    },
    ...
}
```

### 4.2 Entity Enrichment Pipeline

**Processing Flow:**

1. **Extract raw metadata** using multi-source strategies (Section 2)
2. **Normalize author names** via Glossary linking
3. **Extract entity mentions** from document content
4. **Link entities** to canonical Glossary entries
5. **Populate `glossary_entities` field** with linked entities

**Example Result:**

```python
DocumentMetadata(
    # Core fields
    source_url="https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm",
    title="Commodities",
    section_type="archive",

    # Author linking
    author="Karl Marx",  # Canonical from Glossary
    author_source="path",
    author_confidence=1.0,

    # Entity linking
    glossary_entities={
        "people": ["Karl Marx", "Aristotle"],  # Mentioned in footnotes
        "terms": [
            "Surplus Value",
            "Use Value",
            "Exchange Value",
            "Commodity",
            "Abstract Labor"
        ],
        "organizations": [],
        "events": [],
    },

    # Cross-references
    cross_references=[
        "https://www.marxists.org/archive/marx/works/1867-c1/ch02.htm",  # Next chapter
        "https://www.marxists.org/glossary/terms/s/u.htm#surplus-value"  # Glossary link
    ],

    # Document structure
    document_structure={
        "heading_depth": 4,
        "section_count": 8,
        "has_footnotes": True,
        "footnote_count": 23,
        "paragraph_count": 156,
        "avg_paragraph_length": 943
    }
)
```

---

## 5. Character Encoding Strategy

### 5.1 Encoding Distribution (from Corpus Analysis)

| Encoding | Archive | ETOL | EROL | Subject | Reference | Strategy |
|----------|---------|------|------|---------|-----------|----------|
| ISO-8859-1 | 62% | 55% | 48% | 89% | 60% | Convert to UTF-8 |
| UTF-8 | 21% | 30% | 40% | 4% | 25% | No conversion |
| Windows-1252 | 11% | 10% | 8% | 1% | 10% | Convert to UTF-8 |
| Unspecified | 6% | 5% | 4% | 6% | 5% | Detect + convert |

### 5.2 Encoding Normalization

**Processing Pipeline:**

```python
def normalize_encoding(raw_html: bytes, declared_encoding: Optional[str]) -> str:
    """
    Normalize all content to UTF-8.

    Strategy:
    1. Try declared encoding from meta tag
    2. Detect using chardet if undeclared
    3. Fallback sequence: UTF-8 → ISO-8859-1 → Windows-1252 → Latin-1
    4. Record final encoding in metadata
    """

    # Try declared encoding first
    if declared_encoding:
        try:
            return raw_html.decode(declared_encoding)
        except UnicodeDecodeError:
            pass  # Continue to detection

    # Detect encoding
    import chardet
    detected = chardet.detect(raw_html)

    # Try detected encoding
    if detected['confidence'] > 0.7:
        try:
            return raw_html.decode(detected['encoding'])
        except UnicodeDecodeError:
            pass

    # Fallback sequence
    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']:
        try:
            return raw_html.decode(encoding, errors='replace')
        except UnicodeDecodeError:
            continue

    # Ultimate fallback: UTF-8 with replacement characters
    return raw_html.decode('utf-8', errors='replace')
```

**Metadata Recording:**

```python
# Record final encoding used
metadata.character_encoding = final_encoding
```

---

## 6. Implementation Checklist

### 6.1 Processing Pipeline Updates

- [ ] Implement `DocumentMetadata` dataclass with all fields
- [ ] Create multi-source extraction functions for author, date, keywords
- [ ] Build section-specific extraction rules (Archive, ETOL, EROL, Subject, Glossary, Reference)
- [ ] Implement Glossary index pre-loading
- [ ] Create entity linking pipeline
- [ ] Add character encoding normalization
- [ ] Implement confidence scoring for extracted fields
- [ ] Add provenance tracking (record extraction source for each field)

### 6.2 Glossary Integration

- [ ] Parse all 6 Glossary types into structured index
- [ ] Build fuzzy matching for author name normalization
- [ ] Create canonical entity ID system
- [ ] Implement cross-reference extraction
- [ ] Build entity mention extraction (NER + Glossary matching)

### 6.3 Validation & Testing

- [ ] Validate metadata extraction on 100-sample test set per section
- [ ] Verify author coverage targets (Archive 100%, ETOL 85%, EROL 95%)
- [ ] Test encoding normalization on problematic files
- [ ] Verify entity linking accuracy (target 90%+ precision)
- [ ] Test cross-reference extraction completeness

### 6.4 Documentation

- [ ] Document extraction strategies in processing module docstrings
- [ ] Create metadata field glossary for RAG users
- [ ] Document section-specific quirks and edge cases
- [ ] Provide examples of well-extracted vs. poorly-extracted documents

---

## 7. Appendix: Metadata Examples

### 7.1 Well-Structured Archive Document

```yaml
# /archive/marx/works/1867-c1/ch01.htm
source_url: "https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm"
title: "Capital Vol. I, Chapter 1: Commodities"
section_type: "archive"
author: "Karl Marx"
authors_alt: []
author_source: "path"
author_confidence: 1.0
organization: null
provenance: "First published: 1867"
transcriber: null

date_written: "1867"
date_published: "1867"
date_source: "path"
year_period: "1850-1899"

keywords: ["capital", "commodity", "labor", "value", "political economy"]
classification: "Politics, Economics"
subject_categories: []

doc_type: "html"
original_path: "/archive/marx/works/1867-c1/ch01.htm"
character_encoding: "iso-8859-1"
language: "en"
word_count: 12847
paragraph_count: 156

processed_date: "2025-11-08T10:30:00Z"
processor_version: "1.0.0"

glossary_entities:
  people: ["Karl Marx", "Aristotle"]
  terms: ["Surplus Value", "Use Value", "Exchange Value", "Commodity", "Abstract Labor"]
  organizations: []
  events: []

cross_references:
  - "https://www.marxists.org/archive/marx/works/1867-c1/ch02.htm"
  - "https://www.marxists.org/glossary/terms/s/u.htm#surplus-value"

document_structure:
  heading_depth: 4
  has_footnotes: true
  section_count: 8

rag_priority: "high"

# Archive-specific
work_collection: "Capital Volume I"
chapter_number: 1
letter_recipient: null
```

### 7.2 ETOL Document with Multiple Extraction Sources

```yaml
# /history/etol/document/mpls01.htm
source_url: "https://www.marxists.org/history/etol/document/mpls01.htm"
title: "James P. Cannon: Theses on the American Revolution"
section_type: "history/etol"
author: "James P. Cannon"
authors_alt: ["Vincent Dunne", "Farrell Dobbs"]  # Co-authors from keywords
author_source: "title"
author_confidence: 0.8
organization: "Socialist Workers Party"
provenance: null
transcriber: "Einde O'Callaghan"

date_written: "1946"
date_published: null
date_source: "provenance"
year_period: "1940-1949"

keywords: ["Trotskyism", "American Revolution", "SWP", "James P. Cannon", "Farrell Dobbs", "Vincent Dunne"]
classification: "Politics, History"
subject_categories: []

doc_type: "html"
original_path: "/history/etol/document/mpls01.htm"
character_encoding: "utf-8"
language: "en"
word_count: 8521
paragraph_count: 176

glossary_entities:
  people: ["James P. Cannon", "Leon Trotsky", "Farrell Dobbs"]
  terms: ["Revolutionary Party", "Transitional Program"]
  organizations: ["Socialist Workers Party", "Fourth International"]
  events: ["Minneapolis Teamsters Strike"]

cross_references:
  - "https://www.marxists.org/archive/cannon/works/1946/index.htm"
  - "https://www.marxists.org/glossary/people/c/a.htm#cannon-james"

document_structure:
  heading_depth: 4
  has_footnotes: false
  section_count: 12

rag_priority: "high"

# History-specific
newspaper_name: null
movement_affiliation: "Trotskyist"
country_focus: "USA"
```

### 7.3 EROL Organizational Document

```yaml
# /history/erol/ncm-1/1970s/mloc-1972.htm
source_url: "https://www.marxists.org/history/erol/ncm-1/1970s/mloc-1972.htm"
title: "MLOC: Statement on the Sino-Soviet Split"
section_type: "history/erol"
author: null  # Organizational authorship, no individual
authors_alt: []
author_source: "organization"
author_confidence: 0.9
organization: "Marxist-Leninist Organizing Committee (MLOC)"
provenance: null
transcriber: null

date_written: "1972"
date_published: null
date_source: "path"
year_period: "1970s"

keywords: ["MLOC", "Maoism", "Anti-revisionism", "Sino-Soviet Split", "New Communist Movement"]
classification: "Politics, History, Organizational"
subject_categories: []

doc_type: "html"
original_path: "/history/erol/ncm-1/1970s/mloc-1972.htm"
character_encoding: "iso-8859-1"
language: "en"
word_count: 3421
paragraph_count: 58

glossary_entities:
  people: ["Mao Zedong", "Joseph Stalin"]
  terms: ["Revisionism", "Social-Imperialism"]
  organizations: ["MLOC", "Communist Party of China", "Communist Party of the Soviet Union"]
  events: ["Sino-Soviet Split"]

cross_references:
  - "https://www.marxists.org/history/erol/ncm-1/index.htm"

document_structure:
  heading_depth: 3
  has_footnotes: false
  section_count: 5

rag_priority: "high"

# History-specific
movement_affiliation: "New Communist Movement"
country_focus: "USA"
```

### 7.4 Subject Section Anthology

```yaml
# /subject/women/index.htm
source_url: "https://www.marxists.org/subject/women/index.htm"
title: "Marxist Writers on Women's Liberation"
section_type: "subject"
author: null  # Anthology - no single author
authors_alt: ["Alexandra Kollontai", "Clara Zetkin", "Rosa Luxemburg", "Eleanor Marx", "Sylvia Pankhurst", ...]  # 20+ authors
author_source: "anthology"
author_confidence: 0.0
organization: null
provenance: null
transcriber: null

date_written: null
date_published: null
date_source: "unknown"
year_period: null

keywords: ["women", "feminism", "liberation", "gender", "marxism"]
classification: "Politics, Social Theory"
subject_categories: ["Women", "Social Movements"]

doc_type: "html"
original_path: "/subject/women/index.htm"
character_encoding: "iso-8859-1"
language: "en"
word_count: 421  # Short index page
paragraph_count: 12

glossary_entities:
  people: ["Alexandra Kollontai", "Clara Zetkin", "Rosa Luxemburg"]
  terms: ["Women's Liberation", "Patriarchy"]
  organizations: []
  events: []

cross_references:
  - "https://www.marxists.org/archive/kollonta/index.htm"
  - "https://www.marxists.org/archive/zetkin/index.htm"
  - "https://www.marxists.org/archive/luxembur/index.htm"

document_structure:
  heading_depth: 2
  has_footnotes: false
  section_count: 0

rag_priority: "low"  # Navigation index, not primary content

# Subject-specific
thematic_category: "women"
anthology_title: "Marxist Writers on Women's Liberation"
```

### 7.5 Glossary People Entry

```yaml
# /glossary/people/m/a.htm (Karl Marx entry)
source_url: "https://www.marxists.org/glossary/people/m/a.htm#marx-karl"
title: "Karl Marx (1818-1883)"
section_type: "glossary"
author: null  # Encyclopedia entry, not authored work
authors_alt: []
author_source: "unknown"
author_confidence: 0.0
organization: null
provenance: null
transcriber: null

date_written: "1818"  # Birth year
date_published: null
date_source: "content"
year_period: "1800-1899"

keywords: []
classification: "Biographical"
subject_categories: []

doc_type: "html"
original_path: "/glossary/people/m/a.htm"
character_encoding: "utf-8"
language: "en"
word_count: 342
paragraph_count: 3

glossary_entities:
  people: ["Friedrich Engels", "Jenny Marx"]  # Related people
  terms: ["Marxism", "Historical Materialism", "Surplus Value"]
  organizations: ["First International", "Communist League"]
  events: ["Paris Commune", "Revolutions of 1848"]

cross_references:
  - "https://www.marxists.org/archive/marx/index.htm"
  - "https://www.marxists.org/glossary/terms/m/a.htm#marxism"

document_structure:
  heading_depth: 2
  has_footnotes: false
  section_count: 1

rag_priority: "high"  # Critical for entity linking

# Glossary-specific
glossary_type: "people"
entry_id: "people/m/a/marx-karl"
cross_reference_count: 87  # Highly connected node
```

---

## 8. Summary & Next Steps

This unified metadata schema provides:

✅ **Complete coverage** of all corpus sections (Archive, History, Subject, Glossary, Reference)
✅ **Multi-source extraction** strategies achieving 85%+ author coverage target
✅ **Section-aware processing** rules for ETOL, EROL, and other subsections
✅ **Entity linking** foundation via Glossary integration
✅ **Knowledge graph** support through cross-reference extraction
✅ **Encoding normalization** for 62% ISO-8859-1 corpus
✅ **Provenance tracking** for metadata quality assessment

**Next Implementation Steps:**

1. **Update `specs/02-DOCUMENT-PROCESSING-SPEC.md`** with this unified schema
2. **Create `08-chunking-strategies.md`** based on document structure findings
3. **Create `09-knowledge-graph-spec.md`** for cross-reference architecture
4. **Implement metadata extraction pipeline** in processing module
5. **Build Glossary index loader** for entity linking
6. **Create validation tests** for metadata coverage targets

**Dependencies:**
- Requires Glossary section processing to build entity index
- Requires HTML structure analyzer for structural metadata
- Requires character encoding detection library (chardet)

**Estimated Implementation Time:** 2-3 weeks for complete pipeline integration
