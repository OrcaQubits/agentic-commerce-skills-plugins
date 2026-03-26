---
name: medusa-cart-checkout
description: Implement Medusa v2 cart and checkout — cart lifecycle, line items, shipping and payment selection, sales channels, and checkout completion flow. Use when building cart and checkout features.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Cart and Checkout

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com cart module` for cart data model and service methods
2. Web-search `site:docs.medusajs.com checkout flow` for the end-to-end checkout process
3. Web-search `site:docs.medusajs.com sales channel` for sales channel scoping
4. Fetch `https://docs.medusajs.com/resources/references/cart` and review the `ICartModuleService` interface
5. Web-search `medusajs v2 cart workflow 2026` for latest cart-related workflow steps

## Cart Lifecycle

### Flow

```
Create Cart ──> Add Line Items ──> Set Address
  ──> Select Shipping ──> Init Payment ──> Complete
```

### Cart States

| State | Description |
|-------|-------------|
| Active | Cart is open, items can be added/removed |
| Completing | Checkout in progress, payment being processed |
| Completed | Cart converted to order, no further modifications |

## Cart Data Model

| Entity | Key Fields |
|--------|------------|
| **Cart** | region_id, customer_id, sales_channel_id, email |
| **LineItems[]** | variant_id, quantity, unit_price, Adjustments[] |
| **ShippingMethods[]** | shipping_option_id, amount, data |
| **Addresses** | shipping_address, billing_address |
| **PaymentCollection** | PaymentSessions[] |

### Module Architecture

| Link Target | Purpose |
|-------------|---------|
| Product Module | Variant resolution |
| Region Module | Currency, tax rules |
| Sales Channel Module | Storefront scoping |
| Promotion Module | Discount application |
| Payment Module | Payment sessions |
| Fulfillment Module | Shipping methods |

> **Fetch live docs** for cross-module link definitions and `remoteQuery` usage for cart enrichment.

## Checkout Steps

### Step 1: Create Cart

```ts
// Skeleton: create cart in storefront
// Fetch live docs for createCartWorkflow input
const cart = await createCartWorkflow(container)
  .run({ input: { region_id, sales_channel_id } })
// Fetch live docs for required vs optional fields
```

### Step 2: Add Line Items

| Workflow | Purpose |
|----------|---------|
| `addToCartWorkflow` | Add variant + quantity to cart |
| `updateLineItemInCartWorkflow` | Update quantity of existing item |
| `deleteLineItemsWorkflow` | Remove items from cart |

### Step 3: Set Addresses

| Field | Required | Notes |
|-------|----------|-------|
| `first_name` / `last_name` | Yes | |
| `address_1` | Yes | Street address |
| `city` | Yes | |
| `country_code` | Yes | ISO 2-letter code |
| `postal_code` | Conditional | Required by region |
| `province` | Conditional | State/province |

### Step 4: Select Shipping Option

Available options determined by cart **region**, **shipping address**, and **shipping profiles**.

| Workflow | Purpose |
|----------|---------|
| `listShippingOptionsForCartWorkflow` | Fetch available options |
| `addShippingMethodToCartWorkflow` | Apply selected shipping option |

### Step 5: Initialize Payment

| Workflow | Purpose |
|----------|---------|
| `createPaymentCollectionForCartWorkflow` | Create payment collection |
| `initializePaymentSessionWorkflow` | Start provider-specific session |

### Step 6: Complete Cart

| Workflow | Purpose |
|----------|---------|
| `completeCartWorkflow` | Convert cart to order |

Completion validates: all items in stock, shipping selected, payment authorized, email set.

> **Fetch live docs** for the exact validation checks performed during cart completion.

## Sales Channels

| Concept | Description |
|---------|-------------|
| Sales Channel | Named storefront scope (e.g., "Web", "Mobile App", "B2B") |
| Publishable API Key | Associates Store API requests with a sales channel |
| Product-Channel Link | Products published to specific channels |

- Each cart belongs to one sales channel
- Store API requests must include `x-publishable-api-key` header
- Products not linked to the cart's channel are unavailable

> **Fetch live docs** for publishable API key configuration and sales channel management.

## Store API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/store/carts` | POST | Create cart |
| `/store/carts/:id` | GET | Retrieve cart |
| `/store/carts/:id` | POST | Update cart (email, address) |
| `/store/carts/:id/line-items` | POST | Add line item |
| `/store/carts/:id/line-items/:item_id` | POST/DELETE | Update/remove line item |
| `/store/carts/:id/shipping-methods` | POST | Add shipping method |
| `/store/carts/:id/payment-collections` | POST | Create payment collection |
| `/store/carts/:id/complete` | POST | Complete checkout |

> **Fetch live docs** for request body shapes and response formats on each route.

## Best Practices

### Cart Management
- Always create carts with a `region_id` -- it determines currency, tax rules, and shipping
- Use `sales_channel_id` to scope product availability per storefront
- Store custom checkout data in cart `metadata` (e.g., gift messages, notes)

### Checkout Flow
- Validate addresses before shipping option selection -- options depend on the destination
- Re-fetch shipping options after address changes (available options may differ)
- Initialize payment sessions only after shipping is selected (total must include shipping)
- Handle cart completion errors gracefully -- display specific validation failures to the user

### Performance
- Use `remoteQuery` to enrich cart data (product details, images) in a single query
- Cache shipping options per region + address combination to reduce API calls

### Security
- Never expose payment session secrets to the client
- Validate cart ownership (customer or anonymous session) on every mutation
- Use publishable API keys to enforce sales channel scoping

Fetch the Medusa v2 cart module documentation and checkout workflow references for exact service method signatures, workflow inputs, and validation rules before implementing.
