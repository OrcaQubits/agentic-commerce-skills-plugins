# WebMCP Browser Agents Plugin for Claude Code

A deeply expert Claude Code plugin for building **agent-ready websites** using **WebMCP (Web Model Context Protocol)** — the browser-native API that lets sites expose structured tools to AI agents via `navigator.modelContext`.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — browser API architecture, tool registration patterns, declarative forms, schema design, human-in-the-loop flows, security model, and commerce patterns that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest API signatures, Chrome flag names, polyfill packages, and spec status.
- **Spec version is always cited** — generated code includes comments referencing the WebMCP specification version it was written against.

## Plugin Structure

```
webmcp-browser-agents/
├── .claude-plugin/
│   └── plugin.json                              # Plugin manifest
├── agents/
│   └── webmcp-expert.md                         # Subagent: full WebMCP protocol expert
├── hooks/
│   ├── hooks.json                               # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                     # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── webmcp-setup/SKILL.md                    # Project scaffolding & polyfill setup
│   ├── webmcp-register-tool/SKILL.md            # Imperative API (registerTool)
│   ├── webmcp-declarative-forms/SKILL.md        # Declarative API (HTML form attributes)
│   ├── webmcp-tool-schemas/SKILL.md             # JSON Schema design for tools
│   ├── webmcp-user-interaction/SKILL.md         # requestUserInteraction & confirmations
│   ├── webmcp-tool-annotations/SKILL.md         # readOnlyHint, destructiveHint, idempotentHint
│   ├── webmcp-commerce-tools/SKILL.md           # Commerce tools (search, cart, checkout)
│   ├── webmcp-authentication/SKILL.md           # Browser session auth & role-gated tools
│   ├── webmcp-security/SKILL.md                 # Permission model & security best practices
│   ├── webmcp-context-provider/SKILL.md         # provideContext API & bulk registration
│   ├── webmcp-mcp-bridge/SKILL.md               # WebMCP + backend MCP/UCP integration
│   ├── webmcp-polyfill/SKILL.md                 # MCP-B polyfill (vanilla JS & React)
│   ├── webmcp-testing/SKILL.md                  # Testing with AI agents & DevTools
│   └── webmcp-dev-patterns/SKILL.md             # SPA routing, errors, SEO, deployment
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "/path/to/agentic-commerce-claude-plugins/webmcp-browser-agents"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "webmcp-browser-agents": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/webmcp-browser-agents"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `webmcp-browser-agents:webmcp-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves WebMCP:

```
Make my e-commerce site agent-ready with WebMCP tools
```

```
Register a searchProducts tool using navigator.modelContext
```

```
Add human-in-the-loop confirmation to the checkout flow
```

### Explicit invocation

