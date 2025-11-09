# Document Processing Module Specification

**Version:** 2.0
**Status:** SPECIFICATION (Updated with Corpus Analysis Findings)
**Module:** `src/processing/`
**Dependencies:**
- Architecture Spec 1.0
- Unified Metadata Schema (`docs/corpus-analysis/06-metadata-unified-schema.md`)
- Section analyses 01-05 (`docs/corpus-analysis/`)

## Overview

Converts MIA archive files (HTML, PDF) to markdown with extracted metadata. Filters for English content and handles encoding issues gracefully.

**Updates from Corpus Analysis (v2.0):**
- Comprehensive metadata schema with 5 layers (core, authorship, temporal, technical, semantic)
- Section-aware processing (Archive, ETOL, EROL, Subject, Glossary, Reference)
- Multi-source author extraction (85%+ coverage target)
- Character encoding normalization (62% ISO-8859-1 → UTF-8)
- Entity linking via Glossary integration
- CSS class-based semantic structure extraction

## Responsibilities

1. HTML → Markdown conversion with structure preservation
2. PDF → Markdown conversion with text extraction
3. Metadata extraction from documents and paths
4. Language filtering (English only)
5. Content deduplication via hashing
6. Progress tracking and error recovery

## Module Structure

```
src/processing/
├── __init__.py
├── html_processor.py       # HTML conversion logic
├── pdf_processor.py        # PDF conversion logic
├── metadata_extractor.py   # Metadata extraction
├── language_filter.py      # Language detection
└── processor_main.py       # Orchestration & CLI
```

## Data Structures

### DocumentMetadata (dataclass)

**IMPORTANT**: See `docs/corpus-analysis/06-metadata-unified-schema.md` for complete field documentation and extraction strategies.

```python
@dataclass
class DocumentMetadata:
    """
    Unified metadata for all MIA corpus documents.

    Organized into 5 layers:
    1. Core identification (required)
    2. Authorship & provenance (best-effort extraction)
    3. Temporal & classification (extracted or inferred)
    4. Technical & processing (always populated)
    5. Semantic enrichment (from Glossary + cross-references)
    """

    # ===== LAYER 1: Core Identification (Required) =====
    source_url: str              # Reconstructed MIA URL
    title: str                   # Document title (fallback: filename)
    content_hash: str            # SHA256 first 16 chars (deduplication)
    section_type: Literal["archive", "history/etol", "history/erol", "history/other",
                           "subject", "glossary", "reference", "ebooks"]

    # ===== LAYER 2: Authorship & Provenance =====
    author: Optional[str]        # Primary author (canonical name from Glossary if matched)
    authors_alt: List[str]       # Alternative author attributions (co-authors, editors)
    author_source: str           # How extracted: "path" | "meta" | "title" | "keywords" | "inferred" | "unknown"
    author_confidence: float     # 0.0-1.0 confidence in author extraction

    organization: Optional[str]  # For EROL/organizational docs (e.g., "MLOC", "RCP-USA")
    provenance: Optional[str]    # Publication source (e.g., "First published in Pravda, 1917")
    transcriber: Optional[str]   # Archivist/transcriber (from meta tag, often misattributed as author)

    # ===== LAYER 3: Temporal & Classification =====
    date_written: Optional[str]  # Original composition date (YYYY, YYYY-MM, YYYY-MM-DD)
    date_published: Optional[str] # First publication date
    date_source: str             # How extracted: "path" | "meta" | "title" | "provenance" | "unknown"
    year_period: Optional[str]   # Period classification (e.g., "1900-1949")

    keywords: List[str]          # Keywords from meta tags or inferred
    classification: Optional[str] # MIA classification tag (e.g., "Politics, History")
    subject_categories: List[str] # Subject section categories if cross-referenced

    # ===== LAYER 4: Technical & Processing =====
    doc_type: Literal["html", "pdf"]
    original_path: str           # Path in source archive
    character_encoding: str      # Detected encoding (utf-8, iso-8859-1, windows-1252, etc.)
    language: str                # ISO 639-1 code (default: "en")
    word_count: int              # Total words in markdown
    paragraph_count: int         # Total paragraphs in document

    processed_date: str          # ISO 8601 timestamp
    processor_version: str       # Pipeline version (semantic versioning)

    # ===== LAYER 5: Semantic Enrichment =====
    glossary_entities: Dict[str, List[str]]  # Linked entities: {"people": [...], "terms": [...]}
    cross_references: List[str]  # Internal MIA links (source_url format)
    document_structure: Dict[str, Any]  # {"heading_depth": 4, "has_footnotes": True, ...}
    rag_priority: Literal["high", "medium", "low"]  # Processing priority

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

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict"""
        pass

    def to_yaml_frontmatter(self) -> str:
        """Generate YAML frontmatter for markdown file"""
        pass
```

