# Knowledge Graph Specification

**Version:** 1.0
**Status:** IMPLEMENTATION-READY
**Module:** `src/knowledge_graph/`
**Dependencies:**
- Unified Metadata Schema (`docs/corpus-analysis/06-metadata-unified-schema.md`)
- Glossary Section Analysis (`docs/corpus-analysis/04-glossary-section-spec.md`)
- Subject Section Analysis (`docs/corpus-analysis/03-subject-section-spec.md`)
- Document Processing Spec (`specs/02-DOCUMENT-PROCESSING-SPEC.md`)

---

## Executive Summary

This specification defines the knowledge graph architecture for the Marxist Internet Archive RAG system, enabling **multi-hop queries**, **entity disambiguation**, and **contextual retrieval** across 55,753 documents. The knowledge graph is built on:

1. **Glossary as Entity Foundation**: ~2,500 canonical entities (people, terms, organizations, events, periodicals, places)
2. **Cross-Reference Network**: 5,000-10,000 edges extracted from document links
3. **Metadata Relationships**: Author-work, work-chapter, organization-member relationships
4. **Thematic Connections**: Subject categories linking to Archive/Reference works (64% Subject → Archive links)

**Key Objectives:**

- **Entity Disambiguation**: "Stalin" in Reference vs. "Stalin" in Archive (different doctrinal stances)
- **Contextual Retrieval**: Find works by Marx that Lenin referenced + contemporary critiques
- **Intellectual Genealogy**: Trace influence chains (Hegel → Marx → Lenin → Mao)
- **Thematic Exploration**: Discover all works on "dialectics" across sections
- **Temporal Queries**: Find works from "1900-1949" (peak revolutionary period) with specific themes

---

## 1. Graph Data Model

### 1.1 Node Types

**Primary Node Types** (6 entity types from Glossary):

```python
@dataclass
class NodeType(Enum):
    """Node types in knowledge graph."""
    PERSON = "person"          # 800-1,200 nodes (Glossary people)
    TERM = "term"              # 500-600 nodes (Glossary terms)
    ORGANIZATION = "org"       # 200-300 nodes (Glossary orgs)
    EVENT = "event"            # 150-250 nodes (Glossary events)
    PERIODICAL = "periodical"  # 150-200 nodes (Glossary periodicals)
    PLACE = "place"            # 50-75 nodes (Glossary places)

    # Document nodes
    WORK = "work"              # 55,753 nodes (all documents)
    CHUNK = "chunk"            # ~150,000 nodes (estimated 3 chunks/doc avg)

    # Organizational nodes
    SUBJECT_CATEGORY = "subject_category"  # 46 nodes (Subject taxonomy)
    WORK_COLLECTION = "work_collection"    # ~500 nodes (multi-volume works like Capital)
```

**Node Schema:**

```python
@dataclass
class KnowledgeGraphNode:
    """Represents a node in the knowledge graph."""

    node_id: str              # Unique identifier (e.g., "people/marx-karl", "work/marx-capital-1867-ch01")
    node_type: NodeType       # Entity type
    label: str                # Display name (e.g., "Karl Marx", "Capital Vol. I")

    # Properties (type-specific)
    properties: Dict[str, Any]  # Flexible property bag

    # Glossary entities
    # - canonical_name: str (normalized name)
    # - birth_year: Optional[str]
    # - death_year: Optional[str]
    # - definition: str (for terms)
    # - founding_date: Optional[str] (for orgs/periodicals)

    # Works
    # - source_url: str
    # - author: str
    # - date_written: Optional[str]
    # - section_type: str
    # - word_count: int
    # - rag_priority: str

    # Metadata for retrieval
    embedding_id: Optional[str]  # Link to vector DB (for works/chunks)
    aliases: List[str]           # Alternative names for entity linking
    cross_reference_count: int   # Connectivity measure
```

### 1.2 Edge Types

**Relationship Types:**

