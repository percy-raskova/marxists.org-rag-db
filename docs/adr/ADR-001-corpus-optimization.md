# ADR-001: Corpus Optimization from 200GB to 50GB

**Status**: Implemented
**Date**: 2025-11-08
**Decision Makers**: User + Claude Code Assistant

---

## Context

The Marxists Internet Archive (MIA) as originally extracted contained approximately 200GB of mixed content including:
- HTML documents (theoretical texts, historical documents, reference materials)
- PDF files (scanned books, periodicals, pamphlets)
- Audio files (audiobooks, podcasts, speeches)
- Image files (scans, photos, diagrams, covers)
- Video files (documentaries, lectures)
- Non-English content in 40+ languages (28GB)
- Large specialized archives (ETOL 61GB, EROL 14GB, periodicals 56GB)

This massive scale presented several challenges:
1. **Computational Cost**: Embedding generation would cost $400-600 on GPU rentals
2. **Storage Cost**: Vector database would require enterprise-grade infrastructure
3. **Processing Time**: Estimated 200+ hours of processing time
4. **Complexity**: Managing heterogeneous content types with varying quality
5. **Scope Creep**: Risk of losing focus on core theoretical texts

## Ideological Neutrality Statement

**Important**: While the project lead (Persephone Raskova) identifies as a Marxist-Leninist-Maoist Third Worldist, this corpus optimization was conducted with strict ideological neutrality. No content was removed based on ideological tendency, sectarian affiliation, or political perspective.

The decisions to defer ETOL (Trotskyist encyclopedia) and EROL (anti-Revisionist/Maoist encyclopedia) were based purely on technical constraints (size, processing complexity) rather than ideological preference. Both archives are preserved for future inclusion, maintaining the MIA's comprehensive, non-sectarian approach to Marxist history.

This project's mission is to faithfully translate historical materials into AI-legible formats, preserving the full spectrum of Marxist thought - from anarcho-communism to Marxism-Leninism, from council communism to Maoism, from Trotskyism to left communism. The goal is historical preservation and accessibility, not ideological curation.

## Decision

We decided to strategically reduce the corpus from 200GB to ~50GB by:

### What We Removed
1. **All Audio Files** (~5GB)
   - Audiobook recordings (duplicates of HTML texts)
   - Podcast episodes
   - Recorded speeches

2. **All Video Files** (~2GB)
   - Documentary films
   - Lecture recordings
   - Historical footage

3. **All Image Files** (~8GB)
   - Book covers
   - Author photos
   - Scanned diagrams
   - Decorative images
   - *Exception: Inline images in PDFs retained for context*

4. **Duplicate PDFs** (~15GB)
   - PDFs that have HTML equivalents
   - Multiple format versions of same work
   - Lower quality scans when better versions exist

5. **Non-English Content** (~28GB)
   - 40+ language directories
   - Specifically removed: Russian (1.2GB), Romanian (2.4GB), Chinese (21GB), etc.
   - Can be added back in future phases

6. **Specialized Archives** (Deferred - ~131GB)
   - ETOL (Encyclopedia of Trotskyism On-Line): 61GB
   - EROL (Encyclopedia of anti-Revisionism On-Line): 14GB
   - USA labor periodicals: 56GB
   - These remain available for future enhancement

### What We Kept
1. **All HTML Content** (~40GB)
   - Primary source for theoretical texts
   - Best format for text extraction
   - Contains semantic markup and metadata

2. **Essential PDFs** (~10GB)
   - Works without HTML equivalents
   - Unique historical documents
   - Important pamphlets and rare texts

3. **Core Sections**
   - Archive (4.5GB): Theoretical works by author
   - History (~35GB): Core historical texts
   - Subject (9.1GB): Thematic collections with curator annotations
   - Glossary (62MB): Entity definitions and encyclopedia entries
   - Reference (582MB): Supporting materials

## Consequences

### Positive
1. **75% Size Reduction**: 200GB → 50GB makes project feasible
2. **Cost Savings**: Embedding costs reduced from $400-600 to $100-150
3. **Faster Processing**: Estimated time reduced from 200 to 50 hours
4. **Better Focus**: Concentration on text-based knowledge content
5. **Simpler Architecture**: No need for multi-modal processing pipelines
6. **Manageable Scope**: Can complete in weeks rather than months

