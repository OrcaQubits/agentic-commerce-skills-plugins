---
name: medusa-payments
description: Implement Medusa v2 payment processing — payment module, provider abstraction, payment sessions, authorization/capture/refund lifecycle, and Stripe/PayPal integration. Use when adding payment providers.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Payment Processing

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com payment module` for payment data model and service methods
2. Web-search `site:docs.medusajs.com payment provider` for the provider abstraction layer
3. Web-search `site:docs.medusajs.com stripe payment` for Stripe integration setup
4. Fetch `https://docs.medusajs.com/resources/references/payment` and review the `IPaymentModuleService` interface
5. Web-search `medusajs v2 AbstractPaymentProvider 2026` for latest provider interface

## Payment Module Architecture

### Entity Relationships

| Entity | Contains | Key Fields |
|--------|----------|------------|
| **PaymentCollection** | Sessions, Payments | status, amount, currency_code |
| **PaymentSession** | Provider data | provider_id, status, amount, data (JSON) |
| **Payment** | Captures, Refunds | provider_id, amount, captured_at |

### Module Links

```
Cart Module ──link──> Payment Module (payment collection)
Order Module ──link──> Payment Module (payment collection)
Region Module ──link──> Payment Module (available providers)
```

> **Fetch live docs** for exact link definitions and how payment collections bridge carts and orders.

## Payment Lifecycle

### PaymentSession Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Session initialized, awaiting customer action |
| `requires_more` | Additional steps needed (e.g., 3DS) |
| `authorized` | Payment authorized, funds reserved |
| `canceled` | Payment voided/canceled |
| `error` | Payment failed |

### Payment Statuses

After authorization, a **Payment** entity is created from the session:

| Status | Meaning |
|--------|---------|
| `captured` | Funds captured to merchant |
| `partially_refunded` | Partial refund issued |
| `refunded` | Full refund issued |

## Payment Provider Abstraction

All payment providers extend `AbstractPaymentProvider`:

```ts
// Skeleton: custom payment provider
// Fetch live docs for AbstractPaymentProvider interface
class MyPaymentProvider extends AbstractPaymentProvider {
  // Implement: initiatePayment, authorizePayment,
  // capturePayment, refundPayment, cancelPayment
  // Fetch live docs for exact method signatures
}
```

### Key Provider Methods

| Method | Purpose |
|--------|---------|
| `initiatePayment` | Create payment session with provider |
| `authorizePayment` | Authorize payment (reserve funds) |
| `capturePayment` | Capture authorized payment |
| `refundPayment` | Refund captured payment |
| `cancelPayment` | Cancel/void payment |
| `deletePayment` | Clean up provider-side session |
| `getPaymentStatus` | Query current status from provider |
| `updatePayment` | Update an existing payment session |
| `retrievePayment` | Retrieve payment data from provider |
| `getWebhookActionAndData` | Parse incoming webhook events |

> **Fetch live docs** for the full method list — the provider interface has additional methods beyond those listed above (e.g., `createAccountHolder`, `listPaymentMethods`, `savePaymentMethod`). Always verify the current `AbstractPaymentProvider` interface.

## Stripe Integration

| Configuration | Description |
|---------------|-------------|
| `apiKey` | Stripe secret key |
| `webhookSecret` | Stripe webhook signing secret |
| `capture` | Auto-capture or manual (`true`/`false`) |

### Stripe Webhook Events

| Event | Medusa Action |
|-------|---------------|
| `payment_intent.succeeded` | Mark session authorized/captured |
| `payment_intent.payment_failed` | Mark session errored |
| `charge.refunded` | Mark refund completed |

> **Fetch live docs** for Stripe provider configuration options and webhook endpoint setup.

## PayPal Integration

| Configuration | Description |
|---------------|-------------|
| `clientId` | PayPal client ID |
| `clientSecret` | PayPal client secret |
| `sandbox` | Use sandbox environment (`true`/`false`) |

> **Fetch live docs** for PayPal provider options, redirect handling, and webhook configuration.

## Payment Workflows

| Workflow | Purpose |
|----------|---------|
| `createPaymentCollectionForCartWorkflow` | Create collection linked to cart |
| `initializePaymentSessionWorkflow` | Start session with specific provider |
| `authorizePaymentSessionWorkflow` | Authorize a pending session |
| `capturePaymentWorkflow` | Capture an authorized payment |
| `refundPaymentWorkflow` | Refund a captured payment |
| `cancelPaymentWorkflow` | Cancel/void a payment |

### Key Service Methods

| Operation | Method |
|-----------|--------|
| Create collection | `paymentModuleService.createPaymentCollections()` |
| Create session | `paymentModuleService.createPaymentSession()` |
| Authorize session | `paymentModuleService.authorizePaymentSession()` |
| Capture payment | `paymentModuleService.capturePayment()` |
| Refund payment | `paymentModuleService.refundPayment()` |

> **Fetch live docs** for workflow input shapes and provider-specific data requirements.

## Admin API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/admin/payments` | GET | List payments |
| `/admin/payments/:id` | GET | Retrieve payment |
| `/admin/payments/:id/capture` | POST | Capture payment |
| `/admin/payments/:id/refund` | POST | Refund payment |

## Best Practices

### Provider Implementation
- Always extend `AbstractPaymentProvider` — do not implement from scratch
- Store provider-specific data in the session `data` field (not in metadata)
- Handle `requires_more` status for providers with multi-step flows (3DS, redirect)
- Implement idempotent operations — captures and refunds may be retried

### Webhook Handling
- Validate webhook signatures before processing events
- Use idempotency keys to prevent duplicate payment processing
- Log all webhook events for audit trails and debugging
- Handle out-of-order webhook delivery gracefully

### Security
- Never store raw API keys in code — use environment variables
- Never expose payment session secrets to the client
- Use HTTPS-only webhook endpoints
- Implement amount validation — verify captured amount matches the order total

### Testing
- Use provider sandbox/test modes during development
- Test the full lifecycle: initiate -> authorize -> capture -> refund
- Test error scenarios: declined cards, insufficient funds, network timeouts

Fetch the Medusa v2 payment module documentation and provider interface references for exact method signatures, webhook configuration, and provider registration patterns before implementing.
