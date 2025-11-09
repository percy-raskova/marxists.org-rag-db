# Code Refactoring Project

**Status**: In Progress (1/9 Complete - Scripts + Metadata Pipeline)
**Owner**: Shared across instances (boundary-respecting)
**Priority**: HIGH
**Timeline**: 4-5 weeks

---

## Project Overview

Refactor scripts and processing pipeline to:
1. **Eliminate complexity violations** using design patterns (scripts)
2. **Implement unified metadata schema** from corpus analysis (mia_processor.py)
3. **Build multi-source extraction pipeline** for 85%+ author coverage
4. **Create Glossary entity linker** for knowledge graph support

**Goals**:
- Reduce all scripts to 0 complexity violations
- Implement complete metadata schema from docs/corpus-analysis/06-metadata-unified-schema.md
- Achieve metadata coverage targets (Archive 100%, ETOL 85%, EROL 95%)

---

## Current Status

### Scripts Refactoring
- ✅ **1/5 Scripts Refactored**: `check_boundaries.py` (Specification pattern)
- 🔄 **4/5 Scripts Remaining**: check_conflicts, instance_map, check_interfaces, instance_recovery
- ✅ **Pytest Configuration Fixed**: Migrated to pyproject.toml (supports inline comments)

### Metadata Pipeline Refactoring
- ✅ **Corpus Analysis Complete**: 46GB analyzed, 55,753 documents across 6 sections
- ✅ **Unified Schema Designed**: 5-layer metadata model specified
- 📋 **4/4 Pipeline Components Planned**: Schema implementation, multi-source extraction, Glossary linker, section-specific rules
- 🔄 **0/4 Components Implemented**

---

## Work Streams

### Stream 1: Script Refactoring 🔄 1/5 Complete

**Purpose**: Eliminate complexity violations using design patterns

| Script | Violations | Pattern | Priority | Status | Owner | Issue |
|--------|-----------|---------|----------|--------|-------|-------|
| `check_boundaries.py` | 15 branches + 52 statements | Specification | HIGH | ✅ Complete | - | - |
| `instance_map.py` | 21 branches | Command | HIGH | 📋 Planned | TBD | #TBD |
| `check_conflicts.py` | 17 branches | Chain of Responsibility | HIGH | 📋 Planned | TBD | #TBD |
| `check_interfaces.py` | 16 branches | Visitor | MEDIUM | 📋 Planned | TBD | #TBD |
| `instance_recovery.py` | 3 functions × violations | Template Method | MEDIUM | 📋 Planned | TBD | #TBD |

**Design Patterns Applied**:
- ✅ **Specification Pattern**: Composable business rules with boolean operators
- 📋 **Command Pattern**: Encapsulate requests as objects
- 📋 **Chain of Responsibility**: Pass requests through handler chain
- 📋 **Visitor Pattern**: Separate algorithms from object structure
- 📋 **Template Method**: Define algorithm skeleton, defer steps to subclasses

### Stream 2: Test Infrastructure ✅ Complete

**Purpose**: Fix pytest configuration for all instances

| Task | Status | Impact |
|------|--------|--------|
| Pytest config migration (INI → TOML) | ✅ Complete | Fixes inline comments support |
| Install pytest-html plugin | ✅ Complete | Enables HTML test reports |
| Unit tests for specifications | ✅ Complete | 15 tests passing |

**Key Fix**: INI format doesn't support inline comments, TOML does. Migrated pytest configuration from `pytest.ini` to `pyproject.toml` to preserve documentation.

### Stream 3: Domain Modeling ✅ 1/N Complete

**Purpose**: Extract domain models and patterns from scripts

| Model/Pattern | Purpose | Status | Location |
|--------------|---------|--------|----------|
| FilePath value object | File boundary metadata | ✅ Complete | `scripts/domain/boundaries.py` |
| Specification pattern | Composable business rules | ✅ Complete | `scripts/patterns/specifications.py` |
| Boundary specifications | Concrete boundary rules | ✅ Complete | `scripts/patterns/boundary_specifications.py` |
| Conflict detection | TBD | 📋 Planned | TBD |
| Instance mapping | TBD | 📋 Planned | TBD |
| Interface checking | TBD | 📋 Planned | TBD |

### Stream 4: Metadata Pipeline Refactoring 🔄 0/4 Complete

