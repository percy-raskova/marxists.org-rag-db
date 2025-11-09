---
title: "Refactoring: Implement Glossary Entity Linker for Canonical Name Normalization"
labels: refactoring, metadata, knowledge-graph, instance1
assignees: ""
---

## Problem Statement

The current metadata extraction has **no entity linking capability**, resulting in:
- **Author name variations**: "Karl Marx" vs. "Marx, Karl" vs. "K. Marx" are treated as different entities
- **No canonical IDs**: Can't reliably link documents to canonical author entities
- **Cross-reference loss**: ~5,000-10,000 Glossary cross-reference edges unused
- **Knowledge graph gaps**: Missing entity relationships for advanced queries
- **Disambiguation failures**: Common names (e.g., "Smith") can't be resolved to specific people

**Glossary Section Findings** (from `docs/corpus-analysis/04-glossary-metadata-analysis.md`):
- **~2,500 entities** with canonical structure (name, years, description)
- **Cross-reference network**: 5,000-10,000 edges connecting related entities
- **Entry types**: People (80%), organizations (15%), concepts/terms (5%)
- **100% structured content**: Reliable for entity index building

**Example Entity Linking Need**:
```
Extracted: "Marx" (from ETOL title)
→ Link to: "Marx, Karl (1818-1883)" [canonical ID: marx-karl-1818]
→ Cross-references: Engels, Communist Manifesto, Capital
```

## Current Implementation

```python
# Current: No entity linking at all
metadata.authorship.authors = ["Marx"]  # Raw extracted string
metadata.authorship.canonical_author_ids = []  # Always empty
metadata.semantic.glossary_entities = []  # Never populated
metadata.semantic.cross_references = []  # Never populated
```

**Issues:**
- No Glossary index built from MIA Glossary section
- No fuzzy matching to handle name variations
- No canonical ID assignment
- No cross-reference extraction
- No disambiguation logic for common names

## Proposed Solution

Implement **Glossary Entity Linker** with **Index + Fuzzy Matching**:

### Architecture

