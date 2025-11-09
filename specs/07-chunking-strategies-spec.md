# Chunking Strategies Specification

**Version:** 1.0
**Status:** IMPLEMENTATION-READY
**Module:** `src/ingestion/chunking.py`
**Dependencies:**
- Unified Metadata Schema (`docs/corpus-analysis/06-metadata-unified-schema.md`)
- Section analyses 01-05 (`docs/corpus-analysis/`)
- Document Processing Spec (`specs/02-DOCUMENT-PROCESSING-SPEC.md`)

---

## Executive Summary

This specification defines adaptive chunking strategies for the Marxist Internet Archive RAG system based on programmatic corpus analysis of 55,753 HTML documents across 6 corpus sections. The goal is to **preserve semantic coherence** while maintaining consistent chunk sizes for embedding generation.

**Key Design Principles:**

1. **Semantic Preservation**: Chunk at natural rhetorical breaks (section boundaries, paragraph boundaries)
2. **Section-Aware Strategies**: Different sections have different structural characteristics requiring adaptive approaches
3. **Document Structure Respect**: Use heading hierarchies (h1→h6) and CSS classes (.fst, .quoteb) as chunking signals
4. **Consistent Sizing**: Target 512-1024 tokens per chunk (optimal for embedding models)
5. **Edge Case Handling**: Special treatment for index pages, multi-article files, heading-less documents
6. **Fallback Strategies**: Graceful degradation when ideal structure is unavailable

**Chunking Strategy Decision Tree:**

```
Document → Section Type?
  ├─ Archive → Semantic breaks at h3/h4 boundaries (70% good hierarchies)
  ├─ ETOL → Semantic breaks at h3/h4 boundaries (70% good hierarchies)
  ├─ EROL → Semantic breaks at h3 boundaries (90% use h3 as title)
  ├─ History/Other → Paragraph-based chunking (40% have NO headings)
  ├─ Subject → Index filtering + semantic chunking (55% are navigation indexes)
  ├─ Glossary → Entry-based chunking (one chunk per entry, self-contained)
  └─ Reference → Semantic breaks at heading boundaries
```

---

## 1. Chunking Strategy Selection

### 1.1 Strategy Taxonomy

**Primary Strategies (in order of preference):**

1. **Semantic Break Chunking** - Chunk at h3/h4 section boundaries (Archive, ETOL, Reference)
2. **Entry-Based Chunking** - One chunk per encyclopedia entry (Glossary)
3. **Paragraph Cluster Chunking** - Group paragraphs when no headings exist (History/Other)
4. **Token-Based Fallback** - Fixed token count when all else fails (edge cases)

**Selection Algorithm:**

```python
def select_chunking_strategy(metadata: DocumentMetadata, document: str) -> ChunkingStrategy:
    """
    Select optimal chunking strategy based on document metadata and structure.

    Args:
        metadata: DocumentMetadata with section_type and document_structure fields
        document: Markdown content (already converted from HTML)

    Returns:
        ChunkingStrategy enum value
    """
    section = metadata.section_type
    structure = metadata.document_structure

    # Strategy 1: Glossary entry-based chunking
    if section == "glossary":
        return ChunkingStrategy.ENTRY_BASED

    # Strategy 2: Subject section - filter indexes first
    if section == "subject":
        if metadata.rag_priority == "low":  # Index page
            return ChunkingStrategy.SKIP  # Don't chunk navigation indexes
        # For actual content, use semantic breaks
        return ChunkingStrategy.SEMANTIC_BREAKS

    # Strategy 3: Semantic breaks (heading-based) if good heading hierarchy
    if structure.get('heading_depth', 0) >= 3:
        # Good heading hierarchy (h1, h2, h3+)
        return ChunkingStrategy.SEMANTIC_BREAKS

    # Strategy 4: Paragraph clustering for heading-less documents
    if structure.get('heading_depth', 0) == 0:
        # 40% of History/Other documents have NO headings
        return ChunkingStrategy.PARAGRAPH_CLUSTERS

    # Strategy 5: Token-based fallback for minimal structure
    return ChunkingStrategy.TOKEN_BASED
```

---

## 2. Semantic Break Chunking (Primary Strategy)

### 2.1 Overview

**Best for**: Archive (70% good hierarchies), ETOL (70%), EROL (90% h3 structure), Reference

**Principle**: Chunk at natural section boundaries (h3/h4 tags) to preserve argumentative structure of theoretical texts.

