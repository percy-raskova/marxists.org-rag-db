# Contributing to MIA RAG System

## Project Information

**Author**: Persphone Raskova
**Repository**: <https://github.com/percy-raskova/marxists.org-rag-db>

## Overview

This project implements a 200GB-scale RAG (Retrieval Augmented Generation) system for the Marxists Internet Archive, designed for parallel development with 6 Claude Code instances.

## Getting Started

### For Claude Code Instances

1. **Identify your instance** (1-6):

   ```bash
   mise run instance{N}:setup
   ```

2. **Read the documentation**:
   - `AI-AGENT-INSTRUCTIONS.md` - Critical rules and workflows
   - `INSTANCE-BOUNDARIES.md` - Your ownership boundaries
   - Your module spec in `specs/`

3. **Follow TDD practices**:
   - Write tests FIRST
   - Achieve 80%+ coverage
   - Use the templates in `tests/templates/`

### For Human Contributors

1. Fork the repository
2. Create a feature branch
3. Follow the same TDD practices as AI agents
4. Ensure all tests pass
5. Submit a pull request

## Development Workflow

### Using Mise (not Make)

We use Mise for task orchestration:

```bash
# Install dependencies
mise run install

# Run tests
mise run test

# Check code quality
mise run quality

# Start work session
mise run work:start

# Create pull request
mise run pr "Your PR title"
```

### Instance Assignments

| Instance | Owner | Modules |
|----------|-------|---------|
| 1 | Storage & Pipeline | `src/mia_rag/storage/`, `src/mia_rag/pipeline/` |
| 2 | Embeddings | `src/mia_rag/embeddings/` |
| 3 | Weaviate | `src/mia_rag/vectordb/` |
| 4 | API | `src/mia_rag/api/` |
| 5 | MCP | `src/mia_rag/mcp/` |
| 6 | Monitoring | `src/mia_rag/monitoring/`, `tests/integration/` |

## Code Standards

### Python Style

- Use Ruff for linting and formatting
- Type hints required for all functions
- Docstrings in Google style
- 100 character line limit

### Testing Requirements

- **Minimum 80% coverage**
- Write tests before implementation (TDD)
- Use pytest markers for categorization
- Mock external services

### Commit Messages

Follow conventional commits:

```
feat(embeddings): add batch processor
fix(storage): handle connection timeout
docs(api): update endpoint documentation
test(weaviate): add integration tests
```

## Interface Changes

**NEVER** change interface contracts without:

1. Creating an RFC in `docs/rfcs/`
2. Waiting 24 hours for review
3. Getting approval from affected instances
4. Updating version numbers

## Data Sources

The project uses the Marxists Internet Archive dump (200GB):

- Available at: <https://archive.org/details/dump_www-marxists-org>
- Partial download already available at: `/home/user/Downloads/dump_www-marxists-org/`

## Architecture

- **Scale**: 200GB corpus (5-10M documents)
- **Cloud**: Google Cloud Platform
- **Vector DB**: Weaviate
- **Embeddings**: Runpod.io GPU ($40-60 total)
- **Development**: 6 parallel Claude Code instances

## Quality Checks

Before committing:

```bash
# Run all quality checks
mise run quality

# Run tests
mise run test

# Check boundaries
mise run check:boundaries

# Check interfaces
mise run check:interfaces
```

## Documentation

Key documents:

- `README.md` - Project overview
- `AI-AGENT-INSTRUCTIONS.md` - AI agent guidelines
- `INSTANCE-BOUNDARIES.md` - Instance ownership
- `CLAUDE_ENTERPRISE.md` - 200GB scale architecture
- `specs/` - Detailed specifications

## Support

For questions or issues:

- Create an issue on GitHub
- Check existing documentation
- Review work logs for context

## Acknowledgments

- Marxists Internet Archive for the corpus
- Google Cloud Platform for infrastructure
- Runpod.io for GPU resources
- Weaviate for vector database
- Anthropic for Claude Code

---

*"The philosophers have only interpreted the world; the point is to change it."* - Marx