```python
@dataclass
class EdgeType(Enum):
    """Edge types representing relationships in knowledge graph."""

    # ===== AUTHORSHIP =====
    AUTHORED_BY = "authored_by"        # Work → Person (70k+ edges)
    MEMBER_OF = "member_of"            # Person → Organization
    EDITED_BY = "edited_by"            # Work → Person (anthologies)

    # ===== WORK STRUCTURE =====
    PART_OF = "part_of"                # Chapter → Work Collection (e.g., Capital Ch1 → Capital Vol I)
    HAS_CHUNK = "has_chunk"            # Work → Chunk (~150k edges)
    RESPONDS_TO = "responds_to"        # Work → Work (letters, critiques)

    # ===== CONCEPTUAL =====
    MENTIONS_PERSON = "mentions_person"       # Work → Person (entity linking)
    MENTIONS_TERM = "mentions_term"           # Work → Term
    MENTIONS_ORG = "mentions_org"             # Work → Organization
    DISCUSSES_EVENT = "discusses_event"       # Work → Event
    PUBLISHED_IN = "published_in"             # Work → Periodical

    # ===== CROSS-REFERENCES (from Glossary/Subject links) =====
    CROSS_REFERENCES = "cross_references"     # Any → Any (internal MIA links, 5k-10k edges)
    RELATED_TO = "related_to"                 # Glossary → Glossary (see also links)

    # ===== THEMATIC =====
    IN_CATEGORY = "in_category"               # Work → Subject Category (Subject section)
    ABOUT_TOPIC = "about_topic"               # Work → Term (inferred from keywords)

    # ===== TEMPORAL/SPATIAL =====
    OCCURRED_AT = "occurred_at"               # Event → Place
    LOCATED_IN = "located_in"                 # Organization → Place
    ACTIVE_DURING = "active_during"           # Person → Time Period (inferred from dates)

@dataclass
class KnowledgeGraphEdge:
    """Represents an edge in the knowledge graph."""

    edge_id: str              # Unique identifier
    edge_type: EdgeType       # Relationship type
    source_id: str            # Source node ID
    target_id: str            # Target node ID

    # Edge properties
    properties: Dict[str, Any]  # Flexible property bag
    # - confidence: float (0.0-1.0, for inferred edges)
    # - extraction_method: str ("explicit_link", "entity_mention", "metadata", "inferred")
    # - context: str (surrounding text for mentions)

    # Bidirectional flag (for symmetric relationships like "related_to")
    bidirectional: bool = False
```

---

## 2. Graph Construction Pipeline

### 2.1 Phase 1: Glossary Entity Ingestion (Foundation)

**Objective**: Load all ~2,500 Glossary entities as canonical nodes

**Process:**

```python
class GlossaryEntityLoader:
    """Load Glossary entities into knowledge graph."""

    def load_glossary_entities(self, glossary_dir: Path) -> Dict[str, KnowledgeGraphNode]:
        """
        Parse Glossary HTML files and create entity nodes.

        Returns:
            Dictionary of {entity_id: KnowledgeGraphNode}
        """
        entities = {}

        for glossary_type in ["people", "terms", "orgs", "events", "periodicals", "places"]:
            type_dir = glossary_dir / glossary_type
            entity_type = NodeType(glossary_type if glossary_type != "orgs" else "org")

            for html_file in type_dir.glob("**/*.htm"):
                # Parse entries from HTML
                entries = self._parse_glossary_entries(html_file, entity_type)

                for entry in entries:
                    node = KnowledgeGraphNode(
                        node_id=entry.entry_id,
                        node_type=entity_type,
                        label=entry.canonical_name,
                        properties=self._extract_entry_properties(entry, entity_type),
                        embedding_id=None,  # Glossary entries don't need embeddings (lookup only)
                        aliases=self._extract_aliases(entry),
                        cross_reference_count=len(entry.cross_references)
                    )

                    entities[node.node_id] = node

        return entities

    def _extract_entry_properties(self, entry: GlossaryEntry, entity_type: NodeType) -> Dict[str, Any]:
        """Extract type-specific properties from Glossary entry."""
        props = {
            "definition": entry.definition,
            "glossary_file": entry.source_file,
        }

        if entity_type == NodeType.PERSON:
            # Extract birth/death years from entry name (e.g., "Karl Marx (1818-1883)")
            if dates := self._extract_dates_from_name(entry.canonical_name):
                props["birth_year"] = dates.get("birth")
                props["death_year"] = dates.get("death")

        elif entity_type == NodeType.EVENT:
            # Extract event date from definition
            if event_date := self._extract_event_date(entry.definition):
                props["event_date"] = event_date

        elif entity_type == NodeType.ORGANIZATION:
            # Extract founding date
            if founding_date := self._extract_founding_date(entry.definition):
                props["founding_date"] = founding_date

        elif entity_type == NodeType.PERIODICAL:
            # Extract publication period
            if pub_period := self._extract_publication_period(entry.definition):
                props["publication_period"] = pub_period

        return props

    def _extract_aliases(self, entry: GlossaryEntry) -> List[str]:
        """
        Extract name aliases for entity matching.

        Examples:
            - "Leon Trotsky" → ["Trotsky", "L. Trotsky", "Lev Davidovich Bronstein"]
            - "Surplus Value" → ["surplus-value", "Mehrwert"]
        """
        aliases = []

        # Add surname only (for people)
        if entry.entity_type == NodeType.PERSON:
            # "Karl Marx" → "Marx"
            parts = entry.canonical_name.split()
            if len(parts) >= 2:
                aliases.append(parts[-1])  # Surname

        # Extract from definition (look for "also known as", "aka", parenthetical names)
        import re
        if also_known_as := re.search(r'\(also known as ([^)]+)\)', entry.definition):
            aliases.extend(also_known_as.group(1).split(','))

        return [a.strip() for a in aliases]
```

