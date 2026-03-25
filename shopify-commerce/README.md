# Shopify Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **Shopify** development — covering GraphQL Admin and Storefront APIs, Liquid templating, Online Store 2.0 themes, Hydrogen/Remix headless storefronts, Shopify Functions, checkout UI extensions, Polaris components, app development with App Bridge, webhooks, and JavaScript/TypeScript/React patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — Shopify's SaaS platform model, GraphQL-first APIs, Liquid templating engine, Online Store 2.0 theme architecture, Hydrogen/Remix headless framework, Functions (Wasm) extension model, checkout UI extensions, Polaris design system, and App Bridge patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official Shopify developer docs before writing code, so you always get the latest API versions, GraphQL schemas, Liquid objects/filters, and extension targets.
- **JavaScript/TypeScript/React expertise included** — 3 dedicated skills for modern JavaScript/TypeScript, React/Remix patterns, and Node.js backend, since Shopify development heavily uses these technologies.

## Plugin Structure

```
shopify-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── agents/
│   └── shopify-expert.md                          # Subagent: Shopify + JS/TS/React expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_shopify_commands.py              # PreToolUse: block destructive Shopify CLI commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── shopify-setup/SKILL.md                     # Environment setup, Shopify CLI, dev stores
│   ├── shopify-app-dev/SKILL.md                   # App development, Remix template, App Bridge
│   ├── shopify-api-graphql/SKILL.md               # GraphQL Admin + Storefront APIs
│   ├── shopify-api-rest/SKILL.md                  # REST API (deprecated — migration skill)
│   ├── shopify-liquid/SKILL.md                    # Liquid objects, tags, filters, section schema
│   ├── shopify-themes/SKILL.md                    # Online Store 2.0, sections/blocks, Dawn
│   ├── shopify-hydrogen/SKILL.md                  # Hydrogen/Remix, Oxygen, caching, cart
│   ├── shopify-functions/SKILL.md                 # Shopify Functions (Wasm), discounts, delivery
│   ├── shopify-checkout-ui/SKILL.md               # Checkout UI extensions, targets, primitives
│   ├── shopify-catalog/SKILL.md                   # Products, variants, collections, metafields
│   ├── shopify-orders/SKILL.md                    # Order lifecycle, fulfillment, returns
│   ├── shopify-customers/SKILL.md                 # Customer accounts, Multipass SSO, B2B
│   ├── shopify-payments/SKILL.md                  # Shopify Payments, Payment Apps API, Billing
│   ├── shopify-webhooks/SKILL.md                  # Webhooks, HMAC, GDPR, delivery methods
│   ├── shopify-polaris/SKILL.md                   # Polaris components, design tokens, draggable
│   ├── shopify-testing/SKILL.md                   # App/theme/function testing, CI/CD
│   ├── shopify-performance/SKILL.md               # Liquid perf, CWV, caching, image optimization
│   ├── shopify-security/SKILL.md                  # HMAC, session tokens, OAuth, CSP, GDPR
│   ├── js-modern/SKILL.md                         # JavaScript ES6+ & TypeScript
│   ├── react-patterns/SKILL.md                    # React + Remix (loaders, actions, streaming)
│   └── node-backend/SKILL.md                      # Node.js backend for Shopify apps
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install shopify-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/shopify-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "shopify-commerce": {
      "type": "local",
      "path": "/path/to/shopify-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `shopify-commerce:shopify-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves Shopify:

```
Build a custom Shopify theme with product filtering
```

```
Create a Shopify app that syncs inventory with my warehouse
```

```
Set up a Hydrogen storefront with custom product pages
```

### Explicit invocation

