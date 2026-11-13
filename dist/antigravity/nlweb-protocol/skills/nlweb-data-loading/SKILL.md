---
name: nlweb-data-loading
description: >
  Ingest site content into NLWeb's vector store using `db_load.py` — supports
  RSS/Atom feeds, Schema.org JSON-LD, sitemap-driven URL lists, and CSV. Covers
  chunking, embedding computation, site partitioning, batch sizing,
  delete-and-reload, and per-backend write_endpoint targeting. Use when
  bootstrapping a site's index, refreshing content, or migrating between
  retrieval backends.
---

# NLWeb Data Loading

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/tools-database-load.md for the canonical `db_load.py` reference.
2. Inspect `AskAgent/python/data_loading/db_load.py` and `db_load_utils.py` in the live repo for exact CLI flags — they've added flags in recent releases.
3. Check `AskAgent/python/data_loading/rss2schema.py` for how RSS items map to Schema.org `Article` objects.
4. Confirm the **embedding provider** used at ingest matches `preferred_provider` in `config_embedding.yaml` for the query side — mismatch = silent retrieval failure.
5. For partner backends, check `docs/setup-snowflake.md`, `docs/setup-cloudflare-autorag.md`, etc. for backend-specific ingest steps (some bypass `db_load.py`).

## Conceptual Architecture

### What db_load Does

`db_load.py` is the canonical ingest pipeline. Given a source and a site name, it:

1. **Fetches** the source (RSS feed, JSON-LD URL, sitemap-derived URL list, CSV).
2. **Normalizes** each item to a Schema.org JSON object (uses `rss2schema.py` for feeds; passes JSON-LD through; maps CSV columns by convention).
3. **Chunks** long text fields (description, body) if needed.
4. **Computes embeddings** via the configured embedding provider in `config_embedding.yaml`.
5. **Writes** to the `write_endpoint` configured in `config_retrieval.yaml`.
6. **Tags** every record with the `site` value so retrieval can partition.

### Supported Source Types

| Source | Detection | Notes |
|--------|-----------|-------|
| RSS / Atom feed | URL ending `.rss`, `.xml`, `/feed`, or content-type | Mapped to `Article` Schema.org type |
| Schema.org JSON-LD | URL returns `application/ld+json` or HTML with embedded JSON-LD | Preserved as-is |
| Sitemap.xml | URL ending `sitemap.xml` | Crawled for child URLs |
| URL list file | `--url-list path.txt` flag | One URL per line; each fetched and parsed for JSON-LD |
| CSV | `.csv` extension | Column-to-Schema.org mapping by convention; see docs |

### Site Partitioning

Every record carries a `site` field. Queries filter by `site=<name>` to scope retrieval. **Choose site names carefully** — they're user-visible in `/sites` and become part of the agent UX. Conventions:
- Lowercase, no spaces, hyphens or underscores
- One site per logical content domain (not per RSS feed; aggregate related feeds under one site)

### Embedding Dimension Trap

The most common ingest bug: data was loaded with embedding model A (dim 1536), but at query time `config_embedding.yaml` points to model B (dim 768). Retrieval silently returns garbage because vector dimensions don't align — or fails entirely if the backend enforces dimension constraints. **Always verify the embedding provider hasn't changed between ingest and query.**

### Write Endpoint Selection

`db_load.py` writes to **one** endpoint at a time — the `write_endpoint` in `config_retrieval.yaml`, or override with `--database <endpoint-name>`. If you need data in multiple backends, run `db_load` multiple times changing the write endpoint each time.

### Delete and Reload

Sites can be wiped:

```bash
python -m data_loading.db_load --only-delete delete-site <site-name>
```

Without `--only-delete`, the loader does **upsert by URL** — re-running on the same source updates existing records but leaves stale ones. For full refresh, delete first, then load.

### Batch Sizing

`--batch-size N` controls how many records are embedded + written per round-trip. Defaults are sane (~100). Increase for large ingests if your embedding provider rate-limit allows.

### Parallel Loading

`data_loading/parallel_db_load.sh` runs multiple loaders concurrently across sources. Use for cold-start across dozens of feeds. Watch rate limits on the embedding provider — Azure OpenAI has aggressive throttling.

## Implementation Guidance

### Loading an RSS Feed

```bash
python -m data_loading.db_load https://example.com/feed.xml my-blog
```

Each item in the feed becomes a Schema.org `Article` with `headline`, `description`, `url`, `datePublished` populated from the RSS fields. Embeddings come from concatenating headline + description (verify exact field selection in `rss2schema.py`).

### Loading Schema.org JSON-LD

For sites that already serve JSON-LD (Recipe, Product, Event, Article, Movie, etc.), point `db_load` at a sitemap or URL list:

```bash
python -m data_loading.db_load --url-list urls.txt my-recipes
```

Each URL is fetched; the embedded JSON-LD is extracted and indexed verbatim. This is the **highest-fidelity ingest path** — the agent gets the full schema_object back at query time.

### Loading CSV

```bash
python -m data_loading.db_load products.csv my-store
```

CSV columns must follow the Schema.org property naming convention (or the column-mapping rules in `db_load_utils.py` — verify). For products, columns like `name`, `description`, `url`, `image`, `offers.price`, `offers.priceCurrency` are common.

### Overriding the Write Endpoint

```bash
python -m data_loading.db_load --database azure_ai_search source.xml my-site
```

Useful for parallel ingest across backends, or for promoting a dev qdrant_local index to prod Azure AI Search.

### Incremental Refresh Pattern

```bash
# Daily — incremental upsert (existing records updated, new added, stale left)
python -m data_loading.db_load https://example.com/feed.xml my-blog

# Weekly — full refresh
python -m data_loading.db_load --only-delete delete-site my-blog
python -m data_loading.db_load https://example.com/feed.xml my-blog
```

### Verifying a Load

After ingest:
- `curl http://localhost:8000/sites` — your site should appear
- `curl 'http://localhost:8000/ask?query=test&site=my-blog&streaming=false&mode=list'` — should return non-empty results
- Inspect a result's `schema_object` field — confirm it has the Schema.org properties you expect

### Backend-Specific Ingest

Some retrieval backends bypass `db_load.py` entirely:

- **Cloudflare AutoRAG** — ingest is managed by Cloudflare; you upload to R2 and AutoRAG indexes for you. See `docs/setup-cloudflare-autorag.md`.
- **Snowflake Cortex Search** — data lives in Snowflake tables; Cortex Search indexes are created via SQL. NLWeb just queries.
- **Shopify MCP** — no ingest; NLWeb proxies to Shopify's MCP endpoint live.
- **Bing Web Search** — no ingest; live web search.

### Common Failures

- **`db_load` hangs on embedding** — your embedding provider is rate-limiting. Reduce `--batch-size` or switch provider.
- **Records load but never appear in `/ask`** — check `sites:` allowlist in `config_nlweb.yaml`; check that `write_endpoint` and the enabled read endpoints actually overlap.
- **Loaded RSS but `schema_object` is sparse** — RSS doesn't carry rich Schema.org metadata. Either accept it or move to JSON-LD ingest.
- **Embedding dim mismatch** — re-ingest with the correct provider, or change `config_embedding.yaml` to match what was ingested.

Always cross-check flags against the live `db_load.py` — argument names drift release to release.
