---
name: saleor-shipping
description: >
  Configure Saleor shipping — shipping zones, methods (price/weight-based),
  custom shipping Apps, warehouse-based allocation, and click-and-collect. Use
  when setting up delivery options.
---

# Saleor Shipping Configuration

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io shipping zones methods configuration` for shipping zone and method setup
2. Web-search `site:docs.saleor.io warehouse allocation shipping` for warehouse-based stock allocation strategies
3. Web-search `site:docs.saleor.io shipping app SHIPPING_LIST_METHODS_FOR_CHECKOUT` for custom shipping App patterns
4. Fetch `https://docs.saleor.io/docs/developer/shipping` and review shipping zone, method, and pricing models
5. Web-search `site:docs.saleor.io click and collect warehouse pickup` for local pickup configuration

## Shipping Zones

A shipping zone groups countries that share the same shipping methods and rates:

| Field | Description |
|-------|-------------|
| `name` | Display name for the zone (e.g., "Domestic", "Europe") |
| `countries` | List of ISO 3166-1 alpha-2 country codes |
| `default` | Whether this is the fallback zone for unmatched countries |
| `channels` | Channels where this zone is available |
| `shippingMethods` | Shipping methods available in this zone |
| `warehouses` | Warehouses assigned to this zone |

### Zone Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create zone | `shippingZoneCreate` | Set name, countries, channels |
| Update zone | `shippingZoneUpdate` | Modify countries, channels, warehouses |
| Delete zone | `shippingZoneDelete` | Remove zone and its methods |

Zones can map to specific countries, overlap (customer sees all methods), or use a `default` zone as fallback. Zones are channel-scoped — only matching zones appear at checkout.

## Shipping Methods

Each zone contains one or more shipping methods:

### Method Types

| Type | Pricing Basis | Description |
|------|---------------|-------------|
| Price-based | Order subtotal | Rates determined by the total price of the order |
| Weight-based | Order weight | Rates determined by the total weight of the order |

### Method Configuration

| Field | Description |
|-------|-------------|
| `name` | Display name shown to customers |
| `type` | `PRICE` or `WEIGHT` |
| `minimumOrderPrice` | Minimum order total for this method (price-based) |
| `maximumOrderPrice` | Maximum order total for this method (price-based) |
| `minimumOrderWeight` | Minimum order weight for this method (weight-based) |
| `maximumOrderWeight` | Maximum order weight for this method (weight-based) |
| `channelListings` | Per-channel price and min/max order price |
| `maximumDeliveryDays` | Maximum estimated delivery days |
| `minimumDeliveryDays` | Minimum estimated delivery days |

### Method Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create method | `shippingPriceCreate` | Add method to a zone |
| Update method | `shippingPriceUpdate` | Modify method settings |
| Delete method | `shippingPriceDelete` | Remove method from zone |
| Update channel listing | `shippingMethodChannelListingUpdate` | Set per-channel pricing |

### Channel-Specific Pricing

Each shipping method has per-channel pricing:

| Field | Description |
|-------|-------------|
| `price` | Shipping cost in the channel currency |
| `minimumOrderPrice` | Channel-specific minimum order price |
| `maximumOrderPrice` | Channel-specific maximum order price |

## Free Shipping Thresholds

Configure free shipping by setting price ranges on methods:

| Approach | Configuration |
|----------|---------------|
| Free above threshold | Create a price-based method with `minimumOrderPrice` set and `price: 0` |
| Paid below threshold | Create a separate method with `maximumOrderPrice` at the threshold |
| Voucher-based | Use a free shipping voucher (see promotions skill) |

## Excluded Products

Shipping methods can exclude specific products:

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Exclude products | `shippingPriceExcludeProducts` | Products that cannot use this method |
| Remove exclusion | `shippingPriceRemoveProductFromExclude` | Allow previously excluded products |

> Exclusions work at the product level. If any line in the checkout contains an excluded product, the shipping method becomes unavailable.

## Custom Shipping Apps

For dynamic shipping rates (e.g., real-time carrier rates), implement a shipping App:

### Sync Webhook: SHIPPING_LIST_METHODS_FOR_CHECKOUT

| Aspect | Description |
|--------|-------------|
| Trigger | Saleor calls the App when a checkout needs shipping methods |
| Input | Checkout data including lines, shipping address, channel |
| Output | List of available shipping methods with prices and delivery estimates |
| Use case | Real-time carrier API integration (UPS, FedEx, DHL, etc.) |

### App Response Format

The shipping App returns an array of methods:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique method identifier |
| `name` | Yes | Display name for the method |
| `amount` | Yes | Shipping cost |
| `currency` | Yes | Currency code |
| `maximumDeliveryDays` | No | Maximum delivery estimate |
| `minimumDeliveryDays` | No | Minimum delivery estimate |

## Warehouse-Based Allocation

Saleor supports multi-warehouse stock allocation:

### Allocation Strategies

| Strategy | Description |
|----------|-------------|
| Prioritize sorting order | Allocate from warehouses in the order they are sorted in the channel |
| Prioritize by distance | Allocate from the warehouse closest to the shipping address |

### Warehouse Configuration

| Field | Description |
|-------|-------------|
| `name` | Warehouse display name |
| `slug` | URL-friendly identifier |
| `shippingZones` | Zones this warehouse serves |
| `address` | Physical warehouse address |
| `clickAndCollectOption` | `DISABLED`, `LOCAL_STOCK`, or `ALL_WAREHOUSES` |
| `isPrivate` | Whether warehouse is hidden from customers |

### Warehouse Mutations

| Operation | Mutation |
|-----------|----------|
| Create warehouse | `createWarehouse` |
| Update warehouse | `updateWarehouse` |
| Delete warehouse | `deleteWarehouse` |

## Click-and-Collect / Warehouse Pickup

Enable customers to pick up orders from physical locations:

| Option | Description |
|--------|-------------|
| `DISABLED` | No pickup available at this warehouse |
| `LOCAL_STOCK` | Pickup available only for items in stock at this warehouse |
| `ALL_WAREHOUSES` | Pickup available; stock can be transferred from other warehouses |

### Checkout Integration

When click-and-collect is enabled:

| Step | Description |
|------|-------------|
| 1. Set shipping address | Customer sets their address (or warehouse address) |
| 2. Query delivery methods | `checkout.deliveryMethod` returns both shipping and pickup options |
| 3. Select pickup | Use `checkoutDeliveryMethodUpdate` with warehouse ID |
| 4. Complete checkout | Standard checkout completion flow |

> **Fetch live docs** for the `DeliveryMethod` union type which includes both `ShippingMethod` and `Warehouse` for pickup locations.

## Best Practices

- Create separate shipping zones for domestic and international shipping
- Use price-based methods for flat-rate/tiered shipping; weight-based when weight significantly affects cost
- Implement a custom shipping App for real-time carrier rate calculation
- Assign warehouses to shipping zones to control which locations fulfill which regions
- Use channel listings to set different shipping prices per channel and currency
- Configure a default shipping zone as a fallback for unmatched countries
- Set delivery day estimates to improve customer experience
- Enable click-and-collect on warehouses that serve as customer-facing pickup points

Fetch the Saleor shipping and warehouse documentation for exact mutation inputs, webhook payloads, and allocation strategy configuration before implementing.
