# ACP Agentic Commerce Plugin for Claude Code

A deeply expert Claude Code plugin for implementing the **Agentic Commerce Protocol (ACP)** — the open standard co-developed by OpenAI and Stripe for AI-agent-mediated commerce.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — protocol architecture, roles, checkout state machine, payment flow, extensions framework, and security model that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest OpenAPI schemas, field definitions, error codes, and SDK methods.
- **Spec version is always cited** — generated code includes the `API-Version` header matching the spec version it was written against.

## Plugin Structure

```
acp-agentic-commerce/
├── .claude-plugin/
│   └── plugin.json                              # Plugin manifest
├── agents/
│   └── acp-expert.md                            # Subagent: full ACP protocol expert
├── hooks/
│   ├── hooks.json                               # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                     # PostToolUse: detect payment secrets
├── skills/
│   ├── acp-setup/SKILL.md                       # Project scaffolding & dependencies
│   ├── acp-product-feed/SKILL.md                # Product feed generation & push
│   ├── acp-checkout-rest/SKILL.md               # REST checkout — 5 operations
│   ├── acp-checkout-mcp/SKILL.md                # MCP binding for checkout
│   ├── acp-delegated-payment/SKILL.md           # SharedPaymentToken & Stripe SPT
│   ├── acp-payment-handlers/SKILL.md            # Pluggable payment handlers
│   ├── acp-orders-webhooks/SKILL.md             # Order lifecycle & HMAC webhooks
│   ├── acp-fulfillment/SKILL.md                 # Shipping, digital, pickup, local delivery
│   ├── acp-discount-extension/SKILL.md          # Discount codes & allocations
│   ├── acp-capability-negotiation/SKILL.md      # Dynamic capability discovery
│   ├── acp-extensions-authoring/SKILL.md        # Custom extension creation
│   ├── acp-intent-traces/SKILL.md               # Cart abandonment signals
│   ├── acp-affiliate-attribution/SKILL.md       # Privacy-preserving attribution
│   ├── acp-conformance/SKILL.md                 # Spec validation & production readiness
│   └── acp-dev-patterns/SKILL.md                # Idempotency, errors, security patterns
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "acp-agentic-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "acp-agentic-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/acp-agentic-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `acp-agentic-commerce:acp-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves ACP:

```
Build an ACP merchant server with REST checkout
```

```
Implement delegated payment with Stripe SharedPaymentTokens
```

```
Add discount codes and webhook signing to my ACP checkout
```

### Explicit invocation

