---
name: medusa-orders
description: Manage Medusa v2 orders — order lifecycle and state machine, fulfillment workflows, returns, exchanges, claims, draft orders, and order editing. Use when working with order processing.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Order Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com order module` for order data model and service methods
2. Web-search `site:docs.medusajs.com order workflow fulfillment` for fulfillment workflow steps
3. Web-search `site:docs.medusajs.com return exchange claim` for return/exchange/claim flows
4. Fetch `https://docs.medusajs.com/resources/references/order` and review the `IOrderModuleService` interface
5. Web-search `medusajs v2 draft order editing 2026` for latest order editing workflows

## Order Lifecycle

### State Machine

```
PENDING ──> COMPLETED ──> FULFILLED ──> DELIVERED
    │           │              │
    └─ CANCELED └─ RETURNED    └─ PARTIALLY_RETURNED
```

### Order Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Order created, awaiting payment |
| `completed` | Payment captured, order confirmed |
| `archived` | Order archived (no further action) |
| `canceled` | Order canceled before fulfillment |
| `requires_action` | Manual intervention needed |

### Fulfillment Status

| Status | Meaning |
|--------|---------|
| `not_fulfilled` | No items shipped |
| `partially_fulfilled` | Some items shipped |
| `fulfilled` | All items shipped |
| `shipped` / `delivered` | In transit / arrived |
| `partially_returned` / `returned` | Items returned |

### Payment Status

| Status | Meaning |
|--------|---------|
| `not_paid` / `awaiting` | No payment / pending auth |
| `authorized` | Payment authorized, not captured |
| `captured` | Full payment captured |
| `partially_refunded` / `refunded` | Refund issued |
| `canceled` | Payment voided |

## Order Module Architecture

```
Order Module ──link──> Payment Module (payment collections)
Order Module ──link──> Fulfillment Module (fulfillments)
Order Module ──link──> Product Module (line items)
Order Module ──link──> Customer Module (customer)
```

> **Fetch live docs** for exact link definitions and remote query patterns for cross-module order data.

## Key Service Methods

| Operation | Method | Notes |
|-----------|--------|-------|
| List orders | `orderModuleService.listOrders()` | Filters, pagination |
| Retrieve order | `orderModuleService.retrieveOrder()` | By ID with relations |
| Cancel order | via `cancelOrderWorkflow` | Workflow-managed |
| Archive order | via `archiveOrderWorkflow` | Workflow-managed |
| Complete order | via `completeOrderWorkflow` | After payment capture |

## Fulfillment Workflow

```
Order Confirmed ──> Create Fulfillment ──> Create Shipment ──> Delivered
```

| Workflow | Purpose |
|----------|---------|
| `createFulfillmentWorkflow` | Create fulfillment for order items |
| `cancelFulfillmentWorkflow` | Cancel a pending fulfillment |
| `createShipmentWorkflow` | Add tracking and mark as shipped |
| `markOrderFulfillmentAsDeliveredWorkflow` | Mark fulfillment as delivered |

> **Fetch live docs** for workflow input shapes -- fulfillment items, tracking numbers, and labels.

## Returns

```
Return Requested ──> Return Received ──> Refund Issued
       └─> Return Canceled      └─> Items Restocked
```

| Workflow | Purpose |
|----------|---------|
| `createReturnWorkflow` | Initiate return for order items |
| `confirmReturnReceiveWorkflow` | Mark return items as received |
| `cancelReturnWorkflow` | Cancel a return request |

Return reasons are configurable via the **Return Reason** entity (supports nesting via `parent_return_reason_id`).

## Exchanges and Claims

| Workflow | Purpose |
|----------|---------|
| `createExchangeWorkflow` | Initiate exchange (return + new items) |
| `cancelExchangeWorkflow` | Cancel pending exchange |
| `createClaimWorkflow` | Create claim for damaged/wrong items |
| `cancelClaimWorkflow` | Cancel a pending claim |

Exchanges combine return of original items with shipment of replacements, handling price differences automatically. Claims can result in refund, replacement, or both.

## Draft Orders

```ts
// Skeleton: create draft order
// Fetch live docs for createOrderWorkflow input shape
import { createOrderWorkflow } from "@medusajs/medusa/core-flows"

const { result } = await createOrderWorkflow(container)
  .run({ input: { /* order data */ } })
// Fetch live docs for CreateOrderWorkflowInput
```

## Order Editing

Modify orders after creation using the **Order Change** mechanism:

```
Begin Edit ──> Add/Remove Items ──> Confirm Edit ──> Payment Adjustment
```

### Order Change Actions

| Action | Description |
|--------|-------------|
| `ITEM_ADD` | Add a new line item |
| `ITEM_REMOVE` | Remove an existing line item |
| `ITEM_UPDATE` | Update line item quantity |
| `SHIPPING_ADD` / `SHIPPING_REMOVE` | Modify shipping methods |

> **Fetch live docs** for `orderEditAddItemWorkflow` and related edit workflows.

## Admin API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/admin/orders` | GET | List orders with filters |
| `/admin/orders/:id` | GET | Retrieve single order |
| `/admin/orders/:id/cancel` | POST | Cancel order |
| `/admin/orders/:id/fulfillments` | POST | Create fulfillment |
| `/admin/orders/:id/returns` | POST | Create return |
| `/admin/orders/:id/exchanges` | POST | Create exchange |
| `/admin/orders/:id/claims` | POST | Create claim |

> **Fetch live docs** for request body shapes and query parameters on each route.

## Best Practices

### Order Processing
- Always use **workflows** for order mutations -- they handle cross-module orchestration
- Check payment status before creating fulfillments
- Use order changes for post-creation modifications -- never mutate order data directly
- Implement idempotency keys for order creation to prevent duplicates

### Fulfillment
- Support **partial fulfillments** -- one order may ship from multiple locations
- Track fulfillment status through the state machine, not manual status sets
- Use `createShipmentWorkflow` to attach tracking info (not direct service calls)

### Returns and Exchanges
- Configure return reasons as a hierarchy (parent + child reasons) for analytics
- Exchanges automatically calculate price differences -- do not manually compute
- Claims should reference the original fulfillment for traceability

### Observability
- Subscribe to order events (`order.placed`, `order.completed`, `order.canceled`) for side effects
- Use subscribers for notifications, analytics, and third-party integrations

Fetch the Medusa v2 order module documentation and workflow references for exact service method signatures, workflow inputs, and state machine transitions before implementing.
