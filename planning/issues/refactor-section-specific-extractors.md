---
title: "Refactoring: Implement Section-Specific Extraction Rules"
labels: refactoring, metadata, instance1
assignees: ""
---

## Problem Statement

The current metadata extraction treats all MIA sections uniformly, but **each section has unique patterns** that generic extraction misses:

**Archive Section** (from `docs/corpus-analysis/01-archive-metadata-analysis.md`):
- ❌ Missing: Work collection detection (e.g., "Capital Vol. I" chapters)
- ❌ Missing: Chapter numbering extraction
- ❌ Missing: Letter recipient detection (correspondence works)

**ETOL Section** (from `docs/corpus-analysis/02-etol-metadata-analysis.md`):
- ❌ Missing: Transcriber vs. author disambiguation
- ❌ Missing: Newspaper detection (source periodical)
- ❌ Missing: Movement affiliation extraction (Trotskyist, Third Camp, etc.)
- ❌ Missing: Provenance parsing ("Written: Oct 1917, First Published: 1924")

**EROL Section** (from `docs/corpus-analysis/03-erol-metadata-analysis.md`):
- ❌ Missing: Organization attribution (MLOC, RCP, CPUSA, etc.)
- ❌ Missing: NCM classification (New Communist Movement works)
- ❌ Missing: Unique h3-as-title handling (EROL uses h3 for document titles)

**Subject Section** (from `docs/corpus-analysis/03-subject-metadata-analysis.md`):
- ❌ Missing: Anthology detection (multi-work compilations)
- ❌ Missing: Peking Review special handling (unique structure)
- ❌ Missing: Cross-reference network extraction
- ❌ Missing: Subject category breadcrumb parsing

**Glossary Section** (from `docs/corpus-analysis/04-glossary-metadata-analysis.md`):
- ❌ Missing: Entry type classification (person, organization, concept)
- ❌ Missing: Cross-reference count tracking
- ❌ Missing: Canonical ID generation

**Reference Section** (from `docs/corpus-analysis/05-reference-metadata-analysis.md`):
- ❌ Missing: Non-Marxist author detection
- ❌ Missing: Git LFS verification (large PDFs)
- ❌ Missing: Subject/category organization

**Generic extraction fails to capture these section-specific patterns**, losing critical metadata.

## Current Implementation

```python
# Current: One-size-fits-all extraction (no section-specific logic)
def extract_metadata_from_html(html_content, file_path):
    # Same logic for all sections
    author = extract_author_from_path(file_path)  # Doesn't work for ETOL/EROL
    date = extract_date_from_path(file_path)  # Misses ETOL provenance dates
    # ...
    return DocumentMetadata(author=author, date=date, ...)
```

**Issues:**
- No section detection logic
- No section-specific HTML structure handling
- No section-specific metadata fields populated
- Misses 30-50% of metadata in ETOL, EROL, Subject sections

## Proposed Solution

Implement **Section-Specific Extractor Classes** with **Template Method Pattern**:

### Architecture