**Coverage Targets (from Corpus Analysis):**

| Section | Author Coverage | Date Coverage | Keywords Coverage |
|---------|----------------|---------------|-------------------|
| Archive | 100% (path) | 78% (path+title) | 38% (meta) |
| ETOL | 85% (title+keywords) | 65% (path+provenance) | 90% (meta) |
| EROL | 95% (org from title) | 80% (path+filename) | 85% (meta) |
| Subject | 48% (meta+cross-ref) | 45% (meta+cross-ref) | 42% (meta) |
| Glossary | 100% (structure) | 90% (entry content) | N/A |
| Reference | 100% (path) | 55% (path+meta) | 30% (meta) |

### ProcessingStats (dataclass)

```python
@dataclass
class ProcessingStats:
    """Statistics for processing run"""
    html_processed: int = 0
    pdf_processed: int = 0
    skipped_non_english: int = 0
    errors: int = 0
    total_words: int = 0
    start_time: float = field(default_factory=time.time)
    
    def elapsed_time(self) -> float:
        """Get elapsed seconds"""
        pass
    
    def to_dict(self) -> dict:
        """Serialize for reporting"""
        pass
```

## Core Classes

### HTMLProcessor

```python
class HTMLProcessor:
    """Convert HTML files to markdown"""
    
    def __init__(self):
        self.parser = 'html.parser'  # BeautifulSoup parser
    
    def process(self, html_path: Path) -> Optional[tuple[str, DocumentMetadata]]:
        """
        Process single HTML file
        
        Args:
            html_path: Path to HTML file in archive
            
        Returns:
            (markdown_content, metadata) or None on failure
            
        Raises:
            ProcessingError: On unrecoverable errors
        """
        pass
    
    def _extract_metadata(self, soup: BeautifulSoup, path: Path) -> DocumentMetadata:
        """Extract metadata from HTML and path"""
        pass
    
    def _clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Remove navigation, scripts, styles"""
        pass
    
    def _convert_to_markdown(self, soup: BeautifulSoup) -> str:
        """Convert cleaned HTML to markdown"""
        pass
```

### PDFProcessor

```python
class PDFProcessor:
    """Convert PDF files to markdown"""
    
    def __init__(self):
        self.timeout = 300  # 5 minutes per PDF max
    
    def process(self, pdf_path: Path) -> Optional[tuple[str, DocumentMetadata]]:
        """
        Process single PDF file
        
        Args:
            pdf_path: Path to PDF file in archive
            
        Returns:
            (markdown_content, metadata) or None on failure
            
        Raises:
            ProcessingError: On unrecoverable errors
        """
        pass
    
    def _extract_metadata(self, pdf_path: Path) -> DocumentMetadata:
        """Extract metadata from PDF and path"""
        pass
    
    def _infer_author_from_path(self, path: Path) -> Optional[str]:
        """Infer author from archive directory structure"""
        pass
```

### MetadataExtractor

