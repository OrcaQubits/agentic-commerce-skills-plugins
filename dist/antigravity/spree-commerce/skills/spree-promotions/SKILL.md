---
name: spree-promotions
description: >
  Build and customize Spree's promotions engine — Promotion + PromotionRule +
  PromotionAction + CouponCode + Adjustment, the bundled rules
  (FirstOrder/ItemTotal/Product/Taxon/User/OneUsePerUser/Country/CustomerGroup/etc.),
  bundled actions
  (CreateAdjustment/CreateItemAdjustments/FreeShipping/CreateLineItems),
  Calculator classes, coupon batches with CSV export, the v5.1+ advanced
  rule-based engine, and authoring custom rules/actions/calculators. Use when
  modeling promotions, building discount UIs, or extending the promotions
  engine.
---

# Spree Promotions

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/promotions for the canonical model.
2. Inspect the live `Spree::PromotionRule` / `Spree::PromotionAction` source — bundled rule/action classes change between minors.
3. Check the v5.1 announcement for the advanced rule-based engine introduced there.
4. For custom calculators, review live examples in the `app/models/spree/calculator/` directory of the `spree` gem.
5. Check the latest release notes for any promotions changes (v5.0 added coupon batch CSV export).

## Conceptual Architecture

### The Four Building Blocks

```
Promotion
├── PromotionRule[]  (must-match criteria)
├── PromotionAction[]  (what to do on match)
└── CouponCode[]  (optional codes that trigger this promotion)
       ↓
     creates
       ↓
  Adjustment (attached to Order, LineItem, or Shipment)
```

### Rule Match Policy

A `Promotion` has a `match_policy` of either:
- **`all`** — every rule must match
- **`any`** — at least one rule must match

### Bundled Rules (verify against live source)

| Rule | Matches |
|------|---------|
| `Spree::Promotion::Rules::FirstOrder` | User's first order |
| `Spree::Promotion::Rules::ItemTotal` | Cart total ≥ N |
| `Spree::Promotion::Rules::Product` | Specific product(s) in cart |
| `Spree::Promotion::Rules::Taxon` | Product in specific taxon |
| `Spree::Promotion::Rules::User` | Specific user |
| `Spree::Promotion::Rules::UserLoggedIn` | Not a guest |
| `Spree::Promotion::Rules::OneUsePerUser` | User hasn't used promo before |
| `Spree::Promotion::Rules::Country` | Ship-to country in set |
| `Spree::Promotion::Rules::Currency` | Order in specific currency |
| `Spree::Promotion::Rules::OptionValue` | Specific OptionValue selected |
| `Spree::Promotion::Rules::CustomerGroup` | Customer in group |

### Bundled Actions

| Action | Effect |
|--------|--------|
| `Spree::Promotion::Actions::CreateAdjustment` | Order-level discount |
| `Spree::Promotion::Actions::CreateItemAdjustments` | Per-line-item discount |
| `Spree::Promotion::Actions::FreeShipping` | Zero out shipping cost |
| `Spree::Promotion::Actions::CreateLineItems` | Auto-add a gift line item |

### Calculators

Each action uses a `Calculator` to compute its dollar amount:

| Calculator | Math |
|------------|------|
| `Spree::Calculator::FlatPercentItemTotal` | % of order subtotal |
| `Spree::Calculator::FlatRate` | Fixed amount |
| `Spree::Calculator::FlexiRate` | Per-quantity tier |
| `Spree::Calculator::PercentOnLineItem` | % of line item |
| `Spree::Calculator::TieredPercent` | % based on cart total tier |
| `Spree::Calculator::DistributedAmount` | Fixed amount split proportionally |

Calculators are polymorphic — also used by Shipping and Tax.

### Coupon Codes

A `Promotion` can have:
- **No coupon code** (auto-applied if rules match)
- **One code** (single shared coupon)
- **Many codes** (coupon batch — CSV export added in v5.0)

### Single-Use, Limit, and Expiry

`Promotion` has:
- `usage_limit` — global cap
- `per_user_limit` — per-user cap (in addition to OneUsePerUser rule)
- `starts_at` / `expires_at` — windowed availability