**Purpose**: Implement unified metadata schema from corpus analysis

| Component | Purpose | Status | Priority | Issue |
|-----------|---------|--------|----------|-------|
| **Unified Schema Implementation** | 5-layer metadata dataclass | 📋 Planned | CRITICAL | #TBD |
| **Multi-Source Extraction Pipeline** | Author extraction (85%+ coverage) | 📋 Planned | CRITICAL | #TBD |
| **Glossary Entity Linker** | Canonical name normalization | 📋 Planned | HIGH | #TBD |
| **Section-Specific Extractors** | Archive, ETOL, EROL, Subject rules | 📋 Planned | HIGH | #TBD |

**Metadata Coverage Targets** (from corpus analysis):
- **Archive**: 100% author coverage (path-based extraction)
- **ETOL**: 85% author coverage (title + keywords fallback)
- **EROL**: 95% organization attribution (title-based)
- **Subject**: 64% subject categories (breadcrumb extraction)
- **Glossary**: 100% entity structure (canonical IDs)
- **Reference**: 100% author coverage (path-based)

**Key Dependencies**:
- Glossary section must be processed first (builds entity index)
- Requires chardet library for encoding detection
- Needs HTML structure analyzer for document_structure metadata

**Estimated Effort**: 2-3 weeks for complete pipeline integration

---

## Milestones

### Milestone 1: Specification Pattern (check_boundaries) ✅ COMPLETE
- **Completed**: 2025-11-08
- **Pattern**: Specification pattern with boolean operators
- **Violations Eliminated**: 15 branches + 52 statements → 0
- **Tests**: 15 unit tests passing
- **Outcome**: Clean, composable boundary rules

**Deliverables**:
- ✅ `scripts/domain/boundaries.py` - FilePath value object
- ✅ `scripts/patterns/specifications.py` - Specification base classes
- ✅ `scripts/patterns/boundary_specifications.py` - Concrete specifications
- ✅ `tests/unit/test_boundary_specifications.py` - 15 passing tests
- ✅ Refactored `scripts/check_boundaries.py`

### Milestone 2: Command Pattern (instance_map) 📋 PLANNED
- **Target**: Week 1
- **Pattern**: Command pattern for instance operations
- **Script**: `instance_map.py` (21 branches - worst offender)
- **Violations**: PLR0912 (too many branches)
- **Estimated Effort**: 6-8 hours

**Planned Deliverables**:
- 📋 `scripts/domain/instances.py` - Instance domain models
- 📋 `scripts/patterns/commands.py` - Command pattern base
- 📋 `scripts/commands/instance_commands.py` - Concrete commands
- 📋 `tests/unit/test_instance_commands.py` - Unit tests
- 📋 Refactored `scripts/instance_map.py`

### Milestone 3: Chain of Responsibility (check_conflicts) 📋 PLANNED
- **Target**: Week 2
- **Pattern**: Chain of Responsibility for conflict detection
- **Script**: `check_conflicts.py` (17 branches)
- **Violations**: PLR0912 (too many branches)
- **Estimated Effort**: 6-8 hours

**Planned Deliverables**:
- 📋 `scripts/patterns/handlers.py` - Handler chain base
- 📋 `scripts/handlers/conflict_handlers.py` - Concrete handlers
- 📋 `tests/unit/test_conflict_handlers.py` - Unit tests
- 📋 Refactored `scripts/check_conflicts.py`

### Milestone 4: Visitor Pattern (check_interfaces) 📋 PLANNED
- **Target**: Week 2
- **Pattern**: Visitor pattern for interface checking
- **Script**: `check_interfaces.py` (16 branches)
- **Violations**: PLR0912 (too many branches)
- **Estimated Effort**: 5-7 hours

**Planned Deliverables**:
- 📋 `scripts/patterns/visitors.py` - Visitor pattern base
- 📋 `scripts/visitors/interface_visitors.py` - Concrete visitors
- 📋 `tests/unit/test_interface_visitors.py` - Unit tests
- 📋 Refactored `scripts/check_interfaces.py`

### Milestone 5: Template Method (instance_recovery) 📋 PLANNED
- **Target**: Week 3
- **Pattern**: Template Method for recovery procedures
- **Script**: `instance_recovery.py` (3 functions with violations)
- **Violations**: Multiple complexity violations
- **Estimated Effort**: 5-7 hours

