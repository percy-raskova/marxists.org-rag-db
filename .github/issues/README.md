# Complexity Reduction Initiative - Issue Tracker

This directory contains GitHub-style issues for systematically eliminating all remaining code complexity violations in the marxist-rag project.

## Current Status

**Progress**: 4 of 12 complexity violations resolved (33% complete)

**Remaining**: 8 violations across 5 issues

## Issues Overview

### Issue #1: Chain of Responsibility - check_conflicts.py
**File**: `refactor-check-conflicts-chain-of-responsibility.md`
**Priority**: 🔴 High
**Complexity**: Medium
**Effort**: 4-6 hours
**Violations**: 1 (17 branches → ≤12)

**Pattern**: Chain of Responsibility + AST parsing
**Impact**: Security-critical import validation
**Blocks**: Pre-commit clean state

---

### Issue #2: Command Pattern - instance_map.py
**File**: `refactor-instance-map-command-pattern.md`
**Priority**: 🔴 High
**Complexity**: Medium-High
**Effort**: 5-7 hours
**Violations**: 1 (21 branches → ≤6) - **WORST OFFENDER**

**Pattern**: Command + Strategy
**Impact**: Largest single complexity violation
**Synergy**: Shares `InstanceInfo` domain model with boundaries

---

### Issue #3: Specification Pattern - check_boundaries.py
**File**: `refactor-check-boundaries-specification-pattern.md`
**Priority**: 🔴 High
**Complexity**: Medium
**Effort**: 4-5 hours
**Violations**: 2 (15 branches, 52 statements)

**Pattern**: Specification + Composite
**Impact**: Dual violation (branches + statements)
**Benefits**: Declarative business rules, composable with boolean operators

---

### Issue #4: Visitor Pattern - check_interfaces.py
**File**: `refactor-check-interfaces-visitor-pattern.md`
**Priority**: 🟡 Medium
**Complexity**: Medium-High
**Effort**: 6-8 hours
**Violations**: 1 (16 branches → ≤8)

**Pattern**: Visitor + Repository
**Impact**: Contract validation quality
**Requirements**: AST expertise

---

### Issue #5: Template Method - instance_recovery.py
**File**: `refactor-instance-recovery-template-method.md`
**Priority**: 🟡 Medium-High
**Complexity**: High
**Effort**: 8-10 hours
**Violations**: 3 (56 statements, 13 branches, 17 branches)

**Pattern**: Template Method + Strategy
**Impact**: Largest refactor, critical recovery logic
**Risk**: High - requires extensive testing
**Benefits**: Eliminates 3 violations in one refactor

---

## Implementation Order

### Phase 1: Quick Wins (8-10 hours)
1. **Issue #1** - Chain of Responsibility (check_conflicts.py)
2. **Issue #3** - Specification Pattern (check_boundaries.py)

**Rationale**: Both are high-priority, medium complexity, and provide immediate pre-commit relief.

### Phase 2: Major Refactor (5-7 hours)
3. **Issue #2** - Command Pattern (instance_map.py)

**Rationale**: Worst single offender (21 branches). Creates reusable `InstanceInfo` domain model.

### Phase 3: Advanced Patterns (14-18 hours)
4. **Issue #4** - Visitor Pattern (check_interfaces.py)
5. **Issue #5** - Template Method (instance_recovery.py)

**Rationale**: More complex, require AST expertise and extensive testing. Issue #5 eliminates 3 violations but has highest risk.

---

## Dependencies Graph

```
┌─────────────────────────────────────────┐
│  Issue #1: check_conflicts.py          │
│  Chain of Responsibility                │
│  Priority: High | Effort: 4-6h          │
└─────────────────────────────────────────┘
               │
               │ (no dependencies)
               ▼
┌─────────────────────────────────────────┐
│  Issue #3: check_boundaries.py         │
│  Specification Pattern                  │
│  Priority: High | Effort: 4-5h          │
└─────────────────────────────────────────┘
               │
               │ shares InstanceInfo
               ▼
┌─────────────────────────────────────────┐
│  Issue #2: instance_map.py             │
│  Command Pattern (WORST: 21 branches)   │
│  Priority: High | Effort: 5-7h          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Issue #4: check_interfaces.py         │
│  Visitor Pattern                        │
│  Priority: Medium | Effort: 6-8h        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Issue #5: instance_recovery.py        │
│  Template Method (3 violations!)        │
│  Priority: Med-High | Effort: 8-10h     │
└─────────────────────────────────────────┘
```

---

## Success Metrics

### Code Quality
- [ ] All ruff complexity violations eliminated (0 errors)
- [ ] Pre-commit hooks pass cleanly
- [ ] Cyclomatic complexity: Max 12 branches per function
- [ ] Statement count: Max 50 statements per function

### Architecture Quality
- [ ] Domain models created for each concern (boundaries, recovery, interfaces)
- [ ] Design patterns properly implemented (not just ceremony)
- [ ] Each pattern has ≥3 unit tests
- [ ] Integration tests verify behavior unchanged

### Maintainability
- [ ] Adding new validation rules requires no existing code changes (Open/Closed)
- [ ] Each validator/strategy/visitor independently testable (SRP)
- [ ] Business rules expressed declaratively, not procedurally
- [ ] Code is self-documenting with clear naming

---

## Total Effort Estimate

**Minimum**: 27 hours (optimistic)
**Expected**: 35 hours (realistic)
**Maximum**: 41 hours (pessimistic)

**Recommended Pace**: 1-2 issues per week for thorough implementation and testing.

---

## Quick Reference

| Issue | File | Pattern | Branches | Statements | Priority |
|-------|------|---------|----------|------------|----------|
| #1 | check_conflicts.py:250 | Chain of Responsibility | 17→12 | - | High |
| #2 | instance_map.py:130 | Command | 21→6 | - | High |
| #3 | check_boundaries.py:87 | Specification | 15→8 | 52→35 | High |
| #4 | check_interfaces.py:148 | Visitor | 16→8 | - | Medium |
| #5a | instance_recovery.py:134 | Template Method | - | 56→30 | Med-High |
| #5b | instance_recovery.py:285 | Template Method | 13→5 | - | Med-High |
| #5c | instance_recovery.py:336 | Template Method | 17→8 | - | Med-High |

---

## Contributing

When implementing these refactors:

1. **Read the full issue** - Each contains detailed architecture diagrams
2. **Write tests first** - TDD ensures behavior preservation
3. **Commit atomically** - One pattern implementation per commit
4. **Update this README** - Check off completed items
5. **Run benchmarks** - Ensure no performance regression

## References

- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [Martin Fowler - Refactoring](https://refactoring.com/)
- [Original Analysis](../../commits/092592e) - Commit with complexity reduction plan

---

*Generated as part of the systematic complexity reduction initiative.*
*Last Updated: 2025-11-08*
