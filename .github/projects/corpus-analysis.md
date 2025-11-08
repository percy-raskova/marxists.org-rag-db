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

- ✅ **Phase 1 Complete**: Archive section (4.5GB) fully analyzed
- ✅ **Phase 2 Complete**: Methodology and overview documentation
- ✅ **Corpus Optimized**: 200GB → 50GB (75% reduction)
- 🔄 **Phase 3 In Progress**: Remaining section investigations
- 📋 **Phase 4 Planned**: Integration specifications

---

## Work Streams

### Stream 1: Section Investigations ✅ 1/4 Complete

**Purpose**: Analyze each major corpus section

| Section | Size | Priority | Status | Owner | Issue |
|---------|------|----------|--------|-------|-------|
| Archive (theory) | 4.5GB | HIGH | ✅ Complete | - | - |
| History (core texts) | ~35GB | HIGH | 📋 Planned | TBD | #TBD |
| Subject (themes) | 9.1GB | HIGH | 📋 Planned | TBD | #TBD |
| Glossary (encyclopedia) | 62MB | **CRITICAL** | 📋 Planned | TBD | #TBD |
| Reference | 582MB | MEDIUM | 📋 Planned | TBD | #TBD |

**Deliverables**:
- ✅ `01-archive-section-analysis.md` (Complete)
- 📋 `02-history-section-spec.md` (TODO - ready to start)
- 📋 `03-subject-section-spec.md` (TODO)
- 📋 `04-glossary-section-spec.md` (TODO - critical priority)
- 📋 `05-reference-section-spec.md` (TODO)

### Stream 2: Meta-Documentation ✅ Complete

**Purpose**: Create investigation framework and overview

| Document | Status | Purpose |
|----------|--------|---------|
| `00-investigation-methodology-spec.md` | ✅ Complete | Reproducible investigation framework |
| `00-corpus-overview.md` | ✅ Complete | Full corpus statistics and architecture |
| `README.md` | ✅ Complete | Roadmap and index |

### Stream 3: Integration Specs 📋 Planned

**Purpose**: Cross-section specifications for implementation

| Document | Priority | Status | Dependencies |
|----------|----------|--------|--------------|
| `06-metadata-unified-schema.md` | HIGH | 📋 Planned | Section analyses 02-04 |
| `07-processing-pipeline-spec.md` | HIGH | 📋 Planned | Section analyses 02-04 |
| `08-chunking-strategies.md` | MEDIUM | 📋 Planned | Section analyses |
| `09-knowledge-graph-spec.md` | MEDIUM | 📋 Planned | Section analyses |

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

### Milestone 3: Remaining Section Analyses 🔄 IN PROGRESS
- **Target**: 1-2 weeks
- **No Blockers**: Scope resolved through 75% size reduction
- **Deliverables**: Complete analyses for History, Subject, Glossary, Reference sections
- **Outcome**: Full corpus understanding across all 50GB sections

### Milestone 4: Integration Specifications 📋 PLANNED
- **Target**: +1 week after Milestone 3
- **Dependencies**: Milestone 3 complete
- **Deliverables**: Unified schema, processing pipeline, chunking strategies, knowledge graph
- **Outcome**: Implementation-ready specifications for RAG build

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

- ✅ **Phase 1**: Archive section analysis complete (4.5GB documented)
- ✅ **Phase 2**: Methodology framework complete (reproducible approach)
- 📋 **Phase 3**: All section analyses complete (60GB English content documented)
- 📋 **Phase 4**: Integration specs complete (implementation-ready)

### Quality Metrics

- **Pattern Verification**: All claimed patterns verified with grep/find commands
- **Confidence Levels**: All patterns documented with % occurrence
- **Token Efficiency**: <30k tokens per section investigation
- **Actionability**: All specifications are code-ready (not vague)
- **Reproducibility**: Any AI agent can follow methodology and reproduce results

### Implementation Readiness

- ✅ Archive section: Ready for RAG implementation
- 📋 Other sections: Pending investigations
- 📋 Unified schema: Pending integration work
- 📋 Processing pipeline: Pending integration work

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

### Token Budget (Reduced by 40%)

- **Archive Analysis**: ~8,000 tokens (✅ Used)
- **Methodology + Overview**: ~19,000 tokens (✅ Used)
- **History Investigation**: ~15,000 tokens (📋 Budgeted - reduced from 25k)
- **Subject Investigation**: ~12,000 tokens (📋 Budgeted - reduced from 20k)
- **Glossary Investigation**: ~5,000 tokens (📋 Budgeted - reduced from 10k)
- **Reference Investigation**: ~5,000 tokens (📋 Budgeted)
- **Integration Specs**: ~25,000 tokens (📋 Budgeted - reduced from 40k)

**Total Estimated**: ~89,000 tokens (27k used, 62k remaining)

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