**Why Important**: Marxist theoretical texts have **thesis → evidence → synthesis** structure that should not be split mid-argument.

### 2.2 Implementation

```python
class SemanticBreakChunker:
    """
    Chunk at heading boundaries (h3/h4) to preserve semantic units.
    """

    TARGET_MIN_TOKENS = 512
    TARGET_MAX_TOKENS = 1024
    HARD_MAX_TOKENS = 2048  # Split even within sections if exceeded

    def __init__(self, section_type: str):
        """
        Args:
            section_type: "archive", "history/etol", "history/erol", etc.
        """
        self.section_type = section_type
        # EROL uses h3 as primary section marker (not h4)
        self.primary_break_level = "h3" if section_type == "history/erol" else "h4"
        self.secondary_break_level = "h4" if section_type == "history/erol" else "h5"

    def chunk(self, markdown: str, metadata: DocumentMetadata) -> List[Chunk]:
        """
        Chunk markdown at heading boundaries.

        Algorithm:
        1. Parse markdown into heading-delimited sections
        2. Group sections to target 512-1024 tokens
        3. Split oversized sections at secondary break level
        4. Preserve context: include parent headings in metadata
        """
        sections = self._parse_sections(markdown)
        chunks = []
        current_chunk_sections = []
        current_token_count = 0

        for section in sections:
            section_tokens = self._count_tokens(section.content)

            # Case 1: Section exceeds hard max - split internally
            if section_tokens > self.HARD_MAX_TOKENS:
                # Flush current chunk first
                if current_chunk_sections:
                    chunks.append(self._create_chunk(current_chunk_sections, metadata))
                    current_chunk_sections = []
                    current_token_count = 0

                # Split large section at secondary break level
                subsections = self._split_large_section(section)
                for subsection in subsections:
                    chunks.append(self._create_chunk([subsection], metadata))

                continue

            # Case 2: Adding section would exceed target max
            if current_token_count + section_tokens > self.TARGET_MAX_TOKENS:
                # Flush current chunk
                if current_chunk_sections:
                    chunks.append(self._create_chunk(current_chunk_sections, metadata))
                current_chunk_sections = [section]
                current_token_count = section_tokens
            else:
                # Add to current chunk
                current_chunk_sections.append(section)
                current_token_count += section_tokens

        # Flush remaining chunk
        if current_chunk_sections:
            chunks.append(self._create_chunk(current_chunk_sections, metadata))

        return chunks

    def _parse_sections(self, markdown: str) -> List[Section]:
        """
        Parse markdown into sections delimited by primary break level headings.

        Returns:
            List of Section objects with heading hierarchy and content
        """
        import re

        sections = []
        lines = markdown.split('\n')
        current_section_lines = []
        current_heading = None
        heading_hierarchy = []  # Stack of parent headings

        for line in lines:
            # Check for heading (markdown format: ## Heading or ### Heading)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2)

                # Check if this is a primary break level
                is_primary_break = (
                    (self.primary_break_level == "h3" and heading_level == 3) or
                    (self.primary_break_level == "h4" and heading_level == 4)
                )

                if is_primary_break:
                    # Save previous section
                    if current_section_lines:
                        sections.append(Section(
                            heading=current_heading,
                            content='\n'.join(current_section_lines),
                            hierarchy=heading_hierarchy.copy()
                        ))

                    # Start new section
                    current_section_lines = [line]
                    current_heading = heading_text
                    heading_hierarchy = self._update_hierarchy(heading_hierarchy, heading_level, heading_text)
                else:
                    # Part of current section
                    current_section_lines.append(line)
                    # Update hierarchy for nested headings
                    if heading_level < 3:  # h1 or h2 (document/chapter title)
                        heading_hierarchy = self._update_hierarchy(heading_hierarchy, heading_level, heading_text)
            else:
                current_section_lines.append(line)

        # Save final section
        if current_section_lines:
            sections.append(Section(
                heading=current_heading,
                content='\n'.join(current_section_lines),
                hierarchy=heading_hierarchy.copy()
            ))

        return sections

    def _split_large_section(self, section: Section) -> List[Section]:
        """
        Split sections exceeding HARD_MAX_TOKENS at secondary break level.

        Fallback to paragraph breaks if no secondary headings.
        """
        # Try splitting at secondary break level (h5 or h4)
        subsections = self._parse_subsections(section, self.secondary_break_level)

        if subsections and len(subsections) > 1:
            return subsections

        # Fallback: Split by paragraphs
        return self._split_by_paragraphs(section, self.HARD_MAX_TOKENS)

    def _create_chunk(self, sections: List[Section], metadata: DocumentMetadata) -> Chunk:
        """
        Create chunk from sections with metadata preservation.
        """
        # Combine section content
        content = '\n\n'.join(s.content for s in sections)

        # Build chunk metadata
        chunk_metadata = {
            **metadata.to_dict(),  # Inherit all document metadata
            "chunk_headings": [s.heading for s in sections if s.heading],
            "chunk_hierarchy": sections[0].hierarchy if sections else [],
            "section_count": len(sections),
        }

        return Chunk(
            content=content,
            metadata=chunk_metadata,
            chunk_id=self._generate_chunk_id(metadata, sections),
            chunk_index=len(self.chunks_created)  # Track chunk position
        )

    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count (words * 1.3 for English text).
        For precise counting, use tiktoken or transformers tokenizer.
        """
        words = len(text.split())
        return int(words * 1.3)  # Conservative estimate

@dataclass
class Section:
    """Represents a document section with heading hierarchy."""
    heading: Optional[str]
    content: str
    hierarchy: List[str]  # Parent headings (e.g., ["Chapter 1", "Section A"])
```

