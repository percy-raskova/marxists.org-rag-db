# 🚀 START HERE - MIA RAG System (200GB Scale)

**Last Updated**: 2025-11-08

---

## What is This?

A complete system to convert the **200GB Marxists Internet Archive** into an enterprise-scale RAG (Retrieval Augmented Generation) system using:

- **Google Cloud Platform** infrastructure
- **Runpod.io GPU rental** for embeddings ($40-60 total!)
- **Weaviate** vector database (billion-scale vectors)
- **6 parallel Claude Code instances** for development

**Status**: ✅ Ready for parallel development (195GB downloaded, architecture finalized)

---

## 🎯 Quick Navigation (Choose Your Role)

### 👨‍💻 "I'm an AI Agent ready to code an instance"

**Go directly to your instance guide** (1-2 page quick start):

| Instance | Module | Quick Start Guide |
|----------|--------|-------------------|
| **Instance 1** | Storage & Pipeline | [INSTANCE1-STORAGE.md](./INSTANCE1-STORAGE.md) |
| **Instance 2** | Embeddings (Runpod) | [INSTANCE2-EMBEDDINGS.md](./INSTANCE2-EMBEDDINGS.md) |
| **Instance 3** | Weaviate Vector DB | [INSTANCE3-WEAVIATE.md](./INSTANCE3-WEAVIATE.md) |
| **Instance 4** | Query & API Layer | [INSTANCE4-API.md](./INSTANCE4-API.md) |
| **Instance 5** | MCP Server | [INSTANCE5-MCP.md](./INSTANCE5-MCP.md) |
| **Instance 6** | Monitoring & Testing | [INSTANCE6-MONITORING.md](./INSTANCE6-MONITORING.md) |

