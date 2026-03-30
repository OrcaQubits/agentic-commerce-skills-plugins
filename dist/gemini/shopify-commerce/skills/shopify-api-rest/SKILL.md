---
name: shopify-api-rest
description: >
  "MIGRATION SKILL: Shopify REST Admin API — endpoint patterns, authentication,
  rate limits, and REST-to-GraphQL migration guide. The REST Admin API is
  deprecated (October 2024). Use this skill only for maintaining legacy
  integrations or planning migration to GraphQL."
---

# Shopify REST Admin API (DEPRECATED)

> **DEPRECATION NOTICE:** The Shopify REST Admin API was deprecated in October 2024. All new development MUST use the GraphQL Admin API. This skill exists for maintaining legacy code and planning migration.

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev rest admin api deprecation` for deprecation timeline
2. Web-search `site:shopify.dev migrate rest to graphql` for migration guide
3. Fetch `https://shopify.dev/docs/api/admin-rest` for REST reference (if maintaining legacy code)

## REST API Overview (Legacy)

### Endpoints

- Base URL: `https://{store}.myshopify.com/admin/api/{version}/`
- Resources: `products.json`, `orders.json`, `customers.json`, etc.
- CRUD via HTTP methods: GET, POST, PUT, DELETE

### Authentication

- Header: `X-Shopify-Access-Token: {token}`
- Same OAuth tokens work for both REST and GraphQL

### Rate Limits

- Bucket-based: 40 requests per app per store (leaky bucket)
- Headers: `X-Shopify-Shop-Api-Call-Limit: 32/40`
- Plus stores: 80 requests

### Pagination

- Cursor-based via `Link` header (not page numbers)
- `rel="next"` and `rel="previous"` links

## REST-to-GraphQL Migration

### Common Mappings

| REST Endpoint | GraphQL Equivalent |
|---------------|-------------------|
| `GET /products.json` | `query { products(first: 50) { edges { node { ... } } } }` |
| `POST /products.json` | `mutation { productCreate(input: {...}) { ... } }` |
| `PUT /products/{id}.json` | `mutation { productUpdate(input: {...}) { ... } }` |
| `DELETE /products/{id}.json` | `mutation { productDelete(input: {id: "..."}) { ... } }` |
| `GET /orders.json` | `query { orders(first: 50) { edges { node { ... } } } }` |
| `GET /customers.json` | `query { customers(first: 50) { edges { node { ... } } } }` |

### Key Differences

| Aspect | REST | GraphQL |
|--------|------|---------|
| Data shape | Fixed response | Client-defined |
| Rate limiting | Request count (40/s) | Cost-based (1000 points) |
| Pagination | Link headers | Cursor arguments |
| Bulk operations | Not available | `bulkOperationRunQuery` |
| Webhooks | REST endpoint | Same (subscription via GraphQL) |
| ID format | Numeric (`12345`) | GID (`gid://shopify/Product/12345`) |

### ID Conversion

REST uses numeric IDs; GraphQL uses Global IDs (GIDs):
- REST: `12345`
- GraphQL: `gid://shopify/Product/12345`
- Convert: prefix with `gid://shopify/{ResourceType}/`

## Migration Strategy

1. **Audit** existing REST calls — list all endpoints and frequencies
2. **Map** each REST call to its GraphQL equivalent
3. **Migrate incrementally** — replace one endpoint at a time
4. **Leverage bulk operations** — replace paginated REST loops with single bulk queries
5. **Update error handling** — GraphQL returns 200 with `userErrors`, not HTTP status codes
6. **Test thoroughly** — responses have different shapes

## Best Practices

- Do NOT write new code against the REST API
- Prioritize migrating high-frequency REST calls first
- Use bulk operations to replace REST pagination loops
- Update ID handling from numeric to GID format
- Test migration against a development store

Fetch the Shopify REST-to-GraphQL migration guide for exact endpoint mappings and timeline before planning a migration.
