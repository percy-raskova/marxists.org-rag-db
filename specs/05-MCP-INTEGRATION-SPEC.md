# MCP Integration Module Specification

**Version:** 1.0  
**Status:** SPECIFICATION  
**Module:** `src/mcp/`  
**Dependencies:** Architecture Spec 1.0, Query Interface Spec 1.0

## Overview

Exposes RAG system as MCP server tools for integration with PercyBrain and Claude.

## MCP Tools

### search_marxist_theory

```python
{
    "name": "search_marxist_theory",
    "description": "Search Marxist theory corpus for relevant passages",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "n_results": {"type": "integer", "default": 5},
            "author_filter": {"type": "string", "optional": true}
        }
    }
}
```

### find_author_works

```python
{
    "name": "find_author_works",
    "description": "List all works by a specific author",
    "inputSchema": {
        "type": "object",
        "properties": {
            "author": {"type": "string"},
            "limit": {"type": "integer", "default": 20}
        }
    }
}
```

### get_work_context

```python
{
    "name": "get_work_context",
    "description": "Get full context around a passage",
    "inputSchema": {
        "type": "object",
        "properties": {
            "chunk_id": {"type": "string"},
            "context_chunks": {"type": "integer", "default": 2}
        }
    }
}
```

## Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("marxist-theory")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="search_marxist_theory", ...),
        Tool(name="find_author_works", ...),
        Tool(name="get_work_context", ...)
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "search_marxist_theory":
        return await search_theory(arguments)
    # ...
```

## PercyBrain Integration

Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "marxist-theory": {
      "command": "python",
      "args": ["/path/to/mcp/server.py"],
      "env": {
        "VECTOR_DB_PATH": "./mia_vectordb/"
      }
    }
  }
}
```

## Acceptance Criteria

- [ ] MCP server responds to tool calls
- [ ] Tools return valid JSON
- [ ] Integration works with Claude
- [ ] Performance <1s per query

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial specification |