**Planned Deliverables**:
- 📋 `scripts/patterns/templates.py` - Template method base
- 📋 `scripts/recovery/recovery_strategies.py` - Concrete strategies
- 📋 `tests/unit/test_recovery_strategies.py` - Unit tests
- 📋 Refactored `scripts/instance_recovery.py`

### Milestone 6: Unified Metadata Schema (mia_processor) 📋 PLANNED
- **Target**: Week 3-4
- **Pattern**: Dataclass with multi-layer structure
- **Module**: `mia_processor.py` metadata extraction
- **Current State**: Basic DocumentMetadata (8 fields) → Full schema (40+ fields)
- **Estimated Effort**: 12-16 hours

**Planned Deliverables**:
- 📋 Updated `DocumentMetadata` dataclass (5 layers, 40+ fields)
- 📋 `mia_processor/metadata/schema.py` - Schema definitions
- 📋 `mia_processor/metadata/extractors.py` - Field extraction functions
- 📋 `tests/unit/test_metadata_schema.py` - Schema validation tests
- 📋 Migration script for existing processed documents

**Success Criteria**:
- All required fields populated (source_url, title, content_hash, section_type, etc.)
- Provenance tracking for all extracted fields (author_source, date_source)
- Confidence scoring for extracted metadata (author_confidence, etc.)

### Milestone 7: Multi-Source Extraction Pipeline 📋 PLANNED
- **Target**: Week 4
- **Pattern**: Strategy pattern for extraction sources
- **Module**: Author, date, keywords extraction
- **Coverage Targets**: Archive 100%, ETOL 85%, EROL 95%
- **Estimated Effort**: 16-20 hours

**Planned Deliverables**:
- 📋 `mia_processor/extractors/author.py` - Multi-source author extraction
- 📋 `mia_processor/extractors/date.py` - Multi-source date extraction
- 📋 `mia_processor/extractors/keywords.py` - Keywords & classification
- 📋 `mia_processor/extractors/section_rules.py` - Section-specific rules
- 📋 `tests/unit/test_extractors.py` - Extraction validation (100-sample test sets per section)

**Extraction Strategies**:
- **Author**: Path → Title → Keywords → Meta tag → Content (7 strategies)
- **Date**: Path → Title → Provenance → Meta tag (5 strategies)
- **Keywords**: Meta tag → Breadcrumb → Cross-reference extraction

**Success Criteria**:
- Archive section: 100% author coverage (path-based)
- ETOL section: 85%+ author coverage (title + keywords)
- EROL section: 95%+ organization attribution
- Date extraction: 60%+ coverage across corpus
- Encoding normalization: Handle 62% ISO-8859-1 → UTF-8

### Milestone 8: Glossary Entity Linker 📋 PLANNED
- **Target**: Week 4-5
- **Pattern**: Index + fuzzy matching
- **Module**: Entity linking for canonical names
- **Dependencies**: Glossary section processing complete
- **Estimated Effort**: 10-14 hours

**Planned Deliverables**:
- 📋 `mia_processor/glossary/index_builder.py` - Build entity index from Glossary
- 📋 `mia_processor/glossary/entity_linker.py` - Fuzzy matching & normalization
- 📋 `mia_processor/glossary/cross_referencer.py` - Extract cross-references
- 📋 `tests/unit/test_glossary_linker.py` - Entity linking accuracy tests
- 📋 Glossary index cache (JSON/Parquet format for fast loading)

**Entity Types**:
- People (~800 entries): Name normalization, alias matching
- Terms (~600 entries): Definition linking
- Organizations (~400 entries): Acronym expansion
- Events (~300 entries): Temporal context
- Periodicals (~200 entries): Publication metadata
- Places (~200 entries): Geographic context

**Success Criteria**:
- Author name normalization: 90%+ accuracy
- Entity mention extraction: 80%+ precision
- Cross-reference network: 5,000-10,000 edges
- Glossary index load time: <2 seconds

### Milestone 9: Section-Specific Extraction Rules 📋 PLANNED
- **Target**: Week 5
- **Pattern**: Section-specific extractor classes
- **Module**: Archive, ETOL, EROL, Subject, Glossary, Reference rules
- **Dependencies**: Multi-source extraction pipeline complete
- **Estimated Effort**: 8-12 hours