```
Use the acp-expert subagent to implement 3D Secure authentication flow
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest spec version and changelog on GitHub
2. Fetch the relevant OpenAPI spec for exact schemas and field types
3. Fetch the RFC for the capability being implemented
4. Check OpenAI and Stripe docs for integration-specific guidance
5. Write code against the verified-current spec, citing the version

## Available Skills

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **acp-setup** | `/acp-agentic-commerce:acp-setup` | Manual | Scaffold project, import OpenAPI specs, stub endpoints |
| **acp-product-feed** | auto | Auto + manual | Feed generation (CSV/JSON/XML), field mapping, push to endpoint |
| **acp-checkout-rest** | auto | Auto + manual | REST checkout — create, update, retrieve, complete, cancel |
| **acp-checkout-mcp** | auto | Auto + manual | MCP server binding for checkout operations |
| **acp-delegated-payment** | auto | Auto + manual | SPT provisioning, Stripe integration, 3DS flow |
| **acp-payment-handlers** | auto | Auto + manual | Pluggable handlers — tokenized cards, gift cards, points |
| **acp-orders-webhooks** | auto | Auto + manual | Order lifecycle, HMAC webhook signing/verification |
| **acp-fulfillment** | auto | Auto + manual | Shipping, digital, pickup, local delivery options |
| **acp-discount-extension** | auto | Auto + manual | Discount codes, applied/rejected discounts, allocations |
| **acp-capability-negotiation** | auto | Auto + manual | Dynamic capability/extension/handler discovery |
| **acp-extensions-authoring** | auto | Auto + manual | Custom extensions — JSONPath targeting, schema composition |
| **acp-intent-traces** | auto | Auto + manual | Cart abandonment signals, 10 reason codes |
| **acp-affiliate-attribution** | auto | Auto + manual | Privacy-preserving attribution, token-based tracking |
| **acp-conformance** | `/acp-agentic-commerce:acp-conformance` | Manual | Validate against spec, production readiness checklist |
| **acp-dev-patterns** | auto | Auto + manual | Idempotency, error handling, signing, rate limiting |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Stripe keys (`sk_live_`, `sk_test_`, `whsec_`), webhook secrets, Bearer tokens, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## ACP Protocol at a Glance

### Three Roles

| Role | Responsibility |
|------|---------------|
| **Buyer / AI Agent** | Consumer and/or AI agent (e.g., ChatGPT) that manages purchases |
| **Business (Merchant)** | Merchant of Record — processes payments, manages orders, handles fulfillment |
| **Payment Provider (PSP)** | Processes tokenized credentials — Stripe is the first implementation |

### Protocol Layers

1. **Product Feed** — Push-based catalog sync (CSV/JSON/XML/TSV, up to every 15 min)
2. **Checkout** — Session-based REST API with 5 operations
3. **Payment** — Delegated payment via SharedPaymentToken (single-use, scoped)
4. **Orders/Events** — Webhook-based order lifecycle with HMAC signatures
5. **Capability Negotiation** — Dynamic feature discovery
6. **Extensions** — Composable add-ons (discounts, intent traces, affiliate attribution)

### Checkout Status Flow

```
not_ready_for_payment → ready_for_payment → completed
         |                      |                |
         +──────────────────────+→ canceled ←────+
                                |
                           in_progress
                                |
                      authentication_required
```

### ACP vs UCP

| Aspect | ACP (OpenAI/Stripe) | UCP (Google/Shopify) |
|--------|---------------------|---------------------|
| Focus | Agent-mediated checkout execution | Full shopping journey |
| Transport | REST + MCP | REST, MCP, A2A, Embedded |
| Payment | SharedPaymentToken (Stripe) | Google Pay, Shop Pay, AP2 |
| Discovery | Product Feed push | `/.well-known/ucp` pull |
| First Agent | ChatGPT Instant Checkout | Google AI Mode, Gemini |

Shopify supports BOTH protocols — they are complementary, not competing.

## Official References

| Resource | URL |
|----------|-----|
| ACP Spec Website | https://www.agenticcommerce.dev/ |
| GitHub Repository | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol |
| OpenAI Commerce Docs | https://developers.openai.com/commerce/ |
| OpenAI Get Started | https://developers.openai.com/commerce/guides/get-started/ |
| OpenAI Checkout Spec | https://developers.openai.com/commerce/specs/checkout/ |
| OpenAI Payment Spec | https://developers.openai.com/commerce/specs/payment/ |
| OpenAI Feed Spec | https://developers.openai.com/commerce/specs/feed |
| OpenAI Production Guide | https://developers.openai.com/commerce/guides/production/ |
| Stripe ACP Docs | https://docs.stripe.com/agentic-commerce/protocol |
| Stripe SPT Docs | https://docs.stripe.com/agentic-commerce/concepts/shared-payment-tokens |
| Medusa Reference Impl | https://docs.medusajs.com/resources/how-to-tutorials/tutorials/agentic-commerce |
| ACP RFCs | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/rfcs |
| ACP OpenAPI Specs | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/spec |
| Claude Code Plugins Docs | https://code.claude.com/docs/en/plugins |
| Claude Code Subagents Docs | https://code.claude.com/docs/en/sub-agents |
| Claude Code Skills Docs | https://code.claude.com/docs/en/skills |

## Endorsed By

**Founding Maintainers**: OpenAI, Stripe

**Launch Partners**: Etsy, Shopify (1M+ merchants), Mastercard, Visa, Cloudflare

**First Implementation**: ChatGPT Instant Checkout (Plus, Pro, and Free users in the U.S.)