**Output**: ~2,500 entity nodes loaded as knowledge graph foundation

### 2.2 Phase 2: Work and Chunk Nodes

**Objective**: Create nodes for all documents and chunks

**Process:**

```python
class WorkNodeCreator:
    """Create work and chunk nodes from processed documents."""

    def create_work_nodes(self, metadata_dir: Path) -> Dict[str, KnowledgeGraphNode]:
        """
        Load DocumentMetadata JSON files and create work nodes.

        Returns:
            Dictionary of {work_id: KnowledgeGraphNode}
        """
        works = {}

        for metadata_file in metadata_dir.glob("**/*.json"):
            metadata = DocumentMetadata.from_json(metadata_file)

            # Create work node
            work_node = KnowledgeGraphNode(
                node_id=f"work/{metadata.content_hash}",
                node_type=NodeType.WORK,
                label=metadata.title,
                properties={
                    "source_url": metadata.source_url,
                    "author": metadata.author,
                    "date_written": metadata.date_written,
                    "section_type": metadata.section_type,
                    "word_count": metadata.word_count,
                    "keywords": metadata.keywords,
                    "rag_priority": metadata.rag_priority,
                    # ... all metadata fields
                },
                embedding_id=None,  # Works don't get embeddings (chunks do)
                aliases=[],
                cross_reference_count=len(metadata.cross_references)
            )

            works[work_node.node_id] = work_node

        return works

    def create_chunk_nodes(self, chunks_db: ChunksDatabase) -> Dict[str, KnowledgeGraphNode]:
        """
        Create chunk nodes from ingested chunks.

        Chunks are the embedded units, so they link to vector DB.
        """
        chunk_nodes = {}

        for chunk in chunks_db.get_all_chunks():
            chunk_node = KnowledgeGraphNode(
                node_id=chunk.chunk_id,
                node_type=NodeType.CHUNK,
                label=f"{chunk.metadata['title']} (chunk {chunk.chunk_index})",
                properties={
                    "chunk_index": chunk.chunk_index,
                    "chunk_headings": chunk.metadata.get("chunk_headings", []),
                    "token_count": chunk.metadata.get("token_count", 0),
                    **chunk.metadata  # Include all chunk metadata
                },
                embedding_id=chunk.chunk_id,  # Link to vector DB
                aliases=[],
                cross_reference_count=0
            )

            chunk_nodes[chunk_node.node_id] = chunk_node

        return chunk_nodes
```

**Output**: ~55,753 work nodes + ~150,000 chunk nodes

### 2.3 Phase 3: Explicit Relationship Extraction

**Objective**: Create edges from metadata and cross-references

**3.3.1 Authorship Edges:**

```python
def create_authorship_edges(works: Dict[str, KnowledgeGraphNode], entities: Dict[str, KnowledgeGraphNode]) -> List[KnowledgeGraphEdge]:
    """
    Create AUTHORED_BY edges: Work → Person

    Uses:
    - metadata.author (normalized to canonical Glossary name)
    - metadata.author_confidence
    """
    edges = []

    for work_id, work in works.items():
        author_name = work.properties.get("author")
        if not author_name:
            continue

        # Find canonical entity node
        author_entity = find_person_entity(author_name, entities)
        if not author_entity:
            # Author not in Glossary - create placeholder node
            author_entity = create_placeholder_author(author_name)
            entities[author_entity.node_id] = author_entity

        edge = KnowledgeGraphEdge(
            edge_id=f"{work_id}-authored-by-{author_entity.node_id}",
            edge_type=EdgeType.AUTHORED_BY,
            source_id=work_id,
            target_id=author_entity.node_id,
            properties={
                "confidence": work.properties.get("author_confidence", 0.5),
                "extraction_method": work.properties.get("author_source", "unknown")
            }
        )

        edges.append(edge)

    return edges
```

**Expected**: ~55,753 authorship edges (one per work, minus works without authors)

**3.3.2 Work Structure Edges:**

