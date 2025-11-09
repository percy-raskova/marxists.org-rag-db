---
title: "Refactoring: Implement Unified Metadata Schema (5-Layer Model)"
labels: refactoring, metadata, critical, instance1
assignees: ""
---

## Problem Statement

The current `DocumentMetadata` dataclass in `mia_processor.py:33-44` contains only **8 basic fields**, which is insufficient for:
- **Author disambiguation** across sections (Archive vs. ETOL vs. EROL patterns)
- **Multi-source extraction tracking** (provenance + confidence scoring)
- **Entity linking** for canonical name normalization
- **Section-specific metadata** (ETOL newspapers, EROL organizations, Subject categories)
- **Knowledge graph construction** (cross-references, relationships)

**Current Limitations:**
- **Author coverage**: ~70% (path-based only, fails on ETOL/EROL)
- **No provenance tracking**: Can't trace where metadata came from
- **No confidence scoring**: Can't assess extraction quality
- **Missing semantic metadata**: No keywords, topics, cross-references
- **No encoding normalization**: 62% of corpus is ISO-8859-1, needs UTF-8 conversion

## Current Implementation

```python
@dataclass
class DocumentMetadata:
    """Current schema - 8 fields only"""
    source_url: str
    title: str
    author: Optional[str]
    date: Optional[str]
    language: str
    doc_type: str
    word_count: int
    content_hash: str
```

**Issues:**
- No layer separation (identification vs. provenance vs. semantic)
- Single author field can't represent multiple authors or organizations
- No extraction confidence metrics
- Missing section-specific fields (newspapers, organizations, categories)
- No support for entity linking or cross-references

## Proposed Solution

Implement **5-Layer Metadata Model** based on corpus analysis findings:

### Architecture

```python
# Layer 1: Core Identification
@dataclass
class CoreIdentification:
    """Required fields for all documents"""
    source_url: str
    title: str
    content_hash: str
    section_type: Literal['archive', 'etol', 'erol', 'subject', 'glossary', 'reference']
    language: str  # ISO 639-1 code
    encoding_original: str  # e.g., 'ISO-8859-1', 'UTF-8'
    encoding_normalized: bool  # True if converted to UTF-8

# Layer 2: Authorship & Provenance
@dataclass
class AuthorshipProvenance:
    """Author attribution with source tracking"""
    authors: List[str]  # Primary authors (canonical names if linked)
    author_source: Literal['path', 'title', 'keywords', 'meta', 'content', 'manual']
    author_confidence: float  # 0.0-1.0 confidence score
    transcribers: List[str]  # ETOL-specific: who transcribed
    organizations: List[str]  # EROL-specific: MLOC, RCP, etc.
    recipients: List[str]  # Archive letters: who was addressed
    canonical_author_ids: List[str]  # Glossary-linked canonical IDs

# Layer 3: Temporal & Classification
@dataclass
class TemporalClassification:
    """Date information and categorization"""
    date_written: Optional[str]  # ISO 8601 if parseable
    date_published: Optional[str]
    date_source: Literal['path', 'title', 'provenance', 'meta', 'inferred']
    date_confidence: float
    time_period: Optional[str]  # "1840s", "early 20th century"
    movement_affiliation: List[str]  # ETOL: "Trotskyist", "Third Camp", etc.
    subject_categories: List[str]  # Subject section: extracted from breadcrumbs

# Layer 4: Technical & Processing
@dataclass
class TechnicalProcessing:
    """Document structure and processing metadata"""
    doc_type: Literal['html', 'pdf', 'txt']
    file_size_bytes: int
    word_count: int
    character_count: int
    heading_structure: Dict[str, int]  # {'h1': 1, 'h2': 5, 'h3': 12}
    has_toc: bool  # Table of contents detected
    is_anthology: bool  # Subject section: multiple works compiled
    is_git_lfs: bool  # Reference section: stored in Git LFS
    processing_timestamp: str  # ISO 8601
    processor_version: str  # e.g., "2.0.0"

# Layer 5: Semantic Enrichment
@dataclass
class SemanticEnrichment:
    """Keywords, cross-references, entity linking"""
    keywords: List[str]  # Extracted from meta tags, content
    meta_description: Optional[str]
    cross_references: List[str]  # URLs to related documents
    glossary_entities: List[str]  # Linked Glossary entries
    breadcrumb_path: List[str]  # Navigation breadcrumb trail
    collection_id: Optional[str]  # Archive: which author collection
    work_id: Optional[str]  # Archive: which specific work
    chapter_number: Optional[int]  # Archive: chapter within work
    newspaper_name: Optional[str]  # ETOL: source newspaper
    issue_date: Optional[str]  # ETOL: newspaper issue date

# Unified Schema
@dataclass
class DocumentMetadata:
    """Complete unified metadata schema - 40+ fields across 5 layers"""
    core: CoreIdentification
    authorship: AuthorshipProvenance
    temporal: TemporalClassification
    technical: TechnicalProcessing
    semantic: SemanticEnrichment

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to flat dictionary for storage"""
        return {
            **asdict(self.core),
            **asdict(self.authorship),
            **asdict(self.temporal),
            **asdict(self.technical),
            **asdict(self.semantic),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """Deserialize from flat dictionary"""
        # Implementation splits fields across layers
```

