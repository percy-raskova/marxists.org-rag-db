# Corpus Investigation Skill

**Version**: 1.0
**Created**: 2025-11-08
**Type**: Personal Skill

## Overview

This Claude Code Skill enables systematic investigation of large corpus sections (100GB+) using proven methodologies that achieve **95% token reduction** through computational verification and stratified sampling.

**Origin**: Based on the methodology used to successfully analyze the 121GB Marxists Internet Archive.

## What This Skill Does

- Systematically investigates large document collections
- Extracts metadata schemas from corpus sections
- Recommends chunking strategies for RAG pipelines
- Produces comprehensive section analysis specifications
- Uses computational tools (grep, find) for pattern verification
- Employs stratified sampling for token efficiency

## Installation

Already installed! This skill is in your Personal Skills directory:

```
~/.claude/skills/corpus-investigation/
├── SKILL.md        # Main skill instructions
├── reference.md    # Command templates and reference guide
└── README.md       # This file
```

## Quick Start

Just mention investigation tasks naturally:

- "Investigate the corpus in /data/archive/"
- "Analyze this dataset structure"
- "Study the organization of /path/to/corpus/"
- "Document this corpus for RAG ingestion"
- "Investigation and study of /corpus/section/"

Claude will automatically activate this skill and follow the 5-phase methodology.

## Skill Triggers

The skill activates when you mention:

- "investigate corpus"
- "analyze archive"
- "study dataset"
- "document corpus"
- "investigation and study" (Maoist methodology reference)
- Large file/dataset analysis tasks (>1GB)

## Methodology Overview

### 5-Phase Framework

1. **Reconnaissance (10%)**: Directory structure, sizes, file counts
2. **Stratified Sampling (40%)**: Sample 15-25 representative files
3. **Pattern Verification (30%)**: Use grep/find to verify patterns
4. **Edge Case Analysis (10%)**: Sample outliers and exceptions
5. **Synthesis (10%)**: Produce section analysis document

### Token Efficiency

**Achieves 95% token reduction** through:

- Using grep/find instead of reading files
- Strategic sampling instead of exhaustive reading
- Extracting structure instead of full content
- Aggregating statistics instead of individual descriptions
- Referencing examples instead of reproducing them

**Average Investigation**: 15,000-30,000 tokens per section
**Output**: 5,000-10,000 token specification document

## What You Get

A comprehensive **Section Analysis Document** with:

1. Executive summary
2. Directory structure and size distribution
3. File type analysis (HTML, PDF)
4. HTML structure patterns
5. **5-layer metadata schema** (file system, meta tags, breadcrumb, semantic CSS, content-derived)
6. Linking architecture
7. Unique characteristics
8. **Chunking recommendations** with rationale
9. **RAG integration strategy**
10. Edge cases and exceptions
11. Processing risks and mitigations
12. Sample files analyzed
13. Pattern verification commands (reproducible)
14. Recommendations for implementation
15. Open questions

## Example Usage

```bash
# Example 1: Investigate a corpus section
"Please investigate the /data/marxist-archive/history/ section"

# Example 2: Analyze dataset for RAG
"I need to analyze the /corpus/academic-papers/ dataset structure
 to design a RAG ingestion pipeline"

# Example 3: Study organization
"Study the organization of /archive/periodicals/ to extract
 metadata schemas"

# Example 4: Investigation and study (Maoist reference)
"Conduct an investigation and study of the /data/corpus/ section"
```

## Key Features

### Stratified Sampling

Samples across dimensions:
- **Size**: Large (>1GB), medium (100MB-1GB), small (<100MB)
- **Temporal**: Early, mid, late periods (if time-based)
- **Type**: HTML vs PDF, different naming patterns
- **Depth**: Index pages, category pages, content pages

### Computational Verification

Uses bash commands to verify patterns:
```bash
# Meta tag coverage
grep -r '<meta name="author"' /path | wc -l

# CSS class distribution
grep -roh 'class="[^"]*"' /path | sort | uniq -c | sort -rn

# Link patterns
grep -roh 'href="[^"]*"' /path | head -100
```

### 5-Layer Metadata Extraction

1. **File System**: Paths, directories, filenames
2. **HTML Meta Tags**: Author, title, description, classification
3. **Breadcrumb**: Navigation trails, categorical location
4. **Semantic CSS**: Curator context, provenance, annotations
5. **Content-Derived**: Word count, footnotes, images, reading time

### Confidence Levels

Every pattern includes confidence:
- **100%**: Universal (all files)
- **90-99%**: Standard (rare exceptions)
- **75-89%**: Common (notable exceptions)
- **50-74%**: Frequent (not standard)
- **<50%**: Occasional

## Resources

### Skill Files

- **SKILL.md**: Complete methodology and instructions (12,000 tokens)
- **reference.md**: Command templates and quick reference (8,000 tokens)
- **README.md**: This installation and usage guide (2,000 tokens)

### Reference Documentation

Original methodology source:
```
/home/user/projects/marxist-rag/docs/corpus-analysis/
├── 00-investigation-methodology-spec.md  # Detailed methodology
├── 01-archive-section-analysis.md        # Example investigation
├── 00-corpus-overview.md                 # Corpus architecture
└── README.md                             # Documentation index
```

## Testing the Skill

Try these test phrases:

```
1. "What does the corpus-investigation skill do?"
2. "Investigate the sample corpus at /home/user/projects/marxist-rag/"
3. "Analyze the archive section structure"
4. "Study this dataset for RAG ingestion"
```

