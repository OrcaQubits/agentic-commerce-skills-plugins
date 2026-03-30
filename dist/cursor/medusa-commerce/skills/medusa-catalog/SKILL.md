---
name: medusa-catalog
description: >
  Manage the Medusa v2 catalog — products, variants, options, collections,
  categories, tags, and product metadata. Use when working with Medusa product
  data.
---

# Medusa v2 Catalog Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com product module` for product data model and service methods
2. Web-search `site:docs.medusajs.com product variant option` for variant/option relationships
3. Web-search `site:docs.medusajs.com collection category` for collection and category APIs
4. Fetch `https://docs.medusajs.com/resources/references/product` and review the `IProductModuleService` interface
5. Web-search `medusajs v2 product workflow 2026` for latest product-related workflow steps
6. Web-search `site:docs.medusajs.com admin product api route` for Admin API product endpoints

## Product Model

### Hierarchy

| Entity | Relationship | Key Fields |
|--------|-------------|------------|
| **Product** | Root | title, subtitle, description, handle, status |
| **Options** | Product → many | Size, Color, Material (with OptionValues) |
| **Variants** | Product → many | sku, barcode, ean, upc, hs_code |
| **Prices** | Variant → many (link) | Via Pricing Module link |
| **Inventory** | Variant → one (link) | Via Inventory Module link |
| **Images** | Product → many | url, rank |
| **Tags** | Product ↔ many | many-to-many labels |
| **Categories** | Product ↔ many | Nested tree (parent_category_id) |
| **Collections** | Product ↔ many | Curated groupings |
| **Metadata** | On all entities | JSONB key-value store |

### Product Status

| Status | Meaning |
|--------|---------|
| `draft` | Not visible to customers |
| `proposed` | Submitted for review |
| `published` | Visible on storefront |
| `rejected` | Review rejected |

### Module Architecture

Medusa v2 uses a **modular architecture** where the Product Module is decoupled from pricing, inventory, and other concerns through **Module Links**.

```
Product Module ──link──> Pricing Module
Product Module ──link──> Inventory Module
Product Module ──link──> Sales Channel Module
```

> **Fetch live docs** for exact link definitions and how to query across linked modules using `remoteQuery`.

## Variants and Options

### Relationship Model

| Entity | Cardinality | Description |
|--------|-------------|-------------|
| Product -> Option | one-to-many | Each product defines its own options |
| Option -> OptionValue | one-to-many | Each option has enumerated values |
| Variant -> OptionValue | many-to-many | Each variant selects one value per option |
| Variant -> Price | one-to-many | Via Pricing Module link |
| Variant -> InventoryItem | one-to-one | Via Inventory Module link |

### Key Service Methods

| Operation | Method | Notes |
|-----------|--------|-------|
| Create product | `productModuleService.createProducts()` | Accepts variants, options inline |
| Update product | `productModuleService.updateProducts()` | Partial updates supported |
| Delete product | `productModuleService.deleteProducts()` | Cascades to variants |
| List products | `productModuleService.listProducts()` | Supports filters, pagination |
| Retrieve product | `productModuleService.retrieveProduct()` | By ID with relations |
| Create variants | `productModuleService.createProductVariants()` | Link option values |
| Update variants | `productModuleService.updateProductVariants()` | Partial update |

> **Fetch live docs** for the exact method signatures and filter/select/relations options available on each service method.

### Minimal Workflow Pattern

```ts
// Skeleton: create product with variants
// Fetch live docs for createProductsWorkflow input shape
import { createProductsWorkflow } from "@medusajs/medusa/core-flows"

const { result } = await createProductsWorkflow(container)
  .run({ input: { products: [/* ... */] } })
// Fetch live docs for CreateProductsWorkflowInput
```

## Collections

Logical groupings of products:
- Each collection has a `title`, `handle`, and optional `metadata`
- Products can belong to multiple collections
- Managed via `productModuleService.createProductCollections()`
- Useful for seasonal promotions, curated sets, and storefront navigation

## Categories

Hierarchical classification with nesting:

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `handle` | URL-friendly slug |
| `parent_category_id` | Reference to parent (null for root) |
| `rank` | Sort order among siblings |
| `is_active` | Visibility flag |
| `is_internal` | Hidden from storefront |

Categories form a **tree structure** — unlimited depth. Use `category_children` relation to traverse.

> **Fetch live docs** for category service methods and nested tree query patterns.

## Tags

Simple labels for filtering and organization:
- Stored as separate entities with a `value` field
- Many-to-many relationship with products
- Queryable via `listProductTags()`
- Use for lightweight cross-cutting classification (e.g., "new-arrival", "sale")

## Product Metadata

JSONB key-value store on every product entity:
- Available on `Product`, `ProductVariant`, `ProductOption`, and `ProductCollection`
- Schema-free — store arbitrary JSON values
- Queryable via filters: `metadata: { key: value }`
- Use for custom attributes that don't warrant a dedicated field

## Admin API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/admin/products` | GET | List products with filters |
| `/admin/products` | POST | Create product |
| `/admin/products/:id` | GET | Retrieve single product |
| `/admin/products/:id` | POST | Update product |
| `/admin/products/:id` | DELETE | Delete product |
| `/admin/collections` | GET/POST | Manage collections |
| `/admin/categories` | GET/POST | Manage categories |

> **Fetch live docs** for query parameters, request body shapes, and pagination patterns on each route.

## Store API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/store/products` | GET | List published products |
| `/store/products/:id` | GET | Retrieve single product |
| `/store/collections` | GET | List collections |
| `/store/categories` | GET | List active categories |

Store routes respect **sales channel** and **publishable API key** scoping.

## Best Practices

### Data Modeling
- Use **Options + Variants** for product variations — do not duplicate products
- Leverage **categories** for hierarchical navigation and **collections** for curated groupings
- Store custom attributes in `metadata` rather than creating custom modules for simple data

### Performance
- Use `select` and `relations` parameters to fetch only needed fields
- Use `remoteQuery` for cross-module queries (product + pricing + inventory)
- Paginate large catalogs — never fetch all products without `limit` and `offset`

### Workflows
- Use `createProductsWorkflow` and `updateProductsWorkflow` for transactional operations
- Workflows handle cross-module orchestration (linking prices, inventory) automatically
- Custom product logic should extend workflows via hooks, not bypass them

### Module Isolation
- Never import Product Module internals directly — use the service interface
- Cross-module data access must go through links and `remoteQuery`
- Respect module boundaries when building custom features

Fetch the Medusa v2 product module documentation and workflow references for exact service method signatures, workflow inputs, and remote query patterns before implementing.
