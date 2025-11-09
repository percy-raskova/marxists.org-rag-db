# Corpus Analysis Project

**Status**: In Progress (Phase 3)
**Owner**: Shared across instances
**Priority**: HIGH
**Timeline**: 1-2 weeks

---

## Project Overview

Systematic investigation of the ~50GB Marxists Internet Archive (optimized from 200GB) to understand structure, extract metadata schemas, and design optimal RAG architecture.

**Goal**: Complete section-specific analyses for all major corpus sections to inform processing pipeline design.

---

## Current Status

- ✅ **Phase 1 Complete**: Archive section (4.3GB) fully analyzed with programmatic methodology
- ✅ **Phase 2 Complete**: Methodology and overview documentation
- ✅ **Corpus Optimized**: 200GB → 50GB (75% reduction)
- ✅ **Phase 3 Complete**: All section investigations complete (46GB documented)
- ✅ **Phase 4 Complete**: Integration specifications ready for implementation
- 🚀 **READY FOR RAG IMPLEMENTATION**: All corpus analysis and specifications complete!

---

## Work Streams

### Stream 1: Section Investigations ✅ 5/5 Complete

**Purpose**: Analyze each major corpus section

| Section | Size | Priority | Status | Owner | Issue |
|---------|------|----------|--------|-------|-------|
| Archive (theory) | 4.3GB | **HIGH** | ✅ Complete (re-investigated) | - | - |
| History (core texts + ETOL/EROL) | 33GB | **HIGH** | ✅ Complete (re-investigated) | - | - |
| - ETOL (Trotskyist encyclopedia) | 8.3GB | **MEDIUM-HIGH** | ✅ Complete | - | - |
| - EROL (Maoist encyclopedia) | 14GB | **MEDIUM-HIGH** | ✅ Complete | - | - |
| - Other History | 10.7GB | **HIGH** | ✅ Complete | - | - |
| Subject (themes) | 8.9GB | **HIGH** | ✅ Complete | - | - |
| Glossary (encyclopedia) | 62MB | **CRITICAL** | ✅ Complete | - | - |
| Reference | 460MB | MEDIUM | ✅ Complete | - | - |
| Ebooks | 57MB | LOW | 📋 Deferred | - | - |

**Deliverables**:
- ✅ `01-archive-section-analysis.md` (Complete - 4.3GB, 15,637 files)
  - **Re-investigated with programmatic parsing**: 40k tokens (50% reduction)
  - Statistical metadata analysis (n=100): 75% author tags, 62% ISO-8859-1 encoding
  - Document type distribution (n=200): 74% articles, 15% chapters, 5.5% letters
  - Temporal coverage: 1838-1990, peak 1900-1949 (50.9%)
  - RAG-ready with quantified chunking strategies
- ✅ `02-history-section-spec.md` (Complete - 33GB, 33,190 files)
  - **Re-investigated with programmatic parsing**: 70 HTML samples, 23,781 files quantified
  - Covers ETOL (8.3GB, 12,218 files), EROL (14GB, 8,184 files), Other History (10.7GB, 3,379 files)
  - Three distinct HTML architectures confirmed with metadata accuracy rates
  - ETOL: 30-70% author meta accuracy, 87% .fst CSS, 70% good heading hierarchies
  - EROL: 95% org attribution via title/keywords (5% from meta), 90% use h3 as title (not h1)
  - Other History: 40% have NO headings, requires paragraph-based chunking fallback
  - Multi-source author extraction strategy (85%+ target accuracy)
  - Adaptive chunking with 6 edge case patterns (index pages, multi-article, long paras)
- ✅ `03-subject-section-spec.md` (Complete - 8.9GB, 2,259 HTML files)
  - **Programmatic investigation**: 15 HTML samples, 46 subject categories mapped
  - Multi-dimensional taxonomy (8 categories): theoretical, economic, political, geographical, etc.
  - Document types: 55% navigation indexes (exclude), 18% periodicals, 15% essays
  - **China/Peking Review dominates**: 8.4GB of 8.9GB (94%, 1,400 issues 1958-2006)
  - Cross-reference hub: 64% link to /archive/, 19% to /reference/
  - Multi-author works: anthology structure with 80+ authors in some subjects
  - RAG strategy: thematic metadata enrichment + knowledge graph for cross-references
