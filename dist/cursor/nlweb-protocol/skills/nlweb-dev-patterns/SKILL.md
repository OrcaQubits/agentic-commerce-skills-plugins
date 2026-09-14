---
name: nlweb-dev-patterns
description: >
  NLWeb development patterns — the mixed-mode programming philosophy, FastTrack
  vs Analysis parallel paths, config file precedence and the `mode: development`
  override trap, in-stream NLWS headers vs HTTP headers, embedding/ingest
  determinism, debugging the LLM-call chain, neural scorer selection
  (NLWebScorer ModernBERT+GAM), and the A2A / AgentFinder / DataFinder /
  ModelRouter subsystems. Use when designing the internal architecture of an
  NLWeb deployment or solving cross-cutting concerns.
---

# NLWeb Development Patterns

> **Config layout changed upstream.** NLWeb replaced the single `site_types.xml` with two files in `config/`:
> **`sites.xml`** (site name → `itemType` list + description) and **`tools.xml`** (per-site / per-type tool
> definitions, prompts and examples, scoped by `<Site id="…">` / `<Item>` blocks). Older guidance — including any
> `site_type` / `extends` inheritance syntax — describes the retired file. **Fetch `config/sites.xml` and
> `config/tools.xml` from the live repo before editing anything.**

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-systemmap.md for module layout.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-control-flow.md for the request lifecycle.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/life-of-a-chat-query.md for an end-to-end trace.
4. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-configs-files.md for the config precedence rules.
5. Inspect `core/baseHandler.py`, `core/router.py`, `core/retriever.py`, `core/ranking.py` for current code paths.

## Pattern: Mixed-Mode Programming

NLWeb's defining design choice. Rather than one big LLM call per query, NLWeb makes **many small calls**, each with a strict JSON output schema (`<returnStruc>`), feeding Python control flow.

**Implications:**
- Cost and latency scale with the number of call sites, not the size of any one call.
- Failures are localized — one bad call doesn't poison the response.
- Steerability is high — you can tune any single prompt without touching the rest.
- Debugging is harder — you must trace which of N calls misbehaved.

**When designing extensions**, follow the same pattern: small, schema-constrained LLM calls, deterministic Python glue.

## Pattern: FastTrack vs Analysis (Parallel Paths)

`NLWebHandler` runs two paths in parallel:

| Path | What it does | When it wins |
|------|--------------|--------------|
| **FastTrack** | Immediate vector search → stream early results | Common queries with obvious retrieval matches |
| **Analysis** | Decontextualize → detect type → route via `ToolSelector` to a specific handler | Ambiguous queries, complex flows (compare, recipe substitution) |

Both paths stream into the same response. FastTrack results appear quickly; Analysis results appear when ready. The agent decides whether to render incrementally or wait.

**Implications for handlers you write**: if you write a slow, expensive handler, FastTrack will still beat you to first byte for simple queries. That's fine — it's the design.

## Pattern: Config File Precedence

8 YAML config files in `config/`. Precedence (highest first):

1. **Environment variables** (always win)
2. **Query-string params** — but only when `mode: development` in `config_webserver.yaml`
3. **YAML defaults**

The `mode: development` override is a **foot-gun in production**. A query like `?write_endpoint=other_qdrant` would silently switch the write target. Always set `mode: production` before deploying.

## Pattern: "Headers" Are In-Stream Messages, Not HTTP Headers

NLWeb's "NLWS headers" mechanism is **JSON message objects on the SSE channel**, not HTTP response headers. Each carries a `message_type`:

| message_type | Carries |
|--------------|---------|
| `license` | Content license terms |
| `data_retention` | How long the agent may cache |
| `cache_policy` | Caching directives |
| `usage_terms` | Acceptable use |
| `rate_limits` | Calls/sec, daily quota |
| `data_freshness` | Last index time |
| `api_version` | NLWeb release identifier |
| `ui_component` | Optional rendering hint |

**Client parsing rule**: buffer message objects until you see a `results` chunk or terminal marker. Don't assume the first chunk is data.

## Pattern: Embedding/Ingest Determinism

The most common NLWeb bug: changing the embedding provider after ingest, getting empty or garbage results.

**Rule**: pick the embedding provider FIRST, configure the retrieval backend's vector dimension to match, ingest with that provider, query with that provider. Never change mid-stream without re-ingesting.

If you need to migrate embedding providers:
1. Choose a maintenance window
2. Configure the new provider as the `preferred_provider`
3. `db_load.py --only-delete delete-site <site>` for each site
4. Re-ingest with the new provider
5. Restart and verify

## Pattern: Debugging the LLM Call Chain

When `/ask` returns a bad answer, the bug is in one of these call sites:

| Call site | Symptom | Fix |
|-----------|---------|-----|
| Decontextualize | Query rewritten wrong; off-topic results | Pre-compute `decontextualized_query`, log the prompt's output |
| Type detection | Wrong handler invoked | Pass `itemType` explicitly, or check `tools.xml` |
| Tool selection | Right type, wrong tool | Adjust tool descriptions; set `tool_selection_enabled: false` to bypass |
| Ranking | Top results are off | Check embedding alignment first; then try `scorer=nlwebscorer` |
| Summarize / generate | Final answer is poor | Improve Schema.org source data; bump model tier |

