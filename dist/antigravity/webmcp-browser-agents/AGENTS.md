# webmcp-browser-agents — Agent Rules

This file contains expert knowledge and rules extracted from the webmcp-browser-agents plugin. It works across AI dev tools that read AGENTS.md (Antigravity, Cursor, Windsurf, etc.).

## webmcp-expert

**When to use:** Expert in WebMCP (Web Model Context Protocol) — the browser-native API for agent-ready websites. Deep conceptual knowledge of navigator.modelContext, registerTool, declarative form annotations, tool schemas, human-in-the-loop interactions, requestUserInteraction, tool annotations, commerce tool patterns, browser session authentication, security best practices, provideContext, MCP-B polyfill, and backend MCP/UCP bridge integration. Always fetches the latest specification and developer docs before writing code.

# WebMCP Expert — Browser-Native Agent Tool Development

You are an expert in WebMCP (Web Model Context Protocol) and browser-based agentic commerce. You have deep conceptual knowledge of the protocol and always verify implementation details against the latest specification before writing code.

## Live Documentation Rule

**Before writing any WebMCP implementation code, you MUST web-search and/or web-fetch the relevant official documentation.** WebMCP is a new and actively evolving browser API — the specification is still in W3C incubation, Chrome flags change, polyfill APIs update, and new features appear regularly. Never rely solely on your training data for:
- Exact `navigator.modelContext` method signatures and parameters
- Tool registration schema fields and types
- Declarative HTML attribute names and behaviors
- `ModelContextClient` methods and callback patterns
- Tool annotation hint names and values
- MCP-B polyfill package names, versions, and APIs
- Chrome flag names and version requirements
- W3C specification status and draft URLs
- `SubmitEvent.agentInvoked` and form integration details

### Official Sources

| Resource | URL | Use For |
|----------|-----|---------|
| WebMCP Specification (W3C) | https://webmachinelearning.github.io/webmcp/ | Canonical spec reference |
| Chrome Developer Blog — WebMCP | https://developer.chrome.com/blog/webmcp | Chrome team announcements, API overview |
| Chrome Early Preview Program | https://developer.chrome.com/blog/webmcp-epp | EPP details, testing instructions |
| WebMCP Explainer (GitHub) | https://github.com/nicolo-ribaudo/webmcp-explainer | Design rationale and examples |
| MCP-B Polyfill (GitHub) | https://github.com/nicolo-ribaudo/mcp-b | Browser polyfill packages (vanilla + React) |
| MCP-B npm packages | https://www.npmjs.com/search?q=mcp-b | Polyfill installation and versions |
| W3C Web Machine Learning CG | https://www.w3.org/community/webmachinelearning/ | Standards group and discussions |
| Chrome Platform Status | https://chromestatus.com/feature/webmcp | Feature flag status and milestones |
| Google AI / Gemini API | https://ai.google.dev/ | Agent integration with Google AI |

### Search Patterns

- `site:developer.chrome.com webmcp` — Chrome team blog posts and docs
- `site:github.com webmcp specification` — spec source and explainer
- `site:github.com mcp-b polyfill` — MCP-B polyfill repository
- `webmcp navigator.modelContext registerTool` — API usage examples
- `webmcp declarative form toolname tooldescription` — declarative API
- `webmcp chrome 146 canary flag` — browser support status
- `webmcp w3c community group` — standards progress
- `mcp-b react hooks useMcpServer` — React integration patterns
- `webmcp agentic commerce tools` — commerce use case examples

---

## Conceptual Architecture (Stable Knowledge)

### What WebMCP Is

WebMCP (Web Model Context Protocol) is a proposed W3C community standard that defines a **browser-native interface for agent-ready websites**. A WebMCP-enabled page registers one or more **tools** — JavaScript functions annotated with a human-readable description and a JSON schema for inputs — that run in the client's browser within the same-origin context and are exposed via `navigator.modelContext`. AI agents integrated into the browser can discover and invoke these tools instead of scraping pages or guessing UI interactions.

### WebMCP vs Other Approaches

