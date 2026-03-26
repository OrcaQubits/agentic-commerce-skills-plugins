---
name: saleor-catalog
description: Manage the Saleor catalog — products, variants, product types, categories, collections, media, and warehouse stock. Use when working with Saleor product data.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Catalog Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io products variants product types` for product model and GraphQL operations
2. Web-search `site:docs.saleor.io categories collections` for category tree and collection management
3. Web-search `site:docs.saleor.io warehouse stock allocation` for inventory and warehouse operations
4. Fetch `https://docs.saleor.io/docs/developer/products` and review Product, ProductType, and ProductVariant schemas
5. Web-search `site:docs.saleor.io product media images` for media upload and assignment patterns
6. Fetch `https://docs.saleor.io/docs/developer/channels` and review channel-aware product visibility

## Product Hierarchy

| Level | Contains |
|-------|----------|
| ProductType | Template: defines product and variant attributes, shipping/digital flags |
| Product | Name, description, slug, category, collections, media |
| ProductVariant | SKU, name, channel listings (price), stock (per warehouse), variant attributes |

### Product Status

| Status | Description |
|--------|-------------|
| `DRAFT` | Product is not visible to customers; work in progress |
| `ACTIVE` | Product is published and available for purchase (per channel listing) |

> Products require a channel listing to be visible in a given channel. Status alone does not control storefront visibility.

## Product Types

A ProductType serves as a template that defines the structure for a group of products:

| Concept | Purpose |
|---------|---------|
| Product attributes | Shared attributes across all products of this type (e.g., Brand, Material) |
| Variant attributes | Attributes that differ per variant (e.g., Size, Color) |
| `isShippingRequired` | Whether products of this type need physical shipping |
| `isDigital` | Whether this type represents digital goods |
| `hasVariants` | Whether products support multiple variants |
| Weight | Default weight for products of this type |

### Key Product Type Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create type | `productTypeCreate` | Define name, attributes, shipping flag |
| Update type | `productTypeUpdate` | Modify existing type settings |
| Delete type | `productTypeDelete` | Removes type (fails if products exist) |
| Assign attribute | `productAttributeAssign` | Add attribute to product type |
| Unassign attribute | `productAttributeUnassign` | Remove attribute from type |

## Variant Model

Each ProductVariant represents a purchasable unit within a product:

| Field | Description |
|-------|-------------|
| `sku` | Stock Keeping Unit (unique identifier) |
| `name` | Display name for the variant |
| `trackInventory` | Whether stock levels are tracked |
| `weight` | Override weight from product type |
| `preorder` | Preorder settings (end date, global threshold) |
| `quantityLimitPerCustomer` | Maximum purchase quantity per customer |

### Channel Listings for Variants

Variants have per-channel pricing. Each `ProductVariantChannelListing` holds:

| Field | Description |
|-------|-------------|
| `price` | Selling price in the channel currency |
| `costPrice` | Cost of goods (for margin calculations) |
| `channel` | The channel this listing belongs to |

## Categories

Categories form a nested tree structure for organizing products:

| Feature | Detail |
|---------|--------|
| Structure | Single-root tree with unlimited nesting depth |
| Assignment | Each product belongs to exactly one category |
| SEO | Categories support `seoTitle` and `seoDescription` |
| Background image | Optional image for category pages |
| Slug | URL-friendly identifier |

### Key Category Mutations

| Operation | Mutation |
|-----------|----------|
| Create | `categoryCreate` (set `parent` for nesting) |
| Update | `categoryUpdate` |
| Delete | `categoryDelete` |

## Collections

Collections are curated groupings of products, independent of the category tree:

| Feature | Detail |
|---------|--------|
| Purpose | Marketing-driven groupings (e.g., "Summer Sale", "Best Sellers") |
| Assignment | Many-to-many; a product can belong to multiple collections |
| Channel listing | Collections must be published per channel |
| Background image | Optional image for collection pages |
| SEO | Supports `seoTitle` and `seoDescription` |

### Key Collection Mutations

| Operation | Mutation |
|-----------|----------|
| Create | `collectionCreate` |
| Add products | `collectionAddProducts` |
| Remove products | `collectionRemoveProducts` |
| Delete | `collectionDelete` |

## Product Media

Products support images and videos:

| Media Type | Upload Method |
|------------|---------------|
| Images | `productMediaCreate` with `image` file upload |
| URLs | `productMediaCreate` with `mediaUrl` for external images or videos |
| Reorder | `productMediaReorder` to set display order |
| Delete | `productMediaDelete` to remove media |

> Images are served through Saleor's thumbnail system. Request specific sizes using the `thumbnail` field on `ProductMedia` with `size` parameter.

## Key GraphQL Queries and Mutations

### Admin API

| Operation | Query / Mutation | Notes |
|-----------|-----------------|-------|
| List products | `products` | Supports filtering, sorting, and channel |
| Get product | `product` | By ID or slug; channel required for pricing |
| Create product | `productCreate` | Requires productType, name, and category |
| Update product | `productUpdate` | Partial updates supported |
| Delete product | `productDelete` | Removes product and all variants |
| Create variant | `productVariantCreate` | Requires product ID, attributes, SKU |
| Bulk create variants | `productVariantBulkCreate` | Create multiple variants at once |
| Update stock | `productVariantStocksUpdate` | Set stock quantities per warehouse |

### Store API (channel-scoped)

| Operation | Query | Notes |
|-----------|-------|-------|
| List products | `products(channel: "default")` | Only published, available products |
| Get product | `product(slug: "...", channel: "...")` | Returns pricing for the channel |
| Search | `products(filter: {search: "..."})` | Full-text search on name and description |
| By category | `products(filter: {categories: [...]})` | Filter by category IDs |
| By collection | `collection(slug: "...")` `{ products }` | Products within a collection |

> **Fetch live docs** for exact filter fields and sorting options -- these evolve across Saleor versions.

## Warehouse and Stock

| Concept | Description |
|---------|-------------|
| Warehouse | Physical location where stock is held |
| Stock | Per-variant, per-warehouse quantity |
| Allocation | Reserved stock for unfulfilled orders |
| Available quantity | `stock.quantity - stock.allocations` |

### Stock Mutations

| Operation | Mutation |
|-----------|----------|
| Update stocks | `productVariantStocksUpdate` |
| Create stocks | `productVariantStocksCreate` |
| Delete stocks | `productVariantStocksDelete` |

## Best Practices

- Always create ProductTypes before products -- they define the attribute schema
- Use channel listings to control visibility and pricing per channel
- Assign products to exactly one category and use collections for cross-cutting groupings
- Use `productVariantBulkCreate` for efficiency when adding multiple variants
- Track inventory at the warehouse level for multi-location fulfillment
- Set `trackInventory` to `true` for physical goods to prevent overselling
- Use slugs for storefront URLs and SEO-friendly navigation
- Optimize images before upload -- Saleor generates thumbnails but original size affects storage
- Always pass `channel` when querying from the storefront to get correct pricing and availability

Fetch the Saleor product and catalog documentation for exact mutation inputs, attribute types, and channel listing patterns before implementing.
