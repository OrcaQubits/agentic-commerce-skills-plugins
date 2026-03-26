---
name: saleor-graphql
description: Work with the Saleor GraphQL API — queries, mutations, subscriptions, cursor pagination, filters, error handling, GraphQL Playground, and code generation. Use when building against the Saleor API.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor GraphQL API

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/api-reference` for API reference overview
2. Web-search `site:docs.saleor.io GraphQL queries mutations examples` for query patterns
3. Web-search `site:docs.saleor.io cursor pagination first after` for pagination reference
4. Web-search `site:docs.saleor.io authentication JWT token` for auth token handling
5. Web-search `site:docs.saleor.io GraphQL error handling` for mutation error patterns
6. Fetch `https://docs.saleor.io/docs/developer/api-conventions` for API conventions

## GraphQL-First Architecture

Saleor exposes its entire functionality through a single GraphQL endpoint. There is no REST API -- all interactions (storefront, dashboard, apps, integrations) use GraphQL exclusively.

| Aspect | Detail |
|--------|--------|
| Endpoint | `/graphql/` |
| Protocol | HTTP POST with JSON body |
| Introspection | Enabled by default (disable in production if needed) |
| Playground | Available at the API URL in browser |
| Schema | Single unified schema for all consumers |

## Authentication

| Method | Use Case | Header |
|--------|----------|--------|
| JWT (Staff) | Dashboard operations, admin mutations | `Authorization: Bearer <token>` |
| JWT (Customer) | Storefront customer actions | `Authorization: Bearer <token>` |
| App Token | App-to-Saleor API calls | `Authorization: Bearer <app-token>` |
| No Auth | Public storefront queries (products, collections) | None required |

### Token Lifecycle

| Operation | Mutation |
|-----------|---------|
| Staff login | `tokenCreate(email, password)` |
| Customer login | `tokenCreate(email, password)` |
| Refresh token | `tokenRefresh(refreshToken)` |
| Verify token | `tokenVerify(token)` |

Tokens are short-lived JWTs. Always use `tokenRefresh` to obtain new access tokens rather than re-authenticating.

## Query Patterns

### Product Queries

| Query | Purpose |
|-------|---------|
| `products(first, after, filter, channel)` | List products with pagination |
| `product(id, slug, channel)` | Single product by ID or slug |
| `categories(first, after, filter)` | List categories |
| `collections(first, after, filter, channel)` | List collections |

### Order Queries

| Query | Purpose |
|-------|---------|
| `orders(first, after, filter)` | List orders (staff) |
| `order(id)` | Single order detail |
| `me { orders }` | Customer's own orders |
| `draftOrders(first, after)` | List draft orders (staff) |

### Channel Scoping

Most storefront queries require a `channel` argument to scope results:

```graphql
query Products($channel: String!) {
  products(first: 10, channel: $channel) {
    edges { node { id name pricing { ... } } }
  }
}
```

Queries without a channel argument return data across all channels (staff only).

## Cursor-Based Pagination

Saleor uses Relay-style cursor pagination throughout its API:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `first` | Int | Number of items from the start |
| `after` | String | Cursor to paginate forward |
| `last` | Int | Number of items from the end |
| `before` | String | Cursor to paginate backward |

### Pagination Response Structure

| Field | Purpose |
|-------|---------|
| `edges[].node` | The actual data object |
| `edges[].cursor` | Opaque cursor for this edge |
| `pageInfo.hasNextPage` | Whether more items exist forward |
| `pageInfo.hasPreviousPage` | Whether more items exist backward |
| `pageInfo.startCursor` | Cursor of the first edge |
| `pageInfo.endCursor` | Cursor of the last edge |
| `totalCount` | Total number of matching items |

## Filtering

Saleor provides typed filter input objects for each queryable resource:

| Filter Input | Key Fields |
|-------------|-----------|
| `ProductFilterInput` | `search`, `price`, `categories`, `collections`, `productTypes`, `isPublished` |
| `OrderFilterInput` | `created`, `status`, `customer`, `paymentStatus` |
| `CustomerFilterInput` | `search`, `dateJoined`, `numberOfOrders` |

Filters are passed as the `filter` argument on list queries.

## Mutations and Error Handling

Saleor mutations return the result alongside an `errors` array in the response:

| Field | Purpose |
|-------|---------|
| `<entity>` | The created/updated object on success |
| `errors` | Array of `{ field, message, code }` on failure |

### Common Error Codes

| Code | Meaning |
|------|---------|
| `REQUIRED` | A required field is missing |
| `INVALID` | Field value is invalid |
| `NOT_FOUND` | Referenced object does not exist |
| `UNIQUE` | Value violates a uniqueness constraint |
| `GRAPHQL_ERROR` | General GraphQL execution error |

Always check the `errors` array -- a mutation may return HTTP 200 with validation errors in the response body.

## Subscriptions

Saleor supports GraphQL subscriptions for real-time webhook payloads:

| Aspect | Detail |
|--------|--------|
| Transport | Webhook POST (not WebSocket) |
| Definition | Subscription query defines the payload shape |
| Registration | Via App manifest or `webhookCreate` mutation |
| Use Case | Custom webhook payloads with only the fields you need |

Subscription queries are attached to webhook configurations to define exactly which fields are delivered in the payload.

## GraphQL Playground

The built-in Playground is available at the API endpoint URL in a browser:

| Feature | Detail |
|---------|--------|
| Schema explorer | Browse all types, queries, mutations |
| Query editor | Write and execute queries with autocomplete |
| Auth header | Add `Authorization: Bearer <token>` in HTTP Headers panel |
| History | Previously executed queries are saved |
| Docs panel | Inline documentation for all fields |

## Code Generation

| Tool | Purpose |
|------|---------|
| `graphql-codegen` | Generate TypeScript types from Saleor schema |
| `@graphql-codegen/typed-document-node` | Typed document nodes for queries |
| `@graphql-codegen/introspection` | Generate introspection JSON |

### Codegen Configuration

```yaml
# codegen.yml — Fetch live docs for current config shape
schema: "https://your-saleor-instance.com/graphql/"
documents: "src/**/*.graphql"
generates:
  src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
```

## Best Practices

- Always scope storefront queries with the `channel` argument
- Use cursor pagination (`first`/`after`) -- never request unbounded lists
- Check the `errors` array on every mutation response, even on HTTP 200
- Use `tokenRefresh` to renew JWTs instead of storing long-lived tokens
- Define only the fields you need in queries to minimize response size
- Use GraphQL code generation for type safety in TypeScript projects
- Leverage subscription queries for webhook payloads to get exactly the data shape you need

Fetch the Saleor GraphQL API documentation for exact query signatures, filter input types, and mutation patterns before implementing.