### 2.3 Example Output

**Input (Archive: Capital Ch1, Section on Value):**

```markdown
# Capital Volume I

## Chapter 1: Commodities

### Section 1: The Two Factors of a Commodity

The wealth of those societies in which the capitalist mode of production prevails,
presents itself as "an immense accumulation of commodities," its unit being a single
commodity. Our investigation must therefore begin with the analysis of a commodity.

A commodity is, in the first place, an object outside us, a thing that by its properties
satisfies human wants of some sort or another. The nature of such wants, whether, for
instance, they spring from the stomach or from fancy, makes no difference.

[... 300 more words ...]

### Section 2: The Twofold Character of the Labour Embodied in Commodities

At first sight a commodity presented itself to us as a complex of two things – use value
and exchange value. Later on, we saw also that labour, too, possesses the same twofold
nature; for, so far as it finds expression in value, it does not possess the same
characteristics that belong to it as a creator of use values.

[... 400 more words ...]
```

**Output (2 chunks):**

```python
[
    Chunk(
        content="### Section 1: The Two Factors of a Commodity\n\nThe wealth of...",
        metadata={
            "source_url": "https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm",
            "title": "Capital Vol. I, Chapter 1: Commodities",
            "author": "Karl Marx",
            "chunk_headings": ["Section 1: The Two Factors of a Commodity"],
            "chunk_hierarchy": ["Capital Volume I", "Chapter 1: Commodities"],
            "section_count": 1,
            ...
        },
        chunk_id": "marx-capital-1867-ch01-s1",
        chunk_index=0
    ),
    Chunk(
        content="### Section 2: The Twofold Character of the Labour...",
        metadata={
            ...
            "chunk_headings": ["Section 2: The Twofold Character of the Labour Embodied in Commodities"],
            "chunk_hierarchy": ["Capital Volume I", "Chapter 1: Commodities"],
            ...
        },
        chunk_id="marx-capital-1867-ch01-s2",
        chunk_index=1
    )
]
```

---

## 3. Entry-Based Chunking (Glossary)

### 3.1 Overview

**Best for**: Glossary section (100% structured entries)

**Principle**: One chunk per encyclopedia entry (self-contained semantic unit).

**Why Important**: Glossary entries are **already optimally chunked** - each entry is a complete definition with cross-references. Splitting would break semantic coherence.

### 3.2 Implementation

