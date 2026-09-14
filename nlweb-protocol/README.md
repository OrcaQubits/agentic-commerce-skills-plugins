# NLWeb Protocol Plugin for Claude Code

A deeply expert Claude Code plugin for building on **NLWeb (Natural Language Web)** — the Microsoft-originated open framework (authored by R.V. Guha, announced by Satya Nadella at Microsoft Build 2025) for making any website into an agent-accessible AI application via Schema.org + MCP.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — architecture, the mixed-mode programming model, the /ask + /mcp surface area, the retrieval/LLM provider matrix, and the configuration story that are stable across releases.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and web-fetch the official docs and live source files before writing code, so you always get the latest config keys, CLI flags, JSON-RPC schemas, and provider names.
- **Release date is always cited** — generated code includes comments referencing the NLWeb release it was written against (releases are dated markdown files in `docs/release_notes/`, not semver tags).

## Plugin Structure

```
nlweb-protocol/
├── .claude-plugin/
│   └── plugin.json                          # Plugin manifest
├── agents/
│   └── nlweb-expert.md                      # Subagent: full NLWeb protocol expert
├── hooks/
│   ├── hooks.json                           # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                 # PostToolUse: detect hardcoded LLM/cloud secrets
├── skills/
│   ├── nlweb-setup/SKILL.md                 # Bootstrap a local dev environment
│   ├── nlweb-ask-endpoint/SKILL.md          # /ask REST endpoint + SSE streaming
│   ├── nlweb-mcp-server/SKILL.md            # /mcp JSON-RPC interface for AI agents
│   ├── nlweb-data-loading/SKILL.md          # db_load.py: RSS, JSON-LD, sitemap, CSV
│   ├── nlweb-schema-org-grounding/SKILL.md  # Schema.org JSON-LD authoring & types
│   ├── nlweb-retrieval-backends/SKILL.md    # Qdrant/Azure AI Search/Snowflake/etc.
│   ├── nlweb-llm-providers/SKILL.md         # OpenAI/Azure/Anthropic/Gemini/Ollama/etc.
│   ├── nlweb-tools-framework/SKILL.md       # methods/ handlers, ToolSelector, returnStruc
│   ├── nlweb-prompts-customization/SKILL.md # prompts.xml + tools.xml inheritance
│   ├── nlweb-deployment/SKILL.md            # Azure / Snowflake / Cloudflare / Docker
│   ├── nlweb-auth-multitenancy/SKILL.md     # OAuth + per-tenant isolation
│   ├── nlweb-chatgpt-appsdk/SKILL.md        # ChatGPT Apps SDK + Node.js MCP server
│   └── nlweb-dev-patterns/SKILL.md          # Mixed-mode, FastTrack/Analysis, scorer, etc.
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "nlweb-protocol"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "nlweb-protocol": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/nlweb-protocol"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `nlweb-protocol:nlweb-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves NLWeb:

```
Build an NLWeb deployment for my recipe site backed by Azure AI Search
```

```
Wire my NLWeb /mcp endpoint to Claude as a tool source
```

```
Ingest my blog's RSS feed and JSON-LD into NLWeb with the right embedding provider
```

### Explicit invocation

