# Git Workflow Guide for MIA RAG System

## Overview

This guide provides comprehensive instructions for the git workflow designed to support 6 parallel AI instances working on the MIA RAG system. The workflow ensures conflict-free, harmonious development with clear boundaries and automated quality checks.

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/percy-raskova/marxists.org-rag-db.git
cd marxist-rag

# Install dependencies and hooks
mise run install
mise run git:hooks

# Identify your instance (1-6)
mise run instance3:setup  # Replace 3 with your instance number

# Verify your boundaries
mise run show:boundaries
```

### 2. Daily Workflow

```bash
# Start your day
mise run work:start

# Sync with develop
mise run git:sync

# Create feature branch
mise run git:branch
# Enter feature name when prompted: batch-processor

# Work on your feature
# ... make changes ...

# Check boundaries before committing
mise run check:boundaries

# Commit with conventional format
git add src/mia_rag/embeddings/batch_processor.py
git commit -m "feat(embeddings): add batch processor with checkpointing"

# Push and create PR
git push origin instance2/embeddings-batch-processor
mise run git:pr

# End your day
mise run work:end
```

## Branch Structure

### Branch Naming Convention

```
main                          # Protected, production-ready
├── develop                   # Integration branch
│   ├── instance1/storage-feature-name
│   ├── instance2/embeddings-feature-name
│   ├── instance3/weaviate-feature-name
│   ├── instance4/api-feature-name
│   ├── instance5/mcp-feature-name
│   ├── instance6/monitoring-feature-name
│   ├── rfc/001-interface-change
│   ├── release/v2.0.0
│   └── hotfix/critical-bug-name
```

### Branch Types

| Type | Pattern | Example | Purpose |
|------|---------|---------|---------|
| **Feature** | `instance{N}/{module}-{feature}` | `instance2/embeddings-batch-processor` | Regular feature development |
| **RFC** | `rfc/{number}-{description}` | `rfc/001-storage-interface-v2` | Interface changes requiring review |
| **Release** | `release/v{major}.{minor}.{patch}` | `release/v2.0.0` | Release preparation |
| **Hotfix** | `hotfix/{severity}-{description}` | `hotfix/critical-memory-leak` | Emergency production fixes |
| **Integration** | `integration/daily-{date}` | `integration/daily-20240315` | Daily integration testing |

## Commit Message Format

### Convention

```
<type>(<scope>): <subject>

<body>

<footer>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types and Scopes

| Type | Description | Instance 1 | Instance 2 | Instance 3 | Instance 4 | Instance 5 | Instance 6 |
|------|-------------|-----------|-----------|-----------|-----------|-----------|-----------|
| `feat` | New feature | storage, pipeline | embeddings | weaviate, vectordb | api, query | mcp | monitoring |
| `fix` | Bug fix | storage, pipeline | embeddings | weaviate, vectordb | api, query | mcp | monitoring |
| `docs` | Documentation | | | | | | |
| `test` | Test changes | | | | | | integration, tests |
| `refactor` | Code refactoring | | | | | | |
| `perf` | Performance | | | | | | |
| `chore` | Maintenance | | | | | | |
| `rfc` | Interface change | | | | | | |

### Examples

```bash
# Good commit messages
feat(embeddings): add Runpod batch processor with checkpointing
fix(storage): handle GCS connection timeout gracefully
docs(api): update OpenAPI schema for v2 endpoints
test(weaviate): add integration tests for import pipeline
refactor(mcp): extract protocol handlers into separate modules
perf(embeddings): optimize batch size for GPU utilization
chore(deps): update weaviate-client to v4.5.0

# Bad commit messages (rejected by hooks)
feat: add feature           # Missing scope
update code                 # Not descriptive
WIP                        # Use feature branches instead
fix bug                    # What bug?
```

## Instance Boundaries

### Ownership Map

| Instance | Modules | Paths | Test Markers |
|----------|---------|-------|--------------|
| **Instance 1** | Storage & Pipeline | `src/mia_rag/storage/`<br>`src/mia_rag/pipeline/` | `instance1` |
| **Instance 2** | Embeddings | `src/mia_rag/embeddings/` | `instance2` |
| **Instance 3** | Weaviate | `src/mia_rag/vectordb/` | `instance3` |
| **Instance 4** | API | `src/mia_rag/api/` | `instance4` |
| **Instance 5** | MCP | `src/mia_rag/mcp/` | `instance5` |
| **Instance 6** | Monitoring | `src/mia_rag/monitoring/`<br>`tests/integration/` | `instance6`, `integration` |

### Shared Resources

Resources requiring coordination between all instances:

- **Interfaces**: `src/mia_rag/interfaces/`, `src/mia_rag/common/`
- **Configuration**: `pyproject.toml`, `.mise.toml`, `.gitignore`
- **Documentation**: `README.md`, `CLAUDE.md`, `docs/`, `specs/`

## Pull Request Process

### 1. Create Feature Branch

```bash
# Using Mise task
mise run git:branch
# Enter: batch-processor

# Or manually
git checkout -b instance2/embeddings-batch-processor
```

### 2. Make Changes

```bash
# Write tests first (TDD)
vim tests/unit/instance2_embeddings/test_batch_processor.py

# Implement feature
vim src/mia_rag/embeddings/batch_processor.py

# Run tests
mise run test

# Check coverage (must be ≥80%)
poetry run pytest -m instance2 --cov
```

### 3. Pre-commit Checks

```bash
# Automatic checks on commit
git add .
git commit -m "feat(embeddings): add batch processor"

# Manual checks
mise run check:boundaries
mise run check:interfaces
mise run lint
mise run format
```

### 4. Create Pull Request

