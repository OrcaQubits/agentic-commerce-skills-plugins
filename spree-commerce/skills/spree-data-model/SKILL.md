---
name: spree-data-model
description: Navigate Spree's canonical data model — the Catalog (Product/Variant/OptionType/Taxon/Property/Metafield), Pricing (Price/PriceList), Order graph (Order/LineItem/Adjustment/Shipment/Payment/PaymentSession/Refund/Reimbursement), Inventory (StockLocation/StockItem/StockMovement), Shipping (ShippingMethod/Zone), Promotions, Identity (User/Role/Address/StoreCredit/GiftCard), Taxes, and the v5.4+ Markets + Store multi-region model. Use when designing a feature that touches Spree models, writing decorators, or building admin/storefront UIs.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Spree Data Model

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/architecture for the current model graph.
2. Fetch https://spreecommerce.org/docs/developer/core-concepts/orders for the Order/LineItem/Payment/Shipment graph and state.
3. Fetch https://spreecommerce.org/docs/developer/core-concepts/metafields for Metafield (v5+).
4. Fetch https://spreecommerce.org/docs/developer/core-concepts/stores for `Store` and `Market`.
5. Inspect the live `spree` gem source on GitHub for current column names — Spree adds columns between minors.

## Conceptual Architecture

### Catalog

| Model | Purpose | Notes |
|-------|---------|-------|
| `Product` | Top-level catalog item | Has a master `Variant`; many `Image`s, `Property`s, `Taxon`s |
| `Variant` | Concrete SKU | Has `OptionValue`s, `Price`s per currency, `StockItem`s |
| `OptionType` / `OptionValue` | Variant axes (size, color) | An OptionType has many OptionValues |
| `Property` / `ProductProperty` | Free-form spec table | "Material: cotton", "Weight: 250g" |
| `Taxonomy` / `Taxon` | Category trees | `Taxon` is the nested-set node |
| `Image` / `Asset` | Media | Uses ActiveStorage |
| `Metafield` | Custom data on any model (v5+) | Like Shopify metafields |

### Pricing

| Model | Purpose |
|-------|---------|
| `Price` | One row per (Variant × Currency) |
| `PriceList` (v5.3+) | Override prices for a customer group, store, or country |
| `Calculator` | Polymorphic calculator class for shipping/promotion/tax math |

### Order Graph

```
Order
├── LineItem (one per Variant)
│   └── Adjustment[]
├── Shipment (one per StockLocation involved)
│   ├── InventoryUnit
│   ├── ShippingRate
│   └── selected ShippingRate
├── Payment[]
│   ├── PaymentSession (v5.4+, provider-agnostic envelope)
│   └── source (CreditCard, StoreCredit, etc.)
├── Adjustment[] (order-level)
├── Address (bill_address, ship_address)
└── User (optional — guest orders allowed)
```

Plus return-flow models: `ReturnAuthorization` → `CustomerReturn` → `Reimbursement` → `Refund`.

### Inventory

- `StockLocation` — physical / logical warehouse
- `StockItem` — count of a Variant in a StockLocation
- `StockMovement` — append-only ledger of stock changes
- `StockTransfer` — moves stock between locations

### Shipping

- `ShippingMethod` — names a way to ship (UPS Ground, Express)
- `ShippingRate` — computed cost option on a Shipment
- `ShippingCategory` — categorize products by shipping needs
- `Zone` / `ZoneMember` — countries/states a method ships to

### Promotions

`Promotion` + `PromotionRule` + `PromotionAction` + `CouponCode` resulting in `Adjustment`s.

### Identity

| Model | Notes |
|-------|-------|
| `User` | Spree's customer / admin model (Devise-backed in v5+) |
| `Role` | Permissions — `admin`, `customer`, custom |
| `Address` | Bill / ship address, optionally tied to a user |
| `StoreCredit` | Balance on a user, usable as payment |
| `GiftCard` | Tradeable balance, redeemable as payment method |
| `CustomerGroup` | Segments for pricing / promotions |
| `Invitation` | Invite to an account |
| `ApiKey` | Per-user API key for v3 admin API |

