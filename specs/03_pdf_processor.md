# Component Specification: PDF to Markdown Processor

**Version:** 1.0  
**Status:** Ready for Implementation  
**Estimated Complexity:** High  
**Estimated Time:** 3-4 hours  

## 1. Objective

Convert MIA PDF files (scanned revolutionary publications, historical documents) to Markdown optimized for RAG ingestion while handling OCR, multiple columns, and image-based text.

## 2. Scope

**In Scope:**
- PDF text extraction (including OCR when needed)
- Markdown conversion with structure preservation
- Metadata extraction from PDF properties and filenames
- Multi-column layout handling
- Language detection
- Quality assessment

**Out of Scope:**
- HTML processing
- Image extraction/processing
- Vector embedding
- PDF editing/manipulation

## 3. Technical Requirements

### 3.1 System Requirements
- Python 3.9+
- 8GB RAM minimum (OCR is memory-intensive)
- CPU: Multi-core recommended for parallel processing

### 3.2 Dependencies
```python
pymupdf4llm>=0.0.10   # PDF to Markdown conversion
PyMuPDF>=1.23.0       # PDF manipulation
```

**Note:** `pymupdf4llm` handles OCR internally via PyMuPDF.

### 3.3 Performance Requirements
- Process 10-20 PDFs/minute (non-OCR)
- Process 2-5 PDFs/minute (with OCR)
- Handle PDFs up to 500 pages
- Memory: <500MB per PDF

## 4. Data Contracts

### 4.1 Input
```python
@dataclass
class PDFProcessConfig:
    input_path: Path               # Single PDF or directory
    output_dir: Path               # Markdown output directory
    language_filter: str = "en"    # Only process this language
    extract_images: bool = False   # Extract images (future)
    page_limit: Optional[int] = None  # Max pages to process
    quality_threshold: float = 0.3    # Min quality score (0-1)
```

### 4.2 Output Structure
```markdown
---
title: The State and Revolution
author: Vladimir Lenin
date: 1917
source_url: https://www.marxists.org/archive/lenin/works/1917/staterev/
language: en
doc_type: pdf
original_path: /archive/lenin/works/1917/staterev/staterev.pdf
processed_date: 2025-01-15T10:30:00Z
word_count: 45231
page_count: 120
content_hash: f7e2a1b8c9d3
ocr_applied: false
quality_score: 0.95
---

# The State and Revolution

## Chapter 1: Class Society and the State

...
```

### 4.3 Return Value
```python
@dataclass
class PDFProcessingResult:
    success: bool
    input_file: Path
    output_file: Optional[Path]
    metadata: PDFMetadata
    word_count: int
    page_count: int
    ocr_applied: bool
    quality_score: float  # 0-1, content quality assessment
    processing_time: float
    error: Optional[str] = None
```

### 4.4 PDF Metadata Structure
```python
@dataclass
class PDFMetadata:
    source_url: str              # Reconstructed MIA URL
    title: str                   # From PDF properties or filename
    author: Optional[str]        # From PDF properties or path
    date: Optional[str]          # From PDF properties or path
    language: str = "en"
    doc_type: str = "pdf"
    original_path: str
    processed_date: str          # ISO 8601
    content_hash: str            # SHA256 first 16 chars
    word_count: int
    page_count: int
    ocr_applied: bool
    quality_score: float         # Content quality 0-1
```

## 5. Functional Specification

### 5.1 Core Function Signature
```python
def process_pdf_file(
    pdf_path: Path,
    config: PDFProcessConfig
) -> PDFProcessingResult:
    """
    Convert single PDF to Markdown.
    
    Args:
        pdf_path: Path to PDF file
        config: Processing configuration
        
    Returns:
        PDFProcessingResult with output path and metadata
        
    Raises:
        PDFError: If PDF cannot be read
        OCRError: If OCR fails on image-based PDF
        IOError: If cannot write output
    """
```

### 5.2 Processing Pipeline