```python
# 1. Base Section Extractor (Template Method Pattern)
class SectionExtractor(ABC):
    """Abstract base for section-specific metadata extraction"""

    def extract(self, soup: BeautifulSoup, file_path: Path) -> DocumentMetadata:
        """Template method - defines extraction workflow"""
        # Standard extraction (all sections)
        core = self.extract_core_identification(soup, file_path)
        authorship = self.extract_authorship(soup, file_path)
        temporal = self.extract_temporal(soup, file_path)
        technical = self.extract_technical(soup, file_path)
        semantic = self.extract_semantic(soup, file_path)

        # Section-specific enrichment (override in subclasses)
        authorship = self.enrich_authorship(soup, file_path, authorship)
        temporal = self.enrich_temporal(soup, file_path, temporal)
        semantic = self.enrich_semantic(soup, file_path, semantic)

        return DocumentMetadata(
            core=core,
            authorship=authorship,
            temporal=temporal,
            technical=technical,
            semantic=semantic
        )

    # Standard extraction (implemented in base class)
    def extract_core_identification(self, soup, file_path) -> CoreIdentification:
        """Extract basic identification (all sections)"""
        # ...

    @abstractmethod
    def extract_authorship(self, soup, file_path) -> AuthorshipProvenance:
        """Extract authorship - section-specific implementation required"""

    @abstractmethod
    def extract_temporal(self, soup, file_path) -> TemporalClassification:
        """Extract dates - section-specific implementation required"""

    # Section-specific enrichment (optional overrides)
    def enrich_authorship(self, soup, file_path, authorship) -> AuthorshipProvenance:
        """Enrich authorship with section-specific metadata"""
        return authorship  # Default: no enrichment

    def enrich_temporal(self, soup, file_path, temporal) -> TemporalClassification:
        """Enrich temporal with section-specific metadata"""
        return temporal  # Default: no enrichment

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """Enrich semantic with section-specific metadata"""
        return semantic  # Default: no enrichment

# 2. Archive Section Extractor
class ArchiveSectionExtractor(SectionExtractor):
    """Archive-specific extraction: work collections, chapters, letters"""

    def extract_authorship(self, soup, file_path) -> AuthorshipProvenance:
        """Archive: 100% path-based author extraction"""
        # /archive/marx/works/1867-c1/ch01.htm → "Marx, Karl"
        parts = file_path.parts
        archive_idx = parts.index('archive')
        author_slug = parts[archive_idx + 1]
        author = self._slug_to_canonical_name(author_slug)

        return AuthorshipProvenance(
            authors=[author],
            author_source='path',
            author_confidence=1.0,
            transcribers=[],
            organizations=[],
            recipients=[],
            canonical_author_ids=[]
        )

    def extract_temporal(self, soup, file_path) -> TemporalClassification:
        """Archive: Extract date from path (e.g., /1867-c1/)"""
        # Pattern: /works/YYYY-work-id/ or /works/YYYYs/
        match = re.search(r'/(\d{4})s?[/-]', str(file_path))
        if match:
            year = match.group(1)
            return TemporalClassification(
                date_written=year,
                date_published=year,
                date_source='path',
                date_confidence=1.0,
                time_period=self._year_to_period(year),
                movement_affiliation=[],
                subject_categories=[]
            )

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """Archive: Extract work collection, chapter number, letter recipients"""
        # Work collection detection
        # /archive/marx/works/1867-c1/ch01.htm → collection: "capital-v1"
        collection_id = self._detect_work_collection(file_path)

        # Chapter number
        # ch01.htm → chapter_number: 1
        chapter_number = self._extract_chapter_number(file_path)

        # Letter recipient detection (if correspondence)
        # "Letter to Engels" → recipients: ["Engels, Friedrich"]
        recipients = self._extract_letter_recipients(soup)

        semantic.collection_id = collection_id
        semantic.work_id = f"{collection_id}-{file_path.stem}"
        semantic.chapter_number = chapter_number

        # Add recipients to cross-references
        if recipients:
            semantic.cross_references.extend(recipients)

        return semantic

    def _detect_work_collection(self, file_path: Path) -> Optional[str]:
        """Detect work collection from path patterns"""
        # Known collections: /1867-c1/ → "capital-v1", /1848/ → "communist-manifesto"
        collections = {
            '1867-c1': 'capital-v1',
            '1885-c2': 'capital-v2',
            '1894-c3': 'capital-v3',
            '1848': 'communist-manifesto',
            '1845': 'german-ideology',
            # ... from corpus analysis
        }
        for pattern, collection_id in collections.items():
            if pattern in str(file_path):
                return collection_id
        return None

# 3. ETOL Section Extractor
class ETOLSectionExtractor(SectionExtractor):
    """ETOL-specific extraction: transcribers, newspapers, provenance dates"""

    def extract_authorship(self, soup, file_path) -> AuthorshipProvenance:
        """ETOL: Multi-source author extraction with transcriber detection"""
        # Pattern: "Author: Title" or "Author (Year)"
        title = soup.find('title')
        authors = []
        transcribers = []

        if title:
            # Try title pattern extraction
            match = re.match(r'^([A-Z][a-z]+(?: [A-Z][a-z]+)*?):\s+', title.text)
            if match:
                authors.append(match.group(1))

        # Transcriber detection (ETOL-specific)
        # Look for "Transcribed by:" in content
        transcriber_tag = soup.find('b', string=re.compile(r'Transcribed by:', re.I))
        if transcriber_tag:
            transcriber = transcriber_tag.next_sibling.strip()
            transcribers.append(transcriber)

        return AuthorshipProvenance(
            authors=authors,
            author_source='title' if authors else 'unknown',
            author_confidence=0.85 if authors else 0.0,
            transcribers=transcribers,
            organizations=[],
            recipients=[],
            canonical_author_ids=[]
        )

    def extract_temporal(self, soup, file_path) -> TemporalClassification:
        """ETOL: Parse provenance info (Written/Published dates)"""
        # ETOL-specific provenance patterns:
        # "Written: October 1917"
        # "First Published: 1924"

        date_written = None
        date_published = None

        written_tag = soup.find('b', string=re.compile(r'Written:', re.I))
        if written_tag:
            date_written = self._parse_date_string(written_tag.next_sibling)

        published_tag = soup.find('b', string=re.compile(r'First Published:', re.I))
        if published_tag:
            date_published = self._parse_date_string(published_tag.next_sibling)

        return TemporalClassification(
            date_written=date_written,
            date_published=date_published,
            date_source='content' if date_written else 'unknown',
            date_confidence=0.90 if date_written else 0.0,
            time_period=None,
            movement_affiliation=[],
            subject_categories=[]
        )

    def enrich_temporal(self, soup, file_path, temporal) -> TemporalClassification:
        """ETOL: Extract movement affiliation (Trotskyist, Third Camp, etc.)"""
        # Extract from keywords or path
        # /history/etol/writers/trotskyist/ → movement: "Trotskyist"

        movement_affiliation = []
        if 'trotskyist' in str(file_path).lower():
            movement_affiliation.append('Trotskyist')
        elif 'third-camp' in str(file_path).lower():
            movement_affiliation.append('Third Camp')
        # ... more movement patterns

        temporal.movement_affiliation = movement_affiliation
        return temporal

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """ETOL: Extract newspaper name and issue date"""
        # ETOL newspapers: "From: The Militant, Vol. 5 No. 12, March 22, 1941"

        newspaper_tag = soup.find('b', string=re.compile(r'From:', re.I))
        if newspaper_tag:
            newspaper_info = newspaper_tag.next_sibling.strip()
            # Parse: "The Militant, Vol. 5 No. 12, March 22, 1941"
            newspaper_name, issue_date = self._parse_newspaper_info(newspaper_info)
            semantic.newspaper_name = newspaper_name
            semantic.issue_date = issue_date

        return semantic

# 4. EROL Section Extractor
class EROLSectionExtractor(SectionExtractor):
    """EROL-specific extraction: organization attribution, NCM classification"""

    ORGANIZATIONS = [
        'MLOC', 'RCP', 'CPUSA', 'SWP', 'ISO', 'DSA', 'WWP', 'PSL',
        # ... from corpus analysis
    ]

    def extract_authorship(self, soup, file_path) -> AuthorshipProvenance:
        """EROL: Extract organization attribution from title/keywords"""
        organizations = []

        # Check title for organization names
        title = soup.find('title')
        if title:
            for org in self.ORGANIZATIONS:
                if org.lower() in title.text.lower():
                    organizations.append(org)

        # Check keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            for org in self.ORGANIZATIONS:
                if org.lower() in keywords_meta['content'].lower():
                    if org not in organizations:
                        organizations.append(org)

        return AuthorshipProvenance(
            authors=[],  # EROL often doesn't have individual authors
            author_source='organization',
            author_confidence=0.95 if organizations else 0.0,
            transcribers=[],
            organizations=organizations,
            recipients=[],
            canonical_author_ids=[]
        )

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """EROL: Classify NCM (New Communist Movement) works"""
        # NCM period: 1970s-1980s
        # Keywords: anti-revisionist, Marxist-Leninist, etc.

        is_ncm = False
        ncm_keywords = ['anti-revisionist', 'marxist-leninist', 'new communist movement']

        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            keywords_lower = keywords_meta['content'].lower()
            if any(kw in keywords_lower for kw in ncm_keywords):
                is_ncm = True

        if is_ncm:
            semantic.keywords.append('New Communist Movement')

        return semantic

    def extract_core_identification(self, soup, file_path) -> CoreIdentification:
        """EROL: Override title extraction (uses h3 instead of h1)"""
        # EROL unique pattern: uses <h3> for document titles
        h3 = soup.find('h3')
        title = h3.text.strip() if h3 else soup.find('title').text.strip()

        return CoreIdentification(
            source_url=self._path_to_url(file_path),
            title=title,
            content_hash='',  # Computed later
            section_type='erol',
            language='en',
            encoding_original='UTF-8',
            encoding_normalized=True
        )

# 5. Subject Section Extractor
class SubjectSectionExtractor(SectionExtractor):
    """Subject-specific extraction: anthologies, categories, Peking Review"""

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """Subject: Detect anthologies, extract breadcrumb categories"""
        # Anthology detection (multi-work compilations)
        # Look for multiple <h2> or <h3> sections indicating separate works
        headings = soup.find_all(['h2', 'h3'])
        is_anthology = len(headings) > 5  # Heuristic: >5 headings → anthology

        semantic.is_anthology = is_anthology

        # Extract subject categories from breadcrumb
        # <p><a href="/subject/">Subjects</a> » <a href="/subject/economy/">Economy</a> » ...</p>
        breadcrumb = self._extract_breadcrumb(soup)
        if breadcrumb:
            semantic.breadcrumb_path = breadcrumb
            semantic.subject_categories = breadcrumb

        # Peking Review special handling
        if 'peking-review' in str(file_path).lower():
            semantic.newspaper_name = 'Peking Review'
            # Extract issue date from path or title
            issue_date = self._extract_peking_review_date(file_path, soup)
            semantic.issue_date = issue_date

        return semantic

# 6. Glossary Section Extractor
class GlossarySectionExtractor(SectionExtractor):
    """Glossary-specific extraction: entry types, cross-reference counts"""

    def enrich_semantic(self, soup, file_path, semantic) -> SemanticEnrichment:
        """Glossary: Classify entry type, count cross-references"""
        # Entry type detection (person, organization, concept)
        # Heuristic: entries with (YYYY-YYYY) are people
        h1 = soup.find('h1')
        entry_type = 'concept'  # Default

        if h1 and re.search(r'\(\d{4}-\d{4}\)', h1.text):
            entry_type = 'person'
        elif any(org_word in h1.text.lower() for org_word in ['party', 'union', 'organization']):
            entry_type = 'organization'

        # Count cross-references
        see_also = soup.find('b', string=re.compile(r'See also:', re.I))
        cross_ref_count = 0
        if see_also:
            cross_ref_count = len(see_also.parent.find_all('a'))

        semantic.keywords.append(f"entry_type:{entry_type}")
        semantic.keywords.append(f"cross_ref_count:{cross_ref_count}")

        return semantic

# 7. Reference Section Extractor
class ReferenceSectionExtractor(SectionExtractor):
    """Reference-specific extraction: non-Marxist authors, Git LFS detection"""

    def enrich_authorship(self, soup, file_path, authorship) -> AuthorshipProvenance:
        """Reference: Flag non-Marxist authors"""
        # Reference section contains non-Marxist authors (Aristotle, Hegel, etc.)
        authorship.author_source = 'path'
        authorship.author_confidence = 1.0
        # Could add flag: is_non_marxist = True

        return authorship

    def enrich_technical(self, soup, file_path, technical) -> TechnicalProcessing:
        """Reference: Check if file is stored in Git LFS"""
        # Large PDFs in Reference section may be in Git LFS
        # Check file size or .gitattributes

        is_git_lfs = False
        if file_path.suffix == '.pdf' and technical.file_size_bytes > 10 * 1024 * 1024:
            is_git_lfs = True  # Files >10MB likely in LFS

        technical.is_git_lfs = is_git_lfs
        return technical

# 8. Section Extractor Factory
class SectionExtractorFactory:
    """Factory for creating section-specific extractors"""

    @staticmethod
    def create(file_path: Path) -> SectionExtractor:
        """Detect section type from path and return appropriate extractor"""
        path_str = str(file_path).lower()

        if '/archive/' in path_str:
            return ArchiveSectionExtractor()
        elif '/history/etol/' in path_str:
            return ETOLSectionExtractor()
        elif '/history/erol/' in path_str:
            return EROLSectionExtractor()
        elif '/subject/' in path_str:
            return SubjectSectionExtractor()
        elif '/glossary/' in path_str:
            return GlossarySectionExtractor()
        elif '/reference/' in path_str:
            return ReferenceSectionExtractor()
        else:
            return SectionExtractor()  # Fallback: generic extractor
```

