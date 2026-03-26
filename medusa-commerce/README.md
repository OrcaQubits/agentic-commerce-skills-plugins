# Medusa Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **Medusa v2** development — covering custom modules with DML data models, workflow engine with compensation, API routes, subscribers, admin dashboard extensions, Next.js 15 storefronts with JS SDK, payment and fulfillment providers, pricing and promotions, and TypeScript/Node.js/Next.js patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — Medusa's open-source modular architecture, DML data model system, workflow engine with steps and compensation, file-based API routing, event-driven subscribers, admin dashboard widgets, Next.js headless storefronts, and commerce module patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official Medusa developer docs before writing code, so you always get the latest DML syntax, service APIs, workflow patterns, and module configurations.
- **TypeScript/Node.js/Next.js expertise included** — 3 dedicated skills for modern TypeScript, Node.js backend patterns, and Next.js 15 App Router, since Medusa development heavily uses these technologies.

## Plugin Structure

```
medusa-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── agents/
│   └── medusa-expert.md                           # Subagent: Medusa + TS/Node/Next.js expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_medusa_commands.py               # PreToolUse: block destructive Medusa CLI commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── medusa-setup/SKILL.md                      # CLI, PostgreSQL/Redis, project creation
│   ├── medusa-modules/SKILL.md                    # Custom modules, DML models, services, links
│   ├── medusa-workflows/SKILL.md                  # Workflow engine, steps, compensation, hooks
│   ├── medusa-api-routes/SKILL.md                 # File-based routing, middleware, validators
│   ├── medusa-subscribers/SKILL.md                # Event subscribers, scheduled jobs
│   ├── medusa-admin/SKILL.md                      # Admin widgets, UI routes, Medusa UI
│   ├── medusa-plugins/SKILL.md                    # Plugin development, npm packaging
│   ├── medusa-storefront/SKILL.md                 # Next.js 15 starter, JS SDK, Tanstack Query
│   ├── medusa-catalog/SKILL.md                    # Products, variants, collections, categories
│   ├── medusa-orders/SKILL.md                     # Order lifecycle, fulfillment, returns
│   ├── medusa-cart-checkout/SKILL.md              # Cart operations, checkout flow, sales channels
│   ├── medusa-customers/SKILL.md                  # Customer profiles, auth, groups, addresses
│   ├── medusa-payments/SKILL.md                   # Payment providers, sessions, capture/refund
│   ├── medusa-fulfillment/SKILL.md                # Fulfillment providers, shipping options
│   ├── medusa-pricing/SKILL.md                    # Price lists, currencies, tax, promotions
│   ├── medusa-testing/SKILL.md                    # Jest, integration tests, mocks, coverage
│   ├── medusa-security/SKILL.md                   # Auth strategies, API keys, CORS, JWT
│   ├── medusa-deploy/SKILL.md                     # Production build, hosting, env config
│   ├── ts-modern/SKILL.md                         # TypeScript for Medusa — DML types, generics
│   ├── node-backend/SKILL.md                      # Node.js/Express, MikroORM, PostgreSQL
│   └── nextjs-patterns/SKILL.md                   # Next.js 15 App Router for Medusa storefronts
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install medusa-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/medusa-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "medusa-commerce": {
      "type": "local",
      "path": "/path/to/medusa-commerce"
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

Run `/agents` in Claude Code — you should see `medusa-commerce:medusa-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves Medusa:

```
Build a custom Medusa module for product reviews with ratings
```

```
Create a workflow that syncs inventory across multiple warehouses
```

```
Set up a Next.js storefront with custom product filtering
```

### Explicit invocation