```
1. Open PDF → 2. Detect language → 3. Assess if OCR needed →
4. Extract metadata → 5. Convert to Markdown → 6. Clean markdown →
7. Assess quality → 8. Generate frontmatter → 9. Write output
```

#### Step-by-Step:

**1. PDF Opening & Validation**
```python
def open_pdf(pdf_path: Path) -> PDFDocument:
    """
    Open PDF and validate.
    
    Checks:
    - File is valid PDF
    - Not password-protected
    - Not corrupted
    - Has extractable content or images
    """
    import pymupdf
    
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        raise PDFError(f"Cannot open PDF: {e}")
    
    if doc.is_encrypted:
        raise PDFError("PDF is password-protected")
    
    if doc.page_count == 0:
        raise PDFError("PDF has no pages")
    
    return doc
```

**2. Language Detection**
```python
def detect_pdf_language(pdf_path: Path) -> Optional[str]:
    """
    Detect language from path (same heuristics as HTML).
    
    Returns None if should skip.
    """
    path_str = str(pdf_path).lower()
    
    NON_ENGLISH_MARKERS = [
        '/chinese/', '/deutsch/', '/espanol/', '/francais/',
        '/italiano/', '/japanese/', '/polski/', '/portugues/',
        '/russian/', '/turkce/', '/arabic/', '/svenska/'
    ]
    
    for marker in NON_ENGLISH_MARKERS:
        if marker in path_str:
            return None
    
    return "en"
```

**3. OCR Detection**
```python
def needs_ocr(doc: PDFDocument) -> bool:
    """
    Determine if PDF needs OCR.
    
    Strategy:
    - Sample first 3 pages
    - Try text extraction
    - If <100 characters extracted, likely image-based
    """
    import pymupdf
    
    sample_pages = min(3, doc.page_count)
    total_text = 0
    
    for page_num in range(sample_pages):
        page = doc[page_num]
        text = page.get_text()
        total_text += len(text.strip())
    
    # Less than 100 chars in 3 pages → probably needs OCR
    return total_text < 100
```

**4. Metadata Extraction**
```python
def extract_pdf_metadata(
    doc: PDFDocument,
    pdf_path: Path
) -> PDFMetadata:
    """
    Extract metadata from PDF properties and path.
    
    Priority for title:
    1. PDF metadata['title']
    2. Filename (sanitized)
    
    Priority for author:
    1. PDF metadata['author']
    2. Path inference (/archive/lenin/ → "Vladimir Lenin")
    3. None
    
    Priority for date:
    1. PDF metadata['creationDate'] or ['modDate']
    2. Path inference (/1917/ → "1917")
    3. None
    """
    import pymupdf
    
    metadata = doc.metadata
    
    # Extract title
    title = metadata.get('title', '').strip()
    if not title:
        # Use filename without extension
        title = pdf_path.stem.replace('-', ' ').replace('_', ' ').title()
    
    # Extract author
    author = metadata.get('author', '').strip()
    if not author:
        # Try to infer from path
        author = infer_author_from_path(pdf_path)
    
    # Extract date
    date = metadata.get('creationDate', '')
    if not date:
        date = infer_date_from_path(pdf_path)
    
    return PDFMetadata(
        title=title,
        author=author,
        date=date,
        page_count=doc.page_count,
        # ... other fields
    )
```

**5. Markdown Conversion**
```python
def convert_pdf_to_markdown(
    pdf_path: Path,
    page_limit: Optional[int] = None
) -> str:
    """
    Convert PDF to Markdown using pymupdf4llm.
    
    pymupdf4llm handles:
    - Text extraction
    - OCR when needed
    - Structure preservation (headers, lists)
    - Multi-column layouts
    """
    import pymupdf4llm
    
    markdown = pymupdf4llm.to_markdown(
        str(pdf_path),
        pages=list(range(page_limit)) if page_limit else None
    )
    
    return markdown
```

