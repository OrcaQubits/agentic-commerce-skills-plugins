---
name: saleor-attributes
description: >
  Work with Saleor's typed attribute system — attribute types, product types,
  page types, variant selection attributes, and attribute-based filtering. Use
  when defining product schemas.
---

# Saleor Attributes

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/products` for product and attribute overview
2. Web-search `site:docs.saleor.io attribute types DROPDOWN MULTISELECT NUMERIC` for attribute type reference
3. Web-search `site:docs.saleor.io product type attributes variant selection` for product type configuration
4. Web-search `site:docs.saleor.io attribute filtering products` for attribute-based filtering
5. Web-search `site:docs.saleor.io page types attributes` for content page attributes

## Attribute System Overview

Saleor uses a typed attribute system to define flexible product schemas without database migrations. Attributes are attached to product types and page types, providing structured metadata for products, variants, and content pages.

| Concept | Purpose |
|---------|---------|
| Attribute | A named, typed field (e.g., "Color", "Size", "Material") |
| Attribute value | A specific value for an attribute (e.g., "Red", "XL", "Cotton") |
| Product type | A template that defines which attributes a product has |
| Page type | A template that defines which attributes a content page has |
| Variant selection attribute | An attribute used to distinguish product variants |

## Attribute Types

| Type | Input | Storage | Use Case |
|------|-------|---------|----------|
| `DROPDOWN` | Single select from predefined values | String reference | Color, brand, material |
| `MULTISELECT` | Multiple select from predefined values | String references | Features, tags, certifications |
| `RICH_TEXT` | Rich text editor (JSON) | JSON (EditorJS) | Long descriptions, care instructions |
| `PLAIN_TEXT` | Simple text input | String | Short notes, SKU prefix |
| `NUMERIC` | Number input with optional unit | Decimal | Weight, dimensions, capacity |
| `BOOLEAN` | True/false toggle | Boolean | Is organic, is fragile |
| `DATE` | Date picker | Date | Expiry date, release date |
| `DATE_TIME` | Date and time picker | DateTime | Event time, availability window |
| `FILE` | File upload | File reference | Spec sheets, certificates |
| `REFERENCE` | Reference to another entity | Entity ID | Related product, linked page |
| `SWATCH` | Color swatch (hex or image) | String + optional image | Visual color selection |

## Product Types

A product type defines the schema for a group of products:

| Product Type Field | Purpose |
|-------------------|---------|
| `name` | Product type name (e.g., "T-Shirt", "Laptop") |
| `productAttributes` | Attributes shown on the product level |
| `variantAttributes` | Attributes that define variant differences |
| `isShippingRequired` | Whether products of this type need shipping |
| `isDigital` | Whether products are digital downloads |
| `taxClass` | Tax classification for products of this type |
| `weight` | Default weight for products of this type |

### Product Attributes vs Variant Selection Attributes

| Category | Scope | Example |
|----------|-------|---------|
| Product attributes | Same for all variants of a product | Brand, material, care instructions |
| Variant attributes (non-selection) | Per variant, but not for customer selection | Internal SKU code |
| Variant selection attributes | Per variant, presented to the customer for selection | Size, color |

Variant selection attributes generate the variant picker on the storefront (e.g., size/color dropdowns).

## Attribute Values

| Value Aspect | Detail |
|-------------|--------|
| Predefined | Created in advance for DROPDOWN, MULTISELECT, SWATCH types |
| Dynamic | Entered per product for PLAIN_TEXT, RICH_TEXT, NUMERIC, DATE types |
| Sortable | Values can be reordered within an attribute |
| Translatable | Values support multi-language translations |
| Slug | URL-safe identifier auto-generated from the value name |

### Rich Text Values

Rich text attributes use the EditorJS JSON format:

| Block Type | Purpose |
|-----------|---------|
| `paragraph` | Text paragraph |
| `header` | Heading (h1-h6) |
| `list` | Ordered or unordered list |
| `image` | Embedded image |

## Page Types

Page types work like product types but for content pages (CMS):

| Page Type Field | Purpose |
|----------------|---------|
| `name` | Page type name (e.g., "Blog Post", "FAQ") |
| `attributes` | Attributes attached to pages of this type |

Content pages use the same attribute types as products, enabling structured content management without a separate CMS.

## Attribute Input Types

The `inputType` field controls how an attribute is presented in the Dashboard:

| Input Type | Attribute Types | Dashboard UI |
|-----------|----------------|-------------|
| `DROPDOWN` | DROPDOWN | Single-select dropdown |
| `MULTISELECT` | MULTISELECT | Multi-select chips |
| `PLAIN_TEXT` | PLAIN_TEXT | Simple text field |
| `RICH_TEXT` | RICH_TEXT | EditorJS rich text editor |
| `NUMERIC` | NUMERIC | Number input with unit selector |
| `BOOLEAN` | BOOLEAN | Toggle switch |
| `DATE` | DATE | Date picker |
| `DATE_TIME` | DATE_TIME | Date and time picker |
| `FILE` | FILE | File upload widget |
| `REFERENCE` | REFERENCE | Entity search and select |
| `SWATCH` | SWATCH | Color picker or image upload |

## Filtering Products by Attributes

Attributes enable faceted navigation on the storefront:

| Filter Parameter | Type | Purpose |
|-----------------|------|---------|
| `attributes` | list | Filter by attribute slug and values |
| `attributes.slug` | string | Attribute identifier |
| `attributes.values` | string[] | Attribute value slugs to match |
| `attributes.valuesRange` | object | Numeric range filter (min/max) |
| `attributes.date` | object | Date range filter |
| `attributes.dateTime` | object | DateTime range filter |
| `attributes.boolean` | boolean | Boolean attribute filter |

### Faceted Navigation Pattern

| Step | Action |
|------|--------|
| 1 | Query available attributes for the product type or category |
| 2 | Display attribute values as filter options (checkboxes, sliders) |
| 3 | Build `attributes` filter from user selections |
| 4 | Pass filter to `products` query |
| 5 | Update available filter values based on current selection (count-aware) |

## Creating Attributes via GraphQL

| Mutation | Purpose |
|----------|---------|
| `attributeCreate` | Create a new attribute with type and values |
| `attributeUpdate` | Modify attribute settings |
| `attributeDelete` | Remove an attribute |
| `attributeValueCreate` | Add a new value to an attribute |
| `attributeValueUpdate` | Modify an attribute value |
| `attributeValueDelete` | Remove an attribute value |
| `attributeReorderValues` | Change the sort order of values |
| `productTypeCreate` | Create a product type with attribute assignments |
| `productTypeUpdate` | Modify product type attribute assignments |

### Attribute Creation Fields

| Input Field | Required | Purpose |
|-------------|----------|---------|
| `name` | Yes | Display name |
| `slug` | No | Auto-generated from name if omitted |
| `type` | Yes | `PRODUCT_TYPE` or `PAGE_TYPE` |
| `inputType` | Yes | One of the attribute input types |
| `values` | No | Initial predefined values (for DROPDOWN, MULTISELECT) |
| `valueRequired` | No | Whether the attribute must have a value |
| `isVariantOnly` | No | Restrict to variant-level only |
| `visibleInStorefront` | No | Whether the attribute is public |
| `filterableInStorefront` | No | Whether the attribute appears in storefront filters |
| `filterableInDashboard` | No | Whether the attribute appears in Dashboard filters |
| `availableInGrid` | No | Whether the attribute appears in Dashboard product grid |
| `unit` | No | Measurement unit for NUMERIC type |

## Best Practices

- Use DROPDOWN for attributes with a fixed set of values (colors, sizes, brands)
- Use variant selection attributes only for attributes that the customer chooses (size, color)
- Keep product attributes for shared information that does not vary per variant (brand, material)
- Enable `filterableInStorefront` only for attributes that make sense as customer-facing filters
- Use NUMERIC type with units for measurable properties (weight, length) to enable range filtering
- Create separate product types for structurally different products (clothing vs electronics)
- Use page types to model structured content (blog posts, FAQs) without a separate CMS
- Translate attribute names and values for multi-language storefronts

Fetch the Saleor attributes documentation for exact attribute type behaviors, product type configuration patterns, and filtering query syntax before implementing.
