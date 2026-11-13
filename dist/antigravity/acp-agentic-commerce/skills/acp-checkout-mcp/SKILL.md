---
name: acp-checkout-mcp
description: >
  Implement ACP checkout as an MCP server, exposing checkout operations as MCP
  tools. Use when building an MCP-based commerce server for AI agents that use
  tool-calling to complete purchases.
---

# ACP Checkout — MCP Binding

## Before writing code

**Fetch live docs**:
1. Fetch `https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/releases` for the current spec version.
2. **Fetch the official OpenRPC document** — `spec/<version>/openrpc/openrpc.agentic_checkout.json` in the repo. Since the `2026-04-17` release there is a machine-readable JSON-RPC description of the checkout binding; **use it rather than hand-deriving tool names**. The table below predates it.
3. Fetch `https://developers.openai.com/commerce/specs/checkout/` for checkout operation semantics.
4. Fetch `https://modelcontextprotocol.io/specification/` — it redirects to the current MCP revision. Confirm the transport model before writing server code; MCP's core changed shape between revisions (the stateless core removed the `initialize` handshake and `Mcp-Session-Id`), so a server written against an older revision will not match a current client.
5. Fetch MCP SDK docs: web-search `site:github.com modelcontextprotocol python-sdk` or `typescript-sdk` for the current SDK.

## Conceptual Architecture

### What MCP Binding Means

ACP's REST checkout operations can be exposed as **MCP tools** via an MCP server. This allows AI agents that use tool-calling (Claude, ChatGPT, Gemini) to invoke checkout operations directly as tools rather than making raw HTTP calls.

Since `2026-04-17` this mapping is **specified, not improvised** — the OpenRPC document is the source of truth for method names and parameter shapes. Treat the mapping below as orientation and the OpenRPC document as normative.

### Mapping REST to MCP Tools

Each REST checkout operation becomes an MCP tool:

| REST Operation | MCP Tool Name | Description |
|---------------|---------------|-------------|
| POST /checkout_sessions | `create_checkout_session` | Create a new checkout session with items |
| POST /checkout_sessions/{id} | `update_checkout_session` | Update session (items, address, fulfillment) |
| GET /checkout_sessions/{id} | `get_checkout_session` | Retrieve current session state |
| POST /checkout_sessions/{id}/complete | `complete_checkout_session` | Submit payment to finalize |
| POST /checkout_sessions/{id}/cancel | `cancel_checkout_session` | Cancel the session |

### Tool Input Schemas

Each MCP tool accepts JSON input matching the corresponding REST request body. The tool's `inputSchema` should be derived from the ACP OpenAPI spec's request schemas.

### Tool Output

Each tool returns the CheckoutSession object (or error) as JSON, matching the REST response body.

### MCP Server Architecture

```
AI Agent (Claude/ChatGPT)
    ↓ tool call (JSON-RPC)
MCP Server (your code)
    ↓ business logic
Checkout Service (same logic as REST)
    ↓ payment
PSP (Stripe)
```

The MCP server wraps the same business logic that the REST endpoints use. The checkout service layer should be shared between REST and MCP bindings.

### Key Considerations

- **Idempotency** — MCP doesn't have HTTP headers, so pass `idempotency_key` as a tool parameter
- **API versioning** — Include `api_version` as a tool parameter or server configuration
- **Authentication** — MCP transport handles auth (stdio for local, SSE/streamable-HTTP for remote)
- **Error handling** — Return ACP error objects as tool errors with the same `type`/`code`/`message` structure
- **Statelessness** — Each tool call should be stateless; session state lives in the CheckoutSession object

### Use Cases

- AI agents that prefer tool-calling over raw HTTP
- Claude Desktop / Claude Code integrations
- Multi-agent architectures where commerce is one capability
- Rapid prototyping without building a full REST server

### Best Practices

- Share the checkout business logic layer between REST and MCP bindings
- Derive tool input schemas from the ACP OpenAPI spec (don't hand-write them)
- Include descriptive tool descriptions so the agent understands when to use each tool
- Test with the MCP Inspector before connecting to an agent

Fetch the latest ACP OpenAPI spec and MCP SDK documentation for exact schemas and server setup before implementing.