```python
# 1. Glossary Entity Index Entry
@dataclass
class GlossaryEntity:
    """Canonical entity from MIA Glossary"""
    canonical_id: str  # e.g., "marx-karl-1818"
    canonical_name: str  # e.g., "Marx, Karl"
    birth_year: Optional[int]
    death_year: Optional[int]
    years_active: Optional[str]  # e.g., "1818-1883"
    entity_type: Literal['person', 'organization', 'concept']
    description: Optional[str]
    aliases: List[str]  # Name variations: ["Karl Marx", "K. Marx", "Marx, K."]
    cross_references: List[str]  # Linked entity IDs
    source_url: str  # Glossary page URL

# 2. Entity Index
class GlossaryIndex:
    """In-memory index of ~2,500 Glossary entities"""

    def __init__(self):
        self.entities: Dict[str, GlossaryEntity] = {}  # canonical_id → entity
        self.name_index: Dict[str, str] = {}  # normalized_name → canonical_id
        self.alias_index: Dict[str, List[str]] = {}  # alias → [canonical_ids]

    def load_from_directory(self, glossary_dir: Path) -> None:
        """Parse Glossary HTML files to build entity index"""
        for html_file in glossary_dir.glob('**/*.htm*'):
            entity = self._parse_glossary_entry(html_file)
            if entity:
                self.add_entity(entity)

    def _parse_glossary_entry(self, html_file: Path) -> Optional[GlossaryEntity]:
        """Extract entity data from Glossary HTML structure"""
        soup = BeautifulSoup(html_file.read_text(), 'lxml')

        # Glossary structure (from corpus analysis):
        # <h1>Marx, Karl (1818-1883)</h1>
        # <p>Description of Marx...</p>
        # <p><b>See also:</b> <a href="engels.htm">Engels</a>, <a href="...">Communist Manifesto</a></p>

        h1 = soup.find('h1')
        if not h1:
            return None

        # Parse: "Marx, Karl (1818-1883)"
        match = re.match(r'^(.+?)\s*\((\d{4})?-?(\d{4})?\)', h1.text)
        if match:
            canonical_name = match.group(1).strip()
            birth_year = int(match.group(2)) if match.group(2) else None
            death_year = int(match.group(3)) if match.group(3) else None
        else:
            canonical_name = h1.text.strip()
            birth_year, death_year = None, None

        # Generate canonical ID: "marx-karl-1818"
        canonical_id = self._generate_canonical_id(canonical_name, birth_year)

        # Extract description
        description = soup.find('p')
        description_text = description.text if description else None

        # Extract cross-references
        see_also = soup.find('b', string=re.compile(r'See also:', re.I))
        cross_references = []
        if see_also:
            for link in see_also.parent.find_all('a'):
                ref_id = Path(link['href']).stem
                cross_references.append(ref_id)

        # Generate aliases: "Karl Marx", "K. Marx", etc.
        aliases = self._generate_aliases(canonical_name)

        return GlossaryEntity(
            canonical_id=canonical_id,
            canonical_name=canonical_name,
            birth_year=birth_year,
            death_year=death_year,
            years_active=f"{birth_year}-{death_year}" if birth_year and death_year else None,
            entity_type='person',  # Detect from context/keywords
            description=description_text,
            aliases=aliases,
            cross_references=cross_references,
            source_url=f"https://marxists.org/glossary/{html_file.name}"
        )

    def _generate_canonical_id(self, name: str, birth_year: Optional[int]) -> str:
        """Generate canonical ID: 'marx-karl-1818'"""
        # Normalize: "Marx, Karl" → "marx-karl"
        normalized = name.lower().replace(',', '').replace(' ', '-')
        if birth_year:
            normalized += f"-{birth_year}"
        return normalized

    def _generate_aliases(self, canonical_name: str) -> List[str]:
        """Generate name variations for matching"""
        # "Marx, Karl" → ["Karl Marx", "K. Marx", "Marx, K.", "Marx"]
        aliases = []

        if ',' in canonical_name:
            last, first = canonical_name.split(',', 1)
            last = last.strip()
            first = first.strip()

            aliases.append(f"{first} {last}")  # "Karl Marx"
            aliases.append(f"{first[0]}. {last}")  # "K. Marx"
            aliases.append(f"{last}, {first[0]}.")  # "Marx, K."
            aliases.append(last)  # "Marx"

        aliases.append(canonical_name)  # Original form
        return list(set(aliases))  # Deduplicate

    def add_entity(self, entity: GlossaryEntity) -> None:
        """Add entity to index with aliases"""
        self.entities[entity.canonical_id] = entity
        self.name_index[self._normalize_name(entity.canonical_name)] = entity.canonical_id

        for alias in entity.aliases:
            normalized_alias = self._normalize_name(alias)
            if normalized_alias not in self.alias_index:
                self.alias_index[normalized_alias] = []
            self.alias_index[normalized_alias].append(entity.canonical_id)

    def _normalize_name(self, name: str) -> str:
        """Normalize name for matching: lowercase, no punctuation"""
        return name.lower().replace(',', '').replace('.', '').replace('-', ' ').strip()

    def save_to_cache(self, cache_path: Path) -> None:
        """Serialize index to JSON/Parquet for fast loading"""
        cache_data = {
            'entities': {k: asdict(v) for k, v in self.entities.items()},
            'name_index': self.name_index,
            'alias_index': self.alias_index,
        }
        cache_path.write_text(json.dumps(cache_data, indent=2))

    @classmethod
    def load_from_cache(cls, cache_path: Path) -> 'GlossaryIndex':
        """Load pre-built index from cache"""
        cache_data = json.loads(cache_path.read_text())
        index = cls()
        index.entities = {k: GlossaryEntity(**v) for k, v in cache_data['entities'].items()}
        index.name_index = cache_data['name_index']
        index.alias_index = cache_data['alias_index']
        return index

# 3. Entity Linker
class EntityLinker:
    """Link extracted author names to canonical Glossary entities"""

    def __init__(self, glossary_index: GlossaryIndex, fuzzy_threshold: float = 0.85):
        self.index = glossary_index
        self.fuzzy_threshold = fuzzy_threshold

    def link_author(self, author_name: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Link author name to canonical entity ID.

        Args:
            author_name: Extracted author name (e.g., "Marx", "Karl Marx")
            context: Optional context for disambiguation (e.g., birth_year, work_title)

        Returns:
            Canonical entity ID (e.g., "marx-karl-1818") or None
        """
        # 1. Exact match on normalized name
        normalized = self.index._normalize_name(author_name)
        if normalized in self.index.name_index:
            return self.index.name_index[normalized]

        # 2. Exact match on aliases
        if normalized in self.index.alias_index:
            candidates = self.index.alias_index[normalized]
            if len(candidates) == 1:
                return candidates[0]
            else:
                # Multiple matches - use context for disambiguation
                return self._disambiguate(candidates, context)

        # 3. Fuzzy match (handle typos, variations)
        best_match = self._fuzzy_match(author_name)
        if best_match:
            return best_match

        # 4. No match found
        return None

    def _fuzzy_match(self, author_name: str) -> Optional[str]:
        """Fuzzy string matching using Levenshtein distance"""
        from Levenshtein import ratio  # Optional dependency

        normalized = self.index._normalize_name(author_name)
        best_score = 0.0
        best_id = None

        for indexed_name, canonical_id in self.index.name_index.items():
            score = ratio(normalized, indexed_name)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_id = canonical_id

        return best_id

    def _disambiguate(self, candidate_ids: List[str], context: Optional[Dict]) -> str:
        """Disambiguate between multiple matching entities using context"""
        if not context:
            # No context - return first candidate (or most common)
            return candidate_ids[0]

        # Use birth year for disambiguation if available
        if 'birth_year' in context:
            for candidate_id in candidate_ids:
                entity = self.index.entities[candidate_id]
                if entity.birth_year == context['birth_year']:
                    return candidate_id

        # Use work title for disambiguation
        if 'work_title' in context:
            # Check if work title appears in entity description or cross-references
            # ... (implementation details)

        # Fallback: return first candidate
        return candidate_ids[0]

    def get_cross_references(self, canonical_id: str) -> List[GlossaryEntity]:
        """Get cross-referenced entities for knowledge graph"""
        entity = self.index.entities.get(canonical_id)
        if not entity:
            return []

        cross_refs = []
        for ref_id in entity.cross_references:
            if ref_id in self.index.entities:
                cross_refs.append(self.index.entities[ref_id])
        return cross_refs

# 4. Integration with Metadata Extraction
def enrich_metadata_with_entities(
    metadata: DocumentMetadata,
    linker: EntityLinker
) -> DocumentMetadata:
    """Link extracted authors to canonical entities and add cross-references"""

    # Link authors to canonical IDs
    canonical_ids = []
    for author in metadata.authorship.authors:
        context = {
            'birth_year': None,  # Extract from date if available
            'work_title': metadata.core.title,
        }
        canonical_id = linker.link_author(author, context)
        if canonical_id:
            canonical_ids.append(canonical_id)

    metadata.authorship.canonical_author_ids = canonical_ids

    # Extract cross-references for knowledge graph
    cross_refs = []
    for canonical_id in canonical_ids:
        refs = linker.get_cross_references(canonical_id)
        cross_refs.extend([ref.canonical_id for ref in refs])

    metadata.semantic.glossary_entities = canonical_ids
    metadata.semantic.cross_references = cross_refs

    return metadata
```