### Advanced Rule Engine (v5.1+)

v5.1 added composable rule expressions — multiple rules with grouped boolean logic rather than the flat all/any. Verify the live UI and API surface for the current capability.

## Implementation Guidance

### Creating a Promotion Programmatically

```ruby
promo = Spree::Promotion.create!(
  name: 'Welcome 10% off',
  code: 'WELCOME10',
  match_policy: 'all',
  starts_at: Time.current,
  expires_at: 30.days.from_now,
  usage_limit: 1000
)

# Rule: first order
promo.promotion_rules.create!(
  type: 'Spree::Promotion::Rules::FirstOrder'
)

# Action: 10% off the whole order
action = promo.promotion_actions.create!(
  type: 'Spree::Promotion::Actions::CreateAdjustment'
)
action.calculator = Spree::Calculator::FlatPercentItemTotal.new(preferred_flat_percent: 10)
action.save!
```

### Applying a Coupon in Code

```ruby
# Storefront flow
Spree::PromotionHandler::Coupon.new(order).apply
# Returns a status: successful / failed / not-found
```

(Verify the exact class name — Spree has refactored coupon handlers several times.)

### Auto-Apply Promotions

For promos with no coupon code, run the auto-apply handler on cart/order updates:

```ruby
Spree::PromotionHandler::Cart.new(order).activate
```

This is wired into the order updater pipeline by default.

### Custom Rule

```ruby
# app/models/my_app/promotion/rules/loyalty_tier.rb
class MyApp::Promotion::Rules::LoyaltyTier < Spree::PromotionRule
  preference :tier, :string, default: 'gold'

  def applicable?(promotionable)
    promotionable.is_a?(Spree::Order)
  end

  def eligible?(order, options = {})
    order.user&.loyalty_tier == preferred_tier
  end
end

# Register in an initializer
Spree::Promotion::Rules.register(MyApp::Promotion::Rules::LoyaltyTier)
```

Verify the registration API in the current release — the registry pattern occasionally changes.

### Custom Action

```ruby
class MyApp::Promotion::Actions::FreeGift < Spree::PromotionAction
  def perform(payload = {})
    order = payload[:order]
    order.line_items.create!(variant: gift_variant, quantity: 1, price: 0)
  end
end
```

### Custom Calculator

```ruby
class MyApp::Calculator::WeekendDiscount < Spree::Calculator
  preference :weekend_percent, :decimal, default: 15

  def self.description
    'Weekend Discount'
  end

  def compute(object)
    return 0 unless [0, 6].include?(Date.current.wday)
    object.amount * (preferred_weekend_percent / 100.0) * -1
  end
end

# Register
Rails.application.config.spree.calculators.promotion_actions.create_adjustment << MyApp::Calculator::WeekendDiscount
```

### Coupon Batch Import

v5.0+ ships CSV import for coupon batches:
- Admin → Promotions → batch → Generate codes / Import CSV
- Each row creates a `CouponCode` record tied to the promotion

### Debugging Promotion Not Applying

1. Check `Order#promotions.eligible?(order)` for each promotion.
2. Inspect each rule's `eligible?` method return value.
3. Verify match_policy: `any` vs `all`.
4. Check expiry: `promo.expires_at > Time.current && promo.starts_at < Time.current`.
5. Check usage limits: `promo.usage_count < promo.usage_limit`.
6. Look at `Adjustment.where(source: action)` to see if it was created but later canceled.

### Common Pitfalls

- **Forgetting calculator preferences** — actions need a calculator with valid preferences or compute returns nil.
- **Custom rule not registered** — Spree doesn't auto-discover; register explicitly.
- **Coupon code typo in admin** — codes are case-sensitive (verify against current behavior).
- **Adjustments lingering after eligibility lost** — recompute via `Spree::OrderUpdater` to drop stale adjustments.
- **Stacking promotions** — by default, multiple eligible promos all apply. To enforce mutual exclusion, set Promotion#exclusive or use match_policy creatively.
- **Free shipping action with no shipping** — silent no-op.

Always verify the rule/action/calculator class registry against the live source — the registration mechanism varies.
