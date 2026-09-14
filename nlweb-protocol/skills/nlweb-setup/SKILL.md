---
name: nlweb-setup
description: Bootstrap a local NLWeb development environment from scratch — clone the repo, configure .env, install Python deps via `nlweb init-python`, run `nlweb init` for interactive LLM/retrieval selection, load sample Schema.org data, and verify with `nlweb check`. Use when starting a new NLWeb deployment from zero.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb Setup

> **Config layout changed upstream.** NLWeb replaced the single `site_types.xml` with two files in `config/`:
> **`sites.xml`** (site name → `itemType` list + description) and **`tools.xml`** (per-site / per-type tool
> definitions, prompts and examples, scoped by `<Site id="…">` / `<Item>` blocks). Older guidance — including any
> `site_type` / `extends` inheritance syntax — describes the retired file. **Fetch `config/sites.xml` and
> `config/tools.xml` from the live repo before editing anything.**

## Before writing code

**Fetch live docs first**:
1. Fetch https://github.com/nlweb-ai/NLWeb (README) for the current minimum Python version and required deps.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-hello-world.md for the canonical hello-world flow.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-cli.md for current `nlweb` CLI flags.
4. Web-search `site:github.com/nlweb-ai/NLWeb docs/release_notes` and read the **most recent** dated release note — config keys and required env vars change between releases.
5. Identify the default `write_endpoint` and verify which backends are enabled by default in `config/config_retrieval.yaml` on `main`.

## Conceptual Architecture

### What "setup" produces

A working NLWeb dev environment has four parts:

1. **Cloned repo** + Python virtualenv with requirements installed.
2. **`.env`** file with provider credentials (OpenAI/Azure OpenAI key + retrieval backend secrets).
3. **Sample data** ingested into the local vector store (Qdrant local by default).
4. **A running aiohttp server** on `:8000` with `/ask`, `/mcp`, `/sites` reachable.

### Three Default-Enabled Backends — Watch Out

NLWeb ships with **three retrieval backends enabled by default** in `config_retrieval.yaml`:
- `qdrant_local` (file-backed, fine for dev)
- `nlweb_west` (Azure AI Search — requires Azure credentials)
- `shopify_mcp` (queries Shopify's MCP endpoint, requires network)

For most local-dev cases, disable the latter two by setting `enabled: false` so you don't get connection errors at startup. The `write_endpoint` should point to `qdrant_local` for dev.

### Setup Decision Checklist

- **LLM provider** — OpenAI, Azure OpenAI (default), Anthropic, Gemini, Ollama (offline), Snowflake Cortex?
- **Embedding provider** — must match between ingest and query; default is `text-embedding-3-small` on Azure OpenAI.
- **Retrieval write endpoint** — Qdrant local for dev, Azure AI Search / Snowflake Cortex / pgvector for prod.
- **Data source** — Schema.org JSON-LD on the site, RSS/Atom feed, sitemap.xml, or CSV?
- **Mode** — `development` (allows query-string config overrides) or `production` in `config_webserver.yaml`?
- **OAuth** — anonymous-only, or login-gated (GitHub/Google/Microsoft/Facebook)?

### Project Layout (after setup)

```
NLWeb/                                 # cloned repo
├── AskAgent/python/
│   ├── app-aiohttp.py                 # main entry
│   ├── core/, methods/, webserver/    # core code
│   ├── llm_providers/, embedding_providers/, retrieval_providers/
│   └── data_loading/
├── config/
│   ├── config_llm.yaml
│   ├── config_embedding.yaml
│   ├── config_retrieval.yaml
│   ├── config_nlweb.yaml
│   ├── config_webserver.yaml
│   ├── config_oauth.yaml
│   ├── config_storage.yaml
│   ├── config_tools.yaml
│   ├── tools.xml
│   └── prompts.xml
├── data/db/                           # qdrant_local file store
├── .env                               # YOUR credentials (gitignored)
└── docs/, scripts/, demo/, tests/
```

### Setup Sequence

1. `git clone https://github.com/nlweb-ai/NLWeb && cd NLWeb`
2. `nlweb init-python` (or manual `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)
3. `nlweb init` — interactive prompts walk through LLM + retrieval selection and write `.env`
4. Disable the unwanted default backends in `config/config_retrieval.yaml` (`nlweb_west`, `shopify_mcp` for local-only dev)
5. `nlweb data-load <source> <site-name>` — ingest sample content (use a small RSS feed for first run)
6. `nlweb check` — runs connectivity diagnostics; resolve any red flags
7. `nlweb app` — start the server, hit `http://localhost:8000/`
8. Test `/ask?query=hello&site=<site-name>&streaming=false`

### .env Conventions

NLWeb expects credentials via env vars (never YAML). Common keys (verify live):
- `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`
- `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`
- `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`
- `QDRANT_API_KEY` (only for remote Qdrant)
- `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`
- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`

### Verification Targets

After setup, these should work:
- `curl http://localhost:8000/sites` → JSON list including your loaded site
- `curl 'http://localhost:8000/ask?query=test&site=<your-site>&streaming=false'` → JSON with results
- `curl -X POST http://localhost:8000/mcp -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'` → `ask`, `list_sites`, optionally `who`

### Common Setup Failures

- **`nlweb check` fails on Azure**: usually `AZURE_OPENAI_ENDPOINT` missing trailing slash or wrong deployment name.
- **Embedding dim mismatch on retrieval**: data was loaded with a different embedding provider than runtime config. Either re-ingest or change `preferred_provider` in `config_embedding.yaml`.
- **Server starts but `/ask` returns empty**: site name in the query doesn't match the `site` value used during ingest, or the `sites:` allowlist in `config_nlweb.yaml` excludes it.
- **Slow first request**: cold model loading + `/who` endpoint pinging `nlwm.azurewebsites.net`. Disable `who_endpoint_enabled` for offline dev.

Always re-verify against the latest hello-world doc — the exact env-var names and CLI flags change.
