---
title: "Refactor: check_boundaries.py with Specification pattern"
labels: refactoring, technical-debt, complexity-reduction
assignees: ""
---

## Problem Statement

The `check_file_boundaries()` function in `check_boundaries.py:87` has dual complexity issues - both branch count and statement count exceed limits.

**Current Metrics:**
- **Branches**: 15 (target: ≤12)
- **Statements**: 52 (target: ≤50)
- **Complexity**: Business rules mixed with validation logic

## Current Implementation

The function uses nested if-else chains to validate file path compliance:

```python
def check_file_boundaries(file_path: Path, instance_id: str) -> tuple[bool, str]:
    # 15 branches checking:
    # - Instance ownership rules
    # - Shared path access rules
    # - Test file exclusions
    # - Special directory handling
    # - Path normalization edge cases
```

**Issues:**
- Business rules embedded in procedural code
- Difficult to express complex rule combinations (AND/OR/NOT)
- Hard to unit test individual rules
- Unclear which rule caused a violation

## Proposed Solution

Implement **Specification Pattern** for composable boundary validation:

### Architecture

```python
# 1. Domain Model
@dataclass(frozen=True)
class FilePath:
    absolute: Path
    relative_to_project: Path
    instance_owner: Optional[str]
    is_test_file: bool
    is_shared: bool

# 2. Specification Interface
class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, file_path: FilePath) -> bool:
        """Check if file satisfies specification."""

    @abstractmethod
    def reason(self) -> str:
        """Human-readable reason for specification."""

    def __and__(self, other: 'Specification') -> 'AndSpecification':
        return AndSpecification(self, other)

    def __or__(self, other: 'Specification') -> 'OrSpecification':
        return OrSpecification(self, other)

    def __invert__(self) -> 'NotSpecification':
        return NotSpecification(self)

# 3. Concrete Specifications
class OwnedByInstance(Specification):
    """File belongs to instance's owned paths."""

class InSharedPath(Specification):
    """File is in shared/common directory."""

class IsTestFile(Specification):
    """File is in tests/ directory."""

class IsConfigFile(Specification):
    """File is project-level config (.github, pyproject.toml, etc.)."""

# 4. Composite Specifications
class AndSpecification(Specification):
    def __init__(self, *specs: Specification):
        self.specs = specs

    def is_satisfied_by(self, file_path: FilePath) -> bool:
        return all(spec.is_satisfied_by(file_path) for spec in self.specs)

# 5. Boundary Rules
def create_boundary_rules(instance_id: str) -> Specification:
    """Factory for instance boundary rules."""
    owned = OwnedByInstance(instance_id)
    shared = InSharedPath()
    test = IsTestFile()
    config = IsConfigFile()

    # Instance can modify: owned OR shared OR tests OR config
    return owned | shared | test | config
```

### Implementation Steps

1. **Create `FilePath` value object** (`scripts/domain/boundaries.py`)
   - Encapsulate path analysis logic
   - Factory: `from_path(path, project_root)`

2. **Create specification base** (`scripts/patterns/specifications.py`)
   - `Specification` abstract base with boolean operators
   - `AndSpecification`, `OrSpecification`, `NotSpecification`

3. **Implement boundary specifications**
   - `OwnedByInstance`: Check instance ownership
   - `InSharedPath`: Validate shared directory access
   - `IsTestFile`: Test file detection
   - `IsConfigFile`: Project config detection

4. **Create rule factory**
   - `create_boundary_rules(instance_id)`: Build composite spec
   - Load instance config from `.claude/instance-assignments.json`

5. **Refactor `check_file_boundaries()`**
   - Parse file to `FilePath` value object
   - Load boundary rules specification
   - Evaluate: `spec.is_satisfied_by(file_path)`
   - Return violation with `spec.reason()` if false

## Acceptance Criteria

- [ ] Cyclomatic complexity: 15 branches → ≤8 branches
- [ ] Statement count: 52 statements → ≤35 statements
- [ ] Business rules expressed declaratively
- [ ] Specifications composable with `&`, `|`, `~` operators
- [ ] Each specification independently testable
- [ ] Violation messages clearly indicate which rule failed
- [ ] Pre-commit hooks pass
- [ ] Performance: <10ms per file check

## Files to Modify

- `scripts/check_boundaries.py` - Refactor `check_file_boundaries()` to use specifications
- `scripts/domain/boundaries.py` - NEW: `FilePath` value object
- `scripts/patterns/specifications.py` - NEW: Specification pattern implementation
- `tests/unit/test_boundary_specifications.py` - NEW: Specification tests

## Related Issues

- Part of Code Refactoring Project (.github/projects/refactoring-code-complexity.md)
  - **Stream 1**: Script complexity reduction (5 scripts, 1 complete)
  - **Stream 4**: Metadata pipeline refactoring (4 components, 0 complete)
- Related script refactors:
  - check_conflicts.py (Chain of Responsibility pattern)
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

**Time**: 4-5 hours
**Complexity**: Medium
**Priority**: High (dual violation: branches + statements)

## Example Usage

```python
# Before (procedural)
if instance_id in owned_paths and not is_shared and not is_test:
    return True, "OK"
elif shared_path and instance_id in allowed_shared:
    return True, "OK"
# ... 13 more branches

# After (declarative)
spec = create_boundary_rules(instance_id)
file_path = FilePath.from_path(path, project_root)
if spec.is_satisfied_by(file_path):
    return True, "OK"
else:
    return False, spec.reason()
```

## References

- [Specification Pattern](https://en.wikipedia.org/wiki/Specification_pattern)
- [Martin Fowler on Specifications](https://martinfowler.com/apsupp/spec.pdf)
- Original complexity analysis: commit `092592e`
