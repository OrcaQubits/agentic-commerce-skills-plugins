---
name: acp-cart
description: Implement the ACP Cart API — the pre-checkout REST surface for collecting line items without payment configuration, covering create, retrieve, full-replacement update, and cancel, plus estimated totals, `continue_url`, and expiry. Use when building ACP cart sessions ahead of an agentic checkout.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Cart API

## Before writing code

**Fetch live spec** — the Cart API arrived in the `2026-04-17` release, so anything older will not describe it:

1. Fetch `https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/releases` to identify the **current** spec version.
2. Fetch the OpenAPI document for that version: `spec/<version>/openapi/openapi.cart.yaml` in the repo. This is authoritative for paths, headers, and status codes.
3. Fetch `spec/<version>/json-schema/schema.cart.json` for the Cart object schema.
4. Web-search `site:developers.openai.com commerce cart` for narrative guidance.

Never write the request/response shapes from memory — read the OpenAPI document.

## Conceptual Architecture

### What Cart is for

A **lightweight pre-checkout phase for item collection**, with:

- no payment configuration,
- no capability negotiation,
- no status lifecycle.

Checkout carries all of that. Cart deliberately carries none of it, so an agent can assemble a basket cheaply while the buyer is still deciding.

### Endpoints

| Method | Path | Operation |
|--------|------|-----------|
| `POST` | `/carts` | `createCart` — returns **201** |
| `GET` | `/carts/{id}` | `getCart` |
| `PUT` | `/carts/{id}` | `updateCart` |
| `POST` | `/carts/{id}/cancel` | `cancelCart` |

### Update is full replacement

> The agent MUST send the complete desired cart state. The provided `line_items` replace the existing cart contents.

This is the single most important behaviour to get right. `PUT /carts/{id}` is not a patch. Sending one changed line item silently discards the rest of the basket.

### Cancel semantics

`cancelCart` returns the cart state **before** deletion, so the caller gets a final snapshot. Subsequent operations on that cart ID should return **404**.

`getCart` also returns **404** when the cart does not exist, **has expired**, or **was cancelled** — these are indistinguishable to the caller by design.

### Headers

Cart uses the standard ACP header set. `Authorization` (Bearer API key), `Content-Type`, and `API-Version` are required; `Accept-Language`, `Idempotency-Key`, and `Request-Id` are optional but you should send them.

Send `Idempotency-Key` on every mutating call — create, update, and cancel all accept it, and agents retry.

### Cart object

- `id`
- `line_items` — each with `id`, an `item` (`id`, `name`, `unit_amount`), `quantity`, and line-level `totals`
- `currency`
- `totals` — an array of typed entries (`subtotal`, `total`, …), **not** a flat object
- `continue_url` — hand-off link into the seller's own surface
- `expires_at`

Amounts are integers in the currency's minor unit (`12000` = $120.00). Never send a decimal.

### Availability failures

When **all** requested items are unavailable, the seller MAY return **422** with `type: invalid_request`, `code: out_of_stock` rather than creating a cart. Handle 422 distinctly from 400 — it means "understood, but nothing purchasable", which is a different remediation for an agent than a malformed request.

## Implementation Guidance

- Treat `totals` as an ordered array of typed entries and look up by `type`; do not index positionally.
- Always send the full `line_items` set on update. If your client holds a partial view of the cart, `GET` first.
- Surface `continue_url` to the buyer — it is the escape hatch from agent to seller-owned checkout.
- Honour `expires_at` and return 404 after it passes rather than serving a stale cart.
- Relates to `acp-checkout-rest` (the next phase) and `acp-capability-negotiation` (which Cart deliberately skips).
