---
name: mpp-spt-lifecycle
description: Implement Shared Payment Token (SPT) lifecycle management for MPP — creation, usage, deactivation, webhook events, and reconciliation. Use when building the fiat/card payment flow within MPP using Stripe SPTs.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# MPP Shared Payment Token (SPT) Lifecycle

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.stripe.com/agentic-commerce/concepts/shared-payment-tokens` for the canonical SPT documentation
2. Web-search `site:docs.stripe.com shared_payment granted_token API` for SPT API endpoints
3. Web-search `stripe shared payment token webhook events` for SPT event schemas
4. Fetch `https://docs.stripe.com/payments/machine/mpp` for SPT usage within MPP context

## Conceptual Architecture

### What SPTs Are

Shared Payment Tokens are one-time payment tokens scoped to a specific merchant and exact amount. They are the mechanism by which card/fiat payments work within the MPP protocol. The agent never handles raw card data — SPTs abstract away PCI-sensitive information.

### SPT Lifecycle

```
1. Agent → Stripe:    Create SPT (scoped to merchant + amount + expiry)
2. Stripe → Agent:    Returns spt_... token
3. Agent → Server:    Sends SPT as payment credential in 402 flow
4. Server → Stripe:   Creates PaymentIntent with SPT
5. Stripe → Server:   Payment confirmed
6. Stripe → Agent:    Webhook: shared_payment.issued_token.used
7. Stripe → Server:   Webhook: shared_payment.granted_token.used
```

### SPT Creation (Agent-Side)

```
POST /v1/test_helpers/shared_payment/granted_tokens

Parameters:
  payment_method: pm_card_visa
  usage_limits[currency]: usd
  usage_limits[max_amount]: 1000           # $10.00 in cents
  usage_limits[expires_at]: <unix_ts>      # Expiration timestamp
  seller_details[network_id]: <seller_id>  # Merchant's network ID
  seller_details[external_id]: <ext_id>    # Optional external reference
```

### SPT Consumption (Server-Side)

```
POST /v1/payment_intents

Parameters:
  amount: 500                              # $5.00 in cents
  currency: usd
  shared_payment_granted_token: spt_...
  confirm: true
```

When confirmed, Stripe clones the original PaymentMethod and processes the charge.

### SPT Retrieval

```
GET /v1/shared_payment/granted_tokens/{id}
```

Returns limited payment method details (card brand, last four digits) and usage restrictions.

### SPT Webhook Events

| Event | Recipient | Trigger | Key Fields |
|-------|-----------|---------|------------|
| `shared_payment.granted_token.used` | Seller (Server) | SPT successfully consumed | token_id, amount, currency |
| `shared_payment.granted_token.deactivated` | Seller (Server) | SPT revoked or expired | token_id, reason |
| `shared_payment.issued_token.used` | Agent | Seller consumed the SPT | token_id, amount |
| `shared_payment.issued_token.deactivated` | Agent | SPT no longer valid | token_id, reason |

### Webhook Listener (Server-Side)

```typescript
app.post('/webhooks/stripe', async (c) => {
  const sig = c.req.header('stripe-signature');
  const event = stripe.webhooks.constructEvent(
    await c.req.text(),
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  );

  switch (event.type) {
    case 'shared_payment.granted_token.used':
      // SPT was successfully consumed — update records
      break;
    case 'shared_payment.granted_token.deactivated':
      // SPT expired or was revoked — clean up
      break;
  }
});
```

### SPT Constraints

| Constraint | Purpose |
|-----------|---------|
| `max_amount` | Transaction cannot exceed this (minor units) |
| `currency` | Token only works in specified currency |
| `expires_at` | Token invalid after this timestamp |
| `network_id` | Only specified merchant can use it |
| `external_id` | Additional merchant scoping |

### Deactivation Reasons

SPTs can be deactivated for:
- **Expiration** — `expires_at` passed
- **Usage** — Successfully consumed (single-use)
- **Revocation** — Agent or platform revoked the token
- **Fraud** — Flagged by Stripe's fraud detection

### Reconciliation

- Match SPT creation events to consumption events
- Track SPT lifecycle (created → used → settled) for accounting
- Monitor deactivation rates (high expiration rate may mean TTL is too short)
- Cross-reference SPT usage with PaymentIntent events

### Best Practices

- Set `max_amount` to the exact payment amount — never higher
- Set short expiration times (minutes, not hours)
- Implement idempotent webhook handlers (same event may be delivered multiple times)
- Verify webhook signatures using `stripe.webhooks.constructEvent()`
- Log SPT lifecycle events for audit trail (token IDs only, not sensitive data)
- Handle race conditions between SPT creation and consumption
- Monitor SPT deactivation webhook for cleanup

Fetch the latest Stripe SPT API documentation for exact endpoint paths, webhook event schemas, and error codes before implementing.
