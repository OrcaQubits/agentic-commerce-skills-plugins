# Magento 2 Commerce Plugin for Claude Code

A comprehensive Claude Code plugin for **Magento 2 Open Source** development — covering module architecture, DI, plugins, EAV, APIs, checkout, catalog, admin UI, testing, deployment, security, and modern PHP 8.x patterns.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — Magento's 4-layer architecture, DI system, EAV model, plugin/interceptor pattern, service contracts, checkout flow, indexing strategy, and deployment modes that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search the official DevDocs before writing code, so you always get the latest XML schemas, PHP class signatures, CLI options, and system requirements.
- **PHP expertise included** — 3 dedicated PHP skills for modern PHP 8.x features, design patterns, and PHPUnit testing, since Magento is built on PHP.

## Plugin Structure

```
magento2-commerce/
├── .claude-plugin/
│   └── plugin.json                                # Plugin manifest
├── .lsp.json                                      # PHP Intelephense language server config
├── agents/
│   └── magento-expert.md                          # Subagent: Magento 2 + PHP expert
├── hooks/
│   ├── hooks.json                                 # Lifecycle hooks configuration
│   └── scripts/
│       ├── check_magento_commands.py              # PreToolUse: block destructive CLI commands
│       └── check_secrets.py                       # PostToolUse: detect hardcoded DB/admin secrets
├── skills/
│   ├── magento-setup/SKILL.md                     # Installation & environment setup
│   ├── magento-module-dev/SKILL.md                # Module creation & structure
│   ├── magento-di/SKILL.md                        # Dependency injection & di.xml
│   ├── magento-plugins-interceptors/SKILL.md      # Before/after/around plugins
│   ├── magento-service-contracts/SKILL.md         # Repositories & data interfaces
│   ├── magento-eav-attributes/SKILL.md            # EAV system & custom attributes
│   ├── magento-api/SKILL.md                       # REST & GraphQL API development
│   ├── magento-events-cron/SKILL.md               # Events, observers, cron, queues
│   ├── magento-frontend/SKILL.md                  # Layout XML, blocks, templates, themes
│   ├── magento-admin-ui/SKILL.md                  # Admin grids, forms, system config
│   ├── magento-checkout/SKILL.md                  # Payment, shipping, totals collectors
│   ├── magento-catalog/SKILL.md                   # Products, categories, indexing
│   ├── magento-testing/SKILL.md                   # PHPUnit, integration, MFTF, API tests
│   ├── magento-performance/SKILL.md               # Varnish, Redis, indexer tuning
│   ├── magento-deploy/SKILL.md                    # Deployment modes, CLI, zero-downtime
│   ├── magento-security/SKILL.md                  # CSP, 2FA, CSRF, ACL, hardening
│   ├── php-modern/SKILL.md                        # PHP 8.x features & type system
│   ├── php-patterns/SKILL.md                      # Design patterns in PHP
│   └── php-testing/SKILL.md                       # PHPUnit testing & TDD
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "magento2-commerce"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "magento2-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/magento2-commerce"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `magento2-commerce:magento-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves Magento:

```
Create a custom Magento 2 module for product recommendations
```

```
Add a custom shipping method to my Magento store
```

```
Build an admin grid for managing custom entities
```

### Explicit invocation

