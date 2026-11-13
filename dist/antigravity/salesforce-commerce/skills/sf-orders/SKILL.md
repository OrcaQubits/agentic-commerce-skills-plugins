---
name: sf-orders
description: >
  Manage Salesforce Commerce orders — B2C (SCAPI order objects, status
  lifecycle, order confirmation, returns) and B2B (Order object, OrderItem,
  splits, approval workflows, fulfillment). Use when implementing order
  management across either platform.
---

# sf-orders

## Before Writing Code

**Fetch live docs before implementing order management features.**

1. Web-search: "Salesforce Commerce Cloud SCAPI Shopper Orders API 2026"
2. Web-search: "Salesforce B2C Commerce order lifecycle status transitions 2026"
3. Web-search: "Salesforce B2B Commerce Order OrderItem approval workflows 2026"
4. Web-search: "Salesforce Order Management OMS documentation 2026"
5. Web-fetch the SCAPI Shopper Orders reference for current schemas
6. Web-fetch the Salesforce Order object reference for B2B fields

## Conceptual Architecture

### B2C Commerce Order Lifecycle

```
Basket (cart)
  -> Order Created (created)
    -> open (confirmed, ready for fulfillment)
      -> shipped -> completed
      -> partially_shipped -> open
      -> cancelled
    -> failed (payment declined)
    -> replaced (exchange)
```

**B2C Order Status Definitions:**

| Status | Meaning |
|---|---|
| created | Order object created, payment authorized |
| new / open | Confirmed, ready for fulfillment (synonymous; varies by config) |
| completed | All items fulfilled and delivered |
| cancelled | Cancelled by customer or admin |
| replaced | Replaced with new order (e.g., exchange) |
| failed | Creation failed (payment or inventory) |

**Key B2C Order Objects:**

- **Basket**: Temporary cart object; expires after inactivity
- **Order**: Created from basket upon payment success; auto-generated order number
- **OrderItem**: Line item with product, quantity, price
- **PaymentInstrument**: Payment method attached to order
- **ShippingOrder / Shipment**: Fulfillment tracking per delivery group

**B2C Order Confirmation:**
- Confirmation page displays order summary, number, delivery estimate
- Confirmation email triggered via Business Manager templates or ESP (SendGrid, Mailchimp)
- Supports dynamic tokens for order number, customer name, line items

**B2C Order Export for Fulfillment:**
- XML export via scheduled job or real-time webhook to OMS/ERP
- Fulfillment system acknowledges receipt, sends back tracking info
- Supports partial shipment status updates per line item

### B2B Commerce Order Lifecycle

```
WebCart (persists across sessions)
  -> Checkout Flow (multi-step)
    -> Order (Draft)
      -> Activated (submitted)
        -> Approval Workflow (optional)
        -> Fulfillment / Order Splits
          -> completed
```

**B2C vs B2B Order Model Differences:**

| Aspect | B2C (SFCC) | B2B (Lightning) |
|---|---|---|
| Cart object | Basket (temporary) | WebCart (persistent) |
| Order object | SFCC Order (proprietary) | Salesforce Order (standard) |
| Line item | OrderItem (SFCC) | OrderItem (standard sObject) |
| Initial status | created -> open | Draft -> Activated |
| Approval | Not built-in | Flow / Process Builder approvals |
| Payment | Cartridge-based processors | Apex PaymentGatewayAdapter |
| Fulfillment tracking | XML export + status sync | OrderDeliveryGroup sObject |
| Reorder | Clone items to new basket | Quick reorder button, bulk CSV upload |
| Payment terms | Credit card at checkout | PO, net terms, credit limits |
| Order splits | Not native | Parent-child order pattern via OrderSummary |

**B2B Approval Workflow Concepts:**
- Approval criteria: order total threshold, product restrictions, buyer role
- Routing via Flow or Process Builder to designated approver
- Actions: approve, reject, request changes, auto-escalate on timeout

**B2B Order Splits:**
- Multi-location fulfillment splits order across warehouses
- Parent order spawns child orders per location
- OrderSummary provides unified tracking view
- OrderDeliveryGroup tracks shipments per split

### Salesforce Order Management (OMS)

Optional paid add-on for unified order orchestration across B2C and B2B.

| OMS Object | Purpose |
|---|---|
| OrderSummary | Aggregate order (unifies B2C/B2B) |
| FulfillmentOrder | Per-warehouse fulfillment view |
| Order Broker | Routing engine for optimal location |

**OMS Capabilities:**
- Omnichannel fulfillment: ship-from-store, BOPIS
- Distributed Order Management (DOM) routing
- Unified returns processing
- Service Console for agents

**When to use OMS:** Complex multi-location fulfillment, high order volume, omnichannel requirements, high return complexity. Evaluate ROI vs. native order management.

### Order Events

| Platform | Key Events |
|---|---|
| B2C | Order Created, Status Changed, Exported, Cancelled |
| B2B | Order Submitted, Approved, Rejected, Shipped (via Platform Events / CDC) |
| OMS | OrderSummary Created, FulfillmentOrder Created, Shipment Confirmed, Return Initiated |

## Code Examples

```javascript
// Pattern: B2C order status check
// Fetch live docs for SCAPI Shopper Orders endpoints
// GET /orders/{orderNo} -> check order.status
```

```apex
// Pattern: B2B approval trigger
// Fetch live docs for Process Builder / Flow order approvals
// Order.Status changes from Draft -> Activated -> triggers approval
```

## Best Practices

### Order Creation
- Validate basket/cart before conversion (inventory, pricing, address)
- Capture payment authorization synchronously; handle failures with retry logic
- Use idempotent operations to prevent duplicate orders

### Fulfillment Integration
- Export orders to fulfillment system within minutes of creation
- Use idempotent export to avoid duplicate orders in downstream systems
- Support partial shipment status updates per line item

### B2B-Specific
- Persist carts across sessions; support multiple named carts per account
- Configure approval thresholds per buyer group or account
- Enforce credit limits at checkout before order submission

### Monitoring
- Track order creation rate, export failures, and fulfillment SLA in real-time
- Alert on stuck orders (no status change within expected window)
- Monitor refund processing time and payment authorization success rates

Fetch the SCAPI Shopper Orders reference and Salesforce Order object docs for exact schemas and field names before implementing.