```python
class MetadataExtractor:
    """
    Extract and infer metadata from various sources.

    Implements multi-source extraction strategies from corpus analysis
    to achieve 85%+ author coverage and 60%+ date coverage targets.
    """

    def __init__(self, glossary_index: Optional[dict] = None):
        """
        Args:
            glossary_index: Pre-loaded Glossary index for entity linking
                Structure: {
                    "people": {"marx-karl": {"canonical_name": "Karl Marx", ...}, ...},
                    "terms": {...},
                    ...
                }
        """
        self.glossary = glossary_index or {}

    def extract_from_html(self, soup: BeautifulSoup, path: Path, section: str) -> DocumentMetadata:
        """
        Extract complete metadata from HTML with section-aware strategies.

        Args:
            soup: Parsed BeautifulSoup object
            path: Path to HTML file in archive
            section: Section type ("archive", "history/etol", "history/erol", etc.)

        Returns:
            DocumentMetadata with all extractable fields populated
        """
        pass

    def extract_from_pdf(self, pdf_path: Path, section: str) -> DocumentMetadata:
        """Extract from PDF metadata and path"""
        pass

    # ===== AUTHOR EXTRACTION (Multi-Source Strategy) =====

    def extract_author(self, soup: BeautifulSoup, path: Path, section: str) -> Tuple[Optional[str], str, float]:
        """
        Multi-source author extraction with confidence scoring.

        Extraction order (by precedence):
        1. Path-based (Archive, Reference, ETOL writers) - 100% confidence
        2. Title parsing (ETOL documents) - 80% confidence
        3. Keywords (ETOL/EROL) - 70% confidence
        4. Organization extraction (EROL) - 90% confidence
        5. Meta tag (fallback, often transcriber) - 60% confidence
        6. Content patterns ("By [Author]") - 50% confidence

        Returns:
            (author_name, source, confidence)
            where source is one of: "path", "title", "keywords", "meta", "content", "unknown"

        Examples:
            Archive: ("/archive/marx/...", "path", 1.0) → "Karl Marx"
            ETOL doc: ("James P. Cannon: Theses...", "title", 0.8) → "James P. Cannon"
            EROL doc: (None but "MLOC" in keywords, "organization", 0.9) → org field populated
        """
        # Strategy 1: Path-based (100% accuracy for Archive/Reference/ETOL writers)
        if section == "archive" and "/archive/" in str(path):
            return self._extract_author_from_archive_path(path)
        elif section == "reference" and "/reference/archive/" in str(path):
            return self._extract_author_from_reference_path(path)
        elif section == "history/etol" and "/writers/" in str(path):
            return self._extract_author_from_etol_writers_path(path)

        # Strategy 2: Title parsing (ETOL pattern: "Author: Title")
        title = self.extract_title(soup)
        if title and ':' in title:
            potential_author = title.split(':')[0].strip()
            if self._is_valid_person_name(potential_author):
                canonical = self._normalize_author_name(potential_author)
                return (canonical, "title", 0.8)

        # Strategy 3: Keywords (ETOL/EROL - often list authors)
        keywords = self._extract_keywords(soup)
        for keyword in keywords:
            if self._is_valid_person_name(keyword):
                canonical = self._normalize_author_name(keyword)
                return (canonical, "keywords", 0.7)

        # Strategy 4: EROL organization extraction
        if section == "history/erol":
            org = self._extract_organization(soup, title)
            if org:
                return (None, "organization", 0.9)  # Organization goes in separate field

        # Strategy 5: Meta tag (often transcriber in ETOL, use cautiously)
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            author_name = meta_author['content']
            # Check if it's a known transcriber (ETOL pattern)
            if author_name not in self.TRANSCRIBER_NAMES:
                canonical = self._normalize_author_name(author_name)
                return (canonical, "meta", 0.6)
            else:
                # Store as transcriber, continue to next strategy
                self.transcriber = author_name

        # Strategy 6: Content patterns ("By [Author]")
        first_para = soup.find('p', class_='fst') or soup.find('p')
        if first_para:
            import re
            text = first_para.get_text()
            if m := re.match(r'^By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text):
                potential_author = m.group(1)
                canonical = self._normalize_author_name(potential_author)
                return (canonical, "content", 0.5)

        # Fallback: Unknown
        return (None, "unknown", 0.0)

    def _extract_author_from_archive_path(self, path: Path) -> Tuple[str, str, float]:
        """Extract author from Archive section path (100% accurate)"""
        import re
        if m := re.search(r'/archive/([^/]+)/', str(path)):
            author_slug = m.group(1)
            canonical_name = self._normalize_author_name(author_slug)
            return (canonical_name, "path", 1.0)
        return (None, "unknown", 0.0)

    def _normalize_author_name(self, raw_name: str) -> str:
        """
        Normalize author name to canonical Glossary form.

        Strategies:
        1. Exact match in Glossary people index
        2. Fuzzy match on surname
        3. Alias matching (e.g., "Trotsky" → "Leon Trotsky")
        4. Title case conversion as fallback

        Examples:
            "marx" → "Karl Marx"
            "K. Marx" → "Karl Marx"
            "Vladimir Ilyich Lenin" → "Vladimir Lenin"
        """
        if not self.glossary or "people" not in self.glossary:
            # Fallback: basic cleanup
            return raw_name.replace('-', ' ').title()

        # TODO: Implement Glossary fuzzy matching
        # For now, basic cleanup
        return raw_name.replace('-', ' ').title()

    # ===== DATE EXTRACTION (Multi-Source Strategy) =====

    def extract_dates(self, soup: BeautifulSoup, path: Path, section: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Multi-source date extraction.

        Returns:
            (date_written, date_published, source)

        Extraction order:
        1. Year from path (Archive /works/YYYY/, EROL /YYYYs/)
        2. Date from title (e.g., "Letter (March 1867)")
        3. Meta date tag
        4. Provenance info box ("First published: YYYY")
        """
        import re

        # Strategy 1: Year from path
        if "/works/" in str(path):
            if m := re.search(r'/works/(\d{4})(?:-[a-z]\d+)?/', str(path)):
                year = m.group(1)
                return (year, None, "path")

        if section == "history/erol" and re.search(r'/(\d{4})s?/', str(path)):
            if m := re.search(r'/(\d{4})s?/', str(path)):
                decade = m.group(1)
                return (f"{decade}s", None, "path")
            if m := re.search(r'-(\d{4})\.htm', str(path)):
                year = m.group(1)
                return (year, None, "path")

        # Strategy 2: Date from title
        title = self.extract_title(soup)
        if title and (m := re.search(r'\(([A-Za-z\s]*\d{4}(?:-\d{4})?)\)', title)):
            date_str = m.group(1)
            return (date_str, None, "title")

        # Strategy 3: Meta date tag
        meta_date = soup.find('meta', attrs={'name': 'date'})
        if meta_date and meta_date.get('content'):
            return (meta_date['content'], None, "meta")

        # Strategy 4: Provenance info box
        info_box = soup.find(class_='info') or soup.find(class_='information')
        if info_box:
            text = info_box.get_text()
            if m := re.search(r'(?:First published|Written|Published):\s*([A-Za-z\s]*\d{4})', text):
                date_str = m.group(1)
                return (None, date_str, "provenance")  # This is publication date

        return (None, None, "unknown")

    # ===== HELPER METHODS =====

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tag"""
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta and keywords_meta.get('content'):
            return [k.strip() for k in keywords_meta['content'].split(',') if k.strip()]
        return []

    def _is_valid_person_name(self, name: str) -> bool:
        """Heuristic check if string is likely a person name (not organization/keyword)"""
        # Check if it's title case and has spaces (typical name pattern)
        return bool(re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', name))

    def _extract_organization(self, soup: BeautifulSoup, title: str) -> Optional[str]:
        """Extract organization from EROL documents (title or keywords)"""
        import re
        # Pattern: "MLOC: Statement..." → "MLOC"
        if m := re.match(r'^([A-Z]{2,}):?\s', title):
            return m.group(1)
        # Check keywords for acronyms
        keywords = self._extract_keywords(soup)
        for keyword in keywords:
            if keyword.isupper() and len(keyword) <= 8:
                return keyword
        return None

    def construct_source_url(self, path: Path, archive_root: Path) -> str:
        """Convert local path to marxists.org URL"""
        pass

    def extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract title with fallback strategy:
        1. <title> tag
        2. <h1> tag
        3. First header
        4. Filename
        """
        pass

    # Class constant for transcriber names
    TRANSCRIBER_NAMES = [
        "Einde O'Callaghan", "David Walters", "Sally Ryan", "Arie Bober",
        # Add more as discovered
    ]
```

