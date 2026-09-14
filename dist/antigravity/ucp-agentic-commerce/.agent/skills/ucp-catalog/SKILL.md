---
name: ucp-catalog
description: >
  Implement the UCP Catalog capability (`dev.ucp.shopping.catalog`) — free-text
  product Search and identifier-based Lookup, the Product/Variant data model,
  media, ratings, and quantity units. Use when exposing product discovery to
  agents or consuming a business catalog before cart and checkout.
---

# UCP Catalog Capability

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification shopping catalog` and fetch the capability page plus its `search` and `lookup` operation pages. The Product/Variant schema and filter vocabulary evolve between spec versions — read the live schema before writing types.

## Conceptual Architecture

### What Catalog is for

Catalog is the **discovery** half of UCP, upstream of Cart and Checkout. It covers free-text product search, category and filter-based browsing, batch retrieval by identifier, and price comparison across variants. Without it, an agent can only transact against items it already knows the IDs for.

### Two operations

| Operation | Namespace | Purpose |
|-----------|-----------|---------|
| Search | `dev.ucp.shopping.catalog.search` | Locate products by query text and filters |
| Lookup | `dev.ucp.shopping.catalog.lookup` | Retrieve specific products or variants by identifier |

Search is for *finding*; Lookup is for *resolving*. An agent typically searches once and then looks up identifiers it has cached or received from elsewhere (a permalink, a previous cart).

### Product vs Variant — the distinction that matters

- **Product** — a sellable item: title, description, media, one or more variants, and an overall **price range**.
- **Variant** — the **transactional unit**: specific option selections (colour, size), its own price, and availability. Each variant has a unique ID, and **that ID is what goes into checkout**.

Never put a product ID into a line item. Products are for display; variants are for purchase.

### Supporting types

- **Price** — amount in **minor currency units** plus ISO 4217 code. Never a float.
- **Quantity Unit** — the sale basis: each, weight, length, time, with optional ordering granularity via increment values. A catalog selling cable by the metre and a catalog selling t-shirts are both expressible.
- **Selected Option** — chosen values for product options, which is what differentiates variants.
- **Media** — images, video, 3D models, with URLs and optional accessibility text.
- **Rating** — aggregate value, scale bounds, review count.

### Ordering and relevance

Responses are relevance-ordered: businesses return the **most relevant variant and image first**. An agent rendering a single thumbnail or picking a default variant should take element zero rather than applying its own heuristic.

### Messages

Responses carry an optional `messages` array for errors, warnings, and informational notices. Warnings with `presentation: "disclosure"` are **non-dismissible** — allergen statements, safety information, regulatory notices. A client must render these; treating them as dismissible toast is a compliance problem, not a UX choice.

### Bindings

Catalog is exposed over **REST** and **MCP** (JSON-RPC). Over MCP, search and lookup become tools an agent calls directly — see `ucp-checkout-mcp` for the binding conventions.

## Implementation Guidance

- Return variant-level availability, not just product-level; agents need to know *which* size is in stock.
- Price filters are denominated in the **context currency** — resolve context before applying them.
- Keep Lookup genuinely batch-capable; agents resolve many identifiers at once and N+1 lookups will dominate latency.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
