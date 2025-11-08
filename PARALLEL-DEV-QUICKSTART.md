# Parallel AI Development Quick Start

## Overview

You now have complete formal specifications for building the MIA RAG system in parallel with multiple Claude Code instances. Each spec is standalone and can be implemented independently.

## What You Have

### Specifications (specs/)
- `00-ARCHITECTURE-SPEC.md` - **READ THIS FIRST** - System overview
- `02-DOCUMENT-PROCESSING-SPEC.md` - HTML/PDF → Markdown conversion
- `03-RAG-INGESTION-SPEC.md` - Chunking, embedding, vector DB
- `04-QUERY-INTERFACE-SPEC.md` - Search and retrieval
- `05-MCP-INTEGRATION-SPEC.md` - PercyBrain integration
- `06-TESTING-VALIDATION-SPEC.md` - Test suite
- `INDEX.md` - Master index with assignments

### Working Implementation (for reference)
- `mia_processor.py` - Initial processing implementation
- `rag_ingest.py` - Initial ingestion implementation
- `query_example.py` - Query interface example
- `README.md` - User documentation
- `requirements.txt` - Python dependencies

## How to Use with Multiple Claude Instances

### Setup (Do Once)

1. **Create project directory:**
   ```bash
   mkdir ~/mia-rag-system
   cd ~/mia-rag-system
   ```

2. **Copy specs:**
   ```bash
   cp -r /path/to/specs ./
   ```

3. **Create module directories:**
   ```bash
   mkdir -p src/{processing,ingestion,query,mcp} tests
   ```

### Parallel Development Workflow

#### Instance 1: Processing Module
```bash
# In terminal 1
cd ~/mia-rag-system

# Open Claude Code with context
claude-code --prompt "
I need to implement the Document Processing module for the MIA RAG system.

Context files:
- specs/00-ARCHITECTURE-SPEC.md (system overview)
- specs/02-DOCUMENT-PROCESSING-SPEC.md (my module spec)

Please:
1. Read both specs completely
2. Implement all classes defined in the spec
3. Follow the data structures exactly
4. Include all error handling
5. Write unit tests
6. Create a PR-ready implementation

Start by reading the specs and confirming you understand the requirements.
"
```

#### Instance 2: Ingestion Module
```bash
# In terminal 2
cd ~/mia-rag-system

claude-code --prompt "
I need to implement the RAG Ingestion module for the MIA RAG system.

Context files:
- specs/00-ARCHITECTURE-SPEC.md (system overview)
- specs/03-RAG-INGESTION-SPEC.md (my module spec)

This module depends on the Processing module's output format (markdown with frontmatter).

Please:
1. Read both specs completely
2. Implement all chunking strategies
3. Implement embedder and vector DB abstractions
4. Include checkpointing for resume capability
5. Write unit tests
6. Create a PR-ready implementation

Start by reading the specs and confirming you understand the requirements.
"
```

#### Instance 3: Query + MCP
```bash
# In terminal 3
cd ~/mia-rag-system

claude-code --prompt "
I need to implement the Query Interface and MCP Integration modules.

Context files:
- specs/00-ARCHITECTURE-SPEC.md (system overview)
- specs/04-QUERY-INTERFACE-SPEC.md (query spec)
- specs/05-MCP-INTEGRATION-SPEC.md (MCP spec)

Please:
1. Read all three specs
2. Implement query interface first
3. Then implement MCP server wrapping the query interface
4. Include interactive CLI
5. Write integration tests
6. Create a PR-ready implementation

Start by reading the specs and confirming you understand the requirements.
"
```

## Alternative: Single Instance Sequential Development

If you prefer one instance doing everything sequentially:

