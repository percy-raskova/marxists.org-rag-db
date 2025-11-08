# Architectural Decision Records

This directory contains Architectural Decision Records (ADRs) documenting significant technical and architectural decisions made during the development of the Marxist RAG system.

## What is an ADR?

An Architectural Decision Record captures:
- **Context**: Why we needed to make a decision
- **Decision**: What we decided to do
- **Consequences**: The impact of our decision (positive, negative, neutral)
- **Alternatives**: Other options we considered
- **Implementation**: How we executed the decision

## ADR Index

| ADR | Title | Date | Status | Impact |
|-----|-------|------|--------|--------|
| [ADR-001](ADR-001-corpus-optimization.md) | Corpus Optimization from 200GB to 50GB | 2025-11-08 | Implemented | 75% size reduction, enables project feasibility |

## ADR Template

When creating a new ADR, use this structure:

```markdown
# ADR-XXX: [Title]

**Status**: [Proposed | Accepted | Implemented | Superseded by ADR-YYY]
**Date**: YYYY-MM-DD
**Decision Makers**: [List of people/roles involved]

## Context
[Why we needed to make this decision]

## Decision
[What we decided to do]

## Consequences
### Positive
[Benefits of this decision]

### Negative
[Drawbacks or limitations]

### Neutral
[Side effects that are neither good nor bad]

## Implementation Details
[How we executed this decision]

## Alternatives Considered
[Other options we evaluated and why we rejected them]

## References
[Links to relevant documents, discussions, or code]
```

## When to Create an ADR

Create an ADR for:
- Major architectural changes
- Technology selections (databases, frameworks, services)
- Data processing decisions (what to include/exclude)
- Cost/performance trade-offs
- Security decisions
- API design choices
- Development workflow changes

## Status Definitions

- **Proposed**: Decision is being discussed
- **Accepted**: Decision approved but not yet implemented
- **Implemented**: Decision has been executed
- **Superseded**: Replaced by a newer decision (link to new ADR)
- **Deprecated**: No longer relevant but kept for historical record

## Naming Convention

ADRs are named: `ADR-XXX-brief-description.md`
- XXX: Three-digit number (001, 002, etc.)
- brief-description: Kebab-case summary (4-5 words max)

Examples:
- `ADR-001-corpus-optimization.md`
- `ADR-002-vector-database-selection.md`
- `ADR-003-embedding-model-choice.md`