- ✅ `04-glossary-section-spec.md` (Complete - 62MB, ~2,500 entries)
  - **Programmatic investigation**: 6 representative pages, 50+ entries sampled
  - Six glossary types: people (800-1,200), terms (500-600), orgs (200-300), events, periodicals, places
  - Entry-based chunking: 2,200-2,900 chunks total
  - Cross-reference network: 5,000-10,000 edges across ~2,500 nodes
  - **CRITICAL for RAG**: entity extraction for metadata enrichment across entire corpus
  - Knowledge graph foundation: glossary → archive → subject links
  - Metadata completeness: 90% dates, 60% portraits, 80-95% cross-references
  - Optimized for "what is X?" definition queries with separate vector collection
- ✅ `05-reference-section-spec.md` (Complete - 460MB, 4,867 HTML files)
  - **Programmatic investigation**: Git-LFS metadata analysis, path-based taxonomy
  - **100% Git-LFS storage**: All files are LFS pointers (must run `git lfs pull` before processing)
  - Actual content size: 119.68 MB (not 460MB on disk)
  - 105 non-Marxist authors: anarchists, classical economists, German idealists, Western Marxists
  - **Key distinction**: Mao/Stalin/Hoxha in Reference (not core Archive per MIA doctrinal stance)
  - Subject organization: philosophy by country code (us/ge/fr/en), economics by author
  - Temporal coverage: 1600s-1990s (peak 1920s-1940s)
  - Processing priorities: High (Hegel 19.78 MB!, Smith, Ricardo), Medium (anarchists), Lower (Mao/Stalin)
  - RAG strategy: unified collection with metadata filtering, intellectual genealogy tracking

### Stream 2: Meta-Documentation ✅ Complete

**Purpose**: Create investigation framework and overview

| Document | Status | Purpose |
|----------|--------|---------|
| `00-investigation-methodology-spec.md` | ✅ Complete | Reproducible investigation framework |
| `00-corpus-overview.md` | ✅ Complete | Full corpus statistics and architecture |
| `README.md` | ✅ Complete | Roadmap and index |

### Stream 3: Integration Specs ✅ 4/4 Complete

**Purpose**: Cross-section specifications for implementation

| Document | Priority | Status | Dependencies | Location |
|----------|----------|--------|--------------|----------|
| `06-metadata-unified-schema.md` | HIGH | ✅ Complete | Section analyses 01-05 | `docs/corpus-analysis/` |
| `02-DOCUMENT-PROCESSING-SPEC.md` (v2.0) | HIGH | ✅ Complete (Updated) | Section analyses 01-05 | `specs/` |
| `07-chunking-strategies-spec.md` | MEDIUM | ✅ Complete | Section analyses | `specs/` |
| `08-knowledge-graph-spec.md` | MEDIUM | ✅ Complete | Section analyses + Glossary | `specs/` |

**Deliverables**:
- ✅ `docs/corpus-analysis/06-metadata-unified-schema.md` (Complete - 70KB, 1,087 lines)
  - **Unified schema**: 5-layer metadata model (core, authorship, temporal, technical, semantic)
  - **Multi-source extraction**: 85%+ author coverage via path + title + keywords strategies
  - **Section-aware rules**: Adaptive extraction for Archive, ETOL, EROL, Subject, Glossary, Reference
  - **Entity linking**: Glossary integration for canonical names
  - **Encoding normalization**: 60% ISO-8859-1 → UTF-8 conversion strategy
  - **Coverage targets documented**: Per-section author/date/keywords coverage metrics
- ✅ `specs/02-DOCUMENT-PROCESSING-SPEC.md` (Complete - Updated to v2.0)
  - **Enhanced metadata schema**: Integrated unified schema with 5 layers
  - **Multi-source author extraction**: Algorithms achieving 85%+ coverage target
  - **Encoding normalization**: ISO-8859-1 fallback sequence with chardet detection
  - **CSS class patterns**: Corpus-analyzed boilerplate removal (.fst, .footer, .linkback)
  - **Section-specific rules**: EROL h3-as-title handling, transcriber vs author distinction
  - **Updated acceptance criteria**: Section-level targets (Archive 100%, ETOL 85%, etc.)
- ✅ `specs/07-chunking-strategies-spec.md` (Complete - 68KB, 1,172 lines)
  - **Adaptive strategies**: Semantic breaks (70%), entry-based (Glossary), paragraph clusters (40% heading-less), token fallback
  - **Strategy selection algorithm**: Automatic strategy based on document_structure metrics
  - **Implementation details**: Complete Python pseudocode for all 4 strategies
  - **Edge case handling**: Index pages, multi-article files, long paragraphs (500-1000 words)
  - **Quality metrics**: Target avg 650-750 tokens/chunk, >70% with headings
  - **Testing framework**: Unit + integration tests with fixtures
