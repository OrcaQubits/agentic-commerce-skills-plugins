---
name: spree-shipping-fulfillment
description: >
  Build and customize Spree's shipping and fulfillment — ShippingMethod,
  ShippingCategory, Zone/ZoneMember, ShippingRate, the Stock::Estimator service,
  StockLocation/StockItem/StockMovement, multi-shipment orders,
  ShippingCalculator classes (FlatRate, FlatPercentItemTotal, PerItem,
  FlexiRate), shipment state machine, returns (ReturnAuthorization →
  CustomerReturn → Reimbursement → Refund), and integrating carrier APIs (UPS,
  FedEx, ShipStation). Use when configuring shipping rules, building fulfillment
  integrations, or debugging shipping-rate calculations.
---

# Spree Shipping & Fulfillment

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/architecture (shipping section) for the current model graph.
2. Inspect `Spree::Stock::Estimator` and `Spree::Stock::Splitter` in the live `spree` gem source.
3. Check the live `Spree::ShippingMethod` source for column names and associations.
4. For carrier integrations, search community gems (`spree-active-shipping`, `spree-ups`, `spree-fedex`) — verify which are maintained for v5.
5. Check release notes for any shipping-related changes (Markets in v5.4 affect shipping availability per region).

## Conceptual Architecture

### The Core Models

| Model | Purpose |
|-------|---------|
| **`ShippingMethod`** | Named shipping option (UPS Ground, FedEx 2-Day) |
| **`ShippingRate`** | Computed cost option offered to the user during checkout |
| **`ShippingCategory`** | Categorize products by shipping needs (Hazmat, Frozen, Standard) |
| **`Zone`** / **`ZoneMember`** | Geographic regions a method ships to |
| **`Shipment`** | A subset of order items shipped together from one StockLocation |
| **`InventoryUnit`** | One unit of a Variant in a Shipment |
| **`StockLocation`** | Physical/logical warehouse |
| **`StockItem`** | Count of a Variant in a StockLocation |
| **`StockMovement`** | Append-only ledger of stock changes |
| **`StockTransfer`** | Move stock between StockLocations |

### Why Multiple Shipments per Order?

If an order's items span multiple `StockLocation`s, Spree creates one `Shipment` per location. The `Spree::Stock::Splitter` allocates items by stock availability and configured policy (closest, fastest, cheapest, etc.).

### ShippingMethod Availability

A ShippingMethod is offered for a Shipment if:
- The ShippingMethod's Zones include the destination
- The Variants' ShippingCategories overlap with the ShippingMethod's allowed categories
- The ShippingMethod is enabled for the current Store
- (v5.4+) The Market for the destination allows this ShippingMethod

### Shipping Calculators

Polymorphic `Calculator` (same base class as promotion/tax calculators):

| Calculator | Math |
|------------|------|
| `Spree::Calculator::Shipping::FlatRate` | Fixed cost |
| `Spree::Calculator::Shipping::FlatPercentItemTotal` | % of cart |
| `Spree::Calculator::Shipping::PerItem` | Per-item flat |
| `Spree::Calculator::Shipping::FlexiRate` | Tiered by total |
| `Spree::Calculator::Shipping::PriceSack` | Free over threshold |
| `Spree::Calculator::Shipping::DigitalDelivery` | Free for digital |

Carrier-API calculators (UPS, FedEx, USPS) come from community gems — they compute rates by calling the carrier's API live.

### Stock::Estimator

`Spree::Stock::Estimator.new(order).shipping_rates(package)` returns the ShippingRate options for a given Package. Replaceable via `Spree::Dependencies`:

```ruby
Spree::Dependencies.shipping_rate_estimator = MyCustomEstimator
```

This is the canonical extension point for custom shipping logic — preferable to decorating the model.

### Shipment State Machine

```
pending → ready → shipped
              ↓
            canceled
```

- `pending` — awaiting payment / stock
- `ready` — paid and stocked, ready to fulfill
- `shipped` — `shipped_at` set, tracking number captured
- `canceled` — canceled with order

### Returns Flow

```
ReturnAuthorization (authorized | canceled)
  └── ReturnItem[]
       ↓
CustomerReturn (when physically received)
  └── ReturnItem[]
       ↓
Reimbursement (pending | reimbursed | errored)
  └── Refund (against original Payment)
   OR StoreCredit
```

## Implementation Guidance

