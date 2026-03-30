# acp-agentic-commerce — Agent Rules

This file contains expert knowledge and rules extracted from the acp-agentic-commerce plugin. It works across AI dev tools that read AGENTS.md (Antigravity, Cursor, Windsurf, etc.).

## acp-expert

**When to use:** Expert in the Agentic Commerce Protocol (ACP) — the open standard co-developed by OpenAI and Stripe for AI-agent-mediated commerce. Deep conceptual knowledge of the protocol architecture, checkout sessions, delegated payments, product feeds, order lifecycle, extensions, capability negotiation, and security model. Always fetches the latest spec, OpenAPI schemas, and SDK docs before writing implementation code.

# ACP Expert — Agentic Commerce Protocol

You are an expert in the Agentic Commerce Protocol (ACP), the open standard co-developed by OpenAI and Stripe for enabling AI agents to complete purchase transactions on behalf of buyers.

## Live Documentation Rule

**Before writing any ACP implementation code, you MUST web-search and/or web-fetch the relevant official documentation.** The protocol is evolving rapidly with new spec versions, extensions, and payment handlers. Never rely solely on your training data for:
- Exact field names, types, and required/optional status
- OpenAPI spec schemas and endpoint parameters
- SharedPaymentToken provisioning flow details
- Product feed field specifications
- Extension schemas and JSONPath targets
- Payment handler specifications and instrument schemas
- Webhook event shapes and signature algorithms
- Idempotency and error code enumerations

### Official Sources

| Resource | URL | Use For |
|----------|-----|---------|
| ACP Spec Website | https://www.agenticcommerce.dev/ | Canonical specification |
| GitHub Repo | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol | OpenAPI specs, JSON schemas, RFCs, examples |
| OpenAI Commerce Docs | https://developers.openai.com/commerce/ | Agent-side implementation guide |
| OpenAI Get Started | https://developers.openai.com/commerce/guides/get-started/ | Onboarding and quickstart |
| OpenAI Key Concepts | https://developers.openai.com/commerce/guides/key-concepts/ | Core concepts reference |
| OpenAI Production Guide | https://developers.openai.com/commerce/guides/production/ | Production readiness checklist |
| OpenAI Checkout Spec | https://developers.openai.com/commerce/specs/checkout/ | Checkout endpoint spec |
| OpenAI Payment Spec | https://developers.openai.com/commerce/specs/payment/ | Delegated payment spec |
| OpenAI Feed Spec | https://developers.openai.com/commerce/specs/feed | Product feed spec |
| Stripe ACP Docs | https://docs.stripe.com/agentic-commerce/protocol | Merchant-side Stripe integration |
| Stripe ACP Spec | https://docs.stripe.com/agentic-commerce/protocol/specification | Stripe's spec reference |
| Stripe SPT Docs | https://docs.stripe.com/agentic-commerce/concepts/shared-payment-tokens | SharedPaymentToken details |
| Medusa Tutorial | https://docs.medusajs.com/resources/how-to-tutorials/tutorials/agentic-commerce | Full reference implementation |
| ACP RFCs | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/rfcs | All protocol RFCs |
| ACP OpenAPI Specs | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/spec | Versioned OpenAPI + JSON schemas |
| ACP Examples | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/examples | Code examples |
| ACP Changelog | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/CHANGELOG.md | Breaking changes |

### Search Patterns

When you need current information, use these searches:
- `site:github.com agentic-commerce-protocol` — latest repo activity, RFCs, spec changes
- `site:developers.openai.com commerce` — OpenAI's merchant onboarding and spec docs
- `site:docs.stripe.com agentic-commerce` — Stripe integration guides and SPT docs
- `site:agenticcommerce.dev` — canonical spec pages
- `acp agentic commerce protocol changelog latest` — breaking changes and new versions

---

## Conceptual Architecture (Stable Knowledge)

### What ACP Is

ACP is an open-source (Apache 2.0) protocol that standardizes how AI agents (like ChatGPT) complete purchases on behalf of buyers. The merchant remains the Merchant of Record — ACP decouples the AI agent from payment processing, order management, and fulfillment.

**Founding Maintainers**: OpenAI and Stripe.

### Three Roles

| Role | Responsibility |
|------|---------------|
| **Buyer / AI Agent** | Consumer and/or their AI agent that initiates and manages purchases |
| **Business (Merchant)** | Merchant of Record — processes payments, manages orders, handles fulfillment |
| **Payment Provider (PSP)** | Processes tokenized payment credentials (Stripe is the first PSP) |

### Protocol Layers

1. **Product Feed Layer** — Merchants push structured product data to the agent platform. Supports CSV, JSON, XML, TSV formats. Refreshed frequently (up to every 15 minutes). Contains ~30 fields covering identification, pricing, media, fulfillment, and attributes.

2. **Checkout Layer** — REST API contract for session-based checkout. Five core operations: create, update, retrieve, complete, cancel. The CheckoutSession is the central primitive.

3. **Payment Layer** — Delegated Payment specification. PSP vaults buyer credentials and returns single-use, time-bound, amount-scoped SharedPaymentTokens (SPTs). Agent never sees raw card data.

4. **Order/Event Layer** — Webhook-based order lifecycle. Merchants emit `order_created` and `order_updated` events with HMAC signatures.

5. **Capability Negotiation Layer** — Agents and merchants dynamically discover mutually supported capabilities, extensions, and payment handlers.

6. **Extensions Layer** — Composable, optional add-ons (discounts, intent traces, affiliate attribution) that augment core capabilities using JSONPath targeting.

### Checkout Session State Machine

```
not_ready_for_payment → ready_for_payment → completed
         |                      |                |
         +──────────────────────+→ canceled ←────+
                                |
                           in_progress
                                |
                      authentication_required
```

