# UCP Agentic Commerce Plugin for Claude Code

A deeply expert Claude Code plugin for implementing the **Universal Commerce Protocol (UCP)** — the open standard co-developed by Google and Shopify for agentic commerce.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — architecture, roles, flows, patterns, state machines, and design decisions that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest schemas, field names, SDK methods, and API shapes.
- **Spec version is always cited** — generated code includes comments referencing the UCP version it was written against.

## Plugin Structure

```
ucp-agentic-commerce/
├── .claude-plugin/
│   └── plugin.json                       # Plugin manifest
├── agents/
│   └── ucp-expert.md                     # Subagent: full UCP protocol expert
├── hooks/
│   ├── hooks.json                        # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py              # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── ucp-setup/SKILL.md                # Project scaffolding & SDK install
│   ├── ucp-checkout-rest/SKILL.md        # Checkout — REST binding
│   ├── ucp-checkout-mcp/SKILL.md         # Checkout — MCP binding
│   ├── ucp-checkout-a2a/SKILL.md         # Checkout — A2A binding
│   ├── ucp-embedded-checkout/SKILL.md    # Embedded Checkout Protocol (iframe)
│   ├── ucp-orders-webhooks/SKILL.md      # Orders & webhook signatures
│   ├── ucp-fulfillment/SKILL.md          # Fulfillment extension
│   ├── ucp-discount/SKILL.md             # Discount extension
│   ├── ucp-payment-handlers/SKILL.md     # Payment handlers (Google Pay, etc.)
│   ├── ucp-identity-linking/SKILL.md     # OAuth 2.0 identity linking
│   ├── ucp-ap2-mandates/SKILL.md         # AP2 cryptographic payment mandates
│   ├── ucp-schema-authoring/SKILL.md     # Custom schema & extension authoring
│   ├── ucp-buyer-consent/SKILL.md        # Buyer Consent extension (GDPR/CCPA)
│   ├── ucp-conformance/SKILL.md          # Conformance test suite
│   └── ucp-dev-patterns/SKILL.md         # Architecture & cross-cutting patterns
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "ucp-agentic-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "ucp-agentic-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/ucp-agentic-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `ucp-agentic-commerce:ucp-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves UCP:

```
Build a UCP merchant server with REST checkout
```

```
Implement MCP tools for my Shopify store's UCP checkout
```

```
Add fulfillment and discount extensions to my checkout flow
```

### Explicit invocation

```
Use the ucp-expert subagent to implement webhook signature verification
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest spec version on ucp.dev
2. Fetch the relevant specification page for exact schemas
3. Fetch the SDK README for current install/usage instructions
4. Write code against the verified-current spec, citing the version

## Available Skills

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **ucp-setup** | `/ucp-agentic-commerce:ucp-setup` | Manual | Scaffold project, install SDK, create discovery profile |
| **ucp-checkout-rest** | auto | Auto + manual | REST binding — endpoints, headers, status machine, errors |
| **ucp-checkout-mcp** | auto | Auto + manual | MCP binding — 5 tools, JSON-RPC, Shopify integration |
| **ucp-checkout-a2a** | auto | Auto + manual | A2A binding — Agent Cards, DataParts, message structure |
| **ucp-embedded-checkout** | auto | Auto + manual | Embedded Protocol — iframe postMessage, human escalation |
| **ucp-orders-webhooks** | auto | Auto + manual | Order lifecycle, webhook delivery, JWT signatures |
| **ucp-fulfillment** | auto | Auto + manual | Shipping/pickup methods, groups, options, destinations |
| **ucp-discount** | auto | Auto + manual | Discount codes, allocations, error codes |
| **ucp-payment-handlers** | auto | Auto + manual | Google Pay, Shop Pay, trust triangle, credential flow |
| **ucp-identity-linking** | auto | Auto + manual | OAuth 2.0 account linking, UCP scopes |
| **ucp-ap2-mandates** | auto | Auto + manual | SD-JWT mandates, merchant authorization, 7-step flow |
| **ucp-schema-authoring** | auto | Auto + manual | Custom capabilities/extensions, JSON Schema composition |
| **ucp-buyer-consent** | auto | Auto + manual | GDPR/CCPA consent collection, privacy compliance |
| **ucp-conformance** | `/ucp-agentic-commerce:ucp-conformance` | Manual | Run official test suite against your implementation |
| **ucp-dev-patterns** | auto | Auto + manual | Negotiation, idempotency, error loops, multi-binding arch |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Shopify tokens (`shpat_`, `shpss_`), Google API keys, Stripe keys, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## UCP Protocol at a Glance

### Four Roles

| Role | What it does |
|------|-------------|
| **Platform** | AI agent / app that orchestrates shopping on behalf of a buyer |
| **Business** | Merchant of Record — exposes inventory, checkout, and retains financial liability |
| **Credential Provider** | Manages payment instruments (Google Pay, Shop Pay) |
| **PSP** | Financial infrastructure (Stripe, Adyen) — authorization and settlement |

### Three Layers

1. **Shopping Service** — Core primitives (checkout sessions, line items, totals, messages)
2. **Capabilities** — Major domains (Checkout, Orders, Identity Linking) with independent versioning
3. **Extensions** — Composable add-ons (Fulfillment, Discounts, Buyer Consent, AP2 Mandates)

### Four Transport Bindings

| Binding | Use Case |
|---------|----------|
| **REST** | Traditional server-to-server |
| **MCP** | AI agent tool-calling (Claude, Gemini) |
| **A2A** | Autonomous agent-to-agent |
| **Embedded** | Human escalation via iframe |

### Checkout Status Flow

```
incomplete → requires_escalation → ready_for_complete → complete_in_progress → completed
     |                                                                              |
     +--------------------------------→ canceled ←---------------------------------+
```

## Official References

| Resource | URL |
|----------|-----|
| UCP Website | https://ucp.dev |
| Specification (latest) | https://ucp.dev/2026-01-23/ |
| Playground | https://ucp.dev/playground/ |
| GitHub Organization | https://github.com/Universal-Commerce-Protocol |
| Python SDK | https://github.com/Universal-Commerce-Protocol/python-sdk |
| JS/TS SDK | https://github.com/Universal-Commerce-Protocol/js-sdk |
| Sample Servers | https://github.com/Universal-Commerce-Protocol/samples |
| Conformance Tests | https://github.com/Universal-Commerce-Protocol/conformance |
| Google Merchant Guide | https://developers.google.com/merchant/ucp |
| Shopify MCP Server | https://shopify.dev/docs/agents/checkout/mcp |
| AP2 Protocol | https://ap2-protocol.org |
| Awesome UCP | https://github.com/Upsonic/awesome-ucp |
| OpenAI ACP (competing) | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol |

## Endorsed By

Google, Shopify, Etsy, Wayfair, Target, Walmart, Adyen, American Express, Best Buy, Flipkart, Macy's, Mastercard, Stripe, The Home Depot, Visa, Zalando, and 20+ others.
