---
title: "Refactor: instance_map.py with Command pattern"
labels: refactoring, technical-debt, complexity-reduction
assignees: ""
---

## Problem Statement

The `show_instance_info()` function in `instance_map.py:130` has the highest cyclomatic complexity in the codebase (21 branches > 12 allowed), making it a maintenance bottleneck.

**Current Metrics:**
- **Branches**: 21 (target: ≤12) - **WORST OFFENDER**
- **Lines**: ~120
- **Complexity**: Mixing presentation logic with data formatting

## Current Implementation

The function uses a massive if-elif chain to handle different output formats:

```python
def show_instance_info(instance: str, format: str = "table"):
    # 21 conditionals handling:
    # - Format type (table/json/markdown/tree/compact)
    # - Sub-format variations
    # - Color schemes
    # - ASCII vs Unicode
    # - Verbosity levels
```

**Issues:**
- Violates Single Responsibility Principle
- Adding new formats requires modifying existing code
- Difficult to test individual formatters
- Presentation logic mixed with business logic

## Proposed Solution

Implement **Command Pattern** with strategy-based formatters:

### Architecture

```python
# 1. Domain Model (shared with #XXXX)
@dataclass(frozen=True)
class InstanceInfo:
    name: str
    description: str
    owned_paths: list[str]
    dependencies: list[str]
    status: str
    metadata: dict

# 2. Command Interface
class InstanceCommand(ABC):
    @abstractmethod
    def execute(self, info: InstanceInfo, ctx: CommandContext) -> str:
        """Execute command and return formatted output."""

# 3. Concrete Commands
class TableFormatter(InstanceCommand):
    """Rich table format (default)."""

class JsonFormatter(InstanceCommand):
    """JSON output for scripting."""

class MarkdownFormatter(InstanceCommand):
    """Markdown for documentation."""

class TreeFormatter(InstanceCommand):
    """ASCII/Unicode tree visualization."""

class CompactFormatter(InstanceCommand):
    """Single-line compact format."""

# 4. Command Invoker
class InstanceDisplayer:
    def __init__(self):
        self._commands: dict[str, InstanceCommand] = {
            "table": TableFormatter(),
            "json": JsonFormatter(),
            "markdown": MarkdownFormatter(),
            "tree": TreeFormatter(),
            "compact": CompactFormatter(),
        }

    def display(self, instance: str, format: str = "table", **opts) -> str:
        command = self._commands.get(format, self._commands["table"])
        info = self._load_instance_info(instance)
        ctx = CommandContext(**opts)
        return command.execute(info, ctx)
```

### Implementation Steps

1. **Create `InstanceInfo` value object** (`scripts/domain/instance.py`)
   - Encapsulate all instance data
   - Factory method: `from_config_file()`

2. **Create command base class** (`scripts/patterns/commands.py`)
   - `InstanceCommand` abstract base
   - `CommandContext` for options (color, unicode, verbose)

3. **Implement formatter commands**
   - `TableFormatter`: Rich table output
   - `JsonFormatter`: JSON serialization
   - `MarkdownFormatter`: Markdown tables
   - `TreeFormatter`: Tree visualization
   - `CompactFormatter`: One-line summary

4. **Create `InstanceDisplayer` invoker**
   - Registry of available formatters
   - CLI argument parsing
   - Error handling for unknown formats

5. **Refactor `show_instance_info()`**
   - Delegate to `InstanceDisplayer`
   - Reduce to ~10 lines

## Acceptance Criteria

- [ ] Cyclomatic complexity: 21 branches → ≤6 branches
- [ ] Each formatter is independently testable
- [ ] Adding new formats requires no changes to existing code
- [ ] CLI interface unchanged (backward compatible)
- [ ] Unit tests for each formatter
- [ ] Integration test for all formats
- [ ] Pre-commit hooks pass
- [ ] Performance: No regression (target <100ms)

## Files to Modify

- `scripts/instance_map.py` - Refactor `show_instance_info()` to use commands
- `scripts/domain/instance.py` - NEW: `InstanceInfo` value object
- `scripts/patterns/commands.py` - NEW: Command classes and invoker
- `tests/unit/test_instance_formatters.py` - NEW: Formatter tests

## Related Issues

- Part of Code Refactoring Project (.github/projects/refactoring-code-complexity.md)
  - **Stream 1**: Script complexity reduction (5 scripts, 1 complete)
  - **Stream 4**: Metadata pipeline refactoring (4 components, 0 complete)
- Related script refactors:
  - check_boundaries.py (Specification pattern) - ✅ Complete (shares `InstanceInfo` domain model)
  - check_conflicts.py (Chain of Responsibility pattern)
  - check_interfaces.py (Visitor pattern)
  - instance_recovery.py (Template Method pattern)
- Related metadata refactors:
  - Unified Metadata Schema (40+ fields, 5 layers)
  - Multi-Source Extraction Pipeline (85%+ author coverage)
  - Glossary Entity Linker (canonical name normalization)
  - Section-Specific Extractors (Archive, ETOL, EROL, Subject)
- Blocked by: None
- Blocks: None

## Estimated Effort

**Time**: 5-7 hours
**Complexity**: Medium-High
**Priority**: High (worst complexity offender)

## Performance Considerations

Current implementation is fast (~50ms). Command pattern adds minimal overhead (~5ms). Use `functools.lru_cache` for instance config loading if needed.

## References

- [Command Pattern](https://refactoring.guru/design-patterns/command)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy) (similar approach)
- Original complexity analysis: commit `092592e`
