# Agentic Commerce — Agent Rules

This repository contains expert knowledge for agentic commerce protocols and platforms. Each plugin directory has its own AGENTS.md with detailed rules and skills.

## Plugins

| Plugin | Description |
|--------|-------------|
| [ucp-agentic-commerce](./ucp-agentic-commerce/AGENTS.md) | Universal Commerce Protocol (UCP) — Google/Shopify agentic commerce across REST, MCP, A2A, and Embedded bindings |
| [acp-agentic-commerce](./acp-agentic-commerce/AGENTS.md) | Agentic Commerce Protocol (ACP) — OpenAI/Stripe open standard for AI-agent-mediated commerce |
| [a2a-multi-agent](./a2a-multi-agent/AGENTS.md) | A2A (Agent-to-Agent) protocol — Google multi-agent communication with Agent Cards, tasks, and streaming |
| [ap2-agentic-payments](./ap2-agentic-payments/AGENTS.md) | AP2 (Agent Payments Protocol) — Google agentic payment mandates, VDCs, and cryptographic signing |
| [magento2-commerce](./magento2-commerce/AGENTS.md) | Magento 2 Open Source — module development, DI, plugins, EAV, APIs, checkout, catalog, and PHP 8.x |
| [webmcp-browser-agents](./webmcp-browser-agents/AGENTS.md) | WebMCP (Web Model Context Protocol) — browser-native API for agent-ready websites, structured tool registration, declarative forms, and human-in-the-loop commerce |
| [bigcommerce-commerce](./bigcommerce-commerce/AGENTS.md) | BigCommerce — Stencil themes, REST/GraphQL APIs, single-click apps, checkout SDK, headless with Catalyst/Next.js, and Node.js patterns |
| [shopify-commerce](./shopify-commerce/AGENTS.md) | Shopify — GraphQL Admin/Storefront APIs, Liquid, Online Store 2.0 themes, Hydrogen/Remix, Shopify Functions, checkout extensions, Polaris, and JS/TS/React patterns |
| [woocommerce-commerce](./woocommerce-commerce/AGENTS.md) | WooCommerce — plugin/extension architecture, hooks/filters, REST API, checkout blocks, payment gateways, HPOS, and PHP 8.x patterns |
| [salesforce-commerce](./salesforce-commerce/AGENTS.md) | Salesforce Commerce — B2C Commerce Cloud (SFRA, ISML, SCAPI, PWA Kit) and B2B/D2C Commerce on Lightning (Apex, LWC, Experience Builder), Einstein AI, and JS/TS/React patterns |
| [stripe-mpp](./stripe-mpp/AGENTS.md) | Machine Payments Protocol (MPP) — Stripe/Tempo HTTP 402 machine-to-machine payments, charge and session intents, mppx SDK, Tempo blockchain, SPTs, and service discovery |
| [medusa-commerce](./medusa-commerce/AGENTS.md) | Medusa v2 — open-source headless commerce with custom modules, DML data models, workflows, API routes, subscribers, admin extensions, Next.js storefronts, and TypeScript/Node.js patterns |
| [saleor-commerce](./saleor-commerce/AGENTS.md) | Saleor — open-source GraphQL-first headless commerce with Python/Django backend, App extensions, webhooks, Dashboard with App Bridge, Next.js storefronts, channels, typed attributes, and GraphQL/Python/Next.js patterns |

## How to Use

Copy or symlink the plugin directories you need into your project. Your AI dev tool will automatically pick up the AGENTS.md files and the skills in `.agents/skills/`.