### Implementation Steps

1. **Create Glossary index builder** (`mia_processor/glossary/index_builder.py`)
   - `GlossaryEntity` dataclass
   - `GlossaryIndex` class
   - HTML parsing for ~2,500 Glossary entries
   - Alias generation logic
   - Index caching (JSON/Parquet format)

2. **Create entity linker** (`mia_processor/glossary/entity_linker.py`)
   - `EntityLinker` class
   - Exact matching (normalized names, aliases)
   - Fuzzy matching (Levenshtein distance, optional)
   - Disambiguation logic (context-based)

3. **Create cross-reference extractor** (`mia_processor/glossary/cross_referencer.py`)
   - Parse "See also:" sections
   - Build cross-reference graph (5,000-10,000 edges)
   - Export to NetworkX/graph format for analysis

4. **Integrate with metadata pipeline** (`mia_processor.py`)
   - Build Glossary index once at startup (or load from cache)
   - Link authors after extraction pipeline
   - Populate `canonical_author_ids` and `glossary_entities` fields
   - Add cross-references to `semantic.cross_references`

5. **Create validation tests** (`tests/unit/test_glossary_linker.py`)
   - Index building tests (parse sample Glossary entries)
   - Exact matching tests ("Karl Marx" → "marx-karl-1818")
   - Alias matching tests ("Marx" → "marx-karl-1818")
   - Fuzzy matching tests ("Carl Marx" → "marx-karl-1818")
   - Disambiguation tests (multiple matches)
   - Cross-reference extraction tests