```bash
# Push branch
git push origin instance2/embeddings-batch-processor

# Create PR with template
mise run git:pr
# Or
gh pr create --base develop --template .github/pull_request_template.md
```

### 5. PR Review Process

The PR will automatically:

1. Run instance-specific tests
2. Check boundary violations
3. Validate interface contracts
4. Measure coverage
5. Detect conflicts with other PRs

### 6. Merge Strategy

- **Feature → Develop**: Squash and merge
- **Develop → Main**: Merge commit (preserve history)
- **Release branches**: Merge commit
- **Hotfix branches**: Cherry-pick or merge

## Conflict Prevention

### Automated Checks

1. **Pre-commit hooks** validate:
   - Instance boundaries
   - Commit message format
   - No hardcoded secrets
   - TODO format
   - File sizes

2. **CI/CD checks** validate:
   - Unit tests pass
   - Coverage ≥80%
   - No boundary violations
   - Interface compliance
   - No conflicting PRs

### Manual Coordination

For shared resources:

1. Create RFC document in `docs/rfcs/`
2. Version bump in interface files
3. 24-hour review period
4. Approval from affected instances

## Emergency Procedures

### Rollback Procedure

```bash
# Using Mise task
mise run git:rollback
# Enter commit hash and reason

# Or manually
bash scripts/emergency_rollback.sh instance2 abc123 "Memory leak in production"
```

### Recovery Tools

```bash
# Diagnose issues
mise run git:diagnose

# Restore to specific commit
mise run git:recover
# Enter commit hash

# Check instance health
mise run git:health

# View activity report
mise run git:activity
```

## Daily Integration Testing

### Automatic Daily Run

Every day at 2 AM UTC:

1. Creates `integration/daily-YYYYMMDD` branch
2. Merges all instance branches
3. Runs full integration test suite
4. Creates GitHub issue with results

### Manual Integration Test

```bash
# Trigger integration test
gh workflow run daily-integration.yml

# Check results
gh run list --workflow=daily-integration.yml
```

## Git Commands Reference

### Mise Tasks

| Command | Description |
|---------|-------------|
| `mise run git:branch` | Create instance feature branch |
| `mise run git:sync` | Sync with develop branch |
| `mise run git:pr` | Create pull request |
| `mise run git:status` | Show detailed git status |
| `mise run git:conflicts` | Check for conflicts |
| `mise run git:rollback` | Emergency rollback |
| `mise run git:hooks` | Install git hooks |
| `mise run git:diagnose` | Diagnose issues |
| `mise run git:recover` | Recover to commit |
| `mise run git:activity` | Show activity report |
| `mise run git:health` | Health check |

### GitHub CLI

```bash
# List PRs for your instance
gh pr list --search "instance2"

# View PR status
gh pr status

# Check workflow runs
gh run list

# View specific PR
gh pr view 123

# Review PR
gh pr review 123 --approve
```

## Interface Changes

### Process

1. **Create RFC**:

   ```bash
   vim docs/rfcs/001-storage-interface-v2.md
   ```

2. **Create RFC branch**:

   ```bash
   git checkout -b rfc/001-storage-interface-v2
   ```

3. **Update interface with version**:

   ```python
   # src/mia_rag/interfaces/storage_contract.py
   __version__ = "2.0.0"  # Bumped from 1.0.0
   ```

4. **Create PR with RFC label**:

   ```bash
   gh pr create --label "rfc,interface-change"
   ```

5. **Wait 24 hours** for review

6. **Get approvals** from affected instances

## Metrics and Monitoring

### Development Velocity

```bash
# Check instance activity
mise run git:activity

# View all instances status
python scripts/instance_recovery.py status
```

### Integration Health

- Daily integration test results in GitHub Issues
- Coverage reports in Codecov
- PR merge time metrics

## Best Practices

### DO

- ✅ Write tests first (TDD)
- ✅ Maintain ≥80% coverage
- ✅ Use conventional commits
- ✅ Check boundaries before committing
- ✅ Sync with develop daily
- ✅ Create small, focused PRs
- ✅ Update work logs

### DON'T

- ❌ Modify files outside your boundaries
- ❌ Change interfaces without RFC
- ❌ Commit secrets or credentials
- ❌ Use force push on shared branches
- ❌ Skip pre-commit hooks
- ❌ Create PRs >1000 lines
- ❌ Work directly on develop/main

## Troubleshooting

### Common Issues

#### Boundary Violation

```bash
# Check which files violate boundaries
mise run check:boundaries

# See ownership of specific file
python scripts/instance_map.py --file src/mia_rag/api/main.py
```

#### Merge Conflicts

```bash
# Check for conflicts
git status

# Use instance recovery if needed
mise run git:recover
```

#### Failed Tests

```bash
# Run specific test
poetry run pytest tests/unit/instance2_embeddings/test_batch.py -v

# Check coverage
poetry run pytest -m instance2 --cov --cov-report=html
```

#### PR Blocked

Check:

1. All tests passing?
2. Coverage ≥80%?
3. No boundary violations?
4. Conventional commit format?
5. No conflicts with other PRs?

## Support

### Documentation

- [AI Agent Instructions](../../AI-AGENT-INSTRUCTIONS.md)
- [Instance Boundaries](../../INSTANCE-BOUNDARIES.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Conflict Resolution](conflict-resolution.md)

### Commands

```bash
# Get help
mise run help

# Show boundaries
mise run show:boundaries

# Check interfaces
mise run check:interfaces
```

### Issues

Create GitHub issues for:

- Integration test failures
- Boundary clarifications
- Interface change proposals
- Workflow improvements

---

*Last updated: 2024-03-15*
*Version: 1.0.0*
