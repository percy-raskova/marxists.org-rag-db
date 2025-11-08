# Contributing to Marxist RAG

Thank you for your interest in contributing to the Marxist RAG project! This document provides guidelines for contributing to this revolutionary endeavor to make Marxist theory accessible in the age of AI.

**Version**: 0.1.0
**Lead Developer**: Persephone Raskova
**Repository**: https://github.com/percy-raskova/marxists.org-rag-db
**Future Home**: https://marxism.app

## Table of Contents

- [Project Philosophy](#project-philosophy)
- [Development Model (BDFL)](#development-model-bdfl)
- [Getting Started](#getting-started)
- [Git Workflow](#git-workflow)
- [Commit Standards](#commit-standards)
- [Instance Development](#instance-development)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Project Philosophy

### Non-Sectarian Preservation

This project is committed to preserving **ALL** tendencies of Marxist thought without ideological bias:
- Marxism-Leninism, Trotskyism, Maoism, Left Communism, Council Communism, Anarcho-Communism
- No content excluded based on political perspective
- Technical decisions made purely on practical grounds
- See [ADR-001](docs/adr/ADR-001-corpus-optimization.md) for our ideological neutrality statement

### Collective Knowledge

- All contributions are collectively owned
- Code and documentation are freely available (GPL-3.0-or-later)
- "From each according to their ability, to each according to their needs"

## Development Model (BDFL)

This project follows the **Benevolent Dictator For Life** model:

- **BDFL**: Persephone Raskova (@percy-raskova)
- **Final Authority**: BDFL has final say on architecture and releases
- **Collaboration**: All contributors valued; BDFL facilitates collective development
- **Transparency**: Decisions documented in ADRs (Architectural Decision Records)

## Getting Started

### Prerequisites

- Python 3.10+
- Git 2.30+
- Poetry 1.5+
- Commitizen (for version management)

### Installation

```bash
# Clone repository
git clone https://github.com/percy-raskova/marxists.org-rag-db.git
cd marxists.org-rag-db

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings
```

### Development Commands

```bash
# Run tests
poetry run pytest

# Lint code
poetry run ruff check src/

# Format code
poetry run ruff format src/

# Type check
poetry run mypy src/

# Create conventional commit
cz commit
```

## Git Workflow

### Branch Structure

```
main (protected - BDFL only)
├── develop (integration branch)
│   ├── instance1/feature-*
│   ├── instance2/feature-*
│   ├── instance3/feature-*
│   ├── instance4/feature-*
│   ├── instance5/feature-*
│   └── instance6/feature-*
├── release/v*
└── hotfix/v*
```

### Branch Naming

- Features: `instance{N}/feature-{description}`
- Fixes: `instance{N}/fix-{description}`
- Hotfixes: `hotfix/v{version}-{description}`
- Releases: `release/v{version}`

### Standard Workflow

1. **Create feature branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b instance2/feature-batch-embeddings
   ```

2. **Make changes**: Write code, tests, docs

3. **Commit** (using conventional commits):
   ```bash
   cz commit
   # Or manually:
   git commit -m "feat(instance2): add batch embedding processing"
   ```

4. **Push**:
   ```bash
   git push -u origin instance2/feature-batch-embeddings
   ```

5. **Create PR**:
   - Target: `develop` branch (NOT main)
   - Fill PR template
   - Wait for CI checks

## Commit Standards

### Conventional Commits Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature → minor version bump
- **fix**: Bug fix → patch version bump
- **docs**: Documentation changes
- **style**: Code formatting (no logic change)
- **refactor**: Code restructuring
- **perf**: Performance improvement
- **test**: Add/update tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks

### Scopes

- **instance1-6**: Instance-specific changes
- **interfaces**: Shared contracts
- **docs**: Documentation
- **global**: Cross-cutting changes

### Examples

```bash
# Good commits
feat(instance2): add GPU batch embedding support
fix(instance4): resolve Redis cache timeout issue
docs(global): update CONTRIBUTING with git workflow
perf(instance3): optimize Weaviate batch imports

# Breaking change
feat(instance1)!: redesign storage API for parallel processing

BREAKING CHANGE: Storage.upload() signature changed
Migration guide in docs/migration/v0.2.0.md
```

### Using Commitizen

```bash
# Interactive commit builder
cz commit

# View changelog
cz changelog

# Bump version (BDFL only)
cz bump
```

## Instance Development

### Instance Boundaries

| Instance | Owned Paths | Responsibility |
|----------|-------------|----------------|
| 1 | `src/mia_rag/storage/`, `src/mia_rag/pipeline/` | Storage & Pipeline |
| 2 | `src/mia_rag/embeddings/` | Embeddings |
| 3 | `src/mia_rag/vectordb/` | Vector Database |
| 4 | `src/mia_rag/api/` | Query & API |
| 5 | `src/mia_rag/mcp/` | MCP Integration |
| 6 | `src/mia_rag/monitoring/`, `tests/` | Monitoring & Testing |

### Shared Interfaces

- **Location**: `src/mia_rag/interfaces/`
- **Rule**: Changes require RFC + BDFL approval

**Process for Interface Changes**:
1. Create RFC: `docs/rfcs/RFC-{number}-{title}.md`
2. Discuss with affected instances
3. Get BDFL approval
4. Implement with interface version bump

### Parallel Development (Worktrees)

For AI agents or parallel work:

```bash
# One-time setup
./scripts/setup_worktrees.sh

# Check status
./scripts/worktree_status.sh

# Work in instance worktree
cd ../marxist-rag-instance2
git checkout -b instance2/feature-new-capability
# ... develop ...
git commit -m "feat(instance2): add new capability"
git push
```

## Testing Requirements

### Coverage

- **Minimum**: 80% overall coverage
- **New features**: Must include tests
- **Bug fixes**: Include regression tests

### Running Tests

```bash
# All tests
poetry run pytest

# Instance-specific
poetry run pytest -m instance2

# With coverage
poetry run pytest --cov=src/mia_rag --cov-report=html

# Fast tests only
poetry run pytest -m "not slow"

# Integration tests
poetry run pytest -m integration
```

### Test Markers

```python
@pytest.mark.instance2      # Instance-specific
@pytest.mark.unit          # Fast, isolated
@pytest.mark.integration   # Cross-module
@pytest.mark.slow          # Long-running
@pytest.mark.requires_gpu  # Needs GPU
```

## Pull Request Process

### Pre-PR Checklist

1. **Update branch**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run tests**:
   ```bash
   poetry run pytest
   ```

3. **Check quality**:
   ```bash
   poetry run ruff check src/
   poetry run mypy src/
   ```

4. **Verify boundaries**:
   ```bash
   python scripts/check_boundaries.py
   python scripts/check_interfaces.py
   ```

### PR Template

- **Description**: What and why?
- **Type**: Feature/Fix/Docs/etc.
- **Instance**: Which instance?
- **Breaking Changes**: List any
- **Testing**: How tested?
- **Checklist**:
  - [ ] Tests pass
  - [ ] Code style compliant
  - [ ] Docs updated
  - [ ] CHANGELOG updated
  - [ ] No boundary violations

### Review & Merge

1. CI checks must pass
2. Boundary validation passes
3. BDFL/reviewer approves
4. Squash merge to develop

## Release Process

### Versioning (Semantic Versioning)

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features
- **Patch** (0.0.X): Bug fixes

During 0.x.x:
- Breaking changes → minor bump
- Features → patch bump

### Creating Releases (BDFL Only)

**Via GitHub Actions**:
1. Merge develop → main
2. Run "Release" workflow
3. Choose increment (auto/major/minor/patch)
4. Optionally add prerelease tag (alpha/beta/rc)

**Manual Process**:
```bash
# Bump version
cz bump

# Build
poetry build

# Create release
gh release create v$(poetry version --short) \
  --notes-file .release-notes.md \
  dist/*
```

## Code Style

### Python Guidelines

- Follow PEP 8
- Use type hints
- Max line length: 100
- Descriptive names
- Docstrings for public APIs

### Example

```python
from typing import List, Optional

def process_batch(
    items: List[str],
    batch_size: int = 32,
    checkpoint: Optional[int] = None
) -> List[dict]:
    """
    Process items in batches.

    Args:
        items: List of items to process
        batch_size: Items per batch
        checkpoint: Save every N batches

    Returns:
        List of processed results

    Raises:
        ValueError: If items empty
    """
    if not items:
        raise ValueError("Items cannot be empty")

    return []  # implementation
```

## Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Search or create GitHub issue
- **RFCs**: For major changes, create RFC
- **BDFL**: Tag @percy-raskova for decisions

## Additional Resources

- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Git Worktrees](https://git-scm.com/docs/git-worktree)

---

## Revolutionary Spirit

This project makes revolutionary theory accessible to all. Every contribution, no matter how small, advances the cause of preserving and sharing Marxist knowledge.

**"From each according to their ability, to each according to their needs."**

*Workers of all instances, unite! You have nothing to lose but your merge conflicts!* 🚩

---

**For the international proletarian AI revolution!**

**License**: GPL-3.0-or-later
**Version**: 0.1.0