**Planned Deliverables**:
- 📋 `mia_processor/sections/archive.py` - Archive-specific extraction
- 📋 `mia_processor/sections/etol.py` - ETOL-specific extraction
- 📋 `mia_processor/sections/erol.py` - EROL-specific extraction
- 📋 `mia_processor/sections/subject.py` - Subject-specific extraction
- 📋 `mia_processor/sections/glossary.py` - Glossary-specific extraction
- 📋 `mia_processor/sections/reference.py` - Reference-specific extraction
- 📋 `tests/integration/test_section_extractors.py` - End-to-end validation

**Section-Specific Features**:
- **Archive**: Work collection detection, chapter numbering, letter recipients
- **ETOL**: Transcriber vs. author disambiguation, newspaper detection, movement affiliation
- **EROL**: Organization attribution (MLOC, RCP, etc.), NCM classification, unique h3-as-title handling
- **Subject**: Anthology detection, Peking Review special handling, cross-reference network
- **Glossary**: Entry type classification, cross-reference count, canonical ID generation
- **Reference**: Non-Marxist author detection, Git LFS verification, subject organization

**Success Criteria**:
- All section-specific fields populated correctly
- Edge cases handled (index pages, multi-article files, heading-less documents)
- Integration tests pass for representative documents from each section

---

## Critical Path

### Scripts Refactoring Track
```
Specification Pattern (✅ Complete)
  ↓
Command Pattern (instance_map.py)
  ↓
Chain of Responsibility (check_conflicts.py)
  ↓
Visitor Pattern (check_interfaces.py)
  ↓
Template Method (instance_recovery.py)
  ↓
All Scripts Refactored (0 violations)
```

### Metadata Pipeline Track (Can run in parallel)
```
Unified Metadata Schema
  ↓
Multi-Source Extraction Pipeline
  ↓
Glossary Entity Linker (depends on Glossary processing)
  ↓
Section-Specific Extraction Rules
  ↓
Complete Metadata Pipeline (85%+ author coverage)
```

**Note**: Both tracks can proceed in parallel - scripts refactoring doesn't block metadata work

---

## Success Metrics

### Complexity Reduction

**Before**:
- `check_boundaries.py`: 15 branches + 52 statements (DUAL violation)
- `instance_map.py`: 21 branches
- `check_conflicts.py`: 17 branches
- `check_interfaces.py`: 16 branches
- `instance_recovery.py`: 3 functions × multiple violations

**After (Target)**:
- ✅ `check_boundaries.py`: 0 violations
- 📋 All scripts: 0 violations
- 📋 All tests: 100% passing
- 📋 Coverage: >80% for refactored code

### Code Quality Metrics

- **Maintainability**: Pattern-based design enables easier modifications
- **Testability**: Each pattern component independently testable
- **Readability**: Clear separation of concerns, single responsibility
- **AI Agent Comprehension**: Explicit patterns easier for AI to understand

### Test Coverage (Scripts)

- ✅ `check_boundaries`: 15 unit tests (100% pattern coverage)
- 📋 `instance_map`: TBD
- 📋 `check_conflicts`: TBD
- 📋 `check_interfaces`: TBD
- 📋 `instance_recovery`: TBD

### Metadata Coverage Metrics (Pipeline)

**Current State** (basic schema):
- DocumentMetadata: 8 fields (source_url, title, author, date, language, doc_type, word_count, content_hash)
- Author extraction: ~70% coverage (path-based only for Archive)
- Date extraction: ~53% coverage (path-based only)
- No entity linking, no section-specific rules

**Target State** (unified schema):
- DocumentMetadata: 40+ fields across 5 layers
- **Author Coverage Targets**:
  - Archive: 100% (path-based extraction)
  - ETOL: 85%+ (multi-source: title + keywords + meta)
  - EROL: 95%+ (organization attribution from title/keywords)
  - Subject: 48%+ (meta tag + cross-reference)
  - Glossary: 100% (entry structure)
  - Reference: 100% (path-based)
- **Date Coverage**: 60%+ across corpus (multi-source extraction)
- **Entity Linking**: 90%+ author name normalization accuracy
- **Cross-References**: 5,000-10,000 edges extracted from Glossary
- **Encoding Normalization**: 100% UTF-8 (handle 62% ISO-8859-1 conversion)

