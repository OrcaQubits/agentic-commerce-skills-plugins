---
name: saleor-orders
description: Manage the Saleor order lifecycle — order creation, fulfillments, returns, refunds, draft orders, and order events. Use when working with Saleor orders.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Order Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io orders order lifecycle status` for order model and state transitions
2. Web-search `site:docs.saleor.io fulfillments order fulfillment` for fulfillment creation and tracking
3. Web-search `site:docs.saleor.io returns refunds order` for return and refund workflows
4. Fetch `https://docs.saleor.io/docs/developer/orders` and review order statuses, events, and mutations
5. Web-search `site:docs.saleor.io draft orders` for draft order creation and completion patterns
6. Fetch `https://docs.saleor.io/docs/developer/fulfillment` and review fulfillment line items and tracking

## Order Status and States

### Order Status

| Status | Description |
|--------|-------------|
| `UNCONFIRMED` | Order created but not yet confirmed (e.g., pending payment) |
| `UNFULFILLED` | Order confirmed and paid; no items shipped yet |
| `PARTIALLY_FULFILLED` | Some items have been shipped |
| `FULFILLED` | All items have been shipped |
| `PARTIALLY_RETURNED` | Some items have been returned |
| `RETURNED` | All items have been returned |
| `CANCELED` | Order has been cancelled |

### Authorization Status

| Status | Description |
|--------|-------------|
| `NONE` | No payment authorized |
| `PARTIAL` | Partial amount authorized |
| `FULL` | Full amount authorized |

### Charge Status

| Status | Description |
|--------|-------------|
| `NONE` | No payment charged |
| `PARTIAL` | Partial amount charged |
| `FULL` | Full amount charged |
| `OVERCHARGED` | Charged amount exceeds order total |

## Order Creation Flow

Orders in Saleor are typically created through the checkout completion process:

| Step | Description |
|------|-------------|
| 1. Checkout completed | Customer completes checkout with payment |
| 2. Order created | System generates order with status `UNCONFIRMED` or `UNFULFILLED` |
| 3. Payment confirmed | Transaction events confirm successful charge |
| 4. Ready for fulfillment | Order moves to `UNFULFILLED` status |

> Orders can also be created via draft orders (see below) or programmatically through the `orderCreateFromCheckout` mutation.

## Draft Orders

Draft orders allow merchants and staff to create orders manually:

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create draft | `draftOrderCreate` | Specify lines, customer, addresses, channel |
| Update draft | `draftOrderUpdate` | Modify lines, addresses, discounts |
| Add lines | `draftOrderLinesCreate` | Add product variants to draft |
| Delete line | `orderLineDelete` | Remove a line from the draft |
| Complete draft | `draftOrderComplete` | Convert to a real order |
| Delete draft | `draftOrderDelete` | Remove draft before completion |

## Fulfillment Flow

### Creating a Fulfillment

| Step | Description |
|------|-------------|
| 1. Query order | Retrieve unfulfilled order lines and warehouse info |
| 2. Create fulfillment | Use `orderFulfill` with line items and quantities |
| 3. Add tracking | Tracking number and URL included in fulfillment creation |
| 4. Notify customer | Optional email notification on fulfillment |

### Key Fulfillment Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Fulfill order | `orderFulfill` | Specify lines, quantities, warehouse, tracking |
| Cancel fulfillment | `orderFulfillmentCancel` | Restock items optionally |
| Update tracking | `orderFulfillmentUpdateTracking` | Update tracking number and URL |
| Approve fulfillment | `orderFulfillmentApprove` | For orders requiring approval before shipping |

### Fulfillment Status

| Status | Description |
|--------|-------------|
| `FULFILLED` | Items shipped and tracking assigned |
| `CANCELED` | Fulfillment cancelled; items may be restocked |
| `WAITING_FOR_APPROVAL` | Fulfillment created but awaiting staff approval |
| `REFUNDED` | Fulfillment refunded |
| `RETURNED` | Items returned from this fulfillment |
| `REFUNDED_AND_RETURNED` | Items both returned and refunded |

## Returns and Refunds

### Return Flow

| Step | Description |
|------|-------------|
| 1. Create return | Use `orderFulfillmentReturnProducts` with fulfillment lines |
| 2. Specify quantities | Indicate which items and how many are being returned |
| 3. Optional refund | Include refund amount or create refund separately |
| 4. Restock | Optionally restock returned items to warehouse |

### Refund Flow

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Grant refund | `orderGrantRefundCreate` | Create a granted refund (amount or lines) |
| Update grant | `orderGrantRefundUpdate` | Modify granted refund before processing |
| Send refund | `transactionRequestAction` with `REFUND` | Process the actual refund via payment App |

> Saleor separates the concept of "granting" a refund (merchant decision) from "sending" a refund (payment processing). This allows partial refunds and multi-step refund workflows.

## Order Events

Saleor maintains a comprehensive event log for every order:

| Event Type | Description |
|------------|-------------|
| `PLACED` | Order was placed |
| `CONFIRMED` | Order was confirmed |
| `FULFILLMENT_CANCELED` | A fulfillment was cancelled |
| `FULFILLMENT_FULFILLED_ITEMS` | Items were fulfilled |
| `PAYMENT_CAPTURED` | Payment was captured |
| `PAYMENT_REFUNDED` | Payment was refunded |
| `NOTE_ADDED` | Staff note was added |
| `EMAIL_SENT` | Notification email was sent |
| `CANCELED` | Order was cancelled |

> **Fetch live docs** for the complete `OrderEventsEnum` -- additional event types exist for tracking, returns, and transaction updates.

## Order Line Items

Each order contains `OrderLine` objects representing purchased items:

| Field | Description |
|-------|-------------|
| `productName` | Product name at time of purchase |
| `variantName` | Variant name at time of purchase |
| `productSku` | SKU at time of purchase |
| `quantity` | Number of units ordered |
| `quantityFulfilled` | Number of units already shipped |
| `unitPrice` | Price per unit (net and gross) |
| `totalPrice` | Line total (net and gross) |
| `undiscountedUnitPrice` | Original price before discounts |

> Order lines store a snapshot of product data at the time of purchase. Changes to the product after the order do not affect existing orders.

## Order Discounts

| Discount Type | Description |
|---------------|-------------|
| Voucher | Applied via voucher code during checkout |
| Promotion | Automatic catalog or order promotion |
| Manual discount | Staff-applied discount via `orderDiscountAdd` |

### Key Discount Mutations

| Operation | Mutation |
|-----------|----------|
| Add manual discount | `orderDiscountAdd` |
| Update discount | `orderDiscountUpdate` |
| Delete discount | `orderDiscountDelete` |

## Key Admin Queries

| Operation | Query | Notes |
|-----------|-------|-------|
| List orders | `orders` | Filter by status, date, customer, channel |
| Get order | `order` | By ID; includes lines, events, fulfillments |
| Order by token | `orderByToken` | Customer-facing order lookup |

## Best Practices

- Use draft orders for manual order creation instead of direct order mutations
- Always check `chargeStatus` and `authorizeStatus` before fulfilling
- Use `orderFulfillmentReturnProducts` for returns -- it handles restock and refund in one step
- Separate grant refund (business decision) from transaction refund (payment action)
- Monitor order events for audit trails and debugging
- Use channel-scoped queries when fetching orders for a specific storefront
- Handle partial fulfillments -- one order may ship from multiple warehouses
- Store additional order metadata using the `metadata` and `privateMetadata` fields
- Always verify stock availability before creating fulfillments

Fetch the Saleor order lifecycle documentation for exact mutation inputs, order event types, and fulfillment patterns before implementing.
