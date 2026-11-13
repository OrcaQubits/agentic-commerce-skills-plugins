---
name: nlweb-deployment
description: >
  Deploy NLWeb to production — Azure App Service (`deploy_azure_webapp.sh` + AI
  Search + Azure OpenAI), Snowflake Container Services, Cloudflare Worker +
  AutoRAG, Docker, and self-hosted. Covers env-var conventions, `mode:
  production` lockdown, scaling, TLS, OAuth, and CI for data reloads. Use when
  going from local dev to a hosted, internet-facing NLWeb instance.
---

# NLWeb Deployment

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/setup-azure.md for Azure App Service deployment.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/setup-snowflake.md for Snowflake Container Services.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/setup-cloudflare-autorag.md for Cloudflare Worker + AutoRAG.
4. Fetch https://developers.cloudflare.com/ai-search/how-to/nlweb/ for Cloudflare's hosted NLWeb documentation.
5. Inspect `deploy_azure_webapp.sh`, `setup.sh`, `startup_aiohttp.sh` in the live repo for current commands.
6. Web-search the latest release notes for breaking deployment changes.

## Conceptual Architecture

### Deployment Targets Supported

| Target | Notes | Setup doc |
|--------|-------|-----------|
| Azure App Service | Reference deployment; ships shell scripts | `docs/setup-azure.md` |
| Snowflake Container Services | NLWeb runs inside Snowflake compute, closest to data | `docs/setup-snowflake.md` |
| Cloudflare Worker + AutoRAG | Edge deployment; CF manages indexing | `docs/setup-cloudflare-autorag.md` |
| Docker | Bring-your-own host | Build from `Dockerfile` if shipped, else manual |
| Bare Python | systemd + venv on a VM | Use `app-aiohttp.py` directly |
| WordPress plugin | For WP sites | `code/wordpress/nlweb/` |

### Production Hardening Checklist

Before exposing `/ask` or `/mcp` to the internet:

1. **Set `mode: production`** in `config_webserver.yaml` — disables query-string config overrides.
2. **Lock down the `sites:` allowlist** in `config_nlweb.yaml` — only the sites you want public.
3. **Disable `who_endpoint_enabled`** if you don't want federated traffic going to `nlwm.azurewebsites.net`.
4. **Turn off unused retrieval backends** in `config_retrieval.yaml` (`nlweb_west`, `shopify_mcp` unless needed).
5. **Configure OAuth** if you need auth (see `nlweb-auth-multitenancy`).
6. **Set TLS** at the edge (App Service, CF, ALB, etc.).
7. **Set rate limits** — NLWeb itself has limited built-in protection; do it at the edge.
8. **Configure CORS** if a browser client calls `/ask` directly.
9. **Persist conversations** to a real storage provider (`config_storage.yaml`), not in-memory.
10. **Configure observability** — logs, /mcp/health checks, latency metrics.

### Env Vars vs YAML Config

**Secrets always in env vars** — never in `config_*.yaml`. The convention NLWeb uses:

```yaml
# config_llm.yaml
providers:
  azure_openai:
    api_key_env: AZURE_OPENAI_API_KEY     # references env var, doesn't store value
    endpoint_env: AZURE_OPENAI_ENDPOINT
```

`.env` is typical for dev; in cloud deployments use the platform's secret manager (Azure Key Vault, Snowflake secrets, CF Workers KV / Secrets, etc.) and inject as env vars.

### The Two Server Processes

A full production NLWeb deployment may have:

1. **Main aiohttp server** (port 8000) — `/ask`, `/mcp`, `/who`, `/sites`, `/config`, `/api/oauth/*`
2. **AppSDK adapter** (port 8100) — only if you're integrating with ChatGPT Apps SDK. Optional.

Plus optionally the **Node.js MCP server** in `openai-apps-sdk-integration/` if you want the React widget for ChatGPT.

### Reverse-Proxy Concerns