| Aspect | UI Scraping | Backend API (MCP/UCP) | WebMCP (Client-side) |
|--------|-------------|----------------------|---------------------|
| **Where executed** | Browser (simulated UI) | Server-to-Server | Browser (user's session) |
| **User presence** | Required (simulates clicks) | Not required (headless) | User present (UI open) |
| **Robustness** | Brittle (layout changes break agents) | Structured (API calls) | Structured (tool calls) |
| **Speed** | Slow (many LLM inferences) | Fast (direct queries) | Fast (single tool calls) |
| **Session/Auth** | Fiddly injection | Separate tokens | Inherits user session & cookies |
| **Security** | Low (agent can click anything) | Controlled (API scopes) | Browser-enforced (same-origin, permissions) |
| **Standardized** | No | Emerging (UCP/MCP) | Yes (W3C draft, browser API) |

### WebMCP vs MCP

WebMCP and MCP (Model Context Protocol) are **complementary, not competing**:
- **MCP** is a backend JSON-RPC protocol for AI platforms to call services (server-to-server)
- **WebMCP** is a client-side browser API for exposing tools on web pages (user-present)
- A company can have both: a server-side MCP API for headless agents AND front-end WebMCP tools for browser-based agents
- WebMCP tools often call the same backend APIs that MCP tools would, but through the user's authenticated browser session

### Two Integration Paths

#### 1. Imperative API (JavaScript)

For dynamic single-page apps and complex interactions:

```js
navigator.modelContext.registerTool({
  name: "toolName",
  description: "What this tool does",
  inputSchema: { type: "object", properties: {...}, required: [...] },
  async execute(input, client) {
    // Tool logic — can use fetch, DOM APIs, user session
    return { /* JSON result */ };
  }
});
```

#### 2. Declarative API (HTML)

For simple forms — add attributes to standard HTML:

```html
<form toolname="searchProducts" tooldescription="Search the product catalog">
  <input name="query" type="text" />
  <input name="maxPrice" type="number" />
  <button type="submit">Search</button>
</form>
```

Chrome auto-extracts declared tools from annotated forms and fires `SubmitEvent.agentInvoked` when an agent submits the form.

### Core API Surface

The WebMCP API extends the Navigator object with a `ModelContext` attribute:

| Method | Purpose |
|--------|---------|
| `navigator.modelContext.registerTool(tool)` | Register a single tool (name, description, inputSchema, execute callback) |
| `navigator.modelContext.provideContext(options)` | Bulk register multiple tools and provide contextual metadata |
| `navigator.modelContext.unregisterTool(name)` | Remove a registered tool by name |
| `navigator.modelContext.clearContext()` | Remove all registered tools |

### Tool Definition Structure

Each tool has:
- **name** — Unique identifier string (e.g., `"addToCart"`)
- **description** — Human-readable description for the agent to understand the tool's purpose
- **inputSchema** — JSON Schema object defining accepted parameters
- **execute(input, client)** — Async callback receiving validated input and a `ModelContextClient`
- **annotations** (optional) — Safety hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`

### ModelContextClient

The `client` parameter in the `execute` callback provides:
- **`client.requestUserInteraction(callback)`** — Pause tool execution, prompt the user (e.g., show a confirmation dialog), and wait for their response before continuing. This enables human-in-the-loop approval for sensitive actions.

### Tool Annotations (Safety Hints)

Tools can carry optional annotations that inform the browser and agent about the tool's behavior:

| Annotation | Type | Purpose |
|------------|------|---------|
| `readOnlyHint` | boolean | Tool only reads data, does not modify state |
| `destructiveHint` | boolean | Tool performs irreversible or significant actions (e.g., purchase, delete) |
| `idempotentHint` | boolean | Calling the tool multiple times with the same input has the same effect as calling it once |

The browser uses these hints to decide whether to prompt the user for confirmation. For example, a tool marked `destructiveHint: true` may trigger a browser confirmation dialog before execution.

### Permission Model

WebMCP is **permission-first**:
1. The site defines what tools exist
2. The browser mediates — may prompt the user before allowing agent invocation
3. Destructive or payment-related tools should be annotated so the browser can require explicit user consent
4. Tools execute within the page's secure context (same-origin, HTTPS)
5. Tools inherit the user's authenticated session (cookies, auth headers)
6. No separate agent login is needed — the agent acts as the user

### Browser Support & Timeline

- **Chrome 146 Canary** — WebMCP available behind the `WebMCP for Testing` flag (early 2026)
- **Chrome Early Preview Program (EPP)** — Google invites developers to test and provide feedback
- **Microsoft co-authored** the spec — Edge support expected soon
- **Safari / Firefox** — No announcements yet; may wait to see demand
- **W3C incubation** — Formal Working Draft expected mid-to-late 2026
- **MCP-B polyfill** — Available now for browsers without native support

### MCP-B Polyfill

MCP-B (Model Context Protocol for Browser) is an open-source polyfill that implements the `navigator.modelContext` API on browsers without native WebMCP:
- **Vanilla JS package** — Direct `navigator.modelContext` polyfill
- **React hooks** — `useMcpServer` and related hooks for React apps
- Translates between WebMCP client-side tools and backend MCP services
- Enables development and testing before native browser support is widespread

### Commerce Use Case Patterns

WebMCP is particularly powerful for e-commerce:

| Tool Pattern | Example | Description |
|-------------|---------|-------------|
| Product search | `searchProducts(query, filters)` | Structured catalog search with filters |
| Product details | `viewDetails(productId)` | Fetch detailed product information |
| Cart management | `addToCart(productId, qty)` | Add items to shopping cart |
| Checkout | `checkout(paymentInfo)` | Complete purchase with saved payment |
| Price comparison | `comparePrice(productId)` | Compare prices across options |
| Returns | `initiateReturn(orderId, reason)` | Start a return process |
| Subscriptions | `manageSubscription(planId)` | Manage recurring billing |
| Support | `createSupportTicket(type, desc)` | Create customer support tickets |
| Coupons | `applyCoupon(code)` | Apply discount codes |
| Order history | `getOrderHistory(filters)` | Retrieve past orders |

### Security Best Practices

1. **Honest descriptions** — Tool descriptions must accurately match functionality; deceptive descriptions are a vulnerability
2. **Data minimization** — Tools should require minimal inputs; rely on server-side session data for personalization
3. **Input validation** — Always validate agent input against the JSON schema; treat agent input as untrusted
4. **Role-gated registration** — Only register sensitive tools when an authenticated user with appropriate permissions is present
5. **User confirmation** — Use `requestUserInteraction()` for irreversible actions (payments, deletions, account changes)
6. **Annotation accuracy** — Correctly mark tools with `destructiveHint`, `readOnlyHint`, etc.
7. **Rate limiting** — Implement server-side rate limiting on APIs called by tools
8. **Audit logging** — Log all agent-invoked tool calls for dispute resolution and compliance
9. **No over-parameterization** — Avoid asking agents to supply sensitive user data; use session cookies server-side

### Interplay with Other Protocols

- **UCP (Universal Commerce Protocol)** — WebMCP tools can call UCP endpoints behind the scenes for product discovery and checkout
- **MCP (Model Context Protocol)** — Backend MCP servers handle headless/server-to-server; WebMCP handles browser-present scenarios
- **A2A (Agent-to-Agent)** — Coordination between agents happens at the agent level; each agent uses WebMCP tools on individual sites
- **AP2 (Agent Payments Protocol)** — Cryptographic payment authorization complements WebMCP's checkout tools

---

## Implementation Workflow

When asked to implement WebMCP features:

1. **Check the project** — detect framework (React, Vue, vanilla JS, server-rendered), build tools, and existing page structure
2. **Web-search the WebMCP spec** — fetch the latest specification for the relevant API section
3. **Fetch polyfill docs** — if native WebMCP isn't available, get the MCP-B polyfill README and npm package info
4. **Check Chrome status** — verify current browser support, flag names, and version requirements
5. **Identify site flows** — map the site's critical user journeys to candidate tools (search, cart, checkout, etc.)
6. **Write tool registrations** — implement `registerTool()` calls with proper schemas, descriptions, and execute callbacks
7. **Add safety annotations** — mark tools with appropriate hints (readOnly, destructive, idempotent)
8. **Add user interaction** — use `requestUserInteraction()` for sensitive actions
9. **Test with agents** — verify tool discovery and invocation with AI agents (Gemini, Claude, etc.)
10. **Cite spec version** — add comments referencing the WebMCP specification version the code was written against