### Implementation Steps

1. **Create section extractor base** (`mia_processor/extractors/section_base.py`)
   - `SectionExtractor` abstract base class (Template Method pattern)
   - Standard extraction methods (core, authorship, temporal, technical, semantic)
   - Section-specific enrichment hooks

2. **Implement Archive extractor** (`mia_processor/extractors/archive_extractor.py`)
   - Work collection detection (Capital, Manifesto, etc.)
   - Chapter numbering extraction
   - Letter recipient detection

3. **Implement ETOL extractor** (`mia_processor/extractors/etol_extractor.py`)
   - Transcriber vs. author disambiguation
   - Newspaper detection (source periodical)
   - Movement affiliation extraction
   - Provenance date parsing

4. **Implement EROL extractor** (`mia_processor/extractors/erol_extractor.py`)
   - Organization attribution (MLOC, RCP, etc.)
   - NCM classification
   - h3-as-title handling

5. **Implement Subject extractor** (`mia_processor/extractors/subject_extractor.py`)
   - Anthology detection
   - Breadcrumb category extraction
   - Peking Review special handling

6. **Implement Glossary extractor** (`mia_processor/extractors/glossary_extractor.py`)
   - Entry type classification (person, organization, concept)
   - Cross-reference count tracking

7. **Implement Reference extractor** (`mia_processor/extractors/reference_extractor.py`)
   - Non-Marxist author flagging
   - Git LFS detection

