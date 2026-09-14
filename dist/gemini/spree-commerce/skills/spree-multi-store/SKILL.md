---
name: spree-multi-store
description: >
  Configure Spree for multi-store and multi-region commerce — one Rails install
  running many `Store` records, the v5.4+ `Market` model (currency + locale +
  payment methods + shipping per region), what's shared vs per-store
  (products+inventory+customers shared; orders+payments+themes per-store), the
  Marketplace module (Enterprise — vendors/commission/payouts via Stripe
  Connect), and the Multi-tenant SaaS model. Use when planning a multi-brand or
  multi-region Spree deployment.
---

# Spree Multi-Store, Markets, Marketplace

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/stores for the multi-store data model.
2. Fetch https://spreecommerce.org/docs/use-case/marketplace/model for the marketplace use case (Enterprise).
3. Fetch https://spreecommerce.org/docs/use-case/multi-tenant/multi-tenant-model for SaaS-style isolation.
4. Check the v5.4 announcement for the `Market` model details (https://spreecommerce.org/announcing-spree-commerce-5-4/).
5. Inspect `Spree::Store` and `Spree::Market` source for current column shapes and associations.

## Conceptual Architecture

### Multi-Store: One Install, Many Brands

A single Spree app serves many `Store` records, each with:
- Its own domain (`store.foo.com`, `store.bar.com`)
- Its own theme, CMS pages, blog
- Its own legal/policy text
- Its own subset of products (via `Spree::Store#products`)
- Its own orders/payments/shipments
- Its own integrations (Stripe account, Klaviyo list, etc.)

### What's Shared Across Stores

- **Products** and their **inventory** (StockItem)
- **Customers** (User accounts)
- **Shipping methods** and **payment gateways** (each can be enabled per store)
- **Admin users** and roles
- **Markets** (v5.4+)
- **Tax rates** (per Zone, not per Store)
- **Promotions** (can be scoped per-store, but the engine is shared)

### What's Per-Store

- **Orders** — `Order#store_id` always set
- **Payments / Refunds / Reimbursements** — inherit from order's store
- **Store credits / Gift cards**
- **Themes / CmsPages / Blogs / FAQ**
- **Logo / brand / typography**
- **Domain & SSL**
- **Currency** (default; v5.4+ uses Markets)
- **SEO settings**
- **Webhook endpoints**

### Resolving the Current Store

Spree middleware resolves `current_store` from:
1. Request domain (matches `Store#url`)
2. Session / cookie override (for previewing)
3. Fallback to `Spree::Store.default`

In controllers and views:

```ruby
current_store              # the resolved Spree::Store
current_store.url
current_store.default_currency
```

**Always scope queries** by `current_store` in customer-facing code.

### The `Market` Model (v5.4+)

Markets bundle regional configuration:

```
Market: "US"
├── currencies: [USD]
├── locales: [en-US, es-US]
├── countries: [US]
├── payment_methods: [stripe_us, paypal_us]
├── shipping_methods: [ups_us, fedex_us]
└── tax_handling: inclusive | exclusive

Market: "EU"
├── currencies: [EUR]
├── locales: [de, fr, it, es]
├── countries: [DE, FR, IT, ES, NL, BE, ...]
├── payment_methods: [stripe_eu, sepa, klarna_eu]
├── shipping_methods: [dhl_eu]
└── tax_handling: inclusive
```

URL routing pattern: `/us/en/`, `/de/de/`, `/eu/fr/`. The storefront detects market by domain / path / cookie.

### Marketplace (Enterprise Module)

Multi-vendor sites add the **Marketplace module** (Enterprise Edition, official as of v5):

```
Vendor (Marketplace seller)
├── Products
├── Stock locations
├── Payouts (via Stripe Connect)
├── Commission rate
└── Account dashboard (separate from main admin)

Customer Order
├── LineItems split across Vendors
├── Marketplace payment → fan-out to Vendor accounts
└── Commission deducted to platform
```

The community gem `spree_multi_vendor` exists but is **not the recommended path for v5**. Use the Enterprise marketplace module.

### Multi-Tenant (Enterprise Module)

For SaaS Spree where each tenant gets isolated data (separate stores, separate users, no cross-tenant visibility). Built on top of multi-store with stricter scoping at every query.

## Implementation Guidance

### Creating a Second Store

```ruby
Spree::Store.create!(
  name: 'EU Store',
  url: 'eu.example.com',
  mail_from_address: 'eu@example.com',
  default_currency: 'EUR',
  default_locale: 'de',
  default: false
)
```

In admin, copy products from the default store via the bulk action (admin → Products → bulk → "Assign to store").

### Sharing vs Splitting Products

```ruby
# A product can be in multiple stores
product.stores << eu_store
product.stores << us_store

# Query per-store
us_store.products.active
```

Pricing per market:

```ruby
variant.prices.create!(amount: 19.99, currency: 'USD')
variant.prices.create!(amount: 18.50, currency: 'EUR')
```

### Querying Safely

Bad (leaks across stores):
```ruby
Spree::Order.complete.where('total > ?', 100)
```

Good:
```ruby
current_store.orders.complete.where('total > ?', 100)
```

For admin reports that intentionally span stores, scope explicitly:
```ruby
Spree::Order.where(store_id: [us_store.id, eu_store.id])
```

### Setting Up Markets (v5.4+)

```ruby
us_market = Spree::Market.create!(
  name: 'United States',
  default_currency: 'USD',
  default_locale: 'en-US',
  countries: Spree::Country.where(iso: 'US'),
  payment_methods: Spree::PaymentMethod.where(name: ['Stripe US', 'PayPal US']),
  shipping_methods: Spree::ShippingMethod.where(name: 'UPS US')
)
```

(Verify exact API — `Market` is new in v5.4 and the helpers may differ.)

### Headless Multi-Region Routing

The Next.js storefront routes by market:

```
/us/en/products/classic-tee
/de/de/produkte/classic-tee
```

The storefront's market resolution forwards `Spree::Market#id` to the API via header or path.

### Multi-Store Webhooks

Each store has its own Webhook endpoints. Subscribing to `order.completed` for one store doesn't fire for orders in another. Configure separately per store.

### Marketplace Vendor Management

Enterprise marketplace adds:
- Vendor onboarding flow with Stripe Connect Express / Standard
- Per-vendor admin dashboard
- Commission calculation engine
- Payout scheduler
- Vendor product approval workflow

Read the Marketplace use-case doc — the implementation hooks are different from base Spree.

### Common Pitfalls

- **Naive queries leak across stores** — `Spree::Order.all` returns every store's orders. Lint for this in code review.
- **Forgetting `default: false`** on new stores — only one store should be default.
- **Shared products with diverging pricing** — easy to miss a currency Price when adding a new market.
- **Webhook secrets reused across stores** — security risk; generate fresh per store.
- **Domain-based store resolution breaks in local dev** — use `Host` header override or environment-based `Spree.config.default_store_url`.
- **Marketplace integration without Stripe Connect** — payouts require Connect; you can't roll your own with bank transfer.
- **Multi-currency without per-market shipping** — customer gets quoted USD price + USD shipping when their market is EU. Configure Markets fully.

Always verify multi-store fields and Market associations against the live source — these are among the most rapidly-evolving subsystems in v5.4+.
