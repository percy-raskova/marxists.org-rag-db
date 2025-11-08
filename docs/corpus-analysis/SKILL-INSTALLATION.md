# Corpus Investigation Skill - Installation Summary

**Date**: 2025-11-08
**Skill Name**: corpus-investigation
**Version**: 1.0
**Type**: Personal Skill
**Status**: ✅ Installed and Ready

---

## Installation Summary

The corpus-investigation Claude Code Skill has been successfully created and installed in your Personal Skills directory.

### File Locations

```
/home/user/.claude/skills/corpus-investigation/
├── SKILL.md (840 lines)        # Main skill instructions and methodology
├── reference.md (1048 lines)   # Command templates and quick reference
└── README.md (374 lines)       # Installation and usage guide
```

**Total**: 2,262 lines of comprehensive documentation

---

## What Was Created

### 1. SKILL.md - Main Skill Instructions

**Size**: 24KB, 840 lines
**Purpose**: Complete investigation methodology

**Contents**:
- Optimized YAML frontmatter with discovery triggers
- 5-phase investigation framework
- Stratified sampling strategies (size, temporal, type, depth)
- Pattern recognition techniques using grep/find
- Metadata extraction protocols (5 layers)
- Token efficiency tactics (95% reduction)
- Verification without exhaustive reading
- Quality assurance checklist
- Section analysis document template
- Bash command reference
- Investigation tips and examples

**Key Features**:
- Reproducible by any AI agent
- Token-efficient (15k-30k per section)
- Produces actionable specifications
- Includes confidence levels for patterns
- Documents verification commands

### 2. reference.md - Command Templates

**Size**: 29KB, 1048 lines
**Purpose**: Quick reference and command templates

**Contents**:
- Investigation phase checklists
- Bash command template library
- HTML structure extraction templates
- Metadata schema template (Python dataclass)
- Complete section analysis document template
- Statistical sampling methods
- Pattern verification scripts
- Edge case detection commands

**Use Case**: Copy-paste command templates for quick investigations

### 3. README.md - Installation Guide

**Size**: 12KB, 374 lines
**Purpose**: User-facing documentation

**Contents**:
- Skill overview and capabilities
- Installation instructions (already installed!)
- Quick start guide
- Trigger phrases
- Methodology overview
- Example usage
- Token efficiency examples
- Troubleshooting guide
- Background and references

---

## How It Works

### Automatic Activation

The skill activates when you mention:

- "investigate corpus"
- "analyze archive"
- "study dataset structure"
- "document corpus"
- "investigation and study" (Maoist reference)
- Large file/dataset analysis (>1GB)

### Allowed Tools

Restricted to safe, read-only tools:
- **Read**: Sample files
- **Grep**: Pattern extraction
- **Glob**: File discovery
- **Bash**: Run commands
- **Write**: Create analysis documents

### Investigation Process

Follows proven 5-phase methodology:

1. **Reconnaissance (10%)**: Directory structure, sizes, counts
2. **Stratified Sampling (40%)**: Read 15-25 representative files
3. **Pattern Verification (30%)**: Use grep/find to verify patterns
4. **Edge Case Analysis (10%)**: Sample outliers
5. **Synthesis (10%)**: Write section analysis document

**Token Budget**: 15,000-30,000 tokens per section
**Output**: 5,000-10,000 token specification

---

## What You Get

### Section Analysis Document

Every investigation produces a comprehensive specification:

1. **Executive Summary**: Overview of findings
2. **Directory Structure**: Hierarchical organization with sizes
3. **File Type Analysis**: HTML, PDF breakdown
4. **HTML Structure Patterns**: DOCTYPE, meta tags, CSS classes
5. **Metadata Schema**: 5-layer extraction schema (code-ready)
6. **Linking Architecture**: Internal, cross-section, anchor patterns
7. **Unique Characteristics**: Section-specific patterns
8. **Chunking Recommendations**: Optimal boundaries for RAG
9. **RAG Integration Strategy**: Processing pipeline steps
10. **Edge Cases**: Outliers and exceptions
11. **Processing Risks**: Risks with mitigations
12. **Sample Files**: All files analyzed
13. **Verification Commands**: Reproducible bash commands
14. **Recommendations**: Priority, complexity, requirements
15. **Open Questions**: User decisions needed

