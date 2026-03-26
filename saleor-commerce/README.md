# Saleor Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **Saleor** development — covering the GraphQL-only API with Graphene-Django, App development with Next.js SDK and App Bridge, async/sync webhooks with subscription payloads, Dashboard extensions with MacawUI, Next.js storefronts, multi-channel commerce, typed attribute system, transaction-based payment flow, and Python/Django/GraphQL/Next.js patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — Saleor's open-source GraphQL-only architecture, App extension model, webhook system with subscription payloads, Dashboard mounting points, multi-channel commerce, typed attribute system, transaction payment flow, and commerce module patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official Saleor developer docs before writing code, so you always get the latest GraphQL schema, App SDK methods, webhook events, and Dashboard APIs.
- **Python/Django/GraphQL/Next.js expertise included** — 3 dedicated skills for Python/Django backend patterns, GraphQL development, and Next.js App Router, since Saleor development heavily uses these technologies.

## Plugin Structure

```
saleor-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── agents/
│   └── saleor-expert.md                           # Subagent: Saleor + Python/GraphQL/Next.js expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_saleor_commands.py               # PreToolUse: block destructive Django/Saleor commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── saleor-setup/SKILL.md                      # Docker Compose, CLI, PostgreSQL/Redis, env config
│   ├── saleor-graphql/SKILL.md                    # GraphQL queries, mutations, subscriptions, codegen
│   ├── saleor-apps/SKILL.md                       # App manifest, SDK, App Bridge, permissions, APL
│   ├── saleor-webhooks/SKILL.md                   # Async/sync events, subscription payloads, JWS/HMAC
│   ├── saleor-dashboard/SKILL.md                  # Mounting points, App Bridge, MacawUI, iframes
│   ├── saleor-storefront/SKILL.md                 # Next.js, GraphQL client, channel routing, SSR
│   ├── saleor-channels/SKILL.md                   # Multi-currency, multi-region, warehouse allocation
│   ├── saleor-attributes/SKILL.md                 # Typed attributes, product types, page types
│   ├── saleor-catalog/SKILL.md                    # Products, variants, categories, collections, media
│   ├── saleor-orders/SKILL.md                     # Order lifecycle, fulfillments, returns, events
│   ├── saleor-checkout/SKILL.md                   # Checkout flow, line items, payment, completion
│   ├── saleor-customers/SKILL.md                  # Customer accounts, staff, permissions, addresses
│   ├── saleor-payments/SKILL.md                   # Transaction flow, payment Apps, Stripe/Adyen
│   ├── saleor-shipping/SKILL.md                   # Zones, methods, custom shipping Apps, pickup
│   ├── saleor-promotions/SKILL.md                 # Promotions, vouchers, gift cards, discounts
│   ├── saleor-testing/SKILL.md                    # Pytest, Django test client, factory_boy, GraphQL
│   ├── saleor-security/SKILL.md                   # JWT, OIDC, App tokens, permissions, CORS
│   ├── saleor-deploy/SKILL.md                     # Docker, Saleor Cloud, Celery, S3, scaling
│   ├── python-django/SKILL.md                     # Django ORM, signals, Celery, typing, migrations
│   ├── graphql-dev/SKILL.md                       # Queries, fragments, codegen, TypedDocumentNode
│   └── nextjs-react/SKILL.md                      # App Router, server components, GraphQL, MacawUI
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install saleor-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/saleor-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "saleor-commerce": {
      "type": "local",
      "path": "/path/to/saleor-commerce"
    }
  }
}
```

### Other IDEs / Agents

See the installation guides for other environments:
- [Antigravity](./INSTALL-ANTIGRAVITY.md)
- [Codex](./INSTALL-CODEX.md)
- [Cursor](./INSTALL-CURSOR.md)
- [Gemini](./INSTALL-GEMINI.md)
- [OpenClaw](./INSTALL-OPENCLAW.md)

### Verify

Run `/agents` in Claude Code — you should see `saleor-commerce:saleor-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves Saleor:

```
Build a Saleor App that syncs products to an external PIM
```

```
Create a custom payment App with Stripe for Saleor's transaction flow
```

```
Set up a Next.js storefront with multi-channel support and checkout
```

### Explicit invocation

```
Use the saleor-expert subagent to implement a custom shipping App
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest Saleor docs and GraphQL schema
2. Fetch the relevant developer docs for exact App SDK methods and webhook events
3. Check GitHub source for App implementations and storefront templates
4. Write code against verified-current documentation

## Available Skills

### Platform Skills — Core Architecture (8)

| Skill | Command | Description |
|---|---|---|
| **saleor-setup** | `/saleor-commerce:saleor-setup` | Docker Compose, CLI, PostgreSQL/Redis, env config |
| **saleor-graphql** | auto | GraphQL queries, mutations, subscriptions, codegen |
| **saleor-apps** | auto | App manifest, SDK, App Bridge, permissions, APL |
| **saleor-webhooks** | auto | Async/sync events, subscription payloads, JWS/HMAC |
| **saleor-dashboard** | auto | Mounting points, App Bridge, MacawUI, iframes |
| **saleor-storefront** | auto | Next.js, GraphQL client, channel routing, SSR |
| **saleor-channels** | auto | Multi-currency, multi-region, warehouse allocation |
| **saleor-attributes** | auto | Typed attributes, product types, page types |

### Platform Skills — Commerce Domain (8)