### LanguageFilter

```python
class LanguageFilter:
    """Filter documents by language"""
    
    # Non-English directory patterns
    NON_ENGLISH_DIRS = [
        '/chinese/', '/deutsch/', '/espanol/', '/francais/',
        '/italiano/', '/japanese/', '/polski/', '/portugues/',
        '/russian/', '/turkce/', '/arabic/', '/svenska/',
        '/catala/', '/greek/', '/korean/', '/farsi/', '/hindi/'
    ]
    
    def is_english(self, path: Path) -> bool:
        """
        Heuristic check if content is English
        
        Strategy:
        1. Check path for non-English directory markers
        2. English-heavy sections (archive, history, reference)
        3. Default to True (conservative - process and let user filter)
        
        Returns:
            True if likely English, False otherwise
        """
        pass
    
    def detect_language_from_content(self, content: str) -> str:
        """
        Optional: Detect language from content
        
        NOTE: Not implemented in v1.0 - too slow
        Future: Could use langdetect library
        """
        pass
```

### DocumentProcessor (Main Orchestrator)

```python
class DocumentProcessor:
    """Main processing orchestrator"""
    
    def __init__(self, 
                 archive_root: Path,
                 output_dir: Path,
                 skip_pdfs: bool = False,
                 parallel_workers: int = 4):
        self.archive_root = archive_root
        self.output_dir = output_dir
        self.skip_pdfs = skip_pdfs
        self.parallel_workers = parallel_workers
        
        self.html_processor = HTMLProcessor()
        self.pdf_processor = PDFProcessor()
        self.language_filter = LanguageFilter()
        self.metadata_extractor = MetadataExtractor()
        
        self.stats = ProcessingStats()
        
        # Output directories
        self.markdown_dir = output_dir / "markdown"
        self.metadata_dir = output_dir / "metadata"
        self.json_dir = output_dir / "json"
        
        self._setup_output_dirs()
    
    def process_archive(self) -> ProcessingStats:
        """
        Process entire archive
        
        Workflow:
        1. Discover all HTML/PDF files
        2. Filter by language
        3. Process in parallel (HTML) or serial (PDF)
        4. Save markdown + metadata
        5. Generate processing report
        
        Returns:
            ProcessingStats with final counts
        """
        pass
    
    def _discover_files(self) -> tuple[List[Path], List[Path]]:
        """Find all HTML and PDF files in archive"""
        pass
    
    def _process_html_batch(self, html_files: List[Path]) -> None:
        """Process HTML files with multiprocessing"""
        pass
    
    def _process_pdf_batch(self, pdf_files: List[Path]) -> None:
        """Process PDF files serially (OCR is CPU-bound)"""
        pass
    
    def _save_document(self, content: str, metadata: DocumentMetadata) -> None:
        """Save markdown with frontmatter and metadata JSON"""
        pass
    
    def _generate_report(self) -> None:
        """Generate processing_report.json"""
        pass
```