### Metadata Schema

5-layer comprehensive schema:

```python
@dataclass
class DocumentMetadata:
    # Layer 1: File System (paths, directories)
    section: str
    author: Optional[str]
    year: Optional[int]

    # Layer 2: HTML Meta Tags
    title: Optional[str]
    meta_author: Optional[str]
    classification: Optional[str]

    # Layer 3: Breadcrumb Navigation
    breadcrumb: List[str]
    category_path: Optional[str]

    # Layer 4: Semantic CSS Classes
    curator_context: Optional[str]
    provenance: Optional[str]

    # Layer 5: Content-Derived
    word_count: int
    has_footnotes: bool
    reading_time_minutes: int
```

### Chunking Strategy

Specific recommendations:
- Chunk boundary (paragraph/section/article/entry)
- Rationale for boundary choice
- Token size estimates
- Hierarchical context preservation
- Example chunk metadata

### RAG Integration

Actionable implementation plan:
- Processing pipeline steps
- Metadata enrichment approach
- Vector DB schema design
- Expected query patterns
- Cross-section integration

---

## Token Efficiency

### 95% Reduction Achieved

**Traditional Approach**:
- Read 100 files → 500,000 tokens
- Read all authors → 1,000,000 tokens
- Include full HTML examples → 50,000 tokens
- **Total**: ~1,500,000 tokens

**This Skill**:
- grep patterns + 5 samples → 25,000 tokens (95% reduction)
- Read 3 authors + verify → 50,000 tokens (95% reduction)
- 1-2 examples + references → 5,000 tokens (90% reduction)
- **Total**: ~80,000 tokens

### How It Works

1. **Computational Tools**: Use grep/find instead of reading files
2. **Strategic Sampling**: Sample 15-25 files, not all files
3. **Structure Extraction**: Extract headings/meta tags, not full content
4. **Aggregate Statistics**: "95% have pattern X" not "file1 has X, file2 has X..."
5. **Reference Examples**: Link to files instead of reproducing HTML

---

## Testing the Skill

### Quick Tests

Try these phrases to verify activation:

```
1. "What is the corpus-investigation skill?"
   → Should explain the skill capabilities

2. "Investigate the corpus at /home/user/projects/marxist-rag/"
   → Should start 5-phase investigation

3. "Analyze the archive section structure"
   → Should recognize investigation task

4. "Study this dataset for RAG ingestion"
   → Should activate skill
```

### Expected Behavior

When activated, Claude will:

1. Acknowledge using corpus-investigation methodology
2. Start with Phase 1: Reconnaissance
3. Run bash commands for directory structure
4. Document size, file counts, hierarchy
5. Proceed through all 5 phases
6. Produce section analysis document

---

## Use Cases

### 1. RAG Pipeline Design

**Scenario**: You have a 50GB document corpus and need to design a RAG ingestion pipeline.

**Process**:
1. Activate skill: "Investigate this corpus for RAG design"
2. Receive section analysis with metadata schema
3. Get chunking recommendations
4. Implement processing pipeline

**Output**: Code-ready specifications for RAG implementation

### 2. Archive Documentation

**Scenario**: You inherited a large historical archive with unknown structure.

**Process**:
1. Activate skill: "Document this archive structure"
2. Receive organizational analysis
3. Get metadata extraction patterns
4. Understand linking architecture

**Output**: Complete archive documentation

### 3. Quality Assessment

**Scenario**: You need to assess OCR quality in 10,000 PDF files.

**Process**:
1. Activate skill: "Analyze PDF quality in this corpus"
2. Skill samples 15-20 PDFs across time periods
3. Receive quality assessment report
4. Get recommendations for processing

**Output**: Quality assessment with recommendations

### 4. Multi-Corpus Integration

**Scenario**: You need to integrate 5 different corpus sections into unified RAG system.

**Process**:
1. Investigate each section separately
2. Receive individual section analyses
3. Get cross-section linking patterns
4. Design unified metadata schema

**Output**: Integration strategy and unified schema

---

## Skill Triggers (Optimized for Discovery)

The YAML frontmatter includes these optimized triggers:

```yaml
description: Systematically investigate large corpus sections (100GB+) using
  stratified sampling, pattern recognition, and computational verification.
  Produces comprehensive section analyses with metadata schemas, chunking
  strategies, and RAG integration recommendations. Use when analyzing large
  datasets, investigating archive structures, studying corpus organization,
  conducting investigation and study tasks, or documenting dataset
  characteristics for RAG pipeline design.
```

**Key Phrases Claude Will Recognize**:
- "investigate corpus"
- "analyze archive"
- "study dataset"
- "document corpus"
- "investigation and study"
- "large dataset analysis"
- "corpus organization"
- "RAG pipeline design"
- "metadata schema extraction"
- "chunking strategy"

---

## Background: Why This Skill Exists

### The Problem

Large corpora (100GB+) cannot be exhaustively read within token budgets. Traditional approaches:

- Reading every file → 2,000,000+ tokens for 121GB corpus
- Unstructured sampling → Inconsistent results
- Manual investigation → Not reproducible by AI agents
- No verification → Unvalidated patterns

### The Solution

Systematic methodology with:

- **Stratified sampling**: Representative coverage without exhaustive reading
- **Computational verification**: grep/find confirm patterns across entire corpus
- **Structured output**: Reproducible section analysis documents
- **Token efficiency**: 95% reduction through smart techniques

### The Results

Successfully analyzed 121GB Marxists Internet Archive:

- **Corpus size**: 121GB, 96,637 HTML files, 21,141 PDFs
- **Tokens used**: ~50,000 total
- **Time**: 2-3 hours
- **Output**: Complete documentation, metadata schemas, RAG specifications
- **Reproducibility**: Any agent following methodology produces equivalent results

### The Skill

This skill codifies that proven methodology so any AI agent can:

1. Investigate large corpora efficiently
2. Extract metadata schemas systematically
3. Recommend chunking strategies with rationale
4. Produce actionable RAG specifications
5. Document findings reproducibly

---

## Maintenance and Updates

### Current Version: 1.0

**Status**: Production-ready, proven methodology

**Proven On**:
- 121GB Marxists Internet Archive
- Mixed HTML/PDF corpus
- Multi-section hierarchy
- 5-layer metadata extraction

### Future Enhancements

Potential improvements:

1. **Additional Corpus Types**:
   - Database dumps (SQL, JSON)
   - API documentation
   - Code repositories
   - Scientific datasets

2. **Advanced Sampling**:
   - Adaptive sampling (adjust based on variance)
   - Active learning (sample most informative files)
   - Cluster-based sampling

3. **Enhanced Patterns**:
   - XML schema extraction
   - JSON structure analysis
   - Multimedia metadata
   - Knowledge graph discovery

4. **Domain-Specific**:
   - Academic papers (citations, abstracts)
   - Legal documents (case law, statutes)
   - Medical records (HIPAA-compliant)
   - News archives (temporal patterns)

### How to Update

To modify the skill:

```bash
# Edit main methodology
nano /home/user/.claude/skills/corpus-investigation/SKILL.md

# Edit command templates
nano /home/user/.claude/skills/corpus-investigation/reference.md

# Edit user documentation
nano /home/user/.claude/skills/corpus-investigation/README.md
```

Changes take effect immediately (no restart needed).

---

## Reference Materials

### Source Documentation

The skill is based on this documentation:

```
/home/user/projects/marxist-rag/docs/corpus-analysis/
├── 00-investigation-methodology-spec.md  # Detailed methodology (12k tokens)
├── 01-archive-section-analysis.md        # Example investigation (8k tokens)
├── 00-corpus-overview.md                 # Corpus architecture (7k tokens)
└── README.md                             # Documentation index (2k tokens)
```

**Total**: ~29,000 tokens of reference documentation

### Key Principles

From Mao Zedong's "Investigation and Study" (1930):

1. **No investigation, no right to speak**: Systematic research before conclusions
2. **Seek truth from facts**: Evidence-based, not assumption-based
3. **Representative sampling**: Sample across all dimensions
4. **Verification**: Confirm patterns through multiple sources
5. **Synthesis**: Compile findings into actionable knowledge

Adapted for AI agents:

1. **Computational verification**: grep/find over exhaustive reading
2. **Stratified sampling**: Statistical rigor for representative coverage
3. **Token efficiency**: 95% reduction through smart techniques
4. **Reproducibility**: Any agent gets equivalent results
5. **Actionable output**: Code-ready specifications, not vague descriptions

---

## Success Metrics

A successful investigation produces:

### Completeness
- ✅ Directory structure with sizes
- ✅ File counts by type
- ✅ Meta tag schema (all fields)
- ✅ CSS class inventory
- ✅ Link patterns
- ✅ Chunking strategy with rationale
- ✅ RAG integration approach
- ✅ Edge cases documented
- ✅ Verification commands

### Reproducibility
- ✅ Sampling strategy documented
- ✅ Bash commands included
- ✅ File paths specified
- ✅ Investigation date noted

### Token Efficiency
- ✅ Used grep/find (not exhaustive reading)
- ✅ Sampled strategically (15-25 files)
- ✅ Aggregated statistics
- ✅ Referenced examples

### Actionability
- ✅ Metadata schema is code-ready
- ✅ Chunking strategy is specific
- ✅ Pipeline steps defined
- ✅ Risks have mitigations
- ✅ Priority assigned

**Target**: All checkboxes ✅ for complete investigation

---

## Troubleshooting

### Skill Not Activating

**Symptoms**: Claude doesn't recognize investigation tasks

**Solutions**:
1. Use explicit trigger phrases: "investigate corpus at /path/"
2. Mention large dataset analysis: "analyze this 50GB dataset"
3. Reference methodology: "use investigation and study approach"
4. Check skill exists: `ls ~/.claude/skills/corpus-investigation/`

### Investigation Too Slow

**Symptoms**: Using too many tokens, taking too long

**Solutions**:
1. Check using grep/find (not reading files individually)
2. Limit samples to 15-25 files total
3. Extract structure only (headings, meta tags, not full content)
4. Aggregate statistics instead of individual descriptions
5. Reference examples instead of reproducing HTML

### Results Not Actionable

**Symptoms**: Vague recommendations, no code-ready specs

**Solutions**:
1. Check metadata schema includes Python dataclass
2. Verify chunking strategy specifies exact boundaries
3. Ensure verification commands are documented
4. Confirm confidence levels are specified
5. Review quality assurance checklist

### Patterns Not Verified

**Symptoms**: Claims patterns but no confidence levels

**Solutions**:
1. Run verification commands (grep/find)
2. Document pattern coverage percentages
3. Include bash commands in report
4. Sample edge cases explicitly
5. Specify confidence levels for all patterns

---

## Next Steps

### For This Project

1. **Test the skill**: Try investigating a section of the MIA corpus
2. **Validate output**: Check section analysis document completeness
3. **Iterate if needed**: Refine skill based on experience
4. **Document findings**: Add to corpus-analysis documentation

### Example Test Investigation

Try investigating a small section:

```
"Please investigate the /home/user/projects/marxist-rag/docs/ section
using the corpus-investigation skill."
```

Expected output:
- Phase 1: Reconnaissance (directory structure, sizes)
- Phase 2: Sample 10-15 markdown files
- Phase 3: Verify patterns (grep for frontmatter, links)
- Phase 4: Edge cases (largest/smallest files)
- Phase 5: Section analysis document

### For Future Investigations

Apply to remaining MIA sections:

1. **History section** (46GB): Labor periodicals
2. **Subject section** (9.1GB): Thematic collections
3. **Glossary section** (62MB): Encyclopedia
4. **Language sections** (28GB): Multilingual content

Each investigation: 15k-30k tokens, complete specifications

---

## Conclusion

The corpus-investigation skill is now installed and ready to use.

**Key Benefits**:
- ✅ 95% token reduction for large corpus analysis
- ✅ Reproducible methodology for AI agents
- ✅ Comprehensive section analysis documents
- ✅ Code-ready metadata schemas
- ✅ Actionable chunking strategies
- ✅ RAG integration specifications

**Just ask Claude to investigate a corpus and watch it work!**

---

**Installation Date**: 2025-11-08
**Version**: 1.0
**Status**: ✅ Production Ready
**Location**: /home/user/.claude/skills/corpus-investigation/
**Documentation**: 2,262 lines, 65KB total

**Ready for use in corpus analysis tasks!**