6. **Generate entity linking report** (`scripts/generate_entity_report.py`)
   - Linking coverage: % of authors successfully linked
   - Linking confidence: average fuzzy match scores
   - Unlinked authors: entities not in Glossary
   - Cross-reference network metrics

## Acceptance Criteria

- [ ] Glossary index built from ~2,500 Glossary HTML files
- [ ] Index contains canonical IDs, names, years, descriptions, aliases
- [ ] 5,000-10,000 cross-reference edges extracted
- [ ] Index cached to JSON/Parquet for fast loading (<1s)
- [ ] Exact matching: 100% accuracy on canonical names and aliases
- [ ] Fuzzy matching: 90%+ accuracy on common variations (threshold 0.85)
- [ ] Disambiguation: Context-based resolution for common names
- [ ] Entity linking integrated with metadata extraction pipeline
- [ ] 90%+ of Archive authors successfully linked to canonical IDs
- [ ] Cross-references populated in metadata for knowledge graph
- [ ] Performance: <10ms per entity linking operation
- [ ] Linking report shows coverage metrics per section

## Files to Modify

**New Files:**
- `mia_processor/glossary/__init__.py` - Glossary module exports
- `mia_processor/glossary/index_builder.py` - `GlossaryEntity`, `GlossaryIndex`
- `mia_processor/glossary/entity_linker.py` - `EntityLinker` with fuzzy matching
- `mia_processor/glossary/cross_referencer.py` - Cross-reference extraction
- `mia_processor/glossary/entity_index.json` - Cached entity index (generated)
- `tests/unit/test_glossary_linker.py` - Entity linking tests
- `tests/fixtures/glossary_samples/` - Sample Glossary HTML files
- `scripts/generate_entity_report.py` - Entity linking coverage report

**Modified Files:**
- `mia_processor.py` - Integrate entity linking after author extraction

## Dependencies

**External Dependencies:**
- `python-Levenshtein` (optional) - Fuzzy string matching for name variations
- `networkx` (optional) - Cross-reference graph analysis
- BeautifulSoup - HTML parsing (already required)

