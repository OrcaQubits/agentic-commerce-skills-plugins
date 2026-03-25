---
name: shopify-webhooks
description: Implement Shopify webhooks — subscription methods (HTTP, EventBridge, Pub/Sub, SQS), HMAC verification, mandatory GDPR webhooks, delivery methods, retry policy, and idempotency. Use when building event-driven Shopify integrations.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify Webhooks

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev webhooks` for webhook overview
2. Web-search `site:shopify.dev webhook topics` for available event topics
3. Web-search `site:shopify.dev gdpr mandatory webhooks` for GDPR requirements

## Subscription Methods

### HTTP (Default)

Shopify POSTs JSON to your endpoint:
- Set up via GraphQL: `webhookSubscriptionCreate`
- Verify with HMAC-SHA256

### Amazon EventBridge

For AWS-based architectures:
- Events delivered to EventBridge partner event source
- Automatic retries and dead-letter queues
- Set up via Partner event source ARN

### Google Cloud Pub/Sub

For GCP-based architectures:
- Events published to Pub/Sub topic
- Topic must grant Shopify publish access

### Amazon SQS

For queue-based processing:
- Events delivered directly to SQS queue

## HMAC Verification

Every HTTP webhook includes `X-Shopify-Hmac-SHA256` header:

```typescript
import crypto from 'crypto';

function verifyWebhook(body: string, hmacHeader: string, secret: string): boolean {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(body, 'utf8')
    .digest('base64');
  return crypto.timingSafeEqual(
    Buffer.from(hash),
    Buffer.from(hmacHeader),
  );
}
```

**Always verify HMAC before processing** — reject unverified webhooks with 401.

## Webhook Topics

### Orders
`orders/create`, `orders/updated`, `orders/paid`, `orders/fulfilled`, `orders/cancelled`, `orders/delete`

### Products
`products/create`, `products/update`, `products/delete`

### Customers
`customers/create`, `customers/update`, `customers/delete`

### Cart
`carts/create`, `carts/update`

### Checkout
`checkouts/create`, `checkouts/update`

### Inventory
`inventory_levels/update`, `inventory_items/update`

### Fulfillments
`fulfillments/create`, `fulfillments/update`

### Refunds
`refunds/create`

## Mandatory GDPR Webhooks

**Every Shopify app MUST implement these three webhooks:**

1. **`customers/data_request`** — customer requests their data (data portability)
2. **`customers/redact`** — customer requests data deletion
3. **`shop/redact`** — store uninstalls your app, delete all store data within 48 hours

Failure to implement these can result in app rejection or removal from the App Store.

## Retry Policy

- Shopify retries failed deliveries (non-2xx responses)
- Up to 8 retries over 4 hours with exponential backoff
- Retried webhooks maintain the original payload from when triggered
- Use `X-Shopify-Triggered-At` header to detect stale payloads
- After all retries fail, the webhook subscription may be removed
- Check webhook delivery status via `webhookSubscriptions` query

## Subscribing via GraphQL

```graphql
mutation WebhookSubscriptionCreate {
  webhookSubscriptionCreate(
    topic: ORDERS_CREATE
    webhookSubscription: {
      callbackUrl: "https://your-app.com/webhooks/orders"
      format: JSON
    }
  ) {
    webhookSubscription {
      id
      topic
      endpoint {
        ... on WebhookHttpEndpoint {
          callbackUrl
        }
      }
    }
    userErrors { field message }
  }
}
```

## Best Practices

- Always verify HMAC before processing
- Respond with 200 immediately, then process asynchronously
- Implement idempotency — webhooks may be delivered more than once
- Use the webhook ID (`X-Shopify-Webhook-Id` header) for deduplication
- Implement all three mandatory GDPR webhooks
- Handle webhook subscription failures — re-subscribe if delivery fails repeatedly
- Use EventBridge/Pub/Sub/SQS for high-volume scenarios
- Log webhook deliveries for debugging (but never log sensitive customer data)
- Version your webhook handler to handle schema changes across API versions

Fetch the Shopify webhook documentation for exact topic names, payload schemas, and subscription patterns before implementing.