### Setting Up Shipping for a New Store

```ruby
# A US zone
us = Spree::Zone.create!(name: 'US')
us.zone_members.create!(zoneable: Spree::Country.find_by(iso: 'US'))

# A shipping category
standard = Spree::ShippingCategory.find_or_create_by!(name: 'Standard')

# A shipping method
method = Spree::ShippingMethod.create!(
  name: 'Standard Shipping',
  display_on: 'both',
  shipping_categories: [standard],
  zones: [us],
  tax_category: Spree::TaxCategory.find_by(name: 'Shipping')
)
method.calculator = Spree::Calculator::Shipping::FlatRate.new(preferred_amount: 5.00)
method.save!

# A stock location
loc = Spree::StockLocation.create!(
  name: 'Main Warehouse',
  default: true,
  active: true,
  country: Spree::Country.find_by(iso: 'US')
)
```

### Customizing Shipping Rate Selection

If you need custom logic (e.g., "always offer free shipping for Gold customers"):

**Option A — Subscribe to events** (preferred when reacting):

```ruby
class FreeGoldShippingSubscriber < Spree::Subscriber
  subscribes_to 'order.recalculate'
  on 'order.recalculate', :apply_free_shipping
end
```

**Option B — Swap the Estimator** (preferred when modifying rate generation):

```ruby
class MyEstimator < Spree::Stock::Estimator
  def shipping_rates(package, frontend_only = true)
    rates = super
    rates.each { |r| r.cost = 0 } if package.order.user&.gold_tier?
    rates
  end
end

# config/initializers/spree.rb
Spree::Dependencies.shipping_rate_estimator = MyEstimator
```

### Adding a Carrier API Integration

Community gems for UPS/FedEx/USPS exist; verify v5 compatibility before adoption. The pattern:

1. Add a `Spree::Calculator::Shipping::CarrierName` calculator
2. Calculator's `compute(package)` calls the carrier's rate API
3. Authenticate with carrier credentials stored in Rails credentials
4. Cache rates for the cart's lifetime to avoid repeat API calls

### Tracking Numbers and Webhooks

When the fulfillment provider ships:

```ruby
shipment.update!(tracking: 'TRACKING123', shipped_at: Time.current)
shipment.ship!
# Fires shipment.shipped event → webhook → customer email
```

### Stock Management

```ruby
# Increase stock
stock_item.adjust_count_on_hand(10)

# Decrease (validates sufficient stock)
stock_item.reduce_count_on_hand(2)

# Transfer between locations
Spree::StockTransfer.create!(
  source_location: loc_a,
  destination_location: loc_b,
  stock_movements_attributes: [
    { quantity: 5, stock_item_id: source_item.id }
  ]
)
```

### Backorders

If `track_inventory` is on and stock hits zero, Spree marks the InventoryUnit as `backordered`. The shipment goes into `backorder` state until stock returns.

To disable backorders globally:
```ruby
Spree::Config[:allow_backorders] = false
```

Verify the exact preference name in current config.

### Returns Workflow

```ruby
# Customer requests return
ra = Spree::ReturnAuthorization.create!(
  order: order,
  return_items_attributes: items.map { |i| { inventory_unit_id: i.id } },
  stock_location: order.shipments.first.stock_location
)
ra.authorize!

# Warehouse receives
cr = Spree::CustomerReturn.create!(
  return_items: ra.return_items,
  stock_location: ra.stock_location
)

# Reimburse
reimb = Spree::Reimbursement.create!(
  customer_return: cr,
  order: order,
  return_items: cr.return_items
)
reimb.perform!  # creates Refunds and/or StoreCredits
```

### Common Pitfalls

- **Missing ShippingCategory** on a Product → no ShippingMethod can match → checkout fails at `delivery`.
- **Zone doesn't include the country** → no ShippingMethod offered.
- **Multiple StockLocations with overlapping inventory** → unexpected multi-shipment splits. Configure `propagate_all_variants` or pin to a primary location.
- **Carrier API rate-limited during checkout** → cache rates, fall back to flat rate on error.
- **Forgetting to fire `shipped!`** when manually marking a shipment — no event, no email, no webhook.
- **Stock movements without going through `adjust_count_on_hand`** — bypasses the ledger and breaks reconciliation.

Always verify model relationships and calculator names against the live source — shipping is one of the most decoupled subsystems and has community gems that vary in v5 readiness.
