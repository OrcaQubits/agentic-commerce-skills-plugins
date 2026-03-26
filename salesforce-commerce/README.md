# Salesforce Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **Salesforce Commerce** development — covering both **B2C Commerce Cloud** (SFCC/Demandware) with SFRA cartridges, ISML templating, SCAPI/OCAPI APIs, PWA Kit headless storefronts, and **B2B/D2C Commerce on Lightning** with Apex hooks, LWC components, Experience Builder, Einstein AI recommendations, Salesforce Payments, and JavaScript/TypeScript/React patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — Salesforce's dual-platform model (B2C Commerce Cloud + B2B/D2C Lightning), cartridge overlay architecture, SFRA MVC pattern, ISML templating, Apex commerce hooks, LWC component model, Experience Builder, SCAPI vs OCAPI distinction, PWA Kit (React) headless framework, Einstein AI recommendations, and SLAS/OAuth authentication patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official Salesforce developer docs before writing code, so you always get the latest SCAPI schemas, SDK methods, Apex hook interfaces, and LWC APIs.
- **JavaScript/TypeScript/React expertise included** — 3 dedicated skills for modern JavaScript/TypeScript, React patterns (PWA Kit is React-based, NOT Remix/Next.js), and Node.js backend, since Salesforce Commerce development heavily uses these technologies.

## Plugin Structure

```
salesforce-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── agents/
│   └── salesforce-expert.md                       # Subagent: Salesforce Commerce + JS/TS/React expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_salesforce_commands.py            # PreToolUse: block destructive sfcc-ci/sf commands
│       └── check_secrets.py                        # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── sf-setup/SKILL.md                          # Environment setup, CLIs, sandboxes
│   ├── sf-b2c-sfra/SKILL.md                       # SFRA architecture, cartridge overlay, MVC
│   ├── sf-b2c-cartridges/SKILL.md                 # Cartridge structure, stacking, naming
│   ├── sf-b2c-controllers/SKILL.md                # Controllers, middleware chain, CSRF
│   ├── sf-b2c-isml/SKILL.md                       # ISML templates, tags, expressions
│   ├── sf-b2c-scapi/SKILL.md                      # SCAPI Shopper APIs, SLAS, Commerce SDK
│   ├── sf-b2c-ocapi/SKILL.md                      # OCAPI (deprecated — migration skill)
│   ├── sf-b2c-pwa-kit/SKILL.md                    # PWA Kit (React), Managed Runtime, SSR
│   ├── sf-b2c-jobs/SKILL.md                       # Job framework, scheduling, import/export
│   ├── sf-b2b-apex/SKILL.md                       # Apex commerce hooks, governor limits
│   ├── sf-b2b-lwc/SKILL.md                        # LWC components, wire adapters, Jest
│   ├── sf-b2b-experience/SKILL.md                 # Experience Builder, LWR, page types
│   ├── sf-catalog/SKILL.md                        # Catalogs, products, pricing (B2C + B2B)
│   ├── sf-orders/SKILL.md                         # Order lifecycle, fulfillment (B2C + B2B)
│   ├── sf-customers/SKILL.md                      # Customers, buyer groups (B2C + B2B)
│   ├── sf-payments/SKILL.md                       # Salesforce Payments, Stripe, PCI
│   ├── sf-einstein/SKILL.md                       # Einstein Recommendations, Data Cloud
│   ├── sf-integrations/SKILL.md                   # Webhooks, Platform Events, CDC
│   ├── sf-testing/SKILL.md                        # Testing (Node.js + Apex + Jest)
│   ├── sf-performance/SKILL.md                    # Caching, CDN, SOQL, Core Web Vitals
│   ├── sf-security/SKILL.md                       # SLAS, OAuth, CSRF, XSS, PCI
│   ├── js-modern/SKILL.md                         # JavaScript ES6+ & TypeScript
│   ├── react-patterns/SKILL.md                    # React (PWA Kit is React, NOT Remix)
│   └── node-backend/SKILL.md                      # SFCC server-side JS, PWA Kit backend
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install salesforce-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/salesforce-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "salesforce-commerce": {
      "type": "local",
      "path": "/path/to/salesforce-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `salesforce-commerce:salesforce-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves Salesforce Commerce:

```
Build an SFRA cartridge for custom product recommendations
```

```
Create a PWA Kit storefront with product search and filtering
```

```
Implement a B2B Commerce checkout with custom pricing hooks
```

### Explicit invocation

