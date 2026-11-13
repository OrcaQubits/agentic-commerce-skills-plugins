---
name: nlweb-auth-multitenancy
description: >
  Configure NLWeb authentication and multi-tenant deployments — OAuth providers
  (GitHub, Google, Microsoft, Facebook), session storage, the `sites:` allowlist
  in `config_nlweb.yaml`, conversation persistence per authenticated user, and
  per-tenant data isolation. Use when adding login to an NLWeb instance, hosting
  multiple customers on one deployment, or persisting conversation history.
---

# NLWeb Auth & Multitenancy

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/setup-oauth.md for OAuth configuration.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-memory.md for conversation persistence.
3. Inspect `AskAgent/python/webserver/routes/oauth.py` for the current OAuth flow.
4. Inspect `AskAgent/python/core/conversation_history.py` and `storage_providers/` for persistence backends.
5. Check `config/config_oauth.yaml` and `config/config_storage.yaml` for current keys.

## Conceptual Architecture

### NLWeb's Auth Model — What It Does and Doesn't Do

NLWeb ships OAuth-based **user identification** — it lets a logged-in user have persistent conversation memory tied to their identity. It does **not** ship:
- Fine-grained authorization (per-site ACLs)
- API key auth for service-to-service callers
- Multi-tenant data isolation at the retrieval layer

If you need any of those, you build them as middleware on top.

### OAuth Providers Supported

Per `config_oauth.yaml`:

| Provider | Notes |
|----------|-------|
| GitHub | Standard OAuth 2.0 |
| Google | Standard OAuth 2.0 |
| Microsoft | Entra ID / personal accounts |
| Facebook | Standard OAuth 2.0 |

Adding a new provider means a new client class in the OAuth routes module + a config entry. Verify the current extensibility mechanism in the live code.

### OAuth Routes

| Route | Purpose |
|-------|---------|
| `GET /api/oauth/login/{provider}` | Start the OAuth dance |
| `GET /api/oauth/callback/{provider}` | OAuth callback handler |
| `GET /api/oauth/logout` | End session |
| `GET /api/oauth/me` | Current user info |

(Verify exact paths in `webserver/routes/oauth.py`.)

### Session Storage

By default, NLWeb stores sessions in-memory or via an aiohttp session backend. For multi-instance deployments, configure a shared session store (Redis, etc.). The session cookie carries the user identity; conversation persistence keys off that identity.

### Conversation Persistence

`config_storage.yaml` selects which storage backend persists conversations:

| Backend | Notes |
|---------|-------|
| Qdrant (`qdrant_storage.py`) | Conversations as vectors — enables `conversation_search` tool |
| Azure AI Search (`azure_search_storage.py`) | Same idea, on Azure |
| Elasticsearch (`elasticsearch_storage.py`) | Same idea, on ES |

The choice often matches your retrieval backend so conversation search and content search share infrastructure. Anonymous users typically don't get persistence — verify if/how the config exposes this toggle.

### Multitenancy via `sites:` Allowlist

`config_nlweb.yaml` has a `sites:` list of allowed site names. Queries with `site=` not in the list are rejected. Patterns:

**Single-tenant**: just enumerate your own sites.

**Multi-customer SaaS**: prefix every site with a tenant ID (`tenant_a__products`, `tenant_b__products`), and add middleware that:
1. Reads the authenticated user's tenant from the session
2. Rewrites incoming `site` params to scope to that tenant's sites only
3. Rejects queries asking for sites outside the tenant's scope

NLWeb does not ship this middleware — you write it.

### Per-Tenant Data Isolation

At the retrieval layer:
- **Cheap path**: site naming convention as above. Single index, queries filter by site. Cheap but tenants share an index.
- **Strong isolation**: separate retrieval indexes / collections / databases per tenant. Configure NLWeb with multiple endpoints (e.g., `qdrant_tenant_a`, `qdrant_tenant_b`) and route based on the authenticated user.

