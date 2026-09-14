---
name: nlweb-mcp-server
description: Expose NLWeb as an MCP (Model Context Protocol) server — JSON-RPC 2.0 endpoint at /mcp, the `ask` / `list_sites` / `who` tools, protocol revision negotiation, and integration with ChatGPT, Claude, Gemini, and other agent clients. Use when wiring NLWeb to an AI agent via MCP or building an MCP client that consumes an NLWeb site.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb MCP Server

## Before writing code

**Fetch live spec**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md (covers `/mcp` route alongside `/ask`).
2. Read `AskAgent/python/webserver/mcp_wrapper.py` in the live repo for the **exact JSON-RPC method list and tool schemas** — these change between releases.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-chatgpt-integration.md for the ChatGPT-specific wiring.
4. Fetch https://modelcontextprotocol.io/specification/ — it redirects to the **current** revision. Read the transport rules and the changelog there; never assume a revision from memory.
5. Web-search the latest release notes for any MCP-related changes — the wrapper file's own docstring warns "Backwards compatibility is not guaranteed."

## Conceptual Architecture

### How NLWeb Implements MCP

NLWeb is **already an MCP server** out of the box — same code, second binding. The `/mcp` route in `webserver/routes/mcp.py` accepts JSON-RPC 2.0 requests and re-uses the same `NLWebHandler` pipeline as `/ask`. No separate process, no extra config.

### Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/mcp` | POST, GET | Main JSON-RPC endpoint |
| `/mcp/{path}` | POST, GET | Path-scoped variant |
| `/mcp/health` | GET | Liveness check |

### MCP Protocol Revision

NLWeb advertises a dated MCP revision (e.g. `2026-07-28`) and the server name `nlweb-mcp-server`. **Never hard-code a revision string** — the one your build ships is whatever the installed NLWeb release advertises, and the one your client should send is whatever the spec currently defines.

Resolve it at implementation time:

1. Fetch https://modelcontextprotocol.io/specification/ for the current revision.
2. Read the installed NLWeb's `mcp_wrapper.py` for the revision *it* advertises.
3. If they differ, target the older of the two and note the gap — MCP revisions are not silently backward-compatible.

The transport has changed shape across revisions. The `2026-07-28` core is **stateless**: the `initialize` / `notifications/initialized` handshake and the `Mcp-Session-Id` header were removed from Streamable HTTP. Code written against a handshake-era revision will not match a stateless server, and vice versa — so confirm which model applies before writing client code.

### JSON-RPC Methods

`tools/list` and `tools/call` are stable across revisions and are the two you will actually use. Whether a handshake precedes them is revision-dependent:

| Method | Direction | Notes |
|--------|-----------|-------|
| `tools/list` | client → server | Returns the tool definitions |
| `tools/call` | client → server | Invoke a tool |
| `notifications/cancelled` | client → server | Cancel an in-flight tool call |
| `initialize` | client → server | Handshake — **removed in the stateless core**; present only on handshake-era revisions |
| `initialized` | client → server | Notification paired with `initialize`; same caveat |

Confirm the method list against the running server's `tools/list` response and the revision you resolved above.

(`prompts/list` and `prompts/get` appear in some docs but are not in `mcp_wrapper.py` at the time of writing — verify.)

### Tools Exposed

Three tools are advertised via `tools/list`:

#### 1. `ask` — the primary NL query

```json
{
  "name": "ask",
  "description": "Ask a natural-language question grounded in the site's Schema.org content.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "site": { "type": "array", "items": { "type": "string" } },
      "generate_mode": { "type": "string", "enum": ["list", "summarize", "generate"] }
    },
    "required": ["query"]
  }
}
```

Note that the MCP `ask` tool takes `site` as an **array** (where the REST `/ask` takes a single string). Map accordingly in clients.

#### 2. `list_sites` — enumeration

```json
{ "name": "list_sites", "description": "List all sites the agent can query.", "inputSchema": { "type": "object", "properties": {} } }
```

#### 3. `who` — federated discovery (conditional)

Only present when `who_endpoint_enabled: true` in `config_nlweb.yaml`. Takes `{query}`, returns the best NLWeb site(s) for that query — used for federated search across sites.

### Streaming inside MCP