```
Use the shopify-expert subagent to implement a custom discount function
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest Shopify API version and GraphQL schema
2. Fetch the relevant developer docs for exact queries, mutations, and extension APIs
3. Check GitHub source for Dawn, Hydrogen, and app template patterns
4. Write code against verified-current documentation

## Available Skills

### Shopify Skills (18)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **shopify-setup** | `/shopify-commerce:shopify-setup` | Manual | Shopify CLI, Partner account, dev stores, project structures |
| **shopify-app-dev** | auto | Auto + manual | Remix template, App Bridge, session tokens, OAuth, extensions |
| **shopify-api-graphql** | auto | Auto + manual | Admin + Storefront APIs, versioning, rate limits, bulk ops |
| **shopify-api-rest** | auto | Auto + manual | REST API (deprecated) — migration guide, endpoint mappings |
| **shopify-liquid** | auto | Auto + manual | Objects, tags, filters, section schema, JSON templates |
| **shopify-themes** | auto | Auto + manual | Online Store 2.0, sections/blocks, Dawn, Theme Check |
| **shopify-hydrogen** | auto | Auto + manual | Remix-based headless, Oxygen, caching, cart, SEO |
| **shopify-functions** | auto | Auto + manual | Wasm functions — discounts, delivery, payment, cart |
| **shopify-checkout-ui** | auto | Auto + manual | Extension targets, UI primitives, checkout APIs |
| **shopify-catalog** | auto | Auto + manual | Products, variants, collections, metafields/metaobjects |
| **shopify-orders** | auto | Auto + manual | Order lifecycle, FulfillmentOrder, returns, draft orders |
| **shopify-customers** | auto | Auto + manual | Customer accounts, Multipass SSO, segmentation, B2B |
| **shopify-payments** | auto | Auto + manual | Shopify Payments, Payment Apps API, Billing API |
| **shopify-webhooks** | auto | Auto + manual | HMAC verification, GDPR mandatory, delivery methods |
| **shopify-polaris** | auto | Auto + manual | Components, design tokens, Web Components, @shopify/draggable |
| **shopify-testing** | auto | Auto + manual | Vitest, Playwright, Theme Check, function testing, CI/CD |
| **shopify-performance** | auto | Auto + manual | Liquid perf, Core Web Vitals, Hydrogen caching, CDN |
| **shopify-security** | auto | Auto + manual | HMAC, session tokens, OAuth scopes, CSP, GDPR webhooks |

### Language Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **js-modern** | auto | Auto + manual | JavaScript ES6+ & TypeScript — async, modules, types |
| **react-patterns** | auto | Auto + manual | React + Remix — loaders, actions, streaming SSR, hooks |
| **node-backend** | auto | Auto + manual | Node.js — Remix server, @shopify/shopify-app-remix, sessions |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Shopify CLI or Shopify API command | **Blocks** destructive commands (`shopify theme push --live`, `shopify theme delete`, `shopify app deploy --force`, `curl DELETE` to myshopify.com). Warns on impactful operations (`shopify theme push`, `shopify app deploy`, `shopify app release`). Only activates for commands containing "shopify" or "myshopify.com". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Shopify access tokens (`shpat_`, `shpss_`, `shpca_`, `shppa_`, `shpua_`), API keys/secrets, Storefront tokens, Multipass secrets, Stripe live keys, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## Shopify Architecture at a Glance

### Platform Model

| Aspect | Description |
|--------|-------------|
| **Type** | Fully hosted SaaS — no server-side code on Shopify (except Functions) |
| **Themes** | Liquid templates, Online Store 2.0, sections/blocks, Dawn reference |
| **Apps** | Remix-based, embedded in admin via App Bridge, OAuth + session tokens |
| **Headless** | Hydrogen (Remix) on Oxygen or any host, Storefront API |
| **Functions** | JavaScript/Rust → WebAssembly, 11M instruction limit, pure computation |
| **Checkout** | Shopify-hosted, extensible via Functions + Checkout UI extensions |

### Extension Models

| Model | What It Extends | How |
|-------|----------------|-----|
| **Themes** | Storefront appearance | Liquid templates, sections, blocks |
| **Apps** | Admin + storefront | External service via OAuth + APIs |
| **Functions** | Backend logic | Wasm (discounts, shipping, payments) |
| **Checkout UI** | Checkout experience | UI primitives at extension targets |
| **Headless** | Entire storefront | Custom React frontend via Storefront API |

### Supported Stack

| Component | Versions/Details |
|-----------|-----------------|
| APIs | GraphQL Admin, GraphQL Storefront (REST deprecated) |
| Themes | Liquid, Online Store 2.0, Dawn |
| Apps | Remix (official), Node.js 18+ |
| Headless | Hydrogen (Remix), Oxygen |
| Functions | JavaScript/Rust → Wasm |
| Checkout UI | Preact/Remote DOM, Shopify UI primitives |
| Admin UI | Polaris (Web Components + React legacy) |
| CLI | Shopify CLI (`shopify` command) |

### Deprecated Technologies

| Technology | Status | Use Instead |
|------------|--------|-------------|
| REST Admin API | Deprecated Oct 2024 | GraphQL Admin API |
| JS Buy SDK | EOL July 2025 | Storefront API / Hydrogen |
| Polaris React | Maintenance mode | Polaris Web Components |
| Slate | Deprecated | Shopify CLI |
| Theme Kit | Legacy | Shopify CLI (`shopify theme`) |
| Timber | Deprecated | Dawn reference theme |
| App Bridge v1/v2 | Superseded | App Bridge (current) |

*(Always verify against current developer docs)*

## Official References

| Resource | URL |
|----------|-----|
| Shopify Dev Center | https://shopify.dev/ |
| GraphQL Admin API | https://shopify.dev/docs/api/admin-graphql |
| Storefront API | https://shopify.dev/docs/api/storefront |
| Liquid Reference | https://shopify.dev/docs/api/liquid |
| Theme Docs | https://shopify.dev/docs/storefronts/themes |
| Hydrogen Docs | https://shopify.dev/docs/storefronts/headless/hydrogen |
| Shopify Functions | https://shopify.dev/docs/apps/build/functions |
| Checkout Extensions | https://shopify.dev/docs/apps/build/checkout |
| App Bridge | https://shopify.dev/docs/apps/build/app-bridge |
| Polaris | https://polaris.shopify.com/ |
| Shopify CLI | https://shopify.dev/docs/api/shopify-cli |
| Dawn (GitHub) | https://github.com/Shopify/dawn |
| Hydrogen (GitHub) | https://github.com/Shopify/hydrogen |
| Remix Docs | https://remix.run/docs |
| MDN JavaScript | https://developer.mozilla.org/en-US/docs/Web/JavaScript |
| TypeScript Docs | https://www.typescriptlang.org/docs/ |