```
Use the webmcp-expert subagent to implement declarative form annotations
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest spec version on the W3C WebMCP spec page
2. Fetch the Chrome developer blog for current API guidance
3. Fetch the MCP-B polyfill README for current install/usage instructions
4. Write code against the verified-current spec, citing the version

## Available Skills (14)

| Skill | Invocation | Description |
|---|---|---|
| **webmcp-setup** | Auto + manual | Scaffold project, enable Chrome flags, install MCP-B polyfill |
| **webmcp-register-tool** | Auto + manual | Imperative API — `registerTool()`, execute callbacks, lifecycle |
| **webmcp-declarative-forms** | Auto + manual | Declarative API — HTML `toolname`/`tooldescription` attributes |
| **webmcp-tool-schemas** | Auto + manual | JSON Schema design for tool inputs and outputs |
| **webmcp-user-interaction** | Auto + manual | `requestUserInteraction()`, confirmation flows, approvals |
| **webmcp-tool-annotations** | Auto + manual | `readOnlyHint`, `destructiveHint`, `idempotentHint` safety hints |
| **webmcp-commerce-tools** | Auto + manual | Commerce tools — search, cart, checkout, returns, subscriptions |
| **webmcp-authentication** | Auto + manual | Browser session auth, role-gated registration, session handling |
| **webmcp-security** | Auto + manual | Permission model, data minimization, input validation, fraud |
| **webmcp-context-provider** | Auto + manual | `provideContext()` API, bulk registration, page metadata |
| **webmcp-mcp-bridge** | Auto + manual | WebMCP + backend MCP/UCP integration patterns |
| **webmcp-polyfill** | Auto + manual | MCP-B polyfill — vanilla JS, React hooks, feature detection |
| **webmcp-testing** | Auto + manual | Agent testing, schema validation, DevTools, e2e flows |
| **webmcp-dev-patterns** | Auto + manual | SPA routing, errors, performance, SEO, deployment patterns |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded API keys (Google, OpenAI, Anthropic, Stripe, Shopify), Bearer tokens, client secrets, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## WebMCP at a Glance

### Two Integration Paths

| Path | Mechanism | Best For |
|------|-----------|----------|
| **Imperative API** | `navigator.modelContext.registerTool()` | Dynamic SPAs, complex interactions |
| **Declarative API** | `<form toolname="..." tooldescription="...">` | Static forms, legacy pages, quick adoption |

### Core API Methods

| Method | Purpose |
|--------|---------|
| `navigator.modelContext.registerTool(tool)` | Register a tool with name, description, schema, and execute callback |
| `navigator.modelContext.provideContext(options)` | Bulk register tools with page-level metadata |
| `navigator.modelContext.unregisterTool(name)` | Remove a registered tool |
| `navigator.modelContext.clearContext()` | Remove all registered tools |
| `client.requestUserInteraction(callback)` | Pause for user confirmation during tool execution |

### Tool Annotations

| Annotation | Meaning |
|------------|---------|
| `readOnlyHint` | Tool only reads, no state changes |
| `destructiveHint` | Tool performs irreversible/significant actions |
| `idempotentHint` | Multiple identical calls have same effect as one |

### WebMCP vs Backend Protocols

| Aspect | WebMCP | MCP (Server) | UCP |
|--------|--------|-------------|-----|
| **Runs** | Browser (client-side) | Server-to-Server | Server-to-Server |
| **User** | Present (human-in-the-loop) | Not required | Not required |
| **Auth** | Browser session/cookies | API keys/OAuth | API keys |
| **Discovery** | `navigator.modelContext` | Server manifests | `.well-known/ucp/` |
| **Complementary** | Yes — same backend | Yes — same backend | Yes — same backend |

### Browser Support

| Browser | Status |
|---------|--------|
| Chrome 146+ Canary | Behind `WebMCP for Testing` flag |
| Edge | Expected soon (Microsoft co-authored spec) |
| Safari / Firefox | No announcements yet |
| MCP-B Polyfill | Any modern browser |

## Official References

| Resource | URL |
|----------|-----|
| WebMCP Specification (W3C) | https://webmachinelearning.github.io/webmcp/ |
| Chrome Developer Blog | https://developer.chrome.com/blog/webmcp |
| Chrome Early Preview Program | https://developer.chrome.com/blog/webmcp-epp |
| WebMCP Explainer (GitHub) | https://github.com/nicolo-ribaudo/webmcp-explainer |
| MCP-B Polyfill (GitHub) | https://github.com/nicolo-ribaudo/mcp-b |
| W3C Web ML Community Group | https://www.w3.org/community/webmachinelearning/ |
| Chrome Platform Status | https://chromestatus.com/feature/webmcp |

## Standards Context

WebMCP is part of the broader agentic commerce ecosystem:
- **UCP** (Universal Commerce Protocol) — Google/Shopify backend product discovery and checkout
- **MCP** (Model Context Protocol) — Backend JSON-RPC for AI tool calling
- **A2A** (Agent-to-Agent) — Inter-agent communication protocol
- **AP2** (Agent Payments Protocol) — Cryptographic payment authorization

WebMCP provides the **browser-side complement** to these backend protocols, enabling human-in-the-loop agent interactions on web pages.
