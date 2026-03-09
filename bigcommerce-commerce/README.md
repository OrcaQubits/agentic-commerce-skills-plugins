# BigCommerce Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **BigCommerce** development — covering Stencil theme framework, REST/GraphQL APIs, single-click app development, checkout SDK, payment integrations, headless commerce with Catalyst/Next.js, multi-channel architecture, webhooks, widgets/Page Builder, and JavaScript/TypeScript/Node.js patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — BigCommerce's SaaS architecture, Stencil theming engine, REST V2/V3 and GraphQL Storefront APIs, OAuth app flow, Checkout SDK, payment processing, channel-based multi-storefront, webhook system, and widget/Page Builder patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official BigCommerce developer docs before writing code, so you always get the latest API endpoints, Stencil helpers, GraphQL schema, and Catalyst patterns.
- **JavaScript/Node.js expertise included** — 3 dedicated skills for modern JavaScript/TypeScript, Next.js (Catalyst), and Node.js backend patterns, since BigCommerce development heavily uses these technologies.

## Plugin Structure

```
bigcommerce-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── agents/
│   └── bigcommerce-expert.md                      # Subagent: BigCommerce + JS/Node.js expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_bc_commands.py                   # PreToolUse: block destructive Stencil/API commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── bc-setup/SKILL.md                          # Environment setup, Stencil CLI, Catalyst
│   ├── bc-app-dev/SKILL.md                        # Single-click apps, OAuth flow, BigDesign
│   ├── bc-stencil/SKILL.md                        # Stencil themes, Handlebars, front matter
│   ├── bc-api-rest/SKILL.md                       # REST API V2/V3, auth, rate limits, pagination
│   ├── bc-api-graphql/SKILL.md                    # GraphQL Storefront API, tokens, queries
│   ├── bc-webhooks/SKILL.md                       # Webhooks, event topics, payload handling
│   ├── bc-catalog/SKILL.md                        # Products, variants, options, categories, metafields
│   ├── bc-orders/SKILL.md                         # Orders, statuses, shipments, refunds
│   ├── bc-checkout/SKILL.md                       # Checkout SDK, embedded checkout, server-side
│   ├── bc-payments/SKILL.md                       # Payment Processing API, stored instruments
│   ├── bc-customers/SKILL.md                      # Customers, groups, addresses, SSO/Login API
│   ├── bc-headless/SKILL.md                       # Headless commerce, Catalyst, Next.js
│   ├── bc-channels/SKILL.md                       # Multi-channel, multi-storefront, price lists
│   ├── bc-widgets/SKILL.md                        # Widgets, Page Builder, Script Manager
│   ├── bc-testing/SKILL.md                        # API testing, theme testing, E2E, webhooks
│   ├── bc-performance/SKILL.md                    # CDN, image optimization, CWV, caching
│   ├── bc-security/SKILL.md                       # OAuth, JWT, webhook verification, PCI, CSP
│   ├── js-modern/SKILL.md                         # JavaScript ES6+ & TypeScript
│   ├── nextjs-patterns/SKILL.md                   # Next.js App Router, SSR/ISR, Catalyst
│   └── node-backend/SKILL.md                      # Node.js backend for BigCommerce apps
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install bigcommerce-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/bigcommerce-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "bigcommerce-commerce": {
      "type": "local",
      "path": "/path/to/bigcommerce-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `bigcommerce-commerce:bigcommerce-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves BigCommerce:

```
Create a custom Stencil theme for my BigCommerce store
```

```
Build a single-click app that syncs inventory with my ERP
```

```
Set up a headless storefront with Catalyst and Next.js
```

### Explicit invocation

