---
name: spree-catalog
description: >
  Build and customize Spree's catalog — Products with Variants and
  OptionTypes/OptionValues, Taxonomies and Taxons (nested set), Properties,
  Images via ActiveStorage, multi-currency Prices, the v5.3+ PriceList feature
  for customer/segment overrides, MeiliSearch faceted search (v5.4+), product
  archiving/activation, CSV import/export, and SEO. Use when modeling products,
  customizing the catalog UI, indexing search, or importing inventory.
---

# Spree Catalog

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/architecture — catalog model graph.
2. Web-search `spree meilisearch faceted search v5.4` for the current search backend wiring.
3. Inspect the live `Spree::Product` / `Spree::Variant` source for column names — they shift between minors.
4. Check the latest release notes for any new catalog features (CSV importer scope, Page Builder Product Details Page sections, etc.).
5. For PriceList specifics, fetch the latest pricing-related guide on spreecommerce.org/docs.

## Conceptual Architecture

### Product vs Variant

- **`Product`** — the catalog entity (T-shirt, novel, subscription box). Has a `master_variant`.
- **`Variant`** — the sellable SKU. Even simple products have one master variant; products with options have additional variants per OptionValue combination.

A Variant has:
- A unique SKU
- One `StockItem` per `StockLocation`
- One `Price` per currency
- Zero or more `OptionValue`s defining its position on the option axes

### OptionTypes and OptionValues

```
OptionType: size
  OptionValues: small, medium, large
OptionType: color
  OptionValues: red, blue, black
```

A T-shirt product with `[size, color]` option types has 3 × 3 = 9 variants (or fewer if some combos are unavailable).

### Taxonomies and Taxons

A **Taxonomy** is a category tree (e.g., "Categories", "Collections"). A **Taxon** is a node in that tree using `acts_as_nested_set` (or `awesome_nested_set`). Products are tagged with many Taxons via `Spree::Classification`.

```
Taxonomy: Categories
  ├── Taxon: Apparel
  │     ├── Taxon: Shirts
  │     └── Taxon: Pants
  └── Taxon: Accessories
```

### Properties

Free-form attribute table:
```
Product → ProductProperty(property: Property("Material"), value: "Cotton")
```

Properties show up on the storefront's spec table. Distinct from `Metafield` — properties are user-visible product details; metafields are typically internal custom data.

### Images

Spree uses **ActiveStorage** for images attached to `Variant`s and `Product`s. Variant-level images override product-level for that specific SKU. Image variants (resizing) are computed lazily by ActiveStorage with `libvips` / ImageMagick.

### Pricing Model

- One `Price` row per `(Variant, Currency)`.
- `PriceList` (v5.3+) lets you define an override list scoped to a CustomerGroup, Country, or Store. The pricing resolver picks the right price by precedence: user's CustomerGroup → Store's PriceList → default Price.

### Multi-Currency

Activate currencies on the Store; create one `Price` per Variant per Currency. The storefront and APIs select the right Price based on `Store#default_currency` or the user's selected currency.

### Search Backends

| Backend | Notes |
|---------|-------|
| **MeiliSearch** (v5.4+, recommended) | Faceted, typo-tolerant, fast |
| **Algolia** (community gem) | Hosted, mature |
| **PostgreSQL full-text** | Fallback / dev |

The v5.4 `spree` gem wires MeiliSearch by default when the env vars are present.

### Product Lifecycle

| Event | Cause |
|-------|-------|
| `product.activate` | Product made available |
| `product.archive` | Product hidden (not deleted — preserves order history) |
| `product.out_of_stock` | Inventory hit zero |
| `product.back_in_stock` | Inventory restored |

Use **archive** instead of destroy — preserves order history.

### CSV Import/Export

v5.0+ ships CSV import/export for products, customers, orders. Background-job-driven (Sidekiq), reports errors per row.

## Implementation Guidance

### Creating a Product Programmatically

```ruby
product = Spree::Product.create!(
  name: 'Classic Tee',
  description: '100% cotton',
  price: 19.99,
  shipping_category: Spree::ShippingCategory.first,
  tax_category: Spree::TaxCategory.find_by(name: 'Clothing'),
  available_on: Time.current,
  stores: [Spree::Store.default]
)
```

Then add option types, option values, and variants:

```ruby
size = Spree::OptionType.create!(name: 'tshirt-size', presentation: 'Size')
size.option_values.create!([
  { name: 'small', presentation: 'S' },
  { name: 'medium', presentation: 'M' },
  { name: 'large', presentation: 'L' }
])

product.option_types << size

product.variants.create!(
  sku: 'TEE-S',
  option_values: [size.option_values.find_by(name: 'small')],
  price: 19.99
)
```

### Tagging Products to Taxons

```ruby
taxon = Spree::Taxon.find_by(name: 'Shirts')
product.taxons << taxon
```

### Reading Prices Across Currencies

```ruby
product.master.price_in('USD').amount  # 19.99
product.master.price_in('EUR').display_price  # "€18.50"
```

### Variant-Aware Pricing With PriceList (v5.3+)

```ruby
price = Spree::Pricing::PriceFinder.new(
  variant: variant, store: store, user: user, currency: 'USD'
).call
```

Verify the exact service class name in the version you're on.

### Search Indexing

MeiliSearch indexing is event-driven — `product.updated`, `product.activate`, etc., enqueue background jobs. Force reindex:

```bash
bin/rails spree:search:reindex
```

Verify the exact rake task name in the current release.

### CSV Import

```bash
bin/rails console
> Spree::ImportCsvJob.perform_later('products', file_path: '/path/to/products.csv')
```

Or via admin: Products → Import. Verify the job class name in the live code.

### Storefront Product Page

In the Next.js storefront, the product page is built from API v3 calls:

```typescript
// Server component
const product = await spree.products.find(slug, { include: 'variants,images,taxons' });
```

(Pseudo — verify against `@spree/sdk` docs.)

### Common Pitfalls

- **Destroying products instead of archiving** — breaks order history and reports.
- **Forgetting per-currency Prices** — variants without a Price in the current currency become invisible.
- **Adding option types after variants exist** — new option types invalidate existing variant uniqueness; either rebuild variants or use a migration script.
- **Reindex storms** — bulk updates fire many `product.updated` events; throttle the search-indexing subscriber for batch operations.
- **Master variant edits not reflecting on storefront** — caches. Bust with `Spree::Cache.clear` or version-bumped cache keys.

Always verify model relationships and column names against the live `spree` gem source — catalog modeling evolves more than the order graph.
