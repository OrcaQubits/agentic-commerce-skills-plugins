---
name: spree-events-webhooks
description: >
  Build with Spree's event bus and Webhooks 2.0 — `Spree::Events` publication,
  `Spree::Subscriber` DSL with `subscribes_to` and `on`, wildcard matching,
  lifecycle events (`{model}.created/.updated/.deleted` via
  `publishes_lifecycle_events`), the canonical event catalog (order.*,
  payment.*, shipment.*, product.*), Webhooks 2.0 endpoints, HMAC-SHA256 signing
  (`X-Spree-Webhook-Signature`), exponential-backoff retries, and Sidekiq job
  orchestration. Use when wiring event-driven business logic, building webhook
  consumers, or replacing ActiveSupport callback chains.
---

# Spree Events & Webhooks

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/events for the event bus.
2. Fetch https://spreecommerce.org/docs/developer/core-concepts/webhooks for Webhooks 2.0 (HMAC, retries).
3. Inspect the live `lib/spree/event.rb` / `lib/spree/subscriber.rb` and `app/subscribers/` in the `spree` gem for the canonical event names per release.
4. Check the v5.4 announcement for any Webhooks 2.0 changes.
5. For verifying signatures, also check the `@spree/sdk` if you're consuming webhooks in TypeScript.

## Conceptual Architecture

### Why an Event Bus?

Spree's event bus (`Spree::Events`) replaces ad-hoc ActiveSupport::Notifications and `after_*` callbacks for cross-cutting concerns. Benefits:
- **Decoupled** — subscribers don't know about each other
- **Testable** — assert on event publication, not on side effects
- **Webhook-friendly** — Webhooks 2.0 piggybacks on the same events
- **Wildcard subscriptions** — `order.*`, `*.created`, `*` for cross-cutting logging

### Publishing Events

In core code:

```ruby
Spree::Bus.publish('order.completed', order: order, user: order.user)
```

Or via `publishes_lifecycle_events`:

```ruby
class Spree::Product < ApplicationRecord
  publishes_lifecycle_events  # auto-emits product.created/.updated/.deleted
end
```

### Subscribing

```ruby
# app/subscribers/order_completed_subscriber.rb
class OrderCompletedSubscriber < Spree::Subscriber
  subscribes_to 'order.completed'

  on 'order.completed', :handle_completed

  def handle_completed(event)
    order = event.order
    AccountingSync.enqueue(order_id: order.id)
  end
end
```

Subscribers in `app/subscribers/` auto-register on app boot. Otherwise:

```ruby
# config/initializers/spree.rb
Spree.subscribers << CustomSubscriber
```

### Wildcards

```ruby
subscribes_to 'order.*'   # all order events
subscribes_to '*.created' # all lifecycle creations
subscribes_to '*'         # everything (use for logging only)
```

### Canonical Event Catalog (verify against live source)

| Domain | Events |
|--------|--------|
| Order | `order.created`, `order.updated`, `order.completed`, `order.canceled`, `order.resumed`, `order.paid`, `order.shipped` |
| Payment | `payment.created`, `payment.updated`, `payment.paid` |
| Shipment | `shipment.created`, `shipment.updated`, `shipment.shipped`, `shipment.canceled`, `shipment.resumed` |
| Product | `product.activate`, `product.archive`, `product.out_of_stock`, `product.back_in_stock` |
| Lifecycle | `{model}.created`, `{model}.updated`, `{model}.deleted` for any model with `publishes_lifecycle_events` |
| Cart | `cart.add_item`, `cart.remove_item`, `cart.update` |
| User | `user.created`, `user.password_reset_requested` |

This list **isn't exhaustive** — releases add events. Always re-check.

### Event Payload Shape

An `Event` object exposes the payload keys as methods:

```ruby
on 'order.completed', :handle
def handle(event)
  event.order        # Spree::Order
  event.user         # Spree::User
  event.firing_class # Spree::Order (the publisher)
end
```

### Webhooks 2.0

Webhooks subscribe to Spree events and forward HMAC-signed POSTs to external URLs. Configured per Store in admin (Settings → Webhooks).

A webhook endpoint declares:
- **URL** — your receiver
- **Event subscriptions** — pick events (e.g., `order.completed`, `payment.paid`)
- **Secret** — used to sign payloads

### Delivery Mechanics

1. Spree event publishes
2. `WebhookEventSubscriber` matches active endpoints
3. For each match, enqueues a Sidekiq job
4. Worker POSTs to the endpoint URL with body `{ event, data, timestamp }`
5. Signs with `X-Spree-Webhook-Signature: sha256=<hex>` (HMAC-SHA256 of body using shared secret)
6. Expects 2xx; otherwise retries with exponential backoff up to 5 attempts
7. After 5 failures, marks the delivery dead-letter for manual replay