- ✅ `specs/08-knowledge-graph-spec.md` (Complete - 58KB, 955 lines)
  - **Graph schema**: 10 node types, 14 edge types (authorship, structure, mentions, thematic)
  - **Entity foundation**: ~2,500 Glossary entities as canonical nodes
  - **Relationship extraction**: 5k-10k cross-references + 50k-100k entity mentions
  - **Hybrid retrieval**: Vector-first + graph-enhanced, graph-first + vector-filtered strategies
  - **Multi-hop queries**: Intellectual genealogy, citation chains, thematic exploration
  - **Storage options**: Neo4j (recommended), NetworkX (simpler), SQLite (hybrid)
  - **Implementation roadmap**: 8-week phased plan

---

## Milestones

### Milestone 1: Archive Section Analysis ✅ COMPLETE
- **Completed**: 2025-11-08
- **Deliverables**: Complete Archive section analysis, ready for RAG implementation
- **Outcome**: 4.5GB of theoretical works documented, 5-layer metadata schema defined

### Milestone 2: Investigation Framework ✅ COMPLETE
- **Completed**: 2025-11-08
- **Deliverables**: Methodology spec, corpus overview, roadmap
- **Outcome**: Reproducible framework for remaining investigations, token-efficient approach

### Milestone 3: All Section Analyses ✅ COMPLETE
- **Completed**: 2025-11-08
- **Progress**: 5 of 5 major sections complete (46GB documented)
  - Archive: 4.3GB, 15,637 files
  - History: 33GB, 33,190 files (ETOL + EROL + Other)
  - Subject: 8.9GB, 2,259 files
  - Glossary: 62MB, ~2,500 entries
  - Reference: 460MB, 4,867 files
- **Deliverables**: All section specifications complete with programmatic methodology
- **Outcome**: Full corpus understanding across entire 46GB English content

### Milestone 4: Integration Specifications ✅ COMPLETE
- **Completed**: 2025-11-08
- **Dependencies**: Milestone 3 complete ✅
- **Deliverables**: Unified schema, processing pipeline v2.0, chunking strategies, knowledge graph
- **Outcome**: Implementation-ready specifications for RAG build
  - 6-metadata-unified-schema.md (70KB, 5-layer metadata model)
  - 02-DOCUMENT-PROCESSING-SPEC.md v2.0 (enhanced with corpus findings)
  - 07-chunking-strategies-spec.md (68KB, 4 adaptive strategies)
  - 08-knowledge-graph-spec.md (58KB, hybrid retrieval architecture)

---

## Critical Path

```
Archive Analysis (✅ Complete)
  ↓
Investigation Methodology (✅ Complete)
  ↓
Corpus Optimization (✅ Complete: 200GB → 50GB)
  ↓
Remaining Section Analyses (🔄 In Progress)
  ├─ History section (~35GB)
  ├─ Subject section (9.1GB)
  ├─ Glossary section (62MB - CRITICAL)
  └─ Reference section (582MB)
  ↓
Integration Specifications (📋 Planned)
  ├─ Unified metadata schema
  ├─ Processing pipeline
  ├─ Chunking strategies
  └─ Knowledge graph
  ↓
RAG Implementation (Ready to begin)
```

---

## Blockers and Risks

### ✅ No Critical Blockers

**Scope Resolved**: Through strategic content filtering, we've reduced the corpus by 75%:
- Removed all audio/video/images
- Removed duplicate PDFs with HTML equivalents
- Deferred ETOL/EROL encyclopedias (75GB) for future enhancement
- Deferred periodicals archives (56GB) for future enhancement
- Result: ~50GB manageable corpus ready for investigation

### Medium Risks

1. **PDF OCR Quality** (variable, pre-1950s poor)
   - **Mitigation**: HTML-first strategy, quality thresholds
   - **Impact**: May lose some historical documents

2. **Token Budget for Investigations** (15k-25k per section)
   - **Mitigation**: Follow methodology's token-efficient tactics
   - **Impact**: Each investigation costs ~20k tokens average

3. **Pattern Consistency Across Sections** (may vary)
   - **Mitigation**: Stratified sampling verifies patterns
   - **Impact**: May need section-specific handling

---

## Success Metrics

### Phase Completion Metrics

