# MIA RAG System - Documentation Index

**Master index of all documentation in the marxist-rag project.**

Last Updated: 2025-11-08

---

## 🚀 Quick Start (Choose Your Role)

**AI Agent working on a specific instance?**
→ Go directly to your instance guide:

- [INSTANCE1-STORAGE.md](./INSTANCE1-STORAGE.md) - Storage & Data Pipeline
- [INSTANCE2-EMBEDDINGS.md](./INSTANCE2-EMBEDDINGS.md) - Runpod Embeddings
- [INSTANCE3-WEAVIATE.md](./INSTANCE3-WEAVIATE.md) - Vector Database
- [INSTANCE4-API.md](./INSTANCE4-API.md) - Query & API Layer
- [INSTANCE5-MCP.md](./INSTANCE5-MCP.md) - MCP Server Integration
- [INSTANCE6-MONITORING.md](./INSTANCE6-MONITORING.md) - Monitoring & Testing

**New contributor or user?**
→ Start here: [README.md](./README.md) or [START_HERE.md](./START_HERE.md)

**Need architecture overview?**
→ See [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## 📋 Documentation Structure

### Root-Level Documentation (15 files)

#### Essential Entry Points
- [README.md](./README.md) - User-facing project overview
- [START_HERE.md](./START_HERE.md) - Navigation hub for all stakeholders
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contributor guidelines
- [DOCUMENTATION-INDEX.md](./DOCUMENTATION-INDEX.md) - THIS FILE

#### Instance Quick-Start Guides (6 files)
- [INSTANCE1-STORAGE.md](./INSTANCE1-STORAGE.md) - Storage & Pipeline (1-2 pages)
- [INSTANCE2-EMBEDDINGS.md](./INSTANCE2-EMBEDDINGS.md) - Embeddings (1-2 pages)
- [INSTANCE3-WEAVIATE.md](./INSTANCE3-WEAVIATE.md) - Weaviate Vector DB (1-2 pages)
- [INSTANCE4-API.md](./INSTANCE4-API.md) - Query & API (1-2 pages)
- [INSTANCE5-MCP.md](./INSTANCE5-MCP.md) - MCP Server (1-2 pages)
- [INSTANCE6-MONITORING.md](./INSTANCE6-MONITORING.md) - Monitoring & Testing (1-2 pages)

#### Architecture & Infrastructure
- [ARCHITECTURE.md](./ARCHITECTURE.md) - **Comprehensive 200GB architecture** (consolidates CLAUDE_ENTERPRISE + CLOUD-ARCHITECTURE-PLAN + 200GB_SOLUTION_SUMMARY)
- [TERRAFORM.md](./TERRAFORM.md) - Infrastructure as code
- [RUNPOD.md](./RUNPOD.md) - Runpod GPU rental strategy

#### AI Agent Guidance
- [AI-AGENTS.md](./AI-AGENTS.md) - AI agent instructions, NEVER/ALWAYS rules
- [BOUNDARIES.md](./BOUNDARIES.md) - Instance boundary enforcement

#### Project Management
- [PROJECT-STATUS.md](./PROJECT-STATUS.md) - Current project status
- [DELIVERY-MANIFEST.md](./DELIVERY-MANIFEST.md) - Deliverable tracking

---

### docs/ Directory Structure

```
docs/
├── instances/                  # Detailed instance-specific docs
│   ├── instance1-storage/
│   │   ├── README.md           # Detailed implementation guide
│   │   ├── gcs-configuration.md  (to be created)
│   │   ├── parquet-schema.md     (to be created)
│   │   └── troubleshooting.md    (to be created)
│   ├── instance2-embeddings/
│   │   ├── README.md
│   │   └── ... (similar structure)
│   ├── instance3-weaviate/
│   ├── instance4-api/
│   ├── instance5-mcp/
│   └── instance6-monitoring/
│
├── corpus-analysis/            # ⭐ Corpus investigation (46GB analyzed)
│   ├── README.md               # Investigation overview & roadmap
│   ├── 00-investigation-methodology-spec.md  # Reproducible methodology
│   ├── 00-corpus-overview.md   # Full corpus statistics
│   ├── 01-archive-section-analysis.md        # 4.3GB theory (15,637 files)
│   ├── 02-history-section-spec.md            # 33GB historical (ETOL, EROL, Other)
│   ├── 03-subject-section-spec.md            # 8.9GB thematic content
│   ├── 04-glossary-section-spec.md           # 62MB (~2,500 entities)
│   ├── 05-reference-section-spec.md          # 460MB non-Marxist authors
│   └── 06-metadata-unified-schema.md         # 5-layer metadata model (85%+ coverage)
│
├── architecture/               # Architecture documentation
│   ├── system-overview.md      (to be created)
│   ├── infrastructure.md       (to be created)
│   ├── storage-strategy.md     (to be created)
│   ├── interface-contracts.md  (to be created)
│   └── diagrams/               (architecture diagrams)
│
├── processes/                  # Process documentation
│   ├── git-workflow.md         ✅ Exists
│   ├── rfc-process.md          (to be created)
│   ├── testing-strategy.md     (to be created)
│   └── deployment.md           (to be created)
│
├── rfc/                        # Request for Comments
│   ├── RFC-TEMPLATE.md         ✅ Exists
│   └── RFC-001-embedding-batch-size.md  ✅ Exists
│
└── decisions/                  # Architecture Decision Records
    └── adr-template.md         (to be created)
```

---

### specs/ Directory (Formal Specifications)

**Status**: To be reorganized with consistent naming

**Current**:
- [INDEX.md](./specs/INDEX.md) - Master specification index
- [00-ARCHITECTURE-SPEC.md](./specs/00-ARCHITECTURE-SPEC.md) - System architecture
- [02-DOCUMENT-PROCESSING-SPEC.md](./specs/02-DOCUMENT-PROCESSING-SPEC.md) - Processing spec (v2.0 - corpus-informed)
- [03-RAG-INGESTION-SPEC.md](./specs/03-RAG-INGESTION-SPEC.md) - RAG ingestion
- [04-QUERY-INTERFACE-SPEC.md](./specs/04-QUERY-INTERFACE-SPEC.md) - Query interface
- [05-MCP-INTEGRATION-SPEC.md](./specs/05-MCP-INTEGRATION-SPEC.md) - MCP integration
- [06-TESTING-VALIDATION-SPEC.md](./specs/06-TESTING-VALIDATION-SPEC.md) - Testing
- [07-chunking-strategies-spec.md](./specs/07-chunking-strategies-spec.md) - ⭐ 4 adaptive chunking strategies
- [08-knowledge-graph-spec.md](./specs/08-knowledge-graph-spec.md) - ⭐ Hybrid retrieval architecture

**Planned Reorganization**:
- [01-STORAGE-PIPELINE.md](./specs/01-STORAGE-PIPELINE.md) - Consolidated storage spec
- [02-EMBEDDINGS.md](./specs/02-EMBEDDINGS.md) - Embeddings spec (extract from RAG-INGESTION)
- [03-VECTOR-DB.md](./specs/03-VECTOR-DB.md) - Weaviate spec (extract from RAG-INGESTION)
- [04-API.md](./specs/04-API.md) - Rename from QUERY-INTERFACE
- [05-MCP.md](./specs/05-MCP.md) - Rename from MCP-INTEGRATION
- [06-TESTING.md](./specs/06-TESTING.md) - Rename from TESTING-VALIDATION

---

### planning/ Directory - Project Planning & Issues

**Purpose**: Centralized project tracking, issues, and development strategies (accessible to AI agents)

#### Main Index
- [planning/README.md](./planning/README.md) - Planning directory overview

#### Active Projects
- [planning/projects/refactoring-code-complexity.md](./planning/projects/refactoring-code-complexity.md) - 9 components (1/9 complete)
- [planning/projects/corpus-analysis.md](./planning/projects/corpus-analysis.md) - ✅ Complete
- [planning/projects/documentation-reorganization.md](./planning/projects/documentation-reorganization.md) - ✅ Complete

#### Development Strategies
- [planning/PARALLEL-REFACTORING-STRATEGY.md](./planning/PARALLEL-REFACTORING-STRATEGY.md) - 4-wave parallel execution plan
- [planning/WORKFLOW-VALIDATION.md](./planning/WORKFLOW-VALIDATION.md) - CI/CD testing results

#### Refactoring Issues (Scripts)
- [planning/issues/refactor-check-conflicts-chain-of-responsibility.md](./planning/issues/refactor-check-conflicts-chain-of-responsibility.md)
- [planning/issues/refactor-check-boundaries-specification-pattern.md](./planning/issues/refactor-check-boundaries-specification-pattern.md) - ✅ Complete
- [planning/issues/refactor-check-interfaces-visitor-pattern.md](./planning/issues/refactor-check-interfaces-visitor-pattern.md)
- [planning/issues/refactor-instance-map-command-pattern.md](./planning/issues/refactor-instance-map-command-pattern.md)
- [planning/issues/refactor-instance-recovery-template-method.md](./planning/issues/refactor-instance-recovery-template-method.md)

#### Refactoring Issues (Metadata Pipeline)
- [planning/issues/refactor-metadata-unified-schema.md](./planning/issues/refactor-metadata-unified-schema.md) - 5-layer model, 40+ fields
- [planning/issues/refactor-metadata-extraction-pipeline.md](./planning/issues/refactor-metadata-extraction-pipeline.md) - Multi-source extraction
- [planning/issues/refactor-glossary-entity-linker.md](./planning/issues/refactor-glossary-entity-linker.md) - Entity linking
- [planning/issues/refactor-section-specific-extractors.md](./planning/issues/refactor-section-specific-extractors.md) - Archive, ETOL, EROL, Subject

#### Documentation Issues
- [planning/issues/delete-deprecated-root-documentation.md](./planning/issues/delete-deprecated-root-documentation.md) - ✅ Complete
- [planning/issues/reorganize-specs-consistent-naming.md](./planning/issues/reorganize-specs-consistent-naming.md) - Partial
- [planning/issues/update-cross-references-verify-links.md](./planning/issues/update-cross-references-verify-links.md)

---

### .github/ Directory - GitHub Configuration

#### Workflows (CI/CD)
- [.github/workflows/instance-tests.yml](./.github/workflows/instance-tests.yml) - Instance boundary testing
- [.github/workflows/conflict-detection.yml](./.github/workflows/conflict-detection.yml) - PR conflict detection
- [.github/workflows/daily-integration.yml](./.github/workflows/daily-integration.yml) - Daily integration tests
- [.github/workflows/release.yml](./.github/workflows/release.yml) - Release automation

#### Templates
- [.github/pull_request_template.md](./.github/pull_request_template.md) - PR template with instance validation
- [.github/ISSUE_TEMPLATE/bug_report.md](./.github/ISSUE_TEMPLATE/bug_report.md) - Bug report template
- [.github/ISSUE_TEMPLATE/integration_failure.md](./.github/ISSUE_TEMPLATE/integration_failure.md) - Integration failure template

---

## 📚 Documentation by Topic

### Getting Started
1. [README.md](./README.md) - Project overview
2. [START_HERE.md](./START_HERE.md) - Navigation hub
3. [CONTRIBUTING.md](./CONTRIBUTING.md) - How to contribute
4. [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

### Corpus Analysis & Data Architecture
**Essential reading for understanding the data foundation** (46GB analyzed, 55,753 documents)

**Key Resources**:
1. [docs/corpus-analysis/06-metadata-unified-schema.md](./docs/corpus-analysis/06-metadata-unified-schema.md) - **5-layer metadata model** (85%+ author coverage)
2. [specs/07-chunking-strategies-spec.md](./specs/07-chunking-strategies-spec.md) - **4 adaptive chunking strategies** based on document structure
3. [specs/08-knowledge-graph-spec.md](./specs/08-knowledge-graph-spec.md) - **Knowledge graph architecture** for hybrid retrieval

**Section-Specific Analyses** (Implementation-ready specs):
- [docs/corpus-analysis/01-archive-section-analysis.md](./docs/corpus-analysis/01-archive-section-analysis.md) - Archive (4.3GB, 15,637 files)
- [docs/corpus-analysis/02-history-section-spec.md](./docs/corpus-analysis/02-history-section-spec.md) - History: ETOL, EROL, Other (33GB, 33,190 files)
- [docs/corpus-analysis/03-subject-section-spec.md](./docs/corpus-analysis/03-subject-section-spec.md) - Subject (8.9GB, 2,259 files)
- [docs/corpus-analysis/04-glossary-section-spec.md](./docs/corpus-analysis/04-glossary-section-spec.md) - Glossary (~2,500 entities)
- [docs/corpus-analysis/05-reference-section-spec.md](./docs/corpus-analysis/05-reference-section-spec.md) - Reference (460MB, 4,867 files)

**Methodology & Overview**:
- [docs/corpus-analysis/README.md](./docs/corpus-analysis/README.md) - Investigation roadmap
- [docs/corpus-analysis/00-investigation-methodology-spec.md](./docs/corpus-analysis/00-investigation-methodology-spec.md) - Reproducible methodology
- [docs/corpus-analysis/00-corpus-overview.md](./docs/corpus-analysis/00-corpus-overview.md) - Full corpus statistics

### For AI Agents (Instance-Specific)
1. Choose your instance guide (INSTANCE1-6)
2. Read [AI-AGENTS.md](./AI-AGENTS.md) for rules
3. Read [BOUNDARIES.md](./BOUNDARIES.md) for your territory
4. Check `docs/instances/instanceX/` for detailed docs

### Architecture & Design
1. [ARCHITECTURE.md](./ARCHITECTURE.md) - **START HERE**
2. [specs/00-ARCHITECTURE-SPEC.md](./specs/00-ARCHITECTURE-SPEC.md) - Formal spec
3. `docs/architecture/` - Detailed architecture docs
4. [TERRAFORM.md](./TERRAFORM.md) - Infrastructure

### Implementation Specifications
1. [specs/INDEX.md](./specs/INDEX.md) - Spec overview
2. Instance-specific specs in `specs/`
3. Interface contracts in `src/mia_rag/interfaces/contracts.py`

### Testing & Quality
1. [specs/06-TESTING.md](./specs/06-TESTING.md) - Testing approach
2. [specs/06-TESTING-VALIDATION-SPEC.md](./specs/06-TESTING-VALIDATION-SPEC.md) - Formal testing spec
3. `docs/processes/testing-strategy.md` (to be created)

### Project Management
1. [PROJECT-STATUS.md](./PROJECT-STATUS.md) - Current status
2. [DELIVERY-MANIFEST.md](./DELIVERY-MANIFEST.md) - Deliverables
3. `work-logs/instance{1-6}/` - Async work logs

---

## 🗺️ Navigation Patterns

### "I'm a new AI agent, where do I start?"
```
START_HERE.md
  → Identify your instance (1-6)
  → Go to INSTANCEX-*.md
  → Read AI-AGENTS.md for rules
  → Read BOUNDARIES.md for your territory
  → Read specs/0X-*.md for your formal spec
  → Start implementing!
```

### "I need to understand the corpus structure and data"
```
START_HERE.md → "I need to understand the corpus structure"
  → docs/corpus-analysis/06-metadata-unified-schema.md (5-layer metadata model)
  → specs/07-chunking-strategies-spec.md (4 adaptive strategies)
  → specs/08-knowledge-graph-spec.md (hybrid retrieval)
  → Section analyses for implementation details:
    - 01-archive-section-analysis.md (4.3GB theory)
    - 02-history-section-spec.md (33GB ETOL/EROL/Other)
    - 03-subject-section-spec.md (8.9GB thematic)
    - 04-glossary-section-spec.md (~2,500 entities)
    - 05-reference-section-spec.md (460MB non-Marxist)
```

### "I need to understand the architecture"
```
ARCHITECTURE.md (comprehensive overview)
  → docs/architecture/infrastructure.md (GCP details)
  → docs/architecture/storage-strategy.md (data formats)
  → docs/architecture/interface-contracts.md (APIs)
  → TERRAFORM.md (infrastructure as code)
```

### "I need to coordinate with another instance"
```
1. Check BOUNDARIES.md (what they own)
2. Read src/mia_rag/interfaces/contracts.py (their API)
3. Check their work-logs/instanceX/ (their progress)
4. Submit RFC if interface change needed
```

### "I need to test my code"
```
specs/06-TESTING.md (testing approach)
  → docs/instances/instanceX/README.md (instance-specific tests)
  → specs/06-TESTING-VALIDATION-SPEC.md (formal requirements)
  → tests/unit/instanceX_*/ (write your tests here)
```

---

## 🚨 Common Questions

**Q: Which doc is the "source of truth" for X?**
A: See [DOCUMENTATION-CONSISTENCY.md](./DOCUMENTATION-CONSISTENCY.md) (if exists) or:
- Architecture → `ARCHITECTURE.md`
- Instance boundaries → `BOUNDARIES.md`
- Specs → `specs/` directory
- Infrastructure → `TERRAFORM.md`

**Q: I found duplicate information, which is correct?**
A: Root-level files are canonical. If conflict exists, follow this precedence:
1. `ARCHITECTURE.md` (architecture decisions)
2. `specs/` (formal specifications)
3. `INSTANCEX-*.md` (instance-specific guidance)
4. `docs/` (detailed reference)

**Q: Where do I document my work?**
A:
- Code → docstrings and type hints
- Architecture decisions → Submit RFC in `docs/rfc/`
- Progress → `work-logs/instanceX/`
- Detailed implementation → `docs/instances/instanceX/`

**Q: How do I propose a change?**
A:
1. Small change → Submit PR directly
2. Interface change → RFC in `docs/rfc/` (24h review)
3. Architecture change → Discuss in `work-logs/questions.md` first

---

## 📝 Documentation Status

| Category | Count | Status |
|----------|-------|--------|
| Instance guides (root) | 6 | ✅ Complete |
| Instance detailed docs | 6 | 📝 Stubs created |
| Corpus analysis docs | 9 | ✅ Complete (46GB analyzed) |
| Architecture docs | 1 | ✅ Consolidated |
| Specs | 9 | 🔄 To be reorganized |
| Process docs | 1 | 📝 More needed |
| RFCs | 1 example | ✅ Template exists |

**Legend**:
- ✅ Complete
- 🔄 In progress / needs reorganization
- 📝 Stub / placeholder created
- ❌ Not started

---

## 🔄 Planned Updates

1. **Reorganize specs/** - Consistent naming (01-06 with hyphens)
2. **Create detailed architecture docs** - Move content to `docs/architecture/`
3. **Expand instance docs** - Fill in implementation details as development proceeds
4. **Delete legacy files** - ✅ Complete - Deprecated files deleted (consolidated into ARCHITECTURE.md)

---

**Questions about documentation?** Check [START_HERE.md](./START_HERE.md) or create an issue.

**Last Updated**: 2025-11-08