NLWeb streams SSE. Make sure your reverse proxy:
- Disables response buffering for `/ask` paths (`X-Accel-Buffering: no` is sent, but nginx still needs `proxy_buffering off`).
- Sets long timeouts (60-300s) for `/ask` streams.
- Forwards real client IP (`X-Forwarded-For`) for rate limiting.
- Terminates TLS — NLWeb assumes plain HTTP behind a TLS-terminating proxy.

### Data Reload as a CI Job

Most deployments reload site data on a schedule:

```yaml
# .github/workflows/nlweb-reload.yml (sketch)
on:
  schedule:
    - cron: '0 3 * * *'   # daily 03:00 UTC
jobs:
  reload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python -m data_loading.db_load https://example.com/feed.xml my-site
        env:
          AZURE_SEARCH_API_KEY: ${{ secrets.AZURE_SEARCH_API_KEY }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
```

Run reload as a separate process — don't bake it into the server's startup.

### Scaling

NLWeb is stateless per-request (state is in conversation storage + the vector backend). Scale horizontally:
- Multiple app instances behind a load balancer
- Shared vector backend (cloud-hosted, not Qdrant local file)
- Shared conversation storage (Qdrant remote / Azure Search / Elasticsearch)
- Sticky sessions NOT required for `/ask` (each request is self-contained)

LLM and embedding API quota is usually the binding constraint, not CPU.

## Implementation Guidance

### Azure App Service Deployment

Walk through `deploy_azure_webapp.sh` — it provisions:
- App Service Plan + Web App (Linux, Python 3.11+)
- Azure AI Search service
- Azure OpenAI deployment
- App settings (env vars) wired to the search/openai instances

Customize the resource names, set `WEBSITES_PORT=8000` (or whichever the script uses), deploy via `git push` or `az webapp deploy`. Verify `mode: production` in the deployed `config_webserver.yaml`.

### Snowflake Container Services

NLWeb runs as a containerized service inside Snowflake compute, queries Cortex Search (data is already in Snowflake tables). Use the `setup-snowflake.md` doc — it covers the SPCS service spec, image build, and Cortex Search setup.

### Cloudflare Worker + AutoRAG

Cloudflare maintains a hosted variant. Two options:
- **Self-host on CF Workers** following `docs/setup-cloudflare-autorag.md` — covers the worker template and AutoRAG wiring.
- **Use CF's managed deployment** per https://developers.cloudflare.com/ai-search/how-to/nlweb/.

### Docker

If a `Dockerfile` ships in the repo, use it. Otherwise:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "AskAgent/python/app-aiohttp.py"]
```

Mount `config/` and `.env` as bind mounts or use env vars + ConfigMaps. Persist `data/db/` (Qdrant local) on a volume if not using a remote vector store.

### Health Checks

- Liveness: `GET /mcp/health` (or `/sites` as a fallback)
- Readiness: `GET /sites` — fails fast if config is broken

### Logs and Observability

NLWeb logs to stdout via Python `logging`. Wire to your platform's log aggregator (Azure Monitor, CloudWatch, etc.). Key metrics:
- `/ask` latency (p50, p95, p99) — SSE makes this tricky; measure TTFB and total
- LLM API errors / 429s
- Retrieval backend latencies (per-backend)
- Conversation storage write latency

### Production Failure Modes

- **App boots but `/ask` 500s**: usually an env var missing — check the log for the failing provider.
- **Streaming requests time out at the proxy**: increase proxy read timeout; turn off proxy buffering.
- **Cold-start latency**: first request after deploy takes 30-60s as models load. Pre-warm with a synthetic health check.
- **Bills are huge**: too many LLM calls per query — tune `tool_selection_enabled`, model tiers, and `who_endpoint_enabled`.
- **Embedding rate limits during data reload**: throttle `--batch-size`, use a separate embedding deployment, or run reloads off-peak.

Always re-fetch the per-target setup doc and `deploy_*.sh` scripts before deploying — these are the most release-sensitive parts of the codebase.
