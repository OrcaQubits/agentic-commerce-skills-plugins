# Publishing to Claude Code's Public Plugin Directory

Anthropic operates a **hybrid distribution model** for Claude Code plugins:

1. **Decentralized** — anyone can host their own marketplace (this repo already does, via `.claude-plugin/marketplace.json`)
2. **Centralized & curated** — Anthropic maintains [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official), browsable at [**claude.com/plugins**](https://claude.com/plugins), with 100+ plugins from AWS, Google, Microsoft, Datadog, Auth0, Adobe, Figma, etc.

Listing in the centralized directory is the highest-leverage publishing step because the marketplace is **auto-added to every Claude Code install** — users can `/plugin install <name>@claude-plugins-official` with zero setup.

> **Important name disambiguation**: "Claude Marketplace" is two different things. The **Claude Code plugin directory** (this doc) is free, lists open-source CLI plugins, browsable at claude.com/plugins. The separate enterprise "Claude Marketplace" announced March 2026 is for ISVs selling Claude-powered apps to enterprise customers — different audience, different submission flow.

---

## Submission flow (the form)

Anthropic doesn't accept PRs to `claude-plugins-official` directly. Submit each plugin via the official form:

| Surface | URL |
|---------|-----|
| Short link | https://clau.de/plugin-directory-submission |
| Via Claude.ai | https://claude.ai/settings/plugins/submit |
| Via Console | https://platform.claude.com/plugins/submit |

Anthropic reviews each submission against quality/security standards. After review, your plugin is added to `claude-plugins-official` under `external_plugins/` with a pinned Git SHA. Some plugins receive an "Anthropic Verified" badge after additional review.

---

## What our 16 plugins look like to a reviewer

The audit is clean as of commit `5cc2155+`:

- Every `<plugin>/.claude-plugin/plugin.json` has: `name`, `version`, `description`, `author`, `repository` (with `directory` subpath), `homepage`, `keywords`, `license`
- Root `.claude-plugin/marketplace.json` enumerates all 15 with `name`, `description`, `version`, `source`, `author`
- The repo has the canonical `claude-code-plugin` GitHub topic (which drives community aggregators like claudemarketplaces.com automatically)

## End-user install (today, before official-directory listing)

Until each plugin lands in `claude-plugins-official`, users add this repo as a marketplace:

```bash
# Inside Claude Code
/plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins
/plugin install ucp-agentic-commerce@agentic-commerce
/plugin install acp-agentic-commerce@agentic-commerce
# ... or browse with `/plugin` UI
```

## End-user install (after listing)

Once each plugin is approved into `claude-plugins-official`:

```bash
/plugin install ucp-agentic-commerce@claude-plugins-official
```

No `/plugin marketplace add` step — `claude-plugins-official` is auto-added when Claude Code starts.

---

## Per-plugin submission templates

Paste these into the submission form, one plugin at a time. Anthropic asks for: plugin name, description, repository URL, homepage, install command, and a short pitch.

### UCP — Universal Commerce Protocol

- **Plugin name**: `ucp-agentic-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/ucp-agentic-commerce
- **Source subdirectory** (for `git-subdir`): `ucp-agentic-commerce`
- **Category**: Agentic Commerce
- **Pitch** (≤300 chars): Universal Commerce Protocol expert — Google+Shopify's open standard for agentic commerce. Covers discovery, checkout (REST/MCP/A2A/Embedded), orders, payments, fulfillment, discounts, identity linking, and AP2 mandates. 15 skills with live-doc fetching against ucp.dev.

### ACP — Agentic Commerce Protocol

- **Plugin name**: `acp-agentic-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/acp-agentic-commerce
- **Source subdirectory**: `acp-agentic-commerce`
- **Category**: Agentic Commerce
- **Pitch**: Agentic Commerce Protocol expert — the OpenAI+Stripe open standard for AI-agent-mediated commerce. Covers checkout sessions, delegated payments (SharedPaymentTokens), product feeds, extensions, capability negotiation, and webhooks. 16 skills.

### A2A — Agent-to-Agent Protocol

- **Plugin name**: `a2a-multi-agent`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/a2a-multi-agent
- **Source subdirectory**: `a2a-multi-agent`
- **Category**: Multi-Agent
- **Pitch**: A2A (Agent-to-Agent) protocol expert — the Google-initiated open standard (now Linux Foundation) for inter-agent communication. Agent Cards, task lifecycle, JSON-RPC transport, streaming, push notifications, auth, framework integrations. 15 skills.

### AP2 — Agent Payments Protocol

- **Plugin name**: `ap2-agentic-payments`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/ap2-agentic-payments
- **Source subdirectory**: `ap2-agentic-payments`
- **Category**: Payments
- **Pitch**: AP2 (Agent Payments Protocol) expert — Google/FIDO Alliance protocol for secure agentic payments via Verifiable Digital Credentials. Cart/Intent/Payment Mandates, cryptographic signing, challenge/step-up, dispute accountability, A2A extension, MCP server. 18 skills.

### Stripe MPP — Machine Payments Protocol

- **Plugin name**: `stripe-mpp`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/stripe-mpp
- **Source subdirectory**: `stripe-mpp`
- **Category**: Payments
- **Pitch**: Machine Payments Protocol (MPP) expert — Stripe+Tempo Labs open standard for HTTP 402-based agent-to-agent payments. Charge/session intents, Tempo blockchain USDC settlement, Stripe SPT integration, mppx SDK, payment proxies. 12 skills.

### WebMCP — Browser-native Agent Tools

- **Plugin name**: `webmcp-browser-agents`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/webmcp-browser-agents
- **Source subdirectory**: `webmcp-browser-agents`
- **Category**: Agentic Commerce
- **Pitch**: WebMCP (Web Model Context Protocol) expert — browser-native API for agent-ready websites. `navigator.modelContext`, registerTool, declarative form annotations, tool schemas, human-in-the-loop, commerce tools, MCP-B polyfill. 14 skills.

### NLWeb — Natural Language Web

- **Plugin name**: `nlweb-protocol`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/nlweb-protocol
- **Source subdirectory**: `nlweb-protocol`
- **Category**: AI Web
- **Pitch**: NLWeb (Natural Language Web) expert — Microsoft's open framework (R.V. Guha) for making any site agent-accessible via Schema.org + MCP. /ask + /mcp endpoints, mixed-mode programming, 12 retrieval backends (Azure AI Search, Qdrant, Snowflake Cortex, Cloudflare AutoRAG, etc.), 10+ LLM providers. 13 skills.

### Magento 2

- **Plugin name**: `magento2-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/magento2-commerce
- **Source subdirectory**: `magento2-commerce`
- **Category**: Commerce
- **Pitch**: Magento 2 Open Source + PHP 8.x expert — module architecture, DI, plugins/interceptors, EAV, service contracts, REST/GraphQL APIs, checkout, catalog, admin UI components, testing, performance, deployment, security. 19 skills.

### BigCommerce

- **Plugin name**: `bigcommerce-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/bigcommerce-commerce
- **Source subdirectory**: `bigcommerce-commerce`
- **Category**: Commerce
- **Pitch**: BigCommerce expert — Stencil themes, REST/GraphQL APIs, single-click apps, checkout SDK, payment integrations, headless with Catalyst/Next.js, multi-channel, webhooks, and Node.js/JavaScript patterns. 20 skills.

### Shopify

- **Plugin name**: `shopify-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/shopify-commerce
- **Source subdirectory**: `shopify-commerce`
- **Category**: Commerce
- **Pitch**: Shopify expert — GraphQL Admin/Storefront APIs, Liquid, Online Store 2.0 themes, Hydrogen/Remix headless storefronts, Shopify Functions (Wasm), checkout UI extensions, Polaris, App Bridge, webhooks, metafields. 21 skills.

### WooCommerce

- **Plugin name**: `woocommerce-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/woocommerce-commerce
- **Source subdirectory**: `woocommerce-commerce`
- **Category**: Commerce
- **Pitch**: WooCommerce + PHP 8.x expert — plugin/extension architecture, hooks/filters, REST API, checkout blocks, payment gateways, shipping methods, HPOS, catalog, admin UI, testing, deployment, security. 20 skills.

### Salesforce Commerce

- **Plugin name**: `salesforce-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/salesforce-commerce
- **Source subdirectory**: `salesforce-commerce`
- **Category**: Commerce
- **Pitch**: Salesforce Commerce expert — B2C Commerce Cloud (SFCC/Demandware) with SFRA, ISML, SCAPI/OCAPI, PWA Kit, and B2B/D2C Commerce on Lightning with Apex hooks, LWC, Experience Builder, Einstein AI, Salesforce Payments. 24 skills.

### Medusa

- **Plugin name**: `medusa-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/medusa-commerce
- **Source subdirectory**: `medusa-commerce`
- **Category**: Commerce
- **Pitch**: Medusa v2 expert — open-source headless commerce with custom modules, DML data models, workflows, API routes, subscribers, admin extensions, Next.js storefronts, and TypeScript/Node.js patterns. 21 skills.

### Saleor

- **Plugin name**: `saleor-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/saleor-commerce
- **Source subdirectory**: `saleor-commerce`
- **Category**: Commerce
- **Pitch**: Saleor expert — open-source GraphQL-first headless commerce with Python/Django backend, App extensions, webhooks (async/sync with subscription payloads), Dashboard with App Bridge, Next.js storefronts, channels, typed attributes. 21 skills.

### Spree

- **Plugin name**: `spree-commerce`
- **Repository**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins
- **Homepage**: https://github.com/OrcaQubits/agentic-commerce-skills-plugins/tree/main/spree-commerce
- **Source subdirectory**: `spree-commerce`
- **Category**: Commerce
- **Pitch**: Spree v5 expert — open-source Rails e-commerce platform. Consolidated `spree` umbrella gem, Tailwind admin, API v3 (flat JSON, OpenAPI 3.0), Order/Payment/Shipment state machines, prepend-based decorators, Event Bus + Webhooks 2.0, Payment Sessions, Multi-store + Markets, Next.js storefront. 22 skills.

---

## Suggested submission order

If you want to stage the submissions rather than blasting all 15 at once, the most strategic order is:

1. **UCP** — flagship protocol with Google/Shopify endorsement; strongest signal of repo quality
2. **ACP** — second flagship (OpenAI/Stripe); pairs naturally with UCP in the directory
3. **AP2** — third (Google/FIDO); rounds out the "protocols" cluster
4. **Stripe MPP** — fourth protocol; strongest payments story
5. The 4 popular e-commerce platforms (Shopify, Magento, WooCommerce, BigCommerce) — high search volume
6. Salesforce Commerce — enterprise audience
7. The 3 modern open-source commerce platforms (Medusa, Saleor, Spree) — niche but growing
8. WebMCP + NLWeb + A2A — the "agentic web" cluster

Anthropic's reviewers see your prior approvals, so leading with the strongest plugins helps the rest land faster.

---

## Other discoverability surfaces (free, durable)

### 1. GitHub topics (DONE)

These topics are set on the repo and drive community aggregators that auto-populate from public sources:

- `claude-code-plugin` — the canonical convention (2,296 repos), drives claudemarketplaces.com indexing
- `claude-plugin`, `claude-skill`, `claude-code`
- `cursor-plugin`, `codex-cli-plugin`, `openclaw-plugin`, `gemini-cli-extension`

### 2. claudemarketplaces.com

Independent community aggregator (~140k monthly visitors). Auto-populates from public repos with the right topics + valid `marketplace.json`. No submission form needed — wait for indexing.

### 3. aitmpl.com/plugins

Another community aggregator. Same auto-discovery pattern.

### 4. awesome-claude-code

PR-based awesome list at https://github.com/hesreallyhim/awesome-claude-code. Submit a PR adding entries for each plugin.

### 5. MCP Registry

If any plugin's value is primarily an MCP server (we mainly ship plugins WITH MCP knowledge, not server bundles, but UCP/ACP/AP2 have MCP server stubs), list at https://github.com/modelcontextprotocol/registry separately.

---

## Updating a listed plugin

After a plugin is in `claude-plugins-official`:

1. Update the plugin's source (skills, agent, README, etc.) in this repo
2. Bump `version` in `<plugin>/.claude-plugin/plugin.json` AND in the root `.claude-plugin/marketplace.json`
3. Re-run `python scripts/convert.py` to refresh all platform builds
4. Commit, push, **tag the new SHA**
5. Email Anthropic the new SHA (or wait for their next automated sync — the cadence isn't publicly documented)

`claude-plugins-official` pins to a specific SHA per plugin entry, so version updates require Anthropic to update the pin. Anthropic-Verified plugins get faster refresh cadence.

---

## Gotchas

- **"Anthropic Verified" is not granted at first submission** — it's an additional review after listing. Don't expect it on day one.
- **Trust warning still applies** — even listed plugins show the "we don't verify plugin behavior" warning unless Verified.
- **One submission per plugin** — submit them individually; don't try to batch.
- **Per-plugin descriptions must stand alone** — the directory UI shows the plugin's own description, not the marketplace's. Use the per-plugin templates above.
- **Name collisions** — your plugin name must be unique within `claude-plugins-official`. All 15 of our names are scoped enough to avoid collisions (e.g., `ucp-agentic-commerce` not `ucp`).
- **`docs.claude.com` 301-redirects to `code.claude.com`** in 2026 — both still work but `code.claude.com` is canonical.
- **Don't say "Claude Marketplace"** in marketing — it now means the enterprise app marketplace. Say "Claude Code plugin directory" or "`claude-plugins-official`".

---

## Reference URLs

- Plugin docs hub: https://code.claude.com/docs/en/plugins
- Plugin reference (schema): https://code.claude.com/docs/en/plugins-reference
- Marketplace creation: https://code.claude.com/docs/en/plugin-marketplaces
- Discovery / install: https://code.claude.com/docs/en/discover-plugins
- Plugin hints: https://code.claude.com/docs/en/plugin-hints
- Browsable public catalog: https://claude.com/plugins
- Anthropic-managed marketplace repo: https://github.com/anthropics/claude-plugins-official
- Submission (short link): https://clau.de/plugin-directory-submission
- Submission (Console): https://platform.claude.com/plugins/submit
- Submission (Claude.ai): https://claude.ai/settings/plugins/submit
- Skills reference repo: https://github.com/anthropics/skills (reference only, not a submission target)
- MCP Registry: https://github.com/modelcontextprotocol/registry
- Community aggregator: https://claudemarketplaces.com
- Awesome list: https://github.com/hesreallyhim/awesome-claude-code