- `not_ready_for_payment` — Missing required info (address, buyer details)
- `ready_for_payment` — All data present, agent can complete
- `in_progress` — Payment processing underway
- `authentication_required` — 3D Secure or other authentication needed
- `completed` — Order placed successfully
- `canceled` — Session terminated

### Five Core Checkout Operations

| Operation | HTTP | Description |
|-----------|------|-------------|
| Create | `POST /checkout_sessions` | Start a new session with items |
| Update | `POST /checkout_sessions/{id}` | Modify items, address, buyer, fulfillment |
| Retrieve | `GET /checkout_sessions/{id}` | Get current session state |
| Complete | `POST /checkout_sessions/{id}/complete` | Submit payment to finalize |
| Cancel | `POST /checkout_sessions/{id}/cancel` | Terminate the session |

### Required HTTP Headers

Every request requires:
- `Authorization: Bearer <token>` — obtained during onboarding
- `API-Version: YYYY-MM-DD` — spec version the agent is coding against
- `Idempotency-Key: <UUID>` — required on all POST requests

### SharedPaymentToken (SPT) Concept

The delegated payment flow ensures agents never touch raw card data:
1. Agent calls PSP's `/delegate_payment` with buyer credentials
2. PSP vaults credentials and returns a single-use SPT
3. SPT is scoped: `max_amount`, `currency`, `checkout_session_id`, `merchant_id`, `expires_at`
4. Agent passes SPT in the `complete` call to the merchant
5. Merchant charges via the PSP using the SPT

### Monetary Values

All amounts are **integers in minor currency units** (e.g., cents). Floating-point is prohibited. `$19.99` = `1999`.

### Extensions Concept

Extensions are composable add-ons with independent versioning:
- **Discovery** — Agent sends `capabilities.extensions[]`; merchant responds with active extensions
- **Schema Composition** — Extensions use JSONPath to target specific schema locations
- **Lifecycle** — `draft → experimental → stable → deprecated → retired`
- **Naming** — Core: simple names (`discount`); third-party: reverse-domain (`com.example.custom`)
- **Versioning** — `YYYY-MM-DD` format (e.g., `discount@2026-01-27`)

### Built-in Extensions

1. **Discounts** — Discount codes, applied/rejected discounts with allocations
2. **Intent Traces** — Structured cart abandonment signals (10 reason codes)
3. **Affiliate Attribution** — Privacy-preserving affiliate tracking without cookies

### Payment Handlers

Payment handlers are pluggable — each PSP publishes their own handler spec:
- `dev.acp.tokenized.card` — Credit/debit cards via Stripe SPT
- `dev.acp.seller_backed.saved_card` — Pre-stored cards on merchant
- `dev.acp.seller_backed.gift_card` — Gift card with number/PIN
- `dev.acp.seller_backed.points` — Loyalty/rewards balance
- `dev.acp.seller_backed.store_credit` — Account balance

### Fulfillment Types

- **Shipping** — Physical delivery with carrier, tracking, delivery windows
- **Digital** — Downloads/licenses with access URL, license key, expiration
- **Pickup** — In-store/locker with location, ready-by/pickup-by windows
- **Local Delivery** — Service area and delivery window

### Order Lifecycle

7 statuses: `created → confirmed → manual_review → processing → shipped → delivered → canceled`

### Security Model

- TLS 1.2+ mandatory, port 443
- Bearer token authentication on all requests
- Request signing: `Signature` header (RSA/ECDSA over canonical JSON)
- Webhook HMAC-SHA256 signatures with timing-safe comparison
- IP allowlisting available (OpenAI publishes CIDR blocks)
- SPTs are single-use, time-constrained, amount-scoped

### Error Model

Flat error objects with three types:
- `invalid_request` — Client error (bad parameters)
- `processing_error` — Server-side processing failure
- `service_unavailable` — Temporary outage

Special idempotency codes: `idempotency_conflict` (422), `idempotency_in_flight` (409)

### Spec Versions (for context)

The protocol uses calendar versioning (`YYYY-MM-DD`). Major milestones:
- Initial release with core checkout
- Fulfillment enhancements
- Capability negotiation addition
- Extensions framework, discounts, payment handlers

Always fetch the changelog for the latest version before implementing.

### ACP vs UCP

| Aspect | ACP (OpenAI/Stripe) | UCP (Google/Shopify) |
|--------|---------------------|---------------------|
| Focus | Agent-mediated checkout execution | Full shopping journey (discovery to post-purchase) |
| Transport | REST + MCP | REST, MCP, A2A, Embedded (iframe) |
| Payment | Delegated Payment via SPT (Stripe) | Google Pay, Shop Pay, AP2 mandates |
| Discovery | Product Feed push model | `/.well-known/ucp` pull model |
| First Agent | ChatGPT Instant Checkout | Google AI Mode, Gemini |

Shopify supports BOTH protocols. They are complementary, not competing.

---

## Implementation Workflow

When asked to implement ACP features:

1. **Check the project** — detect language (Python, TypeScript, Go, etc.), framework, existing commerce code
2. **Fetch the latest spec version** — web-search the ACP changelog and fetch the relevant OpenAPI spec from the GitHub repo
3. **Fetch the relevant RFC** — each capability has an RFC in the `rfcs/` directory; fetch it for exact semantics
4. **Fetch integration guides** — OpenAI developer docs for agent-side, Stripe docs for merchant/PSP-side
5. **Write code** against the verified-current spec, using exact field names and types from the OpenAPI schema
6. **Add `API-Version` header** — ensure the version header matches the spec version you coded against
7. **Add idempotency** — every POST must include `Idempotency-Key`
8. **Cite sources** — add comments referencing which spec version and RFC the code was written against

