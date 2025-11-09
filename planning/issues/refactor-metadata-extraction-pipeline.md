---
title: "Refactoring: Implement Multi-Source Metadata Extraction Pipeline"
labels: refactoring, metadata, critical, instance1
assignees: ""
---

## Problem Statement

The current `extract_metadata_from_html()` function in `mia_processor.py:144-182` uses **only path-based extraction**, resulting in:
- **~70% author coverage** (fails on ETOL, EROL, Subject sections)
- **~53% date coverage** (only extracts from paths, misses title/content dates)
- **No fallback strategies** when primary extraction fails
- **No confidence scoring** to assess extraction quality
- **No section-specific rules** (Archive vs. ETOL vs. EROL have different patterns)

**Corpus Analysis Findings** (from `docs/corpus-analysis/`):
- **Archive**: 100% path-based author extraction possible
- **ETOL**: Authors in title patterns (~85% coverage with multi-source)
- **EROL**: Organization attribution from titles (~95% coverage)
- **Subject**: Authors in meta tags + cross-references (~48% coverage)
- **Glossary**: 100% entity structure extraction
- **Reference**: 100% path-based author extraction

## Current Implementation

```python
def extract_metadata_from_html(self, html_content: str, file_path: Path) -> DocumentMetadata:
    """Current implementation - path-based only"""
    soup = BeautifulSoup(html_content, 'lxml')

    # Author extraction: path-based only (~70% coverage)
    author = None
    if '/archive/' in str(file_path):
        parts = file_path.parts
        archive_idx = parts.index('archive')
        if archive_idx + 1 < len(parts):
            author = parts[archive_idx + 1].replace('-', ' ').title()

    # Date extraction: path-based only (~53% coverage)
    date = None
    # ... minimal date extraction

    return DocumentMetadata(
        author=author,  # No source tracking, no confidence
        date=date,      # No source tracking, no confidence
        # ...
    )
```