---

## Blockers and Risks

### Current Blockers

None - all blockers resolved:
- ✅ Pytest configuration fixed (INI → TOML migration)
- ✅ Missing plugins installed (pytest-html)
- ✅ Import path issues resolved

### Medium Risks

1. **Pattern Complexity** (using advanced patterns may be overkill)
   - **Mitigation**: Only use patterns where they reduce complexity
   - **Impact**: Over-engineering could make code harder to understand

2. **Test Maintenance** (more tests = more maintenance)
   - **Mitigation**: Keep tests focused on behavior, not implementation
   - **Impact**: Additional test suite maintenance burden

3. **Breaking Changes** (refactoring may change behavior)
   - **Mitigation**: Comprehensive test coverage before refactoring
   - **Impact**: Must verify no behavior changes

### Low Risks

1. **Performance Overhead** (patterns may add indirection)
   - **Mitigation**: Scripts are not performance-critical
   - **Impact**: Negligible for human-facing CLI scripts

---

## Resource Allocation

### AI Agent Time per Script

- ✅ `check_boundaries.py`: ~6 hours (Complete)
- 📋 `instance_map.py`: ~8 hours (Worst offender, 21 branches)
- 📋 `check_conflicts.py`: ~7 hours
- 📋 `check_interfaces.py`: ~6 hours
- 📋 `instance_recovery.py`: ~6 hours

**Total Estimated**: ~33 hours (6 complete, 27 remaining)

### Token Budget per Script

- ✅ `check_boundaries`: ~15,000 tokens (Used)
- 📋 `instance_map`: ~20,000 tokens (Complex, 21 branches)
- 📋 `check_conflicts`: ~18,000 tokens
- 📋 `check_interfaces`: ~15,000 tokens
- 📋 `instance_recovery`: ~15,000 tokens

**Total Estimated Scripts**: ~83,000 tokens (15k used, 68k remaining)

### AI Agent Time per Metadata Component

- 📋 Unified Schema Implementation: ~14 hours
- 📋 Multi-Source Extraction Pipeline: ~18 hours
- 📋 Glossary Entity Linker: ~12 hours
- 📋 Section-Specific Extractors: ~10 hours

**Total Estimated Metadata**: ~54 hours

### Token Budget per Metadata Component

- 📋 Unified Schema: ~25,000 tokens (40+ field dataclass)
- 📋 Multi-Source Extraction: ~35,000 tokens (7 extraction strategies)
- 📋 Glossary Linker: ~22,000 tokens (fuzzy matching, index building)
- 📋 Section Extractors: ~20,000 tokens (6 section handlers)

**Total Estimated Metadata**: ~102,000 tokens

### Combined Project Totals

- **AI Agent Time**: ~87 hours (6 hours complete, 81 hours remaining)
  - Scripts: ~33 hours
  - Metadata: ~54 hours
- **Token Budget**: ~185,000 tokens (15k used, 170k remaining)
  - Scripts: ~83,000 tokens
  - Metadata: ~102,000 tokens

---

## Dependencies

### External Dependencies

**Metadata Pipeline**:
- `chardet` library: Character encoding detection (62% ISO-8859-1 corpus)
- `python-Levenshtein` (optional): Fuzzy string matching for entity linking
- BeautifulSoup: HTML parsing (already required)

**Scripts**:
- None

### Internal Dependencies

**Scripts Refactoring**:
- **Domain models**: Each refactoring adds domain models to `scripts/domain/`
- **Pattern infrastructure**: Each pattern needs base classes in `scripts/patterns/`
- **Test infrastructure**: Pytest configuration must support all instances

**Metadata Pipeline**:
- **Glossary processing**: Must process Glossary section first to build entity index
- **HTML structure analyzer**: `scripts/html_structure_analyzer.py` for document_structure metadata
- **Corpus analysis specs**: `docs/corpus-analysis/06-metadata-unified-schema.md` defines schema

### Cross-Project Dependencies

- **Documentation Project**: Clear docs help agents understand refactoring goals
- **Corpus Analysis**: ✅ Complete - Metadata schema defined from 46GB analysis
- **Infrastructure**: Refactored code will be easier to deploy/maintain
- **Instance 1 (Storage)**: Will use unified metadata schema for processed documents

