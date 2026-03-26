# Agentic Commerce Skills & Plugins — Claude, Gemini, Codex, Cursor, Antigravity, OpenClaw

This repository contains agentic commerce plugins and skills for **AI coding assistants** — the emerging ecosystem where AI agents negotiate, purchase, and fulfill transactions on behalf of users. These plugins provide expert subagents, skills, and lifecycle hooks for the major protocols and platforms shaping this space.

Built natively for Claude Code, with cross-platform conversion support for Gemini CLI, OpenAI Codex CLI, Cursor, Antigravity/Windsurf, and OpenClaw. Each plugin provides deep conceptual knowledge of a commerce protocol or platform, while always fetching the latest specification and SDK documentation before writing implementation code.

Learn more about Claude Code plugins in the [official plugins documentation](https://code.claude.com/docs/en/plugins). For other platforms, see [Multi-Platform Support](#multi-platform-support).

## Plugins in This Directory

| Name | Description | Contents |
|------|-------------|----------|
| [ucp-agentic-commerce](./ucp-agentic-commerce) | Expert in the **Universal Commerce Protocol (UCP)** — the open standard co-developed by Google and Shopify for agentic commerce. Covers checkout (REST, MCP, A2A, Embedded), fulfillment, discounts, payment handlers, identity linking, AP2 mandates, and conformance testing. | **Agent:** `ucp-expert` — full UCP protocol knowledge with live doc fetching<br>**Skills (15):** Setup, REST/MCP/A2A/Embedded checkout, orders, fulfillment, discounts, payments, identity, AP2 mandates, schema authoring, buyer consent, conformance, dev patterns<br>**Hooks:** Async secret detection on code writes |
| [acp-agentic-commerce](./acp-agentic-commerce) | Expert in the **Agentic Commerce Protocol (ACP)** — the open standard co-developed by OpenAI and Stripe for AI-agent-mediated commerce. Covers checkout sessions, delegated payments (SharedPaymentTokens), product feeds, extensions, capability negotiation, and webhooks. | **Agent:** `acp-expert` — full ACP protocol knowledge with live doc fetching<br>**Skills (15):** Setup, product feed, REST/MCP checkout, delegated payment, payment handlers, orders, fulfillment, discounts, capabilities, extensions, intent traces, attribution, conformance, dev patterns<br>**Hooks:** Async Stripe/payment secret detection on code writes |
| [ap2-agentic-payments](./ap2-agentic-payments) | Expert in **AP2 (Agent Payments Protocol)** — Google's open protocol for secure, verifiable payments in agentic commerce. Covers Verifiable Digital Credentials (VDCs), Cart/Intent/Payment Mandates, cryptographic signing, role-based architecture, challenge/step-up flows, and dispute accountability. | **Agent:** `ap2-expert` — full AP2 protocol knowledge with live doc fetching<br>**Skills (18):** Setup, VDC framework, 3 mandate types, human-present/not-present flows, 4 role implementations, cryptographic signing, challenge/step-up, risk signals, A2A extension, MCP server, disputes, dev patterns<br>**Hooks:** Async PCI data and payment secret detection on code writes |
| [a2a-multi-agent](./a2a-multi-agent) | Expert in the **A2A (Agent-to-Agent) protocol** — the open standard initiated by Google (now Linux Foundation) for inter-agent communication. Covers Agent Cards, task lifecycle, JSON-RPC transport, streaming, push notifications, authentication, and framework integrations. | **Agent:** `a2a-expert` — full A2A protocol knowledge with live doc fetching<br>**Skills (16):** Setup, Agent Cards, server/client, task lifecycle, messages/parts, streaming, push notifications, auth, multi-turn, errors, JSON-RPC, MCP bridge, framework integration, testing, dev patterns<br>**Hooks:** Async auth secret detection on code writes |
| [magento2-commerce](./magento2-commerce) | Expert in **Magento 2 Open Source** development and PHP 8.x. Covers module architecture, dependency injection, plugins/interceptors, EAV, service contracts, REST/GraphQL APIs, checkout, catalog, admin UI, testing, performance, deployment, and security. | **Agent:** `magento-expert` — full Magento 2 + PHP knowledge with live doc fetching<br>**Skills (19):** Setup, module dev, DI, plugins, service contracts, EAV, API, events/cron, frontend, admin UI, checkout, catalog, testing, performance, deploy, security, PHP modern/patterns/testing<br>**Hooks:** Sync Magento CLI protection (blocks destructive commands) + async DB/admin secret detection<br>**LSP:** PHP Intelephense configuration for `.php`/`.phtml` files |
| [webmcp-browser-agents](./webmcp-browser-agents) | Expert in **WebMCP (Web Model Context Protocol)** — the browser-native API for agent-ready websites. Covers `navigator.modelContext`, registerTool, declarative form annotations, tool schemas, human-in-the-loop interactions, tool annotations, commerce tools, session auth, security, provideContext, MCP-B polyfill, and backend MCP/UCP bridge integration. | **Agent:** `webmcp-expert` — full WebMCP protocol knowledge with live doc fetching<br>**Skills (14):** Setup, registerTool, declarative forms, schemas, user interaction, annotations, commerce tools, authentication, security, context provider, MCP bridge, polyfill, testing, dev patterns<br>**Hooks:** Async secret detection on code writes |
| [bigcommerce-commerce](./bigcommerce-commerce) | Expert in **BigCommerce** development. Covers Stencil theme framework, REST/GraphQL APIs, single-click app development, checkout SDK, payment integrations, headless commerce with Catalyst/Next.js, multi-channel architecture, webhooks, widgets/Page Builder, and JavaScript/TypeScript/Node.js patterns. | **Agent:** `bigcommerce-expert` — full BigCommerce + JS/Node.js knowledge with live doc fetching<br>**Skills (20):** Setup, app dev, Stencil, REST/GraphQL APIs, webhooks, catalog, orders, checkout, payments, customers, headless, channels, widgets, testing, performance, security, JS modern, Next.js, Node.js backend<br>**Hooks:** Sync Stencil CLI protection (blocks destructive commands) + async secret detection |
| [woocommerce-commerce](./woocommerce-commerce) | Expert in **WooCommerce** development and PHP 8.x. Covers plugin/extension architecture, hooks/filters, CRUD data stores, HPOS, REST API, checkout blocks, payment gateways, shipping methods, catalog, admin UI, Gutenberg blocks, testing, deployment, security, and modern PHP patterns. | **Agent:** `woocommerce-expert` — full WooCommerce + PHP knowledge with live doc fetching<br>**Skills (20):** Setup, plugin dev, hooks/filters, data stores, custom fields, API, blocks, checkout, payments, shipping, catalog, frontend, admin, testing, performance, deploy, security, PHP modern/patterns/testing<br>**Hooks:** Sync WP-CLI protection (blocks destructive commands) + async secret detection<br>**LSP:** PHP Intelephense configuration for `.php` files |
| [shopify-commerce](./shopify-commerce) | Expert in **Shopify** development. Covers GraphQL Admin and Storefront APIs, Liquid templating, Online Store 2.0 themes, Hydrogen/Remix headless storefronts, Shopify Functions (Wasm), checkout UI extensions, Polaris components, app development with App Bridge, webhooks, metafields/metaobjects, and JavaScript/TypeScript/React patterns. | **Agent:** `shopify-expert` — full Shopify + JS/TS/React knowledge with live doc fetching<br>**Skills (21):** Setup, app dev, GraphQL/REST APIs, Liquid, themes, Hydrogen, Functions, checkout UI, catalog, orders, customers, payments, webhooks, Polaris, testing, performance, security, JS modern, React/Remix, Node.js backend<br>**Hooks:** Sync Shopify CLI protection (blocks destructive commands) + async secret detection |
| [salesforce-commerce](./salesforce-commerce) | Expert in **Salesforce Commerce** development — both B2C Commerce Cloud (SFCC/Demandware) with SFRA cartridges, ISML templating, SCAPI/OCAPI APIs, PWA Kit headless storefronts, and B2B/D2C Commerce on Lightning with Apex hooks, LWC components, Experience Builder, Einstein AI, Salesforce Payments, and JavaScript/TypeScript/React patterns. | **Agent:** `salesforce-expert` — full Salesforce Commerce + JS/TS/React knowledge with live doc fetching<br>**Skills (24):** Setup, SFRA, cartridges, controllers, ISML, SCAPI, OCAPI (deprecated), PWA Kit, jobs, Apex hooks, LWC, Experience Builder, catalog, orders, customers, payments, Einstein, integrations, testing, performance, security, JS modern, React, Node.js backend<br>**Hooks:** Sync sfcc-ci/sf CLI protection (blocks destructive commands) + async secret detection |
| [stripe-mpp](./stripe-mpp) | Expert in the **Machine Payments Protocol (MPP)** — the open standard co-authored by Stripe and Tempo Labs for HTTP 402-based machine-to-machine payments. Covers HTTP 402 challenge-response, charge and session intents, Tempo blockchain USDC settlement, Stripe SPT integration, mppx SDK, server middleware, client-side transparent payments, payment proxies, and service discovery. | **Agent:** `mpp-expert` — full MPP protocol knowledge with live doc fetching<br>**Skills (12):** Setup, server middleware, client fetch, charge flow, session flow, Tempo method, Stripe method, service discovery, proxy, dev patterns, SPT lifecycle, conformance<br>**Hooks:** Async Stripe/crypto/MPP secret detection on code writes |

## Installation

### From a Marketplace (Recommended)

If these plugins are published to a marketplace, install them with the Claude Code plugin manager:

1. **Add the marketplace** (one-time setup):

   ```shell
   /plugin marketplace add owner/agentic-commerce-claude-plugins
   ```

   Replace `owner/agentic-commerce-claude-plugins` with the actual GitHub `owner/repo` path or Git URL where this repository is hosted.

2. **Browse available plugins**:

   Run `/plugin` inside Claude Code to open the plugin manager. Navigate to the **Discover** tab to see all available plugins from the marketplace.

3. **Install a plugin**:

   ```shell
   /plugin install ucp-agentic-commerce@marketplace-name
   ```

   Or use the interactive UI: select a plugin in the **Discover** tab, press Enter, and choose an installation scope:
   - **User scope** — install for yourself across all projects
   - **Project scope** — install for all collaborators on this repository
   - **Local scope** — install for yourself in this repository only

4. **Use the plugin**:

   After installing, the plugin's agent and skills are immediately available. Claude auto-delegates to the expert subagent when your task matches the domain. You can also invoke skills directly:

   ```shell
   /ucp-agentic-commerce:ucp-setup
   /acp-agentic-commerce:acp-checkout-rest
   /ap2-agentic-payments:ap2-cart-mandate
   /stripe-mpp:mpp-setup
   ```

### From a Local Directory

If you have this repository cloned locally, you can load plugins directly:

**Per-session** (temporary, for one Claude Code session):

```shell
claude --plugin-dir "/path/to/agentic-commerce-claude-plugins/ucp-agentic-commerce"
```

**Persistent** (add to `~/.claude/settings.json` for automatic loading):

```json
{
  "enabledPlugins": {
    "ucp-agentic-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/ucp-agentic-commerce"
    },
    "acp-agentic-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/acp-agentic-commerce"
    },
    "ap2-agentic-payments": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/ap2-agentic-payments"
    },
    "a2a-multi-agent": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/a2a-multi-agent"
    },
    "magento2-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/magento2-commerce"
    },
    "webmcp-browser-agents": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/webmcp-browser-agents"
    },
    "bigcommerce-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/bigcommerce-commerce"
    },
    "shopify-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/shopify-commerce"
    },
    "woocommerce-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/woocommerce-commerce"
    },
    "salesforce-commerce": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/salesforce-commerce"
    },
    "stripe-mpp": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/stripe-mpp"
    }
  }
}
```

### Verify Installation

Run `/plugin` inside Claude Code and check the **Installed** tab. You should see your plugins listed. Run `/agents` to see the expert subagents (e.g., `ucp-agentic-commerce:ucp-expert`).

## Managing Plugins

Disable a plugin without uninstalling:

```shell
/plugin disable ucp-agentic-commerce@marketplace-name
```

Re-enable a disabled plugin:

```shell
/plugin enable ucp-agentic-commerce@marketplace-name
```

Completely remove a plugin:

```shell
/plugin uninstall ucp-agentic-commerce@marketplace-name
```

## Design Philosophy

All plugins in this collection share the same design philosophy:

- **Conceptual knowledge is baked in** — protocol architecture, roles, state machines, flows, and design patterns that are stable across spec versions are embedded directly in the agent and skill definitions.
- **Implementation details are fetched live** — every agent and skill instructs Claude Code to web-search and fetch the official documentation before writing code, ensuring you always get the latest schemas, SDK methods, and API shapes.
- **Spec version is always cited** — generated code includes comments or headers referencing the specification version it was written against.
- **Domain-specific safety hooks** — lifecycle hooks provide async secret detection (hardcoded API keys, payment tokens, PCI data) and, for Magento, synchronous protection against destructive CLI commands.

## Plugin Structure

Each plugin follows the standard Claude Code plugin structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json       # Plugin metadata (name, version, description, keywords)
├── agents/
│   └── *-expert.md       # Opus-powered expert subagent with live doc fetching
├── hooks/
│   ├── hooks.json        # Lifecycle hook configuration
│   └── scripts/
│       └── *.py          # Python hook scripts (secret detection, CLI protection)
├── skills/
│   └── */SKILL.md        # Domain-specific skills (auto-invoked + manual)
├── .mcp.json             # MCP server configuration (where applicable)
├── .lsp.json             # Language server configuration (Magento only)
└── README.md             # Plugin documentation
```

## Agentic Commerce Protocol Landscape

These plugins cover the major open protocols enabling AI agents to shop, pay, and communicate on behalf of users:

```
                    ┌─────────────────────┐
                    │   AI Agent Layer     │
                    │  (Claude, Gemini,    │
                    │   ChatGPT, etc.)     │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │               │               │            │
 ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌──▼───────┐
 │   A2A       │ │   MCP       │ │  Commerce   │ │  WebMCP  │
 │ Agent-to-   │ │ Agent-to-   │ │  Protocols  │ │ Browser  │
 │ Agent Comms │ │ Tool/Data   │ │  (Backend)  │ │ Agent API│
 └──────┬──────┘ └─────────────┘ └──────┬──────┘ └──────────┘
        │                               │
        │              ┌────────────────┼────────────────┐
        │              │          │          │            │
    ┌───▼────┐   ┌─────▼──┐ ┌────▼───┐ ┌────▼───┐ ┌─────▼──┐
    │  AP2   │   │  MPP   │ │  UCP   │ │  ACP   │ │  x402  │
    │Payment │   │Stripe/ │ │Google/ │ │OpenAI/ │ │Coinbase│
    │Mandates│   │Tempo   │ │Shopify │ │Stripe  │ │        │
    └────────┘   └────────┘ └────────┘ └────────┘ └────────┘
```

| Protocol | Maintainers | Focus | First Agent |
|----------|-------------|-------|-------------|
| **UCP** | Google, Shopify | Full shopping journey (discovery to post-purchase) | Google AI Mode, Gemini |
| **ACP** | OpenAI, Stripe | Agent-mediated checkout execution | ChatGPT Instant Checkout |
| **AP2** | Google | Secure, verifiable agentic payment mandates | Extends A2A |
| **A2A** | Google, Linux Foundation | Inter-agent communication and delegation | Framework-agnostic |
| **MPP** | Stripe, Tempo Labs | HTTP 402 machine-to-machine payments | mppx SDK, Cloudflare Workers |
| **WebMCP** | Google, Microsoft, W3C | Browser-native agent tool API for web pages | Chrome 146+ Canary |

The **Magento 2**, **BigCommerce**, **Shopify**, **WooCommerce**, and **Salesforce Commerce** plugins are not protocols — they are commerce engine plugins that provide expert knowledge for building and customizing storefronts. These stores can implement UCP or ACP endpoints to participate in agentic commerce.

The **WebMCP** plugin covers the client-side browser API that complements backend protocols — it lets websites expose structured tools to AI agents via `navigator.modelContext`, with human-in-the-loop approval flows.

## Multi-Platform Support

These plugins are built for Claude Code but can be converted for use with other AI dev tools:

| Platform | Status | Install Guide |
|----------|--------|---------------|
| **Claude Code** | Native (source of truth) | See [Installation](#installation) above |
| **Gemini CLI** | Supported via conversion | [INSTALL-GEMINI.md](./INSTALL-GEMINI.md) |
| **OpenAI Codex CLI** | Supported via conversion | [INSTALL-CODEX.md](./INSTALL-CODEX.md) |
| **Cursor** | Supported via conversion | [INSTALL-CURSOR.md](./INSTALL-CURSOR.md) |
| **Antigravity / Windsurf** | Supported via conversion | [INSTALL-ANTIGRAVITY.md](./INSTALL-ANTIGRAVITY.md) |
| **OpenClaw** | Supported via conversion | [INSTALL-OPENCLAW.md](./INSTALL-OPENCLAW.md) |

### Quick Start

```shell
# Generate for all platforms
python scripts/convert.py

# Generate for a specific platform
python scripts/convert.py --platform gemini
python scripts/convert.py --platform antigravity
python scripts/convert.py --platform codex
python scripts/convert.py --platform openclaw
python scripts/convert.py --platform cursor

# Validate the output
python scripts/validate.py
```

The conversion script (`scripts/convert.py`) reads the canonical Claude Code sources and generates platform-specific output in `dist/`. See the install guides for details.

## Official References

| Resource | URL |
|----------|-----|
| UCP Specification | https://ucp.dev |
| ACP Specification | https://www.agenticcommerce.dev/ |
| AP2 Specification | https://ap2-protocol.org |
| MPP Specification (IETF) | https://paymentauth.org/ |
| Stripe Machine Payments | https://docs.stripe.com/payments/machine |
| A2A Specification | https://a2a-protocol.org |
| WebMCP Specification (W3C) | https://webmachinelearning.github.io/webmcp/ |
| WebMCP Chrome Blog | https://developer.chrome.com/blog/webmcp |
| Salesforce Commerce Dev Docs | https://developer.salesforce.com/docs/commerce/b2c-commerce/overview |
| Magento Developer Docs | https://developer.adobe.com/commerce/docs/ |
| Claude Code Plugins Docs | https://code.claude.com/docs/en/plugins |
| Discover Plugins | https://code.claude.com/docs/en/discover-plugins |
| Plugin Marketplaces | https://code.claude.com/docs/en/plugin-marketplaces |
| Plugins Reference | https://code.claude.com/docs/en/plugins-reference |

## Troubleshooting

### Plugin not loading

- Ensure the path in `--plugin-dir` or `settings.json` points to the directory containing `.claude-plugin/plugin.json`
- Run `claude --debug` to see plugin loading details
- Verify `.claude-plugin/plugin.json` has valid JSON syntax

### Subagent not appearing

- Run `/agents` to check if the expert subagent is listed (e.g., `ucp-agentic-commerce:ucp-expert`)
- Restart Claude Code after adding or modifying plugins
- Check that the agent `.md` file has valid YAML frontmatter with `tools` as a comma-separated string

### Skills not showing

- Skills are namespaced: use `/plugin-name:skill-name` (e.g., `/ucp-agentic-commerce:ucp-setup`)
- Auto-invoked skills load automatically when Claude detects a relevant task — describe the task naturally
- Run `/plugin` and check the **Errors** tab for any loading issues

### Hooks not running

- Hooks require Python in PATH — verify with `python --version`
- Check `hooks/hooks.json` for valid JSON syntax
- Async hooks deliver output on the next conversation turn, not immediately
- Run `/plugin` and check the **Errors** tab

### Plugin cache issues

If plugins behave unexpectedly after updates:

```shell
rm -rf ~/.claude/plugins/cache
```

Then restart Claude Code and reinstall the plugin.

## Topics

`claude-code-plugin` `claude-code` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `agent-to-agent` `ucp` `universal-commerce-protocol` `acp` `agentic-commerce-protocol` `ap2` `agent-payments` `mpp` `machine-payments` `http-402` `stripe-mpp` `tempo-blockchain` `micropayments` `pay-per-call` `webmcp` `browser-agents` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `shopify-polaris` `shopify-app-development` `salesforce-commerce` `sfcc` `commerce-cloud` `b2c-commerce` `b2b-commerce` `sfra` `scapi` `pwa-kit` `apex-commerce` `lwc-commerce` `einstein-ai` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `google-shopping` `openai-plugins` `stripe-payments` `verifiable-credentials` `payment-gateway` `checkout-api` `product-feed` `agent-orchestration` `claude-plugins` `anthropic` `gemini-cli` `codex-cli` `cursor-ai` `cursor-rules` `antigravity` `windsurf` `openclaw` `clawhub` `multi-platform` `cross-platform-plugins` `ai-dev-tools` `remix`

## Maintainers

Built and maintained by [OrcaQubits AI](https://orcaqubits-ai.com) — Rohit Bajaj and Julekha Khatun.

## License

MIT — see [LICENSE](./LICENSE).