**Issues:**
- Single extraction strategy per field (no fallbacks)
- No provenance tracking (can't trace where metadata came from)
- No confidence scoring (can't assess quality)
- Ignores meta tags, title patterns, keywords
- No section-specific rules (ETOL newspapers, EROL organizations)

## Proposed Solution

Implement **Multi-Source Extraction Pipeline** with **Strategy Pattern**:

### Architecture

```python
# 1. Extraction Result with Provenance
@dataclass
class ExtractionResult:
    """Result from extraction strategy with metadata"""
    value: Any
    source: Literal['path', 'title', 'keywords', 'meta', 'content', 'manual']
    confidence: float  # 0.0-1.0
    extractor_name: str

    def __bool__(self) -> bool:
        return self.value is not None

# 2. Extractor Interface
class MetadataExtractor(ABC):
    """Base class for metadata extraction strategies"""

    @abstractmethod
    def extract(self, soup: BeautifulSoup, file_path: Path) -> ExtractionResult:
        """Extract metadata from document."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Source type for provenance tracking."""

    @property
    @abstractmethod
    def confidence_base(self) -> float:
        """Base confidence for this extraction method."""

# 3. Author Extraction Strategies (7 strategies)
class PathBasedAuthorExtractor(MetadataExtractor):
    """Strategy 1: Extract author from file path (Archive, Reference)"""
    source_type = "path"
    confidence_base = 1.0  # Highly reliable for Archive

    def extract(self, soup: BeautifulSoup, file_path: Path) -> ExtractionResult:
        if '/archive/' in str(file_path):
            parts = file_path.parts
            archive_idx = parts.index('archive')
            if archive_idx + 1 < len(parts):
                author = parts[archive_idx + 1].replace('-', ' ').title()
                return ExtractionResult(
                    value=author,
                    source='path',
                    confidence=1.0,
                    extractor_name='PathBasedAuthorExtractor'
                )
        return ExtractionResult(None, 'path', 0.0, 'PathBasedAuthorExtractor')

class TitlePatternAuthorExtractor(MetadataExtractor):
    """Strategy 2: Extract author from title patterns (ETOL)"""
    source_type = "title"
    confidence_base = 0.85

    # ETOL patterns: "Author: Title", "Author (Year): Title", etc.
    PATTERNS = [
        r'^([A-Z][a-z]+(?: [A-Z][a-z]+)*?):\s+',  # "Marx: Title"
        r'^([A-Z][a-z]+(?: [A-Z][a-z]+)*?)\s+\(\d{4}\)',  # "Marx (1867)"
        # ... more patterns
    ]

class KeywordsAuthorExtractor(MetadataExtractor):
    """Strategy 3: Extract from meta keywords tag (Subject)"""
    source_type = "keywords"
    confidence_base = 0.70

class MetaTagAuthorExtractor(MetadataExtractor):
    """Strategy 4: Extract from <meta name="author"> tag"""
    source_type = "meta"
    confidence_base = 0.90

class ContentAuthorExtractor(MetadataExtractor):
    """Strategy 5: Extract from "By Author" patterns in content"""
    source_type = "content"
    confidence_base = 0.60

class TranscriberAuthorExtractor(MetadataExtractor):
    """Strategy 6: ETOL-specific: Distinguish transcriber vs. author"""
    source_type = "title"
    confidence_base = 0.80

class OrganizationAuthorExtractor(MetadataExtractor):
    """Strategy 7: EROL-specific: Extract organization attribution"""
    source_type = "title"
    confidence_base = 0.95

    ORGANIZATIONS = [
        'MLOC', 'RCP', 'CPUSA', 'SWP', 'ISO', 'DSA',
        # ... extracted from EROL corpus

# 4. Date Extraction Strategies (5 strategies)
class PathBasedDateExtractor(MetadataExtractor):
    """Strategy 1: Extract date from file path"""
    source_type = "path"
    confidence_base = 1.0

    # Patterns: /1867/, /1840s/, /1917-10/, etc.
    PATTERNS = [
        r'/(\d{4})(?:/|\.|-)(\d{2})?(?:/|\.|-)(\d{2})?',  # /1867/10/25/
        r'/(\d{4})s/',  # /1840s/
        r'(\d{4})-(\d{4})',  # 1917-1923 (range)
    ]

class TitlePatternDateExtractor(MetadataExtractor):
    """Strategy 2: Extract date from title patterns"""
    source_type = "title"
    confidence_base = 0.85

    # Patterns: "Title (1867)", "1867: Title", etc.

class ProvenanceDateExtractor(MetadataExtractor):
    """Strategy 3: ETOL-specific: Extract from provenance info"""
    source_type = "content"
    confidence_base = 0.90

    # Patterns: "Written: October 1917", "First Published: 1867"

class MetaTagDateExtractor(MetadataExtractor):
    """Strategy 4: Extract from <meta name="date"> tag"""
    source_type = "meta"
    confidence_base = 0.90

class IssueDateExtractor(MetadataExtractor):
    """Strategy 5: ETOL newspapers: Extract newspaper issue date"""
    source_type = "title"
    confidence_base = 0.95

# 5. Keywords Extraction Strategies (3 strategies)
class MetaKeywordsExtractor(MetadataExtractor):
    """Strategy 1: Extract from <meta name="keywords"> tag"""
    source_type = "meta"
    confidence_base = 0.95

class BreadcrumbKeywordsExtractor(MetadataExtractor):
    """Strategy 2: Extract from breadcrumb navigation"""
    source_type = "content"
    confidence_base = 0.85

class CrossReferenceExtractor(MetadataExtractor):
    """Strategy 3: Extract cross-references from links"""
    source_type = "content"
    confidence_base = 0.80

# 6. Multi-Source Extraction Pipeline
class ExtractionPipeline:
    """Coordinates multiple extraction strategies with fallbacks"""

    def __init__(self, section_type: str):
        self.section_type = section_type
        self.author_extractors = self._load_author_extractors()
        self.date_extractors = self._load_date_extractors()
        self.keywords_extractors = self._load_keywords_extractors()

    def _load_author_extractors(self) -> List[MetadataExtractor]:
        """Load section-specific author extraction strategies"""
        if self.section_type == 'archive':
            return [PathBasedAuthorExtractor()]  # 100% reliable
        elif self.section_type == 'etol':
            return [
                TitlePatternAuthorExtractor(),
                TranscriberAuthorExtractor(),
                KeywordsAuthorExtractor(),
                ContentAuthorExtractor(),
            ]
        elif self.section_type == 'erol':
            return [
                OrganizationAuthorExtractor(),
                TitlePatternAuthorExtractor(),
            ]
        # ... other sections

    def extract_authors(self, soup: BeautifulSoup, file_path: Path) -> List[ExtractionResult]:
        """Try extraction strategies in priority order, return all results"""
        results = []
        for extractor in self.author_extractors:
            result = extractor.extract(soup, file_path)
            if result:
                results.append(result)
        return results

    def select_best_result(self, results: List[ExtractionResult]) -> ExtractionResult:
        """Select highest-confidence result from multiple strategies"""
        if not results:
            return ExtractionResult(None, 'unknown', 0.0, 'none')
        return max(results, key=lambda r: r.confidence)
```

### Implementation Steps

1. **Create extraction framework** (`mia_processor/extractors/base.py`)
   - `ExtractionResult` dataclass
   - `MetadataExtractor` abstract base
   - `ExtractionPipeline` coordinator

2. **Implement author extractors** (`mia_processor/extractors/author.py`)
   - 7 extraction strategies (path, title, keywords, meta, content, transcriber, organization)
   - Section-specific pattern definitions
   - Confidence scoring logic

3. **Implement date extractors** (`mia_processor/extractors/date.py`)
   - 5 extraction strategies (path, title, provenance, meta, issue date)
   - Date parsing and normalization (ISO 8601)
   - Date range handling (1917-1923)

4. **Implement keywords extractors** (`mia_processor/extractors/keywords.py`)
   - 3 extraction strategies (meta, breadcrumb, cross-reference)
   - Keyword cleaning and normalization
   - Deduplication logic

5. **Create section-specific rules** (`mia_processor/extractors/section_rules.py`)
   - Section type detection
   - Extractor loading per section
   - Section-specific pattern configurations

6. **Refactor `mia_processor.py`**
   - Replace `extract_metadata_from_html()` with pipeline
   - Populate all metadata layers (authorship, temporal, semantic)
   - Add encoding detection/normalization
   - Generate extraction reports (coverage metrics)

7. **Create test datasets** (`tests/fixtures/section_samples/`)
   - 100 sample documents per section (Archive, ETOL, EROL, Subject, Glossary, Reference)
   - Gold-standard metadata annotations
   - Coverage test harness

8. **Implement extraction tests** (`tests/unit/test_extractors.py`)
   - Unit tests for each extractor strategy
   - Integration tests for pipeline
   - Coverage tests (100-sample validation per section)
   - Regression tests (compare old vs. new extraction)

## Acceptance Criteria

- [ ] **Author Coverage Targets**:
  - Archive: 100% (path-based)
  - ETOL: 85%+ (multi-source: title + keywords + meta)
  - EROL: 95%+ (organization attribution)
  - Subject: 48%+ (meta + cross-reference)
  - Glossary: 100% (entry structure)
  - Reference: 100% (path-based)

- [ ] **Date Coverage**: 60%+ across corpus (multi-source extraction)
- [ ] **Provenance Tracking**: All extracted fields have `_source` and `_confidence` metadata
- [ ] **Fallback Strategies**: Pipeline tries multiple strategies before giving up
- [ ] **Section-Specific Rules**: Different extractors for Archive vs. ETOL vs. EROL
- [ ] **Extraction Reports**: Generate coverage metrics per section
- [ ] **Performance**: <50ms per document for extraction pipeline
- [ ] **100-Sample Validation**: 85%+ accuracy on test dataset per section
- [ ] **Backward Compatibility**: Successfully processes existing corpus

## Files to Modify

**New Files:**
- `mia_processor/extractors/__init__.py` - Extraction framework exports
- `mia_processor/extractors/base.py` - `ExtractionResult`, `MetadataExtractor`, `ExtractionPipeline`
- `mia_processor/extractors/author.py` - 7 author extraction strategies
- `mia_processor/extractors/date.py` - 5 date extraction strategies
- `mia_processor/extractors/keywords.py` - 3 keywords extraction strategies
- `mia_processor/extractors/section_rules.py` - Section-specific configurations
- `tests/fixtures/section_samples/` - 600 test documents (100 per section)
- `tests/unit/test_extractors.py` - Extractor validation tests
- `tests/integration/test_extraction_coverage.py` - Coverage tests

**Modified Files:**
- `mia_processor.py` - Replace `extract_metadata_from_html()` with pipeline
- `tests/unit/test_mia_processor.py` - Update tests for new extraction logic

## Dependencies

**External Dependencies:**
- `chardet` - Character encoding detection (ISO-8859-1 → UTF-8)
- `python-dateutil` - Date parsing and normalization
- `lxml` - Fast XML/HTML parsing (already required)

**Internal Dependencies:**
- Unified Metadata Schema (#TBD) - **BLOCKS THIS ISSUE** (must define schema first)
- Corpus analysis specs: `docs/corpus-analysis/01-archive-metadata-analysis.md` through `05-reference-metadata-analysis.md`

**Blocks:**
- Section-Specific Extractors (#TBD) - Needs base extraction pipeline
- Glossary Entity Linker (#TBD) - Needs author extraction for linking

## Related Issues

- Part of Code Refactoring Project (Stream 4: Metadata Pipeline)
- Blocked by: Unified Metadata Schema (#TBD)
- Blocks: Section-Specific Extractors (#TBD)
- Blocks: Glossary Entity Linker (#TBD)
- Related: Corpus Analysis (✅ Complete - extraction patterns documented)

## Estimated Effort

**Time**: 16-20 hours
**Complexity**: High (7 author + 5 date + 3 keywords extractors, section-specific rules)
**Priority**: CRITICAL (core metadata extraction functionality)

## Success Metrics

**Coverage Targets** (based on 100-sample validation per section):
- **Archive**: 100% author, 80%+ date
- **ETOL**: 85%+ author, 70%+ date, 90%+ transcriber
- **EROL**: 95%+ organization, 60%+ date
- **Subject**: 48%+ author, 64%+ category
- **Glossary**: 100% entry structure
- **Reference**: 100% author

**Quality Metrics**:
- **Precision**: 95%+ (extracted metadata is correct)
- **Recall**: Targets above (extracted metadata is present)
- **Provenance**: 100% (all extractions have source tracking)
- **Confidence**: Average 0.80+ across corpus

**Performance Targets**:
- Extraction pipeline: <50ms per document
- No performance regression vs. current path-based extraction

## Example Usage

```python
# Before (path-based only, ~70% author coverage)
metadata = extract_metadata_from_html(html_content, file_path)
# author = "Karl Marx" (if Archive) or None (if ETOL/EROL)
# No source tracking, no confidence

# After (multi-source pipeline, 85%+ author coverage)
pipeline = ExtractionPipeline(section_type='etol')

# Try multiple strategies
author_results = pipeline.extract_authors(soup, file_path)
# [
#   ExtractionResult(value="Leon Trotsky", source="title", confidence=0.85, extractor="TitlePatternAuthorExtractor"),
#   ExtractionResult(value="Trotsky", source="keywords", confidence=0.70, extractor="KeywordsAuthorExtractor"),
# ]

# Select best result
best_author = pipeline.select_best_result(author_results)
# ExtractionResult(value="Leon Trotsky", source="title", confidence=0.85, ...)

# Populate metadata schema
metadata.authorship.authors = [best_author.value]
metadata.authorship.author_source = best_author.source
metadata.authorship.author_confidence = best_author.confidence

# Generate coverage report
report = pipeline.generate_coverage_report(processed_documents)
# {
#   'etol': {'author_coverage': 0.87, 'date_coverage': 0.72},
#   'archive': {'author_coverage': 1.0, 'date_coverage': 0.81},
#   ...
# }
```

## References

- Corpus Analysis (metadata patterns): `docs/corpus-analysis/01-archive-metadata-analysis.md` through `05-reference-metadata-analysis.md`
- Unified Schema: `docs/corpus-analysis/06-metadata-unified-schema.md`
- Current Implementation: `mia_processor.py:144-182`
- Refactoring Project: `planning/projects/refactoring-code-complexity.md`
- Design Pattern: **Strategy Pattern** — Encapsulates interchangeable algorithms or behaviors behind a common interface, allowing the selection of the appropriate strategy at runtime. Useful for implementing multi-source extraction pipelines.