```python
def create_work_structure_edges(works: Dict[str, KnowledgeGraphNode]) -> List[KnowledgeGraphEdge]:
    """
    Create PART_OF edges: Chapter → Work Collection

    Uses:
    - metadata.work_collection (e.g., "Capital Volume I")
    - metadata.chapter_number
    """
    edges = []
    work_collections = {}  # Track collections to create nodes

    for work_id, work in works.items():
        collection_name = work.properties.get("work_collection")
        if not collection_name:
            continue

        # Create or get collection node
        collection_id = f"collection/{slugify(collection_name)}"
        if collection_id not in work_collections:
            work_collections[collection_id] = KnowledgeGraphNode(
                node_id=collection_id,
                node_type=NodeType.WORK_COLLECTION,
                label=collection_name,
                properties={"title": collection_name},
                embedding_id=None,
                aliases=[],
                cross_reference_count=0
            )

        # Create edge: chapter → collection
        edge = KnowledgeGraphEdge(
            edge_id=f"{work_id}-part-of-{collection_id}",
            edge_type=EdgeType.PART_OF,
            source_id=work_id,
            target_id=collection_id,
            properties={
                "chapter_number": work.properties.get("chapter_number"),
                "extraction_method": "metadata"
            }
        )

        edges.append(edge)

    return edges, work_collections
```

**Expected**: ~2,000 PART_OF edges (multi-volume works)

**3.3.3 Cross-Reference Edges:**

```python
def create_cross_reference_edges(works: Dict[str, KnowledgeGraphNode], entities: Dict[str, KnowledgeGraphNode]) -> List[KnowledgeGraphEdge]:
    """
    Create CROSS_REFERENCES edges from internal MIA links.

    Uses:
    - metadata.cross_references (list of source URLs)

    Returns edges like:
    - Work → Work (Archive work citing another work)
    - Work → Glossary Entity (work referencing term definition)
    - Glossary → Work (glossary entry linking to example work)
    """
    edges = []

    for work_id, work in works.items():
        cross_refs = work.properties.get("cross_references", [])

        for ref_url in cross_refs:
            # Resolve URL to node ID
            target_node = resolve_url_to_node(ref_url, works, entities)

            if target_node:
                edge = KnowledgeGraphEdge(
                    edge_id=f"{work_id}-xref-{target_node.node_id}",
                    edge_type=EdgeType.CROSS_REFERENCES,
                    source_id=work_id,
                    target_id=target_node.node_id,
                    properties={
                        "extraction_method": "explicit_link",
                        "source_url": ref_url
                    },
                    bidirectional=False
                )

                edges.append(edge)

    return edges

def resolve_url_to_node(url: str, works: Dict, entities: Dict) -> Optional[KnowledgeGraphNode]:
    """
    Map MIA URL to knowledge graph node.

    Examples:
        - "https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm" → Work node
        - "https://www.marxists.org/glossary/terms/s/u.htm#surplus-value" → Term entity
        - "https://www.marxists.org/glossary/people/m/a.htm#marx-karl" → Person entity
    """
    # Check if it's a glossary URL
    if "/glossary/" in url:
        # Extract entry ID from fragment (e.g., #marx-karl)
        if "#" in url:
            entry_id = url.split("#")[1]
            # Reconstruct full entry ID with type prefix
            for entity_type in ["people", "terms", "orgs", "events", "periodicals", "places"]:
                candidate_id = f"{entity_type}/{entry_id}"
                if candidate_id in entities:
                    return entities[candidate_id]

    # Check if it's a work URL
    for work in works.values():
        if work.properties["source_url"] == url:
            return work

    return None
```

**Expected**: 5,000-10,000 cross-reference edges (from corpus analysis)

### 2.4 Phase 4: Entity Mention Extraction (NER)

**Objective**: Create edges from entity mentions in document content

**Process:**

