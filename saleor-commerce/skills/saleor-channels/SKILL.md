---
name: saleor-channels
description: Configure Saleor channels — multi-currency, multi-region, per-channel pricing, warehouse allocation, and multi-brand setups. Use when managing multi-channel commerce.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Channels

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/channels` for channels overview
2. Web-search `site:docs.saleor.io channel configuration currency countries` for channel setup reference
3. Web-search `site:docs.saleor.io per-channel pricing product` for channel-aware pricing
4. Web-search `site:docs.saleor.io warehouse allocation channels` for warehouse-channel mapping
5. Web-search `site:docs.saleor.io multi-brand multi-tenant channels` for multi-brand patterns

## Channel Concept

A channel represents a distinct sales context within a single Saleor instance. One Saleor deployment can serve multiple storefronts, regions, brands, or business models -- each as a separate channel.

| Aspect | Detail |
|--------|--------|
| One instance | Single Saleor backend, shared catalog and infrastructure |
| Many channels | Each channel has its own currency, countries, pricing, and settings |
| Isolation | Customers see only channel-scoped data (prices, availability) |
| Staff access | Staff can manage all channels from one Dashboard |

## Channel Configuration Fields

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Human-readable channel name |
| `slug` | string | URL-safe identifier (used in API queries) |
| `currencyCode` | string | ISO 4217 currency code (e.g., `USD`, `EUR`, `GBP`) |
| `defaultCountry` | string | ISO 3166-1 alpha-2 country code |
| `countries` | string[] | Countries where this channel operates |
| `isActive` | boolean | Whether the channel is publicly accessible |
| `stockSettings.allocationStrategy` | enum | `PRIORITIZE_HIGH_STOCK` or `PRIORITIZE_SORTING_ORDER` |
| `orderSettings.automaticallyConfirmAllNewOrders` | boolean | Auto-confirm orders |
| `orderSettings.automaticallyFulfillNonShippableGiftCard` | boolean | Auto-fulfill digital gift cards |
| `checkoutSettings.useLegacyErrorFlow` | boolean | Legacy vs new error handling |

## Per-Channel Pricing

Products have base prices, but each channel can define its own pricing:

| Pricing Layer | Scope | Purpose |
|--------------|-------|---------|
| Product variant price | Per channel | Base selling price in channel currency |
| Cost price | Per channel | Cost of goods for margin calculation |
| Channel currency | Per channel | All prices in this channel use this currency |
| Tax configuration | Per channel | Tax calculation rules |
| Discounts | Per channel | Promotions scoped to specific channels |

### Pricing Assignment

| Entity | Channel-Scoped Fields |
|--------|----------------------|
| Product variant | `channelListings.price`, `channelListings.costPrice` |
| Product | `channelListings.isPublished`, `channelListings.publishedAt`, `channelListings.isAvailableForPurchase` |
| Collection | `channelListings.isPublished`, `channelListings.publishedAt` |
| Shipping method | `channelListings.price`, `channelListings.minimumOrderPrice`, `channelListings.maximumOrderPrice` |
| Voucher | `channelListings.discountValue`, `channelListings.minSpent` |

## Country Assignment

Each channel defines a set of countries it serves:

| Aspect | Detail |
|--------|--------|
| Shipping | Only shipping methods for assigned countries are available |
| Tax | Tax rules are applied based on channel country settings |
| Address validation | Checkout validates against channel's country list |
| Warehouse selection | Warehouses are linked to countries within channels |

## Warehouse Allocation

Warehouses and channels are connected through country assignments:

| Concept | Relationship |
|---------|-------------|
| Warehouse | Has a list of shipping zones it serves |
| Shipping zone | Has a list of countries |
| Channel | Has a list of countries |
| Allocation | Saleor allocates stock from warehouses that serve the channel's countries |

### Allocation Strategies

| Strategy | Behavior |
|----------|----------|
| `PRIORITIZE_SORTING_ORDER` | Allocate from warehouses in their configured sort order (default) |
| `PRIORITIZE_HIGH_STOCK` | Allocate from the warehouse with the most stock |

## Channel-Aware GraphQL Queries

Most storefront queries require a `channel` argument:

| Query | Channel Behavior |
|-------|-----------------|
| `products(channel: "us")` | Returns products published in the US channel |
| `product(slug: "tee", channel: "us")` | Returns US-channel pricing and availability |
| `collections(channel: "us")` | Returns collections published in the US channel |
| `checkout(channel: "us")` | Creates checkout with US currency and settings |
| `shippingMethods(channel: "us")` | Returns methods available for US channel countries |

Queries without the `channel` argument are reserved for staff/admin operations and return data across all channels.

## Channel Creation via GraphQL

| Mutation | Purpose |
|----------|---------|
| `channelCreate` | Create a new channel with currency and country settings |
| `channelUpdate` | Modify channel settings (countries, stock strategy) |
| `channelDelete` | Remove a channel (irreversible) |
| `channelActivate` | Make a channel publicly accessible |
| `channelDeactivate` | Hide a channel from public access |

### Channel Creation Fields

| Input Field | Required | Purpose |
|-------------|----------|---------|
| `name` | Yes | Display name |
| `slug` | Yes | URL-safe identifier |
| `currencyCode` | Yes | Channel currency |
| `defaultCountry` | Yes | Primary country |
| `addCountries` | No | Additional countries |
| `stockSettings` | No | Allocation strategy |
| `orderSettings` | No | Auto-confirm, fulfillment rules |

## Multi-Brand Architecture

Channels enable multi-brand commerce from a single Saleor instance:

| Brand | Channel | Storefront | Currency |
|-------|---------|-----------|----------|
| Brand A (US) | `brand-a-us` | `brand-a.com` | USD |
| Brand A (EU) | `brand-a-eu` | `brand-a.eu` | EUR |
| Brand B (US) | `brand-b-us` | `brand-b.com` | USD |
| Wholesale | `wholesale` | `wholesale.brand-a.com` | USD |

### Multi-Brand Considerations

| Aspect | Approach |
|--------|----------|
| Product catalog | Shared catalog, per-channel publication and pricing |
| Customers | Shared customer base across channels |
| Orders | Each order belongs to one channel |
| Staff permissions | Channel-level access control for staff members |
| Apps | Apps can be channel-aware or cross-channel |
| Warehouses | Shared warehouses, per-channel allocation |

## Channel Permissions

| Permission | Scope |
|------------|-------|
| `MANAGE_CHANNELS` | Create, update, delete channels |
| Channel-restricted staff | Staff members can be limited to specific channels |
| App permissions | Apps operate across all channels unless filtered |

## Best Practices

- Create separate channels for each currency -- Saleor requires one currency per channel
- Use channel slugs that are descriptive and URL-friendly (e.g., `us-store`, `eu-store`)
- Assign countries to channels carefully -- shipping and tax rules depend on this
- Use the `PRIORITIZE_SORTING_ORDER` allocation strategy when warehouse priority matters
- Publish products to channels explicitly -- unpublished products are invisible to storefronts
- Restrict staff access to relevant channels using channel-level permissions
- Use one channel per storefront for clear data isolation
- Plan channel structure before going live -- migrating orders between channels is not supported

Fetch the Saleor channels documentation for exact mutation inputs, allocation strategy details, and multi-brand configuration patterns before implementing.