**6. Markdown Cleaning**
```python
def clean_pdf_markdown(content: str) -> str:
    """
    Clean PDF-derived markdown.
    
    Common PDF issues:
    - Hyphenation at line breaks
    - Extra spaces in words
    - Page numbers/headers/footers
    - Garbled OCR artifacts
    """
    import re
    
    # Fix hyphenation (word- \n word → word)
    content = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', content)
    
    # Remove page numbers (lines with just "Page N" or "N")
    content = re.sub(r'^\s*(?:Page\s+)?\d+\s*$', '', content, flags=re.MULTILINE)
    
    # Remove excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Remove OCR artifacts (single chars on own lines)
    content = re.sub(r'^\s*[^\w\s]\s*$', '', content, flags=re.MULTILINE)
    
    # Normalize spaces
    content = re.sub(r'  +', ' ', content)
    
    return content.strip()
```

**7. Quality Assessment**
```python
def assess_pdf_quality(
    markdown: str,
    doc: PDFDocument
) -> float:
    """
    Assess quality of converted PDF (0-1 score).
    
    Factors:
    - Text density (words per page)
    - Presence of structure (headers)
    - OCR confidence (if OCR was used)
    - Readable content ratio
    """
    word_count = len(markdown.split())
    page_count = doc.page_count
    
    # Words per page (should be 100-500 typically)
    words_per_page = word_count / max(page_count, 1)
    density_score = min(words_per_page / 300, 1.0)
    
    # Structure presence (headers)
    has_structure = len(re.findall(r'^#{1,3}\s', markdown, re.MULTILINE))
    structure_score = min(has_structure / 5, 1.0)
    
    # Readable content (alphanumeric ratio)
    alnum_chars = sum(c.isalnum() for c in markdown)
    total_chars = len(markdown)
    readability_score = alnum_chars / max(total_chars, 1)
    
    # Combined score
    quality = (density_score * 0.4 +
               structure_score * 0.2 +
               readability_score * 0.4)
    
    return min(quality, 1.0)
```

### 5.3 Batch Processing
```python
def process_pdf_directory(
    input_dir: Path,
    config: PDFProcessConfig,
    parallel: bool = True,
    max_workers: int = 2  # Lower for PDFs (memory intensive)
) -> List[PDFProcessingResult]:
    """
    Process all PDFs in directory.
    
    Note: Use fewer workers than HTML processing due to memory usage.
    """
    pdf_files = list(input_dir.rglob("*.pdf"))
    
    if parallel:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(
                lambda f: process_pdf_file(f, config),
                pdf_files
            )
            return list(results)
    else:
        return [process_pdf_file(f, config) for f in pdf_files]
```

## 6. Error Handling

### 6.1 Error Types
```python
class PDFProcessError(Exception):
    """Base exception"""

class PDFError(PDFProcessError):
    """Cannot open/read PDF"""

class OCRError(PDFProcessError):
    """OCR processing failed"""

class QualityError(PDFProcessError):
    """Output quality below threshold"""
```

### 6.2 Recovery Strategies

| Error | Strategy |
|-------|----------|
| Encrypted PDF | Skip, log warning |
| Corrupted PDF | Skip, log error |
| OCR failure | Skip page, log warning, continue |
| Low quality | Include in output but flag in metadata |
| Memory error | Retry with page_limit |
| Timeout | Skip, log timeout duration |

### 6.3 Quality Filtering
```python
if result.quality_score < config.quality_threshold:
    logger.warning(f"Low quality PDF: {pdf_path} (score: {result.quality_score})")
    # Either skip or flag in metadata depending on config
```

## 7. Testing Requirements

### 7.1 Unit Tests
```python
def test_pdf_opening():
    """Test PDF opening and validation"""
    
def test_ocr_detection():
    """Test detection of OCR need"""
    
def test_metadata_extraction():
    """Test metadata from PDF properties"""
    
def test_markdown_conversion():
    """Test PDF to Markdown quality"""
    
def test_quality_assessment():
    """Test quality scoring algorithm"""
    
def test_markdown_cleaning():
    """Test cleaning of common PDF artifacts"""
```

