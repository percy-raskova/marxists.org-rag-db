# Instance 5: MCP Server Integration

**Quick Start Guide for AI Agent Working on MCP Module**

## 🎯 Your Role

You are responsible for **Model Context Protocol (MCP) server** - exposing the RAG system to Claude via standardized tools and resources.

**Status**: ✅ Ready for development (waiting on Instance 4 API endpoints)

---

## 📁 Your Territory (OWNED PATHS)

```
✅ YOU CAN MODIFY:
src/mia_rag/mcp/              # MCP server, tools, resources
tests/unit/instance5_mcp/     # Your unit tests
docs/instances/instance5-mcp/ # Your detailed docs

❌ YOU CANNOT MODIFY:
Any other directories (will cause merge conflicts!)
```

---

## 🔗 Dependencies

**You depend on**:
- Instance 4 (api) for query processing
  - Uses: `QueryInterface.semantic_search()`, `QueryInterface.filter_search()`

**Who depends on you**:
- Instance 6 (monitoring) tracks tool usage metrics
- End users interact with you via Claude Desktop/API

---

## 🎨 What You Build

### Core Interfaces (in `src/mia_rag/interfaces/contracts.py`)

```python
class MCPServerInterface(Protocol):
    """Contract that other instances use"""
    def register_tool(self, tool: Tool) -> None
    def register_resource(self, resource: Resource) -> None
    def handle_request(self, request: MCPRequest) -> MCPResponse

class ToolInterface(Protocol):
    """Tool definition contract"""
    def execute(self, params: dict) -> ToolResult
    def get_schema(self) -> ToolSchema
```

### Your Deliverables

1. **MCP Server** (`src/mia_rag/mcp/server.py`)
   - Implement MCP protocol (stdio transport)
   - Tool registration and dispatch
   - Resource provider for documents
   - Error handling and logging

2. **RAG Tools** (`src/mia_rag/mcp/tools/`)
   - `search_marxist_theory(query, n_results)` - Semantic search
   - `find_by_author(author, work_title)` - Author-specific search
   - `get_historical_context(time_period, topic)` - Temporal search
   - `get_document(doc_id)` - Full document retrieval

3. **Resource Providers** (`src/mia_rag/mcp/resources.py`)
   - `marxist://documents/{id}` - Document URIs
   - `marxist://authors/{name}` - Author collections
   - `marxist://search/{query}` - Cached search results

4. **Integration Config** (`~/.config/claude/config.json`)
   - MCP server registration
   - Environment variables for API endpoint
   - Logging configuration

---

## ⚡ Quick Commands

```bash
# Your development workflow
mise run test:instance5           # Run your tests only
mise run quality:instance5        # Lint your code
mise run mcp:dev                  # Start MCP server (stdio)
mise run mcp:test-tools           # Test all tools

# Check your boundaries
python scripts/check_boundaries.py --instance mcp

# Submit work
git add src/mia_rag/mcp/
git commit -m "feat(mcp): implement search_marxist_theory tool"
git push origin mcp-dev
```

---

## 📚 Essential Corpus Analysis Reading

**CRITICAL**: MCP tools should leverage corpus patterns for intelligent query expansion. Read these BEFORE tool design:

### Required Reading
1. **[Knowledge Graph Spec](./specs/08-knowledge-graph-spec.md)** ⭐ ESSENTIAL
   - **Query expansion patterns** from 5k-10k cross-references:
     - Entity-based: "Lenin" → expand to works by Lenin + works mentioning Lenin
     - Temporal: "1917" → works written in 1917 + works about 1917 events
     - Thematic: "imperialism" → works tagged + Glossary definition + related subjects
   - **Hybrid retrieval tools**: Expose both vector and graph capabilities to Claude
   - **Multi-hop queries**: "Find Lenin's works on imperialism, then find responses by other theorists"