**Isolate by mode**: `mode=list` skips summarize/generate. If `list` is bad, the issue is retrieval or ranking, not synthesis.

## Pattern: NLWebScorer (Optional Neural Reranker)

The `NLWebScorer/` subsystem provides a ModernBERT + GAM neural reranker as an alternative to LLM-based ranking. Activate via `?scorer=nlwebscorer` on `/ask`. Configure checkpoints in `config_*.yaml`:

```yaml
scorers:
  nlwebscorer:
    bert_checkpoint: ./checkpoints/modernbert.pt
    gam_checkpoint: ./checkpoints/gam.pt
```

Use cases:
- Cost reduction (LLM-ranking is expensive at scale)
- Latency reduction (BERT is faster than even small LLMs)
- Reproducible ranking (no LLM stochasticity)

Tradeoff: it's domain-specific — you may need to fine-tune on your data. See `docs/training-recipe-modernbert-gam.md`.

## Pattern: The Five Subsystems

NLWeb's repo isn't just one server. Five top-level folders are conceptually distinct:

| Subsystem | Purpose | When relevant |
|-----------|---------|---------------|
| `AskAgent/` | The core `/ask` and `/mcp` server | Always |
| `AgentFinder/` | Cross-site NLWeb discovery (federated `/who`) | Multi-site federations |
| `DataFinder/` | NL→SQL for enterprise sources (HubSpot, Dynamics, Jira) | Enterprise data, not vector-backed |
| `ModelRouter/` | Cost/quality routing across LLM providers | Cost optimization at scale |
| `NLWebScorer/` | Neural reranker (ModernBERT + GAM) | High-volume retrieval |

Most deployments use only `AskAgent`. The rest are opt-in.

## Pattern: A2A and MCP as Co-Equal Bindings

NLWeb supports three transport bindings in parallel:

| Binding | Path | Audience |
|---------|------|----------|
| REST `/ask` | port 8000 | Browsers, custom clients |
| MCP `/mcp` | port 8000 | AI agents (Claude, Gemini, native MCP) |
| A2A | `webserver/a2a_wrapper.py`, route `a2a.py` | Google Agent-to-Agent protocol |
| AppSDK adapter | port 8100 | ChatGPT specifically |

All share the same backend pipeline. No data duplication. Choose by audience, not by feature.

## Pattern: Conversation Memory Hooks

`core/conversation_history.py` persists exchanges per authenticated user. `methods/conversation_search.py` queries the persisted history.

**Long-term memory** (cross-conversation user preferences) is NOT shipped. Hook points to add it:
- After response generation in `NLWebHandler.respond()` — extract durable facts, write to user profile
- Before query in the same handler — load user profile, inject into the decontextualize prompt

This is intentional: NLWeb leaves opinionated personalization to the integrator.

## Pattern: Idempotency and Retries

NLWeb doesn't define idempotency keys — `/ask` calls are read-side; replays are safe. `/mcp` follows JSON-RPC 2.0 semantics: include `id` in every request, retry with the same `id` if the connection drops mid-request (server may dedup if implemented).

For `db_load.py`, idempotency is **upsert by URL**. Re-running on the same source updates existing records rather than duplicating.

## Pattern: Schema.org as the Common Currency

Every result carries a `schema_object`. Agents pattern-match on `@type` to render appropriately. **Design rule**: any new tool or handler you write should preserve the `schema_object` in its output. Don't strip it down to text — that defeats the whole point of NLWeb.

## Pattern: Versioning

NLWeb releases as **dated markdown files in `docs/release_notes/`**, not semver tags. When pinning a deployment:

- Pin the git commit, not a tag
- Read the release_notes entries from your pinned commit to the latest before upgrading
- The MCP wrapper docstring explicitly warns "Backwards compatibility is not guaranteed" — re-test agent integrations on every upgrade

## Pattern: Don't Modify Core Files

Most extensibility goes via:
- `config/*.yaml` and XML files (preferred)
- New files in `methods/` (custom handlers)
- New providers in `llm_providers/`, `embedding_providers/`, `retrieval_providers/`
- aiohttp middleware in `webserver/middleware/`

Avoid editing `core/baseHandler.py`, `core/router.py`, etc. — they change frequently and your fork rots.

## Pattern: Disable Defaults Aggressively

The default config enables **three retrieval backends** (`qdrant_local`, `nlweb_west`, `shopify_mcp`), the **federated `/who` endpoint**, and **`mode: development`**. For any non-demo deployment, set these:

```yaml
# config_webserver.yaml
mode: production

# config_nlweb.yaml
who_endpoint_enabled: false

# config_retrieval.yaml
endpoints:
  nlweb_west: { enabled: false }
  shopify_mcp: { enabled: false }
```

These defaults make sense for hello-world demos. They are anti-patterns for production.

---

Always cross-reference with the latest `docs/release_notes/` and the live `core/` modules — patterns evolve and the code is the source of truth.