### Negative
1. **Lost Content Types**: No audio/video analysis capabilities
2. **Language Limitation**: English-only for V1 (excludes important works)
3. **Deferred Content**: ETOL/EROL encyclopedias not immediately available
4. **No Periodicals**: Labor newspapers excluded (valuable primary sources)
5. **Reduced Coverage**: Missing ~75% of original archive

### Neutral
1. **Reversible Decision**: Original archive preserved, can re-add content
2. **Phased Approach**: Sets up natural V2 enhancement opportunities
3. **Clear Boundaries**: Simplified scope makes project more manageable

## Implementation Details

### Removal Process
```bash
# Audio/video removal (example)
find /media/user/marxists.org -type f \( -name "*.mp3" -o -name "*.mp4" -o -name "*.wav" -o -name "*.avi" \) -delete

# Image removal (preserving inline PDF images)
find /media/user/marxists.org -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.gif" \) -not -path "*/pdf/*" -delete

# Non-English content removal
rm -rf /media/user/marxists.org/www.marxists.org/romana
rm -rf /media/user/marxists.org/www.marxists.org/russkij
# ... (other languages)

# Large archive deferral
mv /media/user/marxists.org/www.marxists.org/history/etol /backup/future-enhancement/
mv /media/user/marxists.org/www.marxists.org/history/erol /backup/future-enhancement/
```

### Size Breakdown After Optimization
| Component | Original | Optimized | Reduction |
|-----------|----------|-----------|-----------|
| Total Size | 200GB | ~50GB | 75% |
| HTML Files | ~96,000 | ~40,000 | 58% |
| PDF Files | ~38,000 | ~10,000 | 74% |
| Audio Files | ~5,000 | 0 | 100% |
| Image Files | ~50,000 | 0* | ~100% |
| Languages | 40+ | 1 (English) | 98% |

*Inline PDF images preserved

## Future Enhancements

This decision explicitly enables future phases:

### Phase 2: Specialized Archives
- Add ETOL (61GB) as separate vector collection
- Add EROL (14GB) as separate vector collection
- Dedicated processing pipeline for encyclopedic content

### Phase 3: Periodicals
- Process labor newspapers (56GB) with OCR pipeline
- Time-series aware embeddings
- Separate collection for journalistic content

### Phase 4: Multilingual
- Start with Spanish (4.2GB) and French (1.1GB)
- Cross-lingual embeddings
- Parallel text detection for translations

### Phase 5: Multimodal
- Audio transcription pipeline
- Image analysis for diagrams/charts
- Video processing for documentaries

## Alternatives Considered

1. **Keep Everything** (200GB)
   - Rejected: Too expensive and complex for initial implementation

2. **HTML Only** (~40GB)
   - Rejected: Would lose valuable PDF-only content

3. **Archive Section Only** (4.5GB)
   - Rejected: Too limited, missing important historical context

4. **Include One Language** (e.g., Spanish)
   - Rejected: Adds complexity without critical mass of content

## References

- Original corpus analysis: `docs/corpus-analysis/00-corpus-overview.md`
- Size investigation results: Conversation on 2025-11-08
- Cost projections: `ARCHITECTURE.md` (original 200GB estimates)
- Implementation tracking: `.github/projects/corpus-analysis.md`

## Review and Approval

- **Proposed by**: Claude Code Assistant
- **Reviewed by**: Persephone Raskova (Project Lead/Principal Architect)
- **Approved by**: Persephone Raskova
- **Implementation**: 2025-11-08
- **Ideological Review**: Confirmed no sectarian bias in content selection

---

## Addendum

### Metrics for Success
- [ ] Embedding generation completes in <50 hours
- [ ] Total infrastructure cost <$200 for processing
- [ ] Monthly operational cost <$50
- [ ] Query performance <500ms p95
- [ ] All HTML content successfully processed

### Rollback Plan
If we need to re-add removed content:
1. Original archive preserved at `/media/user/marxists.org.tar.gz`
2. Deferred content backed up to `/backup/future-enhancement/`
3. Can selectively re-add content types as needed
4. Vector DB supports multiple collections for separation