```
Use the nlweb-expert subagent to debug why /ask returns empty results
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest release notes on github.com/nlweb-ai/NLWeb
2. Fetch the relevant specification or setup doc for exact config keys
3. Inspect the live source files (e.g., `mcp_wrapper.py`, `config_retrieval.yaml`) for current API shape
4. Write code against the verified-current release, citing the release date

## Available Skills

| Skill | Invocation | Description |
|---|---|---|
| **nlweb-setup** | Auto + manual | Clone repo, configure `.env`, `nlweb init`, load sample data |
| **nlweb-ask-endpoint** | Auto + manual | `/ask` REST contract, SSE streaming, modes (list/summarize/generate), in-stream NLWS headers |
| **nlweb-mcp-server** | Auto + manual | `/mcp` JSON-RPC 2.0 interface, `ask` / `list_sites` / `who` tools, ChatGPT/Claude wiring |
| **nlweb-data-loading** | Auto + manual | `db_load.py` for RSS/JSON-LD/CSV/URL ingest, site partitioning, delete + reload |
| **nlweb-schema-org-grounding** | Auto + manual | Authoring Schema.org JSON-LD, `tools.xml`, per-type tools |
| **nlweb-retrieval-backends** | Auto + manual | All 12 backends, the single-write/parallel-read pattern, embedding-dim matching |
| **nlweb-llm-providers** | Auto + manual | 10+ providers, high/low tier model selection, ModelRouter, embedding alignment |
| **nlweb-tools-framework** | Auto + manual | Custom handlers in `methods/`, ToolSelector, `<returnStruc>` JSON contracts |
| **nlweb-prompts-customization** | Auto + manual | `prompts.xml` templates, per-type prompt inheritance, localization |
| **nlweb-deployment** | Auto + manual | Azure App Service, Snowflake SPCS, Cloudflare Worker + AutoRAG, Docker |
| **nlweb-auth-multitenancy** | Auto + manual | OAuth (GitHub/Google/Microsoft/Facebook), session storage, tenant isolation |
| **nlweb-chatgpt-appsdk** | Auto + manual | Node.js MCP server, `nlweb-list` tool, React widget, port-8100 adapter |
| **nlweb-dev-patterns** | Auto + manual | Mixed-mode programming, FastTrack/Analysis, scorer, the five subsystems |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded OpenAI/Anthropic/Azure OpenAI/Gemini/Qdrant/Snowflake/Cloudflare/Bing secrets and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## NLWeb at a Glance

### What It Is

A site operator ingests existing structured content (Schema.org JSON-LD, RSS/Atom, CSV) into a vector store, then runs a small Python aiohttp server exposing:

- **`/ask`** — natural-language query, streamed JSON-line results carrying the full Schema.org object
- **`/mcp`** — the same capability re-exposed as a JSON-RPC 2.0 MCP server so AI agents can call the site as a tool

NLWeb is **to MCP/A2A what HTML is to HTTP** — the data layer that makes the agentic web addressable.

### Five Top-Level Subsystems

| Subsystem | Purpose |
|-----------|---------|
| **AskAgent** | The core `/ask` and `/mcp` server |
| **AgentFinder** | Cross-site NLWeb discovery (federated `/who`) |
| **DataFinder** | NL→SQL for enterprise sources |
| **ModelRouter** | Cost/quality routing across LLM providers |
| **NLWebScorer** | Neural reranker (ModernBERT + GAM) |

### Pluggable Everything

- **10+ LLM providers**: OpenAI, Azure OpenAI, Anthropic, Gemini, DeepSeek, Llama, HuggingFace, Inception, Snowflake Cortex, Ollama, Pi Labs
- **12 retrieval backends**: Qdrant (local + remote), Azure AI Search, Milvus, Elasticsearch, OpenSearch (×2), Postgres pgvector, Snowflake Cortex Search, Cloudflare AutoRAG, Shopify MCP, Bing Web Search
- **6 embedding providers**: OpenAI, Azure OpenAI, Gemini, Snowflake, Elasticsearch, Ollama

### Three Transport Bindings + Adapter

| Binding | Path | Audience |
|---------|------|----------|
| **REST `/ask`** | port 8000 | Browsers, custom clients |
| **MCP `/mcp`** | port 8000 | Claude, Gemini, native MCP agents |
| **A2A** | `a2a_wrapper.py` | Google Agent-to-Agent |
| **AppSDK adapter** | port 8100 | ChatGPT Apps SDK |

## Official References

| Resource | URL |
|----------|-----|
| Primary repo | https://github.com/nlweb-ai/NLWeb |
| Microsoft mirror | https://github.com/microsoft/NLWeb |
| Docs index | https://github.com/nlweb-ai/NLWeb/tree/main/docs |
| REST API spec | https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md |
| System map | https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-systemmap.md |
| CLI reference | https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-cli.md |
| Tools framework | https://github.com/nlweb-ai/NLWeb/blob/main/docs/tools.md |
| Providers | https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-providers.md |
| Release notes | https://github.com/nlweb-ai/NLWeb/tree/main/docs/release_notes |
| Cloudflare hosted | https://developers.cloudflare.com/ai-search/how-to/nlweb/ |
| MS Tech Community announcement | https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/the-future-of-ai-optimize-your-site-for-agents---its-cool-to-be-a-tool/4434189 |
| WordPress plugin | https://github.com/nlweb-ai/NLWeb/tree/main/code/wordpress/nlweb |

## Adopted By

Per Microsoft's announcement: Shopify, Snowflake, O'Reilly Media, Tripadvisor, Eventbrite, Hearst, and others.

## License

MIT
