---
name: nlweb-ask-endpoint
description: >
  Implement and consume the NLWeb /ask REST endpoint — request shape (GET/POST,
  query-string and v0.55 structured body), SSE streaming response, modes
  (list/summarize/generate), in-stream "message_type" headers, error envelopes,
  and client-side parsing. Use when building an NLWeb server route, calling /ask
  from a custom agent, or debugging /ask responses.
---

# NLWeb /ask Endpoint

## Before writing code

**Fetch live spec**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md for the canonical `/ask` contract — request params, response shape, and streaming format.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/life-of-a-chat-query.md to trace a request end-to-end.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-headers.md for the **in-stream "headers"** mechanism (license, data-retention, rate-limit messages are NOT HTTP headers).
4. Web-search the latest release notes for the **v0.55+ structured POST body** shape (`query.text`, `prefer.mode`, `prefer.streaming`, `meta.version`) — this is newer than the GET-only legacy contract.
5. Check `webserver/routes/api.py` in the live repo to confirm exact param names.

## Conceptual Architecture

### Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/ask` | GET, POST | Main NL query |
| `/who` | GET | Site relevance for a query (federated) |
| `/sites` | GET | List configured sites |
| `/config` | GET | Public config (safe subset) |

### Request Parameters

Verify exact names against the live `routes/api.py`. Stable subset:

| Param | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `query` | string | yes | — | NL question |
| `site` | string | no | all | Backend partition; in MCP can be array |
| `prev` | string | no | — | Comma-separated previous queries (conversation context) |
| `decontextualized_query` | string | no | — | Pre-resolved query; skips server-side decontextualization |
| `streaming` | bool | no | `true` | `"0"` / `"false"` / `"False"` disables |
| `query_id` | string | no | auto | Echoed in response |
| `mode` | enum | no | `list` | `list` \| `summarize` \| `generate` |
| `scorer` | string | no | default | e.g., `nlwebscorer` for the neural reranker |
| `itemType` | string | no | — | Schema.org type hint (skip type detection) |
| `response_format` | string | no | — | v0.55 structured-body field |

### v0.55 Structured POST Body

The newer body format groups fields:

```json
{
  "query": { "text": "your question" },
  "context": { "prev": ["previous q1", "previous q2"] },
  "prefer": {
    "mode": "list",
    "streaming": true,
    "response_format": "schema"
  },
  "meta": { "version": "0.55" }
}
```

Verify the exact field names against the live docs before relying on this — fields are still settling.

### Streaming Response Format (SSE)

NLWeb uses Server-Sent Events when `streaming=true` (the default):

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

Each chunk is:
```
data: <json>\n\n
```

The `<json>` is one of:
- A **message object** (header-like): `{"message_type": "license", "content": {...}}`
- A **partial result**: `{"results": [...]}` (results may arrive incrementally as FastTrack streams)
- A **terminal object**: `{"query_id": "...", "complete": true}` (exact field — verify live)

### In-Stream "Headers" (NLWS Mechanism)

NLWeb's "headers" are NOT HTTP response headers — they are JSON objects in the SSE stream with a `message_type` discriminator. Known types:

| message_type | Purpose |
|--------------|---------|
| `license` | Content license terms |
| `data_retention` | How long the agent may cache results |
| `cache_policy` | Caching directives |
| `ui_component` | Optional rendering hint |
| `usage_terms` | Acceptable use |
| `rate_limits` | Calls/sec / day budget |
| `data_freshness` | When the underlying data was last indexed |
| `api_version` | Server's NLWeb version |

**Client parsing rule**: don't assume `results` is the first chunk. Buffer message objects until you see the result stream or a terminal marker.

### Non-Streaming Response

With `streaming=false`, the server returns a single `application/json` body:

```json
{
  "query_id": "abc-123",
  "messages": [{"message_type": "license", "content": {...}}, ...],
  "results": [
    {
      "url": "https://example.com/article/x",
      "name": "Article X",
      "site": "example",
      "score": 0.83,
      "description": "...",
      "schema_object": { "@type": "Article", "@context": "https://schema.org", ... }
    }
  ]
}
```

The `schema_object` is the original Schema.org JSON-LD that was indexed — this is what makes NLWeb results **agent-actionable**, not just text snippets.

### Three Modes

| Mode | Behavior | Use case |
|------|----------|----------|
| `list` | Return ranked Schema.org results, no LLM synthesis | Agent does its own rendering / re-ranking |
| `summarize` | LLM condenses top results into a short answer + still returns results | Conversational UIs |
| `generate` | Full RAG — LLM synthesizes an answer grounded in results | Q&A endpoints |

### Errors

For `/ask`, errors generally come back as 500 with a JSON envelope. For `/mcp`, errors use JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": { "code": -32603, "message": "Internal error", "data": {...} }
}
```

Always check status code before parsing — partial SSE streams can drop with 200 followed by silence.

## Implementation Guidance

### Server-Side (extending the route)

If you need to extend `/ask` (e.g., add an auth check or custom param):
1. Locate `webserver/routes/api.py`
2. Add middleware in `webserver/middleware/` rather than modifying the route directly — keeps you upgrade-safe
3. Forward to `NLWebHandler` (`core/baseHandler.py`) unchanged so the streaming + ranking pipeline still runs

### Client-Side (calling /ask)

```python
# Python streaming client (sketch — verify response shape against the live spec)
import httpx, json

async with httpx.AsyncClient() as client:
    async with client.stream("GET", "http://localhost:8000/ask",
                              params={"query": "best running shoes", "site": "shoes", "mode": "generate"}) as r:
        async for line in r.aiter_lines():
            if not line.startswith("data: "):
                continue
            obj = json.loads(line[6:])
            if "message_type" in obj:
                handle_header(obj)
            elif "results" in obj:
                handle_results(obj["results"])
```

### When to use which mode

- Agent that re-ranks and selects on its own → `mode=list`
- Quick conversational answer with citations → `mode=summarize`
- Single synthesized answer (chatbot-style) → `mode=generate`

### Debugging /ask

- Set `streaming=false` first — easier to inspect a single JSON body.
- Add `decontextualized_query` to bypass query rewriting and isolate ranking issues.
- Try `mode=list` to see the raw retrieval — if results are bad here, the problem is ingest/embeddings, not the LLM.
- Pass `query_id` and grep server logs for it.
- Disable `tool_selection_enabled` in `config_nlweb.yaml` to bypass the router and force straight retrieval.

Always verify the exact param names and message_type values against the live spec — they evolve.