```python
class EntryBasedChunker:
    """
    Chunk Glossary entries: one entry = one chunk.

    Glossary files contain multiple entries per HTML file (e.g., /glossary/people/m/a.htm
    contains Marx, Mao, Malatesta, etc.). Each entry is delimited by heading tags or
    anchor tags.
    """

    def chunk(self, markdown: str, metadata: DocumentMetadata) -> List[Chunk]:
        """
        Parse Glossary markdown into individual entry chunks.

        Algorithm:
        1. Identify entry boundaries (h3/h4 headings or anchor IDs)
        2. Extract entry name, definition, cross-references
        3. Create one chunk per entry with entry metadata
        """
        entries = self._parse_entries(markdown, metadata.glossary_type)
        chunks = []

        for idx, entry in enumerate(entries):
            chunk_metadata = {
                **metadata.to_dict(),
                "entry_name": entry.name,
                "entry_type": metadata.glossary_type,
                "entry_id": self._generate_entry_id(entry, metadata),
                "cross_references_in_entry": entry.cross_references,
            }

            chunks.append(Chunk(
                content=entry.definition,
                metadata=chunk_metadata,
                chunk_id=chunk_metadata["entry_id"],
                chunk_index=idx
            ))

        return chunks

    def _parse_entries(self, markdown: str, entry_type: str) -> List[GlossaryEntry]:
        """
        Parse Glossary entries based on type-specific structure.

        Entry detection patterns (from corpus analysis):
        - People: <h3> or <h4> with name, followed by dates in parentheses
        - Terms: <h4> with term name, followed by definition paragraphs
        - Organizations: <h4> with org name, followed by description
        - Events: <h4> with event name and date
        - Periodicals: <h4> with publication title
        - Places: <h4> with location name
        """
        import re

        entries = []
        lines = markdown.split('\n')
        current_entry_lines = []
        current_entry_name = None

        for line in lines:
            # Check for entry heading (h3 or h4)
            heading_match = re.match(r'^(#{3,4})\s+(.+)$', line)

            if heading_match:
                # Save previous entry
                if current_entry_name and current_entry_lines:
                    entries.append(self._create_entry(
                        current_entry_name,
                        '\n'.join(current_entry_lines),
                        entry_type
                    ))

                # Start new entry
                current_entry_name = heading_match.group(2)
                current_entry_lines = [line]
            else:
                if current_entry_name:  # Only add if we're in an entry
                    current_entry_lines.append(line)

        # Save final entry
        if current_entry_name and current_entry_lines:
            entries.append(self._create_entry(
                current_entry_name,
                '\n'.join(current_entry_lines),
                entry_type
            ))

        return entries

    def _create_entry(self, name: str, definition: str, entry_type: str) -> GlossaryEntry:
        """
        Create GlossaryEntry with cross-reference extraction.
        """
        cross_refs = self._extract_cross_references(definition)

        return GlossaryEntry(
            name=name,
            definition=definition,
            entry_type=entry_type,
            cross_references=cross_refs
        )

    def _extract_cross_references(self, definition: str) -> List[str]:
        """
        Extract cross-reference links from entry definition.

        Pattern: [Text](URL) where URL is internal MIA link
        """
        import re
        # Match markdown links: [Text](URL)
        pattern = r'\[([^\]]+)\]\((/(?:glossary|archive|subject|reference)[^\)]+)\)'
        matches = re.findall(pattern, definition)
        return [url for text, url in matches]

@dataclass
class GlossaryEntry:
    """Represents a single Glossary encyclopedia entry."""
    name: str
    definition: str
    entry_type: str  # "people", "terms", "orgs", "events", "periodicals", "places"
    cross_references: List[str]
```

### 3.3 Example Output

**Input (Glossary people/m/a.htm):**

```markdown
### Karl Marx (1818-1883)

Born in Trier, Germany, to a Jewish family. Studied law and philosophy at the
Universities of Bonn and Berlin. Together with [Friedrich Engels](/glossary/people/e/n.htm#engels-friedrich),
developed the theory of [historical materialism](/glossary/terms/h/i.htm#historical-materialism).
Major works include [Capital](/archive/marx/works/1867-c1/) and the
[Communist Manifesto](/archive/marx/works/1848/communist-manifesto/).

### Mao Zedong (1893-1976)

Chinese revolutionary and political theorist. Founder of the People's Republic of China.
Developed [Maoism](/glossary/terms/m/a.htm#maoism) as an adaptation of [Marxism-Leninism](/glossary/terms/m/a.htm#marxism-leninism)
to Chinese conditions.
```

**Output (2 chunks):**

