---
name: ucp-permalink
description: >
  Implement the UCP Permalink capability — browser-addressable shopping intent
  URLs that initialize cart/checkout state via a compact item path and UCP
  field-path query parameters, then redirect the buyer. Use when building
  campaign links, QR/social buy links, buyer prefill, or store-pickup deep
  links.
---

# UCP Permalink Capability

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification permalink` and fetch the page for the exact path grammar, encoding rules, and the current list of addressable field-paths. The encoding rules in particular are easy to get subtly wrong — read them live.

## Conceptual Architecture

### Permalink is not an API

The defining property: **a permalink is a GET browser navigation, not a REST operation.** It has no request body, no auth header, and no JSON response. It is a URL a human can click from an email, a QR code, or a social post, which lands them in a shopping session with state already applied.

### Structure

A permalink is appended to an endpoint discovered from the business's UCP profile (e.g. `https://merchant.example/buy`):

```
/{items}?{query}
```

**Item path** — comma-separated `id:quantity` pairs:

```
/sku_123:2,sku_456:1
```

**Item encoding** — this is the part implementations get wrong. Simple identifiers matching `[A-Za-z0-9._-]+` are used directly. Anything else — notably opaque platform IDs like `gid://shopify/ProductVariant/70881412` — must be **base64url-encoded with a `~` prefix**, because raw slashes and colons break HTTP routing.

**Query parameters** — UCP **field-paths** mapped to values:

```
?buyer/email=alice@example.com&discounts/codes/0=SAVE10
```

The field-path addresses the cart/checkout schema directly, including extension fields. Array positions are numeric segments.

### Resolution

The business responds **`303 See Other`**, applying safe inputs to server-side state and redirecting to a buyer-facing destination.

Two rules constrain what a permalink may do:

1. **Query parameters cannot override line items.** The item path is authoritative.
2. **A business MUST NOT treat loading a permalink as authorization to place an order.** A permalink initializes state; it never commits a purchase. Anyone can construct one.

### `continue_to`

Specifies where the buyer navigates after processing. It **must be validated as same-origin** — an unvalidated `continue_to` is an open-redirect vulnerability, and it is the most likely security defect in a permalink implementation.

### Pass-through parameters

Non-UCP parameters pass through unchanged for analytics and attribution, **unless sensitive**. Do not blindly forward everything — filter anything that could carry credentials or PII into a third-party analytics context.

## Use cases

- **Campaign links** — bundled items plus a discount code plus attribution
- **Buyer prefill** — email, location, preferred payment handler
- **Social and QR** — compact item path with a continuation link
- **Store pickup** — pre-selected fulfillment destination

## Implementation Guidance

- Validate and normalize every field-path before applying it; treat the query string as fully untrusted input.
- Reject or ignore field-paths that address fields the buyer should not control (payment instrument data, totals, order state).
- Keep permalinks short enough to survive QR encoding and SMS — that is the constraint the compact item syntax exists to satisfy.
- Return `303`, not `302` — the method-rewrite semantics matter here.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