Claude should recognize these as investigation tasks and activate the skill.

## Use Cases

### 1. RAG Pipeline Design

- Extract metadata schemas for vector DB design
- Recommend chunking strategies for embeddings
- Identify processing pipeline requirements
- Document corpus characteristics

### 2. Dataset Documentation

- Understand large dataset organization
- Extract structural patterns
- Document file naming conventions
- Identify edge cases and exceptions

### 3. Archive Analysis

- Study historical archive structure
- Extract temporal metadata patterns
- Document content types and organization
- Recommend preservation strategies

### 4. Quality Assessment

- Assess OCR quality in PDF collections
- Identify metadata completeness
- Find encoding issues
- Document broken links and errors

### 5. Cross-Corpus Integration

- Understand linking architecture
- Map cross-references between sections
- Document knowledge graph structure
- Plan multi-corpus RAG systems

## Skill Behavior

### What the Skill Does

- Follows systematic 5-phase methodology
- Uses computational tools (grep, find, du, wc)
- Samples strategically (15-25 files per section)
- Verifies patterns across entire corpus
- Documents confidence levels for patterns
- Produces actionable specifications

### What the Skill Doesn't Do

- Read every file exhaustively (uses sampling)
- Process or modify corpus files (read-only analysis)
- Make architectural decisions (provides recommendations)
- Execute RAG pipeline (provides specifications)

### Allowed Tools

The skill is restricted to these tools for safety and focus:
- **Read**: Sample files, read documentation
- **Grep**: Pattern extraction and verification
- **Glob**: File discovery
- **Bash**: Run reconnaissance and verification commands
- **Write**: Create section analysis documents

## Token Efficiency Examples

### Inefficient Approach
```
Read 100 files to find meta tags → 500,000 tokens
Read every author's archive → 1,000,000 tokens
Include full HTML of examples → 50,000 tokens
```

### Efficient Approach (This Skill)
```
grep meta tags + read 5 samples → 25,000 tokens (95% reduction)
Read 3 authors + verify with find → 50,000 tokens (95% reduction)
Include 1-2 examples + reference → 5,000 tokens (90% reduction)
```

## Quality Assurance

Every investigation includes:

- ✅ Complete directory structure with sizes
- ✅ Accurate file counts (HTML, PDF, other)
- ✅ Full meta tag schema extraction
- ✅ CSS class inventory
- ✅ Link pattern documentation
- ✅ Chunking strategy with rationale
- ✅ RAG integration approach
- ✅ Edge case documentation
- ✅ Sample files list
- ✅ Verification commands (reproducible)
- ✅ Confidence levels for all patterns
- ✅ Open questions for user decisions

## Troubleshooting

### Skill Not Activating?

1. Check skill is installed: `ls ~/.claude/skills/corpus-investigation/`
2. Use explicit trigger phrases: "investigate corpus at /path/"
3. Mention large dataset analysis tasks
4. Reference investigation and study methodology

### Investigation Taking Too Long?

1. Check token budget (should be 15k-30k per section)
2. Ensure using grep/find instead of reading files
3. Limit sample size to 15-25 files
4. Extract structure only, not full content

### Unclear Results?

1. Check confidence levels are specified
2. Verify bash commands are documented
3. Ensure patterns are verified computationally
4. Confirm metadata schema is code-ready

## Updates and Improvements

This skill is based on proven methodology but can be enhanced:

- Add support for new corpus types (databases, APIs, etc.)
- Include additional pattern recognition techniques
- Expand metadata layer templates
- Add specialized sampling strategies
- Include domain-specific analysis patterns

To update: Modify SKILL.md or reference.md in the skill directory.

## Background

This skill codifies the methodology used to successfully analyze the 121GB Marxists Internet Archive (96,637 HTML files, 21,141 PDFs). The investigation produced:

- Complete corpus documentation (7,000 tokens)
- Detailed section analysis (8,000 tokens)
- Metadata schema specifications (5 layers)
- Chunking strategies for RAG ingestion
- Processing pipeline recommendations

**Total investigation**: ~50,000 tokens for 121GB corpus
**Without methodology**: Would require 2,000,000+ tokens

## References

**Original Methodology**:
- Mao Zedong's "Investigation and Study" (1930) - Systematic field research methodology
- Stratified sampling theory - Statistical sampling across dimensions
- Computational linguistics - Pattern recognition via grep/regex
- RAG architecture design - Chunking and metadata strategies

**Technical Foundation**:
- bash/shell utilities (grep, find, du, wc, sort, uniq)
- HTML parsing and structure extraction
- Metadata schema design
- Vector database architecture
- Large-scale corpus processing

## License and Usage

This skill is part of the marxist-rag project Personal Skills.

- ✅ Use for corpus investigation tasks
- ✅ Modify for your specific corpus types
- ✅ Share improvements and enhancements
- ✅ Apply to any large dataset analysis

## Support

For questions or issues:

1. Read SKILL.md for detailed methodology
2. Check reference.md for command templates
3. Review example investigations in `/home/user/projects/marxist-rag/docs/corpus-analysis/`
4. Consult original methodology spec: `00-investigation-methodology-spec.md`

---

**Status**: ✅ Installed and Ready
**Version**: 1.0
**Last Updated**: 2025-11-08
**Skill Type**: Personal Skill
**Activation**: Automatic (when investigation tasks detected)