```python
[
    Chunk(
        content="### Karl Marx (1818-1883)\n\nBorn in Trier, Germany...",
        metadata={
            "source_url": "https://www.marxists.org/glossary/people/m/a.htm#marx-karl",
            "title": "Karl Marx",
            "entry_name": "Karl Marx (1818-1883)",
            "entry_type": "people",
            "entry_id": "people/m/a/marx-karl",
            "cross_references_in_entry": [
                "/glossary/people/e/n.htm#engels-friedrich",
                "/glossary/terms/h/i.htm#historical-materialism",
                "/archive/marx/works/1867-c1/",
                "/archive/marx/works/1848/communist-manifesto/"
            ],
            "section_type": "glossary",
            "glossary_type": "people",
            ...
        },
        chunk_id="people/m/a/marx-karl",
        chunk_index=0
    ),
    Chunk(
        content="### Mao Zedong (1893-1976)\n\nChinese revolutionary...",
        metadata={
            "entry_name": "Mao Zedong (1893-1976)",
            "entry_id": "people/m/a/mao-zedong",
            "cross_references_in_entry": [
                "/glossary/terms/m/a.htm#maoism",
                "/glossary/terms/m/a.htm#marxism-leninism"
            ],
            ...
        },
        chunk_id="people/m/a/mao-zedong",
        chunk_index=1
    )
]
```

---

## 4. Paragraph Cluster Chunking (Heading-less Documents)

### 4.1 Overview

**Best for**: History/Other section (40% have NO headings)

**Principle**: Group paragraphs into clusters targeting 512-1024 tokens when no heading structure exists.

**Why Important**: 40% of History/Other documents have `heading_depth == 0`, requiring paragraph-based fallback.

### 4.2 Implementation

```python
class ParagraphClusterChunker:
    """
    Chunk by grouping paragraphs when no heading structure exists.
    """

    TARGET_MIN_TOKENS = 512
    TARGET_MAX_TOKENS = 1024

    def chunk(self, markdown: str, metadata: DocumentMetadata) -> List[Chunk]:
        """
        Group paragraphs into chunks of 512-1024 tokens.

        Algorithm:
        1. Split into paragraphs
        2. Accumulate paragraphs until target token count
        3. Create chunk, continue accumulation
        """
        paragraphs = self._split_paragraphs(markdown)
        chunks = []
        current_chunk_paragraphs = []
        current_token_count = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            # Case 1: Single paragraph exceeds max - chunk alone
            if para_tokens > self.TARGET_MAX_TOKENS:
                # Flush current chunk first
                if current_chunk_paragraphs:
                    chunks.append(self._create_chunk(current_chunk_paragraphs, metadata))
                    current_chunk_paragraphs = []
                    current_token_count = 0

                # Split long paragraph by sentences
                split_paras = self._split_long_paragraph(para, self.TARGET_MAX_TOKENS)
                for split_para in split_paras:
                    chunks.append(self._create_chunk([split_para], metadata))

                continue

            # Case 2: Adding paragraph would exceed max
            if current_token_count + para_tokens > self.TARGET_MAX_TOKENS:
                # Flush current chunk
                if current_chunk_paragraphs:
                    chunks.append(self._create_chunk(current_chunk_paragraphs, metadata))
                current_chunk_paragraphs = [para]
                current_token_count = para_tokens
            else:
                # Add to current chunk
                current_chunk_paragraphs.append(para)
                current_token_count += para_tokens

        # Flush remaining chunk
        if current_chunk_paragraphs:
            chunks.append(self._create_chunk(current_chunk_paragraphs, metadata))

        return chunks

    def _split_paragraphs(self, markdown: str) -> List[str]:
        """Split markdown into paragraphs (double newline delimiter)."""
        paragraphs = markdown.split('\n\n')
        # Filter empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_long_paragraph(self, paragraph: str, max_tokens: int) -> List[str]:
        """
        Split long paragraph by sentences to fit max_tokens.

        Fallback to character splitting if sentences are too long.
        """
        import re

        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        chunks = []
        current_chunk_sentences = []
        current_token_count = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            if current_token_count + sentence_tokens > max_tokens:
                if current_chunk_sentences:
                    chunks.append(' '.join(current_chunk_sentences))
                current_chunk_sentences = [sentence]
                current_token_count = sentence_tokens
            else:
                current_chunk_sentences.append(sentence)
                current_token_count += sentence_tokens

        if current_chunk_sentences:
            chunks.append(' '.join(current_chunk_sentences))

        return chunks

    def _create_chunk(self, paragraphs: List[str], metadata: DocumentMetadata) -> Chunk:
        """Create chunk from paragraph cluster."""
        content = '\n\n'.join(paragraphs)

        chunk_metadata = {
            **metadata.to_dict(),
            "chunk_paragraph_count": len(paragraphs),
            "chunking_strategy": "paragraph_clusters",
        }

        return Chunk(
            content=content,
            metadata=chunk_metadata,
            chunk_id=self._generate_chunk_id(metadata, paragraphs),
            chunk_index=len(self.chunks_created)
        )
```