2. **[Glossary Analysis](./docs/corpus-analysis/04-glossary-section-spec.md)**
   - **~2,500 entities** enable "What is X?" definition lookup tool
   - Separate MCP tool for glossary definitions vs. full semantic search
   - **80-95% cross-references** - use for automatic query enrichment

3. **[Subject Analysis](./docs/corpus-analysis/03-subject-section-spec.md)**
   - **8 subject categories** (theoretical, economic, political, etc.) for faceted search
   - **64% link to /archive/** - subject browsing as navigation aid
   - MCP resource for subject taxonomy exploration

**Why This Matters**: Your MCP tools are Claude's interface to RAG capabilities. Well-designed tools leveraging corpus patterns enable Claude to perform complex research tasks (e.g., "trace the evolution of the theory of imperialism from Hobson to Lenin to Mao").

**Tool Design Hint**: Consider 4-5 specialized tools (semantic search, entity lookup, definition query, subject browse, related works) rather than one generic search tool.

---

## 📋 Development Checklist

- [ ] **Read knowledge graph spec and glossary/subject analyses** (see Essential Reading above) ⭐
- [ ] Read `docs/instances/instance5-mcp/README.md` (your detailed guide)
- [ ] Read [MCP Specification](https://modelcontextprotocol.io/docs) (official docs)
- [ ] Read `specs/05-MCP.md` (formal specification)
- [ ] Install MCP Python SDK (`pip install mcp`)
- [ ] Implement `MCPServerInterface` in `src/mia_rag/mcp/server.py`
- [ ] Implement all 4 RAG tools in `src/mia_rag/mcp/tools/`
- [ ] Test tools via Claude Desktop
- [ ] Document tool schemas in work logs

---

## 🚨 Critical Rules

### NEVER:
- ❌ Modify code outside `src/mia_rag/mcp/`
- ❌ Change `MCPServerInterface` without RFC
- ❌ Return >10k tokens in one tool call (Claude limits!)
- ❌ Skip input validation (sanitize tool parameters)
- ❌ Hardcode API endpoints (use environment variables)

### ALWAYS:
- ✅ Use TDD (write tests first!)
- ✅ Validate tool parameters with Pydantic
- ✅ Return structured data (not plain text)
- ✅ Log tool usage for analytics
- ✅ Handle API errors gracefully

---

## 📚 Essential Documentation

**Start Here**:
1. `docs/instances/instance5-mcp/README.md` - Your detailed guide
2. [MCP Docs](https://modelcontextprotocol.io/docs) - Official specification
3. `specs/05-MCP.md` - Formal specification

**Reference**:
- [MCP Python SDK](https://github.com/anthropics/python-mcp-sdk) - Code examples
- `docs/instances/instance4-api/README.md` - API contract
- `specs/06-TESTING.md` - Testing without Claude Desktop

**Communication**:
- `work-logs/instance5/` - Your async work log
- `docs/rfc/` - Submit RFCs for interface changes (24h review)

---

## 🎯 Success Criteria

You're done when:
- [ ] All tests pass (>80% coverage)
- [ ] Pre-commit hooks pass
- [ ] `MCPServerInterface` implemented and documented
- [ ] All 4 tools working in Claude Desktop
- [ ] Tool schemas validated
- [ ] Resources accessible via URIs
- [ ] Work log updated

---

## 💡 Pro Tips

**Tool Design**:
- Keep tool parameters simple (≤5 params)
- Return structured JSON (not markdown)
- Include citations in results
- Expected: <3 second tool execution

**Claude Integration**:
- Test in Claude Desktop first (easier debugging)
- Use `mcp-inspector` for protocol debugging
- Check Claude logs: `~/.config/claude/logs/`

**Debugging**:
- MCP inspector: `npx @anthropics/mcp-inspector src/mia_rag/mcp/server.py`
- Test stdio: `echo '{"method":"tools/list"}' | python -m mia_rag.mcp.server`
- Check tool schemas: Valid JSON schema required

---

**Need help?** Check `docs/instances/instance5-mcp/troubleshooting.md`

**Last Updated**: 2025-11-08
