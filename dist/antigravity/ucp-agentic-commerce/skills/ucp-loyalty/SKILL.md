---
name: ucp-loyalty
description: >
  Implement the UCP Loyalty extension — memberships, tiers, benefits, and
  rewards surfaced across catalog, cart, and checkout, with reverse-DNS program
  namespaces, `context.eligibility` claims, and provisional vs verified
  membership. Use when adding member pricing, tier recognition, or rewards
  forecasting to a UCP flow.
---

# UCP Loyalty Extension

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification common extensions loyalty` and fetch the page for the exact eligibility claim shape, membership/tier schema, and current error codes.

## Conceptual Architecture

### Three use cases

Loyalty exists to serve three distinct things, and conflating them causes most design mistakes:

1. **Price-impacting benefits** — member discounts, member shipping. These flow through the **discount extension**, not through loyalty fields directly.
2. **Non-price benefits** — rewards tracking, dedicated support. Value that is real but does not move the total.
3. **Status recognition** — tier verification for display.

### The model

- **Memberships** — independent enrollment pathways within a brand, modeled as **separate sibling entries**. A "Rewards Club" and a "Co-branded Credit Card" are two memberships, not one membership with two facets.
- **Tiers** — achievement ranks within a membership. Members typically hold **one active tier per membership**, though parallel status dimensions allow multiple concurrent tiers.
- **Benefits** — perks tied to tier/membership status. Immediate-value (5% off) and delayed-value (priority support).
- **Rewards** — quantifiable value *earned* from a transaction. Distinct from redeemable balances, which are **payment instruments**, not loyalty fields.

That last distinction matters: points you *earn* are rewards; points you *spend* are a payment instrument and belong in the payment flow (see `ucp-split-payments`).

### Namespacing

Programs use **reverse-domain naming** — `com.example.loyalty`, `com.example.rewards.card` — to prevent collisions and establish provenance. The same reverse-domain key the platform submits is the key the business returns as the membership identifier.

### Claims and verification

The platform submits buyer claims via **`context.eligibility`** in requests. The business either verifies the claim or determines membership from authenticated identity.

Three outcomes:

| Outcome | Response |
|---------|----------|
| **Verified** | `provisional: false`, active `tiers` included, masked `display_id` set, price-impacting benefits applied via the discount extension |
| **Unverified** | `provisional: true`, **no** `display_id` |
| **Invalid** | error message with code `eligibility_invalid` |

**All accepted claims must be resolved at checkout completion.** A provisional membership cannot survive into a completed order — either it verifies or its benefits come off.

### Where it surfaces

Loyalty spans catalog, cart, and checkout. Monetary benefits appear in `totals` or `line_items` with loyalty attribution; reward forecasts include earning breakdowns linked to specific tier benefits.

## Implementation Guidance

- Never render a `display_id` for a provisional membership — that is exactly the field the spec withholds until verification, and showing an unverified one implies a status the buyer may not have.
- Apply price-impacting benefits through the discount extension so they reconcile with every other discount rather than becoming a parallel pricing path.
- Model each enrollment as its own membership entry, even when they share a brand.
- Treat `provisional: true` at completion time as a hard error path, not a warning.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
