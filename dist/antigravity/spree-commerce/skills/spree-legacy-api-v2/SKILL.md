---
name: spree-legacy-api-v2
description: >
  Work with Spree's legacy v2 APIs — JSON:API-style Storefront API at
  `/api/v2/storefront/*` and Platform API at `/api/v2/platform/*`, Doorkeeper
  OAuth2 (password grant for storefront, client_credentials + admin scope for
  platform), the `spree_legacy_api_v2` gem (required in v5+ for backward
  compatibility), and migration patterns to API v3. Use when maintaining a v2
  client during a migration window, integrating an older partner system, or
  deciding when to cut over to v3.
---

# Spree Legacy API v2

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/spree/spree_legacy_api_v2 (README) for the current install and supported Spree versions.
2. The historical v2 docs may live at https://api.spreecommerce.org/ — verify what's still hosted.
3. Compare with the v3 reference at https://spreecommerce.org/docs/api-reference to plan migration.
4. Check the Spree release notes — v2 endpoints can be removed without notice in major upgrades.
5. Inspect the gem's controllers under `app/controllers/spree/api/v2/`.

## Conceptual Architecture

### What Was v2

API v2 was the canonical Spree API across v4.x and v5.0–5.3. Two surfaces:

| API | Path | Auth | Audience |
|-----|------|------|----------|
| **Storefront API** | `/api/v2/storefront/*` | Doorkeeper password grant + publishable `X-Spree-Order-Token` | Customer-facing |
| **Platform API** | `/api/v2/platform/*` | Doorkeeper `client_credentials` grant + `admin` scope | Admin/operations |

Style: **JSON:API 1.0** — `{ data: { id, type, attributes, relationships } }` envelope.

### v2 Status in v5+

- Bundled in `spree` umbrella through v5.3.
- **Extracted to the `spree_legacy_api_v2` gem from v5.4+** — not in the umbrella by default.
- Deprecated; will eventually be removed. Treat any new development as v3-first.

### Why It Existed (and Still Matters)

Apps built between 2020 and 2025 use v2. The gem keeps those clients working while you migrate to v3.

### Adding the Gem in v5.4+

```ruby
# Gemfile
gem 'spree_legacy_api_v2'

# Then
bundle install
bin/rails g spree_legacy_api_v2:install   # if a generator is shipped — verify
```

Mounts `/api/v2/storefront/*` and `/api/v2/platform/*`.

### Auth — Storefront API v2

**Password grant** (verify current OAuth2 grant types accepted):

```http
POST /spree_oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=user@example.com&password=...
```

Response:
```json
{ "access_token": "...", "token_type": "Bearer", "expires_in": 7200, "refresh_token": "..." }
```

For guest carts, use `X-Spree-Order-Token` header. Some v2 endpoints accept anonymous access with just an order token.

### Auth — Platform API v2

**Client credentials grant** with `admin` scope:

```http
POST /spree_oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=...&client_secret=...&scope=admin
```

Doorkeeper applications are managed in admin → Settings → OAuth Applications.

### JSON:API Envelope

```json
{
  "data": {
    "id": "1",
    "type": "product",
    "attributes": {
      "name": "Classic Tee",
      "description": "100% cotton",
      "created-at": "2025-04-15T10:00:00Z",
      "price": "19.99"
    },
    "relationships": {
      "variants": { "data": [{ "id": "2", "type": "variant" }] },
      "default-variant": { "data": { "id": "2", "type": "variant" } }
    }
  },
  "included": [
    { "id": "2", "type": "variant", "attributes": { ... } }
  ]
}
```

Compare with v3's flat JSON — different fundamental shape.

### Sparse Fieldsets & Includes

```
GET /api/v2/storefront/products?include=default_variant,images&fields[product]=name,price
```

`include` pulls related resources into `included`; `fields[type]` filters attributes per type.

### Pagination

JSON:API style:
```
GET /api/v2/storefront/products?page=2&per_page=25
```

Returns `links.first`, `links.next`, `links.prev`, `links.last` + `meta.total_count`, `meta.total_pages`.

### Filtering

```
GET /api/v2/platform/orders?filter[state]=complete&filter[created_at_gteq]=2025-01-01
```

Filters use Ransack syntax (`_eq`, `_gteq`, `_lteq`, `_in`, `_not_eq`, etc.). Powerful but verbose.

### Errors

```json
{
  "errors": [
    {
      "status": "422",
      "code": "invalid_email",
      "title": "Invalid email",
      "detail": "Email is not valid",
      "source": { "pointer": "/data/attributes/email" }
    }
  ]
}
```

## Implementation Guidance

### Decision: v2 or v3 for New Work?

**Always v3** unless:
- You're integrating with an existing v2 partner that can't migrate yet
- You're shipping a patch for an existing v2-only client
- The v3 endpoint coverage is missing for your use case (rare in v5.4+)

### Running v2 and v3 Side-By-Side

In v5.4+, gem-installing `spree_legacy_api_v2` mounts v2 endpoints without conflict — v3 lives at `/api/v3/`, v2 at `/api/v2/`. Same Doorkeeper applications can serve both.

### Authenticating a Storefront v2 Client

```ruby
require 'net/http'
require 'json'

# Get a token
res = Net::HTTP.post(
  URI('https://your-spree.com/spree_oauth/token'),
  { grant_type: 'password', username: email, password: pwd }.to_query,
  'Content-Type' => 'application/x-www-form-urlencoded'
)
token = JSON.parse(res.body)['access_token']

# Use it
req = Net::HTTP::Get.new('/api/v2/storefront/account')
req['Authorization'] = "Bearer #{token}"
```

### Authenticating a Platform v2 Client

```ruby
res = Net::HTTP.post(
  URI('https://your-spree.com/spree_oauth/token'),
  { grant_type: 'client_credentials',
    client_id: ENV['CLIENT_ID'],
    client_secret: ENV['CLIENT_SECRET'],
    scope: 'admin' }.to_query,
  'Content-Type' => 'application/x-www-form-urlencoded'
)
admin_token = JSON.parse(res.body)['access_token']
```

### Migrating From v2 to v3

Field-level changes:

| v2 (JSON:API) | v3 (flat JSON) |
|---------------|----------------|
| `data.id` ("1") | `id` ("prod_…") |
| `data.attributes.name` | `name` |
| `data.attributes.created-at` (kebab) | `created_at` (snake) |
| `data.relationships.variants.data[]` | `variants` (array of IDs) |
| `included[]` | inline via `?expand=` |
| OAuth2 password grant | Publishable key + JWT |
| OAuth2 client_credentials + admin | Per-user API key OR OAuth2 |

Migration strategy:
1. Stand up v3 endpoints in parallel
2. Update one client surface at a time (start with read-only paths)
3. Sunset v2 after observability shows no calls for N weeks
4. Eventually remove the gem

### Common Pitfalls

- **Forgetting to install `spree_legacy_api_v2`** in v5.4+ — your v2 clients silently 404.
- **Mixing v2 and v3 client code** in the same component — different envelope shapes, hard to maintain.
- **Sparse fieldsets without `include`** — relationships still show as `null` references; you need to also include them.
- **Ransack filters expose more than you want** — by default, all model columns are filterable. Configure `ransackable_attributes` per model in production.
- **Password grant exposing user credentials** — only the storefront uses it; never use password grant in third-party integrations.
- **Token refresh not handled** — v2 tokens expire; implement refresh on 401.

Always cross-check the legacy gem's README for the Spree version it currently supports — the gem can lag the umbrella by minor releases.
