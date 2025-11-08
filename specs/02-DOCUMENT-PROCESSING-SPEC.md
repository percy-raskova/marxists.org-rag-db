# Document Processing Module Specification

**Version:** 1.0  
**Status:** SPECIFICATION  
**Module:** `src/processing/`  
**Dependencies:** Architecture Spec 1.0

## Overview

Converts MIA archive files (HTML, PDF) to markdown with extracted metadata. Filters for English content and handles encoding issues gracefully.

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

```python
@dataclass
class DocumentMetadata:
    """Complete metadata for a processed document"""
    source_url: str              # Reconstructed MIA URL
    title: str                   # Document title
    author: Optional[str]        # Extracted or inferred author
    date: Optional[str]          # Publication/writing date
    language: str                # ISO 639-1 code (default: "en")
    doc_type: str                # "html" or "pdf"
    original_path: str           # Path in source archive
    processed_date: str          # ISO 8601 timestamp
    content_hash: str            # SHA256 first 16 chars
    word_count: int              # Total words in markdown
    chunk_count: Optional[int]   # To be filled by ingestion
    
    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict"""
        pass
    
    def to_yaml_frontmatter(self) -> str:
        """Generate YAML frontmatter for markdown file"""
        pass
```

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
    """Extract and infer metadata from various sources"""
    
    def __init__(self, authors_json: Optional[dict] = None):
        self.authors_data = authors_json or {}
    
    def extract_from_html(self, soup: BeautifulSoup, path: Path) -> DocumentMetadata:
        """Extract from HTML meta tags and structure"""
        pass
    
    def extract_from_pdf(self, pdf_path: Path) -> DocumentMetadata:
        """Extract from PDF metadata and path"""
        pass
    
    def infer_author(self, path: Path) -> Optional[str]:
        """
        Infer author from path structure
        
        Examples:
            /archive/marx/... → "Karl Marx"
            /archive/lenin/... → "Vladimir Lenin"
        """
        pass
    
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
    
    def extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract date from:
        1. <meta name="date"> tag
        2. Document structure patterns
        3. Path analysis
        """
        pass
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

## Error Handling

### Error Categories

1. **Encoding Errors:** Try utf-8, latin-1, cp1252 fallbacks
2. **Malformed HTML:** Use lenient parser, log warning
3. **Corrupt PDFs:** Skip file, log error
4. **Missing Metadata:** Use fallback values (title from filename, etc.)
5. **Disk Full:** Fail gracefully with clear message

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

- [ ] Process 126,000 HTML pages without crashing
- [ ] Process 38,000 PDFs without crashing
- [ ] Generate valid YAML frontmatter for all documents
- [ ] Extract author for ≥70% of documents
- [ ] Extract title for 100% of documents
- [ ] Filter non-English with ≥95% accuracy
- [ ] Generate unique hashes (no collisions in test set)
- [ ] Complete processing in <8 hours
- [ ] Generate comprehensive processing report
- [ ] Handle encoding errors gracefully
- [ ] Resume processing after interruption (via skip existing files)

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
