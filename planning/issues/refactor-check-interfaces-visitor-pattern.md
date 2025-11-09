---
title: "Refactor: check_interfaces.py with Visitor pattern"
labels: refactoring, technical-debt, complexity-reduction
assignees: ""
---

## Problem Statement

The `validate_interface_usage()` function in `check_interfaces.py:148` has excessive cyclomatic complexity (16 branches > 12) due to AST traversal logic mixed with validation rules.

**Current Metrics:**
- **Branches**: 16 (target: ≤12)
- **Lines**: ~80
- **Complexity**: Tight coupling between AST parsing and contract validation

## Current Implementation

The function manually traverses AST nodes with nested conditionals:

```python
def validate_interface_usage(file_path: Path) -> list[Violation]:
    # 16 branches handling:
    # - AST node types (ClassDef, FunctionDef, Call, etc.)
    # - Interface inheritance detection
    # - Method implementation checking
    # - Type annotation validation
    # - Import statement analysis
```

**Issues:**
- AST traversal logic mixed with business rules
- Adding new validation rules requires modifying traversal code
- Difficult to test individual validation checks
- Violates Open/Closed Principle

## Proposed Solution

Implement **Visitor Pattern** with separate AST traversal and validation concerns:

### Architecture

```python
# 1. Domain Model
@dataclass(frozen=True)
class InterfaceViolation:
    file_path: Path
    line_number: int
    violation_type: str
    message: str
    severity: str  # "error" | "warning"

@dataclass
class ValidationContext:
    file_path: Path
    declared_interfaces: set[str]
    implemented_methods: dict[str, set[str]]
    violations: list[InterfaceViolation]

# 2. Visitor Base
class InterfaceVisitor(ast.NodeVisitor):
    """Base visitor for interface validation."""

    def __init__(self, ctx: ValidationContext):
        self.ctx = ctx

    @abstractmethod
    def get_violations(self) -> list[InterfaceViolation]:
        """Return collected violations."""

# 3. Concrete Visitors
class InterfaceInheritanceVisitor(InterfaceVisitor):
    """Validates classes inherit from proper interfaces."""

    def visit_ClassDef(self, node: ast.ClassDef):
        # Check if class inherits from interface
        # Verify interface is imported
        self.generic_visit(node)

class MethodImplementationVisitor(InterfaceVisitor):
    """Validates interface methods are implemented."""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Track method implementations
        # Compare against interface contract
        self.generic_visit(node)

class TypeAnnotationVisitor(InterfaceVisitor):
    """Validates type hints match interface contracts."""

    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Check type annotations
        # Verify against interface types
        self.generic_visit(node)

# 4. Repository Pattern (data access)
class InterfaceRepository:
    """Load interface definitions from contracts.py."""

    def __init__(self, contracts_path: Path):
        self.contracts = self._load_contracts(contracts_path)

    def get_interface(self, name: str) -> Optional[InterfaceDefinition]:
        return self.contracts.get(name)

    def get_required_methods(self, interface: str) -> set[str]:
        return self.contracts[interface].methods

# 5. Orchestrator
class InterfaceValidator:
    def __init__(self, repository: InterfaceRepository):
        self.repo = repository
        self.visitors = [
            InterfaceInheritanceVisitor,
            MethodImplementationVisitor,
            TypeAnnotationVisitor,
        ]

    def validate(self, file_path: Path) -> list[InterfaceViolation]:
        tree = ast.parse(file_path.read_text())
        ctx = ValidationContext(file_path=file_path, violations=[])

        # Run all visitors
        for visitor_class in self.visitors:
            visitor = visitor_class(ctx)
            visitor.visit(tree)

        return ctx.violations
```

### Implementation Steps

1. **Create domain models** (`scripts/domain/interfaces.py`)
   - `InterfaceViolation`: Violation value object
   - `ValidationContext`: Shared context for visitors
   - `InterfaceDefinition`: Contract specification

2. **Create repository** (`scripts/patterns/repositories.py`)
   - `InterfaceRepository`: Load and query interface contracts
   - Parse `src/mia_rag/interfaces/contracts.py`

3. **Implement visitor classes** (`scripts/patterns/visitors.py`)
   - `InterfaceInheritanceVisitor`: Check inheritance
   - `MethodImplementationVisitor`: Verify method completeness
   - `TypeAnnotationVisitor`: Validate type hints

4. **Create orchestrator**
   - `InterfaceValidator`: Coordinate visitor execution
   - Aggregate violations from all visitors

5. **Refactor `validate_interface_usage()`**
   - Instantiate `InterfaceValidator`
   - Delegate validation to visitors
   - Return aggregated violations

## Acceptance Criteria

- [ ] Cyclomatic complexity: 16 branches → ≤8 branches
- [ ] AST traversal separated from validation logic
- [ ] Each visitor has single responsibility
- [ ] Adding new validation rules requires no changes to existing visitors
- [ ] Unit tests for each visitor independently
- [ ] Integration test validates full contract checking
- [ ] Pre-commit hooks pass
- [ ] Performance: <200ms for typical file

## Files to Modify

- `scripts/check_interfaces.py` - Refactor `validate_interface_usage()` to use visitors
- `scripts/domain/interfaces.py` - NEW: Domain models for interface validation
- `scripts/patterns/visitors.py` - NEW: AST visitor implementations
- `scripts/patterns/repositories.py` - NEW: Interface contract repository
- `tests/unit/test_interface_visitors.py` - NEW: Visitor unit tests

## Related Issues

- Part of Code Refactoring Project (planning/projects/refactoring-code-complexity.md)
  - **Stream 1**: Script complexity reduction (5 scripts, 1 complete)
  - **Stream 4**: Metadata pipeline refactoring (4 components, 0 complete)
- Related script refactors:
  - check_boundaries.py (Specification pattern) - ✅ Complete
  - check_conflicts.py (Chain of Responsibility pattern) - Complements this (both use AST)
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

**Time**: 6-8 hours
**Complexity**: Medium-High (requires AST expertise)
**Priority**: Medium (blocks pre-commit clean state)

## Example Usage

```python
# Before (procedural AST traversal)
def validate_interface_usage(file_path: Path) -> list[Violation]:
    tree = ast.parse(file_path.read_text())
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if has_interface_base(node):
                if not implements_methods(node):
                    violations.append(...)
        # ... 14 more branches

    return violations

# After (visitor pattern)
def validate_interface_usage(file_path: Path) -> list[Violation]:
    repository = InterfaceRepository(CONTRACTS_PATH)
    validator = InterfaceValidator(repository)
    return validator.validate(file_path)
```

## References

- [Visitor Pattern](https://refactoring.guru/design-patterns/visitor)
- [Python AST NodeVisitor](https://docs.python.org/3/library/ast.html#ast.NodeVisitor)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- Original complexity analysis: commit `092592e`
