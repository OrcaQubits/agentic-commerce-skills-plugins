---
name: ucp-split-payments
description: >
  Implement the UCP Split Payments extension
  (`dev.ucp.common.payment.split_payments`) — paying a single checkout with
  multiple instruments, specified vs open amounts, allocation order,
  `allowed_combinations` config, and atomic completion. Use when supporting gift
  cards plus a card, or any multi-instrument checkout.
---

# UCP Split Payments Extension

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification payment extensions split-payments` and fetch the page for the exact `allowed_combinations` shape and the current failure-message codes. This extension governs money movement across multiple authorizations — implement it against the live spec, not from memory.

## Conceptual Architecture

### Scope

Split Payments (`dev.ucp.common.payment.split_payments`) lets a buyer pay with **multiple payment instruments in a single checkout**. The canonical case is a gift card covering part of the total with a card covering the rest.

### Two submission modes

- **Specified-amount** — the platform requests a specific contribution from an instrument.
- **Open-amount** — the business determines the contribution at processing time. This is what gift cards need: the balance is not known to the platform, so it asks the business to take whatever is there.

Each payment instrument gains an optional `amount` field, in **ISO 4217 minor units**.

### Allocation order

Instruments are processed **in submission order**, and that order establishes allocation priority:

> The first instrument gets first claim on the checkout total, the second gets next claim, and so on.

The business may *authorize* in any operational order it likes, but it must respect the array sequence when deciding **how much** each instrument covers. Practically: put the gift card first if you want it drained before the card is charged.

### `allowed_combinations`

Businesses declare which instrument groupings they accept. Each combination contains instrument groups specifying:

- `types` — accepted instrument types, **OR** logic within the group
- `min` — minimum instruments required (defaults to 0)
- `max` — maximum instruments allowed (defaults to 1)

Read this config before constructing a payment array; an unsupported combination fails at completion, after the buyer has committed.

### Atomicity — the rule that matters most

Split payments complete **atomically**. If the business cannot process a specified-amount instrument, or cannot reach the final total:

- it **MUST** return `payment_failed` in `messages[]`, and
- it **MUST** void or reverse any authorizations it already made.

There is no partial success. A buyer never ends up with a drained gift card and no order.

### Response `amount` is not state

Response `amount` fields convey **actual charges for buyer-facing UX and auditing only**. They do not persist as state across requests. Do not read an amount off a response and send it back on the next request expecting it to mean the same thing.

## Implementation Guidance

- Order the instrument array deliberately — it is the allocation policy, not just a list.
- Use open-amount for any instrument whose balance the platform cannot know; guessing produces avoidable `payment_failed`.
- On the business side, treat the void/reverse path as the primary path in testing. Partial-failure rollback is where real money is lost.
- Validate the proposed combination against `allowed_combinations` client-side before completion, so the buyer learns early.
- Combines with `ucp-payment-terms` (when payment is due) and `ucp-payment-handlers` (how each instrument is processed).
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
