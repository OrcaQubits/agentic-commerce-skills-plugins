---
name: sf-catalog
description: Manage Salesforce Commerce catalogs — B2C (Business Manager catalogs, categories, products, pricing books, promotions, search indexes) and B2B (Product2, Pricebook2, PricebookEntry, volume discounts, entitlements). Use when working with product data across either platform.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-catalog

## Before Writing Code

**Fetch live docs before implementing catalog features.**

1. Web-search: "Salesforce B2C Commerce Cloud catalog management documentation 2026"
2. Web-search: "Salesforce B2B Commerce Product2 ProductCatalog documentation 2026"
3. Web-search: "Salesforce B2C Commerce price books promotions documentation 2026"
4. Web-search: "Salesforce B2B Commerce buyer groups entitlements 2026"
5. Web-fetch the SFCC Business Manager catalog structure reference
6. Web-fetch the Salesforce Product2 and Pricebook2 object reference

## Conceptual Architecture

### B2C Commerce Catalog Model

```
Master Catalog (shared across sites)
  -> Site Catalog (site-specific subset)
    -> Categories (hierarchical tree)
      -> Products (assigned to categories)
```

**Catalog Hierarchy:**
- **Master Catalog**: Contains all products, shared across multiple sites
- **Site Catalog**: Site-specific subset; inherits products from master
- **Categories**: Hierarchical navigation tree; products have one primary category, multiple secondary
- **Catalog Assignment**: Products linked to catalogs via catalog-product relationships

**Product Type Taxonomy:**

| Product Type | Description |
|---|---|
| Standard Product | Simple product without variations |
| Master Product | Parent defining shared attributes |
| Variation Group | Optional grouping layer between master and variations |
| Variation Product | Specific SKU with unique variation attributes (color, size) |
| Product Set | Curated collection (e.g., "Complete the Look") |
| Product Bundle | Package of products sold together at bundle price |

**Attribute System:**
- Products carry standard attributes (name, description, price, images) and custom attributes
- Searchable attributes are indexed for full-text search and faceted navigation
- Variation attributes (color, size) define the master-to-variation relationship
- Custom attributes defined in Business Manager or via XML import

**Pricebook Hierarchy:**

| Concept | Detail |
|---|---|
| Price Book | Container for prices; supports multiple currencies |
| List Price | Base price (MSRP) |
| Sale Price | Promotional price, time-bound |
| Customer Group Pricing | Segment-specific prices |
| Price Book Inheritance | Child books inherit from parent; override selectively |
| Price Tiers | Quantity-based pricing rules |

**Promotions Engine:**
- Product promotions (discount on specific products/categories)
- Order promotions (cart-level, e.g., $10 off $50)
- Shipping promotions (free/discounted shipping)
- Qualifiers: cart total, product quantity, customer group
- Exclusivity rules control stacking; coupon codes single-use or multi-use

**Search and Refinements:**
- Proprietary search index managed by Salesforce
- Searchable attributes indexed for faceted navigation
- Sorting rules: relevance, price, newest, custom
- Search suggestions (typeahead), did-you-mean, search redirects

**Import/Export:**
- Bulk XML import via Business Manager or jobs; strict XSD schema
- Delta import for incremental updates (performance optimization)
- Import modes: replace, update, or delete existing data

### B2B Commerce Catalog Model

```
ProductCatalog (B2B container)
  -> ProductCategory (categories)
    -> Product2 (standard Salesforce object)
      -> PricebookEntry (price per pricebook)
        -> Buyer Group Entitlements
```

**B2C vs B2B Catalog Comparison:**

| Aspect | B2C (SFCC) | B2B (Lightning) |
|---|---|---|
| Product object | SFCC Product (proprietary) | Product2 (standard sObject) |
| Category object | SFCC Category | ProductCategory (B2B-specific) |
| Price container | Price Book (SFCC) | Pricebook2 (standard sObject) |
| Price entry | Price per book + currency | PricebookEntry (junction object) |
| Visibility control | Site catalog assignment | Buyer Group Entitlements |
| Variant model | Master -> Variation Products | Product2 child records + custom fields |
| Search | Proprietary SFCC index | Commerce Search (Einstein-powered) |
| Import | XML via Business Manager | Batch Apex, Platform Events, Data Loader |

**Entitlements and Visibility (B2B):**
- Buyer Groups: collections of buyer accounts (WebStore BuyerGroup)
- Product Entitlements: control which buyer groups see which products
- Price Entitlements: control which buyer groups see which prices
- Account hierarchies: parent-child visibility inheritance

**Volume Pricing (B2B):**
- Tiered pricing with quantity breaks at different unit prices
- Negotiated pricing via account-specific custom price books
- Contract pricing for long-term agreements per account
- Consider Salesforce CPQ for complex pricing logic

### Content Integration (B2C)

- **Content Library**: Shared content assets (text, HTML, images)
- **Content Slots**: Dynamic placeholders on category and product pages
- **Page Designer**: Visual page builder for merchandising pages

### Catalog Sync (B2B)

- ERP integration: sync products from SAP, Oracle, or other systems
- Scheduled batch Apex or Platform Events for bulk updates
- Change Data Capture (CDC) for real-time product updates
- Custom Metadata for catalog configuration without custom objects

## Code Examples

```javascript
// Pattern: B2C product retrieval
// Fetch live docs for SCAPI Shopper Products API
// GET /products/{id} -> product attributes, pricing, variants
```

```apex
// Pattern: B2B product query with entitlements
// Fetch live docs for Product2, BuyerGroup, and Entitlement objects
// Query Product2 WHERE entitled for buyer group
```

## Best Practices

### B2C Catalog Structure
- Keep master catalog clean; use site catalogs for site-specific products
- Limit category depth to 3-4 levels for performance and UX
- Plan variation attributes upfront (color, size) for consistency
- Use delta imports for incremental updates; validate XML against XSD before import

### B2C Pricing and Promotions
- Use price book inheritance to avoid duplicate pricing data
- Set list price and sale price separately (never overwrite list)
- Test promotion stacking rules before launch to prevent unintended discounts
- Schedule promotions to auto-start/end (avoid manual changes)

### B2B Catalog Management
- Use standard Product2 fields where possible; avoid over-customization
- Create buyer-group-specific price books; use standard book as fallback
- Document entitlement rules clearly (who sees what)
- Use batch Apex or Platform Events for large catalog syncs from ERP

### Cross-Platform
- Maintain single source of truth for product master data (PIM or ERP)
- Rebuild search indexes after major catalog changes
- Test catalog changes in sandbox before production
- Use SCAPI (not OCAPI) for new B2C implementations

Fetch the SCAPI Shopper Products reference and Salesforce Product2 object docs for exact field names and schemas before implementing.
