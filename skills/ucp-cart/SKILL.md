---
name: ucp-cart
description: Implement the UCP Cart capability (`dev.ucp.shopping.cart`) — a lightweight CRUD surface for collecting line items before purchase intent exists, and its conversion into a Checkout session. Use when building pre-checkout item collection, shareable carts, or cart-recovery flows over REST, MCP, or Embedded bindings.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# UCP Cart Capability

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification shopping cart` and fetch the page for the exact Cart schema, operation names, and binding details. Also fetch `https://ucp.dev/latest/schemas/shopping/cart.json` for the authoritative JSON Schema. Field names and required-ness change between spec versions — never write the schema from memory.

## Conceptual Architecture

### Why Cart is separate from Checkout

Checkout carries payment handler configuration, buyer commitment, and a status lifecycle. That is overhead a buyer does not need while still browsing. Cart is the lightweight half: collect items, get estimated totals, share a link — with **no payment configuration and no status machine**.

The canonical progression is:

```
cart session  →  checkout session  →  order
```

Cart handles *exploration*. Checkout enforces *commitment*.

### Operations

| Operation | Purpose |
|-----------|---------|
| Create Cart | Initialize a session with line items and optional buyer / context data |
| Get Cart | Read current state; returns `not_found` once expired or cancelled |
| Update Cart | **Full replacement** of cart contents — not a patch |
| Cancel Cart | Terminate the session |

`Update Cart` replacing rather than merging is the detail most implementations get wrong. Send the complete intended line-item set every time.

### Key data model

- `id` — cart identifier
- `line_items` — entries with quantity (in the authoritative sale basis), unit price, and line totals
- `context` — localization signals: country, region, postal code, location
- `buyer` — optional name, email, phone
- `currency` — ISO 4217
- `totals` — **estimated** subtotal, tax, fulfillment, discounts
- `messages` — validation warnings and informational notices
- `continue_url` — handoff link for session recovery
- `expires_at` — optional expiry

### State model

Carts are binary: they exist or they do not. There is no `incomplete → completed` lifecycle, and **totals stay estimates** until checkout conversion. Treat any amount read from a cart as indicative only — never as something to charge against.

### Conversion to Checkout

Create a checkout referencing `cart_id`. Two rules govern this:

1. The business **uses the cart contents and ignores overlapping payload fields**. Do not attempt to pass line items alongside a `cart_id` and expect them to merge.
2. Conversion is **idempotent** — if an incomplete checkout already exists for that cart, the business returns the existing session rather than creating a second one.

After checkout completion the business may clear the cart, driven by TTL or its own business logic. Do not depend on the cart surviving.

### Bindings

Cart is exposed over **REST**, **MCP**, and **Embedded**. It is not an A2A capability. Negotiate it like any other capability — see `ucp-dev-patterns` for the intersection algorithm.

## Implementation Guidance

- Make `Create Cart` idempotent on your side too; agents retry aggressively.
- Populate `continue_url` — it is what makes a cart shareable and recoverable, which is the main reason Cart exists as a separate capability.
- Surface validation problems through `messages` rather than failing the whole request, so an agent can repair one line item without rebuilding the cart.
- Set `expires_at` deliberately and honour it in `Get Cart` with `not_found`.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