## Algorithms

### HTML Cleaning Algorithm

```python
def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove non-content elements
    
    Strategy:
    1. Remove: <script>, <style>, <nav>, <header>, <footer>
    2. Remove: class="navigation", id="sidebar"
    3. Remove: Empty paragraphs and divs
    4. Preserve: Main content area (usually <div id="main">)
    5. Preserve: All semantic HTML (headings, lists, blockquotes)
    
    Returns:
        Cleaned BeautifulSoup object
    """
    # Remove scripts and styles
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Remove navigation classes
    for element in soup.find_all(class_=['nav', 'navigation', 'menu', 'sidebar']):
        element.decompose()
    
    # Remove specific IDs
    for id_name in ['navigation', 'sidebar', 'header', 'footer']:
        element = soup.find(id=id_name)
        if element:
            element.decompose()
    
    return soup
```

### Author Inference Algorithm

```python
def infer_author(path: Path, authors_data: dict) -> Optional[str]:
    """
    Infer author from path structure
    
    Path patterns:
    - /archive/{author-slug}/... → Look up in authors_data
    - /history/etol/writers/{author-slug}/... → ETOLarchive writers
    - No clear author → None
    
    Examples:
        /archive/marx/capital/... → "Karl Marx"
        /archive/lenin/1917/... → "Vladimir Lenin"
        /history/etol/writers/abern/... → "Martin Abern"
        /reference/archive/hegel/... → "Georg Wilhelm Friedrich Hegel"
    """
    path_str = str(path).lower()
    
    # Check /archive/ pattern
    if '/archive/' in path_str:
        parts = path_str.split('/archive/')[-1].split('/')
        if parts:
            author_slug = parts[0]
            return lookup_author(author_slug, authors_data)
    
    # Check /history/etol/writers/ pattern
    if '/history/etol/writers/' in path_str:
        parts = path_str.split('/history/etol/writers/')[-1].split('/')
        if parts:
            author_slug = parts[0]
            return lookup_author(author_slug, authors_data)
    
    return None
```

### Content Hash Generation

```python
def generate_content_hash(content: str) -> str:
    """
    Generate deterministic hash for deduplication
    
    Strategy:
    - Use SHA256 for collision resistance
    - Take first 16 chars for readability
    - Hash the markdown content (not raw HTML/PDF)
    
    Returns:
        16-character hex string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
```

## File Formats

### Output Markdown Format

```markdown
---
title: The Communist Manifesto
author: Karl Marx and Friedrich Engels
source_url: https://www.marxists.org/archive/marx/works/1848/communist-manifesto/
date: 1848
language: en
doc_type: html
word_count: 12345
processed_date: 2025-11-07T10:30:00Z
---

# The Communist Manifesto

A specter is haunting Europe—the specter of communism...
```

