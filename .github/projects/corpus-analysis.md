# Corpus Analysis Project

**Status**: In Progress (Phase 2)
**Owner**: Shared across instances
**Priority**: HIGH
**Timeline**: 3-4 weeks

---

## Project Overview

Systematic investigation of the 121GB Marxists Internet Archive to understand structure, extract metadata schemas, and design optimal RAG architecture.

**Goal**: Complete section-specific analyses for all major corpus sections to inform processing pipeline design.

---

## Current Status

- ✅ **Phase 1 Complete**: Archive section (4.5GB) fully analyzed
- ✅ **Phase 2 Complete**: Methodology and overview documentation
- 🔄 **Phase 3 In Progress**: Remaining section investigations
- 📋 **Phase 4 Planned**: Integration specifications

---

## Work Streams

### Stream 1: Section Investigations ✅ 1/4 Complete

**Purpose**: Analyze each major corpus section

| Section | Size | Priority | Status | Owner | Issue |
|---------|------|----------|--------|-------|-------|
| Archive (theory) | 4.5GB | HIGH | ✅ Complete | - | - |
| History (periodicals) | 46GB | HIGH | 📋 Planned | TBD | #TBD |
| Subject (themes) | 9.1GB | HIGH | 📋 Planned | TBD | #TBD |
| Glossary (encyclopedia) | 62MB | MEDIUM | 📋 Planned | TBD | #TBD |
| Languages (multilingual) | 28GB | LOW | 📋 Future | - | - |

**Deliverables**:
- ✅ `01-archive-section-analysis.md` (Complete)
- 📋 `02-history-section-spec.md` (TODO - needs scope decision)
- 📋 `03-subject-section-spec.md` (TODO)
- 📋 `04-glossary-section-spec.md` (TODO)
- 📋 `05-language-sections-spec.md` (Future)

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

### Milestone 3: Remaining Section Analyses 📋 IN PLANNING
- **Target**: 2-3 weeks
- **Blockers**:
  - User decision needed: Include History periodicals (43GB)?
  - User decision needed: Include Peking Review (8.5GB)?
- **Deliverables**: Complete analyses for History, Subject, Glossary sections
- **Outcome**: Full corpus understanding across all sections

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
[BLOCKER: User Scope Decision]
  ├─ Include History periodicals? (43GB)
  └─ Include Peking Review? (8.5GB)
  ↓
Remaining Section Analyses (📋 Planned)
  ├─ History section
  ├─ Subject section
  └─ Glossary section
  ↓
Integration Specifications (📋 Planned)
  ├─ Unified metadata schema
  ├─ Processing pipeline
  ├─ Chunking strategies
  └─ Knowledge graph
  ↓
RAG Implementation (Ready to begin for Archive section)
```

---

## Blockers and Risks

### Critical Blockers

1. **Scope Decision: History Periodicals** (43GB)
   - **Question**: Include labor periodicals in RAG?
   - **Impact**: 93% of History section, OCR-intensive
   - **Options**: Include all, exclude all, or HTML-only
   - **Recommendation**: Start without, add later if needed
   - **Decision Needed By**: Before History section investigation

2. **Scope Decision: Peking Review** (8.5GB)
   - **Question**: Include Peking Review PDFs?
   - **Impact**: 93% of Subject section
   - **Dependency**: Check overlap with Archive/Mao content
   - **Recommendation**: Investigate overlap first
   - **Decision Needed By**: Before Subject section investigation

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

### AI Agent Time

- **Archive Analysis**: ~8 hours (✅ Complete)
- **Methodology Development**: ~4 hours (✅ Complete)
- **History Investigation**: ~6 hours (📋 Planned)
- **Subject Investigation**: ~4 hours (📋 Planned)
- **Glossary Investigation**: ~2 hours (📋 Planned)
- **Integration Specs**: ~6 hours (📋 Planned)

**Total Estimated**: ~30 hours (8 complete, 22 remaining)

### Token Budget

- **Archive Analysis**: ~8,000 tokens (✅ Used)
- **Methodology + Overview**: ~19,000 tokens (✅ Used)
- **History Investigation**: ~25,000 tokens (📋 Budgeted)
- **Subject Investigation**: ~20,000 tokens (📋 Budgeted)
- **Glossary Investigation**: ~10,000 tokens (📋 Budgeted)
- **Integration Specs**: ~40,000 tokens (📋 Budgeted)

**Total Estimated**: ~122,000 tokens (27k used, 95k remaining)

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
