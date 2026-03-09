# WooCommerce Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **WooCommerce** development — covering plugin/extension architecture, hooks/filters, CRUD data stores, HPOS, REST API, checkout blocks, payment gateways, shipping methods, catalog, admin UI, Gutenberg blocks, testing, deployment, security, and modern PHP 8.x patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — WooCommerce's hook-based architecture, CRUD data stores, HPOS order storage, payment gateway API, shipping method API, block-based checkout, template override system, and WordPress plugin patterns that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official WooCommerce and WordPress developer docs before writing code, so you always get the latest hook names, class signatures, REST API endpoints, and block checkout patterns.
- **PHP expertise included** — 3 dedicated PHP skills for modern PHP 8.x features, design patterns, and PHPUnit testing, since WooCommerce is built on WordPress/PHP.

## Plugin Structure

```
woocommerce-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── .lsp.json                                      # PHP Intelephense language server config
├── agents/
│   └── woocommerce-expert.md                      # Subagent: WooCommerce + PHP expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_woo_commands.py                  # PreToolUse: block destructive WP-CLI commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded secrets
├── skills/
│   ├── woo-setup/SKILL.md                         # Installation & environment setup
│   ├── woo-plugin-dev/SKILL.md                    # Extension/plugin creation & structure
│   ├── woo-hooks-filters/SKILL.md                 # WordPress hooks, WooCommerce hooks
│   ├── woo-data-stores/SKILL.md                   # CRUD objects, data stores, HPOS
│   ├── woo-custom-fields/SKILL.md                 # Product attributes, meta, taxonomies
│   ├── woo-api/SKILL.md                           # REST API v3, webhooks, authentication
│   ├── woo-blocks/SKILL.md                        # Gutenberg blocks, checkout blocks, Store API
│   ├── woo-frontend/SKILL.md                      # Templates, theme integration, asset loading
│   ├── woo-admin/SKILL.md                         # Settings pages, admin menus, product panels
│   ├── woo-checkout/SKILL.md                      # Classic & block checkout, custom fields
│   ├── woo-catalog/SKILL.md                       # Products, categories, attributes, queries
│   ├── woo-payments/SKILL.md                      # Payment gateway development
│   ├── woo-shipping/SKILL.md                      # Shipping methods, zones, rate calculation
│   ├── woo-testing/SKILL.md                       # PHPUnit, WP test suite, E2E, test helpers
│   ├── woo-performance/SKILL.md                   # Caching, HPOS, Action Scheduler, optimization
│   ├── woo-deploy/SKILL.md                        # WP-CLI, migrations, CI/CD, staging
│   ├── woo-security/SKILL.md                      # Nonces, capabilities, sanitization, escaping
│   ├── php-modern/SKILL.md                        # PHP 8.x features & type system
│   ├── php-patterns/SKILL.md                      # Design patterns in PHP
│   └── php-testing/SKILL.md                       # PHPUnit testing & TDD
└── README.md
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add ./.
/plugin install woocommerce-commerce
```

### Per-session

```bash
claude --plugin-dir "/path/to/woocommerce-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "woocommerce-commerce": {
      "type": "local",
      "path": "/path/to/woocommerce-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `woocommerce-commerce:woocommerce-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves WooCommerce:

```
Create a custom WooCommerce payment gateway for Stripe
```

```
Add a custom shipping method based on package weight
```

```
Build a WooCommerce extension that adds product bundles
```

### Explicit invocation

