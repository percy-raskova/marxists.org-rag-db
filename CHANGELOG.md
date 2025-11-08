# Changelog

All notable changes to the Marxist RAG project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Architectural Decision Records (ADR) framework for documenting major decisions
- Corpus optimization from 200GB to 50GB (75% reduction) - see ADR-001
- Project attribution and credits documentation
- Professional git workflow with semantic versioning
- Keep a Changelog compliant changelog (this file!)

### Changed
- Architecture updated from 200GB to 50GB scale
- Reduced computational requirements by 88%
- Simplified from 6 parallel instances to 3-4 sequential phases

### Fixed
- Pytest configuration migrated from INI to TOML to support inline comments

## [0.1.0] - 2025-11-08 - "Spectre Haunting Silicon Valley"

### Added
- Distributed processing orchestrator with Ray/Dask for 200GB corpus
- Google Cloud Storage (GCS) integration with Parquet format
- Runpod.io GPU rental integration for embeddings ($40-60 total cost)
- Weaviate vector database cluster deployment for billion-scale vectors
- FastAPI query engine with Redis caching layer
- MCP (Model Context Protocol) server implementation
- Prometheus + Grafana monitoring stack
- Comprehensive test suite with 6 parallel instance architecture
- GitHub Projects tracking for multiple work streams
- Pre-commit hooks with extensive validation
- Specification pattern for boundary checking

### Changed
- **BREAKING**: Architecture redesigned from 38GB to 200GB scale
- **BREAKING**: Switched from local Chroma to distributed Weaviate
- **BREAKING**: Moved from Ollama to Runpod.io for embedding generation
- Refactored code to use Specification pattern for composable rules
- Updated all documentation to reflect enterprise scale

### Security
- Added secrets detection in pre-commit hooks
- Implemented credential rotation strategy
- Added boundary validation for instance isolation

[Unreleased]: https://github.com/percy-raskova/marxists.org-rag-db/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/percy-raskova/marxists.org-rag-db/releases/tag/v0.1.0-spectre-haunting-silicon-valley