The strong-isolation path requires more config wrangling but is the only safe choice for regulated tenants.

### User Identity in Conversation Search

`methods/conversation_search.py` queries the conversation storage scoped to the current user. The user ID flows from the OAuth session into the handler context. Without OAuth, this tool returns empty.

### Headers for Permission Signaling

NLWeb's in-stream "headers" (the `message_type` JSON objects in SSE) include `usage_terms` and `rate_limits`. These can carry per-user policy — e.g., a higher-tier user gets a higher `rate_limits.daily_quota`. NLWeb doesn't enforce this; the client agent inspects and respects it.

## Implementation Guidance

### Enabling OAuth

1. Register an OAuth app with the provider (e.g., GitHub OAuth Apps).
2. Set the redirect URI to `https://your-host/api/oauth/callback/github`.
3. Set env vars (verify exact names in `config_oauth.yaml`):
   ```
   GITHUB_OAUTH_CLIENT_ID=...
   GITHUB_OAUTH_CLIENT_SECRET=...
   ```
4. Edit `config_oauth.yaml` to enable the provider:
   ```yaml
   providers:
     github:
       enabled: true
       scopes: ["read:user"]
   ```
5. Restart. Visit `/api/oauth/login/github` to test.

### Adding Multi-Tenant Middleware

A sketch (aiohttp middleware):

```python
@web.middleware
async def tenant_scope_middleware(request, handler):
    user = await get_user_from_session(request)
    if user is None:
        return web.json_response({"error": "auth required"}, status=401)

    requested_site = request.query.get("site") or ""
    allowed_prefix = f"{user['tenant_id']}__"
    if not requested_site.startswith(allowed_prefix):
        return web.json_response({"error": "site not in tenant scope"}, status=403)

    return await handler(request)
```

Register on the aiohttp app before NLWeb's own handlers. Verify the exact insertion point in `webserver/aiohttp_server.py`.

### Persisting Conversations Per User

1. Pick a storage backend in `config_storage.yaml` (Qdrant for dev, Azure Search / ES for prod).
2. Ensure OAuth is on (anonymous users don't get persistence by default).
3. Verify the storage class records `user_id` on each conversation row — it does in current code; verify after upgrade.

### Letting Anonymous Users Query Without Persistence

For public sites:
- Leave OAuth optional
- Allow anonymous `/ask` but skip persistence
- Disable `conversation_search` tool for anonymous users (it would return empty anyway)

Confirm the current behavior — anonymous policy has changed across releases.

### API Keys for Service Callers

NLWeb does NOT ship API key auth out of the box. Add it as middleware:

```python
@web.middleware
async def api_key_middleware(request, handler):
    key = request.headers.get("X-API-Key")
    if request.path.startswith("/api/oauth/"):
        return await handler(request)  # OAuth flow exempt
    if not is_valid_key(key):
        return web.json_response({"error": "invalid key"}, status=401)
    return await handler(request)
```

Issue keys via a separate admin endpoint or out-of-band.

### Hardening Sessions for Multi-Instance

- Use a shared session backend (Redis via `aiohttp-session` redis storage).
- Set secure cookie flags (`Secure`, `HttpOnly`, `SameSite=Lax`).
- Rotate the session secret on a schedule.
- Set a sane session TTL.

### Common Pitfalls

- **OAuth callback URL mismatch** — the provider rejects the redirect. Copy the URL byte-for-byte.
- **In-memory sessions lose users on restart** — wire a shared backend before going multi-instance.
- **Conversations not persisting** — storage backend not configured OR user is anonymous OR storage backend's index doesn't exist.
- **Tenant leakage** — middleware order is wrong, OR the storage backend isn't filtering by user. Pen-test before launch.
- **`who` endpoint exposes tenant names** — disable `who_endpoint_enabled` for multitenant deployments.

Always re-fetch the OAuth and storage docs from the live repo — auth code moves between releases.