```
Use the woocommerce-expert subagent to implement a REST API for inventory sync
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest WooCommerce version and system requirements
2. Fetch the relevant developer docs for exact hook names and PHP signatures
3. Check GitHub source for core implementation patterns
4. Write code against verified-current documentation, following WordPress coding standards

## Available Skills

### WooCommerce Skills (17)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **woo-setup** | `/woocommerce-commerce:woo-setup` | Manual | Install WooCommerce, configure stack, set up dev environment |
| **woo-plugin-dev** | auto | Auto + manual | Extension structure, activation hooks, autoloading |
| **woo-hooks-filters** | auto | Auto + manual | WordPress hooks, WooCommerce actions/filters, priorities |
| **woo-data-stores** | auto | Auto + manual | CRUD objects, data stores, HPOS, getters/setters |
| **woo-custom-fields** | auto | Auto + manual | Product attributes, meta fields, taxonomies, custom tabs |
| **woo-api** | auto | Auto + manual | REST API v3, custom endpoints, webhooks, authentication |
| **woo-blocks** | auto | Auto + manual | Gutenberg blocks, checkout blocks, Store API extensions |
| **woo-frontend** | auto | Auto + manual | Templates, template overrides, theme integration, assets |
| **woo-admin** | auto | Auto + manual | Settings API, admin menus, product panels, reports |
| **woo-checkout** | auto | Auto + manual | Classic & block checkout, custom fields, order processing |
| **woo-catalog** | auto | Auto + manual | Product types, categories, queries, variable products |
| **woo-payments** | auto | Auto + manual | Payment gateway API, tokenization, refunds, PCI |
| **woo-shipping** | auto | Auto + manual | Shipping methods, zones, classes, rate calculation |
| **woo-testing** | auto | Auto + manual | PHPUnit, WP test suite, E2E Playwright, test helpers |
| **woo-performance** | auto | Auto + manual | Object caching, HPOS, Action Scheduler, query tuning |
| **woo-deploy** | auto | Auto + manual | WP-CLI, migrations, CI/CD, staging workflows |
| **woo-security** | auto | Auto + manual | Nonces, capabilities, sanitization, escaping, hardening |

### PHP Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **php-modern** | auto | Auto + manual | PHP 8.x features — enums, readonly, match, types |
| **php-patterns** | auto | Auto + manual | Design patterns — Singleton, Factory, Strategy, DI |
| **php-testing** | auto | Auto + manual | PHPUnit — mocks, data providers, assertions, TDD |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a WP-CLI command | **Blocks** destructive commands (`wp db reset`, `wp db drop`, `wp site empty`, `wp plugin uninstall woocommerce`). Warns on heavy operations (`wp cache flush`, `wp wc update`, `wp search-replace`). Only activates for commands containing "wp ". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded database passwords, WordPress salts, Stripe live keys, WooCommerce API secrets, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## LSP Configuration

The plugin includes `.lsp.json` for PHP Intelephense language server support. If `intelephense` is installed in PATH (`npm install -g @bmewburn/vscode-intelephense-client`), Claude Code will provide PHP code intelligence including diagnostics, go-to-definition, and hover information for `.php` files.

## WooCommerce Architecture at a Glance

### Foundation

| Layer | Description |
|-------|-------------|
| **WordPress** | Core CMS — hooks, post types, taxonomies, REST API, users |
| **WooCommerce** | Commerce layer — products, orders, cart, checkout, payments, shipping |
| **Extensions** | Third-party plugins extending WooCommerce via hooks |

### Key Design Patterns

| Pattern | WooCommerce Implementation |
|---------|---------------------------|
| **Hooks/Filters** | Primary extensibility — `add_action()` / `add_filter()` |
| **CRUD + Data Store** | `WC_Data` → `WC_Product`, `WC_Order`, etc. with swappable stores |
| **Factory** | `WC_Product_Factory` resolves product type to class |
| **Singleton** | `WC()` global instance |
| **Strategy** | Payment gateways, shipping methods — interchangeable implementations |
| **Registry** | `WC_Payment_Gateways`, `WC_Shipping` — registries of available methods |
| **Template Override** | Theme templates override plugin templates |
| **Observer** | WordPress hooks = Observer pattern |

### Supported Stack

| Component | Versions |
|-----------|----------|
| PHP | 7.4+ (8.0–8.3 recommended) |
| MySQL | 8.0+ |
| MariaDB | 10.4+ |
| WordPress | 6.4+ |
| WooCommerce | 9.x |

*(Always verify against current system requirements docs)*

## Official References

| Resource | URL |
|----------|-----|
| WooCommerce Developer Docs | https://developer.woocommerce.com/docs/ |
| WooCommerce Code Reference | https://woocommerce.github.io/code-reference/ |
| REST API Reference | https://woocommerce.github.io/woocommerce-rest-api-docs/ |
| WooCommerce GitHub | https://github.com/woocommerce/woocommerce |
| WordPress Developer Docs | https://developer.wordpress.org/ |
| WordPress Plugin Handbook | https://developer.wordpress.org/plugins/ |
| WordPress REST API Handbook | https://developer.wordpress.org/rest-api/ |
| Block Editor Handbook | https://developer.wordpress.org/block-editor/ |
| WP-CLI Commands | https://developer.wordpress.org/cli/commands/ |
| WordPress Coding Standards | https://developer.wordpress.org/coding-standards/ |
| Action Scheduler | https://actionscheduler.org/ |
| PHPUnit | https://phpunit.de/ |
| PHP.net | https://www.php.net/ |
