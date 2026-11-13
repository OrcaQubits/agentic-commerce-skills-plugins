---
name: shopify-payments
description: >
  Integrate Shopify payments — Shopify Payments (Stripe-powered), Payment Apps
  API, payment session flow, Billing API for app charges, refund processing, and
  PCI compliance. Use when working with Shopify payment processing.
---

# Shopify Payments Integration

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev payments apps api` for Payment Apps API
2. Web-search `site:shopify.dev billing api app charges` for app billing
3. Web-search `site:shopify.dev shopify payments` for Shopify Payments overview
4. Web-search `site:shopify.dev payment session resolve reject` for payment session flow
5. Web-search `site:shopify.dev app subscription create usage record` for billing mutations

## Shopify Payments

Shopify's built-in payment processor (powered by Stripe):
- No third-party gateway needed
- Supports credit/debit cards, Shop Pay, Apple Pay, Google Pay
- Lower transaction fees than third-party gateways
- PCI DSS Level 1 compliant (Shopify handles compliance)

### Payment Flow

```
Customer → Checkout → Payment Method Selection → Authorization → Capture
```

- Authorization happens at checkout
- Capture happens when order is fulfilled (or immediately, based on settings)
- Auto-capture can be enabled for immediate charge

### Supported Payment Methods

| Method | Details |
|--------|---------|
| Credit/Debit cards | Visa, Mastercard, Amex, Discover |
| Shop Pay | Shopify's accelerated checkout |
| Apple Pay | On supported devices/browsers |
| Google Pay | On supported devices/browsers |
| Local methods | Varies by country (iDEAL, Bancontact, etc.) |

> **Fetch live docs** for supported payment methods by country — availability varies by region and changes over time.

## Payment Apps API

For building custom payment gateways as Shopify apps:

### Payment Session Flow

```
1. Customer selects your payment method at checkout
2. Shopify creates payment session → calls your app's payment endpoint
3. Your app processes payment with your gateway
4. Return: RESOLVE (success) or REJECT (failure)
5. Optional: REDIRECT for additional auth (3D Secure, bank redirect)
6. Optional: CONFIRM for pending/async payments
```

### Key Mutations

| Operation | Mutation | When |
|-----------|----------|------|
| Approve payment | `paymentSessionResolve` | Payment succeeded |
| Decline payment | `paymentSessionReject` | Payment failed |
| Redirect customer | `paymentSessionRedirect` | 3D Secure, bank auth |
| Confirm payment | `paymentSessionConfirm` | Async/pending payment settled |
| Approve refund | `refundSessionResolve` | Refund succeeded |
| Decline refund | `refundSessionReject` | Refund failed |
| Approve capture | `captureSessionResolve` | Manual capture succeeded |
| Decline capture | `captureSessionReject` | Manual capture failed |
| Approve void | `voidSessionResolve` | Void succeeded |
| Decline void | `voidSessionReject` | Void failed |

> **Fetch live docs** for each session mutation's input fields and the `PaymentSessionActionsRedact` webhook — the API surface for payment apps is complex and version-sensitive.

### Payment App Requirements

- Must handle: payments, refunds, captures, voids
- Must implement: `payments_app_configure` GraphQL mutations
- Must respond within timeout (usually 5 seconds for sync, longer for async)
- Testing: use Shopify's test mode and development store

> **Fetch live docs**: Web-search `site:shopify.dev build payment extension` for current extension configuration, required endpoints, and testing procedures.

## Billing API

For charging merchants for your app:

### Charge Types

| Type | Mutation | Use Case |
|------|----------|----------|
| Recurring | `appSubscriptionCreate` | Monthly/annual subscription |
| One-time | `appPurchaseOneTimeCreate` | One-time feature purchase |
| Usage-based | `appUsageRecordCreate` | Metered billing (per-action, per-order) |

### Subscription Flow

1. Create subscription with `appSubscriptionCreate` → returns `confirmationUrl`
2. Redirect merchant to `confirmationUrl`
3. Merchant approves charge on Shopify-hosted page
4. Shopify handles billing, invoicing, and payouts to your Partner account

### Usage-Based Billing Pattern

1. Create a subscription plan with a usage pricing model via `appSubscriptionCreate`
2. As the merchant uses features, record usage with `appUsageRecordCreate`
3. Shopify bills the merchant at the end of the billing cycle based on recorded usage
4. Capped amounts prevent unexpected charges

> **Fetch live docs** for `AppSubscriptionInput` and `AppUsageRecordInput` fields — pricing models, trial days, currency options, and line item structures change across API versions.

## Refund Processing

- Refunds issued via `refundCreate` mutation (on orders)
- Payment apps handle refund sessions via `refundSessionResolve`/`refundSessionReject`
- Can be full or partial
- Refunded to original payment method
- Refund notification sent to customer automatically

## PCI Compliance

Shopify handles PCI compliance for:
- Shopify Payments (fully managed)
- Checkout-hosted payment forms
- Payment apps that use Shopify's session-based flow

Your app must:
- Never store raw card numbers, CVV, or sensitive cardholder data
- Use Shopify's payment session API (not direct card collection)
- Follow Shopify's security requirements for payment apps
- Implement HTTPS for all endpoints

## Best Practices

- Recommend Shopify Payments as primary gateway (lowest fees, best integration)
- Use the Payment Apps API for custom gateways — never collect cards directly
- Implement proper error handling for payment sessions (timeouts, network errors)
- Use the Billing API for app monetization — never handle payments outside Shopify
- Test payment flows in development stores (test mode)
- Handle refunds gracefully — always confirm with `refundSessionResolve`
- Implement idempotency for payment operations (use idempotency keys)
- Log payment events for debugging but never log sensitive payment data

Fetch the Shopify Payment Apps API and Billing API documentation for exact session flow, mutation inputs, testing procedures, and webhook requirements before implementing.
