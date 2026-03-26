---
name: medusa-pricing
description: Configure Medusa v2 pricing — pricing module, price lists with rules, currencies, tax calculation, regions, and promotion campaigns. Use when setting up pricing and discounts.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Pricing and Promotions

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com pricing module` for pricing data model and service methods
2. Web-search `site:docs.medusajs.com price list rules` for conditional pricing configuration
3. Web-search `site:docs.medusajs.com promotion module` for promotion types and rules
4. Fetch `https://docs.medusajs.com/resources/references/pricing` and review the `IPricingModuleService` interface
5. Web-search `medusajs v2 tax module region 2026` for latest tax calculation and region setup

## Pricing Module Architecture

### Entity Relationships

```
PriceSet
├── Prices[]
│   ├── amount (integer, minor units)
│   ├── currency_code
│   ├── min_quantity, max_quantity
│   └── Rules[] (region_id, customer_group_id)
└── MoneyAmounts[]
```

### Module Links

```
Product Module (variant) ──link──> Pricing Module (price set)
Region Module ──link──> Pricing Module (price context)
Customer Group ──link──> Pricing Module (group pricing)
```

> **Fetch live docs** for exact link definitions and how price sets connect to product variants.

## Price Calculation

### Resolution Flow

```
Customer Request
  └─> Context: { region_id, currency_code, customer_group_id }
        └─> Pricing Module: find best matching price
              ├── Check price lists (sale/override) with rules
              ├── Check variant prices with matching rules
              └─> Return lowest applicable price
```

### Pricing Context

| Context Field | Source | Effect |
|---------------|--------|--------|
| `region_id` | Cart region | Filters by region-specific prices |
| `currency_code` | Region default | Determines currency |
| `customer_group_id` | Customer profile | Enables group-specific pricing |
| `quantity` | Line item qty | Enables quantity-based tiers |

## Price Lists

### Types

| Type | Description | Use Case |
|------|-------------|----------|
| `sale` | Discounted price (lower than default) | Seasonal sales, flash deals |
| `override` | Replaces default price entirely | B2B/wholesale pricing |

### Configuration

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Display name |
| `status` | `active`/`draft` | Visibility |
| `type` | `sale`/`override` | Price list behavior |
| `starts_at` / `ends_at` | datetime | Scheduled activation window |
| `rules` | object | Customer group, region conditions |

### Key Service Methods

| Operation | Method |
|-----------|--------|
| Create price set | `pricingModuleService.createPriceSets()` |
| Add prices | `pricingModuleService.addPrices()` |
| Create price list | `pricingModuleService.createPriceLists()` |
| Calculate price | `pricingModuleService.calculatePrices()` |

> **Fetch live docs** for the full list of rule attributes and how to combine multiple rules.

## Regions and Currencies

### Region Model

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name (e.g., "North America") |
| `currency_code` | string | Default currency (e.g., "usd") |
| `countries` | relation | Countries in this region |
| `automatic_taxes` | boolean | Auto-calculate taxes |

### Region-Currency Mapping

| Region | Currency | Countries |
|--------|----------|-----------|
| North America | `usd` | US, CA |
| Europe | `eur` | DE, FR, IT, ES... |
| United Kingdom | `gbp` | GB |

- Each region has exactly **one** default currency
- Prices stored in **minor units** (cents): $10.00 = `1000`

## Tax Calculation

| Concept | Description |
|---------|-------------|
| Tax Region | Geographic area with tax rules |
| Tax Rate | Percentage rate for a tax region |
| Tax Line | Calculated tax for a line item |
| Tax Provider | External service (TaxJar, Avalara) or built-in |

### Tax Configuration

| Setting | Options | Description |
|---------|---------|-------------|
| `automatic_taxes` | `true`/`false` | Auto-calculate vs manual |
| Tax-inclusive pricing | region setting | Prices include or exclude tax |
| Tax provider | built-in or custom | Calculation engine |

> **Fetch live docs** for tax provider interface and tax-inclusive pricing configuration.

## Promotion Module

### Promotion Types

| Type | Description | Example |
|------|-------------|---------|
| `standard` | Rule-based discounts | 10% off orders over $100 |
| `buyget` | Buy-X-Get-Y promotions | Buy 2 get 1 free |

### Promotion Structure

```
Promotion
├── code (optional coupon), type, is_automatic
├── ApplicationMethod
│   ├── type (percentage, fixed)
│   ├── allocation (each, across)
│   └── target_type (items, shipping, order)
└── Rules[] (attribute, operator, values)
```

### Application Method Types

| Type | Allocation | Description |
|------|------------|-------------|
| `percentage` | `each` | % off each qualifying item |
| `percentage` | `across` | % off total of qualifying items |
| `fixed` | `each` | Fixed amount off each item |
| `fixed` | `across` | Fixed amount off total |

### Promotion Rules

| Rule Attribute | Operator | Description |
|----------------|----------|-------------|
| `customer_group_id` | `in` | Customer group membership |
| `currency_code` | `eq` | Specific currency |
| `product_id` | `in` | Specific products |
| `product_collection_id` | `in` | Specific collections |

> **Fetch live docs** for the complete list of rule attributes and how promotions stack.

### Key Service Methods

| Operation | Method |
|-----------|--------|
| Create promotion | `promotionModuleService.createPromotions()` |
| Compute actions | `promotionModuleService.computeActions()` |
| List promotions | `promotionModuleService.listPromotions()` |

## Best Practices

### Pricing Strategy
- Store all prices in **minor units** (cents/pence) — never use decimals
- Create region-specific prices for multi-currency stores
- Use `sale` price lists for temporary discounts and `override` for permanent B2B pricing

### Promotions
- Use `is_automatic: true` for site-wide promotions (no coupon code needed)
- Combine rules for targeted promotions (e.g., VIP customers + specific collections)
- Test promotion stacking behavior — multiple promotions may apply to the same cart

### Tax and Performance
- Enable `automatic_taxes` and configure tax regions for each country
- Decide on tax-inclusive vs tax-exclusive pricing per region at setup time

Fetch the Medusa v2 pricing, promotion, and tax module documentation for exact service method signatures, rule configuration, and price resolution logic before implementing.
