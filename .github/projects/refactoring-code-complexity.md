# Code Refactoring Project

**Status**: In Progress (1/5 Complete)
**Owner**: Shared across instances (boundary-respecting)
**Priority**: HIGH
**Timeline**: 2-3 weeks

---

## Project Overview

Refactor scripts with code complexity violations (cyclomatic complexity, statement count) using design patterns to improve maintainability, testability, and AI agent comprehension.

**Goal**: Reduce all scripts to 0 complexity violations while maintaining functionality.

---

## Current Status

- ✅ **1/5 Scripts Refactored**: `check_boundaries.py` (Specification pattern)
- 🔄 **4/5 Scripts Remaining**: check_conflicts, instance_map, check_interfaces, instance_recovery
- ✅ **Pytest Configuration Fixed**: Migrated to pyproject.toml (supports inline comments)

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

---

## Critical Path

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

### Test Coverage

- ✅ `check_boundaries`: 15 unit tests (100% pattern coverage)
- 📋 `instance_map`: TBD
- 📋 `check_conflicts`: TBD
- 📋 `check_interfaces`: TBD
- 📋 `instance_recovery`: TBD

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

**Total Estimated**: ~83,000 tokens (15k used, 68k remaining)

---

## Dependencies

### External Dependencies

None

### Internal Dependencies

- **Domain models**: Each refactoring may add domain models to `scripts/domain/`
- **Pattern infrastructure**: Each pattern needs base classes in `scripts/patterns/`
- **Test infrastructure**: Pytest configuration must support all instances

### Cross-Project Dependencies

- **Documentation Project**: Clear docs help agents understand refactoring goals
- **Corpus Analysis**: Not blocked by refactoring, can proceed in parallel
- **Infrastructure**: Refactored code will be easier to deploy/maintain

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
