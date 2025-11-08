# Component Specification: HTML to Markdown Processor

**Version:** 1.0  
**Status:** Ready for Implementation  
**Estimated Complexity:** Medium  
**Estimated Time:** 2-3 hours  

## 1. Objective

Convert MIA HTML files to clean, RAG-optimized Markdown while preserving semantic structure, removing boilerplate, and extracting metadata.

## 2. Scope

**In Scope:**

- HTML parsing and cleaning
- Markdown conversion with proper formatting
- Boilerplate removal (nav, headers, footers)
- Language detection (English filter)
- Metadata extraction from HTML structure
- Frontmatter generation

**Out of Scope:**

- PDF processing
- Vector embedding
- Database operations
- Image processing

## 3. Technical Requirements

### 3.1 System Requirements

- Python 3.9+
- UTF-8 encoding support
- 4GB RAM minimum for batch processing

### 3.2 Dependencies

```python
beautifulsoup4>=4.12.0
markdownify>=0.11.6
lxml>=4.9.0
```

### 3.3 Performance Requirements

- Process 100 HTML files/minute minimum
- Memory usage: <100MB per process
- Support parallel processing

## 4. Data Contracts

### 4.1 Input

```python
@dataclass
class HTMLProcessConfig:
    input_path: Path            # Single file or directory
    output_dir: Path            # Where to write markdown
    language_filter: str = "en" # Only process this language
    remove_elements: List[str] = field(default_factory=lambda: [
        'script', 'style', 'nav', 'header', 'footer', 'iframe'
    ])
    preserve_links: bool = True
    extract_metadata: bool = True
```

### 4.2 Output Structure

```markdown
---
title: The Communist Manifesto
author: Karl Marx, Friedrich Engels
date: 1848
source_url: https://www.marxists.org/archive/marx/works/1848/communist-manifesto/
language: en
doc_type: html
original_path: /archive/marx/works/1848/communist-manifesto/ch01.htm
processed_date: 2025-01-15T10:30:00Z
word_count: 5432
content_hash: a3f5b9c2e1d4
---

# Chapter 1: Bourgeois and Proletarians

The history of all hitherto existing society is the history of class struggles...
```

### 4.3 Return Value

```python
@dataclass
class ProcessingResult:
    success: bool
    input_file: Path
    output_file: Optional[Path]
    metadata: DocumentMetadata
    word_count: int
    processing_time: float
    error: Optional[str] = None
```

### 4.4 Document Metadata Structure

```python
@dataclass
class DocumentMetadata:
    source_url: str              # Reconstructed MIA URL
    title: str                   # Extracted from <title> or <h1>
    author: Optional[str]        # Inferred from path or meta tags
    date: Optional[str]          # From meta tags or content
    language: str = "en"
    doc_type: str = "html"
    original_path: str
    processed_date: str          # ISO 8601 timestamp
    content_hash: str            # SHA256 first 16 chars
    word_count: int
```

## 5. Functional Specification

### 5.1 Core Function Signature

```python
def process_html_file(
    html_path: Path,
    config: HTMLProcessConfig
) -> ProcessingResult:
    """
    Convert single HTML file to Markdown.
    
    Args:
        html_path: Path to HTML file
        config: Processing configuration
        
    Returns:
        ProcessingResult with output path and metadata
        
    Raises:
        EncodingError: If file encoding cannot be determined
        ParseError: If HTML is malformed beyond recovery
        IOError: If cannot write output file
    """
```

### 5.2 Processing Pipeline

```
1. Read HTML file → 2. Detect language → 3. Parse HTML → 
4. Remove boilerplate → 5. Extract metadata → 6. Convert to Markdown →
7. Clean markdown → 8. Generate frontmatter → 9. Write output
```

#### Step-by-Step

**1. File Reading**

```python
def read_html_file(path: Path) -> str:
    """
    Read HTML with encoding detection.
    Try: utf-8, latin-1, cp1252
    """
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise EncodingError(f"Cannot decode {path}")
```

**2. Language Detection**

```python
def detect_language(html_path: Path) -> Optional[str]:
    """
    Heuristic language detection from path.
    
    Rules:
    - /espanol/ → skip (Spanish)
    - /deutsch/ → skip (German)
    - /francais/ → skip (French)
    - /archive/ → likely English
    - /history/ → likely English
    - /reference/ → English
    
    Returns None if should skip.
    """
    path_str = str(html_path).lower()
    
    NON_ENGLISH_MARKERS = [
        '/chinese/', '/deutsch/', '/espanol/', '/francais/',
        '/italiano/', '/japanese/', '/polski/', '/portugues/',
        '/russian/', '/turkce/', '/arabic/', '/svenska/',
        '/catala/', '/greek/', '/korean/', '/farsi/',
        '/czech/', '/dutch/', '/finnish/', '/hungarian/'
    ]
    
    for marker in NON_ENGLISH_MARKERS:
        if marker in path_str:
            return None  # Skip
    
    return "en"  # Process
```

