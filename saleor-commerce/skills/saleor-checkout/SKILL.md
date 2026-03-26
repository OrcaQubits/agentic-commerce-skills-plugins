---
name: saleor-checkout
description: Implement the Saleor checkout flow — checkout creation, line items, shipping/billing addresses, delivery methods, payment, and completion. Use when building checkout experiences.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Checkout Flow

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io checkout flow steps` for the end-to-end checkout process
2. Web-search `site:docs.saleor.io checkout mutations graphql` for checkout creation and update mutations
3. Web-search `site:docs.saleor.io transaction payment checkout` for the transaction-based payment flow
4. Fetch `https://docs.saleor.io/docs/developer/checkout` and review checkout lifecycle and required fields
5. Web-search `site:docs.saleor.io delivery methods shipping checkout` for shipping method selection
6. Fetch `https://docs.saleor.io/docs/developer/payments` and review payment initialization and completion

## Checkout Flow Steps

The Saleor checkout follows a sequential flow:

| Step | Mutation | Description |
|------|----------|-------------|
| 1. Create checkout | `checkoutCreate` | Initialize checkout with channel and lines |
| 2. Add/update lines | `checkoutLinesAdd` / `checkoutLinesUpdate` | Manage line items in the cart |
| 3. Set email | `checkoutEmailUpdate` | Set customer email (for guest checkout) |
| 4. Set shipping address | `checkoutShippingAddressUpdate` | Required for physical goods |
| 5. Set billing address | `checkoutBillingAddressUpdate` | Required for payment processing |
| 6. Select delivery method | `checkoutDeliveryMethodUpdate` | Choose shipping method or warehouse pickup |
| 7. Initialize payment | `transactionInitialize` | Start payment with payment App |
| 8. Process payment | `transactionProcess` | Handle additional payment steps (3DS, redirects) |
| 9. Complete checkout | `checkoutComplete` | Finalize and create the order |

> Steps 3-6 can be done in any order, but all must be complete before payment initialization. The checkout validates required fields at each step.

## Checkout Creation

Create a checkout by specifying the channel and initial line items:

| Field | Required | Description |
|-------|----------|-------------|
| `channel` | Yes | Channel slug (determines currency, country, available products) |
| `lines` | Yes | Array of `{variantId, quantity}` objects |
| `email` | No | Customer email (can be set later) |
| `shippingAddress` | No | Shipping address (can be set later) |
| `billingAddress` | No | Billing address (can be set later) |

> **Fetch live docs** for the complete `CheckoutCreateInput` schema -- additional fields include `languageCode`, `validationRules`, and `metadata`.

## Channel-Aware Checkout

Checkouts are always scoped to a channel:

| Aspect | Channel Impact |
|--------|---------------|
| Currency | Prices displayed in the channel currency |
| Country | Default country and allowed shipping destinations |
| Product availability | Only products with channel listings are purchasable |
| Shipping methods | Only shipping zones covering the channel's countries |
| Payment gateways | Only payment Apps configured for the channel |
| Tax calculation | Tax rules based on channel and country |

## Checkout Line Management

### Line Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Add lines | `checkoutLinesAdd` | Add new variants to checkout |
| Update lines | `checkoutLinesUpdate` | Change quantities of existing lines |
| Delete lines | `checkoutLinesDelete` | Remove lines from checkout |
| Replace all lines | `checkoutLinesAdd` with `forceNewLine: false` | Merges with existing lines |

### Line Fields

| Field | Description |
|-------|-------------|
| `variant` | The product variant being purchased |
| `quantity` | Number of units |
| `totalPrice` | Calculated total for the line |
| `unitPrice` | Price per unit (includes discounts) |
| `undiscountedTotalPrice` | Price before promotions |
| `requiresShipping` | Whether this line needs physical delivery |

## Address Management

### Shipping Address

Setting the shipping address triggers recalculation of available delivery methods:

| Field | Required | Description |
|-------|----------|-------------|
| `firstName` | Yes | Customer first name |
| `lastName` | Yes | Customer last name |
| `streetAddress1` | Yes | Primary street address |
| `streetAddress2` | No | Additional address line |
| `city` | Yes | City name |
| `postalCode` | Varies | Postal or ZIP code |
| `country` | Yes | ISO 3166-1 alpha-2 country code |
| `countryArea` | Varies | State or province |
| `phone` | No | Phone number |

