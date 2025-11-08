# Corpus Analysis Documentation

**Purpose**: Systematic investigation of the Marxists Internet Archive (121GB) to inform RAG architecture design.

**Status**: Phase 1 complete (Archive section), Phase 2 in progress
**Last Updated**: 2025-11-08

---

## Quick Start

### For AI Agents

1. **New to corpus analysis?** Read `00-investigation-methodology-spec.md` first
2. **Need corpus overview?** Read `00-corpus-overview.md`
3. **Investigating a section?** Follow the methodology spec template
4. **Implementing RAG?** Start with `01-archive-section-analysis.md`

### For Humans

**TL;DR**: The Marxists Internet Archive is 121GB containing 96,637 HTML files and 21,141 PDFs. The English theoretical content (Archive section, 4.5GB) is well-documented and ready for RAG implementation. The historical periodicals (History section, 43GB) require OCR and a scope decision.

**Recommended Reading Order**:
1. `00-corpus-overview.md` - Big picture
2. `01-archive-section-analysis.md` - Detailed example (Archive section)
3. `00-investigation-methodology-spec.md` - How we do investigations

---

## Table of Contents

- [Document Index](#document-index)
- [Investigation Status](#investigation-status)
- [Corpus Summary](#corpus-summary)
- [Section Specifications](#section-specifications)
- [Planned Documents](#planned-documents)
- [How to Contribute](#how-to-contribute)

---

## Document Index

### Meta-Level Documentation

| Document | Purpose | Status | Tokens |
|----------|---------|--------|--------|
| **README.md** | This file - roadmap and index | ✅ Current | ~2,000 |
| **00-investigation-methodology-spec.md** | Reproducible investigation framework | ✅ Complete | ~12,000 |
| **00-corpus-overview.md** | Complete corpus statistics and architecture | ✅ Complete | ~7,000 |

### Section-Specific Analyses

| Document | Section | Size | Status | Priority |
|----------|---------|------|--------|----------|
| **01-archive-section-analysis.md** | Archive (by author) | 4.5GB | ✅ Complete | HIGH |
| **02-history-section-spec.md** | History (periodicals) | 46GB | 📋 Planned | HIGH |
| **03-subject-section-spec.md** | Subject (themes) | 9.1GB | 📋 Planned | HIGH |
| **04-glossary-section-spec.md** | Glossary (encyclopedia) | 62MB | 📋 Planned | MEDIUM |
| **05-language-sections-spec.md** | Languages (multilingual) | 28GB | 📋 Future | LOW |

### Cross-Section Documentation

| Document | Purpose | Status | Priority |
|----------|---------|--------|----------|
| **06-metadata-unified-schema.md** | Unified metadata schema | 📋 Planned | HIGH |
| **07-processing-pipeline-spec.md** | HTML/PDF processing pipeline | 📋 Planned | HIGH |
| **08-chunking-strategies.md** | Chunking recommendations by content type | 📋 Planned | MEDIUM |
| **09-knowledge-graph-spec.md** | Graph relationships and linking | 📋 Planned | MEDIUM |

---

## Investigation Status

### Phase 1: Archive Section ✅ COMPLETE

**Objective**: Understand theoretical works structure (Archive section)
**Status**: ✅ Complete
**Output**: `01-archive-section-analysis.md`

**Key Findings**:
- 4.5GB, 411 authors, 28,962 HTML files, 6,637 PDFs
- 5-layer metadata schema (path, meta tags, breadcrumb, semantic, content)
- Hierarchical structure: work → part → chapter → section → paragraph
- Paragraph-level anchors enable precise citation
- Chunking recommendation: Paragraph-level with hierarchical context
- Ready for RAG implementation

**Deliverables**:
- ✅ Complete structural analysis
- ✅ Metadata extraction schema
- ✅ HTML pattern documentation
- ✅ Chunking strategy
- ✅ Sample file analysis

### Phase 2: Comprehensive Overview ✅ COMPLETE

**Objective**: Map entire corpus structure
**Status**: ✅ Complete
**Output**: `00-corpus-overview.md`, `00-investigation-methodology-spec.md`

**Key Findings**:
- 121GB total, but ~60GB processable English content
- History section (46GB) dominated by labor periodicals
- Subject section (9.1GB) includes 8.5GB Peking Review
- Language sections (28GB) out of scope for English RAG V1
- Three content types: theory (Archive), journalism (History), reference (Subject/Glossary)

**Deliverables**:
- ✅ Complete corpus statistics
- ✅ Section-by-section breakdown
- ✅ Priority matrix for investigations
- ✅ Scope decision recommendations
- ✅ Investigation methodology specification

### Phase 3: Remaining Sections 📋 IN PROGRESS

**Objective**: Complete investigations of Subject, History, Glossary sections
**Status**: 📋 Planned
**Timeline**: 2-3 weeks

**Planned Investigations**:
1. **02-history-section-spec.md** (Priority: HIGH)
   - Focus: PDF OCR quality, article extraction, temporal metadata
   - Size: 46GB (43GB periodicals + 4GB culture)
   - Estimated effort: 20,000-30,000 tokens

2. **03-subject-section-spec.md** (Priority: HIGH)
   - Focus: Curator annotations, concept mappings, Peking Review overlap
   - Size: 9.1GB (8.5GB Peking Review + 600MB other)
   - Estimated effort: 15,000-25,000 tokens

3. **04-glossary-section-spec.md** (Priority: MEDIUM)
   - Focus: Entry types, knowledge graph, cross-references
   - Size: 62MB
   - Estimated effort: 5,000-10,000 tokens

**Blockers**:
- Pending user decision: Include History periodicals (43GB) in RAG?
- Pending user decision: Include Peking Review (8.5GB) in RAG?

### Phase 4: Integration Specifications 📋 PLANNED

**Objective**: Cross-section integration and implementation specs
**Status**: 📋 Planned
**Timeline**: 1-2 weeks after Phase 3

**Planned Documents**:
1. **06-metadata-unified-schema.md**
   - Unified schema combining Archive, Subject, History, Glossary
   - Python dataclass definitions
   - Extraction pipeline specification

2. **07-processing-pipeline-spec.md**
   - HTML-to-markdown conversion
   - PDF OCR pipeline
   - Metadata extraction implementation
   - Error handling and validation

3. **08-chunking-strategies.md**
   - Content-type-specific chunking (theory vs journalism vs reference)
   - Hierarchical context preservation
   - Token budget optimization

4. **09-knowledge-graph-spec.md**
   - Entity relationships (author-work, work-concept, concept-concept)
   - Cross-reference graph structure
   - Citation network analysis

### Phase 5: Multilingual Expansion 📋 FUTURE

**Objective**: Investigate non-English content for future expansion
**Status**: 📋 Future work
**Timeline**: TBD (dependent on V1 RAG success)

**Planned Investigation**:
1. **05-language-sections-spec.md**
   - Parallel text detection (same work, multiple languages)
   - Translation quality assessment
   - Cross-lingual linking opportunities
   - Priority languages: Spanish (4.2GB), French (1.1GB), Russian (1.2GB)

---

## Corpus Summary

### Size and Composition

| Section | Size | % Total | HTML | PDF | Status |
|---------|------|---------|------|-----|--------|
| **Total Corpus** | 121GB | 100% | 96,637 | 21,141 | - |
| **English Content** | ~60GB | ~50% | ~50,000 | ~13,000 | - |
| History | 46GB | 38% | ~15,000 | 5,043 | 📋 Planned |
| Languages | 28GB | 23% | ~30,000 | ~8,000 | 📋 Future |
| Supporting | 33GB | 27% | N/A | N/A | Skip |
| Subject | 9.1GB | 8% | 2,259 | 1,412 | 📋 Planned |
| Archive | 4.5GB | 4% | 28,962 | 6,637 | ✅ Complete |
| Glossary | 62MB | <1% | 685 | 0 | 📋 Planned |

### Content Types

**1. Theoretical Works** (Archive section, 4.5GB)
- Long-form theory (10,000+ words typical)
- 411 authors (Marx, Lenin, Trotsky, Luxemburg, etc.)
- Hierarchical structure (work → chapter → section)
- Dense prose, extensive footnotes
- **Status**: ✅ Ready for RAG implementation

**2. Historical Periodicals** (History section, 46GB)
- Labor newspapers and magazines (1900-1980s)
- Short articles (200-1000 words)
- PDFs with variable OCR quality
- Precise temporal metadata
- **Status**: 📋 Needs scope decision

**3. Thematic Collections** (Subject section, 9.1GB)
- Curated reading lists with expert annotations
- Multi-author compilations
- Peking Review (8.5GB of section)
- Cross-references to Archive
- **Status**: 📋 Needs investigation

**4. Reference Materials** (Glossary, 62MB)
- Encyclopedia-style entries
- Biographical sketches, term definitions
- Knowledge graph backbone
- **Status**: 📋 Needs lightweight investigation

---

## Section Specifications

### 01-archive-section-analysis.md ✅

**Section**: Archive (by author)
**Size**: 4.5GB (411 authors)
**Investigation Date**: 2025-11-08
**Status**: ✅ Complete

**Key Findings**:

**Directory Structure**:
```
/archive/{author}/
  ├── works/{year}/{work}/ch##.htm
  ├── letters/
  ├── bio/
  └── index.htm
```

**Metadata Schema** (5 layers):
1. File path: author, year, work, chapter
2. Meta tags: author, title, classification
3. Breadcrumb: categorical navigation
4. Semantic CSS: curator context, provenance
5. Content-derived: word count, footnotes, reading time

**HTML Patterns**:
- DOCTYPE: HTML 4.0 Transitional
- Charset: ISO-8859-1
- Semantic classes: `title`, `fst`, `quoteb`, `context`, `information`
- Paragraph anchors: `<a name="s1p05">` (section 1, paragraph 5)

**Chunking Strategy**: Paragraph-level with hierarchical context preservation

**RAG Priority**: **HIGH** - Core theoretical content, ready for implementation

**Sample Metadata**:
```json
{
  "section": "archive",
  "author": "Karl Marx",
  "work_title": "Capital Volume I",
  "work_year": 1867,
  "chapter": "Chapter 1",
  "chapter_number": 1,
  "section": "Section 1",
  "paragraph_anchor": "015",
  "classification": "Economics",
  "breadcrumb": ["MIA", "Archive", "Marx", "Capital I", "Chapter 1"],
  "curator_context": "...",
  "provenance": "Translated by Samuel Moore...",
  "word_count": 850,
  "has_footnotes": true,
  "reading_time_minutes": 3
}
```

**Next Steps**: Implement processing pipeline, ingest to vector DB

---

### 02-history-section-spec.md 📋 PLANNED

**Section**: History (labor periodicals)
**Size**: 46GB (43GB periodicals + 4GB culture)
**Investigation Priority**: **HIGH**
**RAG Priority**: **MEDIUM** (pending scope decision)

**Planned Investigation Focus**:
1. PDF OCR quality assessment (sample 10-15 PDFs across decades)
2. Article boundary detection in periodicals
3. Temporal metadata extraction (volume, issue, date)
4. Comparison: Journalism style vs theoretical prose
5. Scope recommendation: Include or exclude from RAG?

**Key Questions**:
- Is OCR quality sufficient for reliable RAG?
- Can article boundaries be detected automatically?
- Does journalism content serve RAG use cases?
- Should periodicals be separate RAG collection?

**Timeline**: 2-3 weeks (pending user scope decision)

---

### 03-subject-section-spec.md 📋 PLANNED

**Section**: Subject (thematic collections)
**Size**: 9.1GB (8.5GB Peking Review + 600MB other)
**Investigation Priority**: **HIGH**
**RAG Priority**: **HIGH** (curator annotations valuable)

**Planned Investigation Focus**:
1. Curator annotation schema extraction (`class="context"`)
2. Concept-to-work mapping structure
3. Peking Review overlap analysis with Archive/Mao
4. Cross-reference patterns to Archive section
5. Reading list structure for query expansion

**Key Questions**:
- How much Peking Review content duplicates Archive section?
- Can curator annotations be used for query expansion?
- Should Subject section be metadata layer or separate collection?

**Timeline**: 1-2 weeks

---

### 04-glossary-section-spec.md 📋 PLANNED

**Section**: Glossary (encyclopedia)
**Size**: 62MB (685 HTML files)
**Investigation Priority**: **MEDIUM**
**RAG Priority**: **HIGH** (entity definitions)

**Planned Investigation Focus**:
1. Entry type taxonomy (people, terms, events, orgs, places)
2. Cross-reference graph structure
3. Entry length distribution (50-500 words typical)
4. Links to Archive works (knowledge graph edges)
5. Knowledge graph node specification

**Key Questions**:
- Can Glossary serve as entity disambiguation layer?
- Should entries be separate chunks or merged with Archive?
- How to use for query expansion?

**Timeline**: 1 week

---

### 05-language-sections-spec.md 📋 FUTURE

**Section**: Languages (40+ directories)
**Size**: ~28GB (Chinese 21GB, Spanish 4.2GB, Russian 1.2GB)
**Investigation Priority**: **LOW**
**RAG Priority**: **LOW** (English V1, multilingual V2)

**Planned Investigation Focus** (Future):
1. Parallel text detection (same work, multiple languages)
2. Translation quality assessment
3. Organizational structure comparison to English sections
4. Cross-lingual linking opportunities
5. Multilingual RAG expansion strategy

**Timeline**: TBD (after English RAG V1 success)

---

### 06-metadata-unified-schema.md 📋 PLANNED

**Purpose**: Cross-section metadata schema
**Priority**: **HIGH** (required for RAG implementation)
**Status**: 📋 Planned

**Planned Contents**:
1. Unified Python dataclass combining all sections
2. Section-specific fields (Archive, Subject, History, Glossary)
3. Common fields across all sections
4. Extraction pipeline specification
5. Validation rules and error handling

**Timeline**: 1 week (after remaining section investigations)

---

### 07-processing-pipeline-spec.md 📋 PLANNED

**Purpose**: HTML/PDF processing implementation
**Priority**: **HIGH**
**Status**: 📋 Planned

**Planned Contents**:
1. HTML-to-markdown conversion (preserving footnotes, anchors)
2. PDF OCR pipeline (quality thresholds)
3. Metadata extraction from all 5 layers
4. Error handling and validation
5. Batch processing strategy

**Timeline**: 1 week

---

### 08-chunking-strategies.md 📋 PLANNED

**Purpose**: Content-type-specific chunking
**Priority**: **MEDIUM**
**Status**: 📋 Planned

**Planned Contents**:
1. Theory chunking (paragraph-level, Archive section)
2. Journalism chunking (article-level, History section)
3. Reference chunking (entry-level, Glossary section)
4. Hierarchical context preservation
5. Token budget optimization

**Timeline**: 3-5 days

---

### 09-knowledge-graph-spec.md 📋 PLANNED

**Purpose**: Graph relationships and linking
**Priority**: **MEDIUM**
**Status**: 📋 Planned

**Planned Contents**:
1. Entity relationships (author-work, work-concept)
2. Cross-reference graph structure
3. Citation network analysis
4. Glossary as graph backbone
5. Graph database schema (Neo4j or similar)

**Timeline**: 1 week

---

## How to Contribute

### For AI Agents Conducting Investigations

1. **Read the methodology first**: `00-investigation-methodology-spec.md`
2. **Follow the template**: Use the Section Analysis Template (methodology spec, section 6)
3. **Sample strategically**: Don't read exhaustively, use stratified sampling
4. **Verify computationally**: Use grep/find to verify patterns across corpus
5. **Document confidence**: Specify % of files matching each pattern
6. **Include commands**: Document bash commands used for verification
7. **Be actionable**: Produce code-ready specifications, not vague recommendations

### Quality Checklist

Before marking investigation complete:
- [ ] Directory structure fully documented with sizes
- [ ] Meta tag schema extracted (all fields identified)
- [ ] CSS class inventory complete (semantic classes documented)
- [ ] Link patterns documented (hierarchical, cross-ref, citation)
- [ ] Chunking strategy defined with rationale
- [ ] Sample files listed (all files read during investigation)
- [ ] Verification commands included (grep/find commands)
- [ ] Confidence levels specified (% matching patterns)
- [ ] Open questions documented for user decision

### For Humans Reviewing Investigations

- Check that sampling strategy is justified
- Verify that bash commands are reproducible
- Confirm that specifications are actionable (not vague)
- Ensure metadata schemas are code-ready (can be implemented)
- Validate that chunking recommendations have clear rationale

---

## Investigation Methodology

All section investigations follow the framework defined in `00-investigation-methodology-spec.md`.

### Key Principles

1. **Stratified Sampling**: Sample across size, time, type, depth dimensions
2. **Computational Verification**: Use grep/find to verify patterns
3. **Token Efficiency**: Extract structure, not content
4. **Pattern Documentation**: Describe patterns, not individual files
5. **Confidence Levels**: Specify % of files matching each pattern
6. **Actionable Output**: Code-ready specifications

### Investigation Phases

1. **Reconnaissance** (10% tokens): Directory structure, file counts, size distribution
2. **Stratified Sampling** (40% tokens): Read representative files
3. **Pattern Verification** (30% tokens): grep/find commands to verify
4. **Edge Case Analysis** (10% tokens): Outliers and exceptions
5. **Synthesis** (10% tokens): Compile into specification document

### Token Efficiency Tactics

- Use `grep` instead of reading files to extract patterns (95% token reduction)
- Sample 3-15 files instead of reading all (95% token reduction)
- Extract structure only (headings, meta tags) not full content
- Aggregate statistics instead of individual file descriptions
- Reference examples instead of reproducing full HTML

**Average Investigation**: 15,000-25,000 tokens per section

---

## Recommended Reading Path

### Path 1: Quick Overview (Humans)

1. This README (you are here)
2. `00-corpus-overview.md` - Big picture (10 minutes)
3. `01-archive-section-analysis.md` - Detailed example (20 minutes)

**Total time**: ~30 minutes
**Output**: Understand corpus scope, architecture, and what's ready for RAG

### Path 2: Implementation (AI Agents)

1. `00-investigation-methodology-spec.md` - How to investigate (15 minutes)
2. `01-archive-section-analysis.md` - Example investigation (20 minutes)
3. `00-corpus-overview.md` - Corpus architecture (10 minutes)
4. Begin investigating assigned section using methodology

**Total time**: ~45 minutes
**Output**: Ready to conduct section investigation

### Path 3: RAG Implementation (Developers)

1. `01-archive-section-analysis.md` - Archive section (ready to implement)
2. `06-metadata-unified-schema.md` - Metadata schema (planned)
3. `07-processing-pipeline-spec.md` - Processing pipeline (planned)
4. `08-chunking-strategies.md` - Chunking (planned)

**Total time**: TBD (pending completion of planned docs)
**Output**: Ready to build RAG processing pipeline

---

## Open Questions

### Scope Decisions (User Input Required)

1. **History Periodicals** (43GB): Include in RAG or exclude?
   - See `00-corpus-overview.md` section "Scope Decisions" for analysis

2. **Peking Review** (8.5GB): Include or skip if duplicates Archive?
   - Pending investigation: `03-subject-section-spec.md`

3. **PDF Quality Threshold**: Accept all PDFs or HTML-first strategy?
   - Recommendation: HTML-first (see overview doc)

4. **Multilingual Expansion**: English-only V1, or include languages now?
   - Recommendation: English V1, multilingual V2

### Technical Decisions

1. **Vector Database**: Qdrant vs ChromaDB for 60GB+ corpus?
2. **Chunking Library**: LangChain vs custom implementation?
3. **Metadata Storage**: Vector DB metadata fields vs separate graph DB?
4. **Embedding Model**: Which model for theoretical prose?

---

## Contact and Updates

**Last Updated**: 2025-11-08
**Maintained By**: AI agents following investigation methodology
**Version**: 1.0 (Phase 1 complete, Phase 2 in progress)

**Change Log**:
- 2025-11-08: Initial creation with Archive section complete
- 2025-11-08: Added methodology spec and corpus overview
- Future: Will update as remaining sections investigated

---

## Quick Reference: Document Status

| Document | Status | Tokens | Last Updated |
|----------|--------|--------|--------------|
| README.md | ✅ Current | ~2,000 | 2025-11-08 |
| 00-investigation-methodology-spec.md | ✅ Complete | ~12,000 | 2025-11-08 |
| 00-corpus-overview.md | ✅ Complete | ~7,000 | 2025-11-08 |
| 01-archive-section-analysis.md | ✅ Complete | ~8,000 | 2025-11-08 |
| 02-history-section-spec.md | 📋 Planned | N/A | Pending |
| 03-subject-section-spec.md | 📋 Planned | N/A | Pending |
| 04-glossary-section-spec.md | 📋 Planned | N/A | Pending |
| 05-language-sections-spec.md | 📋 Future | N/A | Future |
| 06-metadata-unified-schema.md | 📋 Planned | N/A | Pending |
| 07-processing-pipeline-spec.md | 📋 Planned | N/A | Pending |
| 08-chunking-strategies.md | 📋 Planned | N/A | Pending |
| 09-knowledge-graph-spec.md | 📋 Planned | N/A | Pending |

**Total Documentation Planned**: 12 documents
**Completed**: 4 (33%)
**In Progress**: 0
**Planned**: 5 (42%)
**Future**: 3 (25%)
