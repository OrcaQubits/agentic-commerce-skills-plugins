---
name: spree-api-v3
description: >
  Build with Spree's v3 APIs (v5.4+) — Store API at `/api/v3/store/*`
  (publishable key + per-user JWT, customer-facing) and Admin API at
  `/api/v3/admin/*` (per-user API keys + OAuth2 Doorkeeper, admin/operations).
  Covers the flat-JSON Stripe-like envelope, `?expand=` / `?include=`
  parameters, prefixed IDs (`prod_…`, `ord_…`), OpenAPI 3.0 spec, rate limiting,
  idempotency, and migration from v2 JSON:API. Use when building API clients,
  SDKs, or extending API endpoints in a Spree v5.4+ deployment.
---

# Spree API v3

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/api-reference for the v3 API index.
2. Fetch the OpenAPI spec for the Spree version you target — it ships per release. Find the link on the API reference page.
3. Fetch the v5.4 announcement (https://spreecommerce.org/announcing-spree-commerce-5-4/) for the design rationale.
4. Inspect the live Spree source under `app/controllers/spree/api/v3/` for the canonical request/response shape per endpoint.
5. Check the rate-limit configuration in `config/initializers/spree.rb` for the deployment you're targeting.

## Conceptual Architecture

### Two APIs, One Generation

| API | Path | Auth | Audience |
|-----|------|------|----------|
| **Store API** | `/api/v3/store/*` | Publishable key (`pk_…`) + per-user JWT bearer | Customers, storefronts |
| **Admin API** | `/api/v3/admin/*` | Per-user API keys + OAuth2 (Doorkeeper) | Admin, operations, server-to-server |

Both follow the same envelope conventions.

### Envelope Conventions

**Flat JSON** (Stripe-like), not JSON:API:

```json
{
  "id": "prod_01HXVZ...",
  "object": "product",
  "name": "Classic Tee",
  "description": "100% cotton",
  "created_at": "2026-04-15T10:00:00Z",
  "variants": ["var_01HXVZ...", "var_01HXVZ..."],
  "default_variant": {
    "id": "var_01HXVZ...",
    "object": "variant",
    "sku": "TEE-S",
    "price": "19.99",
    "currency": "USD"
  }
}
```

vs. v2's JSON:API:
```json
{ "data": { "id": "1", "type": "product", "attributes": { ... }, "relationships": { ... } } }
```

### Prefixed IDs

IDs are strings with type prefixes:

| Prefix | Type |
|--------|------|
| `prod_` | Product |
| `var_` | Variant |
| `ord_` | Order |
| `usr_` | User |
| `pay_` | Payment |
| `ship_` | Shipment |
| `cust_` | Customer |
| `pm_` | PaymentMethod |
| `sm_` | ShippingMethod |
| `txn_` | Transaction |
| `prom_` | Promotion |

Prefixed IDs are **stable** — never reused, safe to expose, decoupled from internal database IDs. Verify the full prefix table in the live docs.

### Listing and Pagination

```
GET /api/v3/store/products?limit=25&starting_after=prod_…&ending_before=prod_…
```

Returns:

```json
{
  "object": "list",
  "url": "/api/v3/store/products",
  "has_more": true,
  "data": [ { "id": "prod_…", ... }, ... ]
}
```

Cursor pagination via `starting_after` / `ending_before` (verify against live spec — may be page-based on some endpoints).

### Expanding Relationships

```
GET /api/v3/store/orders/ord_…?expand=line_items,line_items.variant,shipping_address
```

`expand` inlines nested objects; `include` (also supported) returns them in a separate `included` array. Verify which convention the version you're on uses.

### Filtering

Per-endpoint filter params:
```
GET /api/v3/admin/orders?status=complete&payment_state=paid&created_after=2026-01-01
```

Verify the filter set per endpoint in the OpenAPI spec.

### Auth — Store API

Two layers:

1. **Publishable key** (`pk_…`) — identifies the store + currency. Required on every request via `Authorization: Bearer pk_…` or `X-Spree-Token` header (verify current).
2. **User JWT** — issued by `/api/v3/store/account/sign_in`, sent in `Authorization: Bearer <jwt>`. Identifies the logged-in user.

For guest carts, the cart's `order_token` is sent in `X-Spree-Order-Token`.

### Auth — Admin API

Two paths:

1. **Per-user API key** — generated in admin UI per user. Sent in `Authorization: Bearer <api_key>`. Inherits the user's roles.
2. **OAuth2 (Doorkeeper)** — for app integrations. `client_credentials` grant against `POST /spree_oauth/token` returns an access token with `admin` scope.

### Rate Limiting

Per-endpoint, per-token. Defaults set in `config/initializers/spree.rb`. Headers returned:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1715000000
```

Verify the exact header names against the live source.

### Idempotency

For mutating endpoints (POST/PUT), send `Idempotency-Key: <uuid>` to ensure retries don't double-create. Spree caches the response for 24+ hours (verify current TTL).

### Errors

```json
{
  "object": "error",
  "type": "validation_error",
  "code": "invalid_email",
  "message": "Email is not valid",
  "param": "email",
  "request_id": "req_…"
}
```

HTTP status codes follow standard REST: 400 / 401 / 403 / 404 / 422 / 429 / 500.

### Webhooks

Webhooks 2.0 fire alongside API operations — see `spree-events-webhooks` skill.

## Implementation Guidance

### Setting Up the Store API

In Spree admin → Settings → API Keys:
- Create a publishable key (`pk_live_…` or `pk_test_…`) per store
- Set the storefront's `NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY` env var

### Customer Sign-In Flow

```http
POST /api/v3/store/account/sign_in
Authorization: Bearer pk_live_…
Content-Type: application/json

{ "email": "user@example.com", "password": "..." }
```

Response:
```json
{
  "object": "auth_token",
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "..."
}
```

Store in **httpOnly cookie** (server-side); never expose to the browser.

### Cart Creation (Guest)

```http
POST /api/v3/store/cart
Authorization: Bearer pk_live_…
```

Response includes `order_token` — store in httpOnly cookie. Subsequent cart calls use `X-Spree-Order-Token`.

### Listing Products

```http
GET /api/v3/store/products?expand=default_variant,images&limit=20
Authorization: Bearer pk_live_…
```

### Admin Order Update

```http
PATCH /api/v3/admin/orders/ord_…
Authorization: Bearer <admin_api_key>
Idempotency-Key: <uuid>
Content-Type: application/json

{ "internal_note": "Customer requested expedited shipping" }
```

### Admin OAuth2 Token

```http
POST /spree_oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=...&client_secret=...&scope=admin
```

Response:
```json
{ "access_token": "...", "token_type": "Bearer", "expires_in": 7200, "scope": "admin" }
```

### Migrating From v2 (JSON:API) to v3

Field shape changes:
- `data.attributes.name` → `name`
- `data.attributes.created-at` → `created_at`
- `data.relationships.variants.data` → `variants` (array of prefixed IDs by default; `expand=variants` to inline)
- `data.id` (numeric string) → prefixed ID

You can run v2 and v3 side-by-side during migration via the `spree_legacy_api_v2` gem.

### Generating a TypeScript Client From OpenAPI

```bash
npx @openapitools/openapi-generator-cli generate \
  -i https://your-spree.com/api/v3/openapi.json \
  -g typescript-axios \
  -o ./generated-client
```

But prefer `@spree/sdk` if you don't need every endpoint — see the `spree-typescript-sdk` skill.

### Common Pitfalls

- **Mixing v2 and v3 in the same client** — different envelopes, easy to confuse.
- **Storing API keys in browser code** — only publishable keys belong on the client; secret keys on the server.
- **Ignoring rate-limit headers** — bursty clients get 429s.
- **Skipping Idempotency-Key on retries** — double-charges, duplicate orders.
- **Hardcoding prefixed IDs in tests** — they're ULIDs/UUIDs; use the response's value.
- **Assuming v2 endpoint paths still work** — `/api/v2/storefront/cart` is the legacy path; v3 is `/api/v3/store/cart`.

Always re-fetch the OpenAPI spec for the version you're on — field shapes can shift between minor releases.
