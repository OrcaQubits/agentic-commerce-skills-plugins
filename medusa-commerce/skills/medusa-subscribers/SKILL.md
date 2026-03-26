---
name: medusa-subscribers
description: Implement Medusa v2 event subscribers — pub/sub event handling, subscriber handler functions, scheduled jobs with cron, and the event module (Redis or in-memory). Use when reacting to commerce events.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Subscribers and Scheduled Jobs

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/fundamentals/events-and-subscribers` for subscriber overview
2. Web-search `site:docs.medusajs.com subscriber handler function` for handler API
3. Web-search `site:docs.medusajs.com scheduled jobs cron` for scheduled job patterns
4. Web-search `site:docs.medusajs.com event module redis` for event bus configuration
5. Web-search `site:docs.medusajs.com built-in events list` for available event names

## Subscriber Concept

Subscribers react to events emitted by Medusa workflows and services:
- Asynchronous by default -- do not block the emitting operation
- Registered as files in `src/subscribers/`
- Each file exports a default handler function and a `config` object
- Events follow a naming convention: `{entity}.{action}` (e.g., `product.created`)

## Subscriber File Structure

```
src/subscribers/
├── product-created.ts     # Reacts to product.created
├── order-placed.ts        # Reacts to order.placed
└── customer-registered.ts # Reacts to customer.created
```

Each file is auto-discovered -- no manual registration required.

## Subscriber Handler Pattern

```typescript
// src/subscribers/product-created.ts
// Fetch live docs for SubscriberArgs and SubscriberConfig types
import type { SubscriberArgs, SubscriberConfig } from "@medusajs/framework"

export default async function productCreatedHandler(
  { event, container }: SubscriberArgs<{ id: string }>) {
  // event.data.id contains the entity ID — fetch live docs for payload shapes
}
```

### Config Export

```typescript
// Fetch live docs for SubscriberConfig options
export const config: SubscriberConfig = {
  event: "product.created",
}
```

## Event Naming Conventions

| Domain | Event Examples |
|--------|---------------|
| Products | `product.created`, `product.updated`, `product.deleted` |
| Orders | `order.placed`, `order.canceled`, `order.completed` |
| Customers | `customer.created`, `customer.updated` |
| Cart | `cart.created`, `cart.updated` |
| Fulfillment | `fulfillment.created`, `fulfillment.canceled` |
| Payment | `payment.captured`, `payment.refunded` |
| Inventory | `inventory-item.created` |
| Auth | `invite.created`, `invite.accepted` |

> **Fetch live docs** for the complete event list -- events are added and renamed across Medusa releases.

## Subscribing to Multiple Events

A single subscriber can listen to multiple events:

```typescript
// Fetch live docs for multi-event config
export const config: SubscriberConfig = {
  event: ["product.created", "product.updated"],
}
```

The handler receives the event name in `event.name` to distinguish which event triggered it.

## Event Payload

| Property | Type | Description |
|----------|------|-------------|
| `event.name` | `string` | The event that triggered the subscriber |
| `event.data` | `object` | Payload emitted by the workflow/service |
| `event.metadata` | `object` | Internal metadata (event ID, timestamp) |

The `data` shape varies per event. Typically contains the entity ID(s) affected.

## Event Module Configuration

| Module | Transport | Use Case |
|--------|-----------|----------|
| In-memory (default) | Process memory | Development, single-instance |
| Redis Event Module | Redis Pub/Sub | Production, multi-instance |

### Redis Event Module Setup

```typescript
// In medusa-config.ts modules array
// Fetch live docs for Redis event module configuration
{
  resolve: "@medusajs/medusa/event-bus-redis",
  options: { redisUrl: process.env.REDIS_URL },
}
```

In production, always use the Redis event module to ensure events are delivered across multiple server instances.

## Scheduled Jobs

Scheduled jobs run on a cron schedule, independent of events:

### Job File Structure

```
src/jobs/
├── daily-sync.ts          # Daily data synchronization
└── cleanup-expired.ts     # Periodic cleanup
```

### Scheduled Job Skeleton

```typescript
// src/jobs/daily-sync.ts
// Fetch live docs for MedusaContainer type
import type { MedusaContainer } from "@medusajs/framework"

export default async function dailySyncJob(container: MedusaContainer) {
  const service = container.resolve("my-module")
  // Fetch live docs for job handler API
}
```

### Job Config Export

```typescript
// Fetch live docs for cron expression format
export const config = {
  name: "daily-sync",
  schedule: "0 0 * * *", // Midnight daily (cron syntax)
}
```

### Common Cron Patterns

| Schedule | Cron Expression |
|----------|----------------|
| Every minute | `* * * * *` |
| Every 15 minutes | `*/15 * * * *` |
| Every hour | `0 * * * *` |
| Daily at midnight | `0 0 * * *` |
| Weekly on Monday | `0 0 * * 1` |
| Monthly on the 1st | `0 0 1 * *` |

## Worker Mode and Jobs

| Worker Mode | Subscribers | Scheduled Jobs |
|-------------|------------|----------------|
| `shared` | Processed in-process | Processed in-process |
| `server` | Emitted only, not processed | Not processed |
| `worker` | Processed | Processed |

In production, run a dedicated `worker` instance to handle subscribers and scheduled jobs separately from HTTP traffic.

## Emitting Custom Events

Custom events can be emitted from workflows using the `emitEventStep`:

```typescript
// Inside a workflow
// Fetch live docs for emitEventStep import
import { emitEventStep } from "@medusajs/medusa/core-flows"

emitEventStep({ eventName: "custom.event", data: { id: "123" } })
```

## Best Practices

- Keep subscribers lightweight -- offload heavy work to workflows
- Use descriptive file names matching the event they handle
- Always type the event payload generic: `SubscriberArgs<{ id: string }>`
- Use the Redis event module in production for reliability across instances
- Do not perform synchronous, blocking operations in subscribers
- Use scheduled jobs for periodic tasks -- do not poll from subscribers
- Resolve services from the container, never import directly

Fetch the Medusa subscriber and events documentation for exact event names, payload shapes, and Redis event module configuration before implementing.
