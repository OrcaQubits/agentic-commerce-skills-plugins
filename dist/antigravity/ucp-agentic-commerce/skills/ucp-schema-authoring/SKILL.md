---
name: ucp-schema-authoring
description: >
  Author custom UCP schemas and extensions — create capability schemas,
  extension schemas, and type definitions using JSON Schema 2020-12 composition.
  Use when extending UCP with custom capabilities or building domain-specific
  extensions.
---

# UCP Schema Authoring

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification schema` and fetch the relevant pages for the exact schema metadata requirements, category rules, and composition patterns.

Also fetch:
- https://ucp.dev/latest/specification/reference/ — the base type schemas you will reference
- https://ucp.dev/latest/specification/overview/ — the current service/capability layout, which determines the namespaces available to extend

## Conceptual Architecture

### Schema Categories

The official 6 schema categories are:

| Category | Required Metadata | Purpose | Examples |
|----------|-------------------|---------|----------|
| **Capability** | `$schema`, `$id`, `title`, `description`, `name`, `version` | Major functional domain | checkout, order, identity_linking |
| **Service** | `$schema`, `$id`, `title`, `description` | Transport binding definition | REST, MCP, A2A |
| **Payment Handler** | `$schema`, `$id`, `title`, `description` | Payment method specification | Google Pay, Shop Pay |
| **Component** | `$schema`, `$id`, `title`, `description` | Reusable structural unit | payment, payment_data |
| **Type** | `$schema`, `$id`, `title`, `description` | Primitive data model | buyer, line_item, postal_address, total |
| **Meta** | `$schema`, `$id`, `title`, `description` | Schema about schemas | ucp.json, capability.json |

**Note on Extensions**: Extensions (e.g., fulfillment, discount, buyer_consent, ap2_mandate) are NOT a separate top-level category. They are **Capabilities with an `extends` field** that references their parent capability. An extension has the same required metadata as a Capability (`$schema`, `$id`, `title`, `description`, `name`, `version`) plus the `extends` field.

### Extension Composition via `allOf`

Extensions compose with their parent capability using JSON Schema `allOf`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/my-extension.json",
  "title": "My Extension",
  "description": "Adds X to checkout",
  "name": "com.example.my_extension",
  "version": "<spec-dated-version>",
  "extends": "dev.ucp.shopping.checkout",
  "allOf": [
    { "$ref": "https://ucp.dev/latest/schemas/shopping/checkout.json" },
    {
      "properties": {
        "my_field": { "type": "object" }
      }
    }
  ]
}
```

### Services and the namespace tree

UCP organizes capabilities into **services** — verticals that own an API surface. The official tree is reverse-DNS under `dev.ucp`:

| Service | Namespace | Holds |
|---------|-----------|-------|
| Shopping | `dev.ucp.shopping.*` | Checkout, Cart, Catalog, Order, and shopping extensions |
| Common | `dev.ucp.common.*` | Identity Linking, Location, and cross-vertical extensions |
| Payment | `dev.ucp.payment.*` / `dev.ucp.common.payment.*` | Payment handlers and payment extensions |

Fetch the overview page for the current tree before choosing what to extend — services and capabilities are added between spec versions, and a capability you intend to extend may have moved or may not have existed when this skill was written.

### Namespace Governance

- `dev.ucp.*` — governed by ucp.dev (official standard). **Never author into this namespace.**
- `com.example.*` — governed by example.com (your organization)
- `com.shopify.*` — governed by shopify.com

Use your organization's reverse-domain name for custom extensions.

**Namespace authority binding.** Later spec versions add verification that a party actually holds authority over the reverse-DNS namespace it publishes under — you are expected to be able to demonstrate control of the domain your namespace derives from. There are also ordering and reservation rules for namespaces. Fetch the live spec for the current binding mechanism and reserve your namespace before shipping schemas that use it; retrofitting a namespace change after publication breaks every consumer.

### Schema Resolution Sequence

1. Discovery — fetch Business profile
2. Negotiation — compute capability intersection
3. Fetch base capability schema from `schema` URI
4. Fetch extension schemas for negotiated extensions
5. Compose via `allOf`
6. Validate checkout data against composed schema

### Implementation Guidance

- Use **JSON Schema 2020-12** (`https://json-schema.org/draft/2020-12/schema`)
- Host your schemas at a stable, versioned URL
- Declare extensions in your `/.well-known/ucp` profile with the `extends` field
- Test schema composition with the UCP schema validator: https://github.com/Universal-Commerce-Protocol/ucp-schema
- Fetch existing UCP schemas as reference before authoring custom ones
