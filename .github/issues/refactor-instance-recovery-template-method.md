---
title: "Refactor: instance_recovery.py with Template Method pattern"
labels: refactoring, technical-debt, complexity-reduction
assignees: ""
---

## Problem Statement

The `instance_recovery.py` module has **three separate functions** with complexity violations, all following the same recovery workflow pattern but with duplicated logic.

**Current Metrics:**
- `validate_recovery_state()` at line 134: 56 statements (target: ≤50)
- `perform_recovery()` at line 285: 13 branches (target: ≤12)
- `rollback_recovery()` at line 336: 17 branches (target: ≤12)
- **Total**: 3 violations in related functions

## Current Implementation

Three functions implement similar recovery workflows with duplicated validation and error handling:

```python
def validate_recovery_state() -> bool:
    # 56 statements checking:
    # - Git repository state
    # - Instance configuration
    # - Backup existence
    # - File permissions
    # - Disk space

def perform_recovery() -> bool:
    # 13 branches handling:
    # - Backup selection
    # - File restoration
    # - Git operations
    # - Error recovery

def rollback_recovery() -> bool:
    # 17 branches handling:
    # - Transaction rollback
    # - State restoration
    # - Cleanup operations
    # - Error logging
```

**Issues:**
- Duplicated validation logic across all three functions
- No clear recovery workflow abstraction
- Error handling repeated in each function
- Difficult to extend with new recovery strategies

## Proposed Solution

Implement **Template Method Pattern** with abstract recovery workflow:

### Architecture

```python
# 1. Domain Model
@dataclass(frozen=True)
class RecoveryContext:
    instance_id: str
    backup_path: Path
    target_state: str
    created_at: datetime

@dataclass
class RecoveryResult:
    success: bool
    operations_performed: list[str]
    errors: list[str]
    rollback_available: bool

# 2. Abstract Template
class RecoveryStrategy(ABC):
    """Template for recovery operations."""

    def execute(self, ctx: RecoveryContext) -> RecoveryResult:
        """Template method defining recovery workflow."""
        result = RecoveryResult(success=True, operations_performed=[], errors=[])

        try:
            # 1. Pre-flight validation (HOOK)
            if not self.validate_preconditions(ctx, result):
                return result

            # 2. Prepare recovery (HOOK)
            if not self.prepare(ctx, result):
                return result

            # 3. Execute core recovery (ABSTRACT - must implement)
            if not self.perform_recovery(ctx, result):
                self.rollback(ctx, result)
                return result

            # 4. Verify recovery (HOOK)
            if not self.verify(ctx, result):
                self.rollback(ctx, result)
                return result

            # 5. Finalize (HOOK)
            self.finalize(ctx, result)

        except Exception as e:
            result.errors.append(str(e))
            result.success = False
            self.rollback(ctx, result)

        return result

    # Template hooks (optional override)
    def validate_preconditions(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        """Validate before starting recovery."""
        return True

    def prepare(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        """Prepare for recovery (create backups, etc.)."""
        return True

    def verify(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        """Verify recovery succeeded."""
        return True

    def finalize(self, ctx: RecoveryContext, result: RecoveryResult) -> None:
        """Cleanup and finalize."""
        pass

    # Abstract method (must implement)
    @abstractmethod
    def perform_recovery(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        """Core recovery logic - must be implemented by subclass."""

    # Rollback (optional override)
    def rollback(self, ctx: RecoveryContext, result: RecoveryResult) -> None:
        """Rollback failed recovery."""
        result.rollback_available = False

# 3. Concrete Strategies
class GitRecoveryStrategy(RecoveryStrategy):
    """Recover instance using git reset."""

    def validate_preconditions(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        # Check git status, verify commit exists
        return self._git_repo_valid() and self._commit_exists(ctx.target_state)

    def perform_recovery(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        # git reset --hard <target_state>
        # git clean -fd
        result.operations_performed.append("git_reset")
        return True

class BackupRestoreStrategy(RecoveryStrategy):
    """Recover instance from backup tarball."""

    def validate_preconditions(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        return ctx.backup_path.exists() and self._verify_backup_integrity(ctx.backup_path)

    def prepare(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        # Create safety backup before restoration
        self._create_safety_backup()
        return True

    def perform_recovery(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        # Extract backup to instance directory
        result.operations_performed.append("backup_restore")
        return True

    def rollback(self, ctx: RecoveryContext, result: RecoveryResult) -> None:
        # Restore from safety backup
        self._restore_safety_backup()
        result.rollback_available = True

class ConfigRecoveryStrategy(RecoveryStrategy):
    """Recover instance configuration only."""

    def perform_recovery(self, ctx: RecoveryContext, result: RecoveryResult) -> bool:
        # Restore .claude/ configuration files
        result.operations_performed.append("config_restore")
        return True

# 4. Factory
def create_recovery_strategy(recovery_type: str) -> RecoveryStrategy:
    strategies = {
        "git": GitRecoveryStrategy(),
        "backup": BackupRestoreStrategy(),
        "config": ConfigRecoveryStrategy(),
    }
    return strategies.get(recovery_type, GitRecoveryStrategy())
```

