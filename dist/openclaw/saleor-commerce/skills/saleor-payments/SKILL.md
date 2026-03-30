---
name: saleor-payments
description: >
  Implement Saleor payment processing — transaction-based payment flow, payment
  Apps, sync webhook events, Stripe/Adyen patterns, and refunds. Use when
  building payment integrations.
---

# Saleor Payment Processing

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io transaction payment flow` for the transaction-based payment model
2. Web-search `site:docs.saleor.io payment app sync webhooks` for payment App implementation patterns
3. Web-search `site:docs.saleor.io transaction events CHARGE_REQUESTED` for transaction event types
4. Fetch `https://docs.saleor.io/docs/developer/payments` and review the full payment lifecycle
5. Web-search `site:docs.saleor.io refund transactionRequestAction` for refund processing flow
6. Fetch `https://docs.saleor.io/docs/developer/app-store/apps/stripe` and review Stripe App integration patterns

## Transaction Payment Flow

Saleor uses a transaction-based payment model (replacing the legacy `Payment` model):

| Step | Component | Description |
|------|-----------|-------------|
| 1. List gateways | `checkout.availablePaymentGateways` | Query available payment Apps for the checkout |
| 2. Initialize session | `transactionInitialize` | Send payment request to the payment App |
| 3. Process (if needed) | `transactionProcess` | Handle additional steps (3DS, redirect) |
| 4. Transaction events | Automatic | Payment App reports events via webhooks |
| 5. Complete checkout | `checkoutComplete` | Finalize order after successful payment |

> The transaction flow is designed for asynchronous payment processing. The payment App controls the actual charge timing and reports results back via transaction events.

## Transaction Events

Transaction events track the lifecycle of a payment:

### Request Events (Saleor to Payment App)

| Event Type | Description |
|------------|-------------|
| `AUTHORIZATION_REQUEST` | Request to authorize (hold) funds |
| `CHARGE_REQUEST` | Request to capture payment |
| `REFUND_REQUEST` | Request to refund payment |
| `CANCEL_REQUEST` | Request to void/cancel authorization |

### Success Events (Payment App to Saleor)

| Event Type | Description |
|------------|-------------|
| `AUTHORIZATION_SUCCESS` | Funds successfully authorized |
| `CHARGE_SUCCESS` | Payment successfully captured |
| `REFUND_SUCCESS` | Refund successfully processed |
| `CANCEL_SUCCESS` | Authorization successfully cancelled |

### Failure Events (Payment App to Saleor)

| Event Type | Description |
|------------|-------------|
| `AUTHORIZATION_FAILURE` | Authorization failed |
| `CHARGE_FAILURE` | Charge failed |
| `REFUND_FAILURE` | Refund failed |
| `CANCEL_FAILURE` | Cancellation failed |

### Action Required Events

| Event Type | Description |
|------------|-------------|
| `AUTHORIZATION_ACTION_REQUIRED` | Additional customer action needed (e.g., 3DS) |
| `CHARGE_ACTION_REQUIRED` | Additional step required to complete charge |

> **Fetch live docs** for the complete `TransactionEventTypeEnum` -- additional event types may exist for pending states and information events.

## Payment App Pattern

Payment processing in Saleor is handled by Apps that implement sync webhooks:

| Component | Description |
|-----------|-------------|
| Payment App | A Saleor App that handles payment gateway communication |
| Sync webhooks | Synchronous webhook calls from Saleor to the App |
| Transaction events | App reports payment status back to Saleor |
| Gateway config | Per-channel payment gateway configuration |

### Key Sync Webhook Events

| Webhook Event | When Triggered | Expected Response |
|---------------|----------------|-------------------|
| `PAYMENT_GATEWAY_INITIALIZE_SESSION` | When storefront queries payment gateways | Gateway configuration and client-side data |
| `TRANSACTION_INITIALIZE_SESSION` | On `transactionInitialize` mutation | Payment session data (e.g., client secret) |
| `TRANSACTION_PROCESS_SESSION` | On `transactionProcess` mutation | Updated payment status and next actions |
| `TRANSACTION_CHARGE_REQUESTED` | On `transactionRequestAction` with `CHARGE` | Charge result event |
| `TRANSACTION_REFUND_REQUESTED` | On `transactionRequestAction` with `REFUND` | Refund result event |
| `TRANSACTION_CANCELATION_REQUESTED` | On `transactionRequestAction` with `CANCEL` | Cancellation result event |