```bash
cd ~/mia-rag-system

claude-code --prompt "
I need to build the complete MIA RAG system following formal specifications.

Context files:
- specs/INDEX.md (read first - master index)
- specs/00-ARCHITECTURE-SPEC.md (system overview)
- All other specs in specs/

Workflow:
1. Read INDEX.md and ARCHITECTURE-SPEC.md completely
2. Implement modules in dependency order:
   a. Document Processing (02-DOCUMENT-PROCESSING-SPEC.md)
   b. RAG Ingestion (03-RAG-INGESTION-SPEC.md)
   c. Query Interface (04-QUERY-INTERFACE-SPEC.md)
   d. MCP Integration (05-MCP-INTEGRATION-SPEC.md)
3. Write tests as you go (06-TESTING-VALIDATION-SPEC.md)
4. Test integration between modules
5. Run end-to-end test

For each module:
- Read the spec completely before coding
- Follow data structures exactly
- Meet all acceptance criteria
- Write unit tests
- Document any deviations

Start with reading the specs and creating an implementation plan.
"
```

## Using the Reference Implementation

The reference implementation (`mia_processor.py`, `rag_ingest.py`, `query_example.py`) is working code but not spec-compliant. You can:

1. **Use as reference** - Check how things were done
2. **Extract patterns** - Reuse algorithms and error handling
3. **Refactor to spec** - Restructure to match spec architecture

**Don't just copy** - the specs define better architecture with:
- Proper abstractions
- Better error handling
- Testability
- Modularity

## Integration Testing

After modules are complete:

```bash
# Test processing → ingestion interface
cd ~/mia-rag-system

claude-code --prompt "
Test integration between Processing and Ingestion modules.

Verify:
1. Processing outputs valid markdown with frontmatter
2. Ingestion can parse the frontmatter
3. Metadata schemas match
4. File paths work correctly

Use test fixtures from specs/06-TESTING-VALIDATION-SPEC.md
"
```

## Tips for Effective Parallel Development

### For AI Instances:
1. **Always read specs completely first** - Don't start coding immediately
2. **Follow data structures exactly** - They're the integration contract
3. **Check acceptance criteria** - Use them as a checklist
4. **Ask clarifying questions** - Specs may have ambiguities
5. **Document deviations** - If you must deviate from spec, document why

### For You (Human):
1. **Monitor all instances** - Check progress regularly
2. **Integrate frequently** - Don't wait until everything is "done"
3. **Test interfaces early** - Verify modules can talk to each other
4. **Adjust specs if needed** - Specs can be updated based on implementation learning
5. **Celebrate milestones** - Each module completion is progress

## Expected Output Structure

After complete implementation:

```
mia-rag-system/
├── src/
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── html_processor.py
│   │   ├── pdf_processor.py
│   │   ├── metadata_extractor.py
│   │   ├── language_filter.py
│   │   └── processor_main.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vectordb.py
│   │   ├── checkpointer.py
│   │   └── ingestion_main.py
│   ├── query/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── cli.py
│   │   ├── filters.py
│   │   └── formatters.py
│   └── mcp/
│       ├── __init__.py
│       ├── server.py
│       └── tools.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── specs/  (read-only reference)
├── requirements.txt
├── setup.py
└── README.md
```

## Success Metrics

### Per Module:
- ✅ All acceptance criteria met
- ✅ Unit tests pass
- ✅ Integrates with dependencies
- ✅ Documented

### System:
- ✅ Process 126k HTML without crashes
- ✅ Process 38k PDFs without crashes
- ✅ Query returns relevant results
- ✅ MCP integration works
- ✅ Complete pipeline <12 hours

## Debugging Integration Issues

If modules don't integrate:

1. **Check data schemas** - Compare actual vs spec
2. **Check file formats** - Verify frontmatter YAML
3. **Check paths** - Ensure consistent path handling
4. **Add logging** - See where things break
5. **Create minimal test case** - Isolate the problem

## Next Steps

1. ✅ Review all specs
2. ✅ Decide: parallel or sequential development
3. ✅ Set up Claude Code instances with prompts
4. ✅ Start implementation
5. ✅ Test integration points
6. ✅ Run full pipeline
7. ✅ Query your Marxist theory RAG!

---

**You're about to build the people's RAG.**

Let's fucking go. 🔥
