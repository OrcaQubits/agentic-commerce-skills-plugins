---
name: acp-delegate-authentication
description: Implement the ACP Delegate Authentication API — delegating 3D Secure (3DS2) consumer authentication to merchant-specified providers, covering session creation, fingerprint and challenge actions, the authenticate call, and status handling. Use when adding strong customer authentication or 3DS to an ACP checkout.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Delegate Authentication (3DS)

## Before writing code

**Fetch live spec** — this API arrived in the `2026-04-17` release:

1. Fetch `https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/releases` for the current spec version.
2. Fetch `spec/<version>/openapi/openapi.delegate_authentication.yaml` — authoritative for paths, request fields, statuses, and headers.
3. Fetch `spec/<version>/json-schema/schema.delegate_authentication.json` for the schemas.
4. Read `acp-delegated-payment` alongside this — authentication and payment delegation are separate but adjacent flows.

This API handles **card data and authentication outcomes**. Implement it from the live spec, never from memory or an example found elsewhere.

## Conceptual Architecture

### What it delegates

Consumer authentication — specifically **3D Secure 2** browser-based flows — to a **merchant-specified authentication provider**. The agent does not perform 3DS itself; it drives a provider that does, and carries the result back into checkout.

Note the server in the spec is the *authentication provider*, not the seller. This is a distinct party from the merchant endpoints in `acp-checkout-rest`.

### Endpoints

| Method | Path | Operation |
|--------|------|-----------|
| `POST` | `/delegate_authentication` | `createAuthenticationSession` — **201** |
| `POST` | `/delegate_authentication/{authentication_session_id}/authenticate` | `authenticateSession` |
| `GET` | `/delegate_authentication/{authentication_session_id}` | `getAuthenticationSession` |

### Session statuses

| Status | Meaning |
|--------|---------|
| `action_required` | The provider needs a browser-side action performed — see below |
| `pending` | In progress; no action needed from the caller yet |
| `not_supported` | The card is not enrolled in 3DS |
| `authenticated` | Authentication succeeded |
| `not_authenticated` | Authentication failed |

`not_supported` is **not** a failure. It means the card is not enrolled and the flow should continue without 3DS — treating it as a decline will reject good transactions.

### Two action types

- **`fingerprint`** — invisible device data collection, run before any challenge. Nothing is shown to the buyer.
- **`challenge`** — the buyer-facing 3DS challenge.

The sequence is fingerprint first (when required), then challenge if the issuer asks for one. A session may return `action_required` more than once.

### Request contents

Creating a session carries, broadly:

- **merchant and acquirer identity** — `merchant_id`, plus `acquirer_details` (acquirer BIN, country, acquirer merchant ID, merchant name, requestor ID). 3DS is acquirer-scoped; these are not optional decoration.
- **`payment_method`** — card details.
- **`amount`** — `value` in minor units plus `currency`.
- **`channel`** — for `browser`, the full 3DS browser profile: accept header, IP, JS enabled, language, user agent, colour depth, screen dimensions, timezone offset. The issuer's risk engine consumes these; sending partial or fabricated values degrades authentication outcomes.
- **`flow_preference`** — e.g. requesting or preferring a challenge.
- **`challenge_notification_url`** — where the challenge result is delivered.
- **`shopper_details`** and **`checkout_session_id`** to tie the session to the checkout.

### Headers

Required: `Authorization` (Bearer API key), `Content-Type`, `API-Version`.

Optional but meaningful: `Idempotency-Key`, `Request-Id`, `Accept-Language`, `User-Agent`, and — notably — **`Signature`** and **`Timestamp`** for request signing. Check the live spec for the signing scheme and whether your provider requires it; see `acp-dev-patterns` for ACP's signature conventions.

`Idempotency-Key` and `Request-Id` are echoed back as response headers on creation.

## Implementation Guidance

- Handle `not_supported` as "proceed without 3DS", distinct from `not_authenticated`.
- Never log or persist raw card numbers from the create request. This request carries a PAN; treat the whole path as cardholder-data scope.
- Populate the browser `channel` block honestly and completely — it directly affects frictionless-flow rates.
- Poll or await via `getAuthenticationSession` rather than assuming a terminal state after one call; `action_required` can repeat.
- Always set `Idempotency-Key` on create and authenticate; a duplicated authentication attempt is a real failure mode when agents retry.
- Relates to `acp-delegated-payment`, `acp-checkout-rest`, and `acp-dev-patterns`.