JSON-RPC 2.0 itself is request/response — no streaming. NLWeb's `/mcp` is **NOT SSE by default**. SSE only activates when the inner `ask` tool is called with `streaming: true` in its args. Most MCP clients don't expect that, so for cross-agent compatibility leave streaming off in MCP and turn it on only for clients you control.

### Error Format

JSON-RPC 2.0 errors:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": { "errors": [...] }
  }
}
```

Common codes: `-32700` parse error, `-32600` invalid request, `-32601` method not found, `-32602` invalid params, `-32603` internal error.

### Two Parallel MCP Wrappers

NLWeb actually ships **two** MCP integrations:

| Wrapper | Path | Purpose |
|---------|------|---------|
| `webserver/mcp_wrapper.py` | `/mcp` on the aiohttp server (port 8000) | The canonical Python MCP server |
| `openai-apps-sdk-integration/nlweb_server_node/` | Separate Node.js/TypeScript process | Adds a React widget for ChatGPT Apps SDK — registers a `nlweb-list` tool and serves `ui://widget/nlweb-list.html` |

There's also an **A2A wrapper** (`webserver/a2a_wrapper.py`, route `a2a.py`) for Google's Agent-to-Agent protocol, and an **AppSDK adapter** on port 8100 (`appsdk_adapter_server.py`) that translates NLWeb's message list to OpenAI Apps SDK envelopes for existing clients.

## Implementation Guidance

### Server-Side: Just use the built-in /mcp

You don't typically write an MCP server for NLWeb — it's already there. What you might do:

1. **Verify `tools/list`** matches your needs by hitting it from your agent client.
2. **Customize the tool description** if your site needs a more specific prompt — patch `mcp_wrapper.py::handle_tools_list` carefully (you'll re-merge on upgrade).
3. **Add authentication** via middleware (`webserver/middleware/`) — MCP has no built-in auth; bring your own (bearer token, OAuth proxy, etc.).
4. **Disable `who`** for offline / single-site deployments by setting `who_endpoint_enabled: false`.

### Client-Side: Connecting an agent to NLWeb

```python
# Sketch — verify against latest MCP client SDK
import httpx, json

async def mcp_call(url, method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    async with httpx.AsyncClient() as c:
        r = await c.post(url, json=payload, timeout=60)
        return r.json()

# Handshake — ONLY on handshake-era revisions. The stateless core (2026-07-28+)
# removed `initialize` entirely; skip this call there and go straight to tools/list.
# MCP_REVISION must come from the live spec, not from memory. See "MCP Protocol Revision".
await mcp_call("http://localhost:8000/mcp", "initialize", {"protocolVersion": MCP_REVISION})

# Discover tools
tools = await mcp_call("http://localhost:8000/mcp", "tools/list")

# Ask
result = await mcp_call("http://localhost:8000/mcp", "tools/call", {
    "name": "ask",
    "arguments": {"query": "what's new this week?", "site": ["news"], "generate_mode": "summarize"}
})
```

### Wiring to Claude Code

Add an entry in `~/.claude.json` `mcpServers`:

```json
{
  "mcpServers": {
    "my-nlweb-site": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

(Verify the exact Claude Code MCP config schema in current docs — it changes.)

### Wiring to ChatGPT

ChatGPT Apps SDK requires the separate Node.js MCP server in `openai-apps-sdk-integration/nlweb_server_node/`. It bundles a React widget that renders the `nlweb-list` tool's results. Follow `docs/nlweb-chatgpt-integration.md` for the exact registration steps — ChatGPT's MCP app store rules change.

### Wiring to Gemini

Gemini's tool-calling supports MCP via the Vertex AI Agent SDK. Point it at `http://your-nlweb-host:8000/mcp` and call `tools/list` → `tools/call`.

### Gotchas

- The MCP wrapper's docstring **explicitly warns** that backwards compatibility is not guaranteed. Pin your client to the same NLWeb release you tested against, and re-verify `tools/list` on every upgrade.
- The `site` arg differs between `/ask` (string) and `/mcp::ask` (array). Don't confuse them.
- `/mcp` is **not SSE** by default. Don't wire your client expecting EventSource.
- The AppSDK adapter (port 8100) is its own thing — only ChatGPT Apps SDK clients should hit it; native MCP clients use port 8000's `/mcp`.

Always re-fetch `mcp_wrapper.py` and the chatgpt-integration doc before generating final code.