### Signature Verification (Consumer Side)

```ruby
def verify_signature(body, signature_header, secret)
  expected = OpenSSL::HMAC.hexdigest('SHA256', secret, body)
  ActiveSupport::SecurityUtils.secure_compare(expected, signature_header.sub(/^sha256=/, ''))
end
```

```typescript
import { createHmac, timingSafeEqual } from 'crypto';

function verify(body: string, header: string, secret: string) {
  const expected = createHmac('sha256', secret).update(body).digest('hex');
  const received = header.replace(/^sha256=/, '');
  return timingSafeEqual(Buffer.from(expected), Buffer.from(received));
}
```

### Idempotency on the Consumer

Spree retries on non-2xx. Make your handler idempotent — keyed by event ID or order ID + state.

## Implementation Guidance

### Designing a Subscriber

Pattern: one subscriber class per concern, not per event.

```ruby
class AnalyticsSubscriber < Spree::Subscriber
  subscribes_to 'order.completed', 'order.canceled', 'product.activate'

  on 'order.completed', :track_purchase
  on 'order.canceled',  :track_cancellation
  on 'product.activate', :track_launch

  private

  def track_purchase(event)
    Analytics.track(
      user_id: event.order.user_id,
      event: 'purchase',
      properties: { revenue: event.order.total }
    )
  end

  def track_cancellation(event)
    Analytics.track(user_id: event.order.user_id, event: 'cancellation')
  end

  def track_launch(event)
    Analytics.track(event: 'product_launched', properties: { id: event.product.id })
  end
end
```

### Async Subscribers

Don't block the request — enqueue Sidekiq jobs:

```ruby
on 'order.completed', :handle

def handle(event)
  EmailJob.perform_later(order_id: event.order.id)
end
```

Webhooks 2.0 are already async via Sidekiq — your custom subscriber doesn't need to re-async unless it's heavy.

### Publishing Custom Events

For extension code:

```ruby
# In a service object
Spree::Bus.publish('my_app.special_discount_applied', order: order, amount: amount)

# Subscribe
class MyAppSubscriber < Spree::Subscriber
  subscribes_to 'my_app.special_discount_applied'
  on 'my_app.special_discount_applied', :log_it
end
```

Use a `my_app.` prefix to avoid collisions with core events.

### Wiring Webhooks 2.0

In admin → Settings → Webhooks:
- URL: `https://your-app.com/webhooks/spree`
- Events: pick from the catalog
- Secret: generated; store in your consumer's env

Verify against the live admin UI — Webhooks 2.0 management may have moved.

### Receiving a Webhook (Rails)

```ruby
class WebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token

  def spree
    body = request.body.read
    unless verify_signature(body, request.headers['X-Spree-Webhook-Signature'], ENV['SPREE_WEBHOOK_SECRET'])
      head :unauthorized and return
    end

    payload = JSON.parse(body)
    case payload['event']
    when 'order.completed' then OrderCompletedHandler.perform_later(payload['data'])
    end

    head :ok
  end
end
```

Respond 2xx **immediately** — process async. Slow handlers hit the retry threshold.

### Receiving a Webhook (Next.js)

```typescript
// app/api/webhooks/spree/route.ts
export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get('x-spree-webhook-signature') ?? '';
  if (!verify(body, signature, process.env.SPREE_WEBHOOK_SECRET!)) {
    return new Response('Unauthorized', { status: 401 });
  }
  const payload = JSON.parse(body);
  // Enqueue async — Inngest, Trigger.dev, BullMQ, etc.
  return new Response('OK');
}
```

### Common Pitfalls

- **Subscriber that doesn't enqueue async work** — slows down the request and stalls the bus.
- **Forgetting to register a subscriber** — non-`app/subscribers/` location requires `Spree.subscribers << ...`.
- **Hardcoding event names** — make a constant, since event names occasionally rename across releases.
- **Verifying signature against the wrong secret** — multi-store deployments have a secret per Webhook endpoint, not per Store.
- **Slow webhook receiver** — Spree retries; you get a duplicate-handling problem. Always 2xx fast.
- **Subscribing to `*` in production** — performance hazard. Use for dev/diagnostics only.
- **Assuming event payload shape** — verify the publisher's call site; lifecycle vs custom events have different keys.

Always cross-reference the live `app/subscribers/` directory and the published events in the `spree` gem source — the event taxonomy evolves with new features.
