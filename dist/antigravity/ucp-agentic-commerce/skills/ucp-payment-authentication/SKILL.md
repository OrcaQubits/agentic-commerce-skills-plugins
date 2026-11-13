---
name: ucp-payment-authentication
description: >
  Implement the UCP Payment Authentication extension
  (`dev.ucp.common.payment.authentication`) — browser-surface actions for device
  data collection and 3DS challenge during a payment attempt, including the
  ready/done handshake and origin validation. Use when adding 3-D Secure or
  strong customer authentication to a UCP checkout.
---

# UCP Payment Authentication Extension

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification payment extensions authentication` and fetch the extension page plus the two action pages (`device-data-collection`, `three-ds-challenge`) for the exact action config fields and handshake message names. This extension touches payment security — do not implement it from memory.

## Conceptual Architecture

### What it does, and what it does not

The extension standardizes the **browser-surface interactions** a platform may need to process while a payment attempt is underway. It extends the checkout capability with namespace `dev.ucp.common.payment.authentication`.

It deliberately **does not replace EMV 3DS protocol details**. UCP carries *where the surface lives and when to show it*; the 3DS protocol itself remains between the issuer, the network, and the payment handler.

### Two actions

| Action | Namespace | Surface |
|--------|-----------|---------|
| Device Data Collection | `dev.ucp.common.payment.device_data_collection` | **Invisible**, browser-capable — collects device fingerprinting data |
| 3DS Challenge | `dev.ucp.common.payment.three_ds_challenge` | **Buyer-facing** — presents the authentication challenge |

Device data collection is invisible by design. Rendering it visibly, or skipping it because "nothing shows", breaks the authentication that follows.

### Action occurrence fields

Each emitted action carries:

- `id` — unique action identifier
- `payment_instrument_id` — which payment instrument in the checkout this applies to
- `url` — the surface endpoint, **validated against handler-approved origins**

### Sequencing

The business emits **device data collection first** (if needed), waits for completion, then emits the **3DS challenge in a subsequent checkout response**. These are two round-trips, not one payload. A platform that tries to render both at once has misread the flow.

### The ready handshake

Both surfaces follow the same three-step handshake:

1. Surface sends `action.ready`
2. Platform confirms
3. Surface signals `action.done` or `action.error`

The confirmation step exists so the platform can guarantee the surface is mounted and isolated before the authentication flow starts.

### Platform responsibilities

- **Validate origins** against the handler-approved list before loading any surface `url`.
- **Maintain isolation** — the surface must not be able to reach into the host page.
- **Reconcile outcomes against the authoritative checkout state.** An `action.done` is a signal that the surface finished, *not* proof that authentication succeeded. The checkout response is authoritative; re-read it.

## Implementation Guidance

- Treat `url` as untrusted until origin-validated, every time — not once at configuration.
- Handle `action.error` and timeout as distinct paths; a challenge the buyer abandons is not the same as one that failed.
- Never infer payment success from the action handshake. Complete the checkout and read the result.
- Test the human-abandonment path explicitly; it is the most common real-world outcome after "success".
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