### Implementation Steps

1. **Create metadata schema module** (`mia_processor/metadata/schema.py`)
   - Define 5 dataclass layers
   - Implement `DocumentMetadata` unified class
   - Serialization/deserialization methods
   - Validation logic for required fields

2. **Create field validators** (`mia_processor/metadata/validators.py`)
   - Language code validation (ISO 639-1)
   - Date format validation (ISO 8601)
   - Confidence score bounds (0.0-1.0)
   - Section type enumeration

3. **Create migration utilities** (`mia_processor/metadata/migration.py`)
   - Convert old 8-field schema → new 5-layer schema
   - Backfill missing fields with defaults
   - Preserve existing extracted metadata
   - Generate migration report

4. **Update `mia_processor.py`**
   - Replace `DocumentMetadata` import
   - Update `extract_metadata_from_html()` to populate new fields
   - Add encoding detection/normalization
   - Add document structure analysis (heading counts, ToC detection)

5. **Create comprehensive tests** (`tests/unit/test_metadata_schema.py`)
   - Schema validation tests (required fields, types)
   - Serialization round-trip tests
   - Migration tests (old → new schema)
   - Edge case handling (missing fields, malformed data)

## Acceptance Criteria

- [ ] All 5 metadata layers defined with proper types
- [ ] `DocumentMetadata` class supports 40+ fields
- [ ] Required fields always populated (source_url, title, content_hash, section_type, language)
- [ ] Provenance tracking for all extracted fields (author_source, date_source)
- [ ] Confidence scoring for extracted metadata (0.0-1.0 range)
- [ ] Encoding normalization (62% ISO-8859-1 → UTF-8 conversion)
- [ ] Serialization to/from flat dictionaries for storage
- [ ] Migration script successfully converts existing processed documents
- [ ] 100% test coverage for schema validation
- [ ] YAML frontmatter and JSON sidecar support maintained
- [ ] Performance: <5ms overhead per document for schema instantiation

## Files to Modify

**New Files:**
- `mia_processor/metadata/schema.py` - 5-layer metadata dataclasses
- `mia_processor/metadata/validators.py` - Field validation logic
- `mia_processor/metadata/migration.py` - Old → new schema migration
- `tests/unit/test_metadata_schema.py` - Schema validation tests
- `tests/fixtures/sample_documents.py` - Test data for all 6 sections

**Modified Files:**
- `mia_processor.py` - Update imports, metadata extraction
- `rag_ingest.py` - Handle new metadata structure in chunks
- `query_example.py` - Display new metadata fields in results

## Dependencies

**External Dependencies:**
- `chardet` library - Character encoding detection (ISO-8859-1 → UTF-8)
- BeautifulSoup - HTML structure analysis (already required)

**Internal Dependencies:**
- Corpus analysis specs: `docs/corpus-analysis/06-metadata-unified-schema.md` (defines schema)
- HTML structure analyzer: `scripts/html_structure_analyzer.py` (for document_structure metadata)

