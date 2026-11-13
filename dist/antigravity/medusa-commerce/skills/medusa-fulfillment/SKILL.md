---
name: medusa-fulfillment
description: >
  Implement Medusa v2 fulfillment — fulfillment module, provider interface,
  shipping options, fulfillment sets, shipping profiles, and multi-warehouse
  support. Use when adding fulfillment providers.
---

# Medusa v2 Fulfillment

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com fulfillment module` for fulfillment data model and service methods
2. Web-search `site:docs.medusajs.com fulfillment provider` for the provider abstraction interface
3. Web-search `site:docs.medusajs.com shipping option` for shipping option configuration
4. Fetch `https://docs.medusajs.com/resources/references/fulfillment` and review the `IFulfillmentModuleService` interface
5. Web-search `medusajs v2 AbstractFulfillmentProviderService 2026` for latest provider interface

## Fulfillment Module Architecture

### Entity Relationships

| Entity | Contains | Key Fields |
|--------|----------|------------|
| **FulfillmentSet** | ServiceZones, Fulfillments | name, type (`shipping`, `pick-up`) |
| **ServiceZone** | GeoZones, ShippingOptions | Geographic area with shipping config |
| **ShippingOption** | Rules | name, price_type, provider_id, type |
| **GeoZone** | — | country, province, city, zip |
| **Fulfillment** | Items, Labels | tracking_numbers, packed/shipped/delivered_at |
| **StockLocation** | Link to FulfillmentSet | Warehouse connection |

### Module Links

```
Fulfillment Module ──link──> Stock Location Module (warehouse)
Fulfillment Module ──link──> Cart Module (shipping methods)
Fulfillment Module ──link──> Order Module (order fulfillments)
```

> **Fetch live docs** for exact link definitions and how fulfillment sets connect to stock locations.

## Fulfillment Provider Interface

All providers extend `AbstractFulfillmentProviderService`:

```ts
// Skeleton: custom fulfillment provider
// Fetch live docs for AbstractFulfillmentProviderService
class MyShippingProvider extends AbstractFulfillmentProviderService {
  // Implement: validateFulfillmentData, calculatePrice,
  // createFulfillment, cancelFulfillment
  // Fetch live docs for exact method signatures
}
```

### Required Provider Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `validateFulfillmentData` | Validate shipping data at checkout | Validated data |
| `validateOption` | Validate shipping option config | Boolean |
| `canCalculate` | Whether provider supports dynamic pricing | Boolean |
| `calculatePrice` | Calculate shipping cost dynamically | Price amount |
| `createFulfillment` | Create fulfillment (generate label) | Fulfillment data |
| `cancelFulfillment` | Cancel an existing fulfillment | void |
| `getFulfillmentDocuments` | Get shipping labels/documents | Document URLs |
| `createReturnFulfillment` | Create return shipment | Return data |

> **Fetch live docs** for exact method signatures, input types, and expected return shapes.

## Shipping Options

### Shipping Option Type

Shipping options reference a `ShippingOptionType` entity with a `label` and `code`. Types are configurable — common patterns include "express", "standard", "economy". The `is_return` rule on a shipping option determines if it applies to returns.

> **Fetch live docs** for how `ShippingOptionType` entities are created and linked.

### Price Types

| Price Type | Description |
|------------|-------------|
| `flat_rate` | Fixed price defined in shipping option |
| `calculated` | Dynamic price calculated by provider at checkout |

### Shipping Option Rules

| Rule Attribute | Example | Description |
|----------------|---------|-------------|
| `enabled_in_store` | `true` | Visible to customers |
| `is_return` | `false` | Available for returns |
| custom attributes | varies | Provider-specific criteria |

> **Fetch live docs** for the full list of rule attributes and how to create custom rules.

## Fulfillment Sets and Geo Zones

| Concept | Description |
|---------|-------------|
| Fulfillment Set | Named group of service zones linked to a stock location |
| Service Zone | Geographic area with associated shipping options |
| Geo Zone | Specific geographic boundary |
| Stock Location Link | Connects fulfillment set to a warehouse |

### Geo Zone Types

| Type | Scope | Example |
|------|-------|---------|
| `country` | Entire country | `country_code: "US"` |
| `province` | State/province | `province_code: "CA"` |
| `city` | City | `city: "San Francisco"` |
| `zip` | Postal code range | `postal_expression: "941*"` |

## Shipping Profiles

| Concept | Description |
|---------|-------------|
| Shipping Profile | Links product types to shipping options |
| Default Profile | Applies to products without explicit assignment |
| Custom Profiles | For oversized, fragile, or special-handling items |

## Multi-Warehouse Support

| Entity | Key Fields |
|--------|------------|
| **StockLocation** | name, address, FulfillmentSet (link) |
| **InventoryItem** | stocked_quantity, reserved_quantity, incoming_quantity |

Each InventoryItem tracks stock per variant per location.

### Fulfillment Routing

| Strategy | Description |
|----------|-------------|
| Nearest warehouse | Ship from closest location to customer |
| Inventory priority | Ship from location with highest stock |
| Manual selection | Admin selects fulfillment location |

> **Fetch live docs** for stock location module service methods and inventory allocation strategies.

## Fulfillment Lifecycle

```
Created ──> Packed ──> Shipped ──> Delivered
                                      └─> Return (if needed)
```

### Key Workflows

| Workflow | Purpose |
|----------|---------|
| `createFulfillmentWorkflow` | Create fulfillment for order items |
| `cancelFulfillmentWorkflow` | Cancel a pending fulfillment |
| `createShipmentWorkflow` | Add tracking and mark shipped |
| `markFulfillmentAsDeliveredWorkflow` | Mark as delivered |

### Key Service Methods

| Operation | Method |
|-----------|--------|
| Create fulfillment set | `fulfillmentModuleService.createFulfillmentSets()` |
| Create service zone | `fulfillmentModuleService.createServiceZones()` |
| Create shipping option | `fulfillmentModuleService.createShippingOptions()` |
| List shipping options | `fulfillmentModuleService.listShippingOptions()` |
| Create fulfillment | `fulfillmentModuleService.createFulfillment()` |

## Best Practices

### Provider Implementation
- Always extend `AbstractFulfillmentProviderService` — do not implement from scratch
- Implement `calculatePrice` accurately — it directly affects checkout totals
- Handle rate API failures gracefully — return cached or fallback rates
- Support both outbound and return fulfillment creation

### Shipping Configuration
- Use geo zones to precisely control shipping option availability by location
- Configure shipping profiles for products with different fulfillment requirements
- Set up both `flat_rate` and `calculated` options — flat rate for simplicity, calculated for accuracy

### Multi-Warehouse
- Link each fulfillment set to exactly one stock location
- Configure service zones per warehouse based on geographic proximity
- Support split shipments — one order may be fulfilled from multiple locations

### Tracking
- Always set tracking numbers when creating shipments
- Subscribe to fulfillment events for customer notification triggers
- Store shipping labels in the fulfillment `data` field

Fetch the Medusa v2 fulfillment module documentation and provider interface references for exact method signatures, shipping option configuration, and multi-warehouse patterns before implementing.
