---
name: sf-b2c-scapi
description: "Build with Salesforce Commerce API (SCAPI) — Shopper APIs (Products, Search, Baskets, Orders, Customers), SLAS authentication, Commerce SDK for Node.js, rate limiting, pagination, and headless commerce patterns. This is the primary B2C API. Use when building headless storefronts or API integrations."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-b2c-scapi

Build headless commerce experiences and API integrations with Salesforce Commerce API (SCAPI).

## Before Writing Code

**Fetch live documentation FIRST:**
- Search: "Salesforce Commerce API SCAPI reference 2026"
- Search: "Commerce SDK Node.js documentation"
- WebFetch: `developer.salesforce.com/docs/commerce/commerce-api/references` (SCAPI API reference)
- WebFetch: `developer.salesforce.com/docs/commerce/commerce-api/guide/slas.html` (SLAS auth guide)
- WebFetch: `github.com/SalesforceCommerceCloud/commerce-sdk` (Commerce SDK repo)

**Why:** SCAPI is the modern API replacing OCAPI. Endpoints, authentication flows, rate limits, and SDK versions change frequently. Always verify current specs before implementing.

## Conceptual Architecture

### API Families

| Family | Scope | Examples |
|--------|-------|---------|
| **Shopper Products** | Product data for storefront | Product details, images, prices, variations |
| **Shopper Search** | Product discovery | Keyword search, refinements, facets, suggestions |
| **Shopper Baskets** | Cart operations | Create basket, add/remove items, shipping, payment |
| **Shopper Orders** | Order lifecycle | Create order from basket, order history, status |
| **Shopper Customers** | Customer identity | Registration, profile, addresses, payment methods |
| **Shopper Promotions** | Pricing incentives | Active promotions, promotion details |
| **Shopper Gift Certificates** | Gift cards | Balance check, redemption |
| **Einstein** | AI recommendations | Product and search recommendations |
| **Pricing / Inventory** | Admin data | Price books, multi-location inventory |

### SLAS Authentication Overview

SCAPI uses SLAS (Shopper Login and API Access Service) for OAuth 2.0 authentication. Two primary flows exist:

| Flow | Client Type | Use Case |
|------|------------|----------|
| **Authorization Code + PKCE** | Public (browser/mobile) | Guest and registered shoppers in frontend apps |
| **Client Credentials** | Private/confidential (server) | Server-to-server integrations, back-office tools |

- Guest shoppers use PKCE with `hint=guest` -- this is NOT client_credentials
- Registered users use PKCE with username/password login
- Tokens expire (typically 30 min); implement refresh before expiry
- Configure SLAS in Account Manager: redirect URIs, allowed origins, token lifetime

### Session Bridging

When transitioning a guest user to a registered session (login during checkout), SCAPI supports session bridging to preserve the guest basket. The guest token is exchanged for a registered token via the SLAS token endpoint, and the basket is merged server-side. Fetch live docs for the exact merge behavior and conflict resolution rules.

### Rate Limiting

| Aspect | Detail |
|--------|--------|
| Scope | Per client ID, per endpoint |
| Typical range | 1,000 -- 10,000 requests/min (varies by API) |
| Burst | Short burst allowances above sustained rate |
| Headers | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| On 429 | Exponential backoff; respect `Retry-After` header |

### Pagination

SCAPI uses offset-based pagination with `limit` and `offset` parameters. Responses include `total` count and a `next` link. Avoid deep pagination on large result sets -- use refinements to narrow results instead.

### Commerce SDK

Two SDK packages exist:

| Package | Environment | Notes |
|---------|------------|-------|
| `commerce-sdk` | Node.js only | Server-side integrations |
| `commerce-sdk-isomorphic` | Browser + Node.js | PWA Kit and universal apps |

```javascript
// Pattern: SDK initialization
// Fetch live docs for current config shape
import { ShopperProducts } from 'commerce-sdk-isomorphic';
const client = new ShopperProducts(config);
```

```javascript
// Pattern: Search with refinements
// Fetch live docs for refinement syntax
const results = await searchClient.productSearch({
  parameters: { q, limit, offset, refine, sort }
});
```

### Search Refinement Syntax

| Syntax | Meaning |
|--------|---------|
| `attribute=value` | Exact match |
| `attribute=(min..max)` | Range filter |
| `attribute=val1\|val2` | OR condition |
| `cgid=category-id` | Category refinement |

## Best Practices

### Authentication
- Use SLAS for all auth; never use OCAPI credentials with SCAPI
- Implement token refresh before expiry
- Use PKCE for all public (browser/mobile) clients
- Store client credentials in environment variables, never in code

### SDK and Performance
- Always use the Commerce SDK rather than raw HTTP calls
- Cache product/category responses with appropriate TTLs
- Use ETags for conditional requests (`If-None-Match`)
- Implement debouncing for search-as-you-type

### Error Handling
- Parse structured SCAPI error responses for field-specific messages
- Implement fallbacks for API failures (graceful degradation)
- Log errors with request ID and parameters for debugging

Fetch the SCAPI API reference, Commerce SDK README, and SLAS guide for exact endpoint paths, request/response shapes, and SDK configuration before implementing.