**3. HTML Parsing**

```python
def parse_html(content: str) -> BeautifulSoup:
    """Parse HTML with lxml parser for speed."""
    return BeautifulSoup(content, 'lxml')
```

**4. Boilerplate Removal**

```python
def remove_boilerplate(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove non-content elements:
    - Navigation menus
    - Headers/footers
    - Sidebar widgets
    - JavaScript/CSS
    - MIA-specific boilerplate
    """
    # Remove by tag
    for tag in ['script', 'style', 'nav', 'header', 'footer']:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove by class (MIA-specific)
    for class_name in ['navigation', 'menu', 'sidebar']:
        for element in soup.find_all(class_=class_name):
            element.decompose()
    
    # Remove by ID
    for id_name in ['header', 'footer', 'nav']:
        element = soup.find(id=id_name)
        if element:
            element.decompose()
    
    return soup
```

**5. Metadata Extraction**

```python
def extract_metadata(
    soup: BeautifulSoup,
    html_path: Path
) -> DocumentMetadata:
    """
    Extract metadata from HTML and file path.
    
    Priority for title:
    1. <title> tag
    2. <h1> tag
    3. Filename
    
    Priority for author:
    1. <meta name="author">
    2. Path inference (/archive/marx/ → "Karl Marx")
    3. None
    
    Priority for date:
    1. <meta name="date">
    2. Path inference (/1848/ → "1848")
    3. None
    """
```

**6. Markdown Conversion**

```python
def convert_to_markdown(soup: BeautifulSoup) -> str:
    """
    Convert HTML to Markdown using markdownify.
    
    Settings:
    - heading_style="ATX" (use # instead of underlines)
    - bullets="-" (use - for lists)
    - strip=["a"] (remove empty links)
    """
    from markdownify import markdownify as md
    
    markdown = md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*"
    )
    
    return markdown
```

**7. Markdown Cleaning**

```python
def clean_markdown(content: str) -> str:
    """
    Clean converted markdown:
    - Remove excessive blank lines (3+ → 2)
    - Remove trailing whitespace
    - Normalize list formatting
    - Fix broken links
    """
    import re
    
    # Remove excessive newlines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Remove trailing whitespace
    lines = [line.rstrip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    # Remove leading/trailing whitespace
    content = content.strip()
    
    return content
```

**8. Frontmatter Generation**

```python
def generate_frontmatter(metadata: DocumentMetadata) -> str:
    """
    Generate YAML frontmatter for metadata.
    """
    return f"""---
title: {metadata.title}
author: {metadata.author or 'Unknown'}
date: {metadata.date or 'Unknown'}
source_url: {metadata.source_url}
language: {metadata.language}
doc_type: {metadata.doc_type}
original_path: {metadata.original_path}
processed_date: {metadata.processed_date}
word_count: {metadata.word_count}
content_hash: {metadata.content_hash}
---

"""
```

**9. Output Writing**

```python
def write_output(
    content: str,
    metadata: DocumentMetadata,
    output_dir: Path
) -> Path:
    """
    Write markdown file with frontmatter.
    
    Filename: {sanitized_title}_{hash}.md
    """
    # Sanitize title for filename
    safe_title = re.sub(r'[^\w\s-]', '', metadata.title)[:100]
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    
    filename = f"{safe_title}_{metadata.content_hash}.md"
    output_path = output_dir / filename
    
    # Combine frontmatter + content
    full_content = generate_frontmatter(metadata) + content
    
    output_path.write_text(full_content, encoding='utf-8')
    
    return output_path
```

### 5.3 Batch Processing

```python
def process_html_directory(
    input_dir: Path,
    config: HTMLProcessConfig,
    parallel: bool = True,
    max_workers: int = 4
) -> List[ProcessingResult]:
    """
    Process all HTML files in directory.
    
    Args:
        input_dir: Directory containing HTML files
        config: Processing configuration
        parallel: Use multiprocessing
        max_workers: Number of parallel workers
        
    Returns:
        List of ProcessingResult for each file
    """
    html_files = list(input_dir.rglob("*.htm")) + \
                 list(input_dir.rglob("*.html"))
    
    if parallel:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(
                lambda f: process_html_file(f, config),
                html_files
            )
            return list(results)
    else:
        return [process_html_file(f, config) for f in html_files]
```

## 6. Error Handling

### 6.1 Error Types

```python
class HTMLProcessError(Exception):
    """Base exception"""

class EncodingError(HTMLProcessError):
    """Cannot decode file"""

class ParseError(HTMLProcessError):
    """HTML parsing failed"""

class MetadataExtractionError(HTMLProcessError):
    """Cannot extract required metadata"""
```

### 6.2 Recovery Strategies

