---
name: shopify-orders
description: >
  Manage Shopify orders — order lifecycle, FulfillmentOrder model, returns and
  refunds, draft orders, order editing, transactions, metafields, and risk
  analysis. Use when working with Shopify order processing.
---

# Shopify Order Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev graphql admin api orders` for order queries and mutations
2. Web-search `site:shopify.dev fulfillment order api` for fulfillment model
3. Web-search `site:shopify.dev returns refunds api` for returns processing
4. Fetch `https://shopify.dev/docs/api/admin-graphql` and search for `fulfillmentCreateV2`, `returnCreate`, `refundCreate` for current input schemas
5. Web-search `site:shopify.dev order editing api` for order modification workflow

## Order Lifecycle

```
Created → Paid → Fulfilled → Completed
  ↓         ↓       ↓
Cancelled  Refunded  Returned
```

### Order Statuses

| Status | Meaning |
|--------|---------|
| `OPEN` | Order placed, payment authorized or pending |
| `CLOSED` | All items fulfilled and no further action needed |
| `CANCELLED` | Order cancelled by merchant or customer |

### Financial Status

| Status | Meaning |
|--------|---------|
| `PENDING` | Payment not yet processed |
| `AUTHORIZED` | Payment authorized but not captured |
| `PAID` | Payment captured successfully |
| `PARTIALLY_PAID` | Partial payment received |
| `PARTIALLY_REFUNDED` | Some items refunded |
| `REFUNDED` | Fully refunded |
| `VOIDED` | Authorization voided |

### Fulfillment Status

| Status | Meaning |
|--------|---------|
| `UNFULFILLED` | No items shipped |
| `PARTIALLY_FULFILLED` | Some items shipped |
| `FULFILLED` | All items shipped |
| `RESTOCKED` | Items returned and restocked |

## Querying Orders

```graphql
# Pattern: paginated order query with filter
# Fetch live docs for current queryable fields
query Orders($first: Int!, $query: String) {
  orders(first: $first, query: $query) {
    edges {
      node {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet { shopMoney { amount currencyCode } }
        customer { id firstName lastName email }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

Filter examples: `"financial_status:paid fulfillment_status:unfulfilled"`, `"created_at:>2025-01-01"`, `"tag:rush"`.

> **Fetch live docs** for the full query filter syntax and available `displayFinancialStatus`/`displayFulfillmentStatus` enum values.

## FulfillmentOrder Model

The modern fulfillment API (replaces legacy Fulfillment):
- Each order has one or more `FulfillmentOrder` objects
- Each FulfillmentOrder is assigned to a fulfillment location
- Supports third-party fulfillment services
- Lifecycle: `OPEN` → `IN_PROGRESS` → `CLOSED`

### Key Fulfillment Mutations

| Operation | Mutation |
|-----------|----------|
| Create fulfillment | `fulfillmentCreateV2` |
| Cancel fulfillment | `fulfillmentCancel` |
| Update tracking | `fulfillmentTrackingInfoUpdateV2` |
| Move to new location | `fulfillmentOrderMove` |
| Hold fulfillment | `fulfillmentOrderHold` |
| Release hold | `fulfillmentOrderReleaseHold` |

Fulfillment creation requires: fulfillment order ID, line items with quantities, tracking info (number, URL, company), and notify customer flag.

> **Fetch live docs** for `FulfillmentV2Input` fields and `fulfillmentOrderLineItems` shape — these are the most commonly misused inputs.

## Returns and Refunds

### Returns

```
Return Requested → Return Approved → Items Received → Refund Issued
```

Key mutations:
- `returnCreate` — initiate a return (requires order ID, line items, quantities, return reason)
- `returnApproveRequest` — approve customer return request
- `returnRefund` — issue refund for returned items

Return reasons: `DEFECTIVE`, `WRONG_ITEM`, `SIZE_TOO_SMALL`, `SIZE_TOO_LARGE`, `STYLE`, `COLOR`, `DAMAGED_IN_TRANSIT`, `OTHER`, `UNKNOWN`.

> **Fetch live docs** for `ReturnInput` fields and the current list of return reason enum values.

### Refunds

Key mutation: `refundCreate` (requires order ID, line items, quantities, restock type, optional shipping refund).

Restock types: `RETURN` (back to location), `CANCEL` (restock), `NO_RESTOCK` (don't adjust inventory).

> **Fetch live docs** for `RefundInput` fields — refund shipping, note, and currency options vary by API version.

## Draft Orders

Orders created manually by merchants or apps:
- `draftOrderCreate` — create draft with custom pricing
- `draftOrderComplete` — convert to real order (charges payment)
- Use for: custom orders, B2B quotes, phone orders, wholesale pricing
- Can apply custom discounts and shipping rates

> **Fetch live docs** for `DraftOrderInput` fields — custom line items, applied discounts, and shipping lines shape.

## Order Editing

Modify orders after creation (three-step workflow):

1. `orderEditBegin` — start editing session (returns calculated order ID)
2. Make changes: `orderEditAddVariant`, `orderEditSetQuantity`, `orderEditAddDiscount`, `orderEditRemoveLineItemDiscount`
3. `orderEditCommit` — apply changes (adjusts payment if needed)

> **Fetch live docs**: Web-search `site:shopify.dev order editing api` for exact mutation sequence and calculated order fields.

## Order Metafields

Store custom data on orders via `metafieldsSet` (same pattern as product metafields — specify `ownerId` as the order GID).

## Transactions

Payment records on orders:
- Types: authorization, capture, void, refund
- Multiple transactions per order (e.g., authorize then capture)
- Gateway-specific transaction data accessible via `order.transactions`

## Webhook Topics

| Topic | When Fired |
|-------|-----------|
| `orders/create` | New order placed |
| `orders/updated` | Order modified |
| `orders/paid` | Payment captured |
| `orders/fulfilled` | All items shipped |
| `orders/cancelled` | Order cancelled |

> **Fetch live docs** for the complete list of order-related webhook topics and payload shapes.

## Best Practices

- Use FulfillmentOrder model (not legacy Fulfillment) — it's the current standard
- Always check financial status before fulfilling
- Use order editing API instead of cancelling and recreating
- Implement idempotent order processing (check for existing orders before creating)
- Use webhooks (`orders/create`, `orders/paid`, `orders/fulfilled`) for real-time notifications
- Store custom order data in metafields
- Use `query` parameter for filtering orders server-side (not client-side filtering)
- Handle partial fulfillments — one order can span multiple locations

Fetch the Shopify order and fulfillment API documentation for exact mutation inputs, order lifecycle states, and fulfillment patterns before implementing.
