---
name: ap2-checkout-mandate
description: Implement the AP2 Checkout Mandate — the credential authorizing completion of a checkout, in its open (constrained) and closed (merchant-verified) forms, with merchant-signed checkout payloads, checkout hashes, and user confirmation on a trusted surface. Formerly called the Cart Mandate. Use when building cart/checkout authorization, signing, and verification.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Checkout Mandate

> **Renamed.** This credential was called the **Cart Mandate** in earlier AP2 releases. If you are reading older samples, blog posts, or tutorials that say "Cart Mandate", they are describing this object — but the *structure* changed along with the name, so do not port field names across. Fetch the live schema.

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/ap2/checkout_mandate/` for the current Checkout Mandate schema — open and closed forms.
2. Fetch `https://ap2-protocol.org/ap2/agent_authorization/` for the open/closed mandate model this sits inside. Read that first if you have not; the mandate makes little sense without it.
3. Fetch `https://ap2-protocol.org/glossary/` to catch any further renames.
4. Web-search `site:github.com google-agentic-commerce AP2 code sdk mandate checkout` for the current type definitions under `code/`.

## Conceptual Architecture

### What it authorizes

The Checkout Mandate authorizes **completing a checkout transaction**. It is the credential that says "this user agreed to buy this."

It exists in two forms, matching the open/closed model from the Agent Authorization Framework:

| Form | Bound to a transaction | Used for |
|------|------------------------|----------|
| **Open** | No — carries constraints | Human-not-present: the user authorizes a *shape* of purchase in advance |
| **Closed** | Yes — merchant-verified | Human-present, or the resolution of an open mandate |

### Open mandate constraints

An open Checkout Mandate bounds what a valid closed mandate may contain:

- **Allowed merchants** — which merchants may use the mandate
- **Line items** — acceptable products and quantities

These constraints are the security boundary for autonomous purchasing. The verifier must enforce them; do not rely on the agent to police itself.

### Closed mandate shape

The closed form carries the merchant's commitment:

- **`vct`** — the credential type identifier
- **`checkout_jwt`** — base64url-encoded, serialized, **merchant-signed** JWT of the checkout payload
- **`checkout_hash`** — cryptographic hash identifying the specific checkout
- **`iat` / `exp`** — issued-at and expiry

Read the live schema for the exact `vct` value and the full field list; both have changed between releases.

### Who creates and signs what

- The **Shopping Agent** creates the mandate content.
- The **Trusted Surface** displays that content to the user. This is not the agent conversation — it is a surface the user can trust to show them what they are actually agreeing to.
- For closed mandates, the **Merchant** creates a signed Checkout object that is embedded in the mandate content.

So there are two distinct commitments in play, and conflating them is the classic mistake:

1. **Merchant signature** — an *entity-level* guarantee that the products are available, the prices are accurate, and the merchant will fulfill at those terms. Signed by the merchant organization, **not** by its AI agent.
2. **User approval** — captured on the trusted surface, providing non-repudiation for dispute resolution.

### Signing and canonicalization

The merchant's signature covers a canonicalized form of the checkout payload so that serialization differences cannot change what was signed. Verify against the live spec:

- the current canonicalization scheme,
- the permitted signing algorithms,
- the required JWT header claims (key identification matters — a verifier needs to know which key signed),
- and how `checkout_hash` is computed and what it must match.

Do not implement any of the above from memory or from an older sample. Signature verification that is "close enough" is a security defect.

### Flow (human-present)

1. Shopping Agent assembles the intended purchase.
2. Merchant produces and signs the Checkout object.
3. Checkout Mandate content is presented to the user **on the trusted surface**.
4. User reviews and confirms.
5. Closed mandate is bound to the transaction and presented to the verifier.
6. Verifier validates and returns a signed receipt.

For the human-not-present path, the user signs an **open** mandate at step 3 and the agent later produces the closed mandate — see `ap2-human-not-present-flow`.

## Best Practices

- Present all line items with individual prices, not just a total. The user is signing what they were shown.
- Validate the full signature chain — merchant signature, user approval, and key binding — before processing payment. A closed mandate alone proves nothing.
- Enforce open-mandate constraints at the verifier, independently of the agent.
- Store the complete signed chain for dispute resolution (see `ap2-dispute-accountability`).
- Handle rejection as a first-class path; never force or retry a signature the user declined.
- Set `exp` deliberately — an unexpiring checkout authorization is a standing liability.

## Related

`ap2-agent-authorization` (the framework), `ap2-payment-mandate` (authorizes the payment itself), `ap2-vdc-framework` (credential formats), `ap2-human-present-flow`, `ap2-human-not-present-flow`.
