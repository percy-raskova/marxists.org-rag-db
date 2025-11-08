# Corpus Optimization Impact Analysis

**Created**: 2025-11-08
**Optimization**: 200GB → 50GB (75% reduction)

---

## Executive Summary

By strategically removing non-essential content types, we've transformed the Marxist RAG project from an enterprise-scale challenge to a manageable implementation that can be completed with reasonable resources.

## Resource Impact Comparison

### Computational Requirements

| Metric | Original (200GB) | Optimized (50GB) | Reduction |
|--------|-----------------|------------------|-----------|
| **Embedding Time** | 200-250 hours | 25-30 hours | 88% |
| **GPU Rental Cost** | $400-600 | $100-120 | 75-80% |
| **Processing Cores** | 32-64 recommended | 8-16 sufficient | 75% |
| **RAM Required** | 128GB+ | 32-64GB | 75% |
| **Storage (with vectors)** | ~400GB | ~100GB | 75% |

### Development Timeline

| Phase | Original | Optimized | Time Saved |
|-------|----------|-----------|------------|
| **Corpus Investigation** | 4-6 weeks | 1-2 weeks | 3-4 weeks |
| **Processing Pipeline** | 3-4 weeks | 1-2 weeks | 2 weeks |
| **Embedding Generation** | 2 weeks (waiting) | 3-4 days | 10 days |
| **Testing & Validation** | 2-3 weeks | 1 week | 1-2 weeks |
| **Total Project** | 3-4 months | 3-4 weeks | 2-3 months |

### Infrastructure Costs

| Component | Original (Monthly) | Optimized (Monthly) | Savings |
|-----------|-------------------|---------------------|---------|
| **Vector DB Hosting** | $100-150 | $20-30 | $80-120 |
| **Storage** | $40-50 | $10-15 | $30-35 |
| **API Compute** | $50-75 | $10-20 | $40-55 |
| **Monitoring** | $20-30 | $5-10 | $15-20 |
| **Total Monthly** | $210-305 | $45-75 | $165-230 |

## Architecture Simplification

### Before (200GB)
- 6 parallel instances required
- Complex coordination matrix
- Enterprise Weaviate cluster
- Distributed processing with Ray/Dask
- Multi-node GKE deployment
- Dedicated monitoring stack

### After (50GB)
- 3-4 sequential phases
- Simple linear pipeline
- Single-node vector DB possible
- Local processing viable
- Optional cloud deployment
- Basic monitoring sufficient

## Quality and Coverage Trade-offs

### What We Keep (High Value)
| Content Type | Coverage | Quality | Use Case |
|--------------|----------|---------|----------|
| Theoretical Works | 100% | Excellent | Core RAG queries |
| HTML Documents | 100% | Excellent | Best text extraction |
| Curator Annotations | 100% | Excellent | Context and guidance |
| Essential PDFs | ~30% | Good | Unique content only |
| Glossary/Reference | 100% | Excellent | Entity disambiguation |

### What We Defer (Future Enhancement)
| Content Type | Size | Rationale | Future Phase |
|--------------|------|-----------|--------------|
| ETOL Encyclopedia | 61GB | Specialized Trotskyist content | Phase 2 |
| EROL Encyclopedia | 14GB | Specialized Maoist content | Phase 2 |
| Labor Periodicals | 56GB | Different use case (journalism) | Phase 3 |
| Audio/Video | 7GB | Requires transcription pipeline | Phase 4 |
| Non-English | 28GB | Requires multilingual models | Phase 5 |

## Development Velocity Impact

### Immediate Benefits
1. **Faster Iteration**: Can process entire corpus in days, not weeks
2. **Local Development**: Possible to work with full dataset locally
3. **Cheaper Experimentation**: Can afford multiple embedding runs
4. **Simpler Testing**: Manageable test datasets
5. **Quick Validation**: Results in hours, not days

### Long-term Benefits
1. **Lower Maintenance**: Simpler system = fewer failure points
2. **Easier Scaling**: Can add content incrementally
3. **Cost-Effective**: Sustainable for individual/small team
4. **Clear Roadmap**: Natural progression for enhancements
5. **Proven Foundation**: V1 success enables V2 funding/support

## Risk Mitigation

### Risks Eliminated
- ❌ Budget overrun from GPU costs
- ❌ Complexity paralysis from 6-instance coordination
- ❌ Infrastructure costs exceeding budget
- ❌ Multi-modal pipeline complexity
- ❌ Cross-language synchronization issues

### Risks Reduced
- ⬇️ Processing failures (shorter runs = less failure exposure)
- ⬇️ Coordination overhead (fewer moving parts)
- ⬇️ Testing complexity (manageable dataset size)
- ⬇️ Deployment challenges (simpler architecture)

### New Risks Introduced
- ⬆️ Coverage gaps (75% content deferred)
- ⬆️ Language bias (English-only)
- ⬆️ Missing multimedia insights

## Success Metrics

### Original Targets (200GB)
- Embedding generation: <$600 ❓
- Monthly operations: <$300 ❓
- Processing time: <2 weeks ❓
- Query latency: <500ms ❓
- Development time: <3 months ❓

### Revised Targets (50GB)
- Embedding generation: <$150 ✅
- Monthly operations: <$75 ✅
- Processing time: <4 days ✅
- Query latency: <200ms ✅
- Development time: <1 month ✅

## Recommendations

### Immediate Actions
1. ✅ Document decision in ADR-001
2. ✅ Update all project documentation
3. ⏳ Begin processing HTML content first
4. ⏳ Investigate Glossary for metadata structure
5. ⏳ Design simple linear pipeline

### Next Phases
1. Complete corpus investigation (1-2 weeks)
2. Build processing pipeline (1 week)
3. Generate embeddings (3-4 days)
4. Deploy vector database (2-3 days)
5. Implement query interface (1 week)

### Future Enhancements (Post-V1)
1. **Phase 2**: Add ETOL/EROL encyclopedias (+75GB)
2. **Phase 3**: Add periodicals/journalism (+56GB)
3. **Phase 4**: Add multilingual content (+28GB)
4. **Phase 5**: Add audio transcription (+5GB)

## Conclusion

The 75% corpus reduction transforms this project from a high-risk enterprise endeavor to a achievable proof-of-concept that can demonstrate value quickly and cheaply. This positions us for success in securing resources for future phases while delivering immediate value with core theoretical texts.

### Key Success Factors
- **Focus**: Core theoretical texts are highest value
- **Feasibility**: Manageable with available resources
- **Flexibility**: Can enhance incrementally
- **Proof of Concept**: Demonstrates viability for funding
- **Sustainability**: Operational costs within reach

---

*See [ADR-001](adr/ADR-001-corpus-optimization.md) for detailed decision record*