```
Use the medusa-expert subagent to implement a custom payment provider
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest Medusa v2 docs and DML syntax
2. Fetch the relevant developer docs for exact module APIs and workflow patterns
3. Check GitHub source for module implementations and storefront templates
4. Write code against verified-current documentation

## Available Skills

### Platform Skills — Core Architecture (8)

| Skill | Command | Description |
|---|---|---|
| **medusa-setup** | `/medusa-commerce:medusa-setup` | CLI, PostgreSQL/Redis, project creation, medusa-config.ts |
| **medusa-modules** | auto | Custom modules, DML data models, services, loaders, links |
| **medusa-workflows** | auto | Workflow engine, steps, compensation, hooks, parallel |
| **medusa-api-routes** | auto | File-based routing, middleware, validators, additional-data |
| **medusa-subscribers** | auto | Event subscribers, scheduled jobs, Redis events |
| **medusa-admin** | auto | Admin widgets, UI routes, Medusa UI components |
| **medusa-plugins** | auto | Plugin development, npm packaging, plugin vs module |
| **medusa-storefront** | auto | Next.js 15, JS SDK, Tanstack Query, server components |

### Platform Skills — Commerce Domain (8)

| Skill | Command | Description |
|---|---|---|
| **medusa-catalog** | auto | Products, variants, options, collections, categories, tags |
| **medusa-orders** | auto | Order lifecycle, fulfillment, returns, exchanges, claims |
| **medusa-cart-checkout** | auto | Cart operations, checkout flow, line items, sales channels |
| **medusa-customers** | auto | Customer profiles, authentication, groups, addresses |
| **medusa-payments** | auto | Payment providers, sessions, authorization/capture/refund |
| **medusa-fulfillment** | auto | Fulfillment providers, shipping options, multi-warehouse |
| **medusa-pricing** | auto | Price lists, currencies, tax, regions, promotions |
| **medusa-testing** | auto | Jest, medusaIntegrationTestRunner, mocks, coverage |

### Platform Skills — Cross-cutting (2)

| Skill | Command | Description |
|---|---|---|
| **medusa-security** | auto | Auth strategies, API keys, CORS, JWT, session management |
| **medusa-deploy** | auto | Production build, server/worker mode, hosting, env config |

### Language Skills (3)

| Skill | Command | Description |
|---|---|---|
| **ts-modern** | auto | TypeScript for Medusa — DML types, generics, container typing |
| **node-backend** | auto | Node.js/Express, MikroORM, PostgreSQL, async patterns |
| **nextjs-patterns** | auto | Next.js 15 App Router, server components, Medusa SDK |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Medusa CLI or database command | **Blocks** destructive commands (`medusa db:rollback`, forced migrations, `rm -rf .medusa`, `DROP TABLE/DATABASE`, `TRUNCATE TABLE`). Warns on impactful operations (`medusa db:migrate`, `medusa build`, `medusa start`). Only activates for commands containing "medusa", "drop", or "truncate". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded secrets: Stripe live keys (`sk_live_`, `pk_live_`), Medusa admin secrets, database URLs with credentials, Redis URLs, JWT/cookie secrets, wildcard CORS (`*`), and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## Medusa v2 Architecture at a Glance

### Platform Model

| Aspect | Description |
|--------|-------------|
| **Type** | Open-source, self-hosted headless commerce (Node.js/TypeScript) |
| **Modules** | Isolated commerce domains — DML models, services, loaders |
| **Workflows** | Durable multi-step orchestration with compensation |
| **API** | REST (Admin + Store), file-based custom routes |
| **Admin** | React dashboard, extensible via widgets and UI routes |
| **Storefront** | Headless — Next.js 15 with JS SDK and Tanstack Query |

### Commerce Modules

| Module | Responsibility |
|--------|---------------|
| **Product** | Products, variants, options, collections, categories |
| **Order** | Orders, fulfillments, returns, exchanges, claims |
| **Cart** | Cart lifecycle, line items, checkout completion |
| **Customer** | Profiles, authentication, groups, addresses |
| **Payment** | Payment sessions, providers, capture/refund |
| **Fulfillment** | Shipping providers, options, fulfillment sets |
| **Pricing** | Price lists, currencies, tax calculation |
| **Promotion** | Discount campaigns, rules, automatic/manual |
| **Region** | Regions, currencies, tax, provider configuration |
| **Inventory** | Stock levels, reservations, multi-warehouse |

### Supported Stack

| Component | Details |
|-----------|---------|
| Runtime | Node.js 20+, TypeScript 5+ |
| Database | PostgreSQL (required) |
| Cache/Events | Redis (optional, recommended for production) |
| ORM | MikroORM (via DML abstraction) |
| Admin | React, Vite, Medusa UI components |
| Storefront | Next.js 15 (App Router), Medusa JS SDK |
| API | REST (Admin + Store), OpenAPI spec |
| CLI | `npx medusa` / `@medusajs/medusa-cli` |

### Deprecated v1 Patterns

| v1 Pattern | Use Instead (v2) |
|------------|-------------------|
| TypeORM entities | DML data models (`model.define()`) |
| `medusa-interfaces` (BaseService) | `MedusaService` from generated types |
| `inventory_quantity` on variant | Inventory Module with stock locations |
| `medusa-extender` package | Native module system |
| Subscriber class pattern | Functional subscriber exports |
| `medusa-config.js` | `medusa-config.ts` (TypeScript) |
| Custom endpoints via services | API routes in `src/api/` directory |

*(Always verify against current developer docs)*

## Official References

| Resource | URL |
|----------|-----|
| Medusa Docs | https://docs.medusajs.com/ |
| Learning Path | https://docs.medusajs.com/learn |
| Admin API Reference | https://docs.medusajs.com/api/admin |
| Store API Reference | https://docs.medusajs.com/api/store |
| JS SDK Reference | https://docs.medusajs.com/resources/references/js-sdk |
| Medusa GitHub | https://github.com/medusajs/medusa |
| Next.js Starter | https://github.com/medusajs/nextjs-starter-medusa |
| CLI Reference | https://docs.medusajs.com/learn/fundamentals/cli |
| Commerce Modules | https://docs.medusajs.com/resources/commerce-modules |
| Medusa UI (GitHub) | https://github.com/medusajs/ui |
| TypeScript Docs | https://www.typescriptlang.org/docs/ |
| Next.js Docs | https://nextjs.org/docs |
| Node.js Docs | https://nodejs.org/docs/latest/api/ |
| Discord Community | https://discord.gg/medusajs |

## License

MIT — see [LICENSE](../LICENSE) for details.
