---
name: nlweb-chatgpt-appsdk
description: Integrate NLWeb with ChatGPT's Apps SDK — the Node.js MCP server in `openai-apps-sdk-integration/`, the `nlweb-list` tool, the React widget at `ui://widget/nlweb-list.html`, and the port-8100 AppSDK adapter that translates NLWeb's message list to OpenAI Apps SDK envelopes. Use when publishing an NLWeb site as a ChatGPT app or wiring NLWeb results into an Apps SDK widget.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb + ChatGPT Apps SDK

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-chatgpt-integration.md for the canonical wiring steps.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-appsdk-adapter.md for the port-8100 adapter.
3. Inspect `openai-apps-sdk-integration/nlweb_server_node/` in the live repo — this is a separate Node.js/TypeScript MCP server.
4. Web-search OpenAI's current Apps SDK documentation — link from https://platform.openai.com.
5. Verify the React widget contract — what `nlweb-list.html` expects from the tool result envelope.

## Conceptual Architecture

### Why a Separate Adapter?

NLWeb's native `/mcp` returns generic MCP tool results — a list of Schema.org objects. ChatGPT's Apps SDK expects a richer envelope that pairs tool output with a UI resource (widget). The integration ships **two extra pieces** on top of the base NLWeb server:

1. **`openai-apps-sdk-integration/nlweb_server_node/`** — a Node.js/TypeScript MCP server that registers an `nlweb-list` tool and serves a React widget at `ui://widget/nlweb-list.html`. ChatGPT discovers this and renders the widget when the tool returns results.

2. **AppSDK Adapter (port 8100, `appsdk_adapter_server.py`)** — an aiohttp server that takes legacy NLWeb message-list responses and re-shapes them into the OpenAI Apps SDK envelope on the fly. Useful if you already have NLWeb running and want to plug ChatGPT in without rewriting clients.

Native MCP clients (Claude, Gemini) ignore both — they hit the canonical `/mcp` on port 8000.

### The Two Integration Paths

| Path | Use When |
|------|----------|
| **Node.js MCP server with widget** | You want the full ChatGPT app experience with the React widget |
| **Port-8100 AppSDK adapter** | You only want translation; you don't need a widget |

For a new build, use path 1. For retrofitting an existing NLWeb deployment, path 2 is lower-risk.

### The `nlweb-list` Tool

The Node.js server registers a single MCP tool, `nlweb-list`, with a schema like:

```json
{
  "name": "nlweb-list",
  "description": "Query the site and render a list of results as a card carousel.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "site": { "type": "string" }
    },
    "required": ["query"]
  }
}
```

(Verify exact schema in the live repo.)

The tool internally calls the NLWeb `/ask` endpoint and returns:
- Structured tool output (the result list)
- A UI resource reference: `ui://widget/nlweb-list.html`

ChatGPT's Apps SDK runtime renders the widget, passes the tool output into it via the SDK's `window.openai`-style API (or its successor — Apps SDK is rapidly evolving).

### The React Widget

The widget lives in the Node.js project and is bundled into a single HTML file served at `ui://widget/nlweb-list.html`. It renders the Schema.org results as cards (image, name, description, score). Typical features:
- Type-aware cards (Recipe vs Product vs Event)
- Click-through to source URL
- Optional follow-up actions

### Port 8100 Adapter

`webserver/appsdk_adapter_server.py` runs as a **separate process** alongside the main NLWeb server. It:
- Listens on port 8100
- Proxies `/ask` to the main server on port 8000
- Translates NLWeb's stream of message objects to OpenAI Apps SDK envelope shape
- Serves a UI resource ChatGPT can render

Existing clients still hit `:8000/ask`; only ChatGPT clients hit `:8100/ask`. They share the same backend data and config.

### MCP Protocol Revision Compatibility

The Node.js MCP server must advertise the **same** MCP revision as NLWeb's Python `/mcp` — mismatched revisions are the usual cause of a ChatGPT app that connects but lists no tools.

Do not hard-code the revision. Resolve all three and reconcile them:

1. The current spec revision — fetch https://modelcontextprotocol.io/specification/ (redirects to the live one).
2. What the installed NLWeb Python `/mcp` advertises.
3. What the ChatGPT Apps SDK runtime currently accepts.

Take the oldest revision all three support. ChatGPT updates its Apps SDK runtime frequently — re-test on every OpenAI release, and re-check the revision rather than assuming it held.

### ChatGPT App Approval

Publishing as a public ChatGPT app requires going through OpenAI's review process. The dev experience:
1. Build the MCP server + widget
2. Test locally with ChatGPT's developer mode (links it to localhost)
3. Submit for review per OpenAI's current process (verify the latest steps)
4. Distribute via the GPT Store

OpenAI's policies change — always check the current submission docs.

## Implementation Guidance

### Path 1: Run the Node.js MCP Server

```bash
cd openai-apps-sdk-integration/nlweb_server_node
npm install
npm run build
npm start
```

(Verify exact commands against the live `package.json`.)

Configure the underlying NLWeb URL via env var (typically `NLWEB_ASK_URL=http://localhost:8000/ask`).

Then add the MCP server to ChatGPT's developer mode pointing at the Node.js server's URL.

### Path 2: Run the Port-8100 Adapter

```bash
# Main NLWeb on :8000
python AskAgent/python/app-aiohttp.py

# AppSDK adapter on :8100
python AskAgent/python/webserver/appsdk_adapter_server.py
```

Point ChatGPT at the :8100 endpoint instead of :8000.

### Widget Customization

If you fork the React widget:
- Keep the result-list shape stable — ChatGPT expects a consistent contract
- Test in multiple ChatGPT clients (web, mobile) — rendering quirks vary
- Don't make the widget too large; ChatGPT clips overflowing content

### Tool Naming for Discovery

ChatGPT picks tools based on the description. For an NLWeb-backed app, write the `description` to be specific about the *domain* (e.g., "Search recipes from Joy of Cooking" not "Generic NL search"). Site operators frequently fork the Node.js server to customize this.

### Combining With Native MCP

A single NLWeb deployment can serve both audiences:
- Claude / Gemini / direct MCP clients → port 8000 `/mcp`
- ChatGPT → port 8100 adapter OR Node.js server (whichever path you chose)

Both share the same retrieval and ranking. No data duplication.

### Common Pitfalls

- **Widget renders but data is empty** — the result envelope doesn't match what the widget JS expects. Console-log the tool output in ChatGPT's developer mode to inspect.
- **ChatGPT can't find the MCP server** — port not exposed, or the server didn't advertise itself correctly during the developer-mode handshake.
- **CORS errors when widget loads** — the UI resource origin restrictions. Serve from a single origin or set proper CORS.
- **Latency spikes via :8100 adapter** — the adapter buffers the SSE stream before translating. Acceptable for short queries; problematic for `mode=generate`. Use path 1 for streaming-heavy use cases.
- **Apps SDK API changes break the widget** — OpenAI updates the `window.openai`-style runtime frequently. Pin a tested SDK version in the React build.

Always re-fetch `nlweb-chatgpt-integration.md` and the Node.js project's `README.md` before customizing — this is one of the fastest-moving parts of NLWeb.