```
Use the magento-expert subagent to implement a REST API for inventory management
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest Magento system requirements and version
2. Fetch the relevant DevDocs page for exact XML schemas and PHP signatures
3. Check GitHub source for core module implementation patterns
4. Write code against verified-current documentation, following Magento coding standards

## Available Skills

### Magento 2 Skills (16)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **magento-setup** | `/magento2-commerce:magento-setup` | Manual | Install Magento, configure stack, set up dev environment |
| **magento-module-dev** | auto | Auto + manual | Module structure, registration, models, patches |
| **magento-di** | auto | Auto + manual | di.xml, types, virtual types, preferences, arguments |
| **magento-plugins-interceptors** | auto | Auto + manual | Before/after/around plugins, sortOrder, limitations |
| **magento-service-contracts** | auto | Auto + manual | Repository interfaces, data interfaces, SearchCriteria |
| **magento-eav-attributes** | auto | Auto + manual | EAV model, custom attributes, attribute sets |
| **magento-api** | auto | Auto + manual | REST webapi.xml, GraphQL schema/resolvers, auth |
| **magento-events-cron** | auto | Auto + manual | Events, observers, cron jobs, message queues |
| **magento-frontend** | auto | Auto + manual | Layout XML, blocks, templates, themes, JS, Hyva |
| **magento-admin-ui** | auto | Auto + manual | Admin grids, forms, system config, ACL, menus |
| **magento-checkout** | auto | Auto + manual | Payment methods, shipping carriers, totals collectors |
| **magento-catalog** | auto | Auto + manual | Product types, categories, indexing, search |
| **magento-testing** | auto | Auto + manual | Unit, integration, MFTF, API functional, static tests |
| **magento-performance** | auto | Auto + manual | Varnish FPC, Redis, indexer tuning, JS/CSS optimization |
| **magento-deploy** | auto | Auto + manual | Modes, static deploy, DI compile, zero-downtime |
| **magento-security** | auto | Auto + manual | CSP, 2FA, CSRF, ACL, input validation, hardening |

### PHP Skills (3)

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **php-modern** | auto | Auto + manual | PHP 8.x features — enums, readonly, match, types |
| **php-patterns** | auto | Auto + manual | Design patterns — Repository, Factory, Strategy, DI |
| **php-testing** | auto | Auto + manual | PHPUnit — mocks, data providers, assertions, TDD |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PreToolUse** (sync) | Bash tool about to execute a Magento CLI command | **Blocks** destructive commands (`setup:db:rollback`, `setup:uninstall`, `module:uninstall`, `indexer:reset --all`). Warns on heavy operations (`cache:flush`, `setup:upgrade`, `setup:di:compile`). Only activates for commands containing "magento". |
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded database passwords, admin passwords, encryption keys, OAuth secrets, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## LSP Configuration

The plugin includes `.lsp.json` for PHP Intelephense language server support. If `intelephense` is installed in PATH (`npm install -g @bmewburn/vscode-intelephense-client`), Claude Code will provide PHP code intelligence including diagnostics, go-to-definition, and hover information for `.php` and `.phtml` files.

## Magento 2 Architecture at a Glance

### Four Layers

| Layer | Responsibility |
|-------|---------------|
| **Presentation** | Layout XML, Blocks, Templates, UI Components, KnockoutJS |
| **Service** | Service Contracts (PHP interfaces) — module's public API |
| **Domain** | Business logic, models |
| **Persistence** | Resource models, EAV storage, database operations |

### Key Design Patterns

| Pattern | Magento Implementation |
|---------|----------------------|
| **DI** | Object Manager + di.xml — constructor injection |
| **Repository** | `Api/*RepositoryInterface` — centralized data access |
| **Service Contract** | `Api/` interfaces — stable public APIs |
| **Plugin/Interceptor** | before/after/around method interception |
| **Factory** | Auto-generated `*Factory` classes for entity creation |
| **Proxy** | Auto-generated `*\Proxy` for lazy instantiation |
| **Virtual Type** | Class variation via di.xml without new PHP code |
| **Observer** | Event dispatch + events.xml listeners |

### Supported Stack

| Component | Versions |
|-----------|----------|
| PHP | 8.2, 8.3, 8.4 |
| MySQL | 8.0+, 8.4 LTS |
| MariaDB | 10.6+, 11.4 LTS |
| OpenSearch | 2.12+ |
| Redis/Valkey | 7.x / 8.x |
| Varnish | 7.x |
| RabbitMQ | 3.13+ |
| Composer | 2.x |

*(Always verify against current system requirements docs)*

## Official References

| Resource | URL |
|----------|-----|
| Developer Docs Hub | https://developer.adobe.com/commerce/docs/ |
| PHP Development Guide | https://developer.adobe.com/commerce/php/development/ |
| GraphQL Development | https://developer.adobe.com/commerce/webapi/graphql/develop/ |
| REST/Web API | https://developer.adobe.com/commerce/webapi/ |
| Experience League | https://experienceleague.adobe.com/en/docs/commerce |
| System Requirements | https://experienceleague.adobe.com/en/docs/commerce-operations/installation-guide/system-requirements |
| Magento 2 GitHub | https://github.com/magento/magento2 |
| Mage-OS DevDocs | https://devdocs.mage-os.org/ |
| Magento Stack Exchange | https://magento.stackexchange.com/ |
| Magento Coding Standard | https://github.com/magento/magento-coding-standard |
| Hyva Themes | https://www.hyva.io/ |
| PHPUnit | https://phpunit.de/ |
| PHP.net | https://www.php.net/ |
| Claude Code Plugins Docs | https://code.claude.com/docs/en/plugins |