```python
class EntityMentionExtractor:
    """
    Extract entity mentions from document content using NER + Glossary matching.
    """

    def __init__(self, glossary_entities: Dict[str, KnowledgeGraphNode]):
        """
        Args:
            glossary_entities: Canonical entities from Glossary for matching
        """
        self.glossary_entities = glossary_entities
        self.entity_index = self._build_entity_index(glossary_entities)

    def _build_entity_index(self, entities: Dict) -> Dict[str, str]:
        """
        Build fast lookup index: canonical_name → entity_id

        Includes aliases for fuzzy matching.
        """
        index = {}

        for entity_id, entity in entities.items():
            # Add canonical name
            index[entity.label.lower()] = entity_id

            # Add aliases
            for alias in entity.aliases:
                index[alias.lower()] = entity_id

        return index

    def extract_mentions(self, work_id: str, content: str) -> List[KnowledgeGraphEdge]:
        """
        Extract entity mentions from work content.

        Algorithm:
        1. Tokenize content into sentences
        2. For each sentence, find entity matches (exact + fuzzy)
        3. Create MENTIONS_* edges with context
        """
        edges = []
        sentences = self._split_sentences(content)

        for sentence in sentences:
            # Find entity mentions in sentence
            mentions = self._find_entity_mentions(sentence)

            for entity_id, mention_text, confidence in mentions:
                entity = self.glossary_entities[entity_id]

                # Determine edge type based on entity type
                edge_type = self._get_mention_edge_type(entity.node_type)

                edge = KnowledgeGraphEdge(
                    edge_id=f"{work_id}-mentions-{entity_id}-{len(edges)}",
                    edge_type=edge_type,
                    source_id=work_id,
                    target_id=entity_id,
                    properties={
                        "extraction_method": "entity_mention",
                        "confidence": confidence,
                        "context": sentence,  # Surrounding sentence for context
                        "mention_text": mention_text  # Actual text matched
                    }
                )

                edges.append(edge)

        return edges

    def _find_entity_mentions(self, sentence: str) -> List[Tuple[str, str, float]]:
        """
        Find entity mentions in sentence.

        Returns:
            List of (entity_id, mention_text, confidence)

        Strategies:
        1. Exact match on canonical names
        2. Exact match on aliases
        3. Fuzzy match with Levenshtein distance (threshold > 0.85)
        """
        mentions = []
        sentence_lower = sentence.lower()

        # Exact matches (high confidence)
        for canonical_name, entity_id in self.entity_index.items():
            if canonical_name in sentence_lower:
                # Find actual mention text (preserve capitalization)
                import re
                pattern = re.compile(re.escape(canonical_name), re.IGNORECASE)
                match = pattern.search(sentence)
                if match:
                    mentions.append((entity_id, match.group(), 1.0))

        # Fuzzy matches (lower confidence)
        # TODO: Implement fuzzy matching for complex names

        return mentions

    def _get_mention_edge_type(self, entity_type: NodeType) -> EdgeType:
        """Map entity type to mention edge type."""
        mapping = {
            NodeType.PERSON: EdgeType.MENTIONS_PERSON,
            NodeType.TERM: EdgeType.MENTIONS_TERM,
            NodeType.ORGANIZATION: EdgeType.MENTIONS_ORG,
            NodeType.EVENT: EdgeType.DISCUSSES_EVENT,
            NodeType.PERIODICAL: EdgeType.PUBLISHED_IN,
        }
        return mapping.get(entity_type, EdgeType.MENTIONS_TERM)
```

**Expected**: ~50,000-100,000 mention edges (estimated 1-2 entity mentions per document on average)

### 2.5 Phase 5: Thematic Edges (Subject Categories)

**Objective**: Link works to Subject taxonomy categories

**Process:**

```python
def create_subject_category_edges(works: Dict, subject_categories: List[str]) -> Tuple[List[KnowledgeGraphEdge], Dict]:
    """
    Create IN_CATEGORY edges: Work → Subject Category

    Uses:
    - metadata.subject_categories (from Subject section breadcrumb)
    - metadata.keywords (inferred categories)

    Returns:
        (edges, category_nodes)
    """
    edges = []
    category_nodes = {}

    # Create category nodes
    for category in subject_categories:
        category_id = f"category/{slugify(category)}"
        category_nodes[category_id] = KnowledgeGraphNode(
            node_id=category_id,
            node_type=NodeType.SUBJECT_CATEGORY,
            label=category,
            properties={"category_name": category},
            embedding_id=None,
            aliases=[],
            cross_reference_count=0
        )

    # Create edges from works to categories
    for work_id, work in works.items():
        categories = work.properties.get("subject_categories", [])

        for category in categories:
            category_id = f"category/{slugify(category)}"

            if category_id in category_nodes:
                edge = KnowledgeGraphEdge(
                    edge_id=f"{work_id}-in-{category_id}",
                    edge_type=EdgeType.IN_CATEGORY,
                    source_id=work_id,
                    target_id=category_id,
                    properties={"extraction_method": "subject_metadata"}
                )

                edges.append(edge)

    return edges, category_nodes
```

**Expected**: ~2,000 category edges (Subject section has 2,259 files, many are indexes)

---

## 3. Graph Storage & Querying

### 3.1 Storage Options

**Option A: Neo4j (Recommended for RAG)**

**Pros:**
- Native graph database optimized for traversals
- Cypher query language (declarative, powerful)
- Excellent visualization tools
- Good Python integration (neo4j-driver)

**Cons:**
- Additional infrastructure (separate DB server)
- JVM-based (higher memory usage)

**Example Schema:**