### Taxes

- `TaxCategory` — assignable to products (e.g., "Clothing", "Books")
- `TaxRate` — percentage by Zone + TaxCategory

### Multi-Store / Region

| Model | Purpose |
|-------|---------|
| `Store` | One install → many stores, each with own domain/theme/policies |
| `Market` (v5.4+) | Bundles currency + locale + payment methods + shipping per region |
| `CmsPage` | Content pages per store |
| `Theme` | Storefront theme per store |

**Shared across stores**: products, inventory, customers, shipping methods, payment gateways, Markets, admin roles.
**Per-store**: orders, shipments, payments, refunds, store credits, gift cards, themes, blogs, pages, integrations.

### Spree::Metafield (v5+)

A flexible custom-data system attached to any model. Replaces ad-hoc decorators for "I just need one extra field." Use this before adding a column.

### prefixed IDs (v5.4+)

API v3 exposes prefixed IDs (`prod_…`, `ord_…`, `var_…`, `usr_…`, `pay_…`) — these are stable string identifiers separate from the database `id`. Models gain a `prefixed_id` method.

### Polymorphic Adjustments

`Adjustment` belongs to an `adjustable` (Order, LineItem, Shipment) and a `source` (PromotionAction, TaxRate, manual). When sums change, run `order.update_totals` or use `Spree::OrderUpdater` (or its swappable replacement via `Spree::Dependencies`).

## Implementation Guidance

### Querying Safely in Multi-Store

```ruby
# WRONG — leaks across stores
Spree::Order.complete

# RIGHT — always scope by current_store in customer-facing code
current_store.orders.complete

# Admin-side: admin sees all stores by default, but check role scoping
Spree::Order.where(store_id: current_store.id)
```

### Reading Variants With Their Pricing

```ruby
variant = Spree::Variant.find(...)
variant.price_in('USD').amount    # raw decimal
variant.price_in('USD').display_price  # formatted "$19.99"
variant.amount_in('USD')          # alias for price_in(currency).amount
```

For v5.3+ PriceList overrides:

```ruby
price = Spree::Pricing::PriceFinder.new(variant: variant, store: store, user: user, currency: 'USD').call
```

(Verify the live API — pricing service objects are routinely renamed.)

### Order Totals

Don't recompute totals manually. Use the order updater service:

```ruby
Spree::OrderUpdater.new(order).update
# or via Dependencies
Spree::Dependencies.order_updater.call(order)
```

### Adding Custom Data Without a Decorator

Prefer Metafield over adding columns:

```ruby
product.metafields.create!(
  namespace: 'my_app',
  key: 'launch_date',
  value: '2026-06-01',
  value_type: 'string'
)
product.metafield('my_app', 'launch_date')
```

Verify the exact API in the live metafields doc.

### Designing for the Order Graph

- **One Order has many Shipments** when items come from different `StockLocation`s.
- **One Shipment has many InventoryUnit**s — one per unit sold.
- **Payments are not necessarily 1:1 with orders** — split tender (store credit + card) creates multiple Payments.
- **PaymentSessions (v5.4+) wrap a Payment** for provider-agnostic checkout flows.

### Common Pitfalls

- **Modifying Order totals directly** — always recompute via the updater service.
- **Adding columns when a Metafield would do** — Metafields don't need migrations and survive upgrades.
- **Ignoring `Store#default`** — most APIs default to it, but explicit scoping is safer.
- **Adjustments on canceled lines** — when a line item is removed mid-order, adjustments tied to it need explicit cleanup. Use service objects, not raw `delete`.
- **Assuming `Variant.is_master` ordering** — the master variant is always present; option-variant ordering follows position columns.

Always cross-check column names and relationships against the live source — the data model evolves between minor releases.
