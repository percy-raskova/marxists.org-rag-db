# Marxists Internet Archive: Corpus Overview

**Total Size**: 121GB
**HTML Files**: 96,637
**PDF Files**: 21,141
**Top-Level Directories**: 67
**Investigation Date**: 2025-11-08
**Status**: Comprehensive structural analysis complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Corpus Composition](#corpus-composition)
3. [Major Sections](#major-sections)
4. [Comparative Analysis](#comparative-analysis)
5. [Priority Matrix](#priority-matrix)
6. [Scope Decisions](#scope-decisions)
7. [Investigation Status](#investigation-status)

---

## Executive Summary

The Marxists Internet Archive (MIA) is a **121GB corpus** containing approximately 96,637 HTML files and 21,141 PDFs across 67 top-level directories. The archive is organized into five primary sections:

1. **History Archive** (46GB, 38%) - Historical documents and labor movement periodicals
2. **Archive by Author** (4.5GB, 4%) - Theoretical works by 411 revolutionary thinkers
3. **Subject Archive** (9.1GB, 8%) - Thematic collections with expert curation
4. **Language Directories** (~28GB, 23%) - Content in 40+ languages
5. **Supporting Content** (~33GB, 27%) - Ebooks, audiobooks, site infrastructure

### Critical Insight: Corpus Architecture

**The 200GB estimate appears to include redundant formats and non-processable content.** The actual English-language theoretical and historical content is approximately **60GB**, structured with three distinct content types:

1. **Theoretical Works** (Archive section, 4.5GB) - Long-form theory, dense prose, hierarchical structure
2. **Historical Periodicals** (History section, 46GB) - Journalism, news articles, OCR-heavy PDFs
3. **Reference Materials** (Subject + Glossary, 9.2GB) - Curated collections, encyclopedia entries

Each content type requires different processing strategies, chunking approaches, and metadata schemas.

---

## Corpus Composition

### Size Distribution by Section

| Section | Size | % of Total | HTML Count | PDF Count | Content Type |
|---------|------|------------|------------|-----------|--------------|
| **History** | 46GB | 38% | ~15,000 | 5,043 | Labor periodicals, historical docs |
| **Languages** | ~28GB | 23% | ~30,000 | ~8,000 | Non-English translations |
| **Supporting** | ~33GB | 27% | N/A | N/A | Ebooks, audiobooks, infrastructure |
| **Subject** | 9.1GB | 8% | 2,259 | 1,412 | Thematic collections |
| **Archive** | 4.5GB | 4% | 28,962 | 6,637 | Theoretical works by author |
| **Glossary** | 62MB | <1% | 685 | 0 | Encyclopedia entries |
| **Other** | ~1GB | <1% | Variable | Variable | Admin, miscellaneous |

### English Content Breakdown

**Total English Content**: ~60GB

| Content Type | Size | Primary Use | Processing Complexity |
|--------------|------|-------------|----------------------|
| Theoretical Works (Archive) | 4.5GB | RAG query base | Medium |
| Historical Periodicals (History) | 46GB | Historical context | High (OCR) |
| Thematic Collections (Subject) | 9.1GB | Concept navigation | Medium |
| Reference (Glossary) | 62MB | Entity definitions | Low |

---

## Major Sections

### 1. History Archive (46GB)

**Path**: `/history/`
**Primary Content**: Historical documents, labor movement periodicals
**Processing Complexity**: HIGH (OCR-intensive)

#### 1.1 USA Publications (43GB - 93% of History Section)

**Path**: `/history/usa/pubs/`
**Structure**: Periodical archives organized by publication name

**Major Collections**:
- Daily Worker (1924-1926): 11GB
- Western Worker: 7.5GB
- Labor Defender: 5.2GB
- New Masses: 2.8GB
- Northwest Organizer: 2.4GB
- Workers' Age: 1.7GB
- 35+ other labor publications

**Characteristics**:
- Almost entirely PDF scans (5,043 PDFs)
- Organized chronologically by volume/issue
- Temporal metadata extremely precise (YYYY-MM-DD in filenames)
- Represents primary source documents from 1900-1980s
- Working-class journalism, not theoretical texts
- Variable OCR quality (pre-1990s issues)

**File Naming Pattern**:
```
v{vol}n{issue}-{date}-{abbrev}.pdf
Example: v02n085-apr-21-1925-DW.pdf
```

**Organizational Structure**:
```
/history/usa/pubs/{publication-name}/
  ├── {year}/
  │   ├── v{vol}n{issue}-{date}-{abbrev}.pdf
  │   └── index.htm (issue list)
  ├── index.htm (publication introduction)
  └── masthead.jpg
```

**Metadata Available**:
- Publication name
- Volume/issue numbers
- Exact publication dates
- Historical context in introduction pages
- Digitization provenance

**RAG Implications**:
- Requires OCR extraction pipeline
- Different reading level than Archive section (journalism vs theory)
- Temporal metadata critical for historical queries
- May need separate processing pipeline from theoretical works
- Question: Should periodicals be included in RAG, or focus on theory?

#### 1.2 USA Other Content (4GB)

- `/history/usa/culture/`: 4GB (workers' culture, songs, literature)
- `/history/usa/unions/`: 39MB (labor union documents)

#### 1.3 International History (<1GB)

- Argentina, Haiti (minimal content)

**Investigation Status**: Requires detailed investigation (see `02-history-section-spec.md` - TODO)

---

### 2. Archive by Author (4.5GB)

**Path**: `/archive/`
**File Count**: 28,962 HTML files, 6,637 PDFs
**Author Count**: 411 authors
**Processing Complexity**: MEDIUM

**Purpose**: Long-form theoretical works organized by author

**Organizational Pattern**:
```
/archive/{author-lastname}/
  ├── works/
  │   ├── {year}/
  │   │   ├── {work-slug}/
  │   │   │   ├── ch01.htm, ch02.htm...
  │   │   │   └── index.htm
  │   ├── date/index.htm (chronological work list)
  │   └── subject/index.htm (thematic work list)
  ├── letters/ (correspondence)
  ├── bio/ (biographical materials)
  ├── images/ (photos, portraits)
  └── index.htm (author overview)
```

**Largest Author Collections**:
1. Raya Dunayevskaya: 1.2GB
2. Daniel De Leon: 433MB
3. Joseph McCarney: 305MB
4. Lenin: 289MB
5. Marx: 261MB
6. William Z. Foster: 216MB
7. Lev Vygotsky: 169MB (psychology)
8. Alexander Luria: 162MB (psychology)
9. Trotsky: 86MB
10. Luxemburg: 32MB

**Characteristics**:
- Hierarchical work structure (work → part → chapter → section)
- Extensive footnote apparatus with bidirectional links
- Paragraph-level anchors for precise citation
- Rich cross-references between works
- Mix of HTML (preferred) and PDF (scanned books)
- Dense theoretical prose (500-1000 words/page)

**HTML Structure** (Detailed):
- DOCTYPE: HTML 4.0 Transitional
- Charset: ISO-8859-1 (requires UTF-8 conversion)
- Semantic CSS classes:
  - `class="title"`: Work titles
  - `class="fst"`: First paragraph (often has anchor)
  - `class="quoteb"`: Block quotes
  - `class="context"`: Historical context annotations
  - `class="information"`: Provenance (source publication, digitizer)

**Metadata Layers** (5 levels):
1. **File path**: author, year, work, chapter
2. **Meta tags**: author, title, classification
3. **Breadcrumb**: categorical navigation
4. **Semantic content**: curator annotations, provenance
5. **Content-derived**: word count, footnotes, reading time

**Linking Architecture**:
- Hierarchical breadcrumbs (work → chapter → section)
- Cross-references to related works (`<a href="../other-work/">`)
- Footnote links (`<a href="#footnote1">` ↔ `<a name="footnote1">`)
- Citation anchors (`<a name="s1p05">` for section 1, paragraph 5)

**Chunking Recommendation**: Paragraph-level with hierarchical context preservation

**Investigation Status**: ✅ Complete (see `01-archive-section-analysis.md`)

---

### 3. Subject Archive (9.1GB)

**Path**: `/subject/`
**File Count**: 2,259 HTML files, 1,412 PDFs
**Category Count**: 50 thematic collections
**Processing Complexity**: MEDIUM

**Purpose**: Curated thematic collections with expert annotations

#### 3.1 China Subject Section (8.5GB - 93% of Subject Section)

**Path**: `/subject/china/`
**Content**: Chinese Revolution materials

**Breakdown**:
- Peking Review (1958-2006): 8.4GB, 1,376 PDFs
- Documents: 31MB (HTML documents)
- Music: 44MB (revolutionary songs)

**Organizational Pattern**:
```
/subject/china/peking-review/
  ├── {year}/
  │   ├── PR{year}-{issue}.pdf (full issue scans)
  │   ├── PR{year}-{issue}a.htm (article 1 extracted)
  │   └── PR{year}-{issue}b.htm (article 2 extracted)
  └── index.htm (year/issue index)
```

**Characteristics**:
- Complete run of Peking Review periodical (1958-2006)
- Mix of full-issue PDFs and extracted HTML articles
- Represents Maoist period primary sources
- Organized by year and issue number
- Question: Overlap with Archive section (Mao's works)? Duplicate content?

#### 3.2 Other Subject Sections (600MB)

**Major Categories**:
- Art & Literature: 427MB
- Political Economy: 51MB
- Women: 38MB
- LGBTQ: 28MB
- Africa: 19MB
- Fascism: 11MB
- Psychology, Philosophy, Education, Ethics: <10MB each

**Organizational Pattern**:
```
/subject/{topic}/
  ├── index.htm (curated overview with context annotations)
  ├── {subtopic}/
  │   └── works from multiple authors
  └── [links to /archive/{author}/ works]
```

**Unique Characteristics**:
- Cross-references to Archive section
- Curator annotations explaining significance (`class="context"`)
- Multi-author thematic groupings
- Expert-written reading guides
- Acts as metadata layer over Archive content

**Chunking Recommendation**:
- Treat as metadata enhancement layer
- Extract curator annotations as concept definitions
- Build concept-to-work mappings for query expansion

**Investigation Status**: Requires detailed investigation (see `03-subject-section-spec.md` - TODO)

---

### 4. Glossary/Encyclopedia (62MB)

**Path**: `/glossary/`
**File Count**: 685 HTML files
**Processing Complexity**: LOW

**Purpose**: Encyclopedia-style reference entries

**Structure**:
```
/glossary/
  ├── {a-z}.htm (alphabetical term indexes)
  ├── terms/{letter}/ (term definitions)
  ├── people/{letter}/ (biographical entries)
  ├── events/ (historical events)
  ├── orgs/ (organizations)
  ├── periodicals/ (publication descriptions)
  └── places/ (geographic locations)
```

**Entry Types**:
- **Terms**: Theoretical concepts (e.g., "surplus value", "dialectics")
- **People**: Biographical sketches (50-500 words)
- **Events**: Historical event summaries (e.g., "Paris Commune")
- **Organizations**: Group histories (e.g., "First International")
- **Periodicals**: Publication overviews
- **Places**: Geographic context

**Characteristics**:
- Encyclopedia-style entries (50-500 words each)
- Extensive cross-linking to Archive works
- Definition-focused
- No original theoretical content (points to Archive)
- Serves as knowledge graph backbone

**RAG Implications**:
- Use for entity extraction and disambiguation
- Build knowledge graph nodes (people, events, concepts)
- Enhance retrieval with contextual definitions
- Query expansion via related entries

**Chunking Recommendation**: Entry-level chunks (one entry = one chunk)

**Investigation Status**: Requires lightweight investigation (see `04-glossary-section-spec.md` - TODO)

---

### 5. Language Directories (~28GB)

**Total**: 40+ language directories
**Processing Complexity**: OUT OF SCOPE (for English-only RAG)

**Major Language Sections**:
- Chinese (`/chinese/`): 21GB
- Spanish (`/espanol/`): 4.2GB
- Russian (`/russkij/`): 1.2GB
- French (`/francais/`): 1.1GB
- German (`/deutsch/`): 110MB
- Italian (`/italiano/`): 44MB
- 35+ other languages: <50MB each

**Organizational Pattern**:
- Often mirrors English structure: `/espanol/archivo/{author}/`
- Some parallel translations of English content
- Some unique content not in English archive
- Variable completeness (some languages nearly complete, others minimal)

**RAG Implications**:
- Out of scope for English-only RAG
- Potential future multilingual expansion
- Cross-lingual linking opportunities (parallel texts)
- Translation quality varies

**Investigation Status**: Low priority (see `05-language-sections-spec.md` - Future work)

---

### 6. Supporting Content (~33GB)

**Purpose**: Alternative formats and site infrastructure
**Processing Complexity**: OUT OF SCOPE

**Likely Contents**:
- `/ebooks/`: E-book format conversions (EPUB, MOBI)
- `/audiobooks/`: Audio versions of works
- `/css/`, `/admin/`: Site infrastructure
- Image files (portraits, diagrams, mastheads)
- JavaScript, stylesheets
- Duplicate formats (same content, multiple formats)

**RAG Implications**: Not processable content; may contain useful metadata files

---

## Comparative Analysis

### Universal Patterns (Across All Sections)

These patterns appear in Archive, Subject, History, and Glossary sections:

#### 1. HTML Structure Patterns

- **DOCTYPE**: HTML 4.0 Transitional (consistent)
- **Charset**: ISO-8859-1 (needs UTF-8 conversion for processing)
- **Semantic CSS classes**:
  - `class="title"`: Titles
  - `class="fst"`: First paragraphs
  - `class="quoteb"`: Block quotes
  - `class="context"`: Curator/historical context
  - `class="information"`: Provenance metadata

#### 2. Metadata Schema Patterns

All sections include:
- **Path-based metadata**: Extractable from file paths
- **HTML meta tags**: author, description, classification
- **Breadcrumb navigation**: Hierarchical location
- **Provenance**: Source publication, digitizer, transcriber

#### 3. Link Architecture Patterns

- **Hierarchical breadcrumbs**: Section → subsection → page
- **Cross-references**: Links between related content
- **Bidirectional footnotes**: Text ↔ footnote with anchors
- **Paragraph-level anchors**: `<a name="##">` for precise citation

#### 4. Editorial Apparatus Patterns

- **Curator context annotations**: `class="context"` explaining significance
- **Scholarly footnotes**: Numbered, linked, bidirectional
- **Translation notes**: Editorial comments on translation choices
- **Source citations**: Original publication information

### Section-Specific Patterns

#### Archive Section (Theoretical Works)

**Unique Characteristics**:
- Long-form texts (10,000+ words typical)
- Chapter/section hierarchy with anchors
- Extensive footnote apparatus (10-50+ footnotes per chapter)
- Dense theoretical prose (500-1000 words/page)
- Cross-references to author's other works

**Chunking Strategy**: Paragraph-level with hierarchical context

**Metadata Focus**: Author, work, temporal location, classification

**Query Patterns**: "What did Marx say about X?", "Explain surplus value"

#### History Section (Periodicals)

**Unique Characteristics**:
- Short articles (200-1000 words)
- News/journalism writing style
- Date-precise (exact publication date critical)
- PDFs dominant (OCR required)
- Working-class audience (different register)

**Chunking Strategy**: Article-level (each article = one chunk)

**Metadata Focus**: Publication, date, issue, historical period

**Query Patterns**: "What happened in 1925?", "Labor movement in 1930s"

#### Subject Section (Curated Collections)

**Unique Characteristics**:
- Expert-curated reading lists
- Context annotations explaining why works matter
- Multi-author thematic compilations
- Heavy cross-referencing to Archive
- Acts as navigation layer

**Chunking Strategy**: Treat as metadata enhancement

**Metadata Focus**: Theme, curator annotations, concept relationships

**Query Patterns**: "Best works on political economy", "Introduction to dialectics"

#### Glossary Section (Reference)

**Unique Characteristics**:
- Encyclopedia entries (50-500 words)
- Definition-focused (not argumentative)
- Extensive cross-linking (web of concepts)
- No original content (points to Archive)
- Serves as knowledge graph

**Chunking Strategy**: Entry-level (one entry = one chunk)

**Metadata Focus**: Entry type (person/term/event), related entries

**Query Patterns**: "Who was Rosa Luxemburg?", "Define dialectical materialism"

---

## Priority Matrix

### Section Investigation Priorities

| Section | Size | Complexity | In-Scope? | Investigation Priority | RAG Priority | Status |
|---------|------|------------|-----------|----------------------|--------------|--------|
| **Archive** (Theory) | 4.5GB | High | ✅ Yes | COMPLETED | **HIGH** | ✅ |
| **History/USA/Pubs** (Periodicals) | 43GB | Medium | ❓ TBD | **HIGH** | **MEDIUM** | TODO |
| **Subject/China** (Peking Review) | 8.5GB | Medium | ❓ TBD | **HIGH** | **MEDIUM** | TODO |
| **Subject** (Other) | 600MB | Medium | ✅ Yes | MEDIUM | **HIGH** | TODO |
| **Glossary** | 62MB | Low | ✅ Yes | MEDIUM | **HIGH** | TODO |
| **Languages/Chinese** | 21GB | Unknown | ❌ No | LOW | LOW | Future |
| **Languages/Spanish** | 4.2GB | Unknown | ❌ No | LOW | LOW | Future |
| **Languages** (Other) | ~3GB | Unknown | ❌ No | LOW | LOW | Future |
| **Supporting** | ~33GB | N/A | ❌ No | N/A | N/A | Skip |

### Rationale for Priorities

**HIGH Priority Investigations**:
- **Archive**: ✅ Complete - Core theoretical content, well-structured, manageable size
- **History/USA/Pubs** (43GB): Needs scope decision - OCR-intensive, large, uncertain ROI
- **Subject/China** (8.5GB): Needs overlap analysis with Archive Mao content

**MEDIUM Priority Investigations**:
- **Subject (other)**: Curator annotations are valuable for query expansion
- **Glossary**: Small, low-complexity, high value for entity extraction

**LOW Priority**:
- **Language sections**: Out of scope for English RAG (future multilingual expansion)

**SKIP**:
- **Supporting content**: Alternative formats, not processable text

---

## Scope Decisions

### Critical Questions Requiring User Input

#### 1. Periodical Inclusion

**Question**: Should labor periodicals (History/USA/Pubs, 43GB) be included in RAG?

**Pros**:
- Primary historical sources
- Working-class perspective
- Rich temporal metadata
- Contextualizes theoretical works

**Cons**:
- OCR quality variable (pre-1950s poor)
- Different content type (journalism vs theory)
- Massive size (43GB = 90% of total)
- Different use case (historical research vs theoretical queries)

**Recommendation**: **Start without periodicals, add later if needed**
- Focus initial RAG on Archive section (4.5GB of theory)
- Add Subject and Glossary (9.2GB total for complete RAG)
- Periodicals can be separate RAG instance for historical queries

#### 2. Peking Review Inclusion

**Question**: Should Peking Review (8.4GB) be included?

**Pros**:
- Important historical documents
- Maoist theory and practice
- Complete chronological run (1958-2006)

**Cons**:
- Mostly PDFs (OCR required)
- May duplicate Archive section (Mao's works already in Archive)
- Large size relative to other Subject sections

**Recommendation**: **Investigate overlap first**
- Check if Peking Review articles duplicate Archive/Mao content
- If unique: Include HTML articles, defer PDFs
- If duplicate: Skip and rely on Archive content

#### 3. Language Scope

**Question**: English only, or multilingual RAG?

**English-only (Recommended for V1)**:
- Size: ~60GB (Archive 4.5GB + History 46GB + Subject 9.1GB + Glossary 0.06GB)
- Processing: Simpler, no translation alignment
- Timeline: Faster to production

**Multilingual (Future V2)**:
- Size: 121GB+ (includes 28GB language content)
- Processing: Requires translation alignment, parallel text detection
- Value: Serves non-English speakers, cross-lingual queries
- Prioritize: Spanish (4.2GB), French (1.1GB), Russian (1.2GB)

**Recommendation**: **English-only for V1, plan multilingual V2**

#### 4. PDF Processing Quality Threshold

**Question**: What quality threshold for OCR?

**Options**:
1. **Accept all PDFs** (6,637 in Archive + 5,043 in History)
   - Pro: Complete coverage
   - Con: Variable quality, OCR errors

2. **Only post-1950s PDFs** (better OCR quality)
   - Pro: Higher accuracy
   - Con: Loses historical documents

3. **Prefer HTML, PDFs only where no HTML exists**
   - Pro: Best quality, minimal OCR errors
   - Con: Incomplete coverage

**Recommendation**: **Option 3 - HTML-first strategy**
- Process all HTML files (high quality)
- For PDFs: Check if HTML version exists
- If no HTML: Process PDF with quality check
- Flag low-confidence OCR for manual review

---

## Investigation Status

### Completed Investigations

✅ **01-archive-section-analysis.md**
- Section: Archive (by author)
- Size: 4.5GB, 411 authors
- Status: Complete detailed analysis
- Findings: 5-layer metadata schema, paragraph-level chunking, hierarchical structure
- Ready for: RAG implementation

### Planned Investigations

📋 **02-history-section-spec.md** (TODO)
- Section: History/USA/Pubs (labor periodicals)
- Size: 43GB, 5,043 PDFs
- Priority: HIGH (pending scope decision)
- Focus: PDF quality assessment, article extraction, temporal metadata
- Estimated tokens: 20,000-30,000

📋 **03-subject-section-spec.md** (TODO)
- Section: Subject (thematic collections)
- Size: 9.1GB (including Peking Review)
- Priority: HIGH
- Focus: Curator annotations, concept mappings, overlap analysis
- Estimated tokens: 15,000-25,000

📋 **04-glossary-section-spec.md** (TODO)
- Section: Glossary (encyclopedia)
- Size: 62MB, 685 files
- Priority: MEDIUM
- Focus: Entry types, knowledge graph structure, cross-references
- Estimated tokens: 5,000-10,000

📋 **05-language-sections-spec.md** (Future)
- Sections: 40+ language directories
- Size: ~28GB
- Priority: LOW (out of scope for English RAG V1)
- Focus: Parallel text detection, translation quality, future expansion
- Estimated tokens: 10,000-15,000

📋 **06-metadata-unified-schema.md** (TODO)
- Purpose: Cross-section metadata schema
- Combines: Archive, Subject, History, Glossary schemas
- Priority: HIGH (required for RAG implementation)
- Output: Unified dataclass, extraction pipeline spec
- Estimated tokens: 10,000-15,000

### Investigation Methodology

All investigations follow: **00-investigation-methodology-spec.md**

**Key Principles**:
1. Stratified sampling (size, time, type, depth)
2. Computational verification (grep, find commands)
3. Token efficiency (structure extraction, not content reading)
4. Pattern documentation with confidence levels
5. Actionable specifications (code-ready)

**Average Investigation**:
- Tokens used: 15,000-25,000 per section
- Time: 30-60 minutes (including sampling and verification)
- Output: Complete section specification document

---

## Recommended Processing Order

### Phase 1: Core RAG (Archive Section Only)

**Content**: 4.5GB theoretical works
**Timeline**: 1-2 weeks
**Output**: Working RAG with 411 authors, ~30,000 documents

**Steps**:
1. Implement metadata extraction (5-layer schema from 01-archive-section-analysis.md)
2. Build HTML-to-markdown pipeline with footnote preservation
3. Implement paragraph-level chunking with hierarchical context
4. Ingest to vector database (Qdrant recommended)
5. Build query interface with author/work/date filtering

**Success Metric**: "What did Marx say about surplus value?" returns relevant paragraphs

### Phase 2: Enhanced RAG (Archive + Subject + Glossary)

**Content**: 4.5GB + 600MB + 62MB = ~5.2GB (excluding Peking Review)
**Timeline**: +1 week
**Output**: RAG with thematic navigation and entity definitions

**Steps**:
1. Investigate Subject section (curator annotations)
2. Investigate Glossary section (encyclopedia entries)
3. Implement concept-to-work mappings from Subject
4. Implement entity extraction from Glossary
5. Enhance query expansion with thematic relationships

**Success Metric**: "Best works on political economy" uses Subject metadata to rank

### Phase 3: Historical RAG (Add History Section - CONDITIONAL)

**Content**: +46GB labor periodicals
**Timeline**: +2-3 weeks
**Output**: Historical document RAG with temporal queries

**Prerequisites**:
- User decision: Include periodicals? (pending)
- OCR quality assessment (from 02-history-section-spec.md)
- Separate processing pipeline for journalism

**Steps**:
1. PDF OCR extraction pipeline
2. Article boundary detection
3. Temporal metadata extraction
4. Separate vector collection for periodicals (different query patterns)

**Success Metric**: "Labor movement in 1925" returns Daily Worker articles

### Phase 4: Multilingual RAG (Add Language Sections - FUTURE)

**Content**: +28GB translations
**Timeline**: +4-6 weeks
**Output**: Multilingual RAG with cross-lingual queries

**Prerequisites**:
- Investigation of language sections (05-language-sections-spec.md)
- Parallel text alignment
- Translation quality assessment

**Steps**:
1. Identify parallel texts (same work, multiple languages)
2. Implement language detection
3. Build multilingual embeddings
4. Cross-lingual query support

**Success Metric**: Query in English, retrieve results in Spanish/French/Russian

---

## Key Takeaways

1. **Archive section is the core** (4.5GB, well-structured, ready for RAG)
2. **History section dominates by size** (43GB, 93% of English content) but is OCR-intensive journalism
3. **Subject and Glossary add value beyond size** (curator annotations, entity definitions)
4. **Language sections are substantial** (28GB) but out of scope for English V1
5. **Total processable English content** is ~60GB, not 200GB (duplicates, non-text)

**Recommended Strategy**: **Start with Archive (4.5GB theory), expand to Subject+Glossary (5.2GB total), evaluate History periodicals (43GB) based on use case.**

---

## Next Steps

1. **User scope decision**: Periodicals in or out? (History section, 43GB)
2. **Complete remaining investigations**: Subject, Glossary, History specs
3. **Create unified metadata schema**: Cross-section schema document
4. **Begin Archive processing**: Implement pipeline from 01-archive-section-analysis.md
5. **Build proof-of-concept RAG**: Archive section only, validate approach

---

**Document Status**: Complete overview based on comprehensive investigation
**Last Updated**: 2025-11-08
**See Also**:
- `00-investigation-methodology-spec.md` - How investigations are conducted
- `01-archive-section-analysis.md` - Complete Archive section analysis
- `README.md` - Investigation roadmap and status tracking