### Metadata JSON Format

```json
{
  "source_url": "https://www.marxists.org/archive/marx/works/1848/communist-manifesto/",
  "title": "The Communist Manifesto",
  "author": "Karl Marx and Friedrich Engels",
  "date": "1848",
  "language": "en",
  "doc_type": "html",
  "original_path": "/archive/marx/works/1848/communist-manifesto/ch01.htm",
  "processed_date": "2025-11-07T10:30:00Z",
  "content_hash": "a1b2c3d4e5f6g7h8",
  "word_count": 12345
}
```

## Character Encoding Normalization

### Encoding Distribution (from Corpus Analysis)

| Encoding | Archive | ETOL | EROL | Subject | Reference | Overall |
|----------|---------|------|------|---------|-----------|---------|
| ISO-8859-1 | 62% | 55% | 48% | 89% | 60% | ~60% |
| UTF-8 | 21% | 30% | 40% | 4% | 25% | ~25% |
| Windows-1252 | 11% | 10% | 8% | 1% | 10% | ~10% |
| Unspecified | 6% | 5% | 4% | 6% | 5% | ~5% |

**Critical Finding**: ~60% of corpus is ISO-8859-1 encoded and requires conversion to UTF-8 for consistent processing.

### Encoding Normalization Strategy

```python
def normalize_encoding(raw_html: bytes, declared_encoding: Optional[str]) -> Tuple[str, str]:
    """
    Normalize all content to UTF-8.

    Strategy:
    1. Try declared encoding from meta tag
    2. Detect using chardet if undeclared
    3. Fallback sequence: UTF-8 → ISO-8859-1 → Windows-1252 → Latin-1
    4. Record final encoding in metadata.character_encoding

    Returns:
        (decoded_content, final_encoding)
    """
    # Try declared encoding first
    if declared_encoding:
        try:
            return (raw_html.decode(declared_encoding), declared_encoding)
        except UnicodeDecodeError:
            pass  # Continue to detection

    # Detect encoding
    import chardet
    detected = chardet.detect(raw_html)

    # Try detected encoding if high confidence
    if detected['confidence'] > 0.7:
        try:
            return (raw_html.decode(detected['encoding']), detected['encoding'])
        except UnicodeDecodeError:
            pass

    # Fallback sequence
    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']:
        try:
            return (raw_html.decode(encoding, errors='replace'), encoding)
        except UnicodeDecodeError:
            continue

    # Ultimate fallback: UTF-8 with replacement characters
    return (raw_html.decode('utf-8', errors='replace'), 'utf-8-fallback')
```

## CSS Class Patterns and Semantic Markup

### Common CSS Classes (from Corpus Analysis)

**Archive Section** (53-59% presence):

| Class | Frequency | Purpose | Processing Implication |
|-------|-----------|---------|------------------------|
| `.fst` | 53% | First paragraph styling | Start of main content (boilerplate removal marker) |
| `.info` | 59% | Publication provenance | Extract provenance metadata |
| `.quoteb` | 19% | Block quotes | Preserve as markdown blockquotes |
| `.enote` | 7% | Footnote citations | Extract footnote structure |

**ETOL Section** (87-97% presence):

| Class | Frequency | Purpose | Processing Implication |
|-------|-----------|---------|------------------------|
| `.fst` | 87% | First paragraph (drop cap) | Very reliable content start marker |
| `.footer` | 97% | Footer navigation | Remove as boilerplate |
| `.linkback` | 83% | Navigation links | Remove as boilerplate |
| `.info` | 50% | Publication metadata | Extract provenance |

**EROL Section** (variable presence):

| Class | Frequency | Purpose | Processing Implication |
|-------|-----------|---------|------------------------|
| `.fst` | 35% | First paragraph | Less reliable than ETOL/Archive |
| `.footer` | 60% | Footer navigation | Remove as boilerplate |
| `.info` | 40% | Publication metadata | Extract when present |

### HTML Cleaning Strategy (Updated)