### Billing Address

Required before payment. Can be set independently or copied from shipping address. Uses the same address input schema.

## Delivery Method Selection

After setting the shipping address, query available delivery methods:

| Method Type | Description |
|-------------|-------------|
| Shipping method | Standard carrier-based shipping (price or weight based) |
| Warehouse pickup | Click-and-collect from a physical warehouse |
| Custom shipping App | Dynamic rates from a shipping App via sync webhook |

Use `checkoutDeliveryMethodUpdate` to set the selected method by its ID.

> **Fetch live docs** for the `deliveryMethod` union type -- it includes both `ShippingMethod` and `Warehouse` for pickup.

## Payment Initialization (Transaction Flow)

Saleor uses a transaction-based payment model:

| Step | Mutation | Description |
|------|----------|-------------|
| 1. Initialize | `transactionInitialize` | Sends request to payment App; returns data or action needed |
| 2. Process (if needed) | `transactionProcess` | Handle additional steps like 3DS authentication |
| 3. Complete | `checkoutComplete` | Finalize checkout after successful payment |

### Transaction Initialize Input

| Field | Description |
|-------|-------------|
| `id` | Checkout ID |
| `paymentGateway` | Payment App ID and data (gateway-specific) |
| `amount` | Amount to charge (usually checkout total) |
| `idempotencyKey` | Unique key to prevent duplicate transactions |

### Transaction Initialize Response

| Field | Description |
|-------|-------------|
| `transaction` | Created transaction object |
| `transactionEvent` | Initial event (e.g., `CHARGE_REQUESTED`) |
| `data` | Gateway-specific response (e.g., client secret for Stripe) |

## Checkout Completion

After successful payment, call `checkoutComplete`:

| Outcome | Description |
|---------|-------------|
| Success | Returns `order` object; checkout is consumed |
| Confirmation needed | Returns `confirmationNeeded: true` with `confirmationData` |
| Error | Returns `errors` array with field and message |

> Checkout completion is idempotent -- calling it multiple times with the same checkout ID returns the same order.

## Error Handling

Common checkout errors and their causes:

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `INSUFFICIENT_STOCK` | Variant out of stock | Remove line or reduce quantity |
| `INVALID_SHIPPING_METHOD` | Selected method unavailable for address | Re-query available methods |
| `SHIPPING_ADDRESS_NOT_SET` | Missing shipping address | Set address before delivery method |
| `BILLING_ADDRESS_NOT_SET` | Missing billing address | Set address before payment |
| `VOUCHER_NOT_APPLICABLE` | Voucher invalid for this checkout | Remove voucher or adjust checkout |
| `CHECKOUT_NOT_FULLY_PAID` | Payment incomplete | Complete payment before checkout |

## Abandoned Checkout Handling

| Strategy | Description |
|----------|-------------|
| Query stale checkouts | Use `checkouts` query filtered by `lastChange` date |
| Email recovery | Send reminder emails for checkouts with email set |
| Metadata tracking | Use checkout `metadata` to store abandonment funnel data |
| TTL cleanup | Saleor automatically removes expired checkouts (configurable) |

> **Fetch live docs** for checkout expiration settings and the `checkouts` admin query filter syntax.

## Best Practices

- Always create checkouts scoped to a specific channel
- Validate stock availability before checkout completion (Saleor checks automatically, but early validation improves UX)
- Use `transactionInitialize` / `transactionProcess` for payments (not legacy `checkoutPaymentCreate`)
- Set both shipping and billing addresses before payment initialization
- Use `idempotencyKey` on transaction initialization to prevent duplicate charges
- Handle `confirmationNeeded` responses for payment methods requiring additional authentication
- Query `availableShippingMethods` and `availablePaymentGateways` dynamically after address changes
- Store custom data in checkout `metadata` for analytics and recovery workflows
- Implement error handling for every checkout step -- validate responses before proceeding

Fetch the Saleor checkout and transaction documentation for exact mutation inputs, error codes, and payment flow patterns before implementing.