```cypher
// Create constraints for node IDs
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.node_id IS UNIQUE;
CREATE CONSTRAINT work_id IF NOT EXISTS FOR (w:Work) REQUIRE w.node_id IS UNIQUE;
CREATE CONSTRAINT term_id IF NOT EXISTS FOR (t:Term) REQUIRE t.node_id IS UNIQUE;

// Create indexes for fast lookup
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.label);
CREATE INDEX work_title IF NOT EXISTS FOR (w:Work) ON (w.label);
```

**Option B: NetworkX (In-Memory, Simpler)**

**Pros:**
- Pure Python, no external DB
- Fast for small-medium graphs (<100k nodes)
- Good for prototyping

**Cons:**
- All in-memory (limit ~1M nodes on 16GB RAM)
- Slower traversals for large graphs
- No native persistence (serialize to disk)

**Example Usage:**

```python
import networkx as nx

# Create directed graph
G = nx.DiGraph()

# Add nodes
G.add_node("people/marx-karl", node_type="person", label="Karl Marx", birth_year="1818")
G.add_node("work/marx-capital-1867-ch01", node_type="work", label="Capital Vol. I, Ch. 1")

# Add edges
G.add_edge("work/marx-capital-1867-ch01", "people/marx-karl", edge_type="authored_by", confidence=1.0)
```

**Option C: SQLite with Graph Extensions (Hybrid)**

**Pros:**
- Single file database (portable)
- SQL familiarity
- Can store alongside vector DB

**Cons:**
- Graph traversals slower than Neo4j
- Requires recursive CTEs for multi-hop queries

### 3.2 Query Patterns

**3.2.1 Find all works by author:**

```cypher
// Neo4j Cypher
MATCH (w:Work)-[:AUTHORED_BY]->(p:Person {node_id: 'people/marx-karl'})
RETURN w.label, w.source_url, w.date_written
ORDER BY w.date_written
```

```python
# NetworkX
marx_works = [
    G.nodes[node]
    for node, author in G.in_edges("people/marx-karl")
    if G.nodes[node]["node_type"] == "work"
]
```

**3.2.2 Find works mentioning a term:**

```cypher
// Neo4j: Find works discussing "surplus value"
MATCH (w:Work)-[:MENTIONS_TERM]->(t:Term {node_id: 'terms/surplus-value'})
RETURN w.label, w.author, w.date_written
```

**3.2.3 Multi-hop: Find works cited by Lenin that mention Marx:**

```cypher
// Neo4j: Complex multi-hop query
MATCH (lenin:Person {label: 'Vladimir Lenin'})<-[:AUTHORED_BY]-(lenin_work:Work)-[:CROSS_REFERENCES]->(cited_work:Work)-[:MENTIONS_PERSON]->(marx:Person {label: 'Karl Marx'})
RETURN cited_work.label, cited_work.source_url
```

**3.2.4 Intellectual genealogy:**

```cypher
// Neo4j: Trace influence chain Hegel → Marx → Lenin
MATCH path = (hegel:Person {label: 'Georg Wilhelm Friedrich Hegel'})<-[:MENTIONS_PERSON*1..3]-(work:Work)-[:AUTHORED_BY]->(lenin:Person {label: 'Vladimir Lenin'})
RETURN path
LIMIT 10
```

**3.2.5 Thematic exploration:**

```cypher
// Neo4j: Find all works in "dialectics" category by period
MATCH (w:Work)-[:IN_CATEGORY]->(c:SubjectCategory {label: 'dialectics'})
WHERE w.date_written >= '1900' AND w.date_written <= '1949'
RETURN w.label, w.author, w.date_written
ORDER BY w.date_written
```

---

## 4. Integration with Vector Database

### 4.1 Hybrid Retrieval Strategy

**Problem**: Vector search returns semantically similar chunks, but lacks:
- Entity disambiguation (which "Stalin"?)
- Relationship awareness (find critiques of a work, not just similar texts)
- Multi-hop reasoning

**Solution**: Combine vector search with knowledge graph traversal

**4.1.1 Vector-First, Graph-Enhanced Retrieval:**