```python
def clean_html(soup: BeautifulSoup, section: str) -> BeautifulSoup:
    """
    Remove non-content elements using corpus-analyzed CSS patterns.

    Strategy:
    1. Remove: <script>, <style>, <nav>, <header>, <footer>
    2. Remove: class="footer", class="linkback" (navigation boilerplate)
    3. Preserve: class="fst" (first paragraph marker)
    4. Preserve: class="info" (extract metadata first, then optionally remove)
    5. Preserve: class="quoteb", class="enote" (semantic structure)
    6. Section-specific: EROL h3 handling (90% use h3 as title, not h1)

    Returns:
        Cleaned BeautifulSoup object with semantic structure preserved
    """
    # Remove scripts, styles, navigation elements
    for element in soup(['script', 'style', 'nav', 'header']):
        element.decompose()

    # Remove footer class (97% in ETOL, 60% in EROL - reliable boilerplate)
    for element in soup.find_all(class_='footer'):
        element.decompose()

    # Remove linkback class (83% in ETOL - navigation)
    for element in soup.find_all(class_='linkback'):
        element.decompose()

    # Extract metadata from .info before potentially removing
    info_boxes = soup.find_all(class_=['info', 'information'])
    for info_box in info_boxes:
        # Extract provenance metadata
        extract_provenance(info_box)
        # Optionally keep for content (some have substantive notes)

    # Section-specific handling
    if section == "history/erol":
        # EROL: 90% use h3 as title (not h1)
        # Promote first h3 to h1 for consistent structure
        first_h3 = soup.find('h3')
        if first_h3 and not soup.find('h1'):
            first_h3.name = 'h1'

    # Preserve semantic classes: .fst, .quoteb, .enote
    # These provide structural information for chunking

    return soup
```

## Error Handling

### Error Categories

1. **Encoding Errors:** Try utf-8, latin-1, cp1252 fallbacks with chardet detection
2. **Malformed HTML:** Use lenient parser, log warning
3. **Corrupt PDFs:** Skip file, log error
4. **Missing Metadata:** Use fallback values (title from filename, etc.)
5. **Disk Full:** Fail gracefully with clear message
6. **Section Detection Failure:** Infer from path, default to "archive" as fallback

### Retry Logic

```python
@retry(max_attempts=3, exceptions=(UnicodeDecodeError,))
def read_file_with_retry(path: Path) -> str:
    """Try multiple encodings"""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ProcessingError(f"Cannot decode {path}")
```

## Configuration

### CLI Interface

```bash
python processor_main.py \
    --archive /path/to/archive \
    --output ~/marxists-processed \
    --workers 4 \
    --skip-pdfs \
    --download-json
```

### CLI Arguments

```python
parser = argparse.ArgumentParser()
parser.add_argument('--archive', type=Path, required=True,
                    help='Path to MIA archive directory')
parser.add_argument('--output', type=Path, default=Path('~/marxists-processed'),
                    help='Output directory')
parser.add_argument('--workers', type=int, default=4,
                    help='Parallel workers for HTML processing')
parser.add_argument('--skip-pdfs', action='store_true',
                    help='Skip PDF processing (faster)')
parser.add_argument('--download-json', action='store_true',
                    help='Download MIA JSON metadata first')
parser.add_argument('--verbose', action='store_true',
                    help='Verbose logging')
```

## Testing Requirements

### Unit Tests

- [ ] `test_html_processor` - Test HTML→MD conversion
- [ ] `test_pdf_processor` - Test PDF→MD conversion
- [ ] `test_metadata_extraction` - Test all metadata extraction paths
- [ ] `test_language_filter` - Test language detection accuracy
- [ ] `test_author_inference` - Test author extraction from paths
- [ ] `test_url_reconstruction` - Test source URL generation
- [ ] `test_hash_generation` - Test deterministic hashing

### Integration Tests

- [ ] Process sample archive (100 files)
- [ ] Verify all output files created
- [ ] Verify metadata completeness
- [ ] Verify no data loss in conversion

### Test Fixtures

```
tests/fixtures/
├── sample_html/
│   ├── marx_manifesto.htm
│   ├── lenin_state.html
│   └── luxemburg_mass_strike.htm
├── sample_pdf/
│   ├── capital_vol1_ch1.pdf
│   └── grundrisse_excerpt.pdf
└── expected_output/
    ├── marx_manifesto.md
    └── marx_manifesto_meta.json
```

## Performance Requirements

- **HTML Processing:** ≥100 files/minute (with 4 workers)
- **PDF Processing:** ≥10 files/minute (serial)
- **Memory Usage:** <2GB RSS for HTML, <4GB for PDFs
- **Error Rate:** <1% for HTML, <5% for PDFs

## Dependencies

```txt
# requirements.txt for this module
beautifulsoup4>=4.12.0
markdownify>=0.11.6
pymupdf4llm>=0.0.10
lxml>=4.9.0
requests>=2.31.0  # For JSON metadata download
```