8. **Create factory** (`mia_processor/extractors/factory.py`)
   - Section detection from file path
   - Extractor instantiation

9. **Integrate with `mia_processor.py`**
   - Replace generic extraction with factory-based section extraction
   - Populate all section-specific metadata fields

10. **Create section-specific tests** (`tests/unit/test_section_extractors.py`)
    - Unit tests for each section extractor
    - Validation against corpus analysis findings

## Acceptance Criteria

- [ ] All 6 section extractors implemented (Archive, ETOL, EROL, Subject, Glossary, Reference)
- [ ] Section detection from file path works 100% accurately
- [ ] **Archive-specific metadata**:
  - [ ] Work collection detection (Capital, Manifesto, etc.)
  - [ ] Chapter numbering extraction
  - [ ] Letter recipient detection
- [ ] **ETOL-specific metadata**:
  - [ ] Transcriber extraction (90%+ coverage)
  - [ ] Newspaper detection (80%+ coverage)
  - [ ] Movement affiliation (70%+ coverage)
  - [ ] Provenance date parsing (90%+ accuracy)
- [ ] **EROL-specific metadata**:
  - [ ] Organization attribution (95%+ coverage)
  - [ ] NCM classification
  - [ ] h3-as-title handling (100% accuracy)
- [ ] **Subject-specific metadata**:
  - [ ] Anthology detection (90%+ accuracy)
  - [ ] Breadcrumb category extraction (64%+ coverage)
  - [ ] Peking Review special handling