---

## 5. Token-Based Fallback Chunking

### 5.1 Overview

**Best for**: Edge cases, malformed documents, last resort

**Principle**: Fixed token count chunking with overlapping windows.

**Use When**: All structured chunking strategies fail.

### 5.2 Implementation

```python
class TokenBasedChunker:
    """
    Fixed token-count chunking with overlapping windows (last resort).
    """

    CHUNK_SIZE = 512
    OVERLAP = 50  # 10% overlap to preserve context across boundaries

    def chunk(self, markdown: str, metadata: DocumentMetadata) -> List[Chunk]:
        """
        Chunk by fixed token count with overlap.

        Algorithm:
        1. Tokenize content
        2. Create sliding windows of CHUNK_SIZE tokens
        3. Overlap by OVERLAP tokens
        """
        tokens = self._tokenize(markdown)
        chunks = []

        start_idx = 0
        while start_idx < len(tokens):
            end_idx = min(start_idx + self.CHUNK_SIZE, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]

            # Convert tokens back to text
            chunk_text = self._detokenize(chunk_tokens)

            chunk_metadata = {
                **metadata.to_dict(),
                "chunking_strategy": "token_based_fallback",
                "token_start": start_idx,
                "token_end": end_idx,
            }

            chunks.append(Chunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=f"{metadata.content_hash}-tok-{start_idx}",
                chunk_index=len(chunks)
            ))

            # Move to next chunk with overlap
            start_idx += (self.CHUNK_SIZE - self.OVERLAP)

        return chunks

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text (whitespace splitting for simplicity).

        For production, use: tiktoken (OpenAI) or transformers tokenizer
        """
        return text.split()

    def _detokenize(self, tokens: List[str]) -> str:
        """Reconstruct text from tokens."""
        return ' '.join(tokens)
```

---

## 6. Edge Case Handling

### 6.1 Index Pages (Subject Section)

**Problem**: 55% of Subject section are navigation indexes (file lists, tables of contents)

**Solution**: Skip chunking for low-priority index pages

```python
def handle_index_pages(metadata: DocumentMetadata, markdown: str) -> Optional[List[Chunk]]:
    """
    Detect and skip index pages.

    Indicators (from corpus analysis):
    - file_size < 10KB
    - metadata.rag_priority == "low"
    - High link density (> 20 links, < 500 words)
    - Title contains "Index", "Contents", "Works of"
    """
    if metadata.rag_priority == "low":
        return None  # Skip entirely

    # Additional heuristic: link density
    link_count = markdown.count('[](')
    word_count = len(markdown.split())

    if link_count > 20 and word_count < 500:
        # High link density, minimal content - likely index
        return None

    # Proceed with normal chunking
    return None  # Signal to continue with strategy selection
```

### 6.2 Multi-Article Files (ETOL Newspapers)

**Problem**: Some ETOL newspaper issues contain multiple short articles in one HTML file

**Solution**: Split at article boundaries (detected by repeating heading patterns)

```python
def detect_multi_article_file(markdown: str) -> bool:
    """
    Detect if file contains multiple short articles.

    Indicators:
    - Multiple h3 headings at same level (not nested)
    - Sections are short (< 200 tokens each)
    - Pattern: h3 → paragraphs → h3 → paragraphs (flat structure)
    """
    import re

    h3_headings = re.findall(r'^### (.+)$', markdown, re.MULTILINE)

    if len(h3_headings) >= 3:  # Multiple h3 headings
        # Check if sections are short
        sections = markdown.split('###')
        avg_section_length = sum(len(s.split()) for s in sections) / len(sections)

        if avg_section_length < 200:  # Short sections
            return True

    return False
```

### 6.3 Long Paragraphs (Archive, History)

**Problem**: Some theoretical texts have 500-1000 word paragraphs (esp. Marx, Hegel)

**Solution**: Split at sentence boundaries when paragraphs exceed threshold

```python
LONG_PARAGRAPH_THRESHOLD = 1024  # tokens

def handle_long_paragraph(paragraph: str, max_tokens: int = LONG_PARAGRAPH_THRESHOLD) -> List[str]:
    """
    Split long paragraphs at sentence boundaries.

    Used as fallback within SemanticBreakChunker and ParagraphClusterChunker.
    """
    # Implementation shown in ParagraphClusterChunker._split_long_paragraph()
    pass
```

---

