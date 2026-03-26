---
name: saleor-promotions
description: Configure Saleor promotions — catalog promotions, order promotions, vouchers, manual discounts, gift cards, and discount stacking. Use when setting up pricing rules.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Promotions and Discounts

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io promotions catalog order rules` for promotion types and rule configuration
2. Web-search `site:docs.saleor.io vouchers voucher codes` for voucher creation and usage patterns
3. Web-search `site:docs.saleor.io gift cards` for gift card creation, activation, and redemption
4. Fetch `https://docs.saleor.io/docs/developer/discounts` and review the promotion model, rules, and conditions
5. Web-search `site:docs.saleor.io manual discount order staff` for staff-applied manual discounts
6. Fetch `https://docs.saleor.io/docs/developer/gift-cards` and review gift card as product and as payment method

## Promotion Types

Saleor distinguishes between two promotion types that apply at different stages:

| Type | When Applied | Effect |
|------|-------------|--------|
| Catalog promotion | At product display time | Reduces the visible price on product listings and detail pages |
| Order promotion | At checkout time | Applies discount to the order total or specific lines during checkout |

### Catalog Promotions

| Aspect | Description |
|--------|-------------|
| Timing | Applied before the product reaches the cart |
| Visibility | Customers see the discounted price on product pages |
| Price display | `undiscountedPrice` and `pricing.discount` show the original and savings |
| Stacking | Multiple catalog promotions can apply to the same product |

### Order Promotions

| Aspect | Description |
|--------|-------------|
| Timing | Applied when conditions are met in the checkout |
| Visibility | Discount shown as a line discount or order-level discount |
| Conditions | Based on cart contents, order total, or specific products |
| Application | Automatic when conditions match -- no code required |

## Promotion Rules and Conditions

Each promotion contains one or more rules:

### Rule Structure

| Field | Description |
|-------|-------------|
| `name` | Rule display name |
| `channels` | Channels where this rule applies |
| `cataloguePredicate` | Conditions based on product, category, collection, or variant |
| `orderPredicate` | Conditions based on order total or checkout lines |
| `rewardValue` | Discount amount (fixed or percentage) |
| `rewardValueType` | `FIXED` or `PERCENTAGE` |
| `rewardType` | For order promotions: `SUBTOTAL_DISCOUNT` or `GIFT` |

Catalogue predicate conditions: `productPredicate`, `categoryPredicate`, `collectionPredicate`, `variantPredicate`. Order predicate conditions: `discountedObjectPredicate` (minimum subtotal), `totalPrice` (order total threshold).

## Promotion Management

### Key Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create promotion | `promotionCreate` | Set name, type, start/end dates, rules |
| Update promotion | `promotionUpdate` | Modify promotion settings |
| Delete promotion | `promotionDelete` | Remove promotion |
| Create rule | `promotionRuleCreate` | Add rule to existing promotion |
| Update rule | `promotionRuleUpdate` | Modify rule conditions and rewards |
| Delete rule | `promotionRuleDelete` | Remove rule from promotion |

### Promotion Fields

| Field | Description |
|-------|-------------|
| `name` | Promotion display name |
| `type` | `CATALOGUE` or `ORDER` |
| `startDate` | When the promotion becomes active |
| `endDate` | When the promotion expires (optional) |
| `rules` | Array of promotion rules |
| `metadata` | Custom key-value metadata |

## Voucher Codes

Vouchers are code-based discounts that customers enter at checkout:

### Voucher Types

| Type | Description |
|------|-------------|
| `ENTIRE_ORDER` | Discount applied to the entire order |
| `SHIPPING` | Free or discounted shipping |
| `SPECIFIC_PRODUCT` | Discount on specific products only |

### Voucher Configuration

| Field | Description |
|-------|-------------|
| `code` | The voucher code customers enter |
| `type` | Voucher type (see above) |
| `discountValueType` | `FIXED` or `PERCENTAGE` |
| `discountValue` | Discount amount or percentage |
| `minCheckoutItemsQuantity` | Minimum items required in checkout |
| `minSpent` | Minimum order amount (per channel) |
| `usageLimit` | Total number of times the voucher can be used |
| `applyOncePerCustomer` | Whether each customer can use it only once |
| `applyOncePerOrder` | Whether the discount applies to one item or all matching items |
| `onlyForStaff` | Restrict to staff-created orders |
| `startDate` | Activation date |
| `endDate` | Expiration date |

### Key Voucher Mutations

| Operation | Mutation |
|-----------|----------|
| Create voucher | `voucherCreate` |
| Update voucher | `voucherUpdate` |
| Delete voucher | `voucherDelete` |
| Add products | `voucherCataloguesAdd` |
| Remove products | `voucherCataloguesRemove` |

## Manual Staff Discounts

Staff users can apply manual discounts to orders:

| Operation | Mutation | Scope |
|-----------|----------|-------|
| Add order discount | `orderDiscountAdd` | Entire order |
| Update order discount | `orderDiscountUpdate` | Modify existing discount |
| Delete order discount | `orderDiscountDelete` | Remove discount |
| Add line discount | `orderLineDiscountAdd` (draft orders) | Specific line item |

> Manual discounts are only available for draft orders and through staff-facing operations. They cannot be combined with automatic promotions on the same order line.

## Gift Cards

Gift cards function both as a product type and as a payment method:

### Gift Card as Product

| Aspect | Description |
|--------|-------------|
| Product type | Create a product type with `isDigital: true` for gift cards |
| Variants | Each variant represents a gift card denomination |
| Purchase | Customer buys a gift card like any other product |
| Activation | Gift card is automatically created and code sent to buyer |

### Gift Card as Payment

| Aspect | Description |
|--------|-------------|
| Application | Customer enters gift card code at checkout |
| Balance | Gift card has a remaining balance that decreases with each use |
| Partial use | Gift card can be used for partial payment; remainder stays as balance |
| Multiple cards | Multiple gift cards can be applied to one checkout |

### Gift Card Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create gift card | `giftCardCreate` | Staff-created gift card |
| Update gift card | `giftCardUpdate` | Modify balance, expiry |
| Deactivate | `giftCardDeactivate` | Disable without deleting |
| Activate | `giftCardActivate` | Re-enable a deactivated card |
| Resend code | `giftCardResend` | Resend gift card code via email |
| Bulk create | `giftCardBulkCreate` | Generate multiple cards at once |
| Add note | `giftCardAddNote` | Add staff note to gift card |

## Discount Stacking Rules

| Scenario | Behavior |
|----------|----------|
| Multiple catalog promotions | All matching promotions apply; discounts stack |
| Catalog promotion + voucher | Both apply; catalog discount reduces base price, voucher applies on top |
| Catalog promotion + order promotion | Both can apply; catalog reduces price, order promotion discounts checkout |
| Multiple vouchers | Only one voucher code per checkout |
| Voucher + manual discount | Voucher applies first; manual discount applies on remaining amount |
| Gift card + other discounts | Gift card applies after all other discounts as a payment method |

## Best Practices

- Use catalog promotions for sale prices visible on product pages; order promotions for cart-level discounts
- Use vouchers when a code-based redemption experience is required
- Set `startDate` and `endDate` on promotions to automate sale periods
- Use `usageLimit` and `applyOncePerCustomer` on vouchers to control distribution
- Test promotion stacking behavior in a staging environment before going live
- Use gift cards with expiration dates to manage liability
- Always specify channels on promotion rules to prevent unintended cross-channel discounts

Fetch the Saleor promotions and voucher documentation for exact mutation inputs, predicate syntax, and discount stacking behavior before implementing.