- [ ] **Glossary-specific metadata**:
  - [ ] Entry type classification (person, org, concept)
  - [ ] Cross-reference count tracking
- [ ] **Reference-specific metadata**:
  - [ ] Git LFS detection
- [ ] Performance: <20ms overhead per document for section-specific extraction
- [ ] Backward compatibility: Works with existing corpus

## Files to Modify

**New Files:**
- `mia_processor/extractors/section_base.py` - `SectionExtractor` base class
- `mia_processor/extractors/archive_extractor.py` - Archive section extractor
- `mia_processor/extractors/etol_extractor.py` - ETOL section extractor
- `mia_processor/extractors/erol_extractor.py` - EROL section extractor
- `mia_processor/extractors/subject_extractor.py` - Subject section extractor
- `mia_processor/extractors/glossary_extractor.py` - Glossary section extractor
- `mia_processor/extractors/reference_extractor.py` - Reference section extractor
- `mia_processor/extractors/factory.py` - Section extractor factory
- `tests/unit/test_section_extractors.py` - Section extractor tests

**Modified Files:**
- `mia_processor.py` - Replace generic extraction with factory-based section extraction

## Dependencies

**Internal Dependencies:**
- Unified Metadata Schema (#TBD) - Needs section-specific metadata fields
- Multi-Source Extraction Pipeline (#TBD) - Needs base extraction strategies

**Blocks:**
- Complete metadata coverage targets (85%+ author coverage)

## Related Issues

- Part of Code Refactoring Project (Stream 4: Metadata Pipeline)
- Blocked by: Unified Metadata Schema (#TBD)
- Blocked by: Multi-Source Extraction Pipeline (#TBD)
- Related: Corpus Analysis (✅ Complete - section patterns documented)

## Estimated Effort

**Time**: 8-12 hours
**Complexity**: Medium (6 extractors, section-specific patterns)
**Priority**: HIGH (critical for achieving metadata coverage targets)

## Success Metrics

**Section-Specific Metadata Population**:
- **Archive**: 100% work collection, 90%+ chapter numbers, 70%+ letter recipients
- **ETOL**: 90%+ transcribers, 80%+ newspapers, 70%+ movement affiliation
- **EROL**: 95%+ organization attribution, 100% NCM classification
- **Subject**: 90%+ anthology detection, 64%+ category extraction
- **Glossary**: 100% entry type, 100% cross-ref count
- **Reference**: 100% Git LFS detection

**Overall Coverage Improvement**:
- Before: ~70% author coverage (generic extraction)
- After: 85%+ author coverage (section-specific extraction)

## Example Usage

```python
# Before (generic extraction - misses section-specific metadata)
metadata = extract_metadata_from_html(html_content, file_path)
# metadata.semantic.newspaper_name = None (ETOL newspaper info lost)
# metadata.authorship.transcribers = [] (ETOL transcriber info lost)
# metadata.authorship.organizations = [] (EROL organization info lost)

# After (section-specific extraction)
factory = SectionExtractorFactory()
extractor = factory.create(file_path)  # Returns ETOLSectionExtractor for ETOL files
metadata = extractor.extract(soup, file_path)

# ETOL-specific metadata populated:
print(metadata.authorship.transcribers)
# Output: ["Ted Crawford"]

print(metadata.semantic.newspaper_name)
# Output: "The Militant"

print(metadata.semantic.issue_date)
# Output: "1941-03-22"

print(metadata.temporal.movement_affiliation)
# Output: ["Trotskyist"]

# EROL-specific metadata populated:
print(metadata.authorship.organizations)
# Output: ["MLOC", "RCP"]

# Archive-specific metadata populated:
print(metadata.semantic.collection_id)
# Output: "capital-v1"

print(metadata.semantic.chapter_number)
# Output: 1
```

## References

- Corpus Analysis (section patterns):
  - `docs/corpus-analysis/01-archive-metadata-analysis.md`
  - `docs/corpus-analysis/02-etol-metadata-analysis.md`
  - `docs/corpus-analysis/03-erol-metadata-analysis.md`
  - `docs/corpus-analysis/03-subject-metadata-analysis.md`
  - `docs/corpus-analysis/04-glossary-metadata-analysis.md`
  - `docs/corpus-analysis/05-reference-metadata-analysis.md`
- Unified Schema: `docs/corpus-analysis/06-metadata-unified-schema.md`
- Refactoring Project: `planning/projects/refactoring-code-complexity.md`
- Design Pattern: [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