## Acceptance Criteria

**Updated based on corpus analysis (v2.0):**

### File Processing

- [ ] Process 55,753 HTML files (46GB English corpus) without crashing
  - Archive: 15,637 files (4.3GB)
  - History: 33,190 files (33GB: 12,218 ETOL + 8,184 EROL + 3,379 Other)
  - Subject: 2,259 files (8.9GB)
  - Glossary: 685 files (62MB)
  - Reference: 4,867 files (460MB Git-LFS)
- [ ] Process PDFs (optional, lower priority)
- [ ] Generate valid YAML frontmatter for all documents
- [ ] Resume processing after interruption (via skip existing files)

### Metadata Coverage Targets (from Corpus Analysis)

- [ ] **Author Extraction**:
  - Archive: 100% (path-based, high confidence)
  - ETOL: ≥85% (multi-source: title + keywords)
  - EROL: ≥95% (organization from title/keywords)
  - Subject: ≥48% (meta + cross-reference)
  - Glossary: 100% (structured entries)
  - Reference: 100% (path-based)
  - **Overall target: ≥85% coverage**

- [ ] **Date Extraction**:
  - Archive: ≥78% (path + title)
  - ETOL: ≥65% (path + provenance)
  - EROL: ≥80% (path + filename)
  - Subject: ≥45% (meta + cross-reference)
  - Glossary: ≥90% (entry content)
  - Reference: ≥55% (path + meta)
  - **Overall target: ≥60% coverage**

- [ ] **Keywords Extraction**:
  - ETOL: ≥90% (meta tags extensive)
  - EROL: ≥85% (meta tags)
  - Archive: ≥38% (meta tags)
  - Subject: ≥42% (meta tags)
  - **Overall target: ≥50% coverage**

- [ ] Extract title for 100% of documents (with filename fallback)

### Character Encoding

- [ ] Normalize 60% ISO-8859-1 content to UTF-8
- [ ] Handle 25% UTF-8 content (no conversion needed)
- [ ] Handle 10% Windows-1252 content with conversion
- [ ] Detect and convert 5% unspecified encodings
- [ ] Record final encoding in metadata.character_encoding for all docs

### Language Filtering

- [ ] Filter non-English with ≥95% accuracy (path-based heuristics)
- [ ] Default to processing (conservative - let user filter later)

### Quality & Performance

- [ ] Generate unique hashes (no collisions in test set)
- [ ] Complete Archive section (15,637 files) in <2 hours (benchmark)
- [ ] Generate comprehensive processing report with section-level statistics
- [ ] Handle encoding errors gracefully (fallback to replacement characters)

### Section-Specific Requirements

- [ ] Archive: Detect work collections, chapter numbers, letter recipients
- [ ] ETOL: Distinguish transcribers from authors, extract newspaper names/issues
- [ ] EROL: Extract organizational authorship, handle h3-as-title pattern
- [ ] Subject: Extract thematic categories, handle Peking Review periodicals
- [ ] Glossary: Classify entry types (people/terms/orgs/events/periodicals/places)
- [ ] Reference: Handle 100% Git-LFS storage (verify `git lfs pull` before processing)

### Semantic Enrichment

- [ ] Extract cross-references (internal MIA links) for knowledge graph
- [ ] Extract document structure metrics (heading depth, footnote count, etc.)
- [ ] Assign RAG priority (high/medium/low) based on document type
- [ ] Populate section-specific fields (work_collection, newspaper_name, etc.)

## Implementation Notes

### Optimization Opportunities

1. **Multiprocessing:** Use `multiprocessing.Pool` for HTML
2. **Caching:** Skip already-processed files (check by hash)
3. **Progress Tracking:** Use `tqdm` for user feedback
4. **Batch Writes:** Buffer metadata writes to reduce I/O

### Known Limitations

1. **PDF OCR Quality:** Pre-1990 scans may have errors
2. **Author Extraction:** Only ~70% accurate due to irregular paths
3. **Date Extraction:** Often missing or inconsistent format
4. **Mathematical Notation:** LaTeX/equations may not convert well

### Future Enhancements

- Language detection via `langdetect` library
- Better date parsing with `dateutil`
- Table preservation in PDFs
- Image extraction and captioning
- Cross-document reference detection

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |

---

**Implementation Priority:** HIGH (blocking for all downstream modules)