| Skill | Command | Description |
|---|---|---|
| **saleor-catalog** | auto | Products, variants, product types, categories, collections |
| **saleor-orders** | auto | Order lifecycle, fulfillments, returns, draft orders |
| **saleor-checkout** | auto | Checkout flow, line items, payment, completion |
| **saleor-customers** | auto | Customer accounts, staff, permissions, addresses |
| **saleor-payments** | auto | Transaction flow, payment Apps, Stripe/Adyen |
| **saleor-shipping** | auto | Zones, methods, custom shipping Apps, pickup |
| **saleor-promotions** | auto | Promotions, vouchers, gift cards, discounts |
| **saleor-testing** | auto | Pytest, Django test client, factory_boy, GraphQL tests |

### Platform Skills — Cross-cutting (2)

| Skill | Command | Description |
|---|---|---|
| **saleor-security** | auto | JWT, OIDC, App tokens, permissions, CORS |
| **saleor-deploy** | auto | Docker, Saleor Cloud, Celery, S3, scaling |

### Language Skills (3)

| Skill | Command | Description |
|---|---|---|
| **python-django** | auto | Django ORM, signals, Celery, typing, migrations |
| **graphql-dev** | auto | Queries, fragments, codegen, TypedDocumentNode |
| **nextjs-react** | auto | App Router, server components, GraphQL, MacawUI |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Saleor/Django or database command | **Blocks** destructive commands (`manage.py flush`, `manage.py reset_db`, fake migrations, `DROP TABLE/DATABASE`, `TRUNCATE TABLE`, `rm -rf` on Saleor/media dirs, `docker-compose down -v`). Warns on impactful operations (`manage.py migrate`, `createsuperuser`, `docker-compose up`, `saleor deploy`, `celery purge`). Only activates for commands containing "manage.py", "saleor", "drop", "truncate", "celery", or "docker". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded secrets: Stripe live keys (`sk_live_`, `pk_live_`), Django `SECRET_KEY`, database URLs with credentials, Redis/Celery broker URLs, wildcard `ALLOWED_HOSTS`, Saleor secrets, JWT secrets, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in Path.

## Saleor Architecture at a Glance

### Platform Model

| Aspect | Description |
|--------|-------------|
| **Type** | Open-source headless commerce (Python/Django, BSD-3-Clause) |
| **API** | GraphQL-only (Graphene-Django) — no REST |
| **Extensions** | Apps (standalone web apps with manifest, webhooks, Dashboard mounting) |
| **Webhooks** | Async + sync events with GraphQL subscription payloads |
| **Dashboard** | React admin UI, extensible via App Bridge and MacawUI |
| **Storefront** | Headless — Next.js with GraphQL client and channel routing |
| **Multi-channel** | Per-channel currencies, countries, warehouses, pricing |

### Commerce Domains

| Domain | Responsibility |
|--------|---------------|
| **Catalog** | Products, product types, variants, categories, collections |
| **Attributes** | Typed attributes on products, variants, and pages |
| **Orders** | Order lifecycle, fulfillments, returns, refunds, events |
| **Checkout** | Checkout creation, line management, shipping/payment, completion |
| **Customers** | Accounts, addresses, staff users, permission groups |
| **Payments** | Transaction-based flow, payment Apps, refunds |
| **Shipping** | Zones, methods, custom shipping Apps, warehouse pickup |
| **Promotions** | Catalog/order promotions, vouchers, gift cards |
| **Channels** | Multi-currency, multi-region, warehouse allocation |

### Supported Stack

| Component | Details |
|-----------|---------|
| Runtime | Python 3.12+, Django 4.x+ |
| Database | PostgreSQL (required) |
| Task Queue | Celery with Redis broker |
| Cache | Redis |
| API | GraphQL (Graphene-Django) |
| Dashboard | React, TypeScript, MacawUI |
| Storefront | Next.js, TypeScript, urql/Apollo, Tailwind |
| Apps | Next.js, saleor-app-sdk, App Bridge |
| CLI | `saleor` CLI (npm package) |

### Deprecated Patterns

| Deprecated | Use Instead |
|------------|-------------|
| Legacy plugins (BasePlugin/PluginsManager) | Apps with webhooks |
| Built-in payment gateways | Payment Apps with transaction flow |
| `checkout.payments` (old model) | Transaction-based payment flow |
| `order.payments` (old model) | `order.transactions` |
| Direct ORM access from extensions | GraphQL API or webhooks |
| Webhook HMAC-SHA256 signing | JWS with RS256 (default since 3.5+) |

*(Always verify against current developer docs)*

## Official References

| Resource | URL |
|----------|-----|
| Saleor Docs | https://docs.saleor.io/ |
| API Reference | https://docs.saleor.io/api-reference |
| Saleor GitHub | https://github.com/saleor/saleor |
| Dashboard GitHub | https://github.com/saleor/saleor-dashboard |
| Storefront GitHub | https://github.com/saleor/storefront |
| App Template | https://github.com/saleor/saleor-app-template |
| saleor-platform | https://github.com/saleor/saleor-platform |
| App SDK (GitHub) | https://github.com/saleor/app-sdk |
| MacawUI (GitHub) | https://github.com/saleor/macaw-ui |
| Saleor CLI | https://docs.saleor.io/cli |
| Saleor Cloud | https://cloud.saleor.io/ |
| Python Docs | https://docs.python.org/3/ |
| Django Docs | https://docs.djangoproject.com/ |
| Next.js Docs | https://nextjs.org/docs |
| Discord Community | https://discord.gg/H52JTZAtSH |

## License

MIT — see [LICENSE](../LICENSE) for details.