| Error | Strategy |
|-------|----------|
| Encoding error | Try multiple encodings, log on failure |
| Parse error | Use 'html.parser' fallback instead of 'lxml' |
| Missing title | Use filename as title |
| Missing author | Set to "Unknown", continue |
| Empty content | Skip file, log warning |
| Write failure | Retry once, then fail |

## 7. Quality Validation

### 7.1 Output Quality Checks

```python
def validate_output(markdown: str, metadata: DocumentMetadata) -> bool:
    """
    Validate processed markdown:
    - Length > 100 characters
    - Has at least one paragraph
    - Word count matches metadata
    - No excessive HTML tags remaining
    """
    # Check minimum length
    if len(markdown) < 100:
        return False
    
    # Check for excessive HTML (< 5% of content)
    html_tags = re.findall(r'<[^>]+>', markdown)
    if len(''.join(html_tags)) > len(markdown) * 0.05:
        return False
    
    # Verify word count
    actual_words = len(markdown.split())
    if abs(actual_words - metadata.word_count) > 10:
        return False
    
    return True
```

### 7.2 Content Quality Heuristics

```python
def assess_content_quality(soup: BeautifulSoup) -> float:
    """
    Assess content quality (0-1 score).
    
    Factors:
    - Text to HTML ratio
    - Presence of actual paragraphs
    - Link density
    - Content length
    """
    text_length = len(soup.get_text())
    html_length = len(str(soup))
    
    # Higher score for more text vs markup
    text_ratio = text_length / max(html_length, 1)
    
    # Presence of substantial paragraphs
    paragraphs = soup.find_all('p')
    has_content = sum(1 for p in paragraphs if len(p.get_text()) > 50)
    
    # Lower score for link farms
    links = len(soup.find_all('a'))
    link_density = links / max(text_length, 1) * 100
    
    score = (text_ratio * 0.4 +
             min(has_content / 5, 1) * 0.4 +
             max(0, 1 - link_density / 10) * 0.2)
    
    return min(score, 1.0)
```

## 8. Testing Requirements

### 8.1 Unit Tests

```python
def test_language_detection():
    """Test language detection heuristics"""
    
def test_boilerplate_removal():
    """Test removal of nav/header/footer"""
    
def test_metadata_extraction():
    """Test metadata from various HTML structures"""
    
def test_markdown_conversion():
    """Test HTML to Markdown quality"""
    
def test_frontmatter_generation():
    """Test YAML frontmatter format"""
```

### 8.2 Integration Tests

```python
def test_full_pipeline():
    """Test complete HTML→Markdown pipeline"""
    
def test_batch_processing():
    """Test directory processing"""
    
def test_parallel_processing():
    """Test multiprocessing"""
```

### 8.3 Test Fixtures

Create test HTML files representing:

- Simple article (Marx essay)
- Complex nested structure (Capital chapter)
- Heavy boilerplate (index page)
- Non-English content
- Malformed HTML

## 9. Success Criteria

### 9.1 Functional

- [ ] Processes 95%+ of English HTML files
- [ ] Removes all navigation boilerplate
- [ ] Preserves document structure (headings, lists, quotes)
- [ ] Generates valid YAML frontmatter
- [ ] Calculates accurate word counts
- [ ] Produces clean, readable Markdown

### 9.2 Non-Functional

- [ ] Processes ≥100 files/minute
- [ ] Memory usage <100MB per process
- [ ] No data loss on interruption (atomic writes)
- [ ] Deterministic output (same input → same output)

## 10. Example Test Case

### Input HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>Wage Labour and Capital - Marx</title>
    <meta name="author" content="Karl Marx">
    <meta name="date" content="1847">
</head>
<body>
    <nav><a href="/">Home</a></nav>
    <h1>Wage Labour and Capital</h1>
    <p>Wages are determined through the antagonistic struggle between capitalist and worker.</p>
    <footer>Copyright MIA</footer>
</body>
</html>
```

### Expected Output

```markdown
---
title: Wage Labour and Capital - Marx
author: Karl Marx
date: 1847
source_url: https://www.marxists.org/archive/marx/works/1847/wage-labour/
language: en
doc_type: html
word_count: 12
content_hash: abc123...
---

# Wage Labour and Capital

Wages are determined through the antagonistic struggle between capitalist and worker.
```

## 11. Performance Benchmarks

- Small file (<10KB): <50ms
- Medium file (10-100KB): <200ms
- Large file (>100KB): <1s
- Batch (1000 files): <10 minutes

## 12. Implementation Confidence

**Confidence:** 90%

**Risks:**

- Edge cases in HTML structure (10%)
- Character encoding issues with old scans (5%)

**Mitigation:**

- Extensive test suite
- Graceful degradation

## 13. Integration Points

**Requires:** None (standalone)  
**Provides:** Markdown files for RAG ingestion  
**Used By:** Vector DB ingestion component