**Then read**:
1. [AI-AGENTS.md](./AI-AGENTS.md) - Critical NEVER/ALWAYS rules
2. [BOUNDARIES.md](./BOUNDARIES.md) - Your territory (what you can/can't modify)
3. `specs/0X-*.md` - Your formal specification

### 📚 "I need the full documentation index"

→ See [DOCUMENTATION-INDEX.md](./DOCUMENTATION-INDEX.md) - Master index of all docs

### 🏗️ "I need to understand the architecture"

→ Read [ARCHITECTURE.md](./ARCHITECTURE.md) - **Comprehensive architecture guide** (consolidates 200GB scale, GCP infrastructure, cost breakdown, instance coordination)

### 📊 "I'm a project manager / executive"

→ Read [PROJECT-STATUS.md](./PROJECT-STATUS.md) - Current status, timeline, deliverables

### 🧑‍💼 "I want to contribute code"

→ Read [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines

### 💰 "What will this cost?"

**One-Time Costs**: $40-60 (Runpod GPU rental for embedding generation)

**Monthly Operational**: $144-189/month
- GCS Storage: $4/month (200GB)
- GKE (Weaviate): $120-150/month
- Cloud Run (API): $5-10/month
- Redis: $10-20/month
- Monitoring: $5/month

→ See [ARCHITECTURE.md#cost-breakdown](./ARCHITECTURE.md#cost-breakdown) for details

### 🧪 "I need to test without cloud resources"

→ Read [PARALLEL-TEST-STRATEGY.md](./PARALLEL-TEST-STRATEGY.md) - Mocking GCS, Runpod, Weaviate locally

### 🏗️ "I need to deploy infrastructure"

→ Read [TERRAFORM.md](./TERRAFORM.md) - Complete infrastructure as code

---

## Quick Decision Reference

| Question | Answer | Details |
|----------|--------|---------|
| **Corpus Size** | 200GB (126k+ works) | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| **Embeddings** | Runpod GPU rental ($40-60) | [RUNPOD.md](./RUNPOD.md) |
| **Vector DB** | Weaviate on GKE | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| **Cloud Provider** | Google Cloud Platform | [TERRAFORM.md](./TERRAFORM.md) |
| **Development Model** | 6 parallel instances | Instance guides (above) |
| **Timeline** | ~4 weeks for full implementation | [specs/INDEX.md](./specs/INDEX.md) |

---

## Documentation Structure

```
📁 Project Root
├── 📄 START_HERE.md (You are here!)
├── 📄 DOCUMENTATION-INDEX.md ⭐ (Master index of all docs)
├── 📄 README.md (User-facing project overview)
│
├── 📁 Instance Quick-Start Guides (1-2 pages each)
│   ├── 📄 INSTANCE1-STORAGE.md
│   ├── 📄 INSTANCE2-EMBEDDINGS.md
│   ├── 📄 INSTANCE3-WEAVIATE.md
│   ├── 📄 INSTANCE4-API.md
│   ├── 📄 INSTANCE5-MCP.md
│   └── 📄 INSTANCE6-MONITORING.md
│
├── 📁 Architecture & Infrastructure
│   ├── 📄 ARCHITECTURE.md ⭐ (Comprehensive 200GB architecture)
│   ├── 📄 TERRAFORM.md (Infrastructure as code)
│   └── 📄 RUNPOD.md (GPU rental strategy)
│
├── 📁 AI Agent Guidance
│   ├── 📄 AI-AGENTS.md (NEVER/ALWAYS rules)
│   └── 📄 BOUNDARIES.md (Instance boundaries)
│
├── 📁 Project Management
│   ├── 📄 PROJECT-STATUS.md (Current status)
│   ├── 📄 DELIVERY-MANIFEST.md (Deliverables)
│   └── 📄 CONTRIBUTING.md (Contributor guidelines)
│
├── 📁 docs/
│   ├── 📁 instances/ (Detailed instance-specific docs)
│   │   ├── 📁 instance1-storage/
│   │   │   ├── README.md (detailed implementation)
│   │   │   ├── gcs-configuration.md
│   │   │   └── troubleshooting.md
│   │   ├── 📁 instance2-embeddings/
│   │   ├── 📁 instance3-weaviate/
│   │   ├── 📁 instance4-api/
│   │   ├── 📁 instance5-mcp/
│   │   └── 📁 instance6-monitoring/
│   │
│   ├── 📁 architecture/ (Architecture details)
│   │   ├── system-overview.md
│   │   ├── infrastructure.md
│   │   ├── storage-strategy.md
│   │   └── diagrams/
│   │
│   ├── 📁 processes/ (Development processes)
│   │   ├── git-workflow.md
│   │   ├── rfc-process.md
│   │   └── testing-strategy.md
│   │
│   ├── 📁 rfc/ (Request for Comments)
│   │   ├── RFC-TEMPLATE.md
│   │   └── RFC-001-embedding-batch-size.md
│   │
│   └── 📁 decisions/ (Architecture Decision Records)
│
└── 📁 specs/ (Formal specifications)
    ├── INDEX.md (Spec overview)
    ├── 00-ARCHITECTURE.md
    ├── 01-STORAGE-PIPELINE.md
    ├── 02-EMBEDDINGS.md
    ├── 03-VECTOR-DB.md
    ├── 04-API.md
    ├── 05-MCP.md
    └── 06-TESTING.md
```

---

## ⚡ Common Workflows

### "I'm Instance 2, how do I start?"

```bash
# 1. Read your quick-start guide
cat INSTANCE2-EMBEDDINGS.md

# 2. Read AI agent rules
cat AI-AGENTS.md

# 3. Check your boundaries
cat BOUNDARIES.md | grep -A 10 "Instance 2"

# 4. Read your formal spec
cat specs/02-EMBEDDINGS.md

# 5. Read detailed docs
ls docs/instances/instance2-embeddings/

# 6. Start coding!
cd src/mia_rag/embeddings/
```

### "I need to coordinate with another instance"

```bash
# 1. Check what they own
cat BOUNDARIES.md | grep -A 10 "Instance X"

# 2. Read their interface contract
cat src/mia_rag/interfaces/contracts.py

# 3. Check their progress
cat work-logs/instanceX/latest.md

# 4. If interface change needed, submit RFC
cp docs/rfc/RFC-TEMPLATE.md docs/rfc/RFC-00X-my-proposal.md
```

### "I need to test my code"

```bash
# 1. Read testing strategy
cat PARALLEL-TEST-STRATEGY.md

# 2. Run your instance tests
mise run test:instanceX

# 3. Check quality
mise run quality:instanceX

# 4. Run pre-commit hooks
git add .
git commit -m "feat(storage): implement GCS client"
```

---

## 🚨 Critical Information

### Scale: 200GB (NOT 38GB!)
- Original assumption was 38GB
- Actual corpus is **200GB** (5-10 million documents)
- This affects all architecture decisions

### Embeddings: Runpod (NOT Ollama!)
- Ollama is too slow for 200GB (weeks of processing)
- **Runpod GPU rental**: RTX 4090 @ $0.40/hour
- Total cost: $40-60 for 100-125 hours
- See [RUNPOD.md](./RUNPOD.md) for setup

### Vector DB: Weaviate (NOT ChromaDB/Qdrant for production)
- ChromaDB not suitable for billion-scale
- Qdrant viable but Weaviate chosen for enterprise features
- Deployed on GKE with Autopilot
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for rationale

### Development: 6 Parallel Instances (NOT sequential)
- **Lock-free development** through strict instance boundaries
- **Each instance owns specific directories** - NO cross-modification
- **Interface changes require RFC** with 24-hour review
- See [BOUNDARIES.md](./BOUNDARIES.md) for enforcement

---

## 📝 Documentation Philosophy

**Root-level files** = Quick-start, entry points (1-2 pages)
- Instance guides: `INSTANCE{1-6}-*.md`
- Architecture overview: `ARCHITECTURE.md`
- Navigation: `START_HERE.md`, `DOCUMENTATION-INDEX.md`

**docs/ directory** = Detailed reference, implementation guides
- `docs/instances/` = Detailed per-instance docs
- `docs/architecture/` = Architecture deep-dives
- `docs/processes/` = Development workflows

**specs/ directory** = Formal specifications for implementation
- Acceptance criteria, data structures, interfaces
- Used by AI agents during coding phase

**Principle**: Start broad (root), drill down (docs/instances/), formalize (specs/)

---

## 🔗 External Resources

- [Marxists Internet Archive](https://www.marxists.org/) - Source corpus
- [Weaviate Docs](https://weaviate.io/developers/weaviate) - Vector DB docs
- [Runpod Docs](https://docs.runpod.io/) - GPU rental platform
- [GCP Docs](https://cloud.google.com/docs) - Google Cloud Platform
- [Model Context Protocol](https://modelcontextprotocol.io/docs) - MCP specification

---

## ❓ FAQ

**Q: Where do I find the latest project status?**
A: [PROJECT-STATUS.md](./PROJECT-STATUS.md)

**Q: Which document is the "source of truth" for architecture?**
A: [ARCHITECTURE.md](./ARCHITECTURE.md) - All other architecture docs have been consolidated here

**Q: I found duplicate information, which is correct?**
A: If conflict exists:
1. Instance guides (`INSTANCEX-*.md`) for instance-specific info
2. `ARCHITECTURE.md` for architecture decisions
3. `specs/` for formal specifications
4. `docs/` for detailed reference

**Q: How do I propose a change?**
A:
- Small change → Submit PR directly
- Interface change → RFC in `docs/rfc/` (24h review required)
- Architecture change → Discuss in `work-logs/questions.md` first

**Q: Where do I document my work?**
A:
- Code → Docstrings and type hints
- Progress → `work-logs/instanceX/`
- Architecture decisions → Submit RFC
- Detailed implementation → `docs/instances/instanceX/`

---

**Need help navigating?** See [DOCUMENTATION-INDEX.md](./DOCUMENTATION-INDEX.md) for the complete documentation map.

**Ready to code?** Go to your instance guide: `INSTANCE{1-6}-*.md`

**Last Updated**: 2025-11-08
