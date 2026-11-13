---
name: nlweb-retrieval-backends
description: >
  Choose and configure NLWeb retrieval backends — Qdrant (local + remote),
  Azure AI Search, Elasticsearch, OpenSearch (with/without k-NN), Postgres
  pgvector, Milvus, Snowflake Cortex Search, Cloudflare AutoRAG, Shopify MCP,
  and Bing Web Search. Covers `config_retrieval.yaml`, the single
  `write_endpoint` rule, parallel read-fanout with URL dedup, and per-backend
  setup pages. Use when picking a retrieval store, migrating between backends,
  or debugging "results are empty."
---

# NLWeb Retrieval Backends

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-retrieval.md for the architectural overview.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/config_retrieval.yaml for the **canonical list of endpoint names** and their defaults — config keys move release to release.
3. Pick the per-backend setup page from `docs/setup-*.md` (Qdrant, Azure AI Search, Elasticsearch, OpenSearch, Postgres, Snowflake, Cloudflare AutoRAG).
4. Inspect `AskAgent/python/retrieval_providers/<backend>.py` for the exact client signature and required env vars.
5. Verify the embedding dimension and metric (cosine/dot/L2) the backend expects — must match the embedding provider.

## Conceptual Architecture

### The Read-Fanout, Single-Write Pattern

NLWeb does something unusual: it **reads from every enabled retrieval endpoint in parallel and deduplicates by URL**, but writes go to **exactly one** `write_endpoint`. This means:
- You can run a hybrid index (e.g., local Qdrant for site content + Bing for fresh news) without code changes
- You migrate between backends by re-running `db_load` against the new `write_endpoint`
- "Result quality" is the union of all enabled stores — a noisy backend pollutes the top-k

### All Supported Backends

| Endpoint key (config_retrieval.yaml) | Backend | Notes |
|--------------------------------------|---------|-------|
| `qdrant_local` | Qdrant file-backed | Default-enabled; data in `../data/db` |
| `qdrant_url` | Qdrant remote | Set URL + API key in env |
| `nlweb_west` | Azure AI Search | Default-enabled MS-hosted demo instance — usually disable |
| `azure_ai_search` | Azure AI Search (your own) | Bring your own index name |
| `milvus` | Milvus | Flagged "under development" in YAML |
| `elasticsearch` | Elasticsearch | dense_vector + int8_hnsw |
| `opensearch_knn` | OpenSearch + k-NN plugin | The recommended OpenSearch path |
| `opensearch_script` | OpenSearch no plugin | script_score fallback, slower |
| `postgres` | Postgres + pgvector | Good if you already run Postgres |
| `snowflake_cortex_search_1` | Snowflake Cortex Search | Data lives in Snowflake tables |
| `cloudflare_autorag` | Cloudflare AutoRAG | Indexing managed by CF; ingest via R2 |
| `shopify_mcp` | Shopify's MCP endpoint | Default-enabled; live proxy, no ingest |
| `bing_search` | Bing Web Search API | Live web fallback; not a vector store |

### Read vs Write

Every endpoint declares:
- `enabled: true/false` — whether `/ask` queries it
- `read: true/false` — finer-grained: enable for reads
- (only one endpoint should be the `write_endpoint`)

The default config has `qdrant_local`, `nlweb_west`, and `shopify_mcp` enabled — for local dev disable the last two.

### Choosing a Backend

| If you need... | Use |
|----------------|-----|
| Local dev with no cloud deps | `qdrant_local` |
| Largest scale + Microsoft-stack | `azure_ai_search` |
| Already on AWS | `opensearch_knn` |
| Already on Postgres | `postgres` (pgvector) |
| Live e-commerce catalog | `shopify_mcp` |
| Snowflake-resident data | `snowflake_cortex_search_1` |
| Edge deployment | `cloudflare_autorag` |
| Live news/freshness | `bing_search` (combine with a vector backend) |

### Embedding Dimension Compatibility

Each backend stores fixed-dimension vectors. The embedding provider must emit the same dimension:

| Embedding provider | Default model | Dim |
|--------------------|---------------|-----|
| OpenAI `text-embedding-3-small` | default | 1536 |
| OpenAI `text-embedding-3-large` | — | 3072 |
| Azure OpenAI `text-embedding-3-small` | default | 1536 |
| Gemini `text-embedding-004` | — | 768 |
| Snowflake `arctic-embed-m-v1.5` | — | 768 |
| Elasticsearch `multilingual-e5-small` | — | 384 |

Pick the embedding provider FIRST, configure the backend's index to match THAT dimension, then ingest.

### Metric Compatibility

Most NLWeb providers use **cosine similarity**. When creating a new index manually (Azure AI Search, OpenSearch, Postgres) make sure the metric matches what the retrieval provider class expects. Look in `retrieval_providers/<backend>.py` for the metric the SDK call passes.

### The `nlweb_west` Trap

`nlweb_west` is a Microsoft-hosted demo Azure AI Search instance that's **enabled by default**. For most users this:
- Pollutes results with MS demo data
- Requires the demo's Azure credentials to even connect
- Costs nothing but adds latency

Disable it in local dev unless you specifically want the demo content.

## Implementation Guidance

### Switching the Write Endpoint

Edit `config/config_retrieval.yaml`:

```yaml
write_endpoint: azure_ai_search

endpoints:
  qdrant_local:
    enabled: false
  azure_ai_search:
    enabled: true
    api_key_env: AZURE_SEARCH_API_KEY
    endpoint_env: AZURE_SEARCH_ENDPOINT
    index_name: nlweb-main
```

Then re-ingest:
```bash
python -m data_loading.db_load --only-delete delete-site <site>
python -m data_loading.db_load <source> <site> --database azure_ai_search
```

### Running Multiple Backends in Parallel

Leave several `enabled: true` simultaneously — `/ask` will fan out reads, dedup by URL. Useful for:
- Hybrid: Postgres (cheap) for site content + Bing for live web facts
- A/B: Qdrant + Azure AI Search to compare retrieval quality

### Adding a New Backend Provider

If NLWeb doesn't ship the backend you need:
1. Subclass the base in `retrieval_providers/` — look at any existing one for the contract (search, upsert, delete-by-site).
2. Add an endpoint entry in `config_retrieval.yaml`.
3. Register the class in the provider factory (verify location in current code).
4. Ingest a test site.

### Backend-Specific Notes

**Qdrant local**: zero setup; collection lives at `../data/db`. To reset, delete the directory.

**Azure AI Search**: create the index manually (or via the setup doc's ARM template). Vector field must be `vector` (or whatever the provider class names it — verify).

**Postgres + pgvector**: `CREATE EXTENSION vector;` then ensure the column is `vector(1536)` or whichever dim matches your embedding. NLWeb uses cosine distance by default.

**Snowflake Cortex Search**: data is in a Snowflake table; you create a `CORTEX SEARCH SERVICE` over it. NLWeb queries via the Cortex API. No `db_load.py` involvement.

**Cloudflare AutoRAG**: upload files to R2, point AutoRAG at the bucket, wire NLWeb to the AutoRAG endpoint. CF manages indexing.

**Shopify MCP**: zero ingest. NLWeb proxies queries to a Shopify store's MCP endpoint. Configure the shop domain per-site. Disable for non-commerce deployments.

**Bing**: API key required; only useful combined with at least one vector backend (Bing returns web pages, not your indexed content).

### Debugging Empty Results

Diagnostic ladder:
1. `curl http://localhost:8000/sites` — site is registered?
2. `curl 'http://localhost:8000/ask?query=test&site=X&mode=list&streaming=false'` — any results at all?
3. Disable all backends except the one you wrote to — does the write_endpoint return results?
4. Check embedding dimension: `python -c "from embedding_providers import get_default; print(get_default().dim)"` (verify exact API) and compare to your index schema.
5. Inspect the raw store: `qdrant` CLI / Azure Search Studio / `SELECT count(*) FROM index` for Postgres.
6. Re-ingest with the embedding provider that matches the index.

Always re-fetch `config_retrieval.yaml` from the live repo before generating config — keys change.
