---
title: "Refactor: check_conflicts.py with Chain of Responsibility pattern"
labels: refactoring, technical-debt, complexity-reduction, good-first-issue
assignees: ""
---

## Problem Statement

The `analyze_imports()` function in `check_conflicts.py:250` has excessive cyclomatic complexity (17 branches > 12 allowed), making it difficult to test, maintain, and extend.

**Current Metrics:**
- **Branches**: 17 (target: ≤12)
- **Lines**: ~75
- **Complexity**: High coupling between parsing logic and validation rules

## Current Implementation

The function uses imperative if-else chains with string parsing for import analysis:

```python
def analyze_imports(file_path: Path, instance_id: str) -> list:
    # 17 nested conditionals checking:
    # - Line type (from/import)
    # - Module ownership (src vs shared)
    # - Cross-instance imports
    # - Shared module usage
    # - Path validation
```

**Issues:**
- String manipulation instead of AST parsing
- Tight coupling between parsing and validation
- Difficult to add new validation rules
- Hard to unit test individual validation steps

## Proposed Solution

Implement **Chain of Responsibility** pattern with AST-based import parsing:

### Architecture

```python
# 1. Domain Model
@dataclass(frozen=True)
class ImportStatement:
    module: str
    names: list[str]
    level: int
    source_file: Path
    line_number: int

@dataclass(frozen=True)
class ValidationContext:
    instance_id: str
    owned_paths: set[str]
    shared_modules: set[str]

# 2. Abstract Handler
class ImportValidator(ABC):
    def __init__(self, next_handler: Optional['ImportValidator'] = None):
        self._next = next_handler

    @abstractmethod
    def validate(self, import_stmt: ImportStatement, ctx: ValidationContext) -> Optional[Violation]:
        pass

    def handle(self, import_stmt: ImportStatement, ctx: ValidationContext) -> list[Violation]:
        violations = []
        if violation := self.validate(import_stmt, ctx):
            violations.append(violation)
        if self._next:
            violations.extend(self._next.handle(import_stmt, ctx))
        return violations

# 3. Concrete Validators
class OwnedPathValidator(ImportValidator):
    """Ensures instance only imports from owned paths."""

class SharedImportValidator(ImportValidator):
    """Validates shared module usage."""

class CrossInstanceValidator(ImportValidator):
    """Detects forbidden cross-instance imports."""

# 4. Factory
def create_validation_chain() -> ImportValidator:
    return OwnedPathValidator(
        SharedImportValidator(
            CrossInstanceValidator()
        )
    )
```

### Implementation Steps

1. **Create AST-based import parser** (`scripts/patterns/ast_utils.py`)
   - Replace string parsing with `ast.parse()`
   - Extract `ImportStatement` value objects

2. **Create validator base class** (`scripts/patterns/validators.py`)
   - `ImportValidator` abstract base
   - Chain of Responsibility implementation

3. **Implement concrete validators**
   - `OwnedPathValidator`: Check module ownership
   - `SharedImportValidator`: Validate shared module usage
   - `CrossInstanceValidator`: Detect cross-instance violations

4. **Refactor `analyze_imports()`**
   - Parse file to AST
   - Extract imports as `ImportStatement` objects
   - Run validation chain
   - Collect and return violations

## Acceptance Criteria

- [ ] Cyclomatic complexity: 17 branches → ≤12 branches
- [ ] AST-based parsing replaces string manipulation
- [ ] Each validator has single responsibility
- [ ] Unit tests for each validator independently
- [ ] Integration test verifies full chain
- [ ] Existing functionality preserved (no behavior change)
- [ ] Pre-commit hooks pass
- [ ] Documentation updated with architecture diagram

## Files to Modify

- `scripts/check_conflicts.py` - Refactor `analyze_imports()` function
- `scripts/patterns/ast_utils.py` - NEW: AST parsing utilities
- `scripts/patterns/validators.py` - NEW: Validator chain classes
- `tests/unit/test_import_validators.py` - NEW: Unit tests for validators

## Related Issues

- Part of Code Refactoring Project (planning/projects/refactoring-code-complexity.md)
  - **Stream 1**: Script complexity reduction (5 scripts, 1 complete)
  - **Stream 4**: Metadata pipeline refactoring (4 components, 0 complete)
- Related script refactors:
  - check_boundaries.py (Specification pattern) - ✅ Complete
  - check_interfaces.py (Visitor pattern)
  - instance_map.py (Command pattern)
  - instance_recovery.py (Template Method pattern)
- Related metadata refactors:
  - Unified Metadata Schema (40+ fields, 5 layers)
  - Multi-Source Extraction Pipeline (85%+ author coverage)
  - Glossary Entity Linker (canonical name normalization)
  - Section-Specific Extractors (Archive, ETOL, EROL, Subject)
- Blocked by: None
- Blocks: None

## Estimated Effort

**Time**: 4-6 hours
**Complexity**: Medium
**Priority**: High (blocking pre-commit clean state)

## References

- [Chain of Responsibility Pattern](https://refactoring.guru/design-patterns/chain-of-responsibility)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- Original complexity analysis: commit `092592e`
