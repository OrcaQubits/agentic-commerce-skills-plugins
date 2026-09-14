---
name: ucp-payment-terms
description: Implement the UCP Payment Terms extension (`dev.ucp.common.payment.terms`) — offering the buyer a choice of when payment is due via payment terms and schedules (pay now, deposit plus balance, deferred). Use when building split-timing payment options into a UCP checkout.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# UCP Payment Terms Extension

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification payment extensions terms` and fetch the page for the exact term/schedule schema and the current `type` vocabulary. The vocabulary is open-ended and grows — read it live.

## Conceptual Architecture

### The question it answers

Payment Terms (`dev.ucp.common.payment.terms`) lets a business offer the buyer a choice of **when** payment is due. It is about timing, not about which instrument pays — that is `ucp-payment-handlers`, and for multiple instruments at once, `ucp-split-payments`.

### Two nested concepts

- **Payment Term** — an addressable option composed of one or more payment schedules. "Pay now." "Deposit plus balance at check-in."
- **Payment Schedule** — a single payment within a term: amount, description, `type`, and optional due date.

A term is the thing the buyer selects; schedules are what that selection actually commits them to.

### Timing classes

The schedule `type` field uses an **open vocabulary**. `immediate` means due on checkout completion; other values (e.g. `deferred`) mean it is not. Because the vocabulary is open, handle unknown `type` values gracefully — render the description rather than failing.

### Fields added to `checkout.payment`

- `terms[]` — available term options. **Response-only** — the platform never writes this.
- `selected_term_id` — which term the buyer chose.

### The recalculation rule

This is the part that breaks implementations. Selecting a term triggers a **complete recomputation**. Amounts shown in `terms[]` are *indicative pricing* for unselected terms.

> Re-render from the business response after selecting a term. Never reuse amounts read from `terms[]`.

Term selection can change totals, payment handler eligibility, policies, and messages. All of these become authoritative **only in the response**. A client that optimistically renders the `terms[]` amount it already had will show the buyer a number the business did not agree to.

### The summation invariant

The selected term's schedule amounts **must sum to the checkout total**. If they do not, the checkout is in an invalid state — surface it rather than rounding it away.

## Implementation Guidance

- Treat `terms[]` as strictly read-only on the platform side; the only thing you write is `selected_term_id`.
- After every term selection, discard cached totals and re-render from the response — including fields you would not expect to move, like available payment handlers.
- Validate the summation invariant on receipt; a mismatch is a business-side bug worth surfacing loudly in development.
- Render schedule descriptions verbatim. Deferred-payment terms often carry regulatory disclosure obligations that live in that text.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