## 7. Metadata Enrichment for Chunks

### 7.1 Chunk Metadata Schema

**Each chunk inherits all document metadata PLUS chunk-specific fields:**

```python
chunk_metadata = {
    # ===== INHERITED FROM DOCUMENT =====
    "source_url": str,
    "title": str,
    "author": str,
    "date_written": str,
    "section_type": str,
    # ... (all DocumentMetadata fields)

    # ===== CHUNK-SPECIFIC =====
    "chunk_id": str,              # Unique chunk identifier
    "chunk_index": int,           # Position in document (0-indexed)
    "chunk_headings": List[str],  # Headings within this chunk
    "chunk_hierarchy": List[str], # Parent headings (context)
    "chunking_strategy": str,     # "semantic_breaks", "entry_based", "paragraph_clusters", "token_based"

    # Optional (strategy-dependent)
    "section_count": int,         # Number of sections merged (semantic breaks)
    "chunk_paragraph_count": int, # Number of paragraphs (paragraph clusters)
    "entry_name": str,            # Glossary entry name
    "token_start": int,           # Start token index (token-based)
    "token_end": int,             # End token index (token-based)
}
```

### 7.2 Chunk ID Generation

```python
def generate_chunk_id(metadata: DocumentMetadata, chunk_index: int, chunk_content: str) -> str:
    """
    Generate deterministic chunk ID.

    Format: {author-slug}-{work-slug}-{section-identifier}

    Examples:
        - "marx-capital-1867-ch01-s1" (Archive, semantic breaks)
        - "people-marx-karl" (Glossary, entry-based)
        - "cannon-theses-1946-p3" (Paragraph clusters)
        - "a1b2c3d4e5f6-tok-512" (Token-based fallback)
    """
    # Glossary: Use entry ID
    if metadata.section_type == "glossary" and metadata.entry_id:
        return metadata.entry_id

    # Archive/ETOL: Use author + work + section
    if metadata.section_type in ["archive", "history/etol", "reference"]:
        author_slug = slugify(metadata.author or "unknown")
        work_slug = extract_work_slug(metadata.source_url)
        return f"{author_slug}-{work_slug}-{chunk_index}"

    # Fallback: content hash + index
    return f"{metadata.content_hash}-{chunk_index}"
```

---

## 8. Testing & Validation

### 8.1 Unit Tests

```python
# Test semantic break chunking
def test_semantic_break_chunking_archive():
    """Test Archive section with good heading hierarchy."""
    chunker = SemanticBreakChunker("archive")
    markdown = load_fixture("marx_capital_ch01.md")
    metadata = create_test_metadata(section_type="archive", heading_depth=4)

    chunks = chunker.chunk(markdown, metadata)

    assert len(chunks) == 8  # Ch01 has 8 sections
    assert all(512 <= count_tokens(c.content) <= 1024 for c in chunks)
    assert chunks[0].metadata["chunk_headings"] == ["Section 1: The Two Factors of a Commodity"]

# Test entry-based chunking
def test_entry_based_chunking_glossary():
    """Test Glossary entry chunking."""
    chunker = EntryBasedChunker()
    markdown = load_fixture("glossary_people_m_a.md")
    metadata = create_test_metadata(section_type="glossary", glossary_type="people")

    chunks = chunker.chunk(markdown, metadata)

    # File contains Marx, Mao, Malatesta, etc.
    assert len(chunks) >= 3
    assert chunks[0].metadata["entry_name"] == "Karl Marx (1818-1883)"
    assert "Friedrich Engels" in chunks[0].content  # Cross-reference

# Test paragraph clustering
def test_paragraph_cluster_chunking_headingless():
    """Test heading-less documents (History/Other)."""
    chunker = ParagraphClusterChunker()
    markdown = load_fixture("history_other_usa_headingless.md")
    metadata = create_test_metadata(section_type="history/other", heading_depth=0)

    chunks = chunker.chunk(markdown, metadata)

    assert all(512 <= count_tokens(c.content) <= 1024 for c in chunks)
    assert chunks[0].metadata["chunking_strategy"] == "paragraph_clusters"
```

### 8.2 Integration Tests