### 7.2 Integration Tests
```python
def test_text_based_pdf():
    """Test modern text-based PDF"""
    
def test_scanned_pdf():
    """Test OCR on scanned document"""
    
def test_multicolumn_layout():
    """Test multi-column preservation"""
    
def test_large_pdf():
    """Test handling of 100+ page document"""
```

### 7.3 Test Fixtures
Need sample PDFs:
- Modern text-based (born-digital)
- Scanned historical document (requires OCR)
- Multi-column layout
- Low-quality scan
- Corrupted PDF (for error handling)

## 8. Success Criteria

### 8.1 Functional
- [ ] Processes 90%+ of valid PDFs
- [ ] Correctly detects when OCR is needed
- [ ] Preserves document structure
- [ ] Handles multi-column layouts
- [ ] Extracts metadata accurately
- [ ] Quality scores correlate with usability

### 8.2 Non-Functional
- [ ] Processes 10+ PDFs/minute (non-OCR)
- [ ] Handles PDFs up to 500 pages
- [ ] Memory usage <500MB per PDF
- [ ] No crashes on malformed PDFs

## 9. Known Limitations

### 9.1 OCR Accuracy
- Pre-1990s documents may have poor OCR
- Handwritten notes typically fail
- Mathematical notation often garbled
- Quality depends on scan resolution

### 9.2 Layout Challenges
- Complex tables may lose structure
- Multi-column layouts sometimes merge incorrectly
- Footnotes may be misplaced
- Diagrams/images lost (text only)

### 9.3 Workarounds
```python
# For particularly important but low-quality PDFs:
# 1. Manual review flagged in metadata
# 2. Provide original PDF link in output
# 3. Flag for human post-processing
```

## 10. Performance Benchmarks

- Small PDF (<10 pages, text): 1-3 seconds
- Medium PDF (10-100 pages, text): 5-30 seconds
- Large PDF (100+ pages, text): 30-120 seconds
- Scanned PDF (OCR): 2-10x slower

**Batch processing 38,000 PDFs:**
- Estimated: 10-20 hours (without OCR)
- Estimated: 40-80 hours (with OCR where needed)

## 11. Implementation Confidence

**Confidence:** 75%

**Risks:**
- OCR quality highly variable (20%)
- Complex layouts may fail (15%)
- Memory issues with large PDFs (10%)

**Mitigation:**
- Quality scoring to flag problems
- Graceful degradation
- Page-by-page processing for large files

## 12. Integration Points

**Requires:** None (standalone)  
**Provides:** Markdown files for RAG ingestion  
**Used By:** Vector DB ingestion component  
**Quality Metrics:** Feed into monitoring dashboard

## 13. Example Output Comparison

### Good Quality PDF (score: 0.9+)
```markdown
# The State and Revolution

## Chapter 1: Class Society and the State

The state is a product of the irreconcilability of class antagonisms. The state arises where, when and insofar as class antagonism objectively cannot be reconciled.
```

### Poor Quality PDF (score: <0.5)
```markdown
# Th e St at e an d Rev ol ut io n

Ch apt er 1 C la ss So ci et y

Th e st at e i s a pr od uc t o f t he i rr ec on ci la bi li ty
```

**Action:** Flag low-quality PDFs for potential manual review.

## 14. Command Line Interface

```bash
# Process single PDF
python pdf_processor.py \
  --input /path/to/document.pdf \
  --output ./markdown/

# Process directory
python pdf_processor.py \
  --input /path/to/pdfs/ \
  --output ./markdown/ \
  --parallel \
  --max-workers 2

# With quality filtering
python pdf_processor.py \
  --input /path/to/pdfs/ \
  --output ./markdown/ \
  --quality-threshold 0.5
```