**Blocks:**
- Multi-Source Extraction Pipeline (needs schema definition first)
- Glossary Entity Linker (needs canonical_author_ids fields)
- Section-Specific Extractors (need section-specific fields)

## Related Issues

- Part of Code Refactoring Project (Stream 4: Metadata Pipeline)
- Blocks: Multi-Source Extraction Pipeline (#TBD)
- Blocks: Glossary Entity Linker (#TBD)
- Blocks: Section-Specific Extractors (#TBD)
- Related: Corpus Analysis (✅ Complete - schema defined)

## Estimated Effort

**Time**: 12-16 hours
**Complexity**: Medium-High (40+ fields, 5 layers, migration logic)
**Priority**: CRITICAL (blocks all other metadata work)

## Success Metrics

**Coverage Targets** (baseline for extraction pipeline):
- **Required fields**: 100% populated (source_url, title, content_hash, section_type, language)
- **Encoding normalization**: 100% UTF-8 (handle 62% ISO-8859-1 conversion)
- **Schema validation**: 100% of processed documents pass validation
- **Migration success**: 100% of existing documents converted without data loss

**Performance Targets**:
- Schema instantiation: <5ms per document
- Serialization: <2ms per document
- Validation: <1ms per document

## Example Usage

```python
# Before (8 fields)
metadata = DocumentMetadata(
    source_url="https://marxists.org/archive/marx/works/1867-c1/ch01.htm",
    title="Capital Vol. I, Chapter 1",
    author="Karl Marx",  # No provenance, no confidence
    date="1867",  # No source tracking
    language="en",
    doc_type="html",
    word_count=5432,
    content_hash="abc123"
)

# After (40+ fields, 5 layers)
metadata = DocumentMetadata(
    core=CoreIdentification(
        source_url="https://marxists.org/archive/marx/works/1867-c1/ch01.htm",
        title="Capital Vol. I, Chapter 1: Commodities",
        content_hash="abc123",
        section_type="archive",
        language="en",
        encoding_original="UTF-8",
        encoding_normalized=True
    ),
    authorship=AuthorshipProvenance(
        authors=["Karl Marx"],
        author_source="path",
        author_confidence=1.0,
        transcribers=[],
        organizations=[],
        recipients=[],
        canonical_author_ids=["marx-karl-1818"]
    ),
    temporal=TemporalClassification(
        date_written="1867",
        date_published="1867",
        date_source="path",
        date_confidence=1.0,
        time_period="1860s",
        movement_affiliation=["Scientific Socialism"],
        subject_categories=[]
    ),
    technical=TechnicalProcessing(
        doc_type="html",
        file_size_bytes=45321,
        word_count=5432,
        character_count=32145,
        heading_structure={"h1": 1, "h2": 0, "h3": 4},
        has_toc=False,
        is_anthology=False,
        is_git_lfs=False,
        processing_timestamp="2025-11-08T12:00:00Z",
        processor_version="2.0.0"
    ),
    semantic=SemanticEnrichment(
        keywords=["commodity", "use-value", "exchange-value", "labor"],
        meta_description=None,
        cross_references=[],
        glossary_entities=["commodity", "use-value", "exchange-value"],
        breadcrumb_path=["Marx", "Capital Vol. I", "Chapter 1"],
        collection_id="marx-capital-v1",
        work_id="capital-v1-ch01",
        chapter_number=1,
        newspaper_name=None,
        issue_date=None
    )
)

# Serialize for storage
flat_dict = metadata.to_dict()

# Deserialize from storage
metadata_restored = DocumentMetadata.from_dict(flat_dict)
```

## References

- Corpus Analysis: `docs/corpus-analysis/06-metadata-unified-schema.md`
- Current Implementation: `mia_processor.py:33-44`
- Refactoring Project: `.github/projects/refactoring-code-complexity.md`
- Metadata Coverage Analysis: `docs/corpus-analysis/01-archive-metadata-analysis.md` through `05-reference-metadata-analysis.md`