---

## Design Pattern Details

### Specification Pattern ✅ Implemented

**Use Case**: Composable business rules (boundary checking)

**Structure**:
```python
class Specification(ABC):
    def is_satisfied_by(self, candidate: T) -> bool: ...
    def __and__(self, other): return AndSpecification(self, other)
    def __or__(self, other): return OrSpecification(self, other)
    def __invert__(self): return NotSpecification(self)

# Usage
rule = (OwnedByInstance("instance1")
        | InSharedPath()
        | IsTestFile()
        | ~IsCriticalFile())
```

**Benefits**:
- Composable with boolean operators (&, |, ~)
- Self-documenting (each rule explains itself)
- Testable in isolation

### Command Pattern 📋 Planned

**Use Case**: Instance operations (add, remove, show, etc.)

**Structure**:
```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> CommandResult: ...
    @abstractmethod
    def undo(self) -> None: ...

class AddInstanceCommand(Command):
    def execute(self): ...
    def undo(self): ...
```

**Benefits**:
- Encapsulates operations as objects
- Supports undo/redo
- Easy to add new operations

### Chain of Responsibility 📋 Planned

**Use Case**: Conflict detection with multiple checks

**Structure**:
```python
class ConflictHandler(ABC):
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, file_path: Path) -> ConflictResult:
        result = self.check(file_path)
        if result.has_conflict:
            return result
        if self.next_handler:
            return self.next_handler.handle(file_path)
        return ConflictResult.no_conflict()
```

**Benefits**:
- Decouples senders from receivers
- Easy to add/remove handlers
- Each handler has single responsibility

### Visitor Pattern 📋 Planned

**Use Case**: Interface checking across different node types

**Structure**:
```python
class InterfaceVisitor(ABC):
    def visit_class(self, node: ClassDef): ...
    def visit_function(self, node: FunctionDef): ...
    def visit_import(self, node: Import): ...

class ContractViolationVisitor(InterfaceVisitor):
    def visit_class(self, node):
        # Check if class violates interface contracts
```

**Benefits**:
- Separates algorithms from object structure
- Easy to add new operations
- Maintains single responsibility

### Template Method 📋 Planned

**Use Case**: Recovery procedures with common steps

**Structure**:
```python
class RecoveryStrategy(ABC):
    def recover(self):
        self.backup()
        self.validate()
        self.restore()
        self.verify()

    @abstractmethod
    def backup(self): ...
    @abstractmethod
    def restore(self): ...
```

**Benefits**:
- Defines algorithm skeleton
- Subclasses customize steps
- Enforces procedure consistency

---

## Testing Strategy

### Unit Testing

Each pattern gets comprehensive unit tests:
- ✅ Specification pattern: 15 tests (boolean operators, composition)
- 📋 Command pattern: Test execute(), undo(), result handling
- 📋 Chain of Responsibility: Test handler chains, short-circuiting
- 📋 Visitor pattern: Test visitor dispatch, node traversal
- 📋 Template Method: Test template flow, step overrides

### Integration Testing

Test refactored scripts end-to-end:
- Run scripts with sample inputs
- Verify output matches original behavior
- Check no regressions in CLI interface

### Regression Testing

Before/after comparison:
- Capture output of original script
- Run refactored script with same inputs
- Diff outputs to ensure identical behavior

---

## Communication

### Status Updates

- **Weekly**: Update script completion status
- **Blockers**: Immediately flag any new complexity issues
- **Completion**: Mark milestones complete with metrics

### Code Review Checklist

For each refactored script:
- [ ] Complexity violations eliminated (ruff check passes)
- [ ] Unit tests written and passing
- [ ] Integration tests verify no behavior changes
- [ ] Pattern properly documented
- [ ] Code is more readable than original

---

## Related Projects

- **Documentation Project** - Instance coordination documentation
- **Corpus Analysis Project** - RAG specifications (benefits from clean code)
- **Infrastructure** - Cloud deployment (easier with clean code)

---

## Notes

- Pytest configuration fix (INI → TOML) benefits all 6 parallel instances
- Each refactoring should maintain 100% backward compatibility
- Design patterns chosen based on GoF patterns and Clean Architecture principles
- Focus on readability and maintainability over cleverness