```
Use the bigcommerce-expert subagent to implement a custom payment integration
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest BigCommerce API version and available endpoints
2. Fetch the relevant developer docs for exact REST/GraphQL schemas
3. Check GitHub source for Catalyst patterns and sample apps
4. Write code against verified-current documentation

## Available Skills

### BigCommerce Skills (17)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **bc-setup** | `/bigcommerce-commerce:bc-setup` | Manual | Stencil CLI, Catalyst, API credentials, dev environment |
| **bc-app-dev** | auto | Auto + manual | Single-click apps, OAuth flow, BigDesign, marketplace |
| **bc-stencil** | auto | Auto + manual | Stencil themes, Handlebars, front matter, config/schema |
| **bc-api-rest** | auto | Auto + manual | REST V2/V3, auth, rate limits, pagination, batch ops |
| **bc-api-graphql** | auto | Auto + manual | GraphQL Storefront API, tokens, queries, mutations |
| **bc-webhooks** | auto | Auto + manual | Event topics, payload handling, verification, retries |
| **bc-catalog** | auto | Auto + manual | Products, variants, options, modifiers, categories, metafields |
| **bc-orders** | auto | Auto + manual | Order lifecycle, statuses, shipments, refunds |
| **bc-checkout** | auto | Auto + manual | Checkout SDK, embedded checkout, server-side checkout |
| **bc-payments** | auto | Auto + manual | Payment Processing API, stored instruments, PCI |
| **bc-customers** | auto | Auto + manual | Customer API, groups, addresses, Login API (SSO) |
| **bc-headless** | auto | Auto + manual | Catalyst (Next.js), headless architecture, composable commerce |
| **bc-channels** | auto | Auto + manual | Multi-channel, multi-storefront, price lists, channel API |
| **bc-widgets** | auto | Auto + manual | Widgets, Page Builder, Script Manager, content management |
| **bc-testing** | auto | Auto + manual | API tests, theme tests, E2E, webhook testing, sandbox stores |
| **bc-performance** | auto | Auto + manual | CDN, image optimization, Core Web Vitals, caching |
| **bc-security** | auto | Auto + manual | OAuth tokens, JWT verification, CSP, PCI, input validation |

### Language Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **js-modern** | auto | Auto + manual | JavaScript ES6+ & TypeScript — async, modules, types |
| **nextjs-patterns** | auto | Auto + manual | Next.js App Router — SSR, ISR, Server/Client Components |
| **node-backend** | auto | Auto + manual | Node.js — Express/Fastify, OAuth, JWT, webhook handlers |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Stencil CLI or BigCommerce API command | **Blocks** destructive commands (`stencil push --activate --delete`, `curl DELETE` to products/orders/customers). Warns on impactful operations (`stencil push`, API PUT requests). Only activates for commands containing "stencil" or "bigcommerce". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded API tokens, client secrets, store hashes, Stripe live keys, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## BigCommerce Architecture at a Glance

### Platform Model

| Aspect | Description |
|--------|-------------|
| **Type** | Fully hosted SaaS — no server-side code on BigCommerce |
| **Themes** | Stencil (Handlebars + SCSS + JS) — server-rendered by BigCommerce |
| **Apps** | External services connected via OAuth + REST/GraphQL APIs |
| **Headless** | Catalyst (Next.js) or any frontend framework via APIs |
| **Content** | Widgets + Page Builder for merchant self-service |

### Key Design Patterns

| Pattern | BigCommerce Implementation |
|---------|---------------------------|
| **API-First** | All data access via REST V2/V3 and GraphQL Storefront API |
| **OAuth** | App authentication and authorization for marketplace apps |
| **Webhook** | Event-driven notifications for real-time integrations |
| **Channel** | Multi-storefront isolation with shared backend |
| **Theme Object** | Front matter data injection into Stencil templates |
| **Widget** | Composable content components with JSON schemas |
| **Headless** | Decoupled frontend/backend with Catalyst reference |
| **Embedded Checkout** | PCI-compliant checkout in iframe for headless sites |

### Supported Stack

| Component | Versions/Details |
|-----------|-----------------|
| Stencil CLI | Node.js 18+ |
| Catalyst | Next.js 14+ |
| REST API | V2 (legacy), V3 (current) |
| GraphQL | Storefront API (client-side) |
| Apps | Any server-side language |

*(Always verify against current developer docs)*

## Official References

| Resource | URL |
|----------|-----|
| BigCommerce Dev Center | https://developer.bigcommerce.com/ |
| API Reference | https://developer.bigcommerce.com/docs/rest |
| GraphQL Storefront API | https://developer.bigcommerce.com/docs/storefront/graphql |
| Stencil Docs | https://developer.bigcommerce.com/docs/storefront/stencil |
| Apps Guide | https://developer.bigcommerce.com/docs/integrations/apps |
| Checkout SDK | https://developer.bigcommerce.com/docs/storefront/cart-checkout/checkout-sdk |
| Webhooks | https://developer.bigcommerce.com/docs/integrations/webhooks |
| Multi-Storefront | https://developer.bigcommerce.com/docs/storefront/multi-storefront |
| Catalyst | https://www.catalyst.dev/ |
| Catalyst GitHub | https://github.com/bigcommerce/catalyst |
| BigCommerce GitHub | https://github.com/bigcommerce |
| BigDesign | https://developer.bigcommerce.com/big-design |
| Next.js Docs | https://nextjs.org/docs |
| MDN JavaScript | https://developer.mozilla.org/en-US/docs/Web/JavaScript |
| TypeScript Docs | https://www.typescriptlang.org/docs/ |