```python
def test_chunking_strategy_selection():
    """Test that correct strategy is selected based on document characteristics."""

    # Test Archive with good hierarchy → semantic breaks
    metadata_archive = create_metadata(section_type="archive", heading_depth=4)
    strategy = select_chunking_strategy(metadata_archive, "...")
    assert strategy == ChunkingStrategy.SEMANTIC_BREAKS

    # Test History/Other with no headings → paragraph clusters
    metadata_headingless = create_metadata(section_type="history/other", heading_depth=0)
    strategy = select_chunking_strategy(metadata_headingless, "...")
    assert strategy == ChunkingStrategy.PARAGRAPH_CLUSTERS

    # Test Glossary → entry-based
    metadata_glossary = create_metadata(section_type="glossary")
    strategy = select_chunking_strategy(metadata_glossary, "...")
    assert strategy == ChunkingStrategy.ENTRY_BASED

    # Test Subject index page → skip
    metadata_index = create_metadata(section_type="subject", rag_priority="low")
    strategy = select_chunking_strategy(metadata_index, "...")
    assert strategy == ChunkingStrategy.SKIP
```

### 8.3 Quality Metrics

**Chunking Quality Metrics (to track):**

```python
@dataclass
class ChunkingQualityMetrics:
    """Track chunking quality across corpus."""

    # Token distribution
    avg_tokens_per_chunk: float
    min_tokens: int
    max_tokens: int
    std_dev_tokens: float

    # Strategy distribution
    semantic_breaks_pct: float  # Target: 70% (Archive + ETOL + Reference)
    entry_based_pct: float      # Target: ~5% (Glossary)
    paragraph_clusters_pct: float  # Target: 20% (History/Other)
    token_based_pct: float      # Target: <5% (fallback only)
    skipped_pct: float          # Target: ~10% (Subject indexes)

    # Semantic coherence
    chunks_with_headings_pct: float  # Target: >70%
    avg_sections_per_chunk: float    # Target: 1-3
    cross_section_splits_pct: float  # Target: <5% (chunks that span sections)
```

**Target Metrics (from corpus analysis):**

| Metric | Target | Rationale |
|--------|--------|-----------|
| Avg tokens/chunk | 650-750 | Optimal for embedding models (512-1024 range) |
| Chunks with headings | >70% | Semantic preservation (Archive/ETOL/Reference have good hierarchies) |
| Token-based fallback | <5% | Most docs have structure, fallback rare |
| Skipped chunks | ~10% | Subject section indexes |

---

## 9. Implementation Checklist

- [ ] Implement `ChunkingStrategy` enum and selection logic
- [ ] Implement `SemanticBreakChunker` for Archive/ETOL/Reference
- [ ] Implement `EntryBasedChunker` for Glossary
- [ ] Implement `ParagraphClusterChunker` for History/Other
- [ ] Implement `TokenBasedChunker` as fallback
- [ ] Add edge case handlers (index pages, multi-article files, long paragraphs)
- [ ] Implement chunk metadata enrichment
- [ ] Implement chunk ID generation
- [ ] Write unit tests for each strategy
- [ ] Write integration tests for strategy selection
- [ ] Implement quality metrics tracking
- [ ] Validate on 100-doc sample from each section
- [ ] Performance benchmark (target: 1000 docs/minute)

---

## 10. Usage Example

```python
from src.ingestion.chunking import ChunkingPipeline
from src.processing.metadata import DocumentMetadata

# Initialize chunking pipeline
pipeline = ChunkingPipeline()

# Process a document
markdown_content = load_processed_markdown("marx_capital_ch01.md")
metadata = DocumentMetadata(
    source_url="https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm",
    title="Capital Vol. I, Chapter 1: Commodities",
    author="Karl Marx",
    section_type="archive",
    document_structure={"heading_depth": 4, "section_count": 8},
    # ... other fields
)

# Chunk with automatic strategy selection
chunks = pipeline.chunk(markdown_content, metadata)

print(f"Created {len(chunks)} chunks using {chunks[0].metadata['chunking_strategy']}")
# Output: "Created 8 chunks using semantic_breaks"

# Inspect chunks
for chunk in chunks[:2]:
    print(f"\nChunk {chunk.chunk_index}: {chunk.chunk_id}")
    print(f"Headings: {chunk.metadata['chunk_headings']}")
    print(f"Tokens: ~{count_tokens(chunk.content)}")
    print(f"Preview: {chunk.content[:200]}...")
```

---

## 11. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-08 | Initial specification based on corpus analysis Phase 3 findings |

---

**Status**: Ready for implementation by parallel AI agents
**Priority**: HIGH (blocking for RAG ingestion pipeline)
**Estimated Implementation Time**: 1-2 weeks