### Payment App Implementation Pattern

A payment App must:

| Step | Description |
|------|-------------|
| 1. Register webhooks | Subscribe to the sync webhook events above |
| 2. Handle initialize | Create payment session with the gateway (e.g., Stripe PaymentIntent) |
| 3. Return session data | Send client-side data back (e.g., `clientSecret` for Stripe Elements) |
| 4. Handle process | Process additional steps and return updated status |
| 5. Report events | Use `transactionEventReport` to report async payment updates |
| 6. Handle actions | Process charge, refund, and cancel requests |

## Transaction Actions

Staff and Apps can request actions on existing transactions:

| Action | Mutation | Description |
|--------|----------|-------------|
| Charge | `transactionRequestAction` with `CHARGE` | Capture authorized funds |
| Refund | `transactionRequestAction` with `REFUND` | Refund charged amount |
| Cancel | `transactionRequestAction` with `CANCEL` | Void authorization |

### Manual Transaction Creation

For manual or offline payments:

| Mutation | Purpose |
|----------|---------|
| `transactionCreate` | Create a transaction record manually |
| `transactionUpdate` | Update transaction details |
| `transactionEventReport` | Report payment events from external systems |

## Refund Flow

Saleor implements a two-step refund process:

| Step | Mutation | Description |
|------|----------|-------------|
| 1. Grant refund | `orderGrantRefundCreate` | Merchant decides refund amount or lines |
| 2. Process refund | `transactionRequestAction` with `REFUND` | Payment App processes the actual refund |

### Grant Refund Options

| Option | Description |
|--------|-------------|
| Amount-based | Specify a flat refund amount |
| Line-based | Specify order lines and quantities to refund |
| Shipping refund | Include shipping cost in the refund |
| Reason | Optional text reason for the refund |

> The grant-then-process pattern allows merchants to review and approve refunds before the payment is actually reversed.

## Legacy Payments (Deprecated)

| Legacy Mutation | Replacement |
|-----------------|-------------|
| `checkoutPaymentCreate` | `transactionInitialize` |
| `checkoutComplete` (with payment data) | `transactionProcess` + `checkoutComplete` |
| `orderCapture` | `transactionRequestAction` with `CHARGE` |
| `orderRefund` | `orderGrantRefundCreate` + `transactionRequestAction` |
| `orderVoid` | `transactionRequestAction` with `CANCEL` |

> Legacy payment mutations are deprecated. All new integrations should use the transaction-based flow. Existing integrations should migrate to transactions.

## Stripe Integration Pattern

The official Saleor Stripe App follows this flow:

| Step | Client | Server |
|------|--------|--------|
| 1. Initialize | Call `transactionInitialize` | App creates Stripe PaymentIntent |
| 2. Client secret | Receive `data.clientSecret` | -- |
| 3. Confirm | Use Stripe.js to confirm payment | -- |
| 4. Process | Call `transactionProcess` if needed | App checks PaymentIntent status |
| 5. Webhook | -- | Stripe webhook updates transaction |

## Adyen Integration Pattern

The official Saleor Adyen App follows a similar pattern:

| Step | Client | Server |
|------|--------|--------|
| 1. Initialize | Call `transactionInitialize` | App creates Adyen session |
| 2. Session data | Receive Adyen Drop-in config | -- |
| 3. Submit | Use Adyen Web Components | -- |
| 4. Process | Call `transactionProcess` with result | App verifies with Adyen |
| 5. Webhook | -- | Adyen webhook updates transaction |

## Best Practices

- Use the transaction-based flow for all new payment integrations (not legacy payments)
- Implement idempotency keys on `transactionInitialize` to prevent duplicate charges
- Handle `ACTION_REQUIRED` events for 3DS and redirect-based payment methods
- Use `transactionEventReport` for webhook-based async payment updates from gateways
- Separate grant refund (business decision) from payment refund (gateway action)
- Test payment flows with gateway sandbox/test modes before going live
- Subscribe to both success and failure events for comprehensive error handling
- Store gateway-specific data in transaction `metadata` for debugging
- Validate `checkout.totalPrice` matches the amount passed to `transactionInitialize`
- Use channel-specific payment gateway configuration for multi-channel setups

Fetch the Saleor payment and transaction documentation for exact webhook payloads, event types, and App implementation patterns before implementing.