```python
class HybridRetriever:
    """Combine vector search with knowledge graph traversal."""

    def __init__(self, vector_db: VectorDatabase, knowledge_graph: KnowledgeGraph):
        self.vector_db = vector_db
        self.kg = knowledge_graph

    def retrieve(self, query: str, n_results: int = 10, enhance_with_kg: bool = True) -> List[RetrievalResult]:
        """
        Retrieve documents with optional knowledge graph enhancement.

        Algorithm:
        1. Vector search for top-N semantically similar chunks
        2. If enhance_with_kg:
           a. Extract entities from query
           b. Find entity nodes in knowledge graph
           c. Traverse graph for related works
           d. Re-rank results combining vector similarity + graph relevance
        """
        # Step 1: Vector search
        vector_results = self.vector_db.search(query, n_results=n_results * 2)  # Over-retrieve

        if not enhance_with_kg:
            return vector_results[:n_results]

        # Step 2: Extract entities from query
        query_entities = self._extract_query_entities(query)

        # Step 3: Find related works via knowledge graph
        kg_related_works = []
        for entity_id in query_entities:
            # Traverse: Entity → MENTIONS_* ← Work
            related = self.kg.find_works_mentioning_entity(entity_id)
            kg_related_works.extend(related)

        # Step 4: Re-rank combining vector similarity + graph relevance
        reranked = self._rerank(vector_results, kg_related_works)

        return reranked[:n_results]

    def _extract_query_entities(self, query: str) -> List[str]:
        """
        Extract entities from query string.

        Example:
            "What did Marx say about surplus value?" →
            ["people/marx-karl", "terms/surplus-value"]
        """
        # Use entity mention extractor from Phase 4
        entities = []

        # Exact match against Glossary entity index
        for canonical_name, entity_id in self.kg.entity_index.items():
            if canonical_name.lower() in query.lower():
                entities.append(entity_id)

        return entities

    def _rerank(self, vector_results: List, kg_related_works: List) -> List:
        """
        Re-rank results combining vector similarity + knowledge graph relevance.

        Scoring:
        - Vector similarity: 0.0-1.0 (cosine similarity)
        - KG relevance: +0.2 if work mentions query entity
        - Final score: (0.7 * vector_sim) + (0.3 * kg_boost)
        """
        scored_results = []

        for result in vector_results:
            work_id = result.metadata.get("work_id")
            vector_score = result.similarity

            # Check if work is in KG-related works
            kg_boost = 0.2 if work_id in kg_related_works else 0.0

            final_score = (0.7 * vector_score) + (0.3 * kg_boost)

            scored_results.append((final_score, result))

        # Sort by final score
        scored_results.sort(key=lambda x: x[0], reverse=True)

        return [result for score, result in scored_results]
```

**4.1.2 Graph-First, Vector-Filtered Retrieval:**

```python
def graph_first_retrieval(kg: KnowledgeGraph, vector_db: VectorDatabase, author: str, topic: str, n_results: int = 10) -> List:
    """
    Use knowledge graph to narrow candidates, then vector search within candidates.

    Example:
        "Find works by Marx about dialectics" →
        1. KG: Find all Marx works
        2. KG: Filter to works mentioning "dialectics" term
        3. Vector search: Rank by semantic similarity to detailed query
    """
    # Step 1: Find author entity
    author_entity = kg.find_person_entity(author)

    # Step 2: Find works by author
    author_works = kg.find_works_by_author(author_entity.node_id)

    # Step 3: Filter to works mentioning topic
    topic_entity = kg.find_term_entity(topic)
    filtered_works = [
        w for w in author_works
        if kg.has_edge(w.node_id, topic_entity.node_id, EdgeType.MENTIONS_TERM)
    ]

    # Step 4: Get chunk IDs for filtered works
    chunk_ids = []
    for work in filtered_works:
        chunks = kg.find_chunks_for_work(work.node_id)
        chunk_ids.extend([c.embedding_id for c in chunks])

    # Step 5: Vector search within filtered chunks
    results = vector_db.search_in_subset(query=topic, chunk_ids=chunk_ids, n_results=n_results)

    return results
```

---

## 5. Implementation Roadmap

### 5.1 Phase 1: Foundation (Week 1)

- [ ] Design graph schema (nodes, edges, properties)
- [ ] Choose storage backend (Neo4j vs NetworkX vs SQLite)
- [ ] Implement Glossary entity loader
- [ ] Load ~2,500 entities into graph
- [ ] Validate entity index and alias matching

### 5.2 Phase 2: Work Nodes & Authorship (Week 2)

- [ ] Implement work node creator
- [ ] Load ~55,753 work nodes
- [ ] Create authorship edges (AUTHORED_BY)
- [ ] Create work structure edges (PART_OF for multi-volume works)
- [ ] Validate authorship relationships

### 5.3 Phase 3: Cross-References (Week 3)

- [ ] Implement URL → node resolver
- [ ] Extract cross-references from metadata
- [ ] Create 5k-10k cross-reference edges
- [ ] Validate bidirectional cross-refs

### 5.4 Phase 4: Entity Mentions (Week 4-5)

- [ ] Implement entity mention extractor (NER + Glossary matching)
- [ ] Run on full corpus (55k documents)
- [ ] Create 50k-100k mention edges
- [ ] Optimize for performance (parallel processing)

