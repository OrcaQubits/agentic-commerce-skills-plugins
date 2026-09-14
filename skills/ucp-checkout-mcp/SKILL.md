---
name: ucp-checkout-mcp
description: Implement UCP Checkout over the MCP (Model Context Protocol) binding — expose checkout operations as MCP tools for AI agents. Use when building an MCP server that AI agents like Claude or Gemini can call for commerce, or when integrating with Shopify's MCP endpoint.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# UCP Checkout — MCP Binding

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification checkout-mcp` and fetch the page for exact tool definitions, JSON-RPC envelope format, and `_meta` requirements.

For Shopify's production MCP server, fetch https://shopify.dev/docs/agents/checkout/mcp for auth flow and endpoint details.

## Conceptual Architecture

### How MCP Maps to UCP

UCP over MCP is a **1:1 mapping** of checkout operations to MCP tools using JSON-RPC 2.0. The same data model as REST, different envelope.

### Five MCP Tools

| MCP Tool Name | Maps To | Key Inputs |
|---------------|---------|------------|
| `create_checkout` | POST /checkout-sessions | checkout object + idempotency_key |
| `get_checkout` | GET /checkout-sessions/{id} | id |
| `update_checkout` | PUT /checkout-sessions/{id} | id + checkout object |
| `complete_checkout` | POST .../complete | id + payment_data + idempotency_key |
| `cancel_checkout` | POST .../cancel | id + idempotency_key |

### Meta Requirements

Every MCP tool call MUST include `_meta.ucp.profile` pointing to the platform's UCP profile URI. This replaces the `UCP-Agent` HTTP header from the REST binding.

### Error Mapping

UCP errors embed inside JSON-RPC 2.0 error responses:
- JSON-RPC `error.code`: `-32603` (Internal Error)
- JSON-RPC `error.data`: Contains an `errors[]` array, where each error has `code`, `message`, `severity`, and `details` fields

### When to Use MCP Binding

- You're building a **merchant MCP server** that AI agents (Claude, Gemini, etc.) call via tool use
- You're integrating with an existing MCP server (e.g., Shopify's)
- You want AI agents to autonomously browse and purchase without REST client code

### Implementation Guidance

**Building a Business MCP Server:**
1. Implement the 5 tools using your MCP framework (e.g., `@modelcontextprotocol/sdk` for Node, `mcp` for Python)
2. Extract `_meta.ucp.profile` from every tool call for negotiation
3. Return checkout objects as JSON in the MCP tool result
4. Return errors using JSON-RPC error format with UCP data payload
5. Implement idempotency on create and complete tools

**Connecting to an existing MCP server (e.g., Shopify):**
1. Authenticate (Shopify uses OAuth2 client_credentials for access tokens)
2. Connect to the MCP endpoint
3. Call tools with proper `_meta.ucp.profile` and checkout payloads
4. Parse tool results for checkout status and messages

### Shopify MCP Integration

Shopify provides a production MCP server for UCP checkout. Before implementing:
- Fetch https://shopify.dev/docs/agents/checkout/mcp for the latest auth flow, endpoint URL format, and error codes
- Authentication uses `POST https://api.shopify.com/auth/access_token` with client credentials
- MCP endpoint is `POST https://{shop-domain}/api/ucp/mcp`