```
Use the salesforce-expert subagent to implement SCAPI basket management
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest SCAPI schemas and Commerce SDK methods
2. Fetch the relevant developer docs for exact API endpoints and parameters
3. Check GitHub source for SFRA, PWA Kit, and Commerce SDK patterns
4. Write code against verified-current documentation

## Available Skills

### B2C Commerce Cloud Skills (9)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **sf-b2c-sfra** | auto | Auto + manual | SFRA architecture, cartridge overlay, MVC, module.superModule |
| **sf-b2c-cartridges** | auto | Auto + manual | Cartridge structure, stacking, naming conventions |
| **sf-b2c-controllers** | auto | Auto + manual | Controllers, middleware chain, CSRF, form validation |
| **sf-b2c-isml** | auto | Auto + manual | ISML templates, tags, expressions, decorators |
| **sf-b2c-scapi** | auto | Auto + manual | SCAPI Shopper APIs, SLAS auth, Commerce SDK |
| **sf-b2c-ocapi** | auto | Auto + manual | OCAPI (deprecated) — migration guide, endpoint mappings |
| **sf-b2c-pwa-kit** | auto | Auto + manual | PWA Kit (React), Managed Runtime, Commerce SDK, SSR |
| **sf-b2c-jobs** | auto | Auto + manual | Job framework, scheduling, import/export, monitoring |
| **sf-setup** | `/salesforce-commerce:sf-setup` | Manual | sfcc-ci, sf CLI, sandboxes, project structures |

### B2B/D2C Commerce on Lightning Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **sf-b2b-apex** | auto | Auto + manual | Apex commerce hooks, governor limits, test coverage |
| **sf-b2b-lwc** | auto | Auto + manual | LWC components, wire adapters, Jest testing |
| **sf-b2b-experience** | auto | Auto + manual | Experience Builder, LWR, page types, components |

### Cross-Platform Skills (9)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **sf-catalog** | auto | Auto + manual | Catalogs, products, pricing (B2C + B2B) |
| **sf-orders** | auto | Auto + manual | Order lifecycle, fulfillment, returns (B2C + B2B) |
| **sf-customers** | auto | Auto + manual | Customers, buyer groups, SLAS (B2C + B2B) |
| **sf-payments** | auto | Auto + manual | Salesforce Payments (Stripe), PCI, 3DS |
| **sf-einstein** | auto | Auto + manual | Einstein Recommendations, Data Cloud personalization |
| **sf-integrations** | auto | Auto + manual | Webhooks, Platform Events, CDC, HMAC |
| **sf-testing** | auto | Auto + manual | Node.js + Apex + Jest testing, CI/CD |
| **sf-performance** | auto | Auto + manual | Caching, CDN, SOQL optimization, CWV |
| **sf-security** | auto | Auto + manual | SLAS, OAuth, CSRF, XSS, PCI, OWASP |

### Language Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **js-modern** | auto | Auto + manual | JavaScript ES6+ & TypeScript — SFCC, PWA Kit, LWC contexts |
| **react-patterns** | auto | Auto + manual | React (PWA Kit is React, NOT Remix/Next.js) |
| **node-backend** | auto | Auto + manual | SFCC server-side JS, PWA Kit backend, Commerce SDK |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Salesforce CLI command | **Blocks** destructive commands (`sfcc-ci code:activate` on production, `sfcc-ci code:delete`, `sfcc-ci sandbox:delete`, `sf org delete`, `sf project deploy start` to production, `curl DELETE` to salesforce.com/demandware.net). Warns on impactful operations (`sfcc-ci code:activate`, `sfcc-ci instance:upload`, `sf project deploy start`, `sf org login`). Only activates for commands containing "sfcc", "salesforce", "demandware", or "sfdx". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Salesforce secrets (Commerce client IDs/secrets, SFCC OAuth credentials, SF access tokens, SFDX auth URLs, JWT tokens, dw.json passwords, private keys, Stripe live keys, Salesforce Org IDs). Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## Architecture at a Glance

### Two-Platform Model

| Aspect | B2C Commerce Cloud (SFCC) | B2B/D2C Commerce on Lightning |
|--------|--------------------------|-------------------------------|
| **Origin** | Demandware (acquired 2016) | Built on Salesforce Platform |
| **Server-side** | JavaScript (CommonJS) | Apex |
| **Templates** | ISML | LWC (HTML + JS) |
| **Headless** | PWA Kit (React) | LWC Experience Sites |
| **APIs** | SCAPI (primary), OCAPI (deprecated) | Salesforce REST/SOAP, Connect API |
| **Admin** | Business Manager | Salesforce Setup / Experience Builder |
| **CLI** | sfcc-ci | sf CLI |
| **Data model** | Custom (catalogs, content slots) | Standard Salesforce objects |
| **Deployment** | Code versions via sfcc-ci | Metadata via sf CLI |
| **Testing** | Node.js unit tests | Apex tests (75%), Jest for LWC |
| **AI** | Einstein Recommendations | Einstein + Data Cloud |

### Deprecated Technologies

| Technology | Status | Use Instead |
|------------|--------|-------------|
| OCAPI | Maintenance-only — no new features | SCAPI |
| SiteGenesis | Legacy architecture | SFRA |
| Pipelines | Legacy controller model | SFRA controllers |
| Link Cartridges | Legacy integration pattern | SFRA cartridges |

*(Always verify against current developer docs)*

## Official References

| Resource | URL |
|----------|-----|
| Salesforce Dev Center | https://developer.salesforce.com/ |
| B2C Commerce Docs | https://developer.salesforce.com/docs/commerce/b2c-commerce/overview |
| SFRA Guide | https://developer.salesforce.com/docs/commerce/sfra/overview |
| SCAPI Reference | https://developer.salesforce.com/docs/commerce/commerce-api/overview |
| OCAPI Reference | https://developer.salesforce.com/docs/commerce/b2c-commerce/references/ocapi |
| PWA Kit Docs | https://developer.salesforce.com/docs/commerce/pwa-kit-managed-runtime/overview |
| Commerce SDK (GitHub) | https://github.com/SalesforceCommerceCloud/commerce-sdk |
| PWA Kit (GitHub) | https://github.com/SalesforceCommerceCloud/pwa-kit |
| SFRA (GitHub) | https://github.com/SalesforceCommerceCloud/storefront-reference-architecture |
| B2B Commerce Dev Guide | https://developer.salesforce.com/docs/atlas.en-us.b2b_comm_lex_dev.meta/b2b_comm_lex_dev |
| LWC Dev Guide | https://developer.salesforce.com/docs/platform/lwc/guide |
| Apex Dev Guide | https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode |
| Einstein Commerce | https://developer.salesforce.com/docs/commerce/b2c-commerce/guide/einstein-recommendations.html |
| sfcc-ci (GitHub) | https://github.com/SalesforceCommerceCloud/sfcc-ci |
| Salesforce CLI Ref | https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference |
| Trailhead Commerce | https://trailhead.salesforce.com/content/learn/trails/develop-for-commerce-cloud |