### 5.5 Phase 5: Thematic Edges (Week 5)

- [ ] Create Subject category nodes (46 categories)
- [ ] Link works to categories
- [ ] Validate thematic connections

### 5.6 Phase 6: Query Interface (Week 6)

- [ ] Implement query patterns (by author, by term, multi-hop)
- [ ] Build hybrid retrieval (vector + graph)
- [ ] Optimize query performance
- [ ] Create query API

### 5.7 Phase 7: Integration & Testing (Week 7-8)

- [ ] Integrate with vector DB
- [ ] Test hybrid retrieval end-to-end
- [ ] Performance benchmarking
- [ ] Documentation and examples

---

## 6. Testing Requirements

### 6.1 Unit Tests

```python
def test_glossary_entity_loading():
    """Test that all Glossary entities load correctly."""
    loader = GlossaryEntityLoader()
    entities = loader.load_glossary_entities(glossary_dir)

    # Should have ~2,500 entities
    assert 2000 <= len(entities) <= 3000

    # Check person entity structure
    marx = entities.get("people/marx-karl")
    assert marx is not None
    assert marx.label == "Karl Marx"
    assert marx.properties["birth_year"] == "1818"
    assert "Marx" in marx.aliases

def test_authorship_edge_creation():
    """Test authorship edge creation from metadata."""
    edges = create_authorship_edges(works, entities)

    # Should have edge for every work with author
    works_with_authors = [w for w in works.values() if w.properties.get("author")]
    assert len(edges) >= len(works_with_authors) * 0.9  # Allow 10% missing

def test_cross_reference_resolution():
    """Test URL → node resolution."""
    url = "https://www.marxists.org/glossary/people/m/a.htm#marx-karl"
    node = resolve_url_to_node(url, works, entities)

    assert node is not None
    assert node.node_type == NodeType.PERSON
    assert node.node_id == "people/marx-karl"
```

### 6.2 Integration Tests

```python
def test_hybrid_retrieval():
    """Test vector + graph hybrid retrieval."""
    retriever = HybridRetriever(vector_db, kg)

    query = "What did Marx say about surplus value?"
    results = retriever.retrieve(query, n_results=10, enhance_with_kg=True)

    # Should return Marx works about surplus value
    assert len(results) > 0
    assert any("Marx" in r.metadata.get("author", "") for r in results)
    assert any("surplus value" in r.content.lower() for r in results)

def test_multi_hop_query():
    """Test multi-hop graph traversal."""
    # Find works cited by Lenin that mention Marx
    query = """
    MATCH (lenin:Person {label: 'Vladimir Lenin'})<-[:AUTHORED_BY]-(lenin_work:Work)
          -[:CROSS_REFERENCES]->(cited_work:Work)
          -[:MENTIONS_PERSON]->(marx:Person {label: 'Karl Marx'})
    RETURN cited_work.label
    """

    results = kg.execute_cypher(query)
    assert len(results) > 0
```

---

## 7. Usage Examples

### 7.1 Basic Graph Queries

```python
from src.knowledge_graph import KnowledgeGraph

# Initialize graph
kg = KnowledgeGraph.load("knowledge_graph.db")

# Find all works by Marx
marx_works = kg.find_works_by_author("Karl Marx")
print(f"Found {len(marx_works)} works by Marx")

# Find works mentioning "dialectics"
dialectics_works = kg.find_works_mentioning_term("dialectics")
print(f"Found {len(dialectics_works)} works discussing dialectics")

# Trace intellectual influence
influence_chain = kg.find_influence_path("Georg Wilhelm Friedrich Hegel", "Vladimir Lenin")
for hop in influence_chain:
    print(f"{hop['source']} → {hop['work']} → {hop['target']}")
```

### 7.2 Hybrid RAG Retrieval

```python
from src.retrieval import HybridRetriever

retriever = HybridRetriever(vector_db=vector_db, knowledge_graph=kg)

# Query with entity disambiguation
query = "What is Stalin's position on dialectical materialism?"
results = retriever.retrieve(query, n_results=5, enhance_with_kg=True)

for r in results:
    print(f"\n{r.metadata['title']} by {r.metadata['author']}")
    print(f"Score: {r.score:.3f} (vector: {r.vector_score:.3f}, kg_boost: {r.kg_boost:.3f})")
    print(f"Preview: {r.content[:200]}...")
```

---

## 8. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-08 | Initial specification based on corpus analysis findings |

---

**Status**: Ready for implementation by parallel AI agents
**Priority**: MEDIUM-HIGH (enhances RAG but not blocking)
**Estimated Implementation Time**: 6-8 weeks (can be parallelized)
