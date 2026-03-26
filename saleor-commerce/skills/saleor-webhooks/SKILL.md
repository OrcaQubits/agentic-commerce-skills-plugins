---
name: saleor-webhooks
description: Configure Saleor webhooks — async and sync events, subscription payloads, JWS/HMAC signature verification, retry policy, and event types. Use when building webhook-driven integrations.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Webhooks

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/extending/webhooks/overview` for webhook overview
2. Web-search `site:docs.saleor.io async sync webhook events list` for event type reference
3. Web-search `site:docs.saleor.io webhook subscription payload` for subscription query syntax
4. Web-search `site:docs.saleor.io webhook payload signature JWS verification` for signature verification
5. Web-search `site:docs.saleor.io webhook retry policy` for retry behavior

## Async vs Sync Webhooks

| Aspect | Async Webhooks | Sync Webhooks |
|--------|---------------|---------------|
| Timing | Fired after the action completes | Fired during the action, blocks response |
| Response | Saleor ignores the response body | Saleor uses the response to alter behavior |
| Timeout | Longer (configurable) | Short (seconds) -- must respond quickly |
| Retry | Retried on failure | Not retried -- failure may abort the operation |
| Use Case | Notifications, syncing, analytics | Tax calculation, payment gateways, shipping rates |

## Key Async Event Types

| Event | Trigger |
|-------|---------|
| `ORDER_CREATED` | New order is placed |
| `ORDER_UPDATED` | Order fields are modified |
| `ORDER_CONFIRMED` | Order is confirmed |
| `ORDER_FULFILLED` | All items in the order are fulfilled |
| `ORDER_CANCELLED` | Order is cancelled |
| `ORDER_FULLY_PAID` | Order payment is complete |
| `PRODUCT_CREATED` | New product is created |
| `PRODUCT_UPDATED` | Product fields are modified |
| `PRODUCT_DELETED` | Product is deleted |
| `CUSTOMER_CREATED` | New customer account is created |
| `CUSTOMER_UPDATED` | Customer data is modified |
| `CHECKOUT_CREATED` | New checkout session starts |
| `CHECKOUT_UPDATED` | Checkout data changes |
| `FULFILLMENT_CREATED` | Fulfillment record is created |
| `INVOICE_SENT` | Invoice email is dispatched |

## Key Sync Event Types

| Event | Expected Response |
|-------|------------------|
| `PAYMENT_GATEWAY_INITIALIZE_SESSION` | Payment session configuration |
| `TRANSACTION_INITIALIZE_SESSION` | Transaction processing data |
| `TRANSACTION_PROCESS_SESSION` | Transaction result |
| `TRANSACTION_CHARGE_REQUESTED` | Charge confirmation |
| `TRANSACTION_REFUND_REQUESTED` | Refund confirmation |
| `SHIPPING_LIST_METHODS_FOR_CHECKOUT` | Available shipping methods and rates |
| `CHECKOUT_CALCULATE_TAXES` | Tax amounts for checkout lines |
| `ORDER_CALCULATE_TAXES` | Tax amounts for order lines |
| `CHECKOUT_FILTER_SHIPPING_METHODS` | Filter available shipping options |
| `ORDER_FILTER_SHIPPING_METHODS` | Filter shipping for existing orders |

Sync webhooks must return a response in the expected format -- fetch live docs for each event's response schema.

## Subscription Payloads

Saleor uses GraphQL subscription queries to define webhook payload shapes:

```graphql
subscription OrderCreated {
  event {
    ... on OrderCreated {
      order { id number total { gross { amount currency } } user { email } }
    }
  }
}
```

This subscription query is attached to the webhook configuration and controls exactly which fields appear in the delivered payload.

### Subscription Payload Benefits

| Benefit | Detail |
|---------|--------|
| Precise data | Request only the fields you need |
| Reduced payload size | No unnecessary nested objects |
| Type safety | Payload matches the subscription query shape |
| Versioning | Update the query when you need new fields |

## Webhook Registration

### Via App Manifest

Webhooks are declared in the App manifest and registered automatically during installation:

| Manifest Field | Purpose |
|---------------|---------|
| `webhooks[].name` | Human-readable webhook name |
| `webhooks[].asyncEvents` | List of async event types |
| `webhooks[].syncEvents` | List of sync event types |
| `webhooks[].query` | GraphQL subscription query for payload |
| `webhooks[].targetUrl` | URL to receive the webhook POST |
| `webhooks[].isActive` | Enable or disable the webhook |

### Via GraphQL API

| Mutation | Purpose |
|----------|---------|
| `webhookCreate` | Register a new webhook |
| `webhookUpdate` | Modify an existing webhook |
| `webhookDelete` | Remove a webhook |

Staff users or Apps with `MANAGE_APPS` permission can manage webhooks via the API.

## Payload Signature Verification

Saleor signs every webhook payload to ensure authenticity. Since Saleor 3.5+, the default method is **JWS (JSON Web Signature)** with RS256. Legacy HMAC-SHA256 is deprecated.

| Header | Value |
|--------|-------|
| `Saleor-Signature` | JWS signature (default) or HMAC-SHA256 hex digest (deprecated) |
| `Saleor-Event` | The event type (e.g., `order_created`) |
| `Saleor-Domain` | The Saleor instance domain |
| `Saleor-Api-Url` | Full URL of the Saleor GraphQL endpoint |

### Signature Methods

| Method | Status | How It Works |
|--------|--------|-------------|
| **JWS (RS256)** | Default (3.5+) | Payload-detached JWS; verify with public key from `/.well-known/jwks.json` |
| **HMAC-SHA256** | Deprecated | Only used when a webhook secret key is explicitly set; will be removed in 4.0 |

### JWS Verification Steps

| Step | Action |
|------|--------|
| 1 | Read the `Saleor-Signature` header (JWS compact serialization) |
| 2 | Fetch the public key from `<saleor-domain>/.well-known/jwks.json` |
| 3 | Verify the JWS signature using the RS256 public key |
| 4 | Reject the request if verification fails |

The `saleor-app-sdk` provides built-in middleware for automatic signature verification. Always verify signatures before processing any webhook payload.

## Retry Policy

| Aspect | Detail |
|--------|--------|
| Async retries | Saleor retries failed async webhooks with exponential backoff |
| Max attempts | Configurable -- fetch live docs for default |
| Failure criteria | Non-2xx HTTP response or connection timeout |
| Sync retries | Sync webhooks are not retried |
| Circuit breaker | Saleor may disable a webhook after repeated failures |

## Webhook Handler Pattern

| Step | Action |
|------|--------|
| 1 | Receive POST request at `targetUrl` |
| 2 | Verify payload signature (JWS or HMAC) |
| 3 | Parse the JSON payload |
| 4 | Route by event type (`Saleor-Event` header) |
| 5 | Process the event (sync: return response; async: acknowledge with 200) |
| 6 | Return appropriate HTTP status |

For async webhooks, return HTTP 200 immediately and process the event asynchronously if it requires heavy work.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| App returns 5xx | Async: retried; Sync: operation may fail |
| App returns 4xx | Async: retried; Sync: operation may fail |
| App timeout | Async: retried; Sync: fallback or failure |
| Invalid signature | App should return 401 and not process |
| Malformed payload | App should return 400 and log the error |

## Best Practices

- Always verify payload signatures (JWS or HMAC) before processing any webhook
- Use subscription queries to minimize payload size and improve performance
- Return HTTP 200 immediately for async webhooks, then process asynchronously
- Keep sync webhook handlers fast -- they block the user-facing operation
- Monitor webhook delivery status in the Saleor Dashboard
- Implement idempotency for async handlers -- the same event may be delivered more than once
- Use the `Saleor-Event` header to route to the correct handler function
- Log failed webhook deliveries for debugging and alerting

Fetch the Saleor webhook documentation for exact event type enumerations, subscription query patterns, and retry configuration before implementing.