### Implementation Steps

1. **Create domain models** (`scripts/domain/recovery.py`)
   - `RecoveryContext`: Input parameters
   - `RecoveryResult`: Output with success/errors/operations

2. **Create abstract template** (`scripts/patterns/recovery.py`)
   - `RecoveryStrategy`: Abstract base with template method
   - Define workflow: validate → prepare → recover → verify → finalize

3. **Implement concrete strategies**
   - `GitRecoveryStrategy`: Git-based recovery
   - `BackupRestoreStrategy`: Tarball restoration
   - `ConfigRecoveryStrategy`: Config-only recovery

4. **Add validation utilities** (`scripts/patterns/recovery_validators.py`)
   - `DiskSpaceValidator`: Check available disk space
   - `GitStateValidator`: Validate git repository
   - `BackupIntegrityValidator`: Verify backup checksums

5. **Refactor existing functions**
   - `validate_recovery_state()` → Strategy hook methods (56 → ~15 lines each)
   - `perform_recovery()` → Strategy template method (13 → ~5 lines)
   - `rollback_recovery()` → Strategy rollback hook (17 → ~8 lines)

## Acceptance Criteria

- [ ] `validate_recovery_state()`: 56 statements → ≤30 statements (distributed across hooks)
- [ ] `perform_recovery()`: 13 branches → ≤5 branches
- [ ] `rollback_recovery()`: 17 branches → ≤8 branches
- [ ] **Total reduction**: 3 violations → 0 violations
- [ ] Each recovery strategy independently testable
- [ ] Template workflow eliminates duplication
- [ ] Error handling centralized in template method
- [ ] CLI interface unchanged
- [ ] Unit tests for each strategy
- [ ] Integration test for full recovery workflow
- [ ] Pre-commit hooks pass

## Files to Modify

- `scripts/instance_recovery.py` - Refactor to use strategy pattern
- `scripts/domain/recovery.py` - NEW: Domain models
- `scripts/patterns/recovery.py` - NEW: Template method and strategies
- `scripts/patterns/recovery_validators.py` - NEW: Validation utilities
- `tests/unit/test_recovery_strategies.py` - NEW: Strategy tests

## Related Issues

- Part of #XXXX: Systematic complexity reduction initiative
- Largest refactor: 3 violations in one module
- Blocked by: None
- Blocks: None

## Estimated Effort

**Time**: 8-10 hours
**Complexity**: High (largest refactor, critical recovery logic)
**Priority**: Medium-High (3 violations, but complex)

## Risk Mitigation

**High Risk Area**: Recovery logic is critical - bugs could cause data loss

**Mitigation Steps**:
1. Comprehensive unit tests for each strategy (>90% coverage)
2. Integration tests with real git repos and backups
3. Manual testing with instance1-6 configurations
4. Code review required before merge
5. Feature flag: `USE_NEW_RECOVERY=true` environment variable
6. Rollback plan: Keep old implementation for 2 releases

## Example Usage

```python
# Before (3 separate complex functions)
if not validate_recovery_state(instance, backup):  # 56 statements
    return False

if not perform_recovery(instance, backup):  # 13 branches
    rollback_recovery(instance)  # 17 branches
    return False

# After (declarative strategy)
ctx = RecoveryContext(instance_id=instance, backup_path=backup, target_state="HEAD~1")
strategy = create_recovery_strategy("git")
result = strategy.execute(ctx)

if not result.success:
    console.print(f"[red]Recovery failed: {result.errors}[/red]")
    return False
```

## References

- [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy) (complementary)
- [Transaction Script vs Domain Model](https://martinfowler.com/eaaCatalog/transactionScript.html)
- Original complexity analysis: commit `092592e`