**Internal Dependencies:**
- Unified Metadata Schema (#TBD) - Needs `canonical_author_ids`, `glossary_entities` fields
- Multi-Source Extraction Pipeline (#TBD) - Needs author extraction to link
- **Glossary section processing** - Must process Glossary first to build index

**Blocks:**
- Knowledge graph construction (needs cross-reference network)
- Advanced entity-based queries (needs canonical IDs)

## Related Issues

- Part of Code Refactoring Project (Stream 4: Metadata Pipeline)
- Blocked by: Unified Metadata Schema (#TBD)
- Blocked by: Multi-Source Extraction Pipeline (#TBD)
- Blocks: Knowledge graph construction (future)
- Related: Corpus Analysis - Glossary (✅ Complete - entity structure documented)

## Estimated Effort

**Time**: 10-14 hours
**Complexity**: Medium (HTML parsing, fuzzy matching, graph extraction)
**Priority**: HIGH (enables canonical entity linking and knowledge graph)

## Success Metrics

**Entity Index Quality**:
- ~2,500 entities indexed from Glossary
- 100% parse success rate on Glossary HTML
- 5-10 aliases per entity (average)
- 5,000-10,000 cross-reference edges extracted

**Entity Linking Coverage** (based on corpus analysis):
- **Archive**: 90%+ authors linked (canonical names in Glossary)
- **ETOL**: 70%+ authors linked (many non-Marxist authors not in Glossary)
- **EROL**: 85%+ organizations linked
- **Subject**: 60%+ authors linked (anthology compilations)
- **Overall**: 80%+ author linking success rate

**Linking Accuracy**:
- **Exact matches**: 100% precision (canonical names, aliases)
- **Fuzzy matches**: 90%+ precision (threshold 0.85)
- **False positives**: <5% (incorrect links)

**Performance**:
- Index loading: <1s from cache
- Entity linking: <10ms per author
- No significant performance regression

## Example Usage

```python
# 1. Build Glossary index (one-time setup)
index_builder = GlossaryIndex()
index_builder.load_from_directory(Path('/media/user/marxists.org/www.marxists.org/glossary/'))
index_builder.save_to_cache(Path('mia_processor/glossary/entity_index.json'))
print(f"Indexed {len(index_builder.entities)} entities")
# Output: Indexed 2,487 entities

# 2. Load index from cache (fast startup)
glossary_index = GlossaryIndex.load_from_cache(Path('mia_processor/glossary/entity_index.json'))

# 3. Create entity linker
linker = EntityLinker(glossary_index, fuzzy_threshold=0.85)

# 4. Link author names to canonical IDs
canonical_id = linker.link_author("Marx")
# Returns: "marx-karl-1818"

canonical_id = linker.link_author("Karl Marx")
# Returns: "marx-karl-1818" (exact alias match)

canonical_id = linker.link_author("Carl Marx")  # Typo
# Returns: "marx-karl-1818" (fuzzy match, 0.90 similarity)

# 5. Get cross-references for knowledge graph
cross_refs = linker.get_cross_references("marx-karl-1818")
# Returns: [
#   GlossaryEntity(canonical_id="engels-friedrich-1820", ...),
#   GlossaryEntity(canonical_id="communist-manifesto", ...),
#   GlossaryEntity(canonical_id="capital", ...),
# ]

# 6. Integrate with metadata extraction
metadata = extract_metadata_from_html(html_content, file_path)
metadata = enrich_metadata_with_entities(metadata, linker)

print(metadata.authorship.authors)
# Output: ["Karl Marx"]

print(metadata.authorship.canonical_author_ids)
# Output: ["marx-karl-1818"]

print(metadata.semantic.glossary_entities)
# Output: ["marx-karl-1818"]

print(metadata.semantic.cross_references)
# Output: ["engels-friedrich-1820", "communist-manifesto", "capital"]
```

## References

- Corpus Analysis (Glossary): `docs/corpus-analysis/04-glossary-metadata-analysis.md`
- Unified Schema: `docs/corpus-analysis/06-metadata-unified-schema.md`
- Glossary Location: `/media/user/marxists.org/www.marxists.org/glossary/`
- Refactoring Project: `planning/projects/refactoring-code-complexity.md`
- Design Pattern: Entity Linking with Fuzzy Matching