- ✅ **Phase 1**: Archive section analysis complete (4.3GB documented)
- ✅ **Phase 2**: Methodology framework complete (reproducible approach)
- ✅ **Phase 3**: All section analyses complete (46GB English content documented)
- ✅ **Phase 4**: Integration specs complete (implementation-ready)

### Quality Metrics

- **Pattern Verification**: All claimed patterns verified with grep/find commands
- **Confidence Levels**: All patterns documented with % occurrence
- **Token Efficiency**: <30k tokens per section investigation
- **Actionability**: All specifications are code-ready (not vague)
- **Reproducibility**: Any AI agent can follow methodology and reproduce results

### Implementation Readiness

- ✅ Archive section: Ready for RAG implementation
- ✅ All sections: Specifications complete (Archive, ETOL, EROL, Subject, Glossary, Reference)
- ✅ Unified schema: Complete (5-layer metadata model with 85%+ author coverage targets)
- ✅ Processing pipeline: Spec updated to v2.0 with corpus-informed algorithms
- ✅ Chunking strategies: 4 adaptive strategies specified with quality metrics
- ✅ Knowledge graph: Complete architecture (10 node types, 14 edge types, hybrid retrieval)

---

## Resource Allocation

### AI Agent Time (Reduced by 50%)

- **Archive Analysis**: ~8 hours (✅ Complete)
- **Methodology Development**: ~4 hours (✅ Complete)
- **History Investigation**: ~3 hours (📋 Planned - reduced from 6)
- **Subject Investigation**: ~2 hours (📋 Planned - reduced from 4)
- **Glossary Investigation**: ~1 hour (📋 Planned - reduced from 2)
- **Reference Investigation**: ~1 hour (📋 Planned)
- **Integration Specs**: ~4 hours (📋 Planned - reduced from 6)

**Total Estimated**: ~23 hours (12 complete, 11 remaining)

### Token Usage Tracking (For Reference Only)

- **Archive Analysis (initial)**: ~8,000 tokens (✅ manual approach)
- **Archive Re-investigation**: ~40,000 tokens (✅ programmatic approach)
- **Methodology + Overview**: ~19,000 tokens (✅)
- **History Investigation (initial)**: ~15,000 tokens (✅ manual approach)
- **History Re-investigation**: ~55,000 tokens (✅ programmatic approach, 70 samples)
- **Subject Investigation**: TBD (in progress)
- **Glossary Investigation**: TBD (pending)
- **Reference Investigation**: TBD (pending)
- **Integration Specs**: TBD (pending)

**Total Used**: ~137,000 tokens

---

## Dependencies

### External Dependencies

- **User Decisions**: Scope decisions for History and Subject sections
- **Archive Extraction**: Full archive extracted to `/media/user/marxists.org/` (in progress)

### Internal Dependencies

- Integration specs depend on section analyses completion
- Processing pipeline depends on unified metadata schema
- RAG implementation depends on all specifications complete

### Cross-Project Dependencies

- **Refactoring Project**: Code complexity reduction enables maintainable pipeline
- **Documentation Project**: Clean docs enable parallel instance work
- **Infrastructure**: Cloud architecture for 200GB processing

---

## Communication

### Status Updates

- **Weekly**: Update milestone progress in this document
- **Blockers**: Immediately flag scope decisions needed
- **Completion**: Mark phases complete with outcomes documented

### Stakeholder Decisions Needed

1. **History Periodicals Inclusion** (43GB labor newspapers)
   - Pros: Primary sources, historical context, working-class perspective
   - Cons: OCR quality, different use case, massive size
   - Recommendation: Start without, add later as separate RAG

2. **Peking Review Inclusion** (8.5GB Chinese Revolution periodical)
   - Pros: Important historical documents, Maoist theory
   - Cons: Mostly PDFs, may duplicate Archive/Mao content
   - Recommendation: Investigate overlap first, then decide

3. **Multilingual Expansion Timing** (28GB non-English)
   - Options: Include now vs. defer to V2
   - Recommendation: English V1, multilingual V2

---

## Related Projects

- **Refactoring Project** (`refactoring-code-complexity.md`) - Clean codebase for pipeline
- **Documentation Project** (`documentation-reorganization.md`) - Instance coordination
- **RAG Implementation** (not yet created) - Will use these specifications

---

## Notes

- All investigations follow `00-investigation-methodology-spec.md` framework
- Token efficiency tactics achieve 95% reduction vs exhaustive reading
- Archive section (4.5GB) ready for immediate RAG implementation
- Full 60GB English content requires remaining section investigations
- Estimated 3-4 weeks to complete all section analyses
