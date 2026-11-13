---
name: spree-dev-patterns
description: >
  Cross-cutting Spree development patterns — the customization preference
  hierarchy (Events > Webhooks > Dependencies > Decorators),
  `Spree::Dependencies` service-object swapping, the `_decorator.rb` + `prepend`
  + `self.prepended` idiom, idempotent subscribers and webhook receivers,
  multi-store scoping discipline, prefixed IDs, calculator polymorphism
  (shipping/promotion/tax share the base), service-object composition with
  `dry-monads` or simple results, why to avoid `class_eval` reopening and
  Deface, and Spree-on-Rails idioms (Hotwire/Turbo Stimulus, ActiveStorage,
  Action Cable, Sidekiq). Use when designing the architecture of a Spree
  extension or solving cross-cutting concerns.
---

# Spree Development Patterns

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/customization/decorators for the modern decorator pattern.
2. Inspect `lib/spree/dependencies.rb` in the live `spree` gem for the current swappable-services registry.
3. Read the Spree blog's developer posts for current best practices: https://spreecommerce.org/blog.
4. For Rails idioms, cross-reference the Rails 7+ guides.
5. Check the v5.4 announcement's AGENTS.md mention — Spree ships AI-coding rules.

## Pattern: The Customization Hierarchy

Always reach for the lowest-numbered tool that solves your problem:

| Priority | Tool | When |
|----------|------|------|
| **1** | Event Subscriber | React to a domain change asynchronously |
| **2** | Webhook | Notify an external system |
| **3** | `Spree::Dependencies` swap | Change a service object's behavior |
| **4** | Admin Navigation + Partials | Add UI to admin |
| **5** | Decorator (`prepend`) | Last resort for model/controller customization |

Higher numbers tie you tighter to Spree internals and break more often on upgrade.

## Pattern: The Decorator Idiom

```ruby
# app/models/spree/product_decorator.rb
module MyApp::ProductDecorator
  def self.prepended(base)
    # Class-level additions go here
    base.has_many :reviews, class_name: 'MyApp::Review'
    base.validates :seo_title, length: { maximum: 70 }, allow_nil: true
    base.scope :featured, -> { where(featured: true) }
  end

  # Instance-method overrides — call `super` to preserve core behavior
  def display_name
    seo_title.presence || super
  end
end

Spree::Product.prepend(MyApp::ProductDecorator) unless Spree::Product.include?(MyApp::ProductDecorator)
```

Three things to never forget:
- File ends with `_decorator.rb`
- `prepend`, not `include` (so `super` works)
- Guard against double-prepend (the `unless` clause)

## Pattern: `Spree::Dependencies` Service Swapping

```ruby
# config/initializers/spree.rb
Spree::Dependencies.cart_add_item_service = MyApp::CartAddItemService
Spree::Dependencies.shipping_rate_estimator = MyApp::CustomEstimator
Spree::Dependencies.order_updater_class = MyApp::OrderUpdater
```

Your service must implement the **same public contract** as the one it replaces. Extend rather than rewrite:

```ruby
class MyApp::CartAddItemService < Spree::Cart::AddItem
  def call(order:, variant:, quantity: 1, options: {})
    result = super
    apply_custom_logic(result, options)
    result
  end
end
```

## Pattern: Idempotent Subscribers

Events fire **at least once** in some failure modes (process restart mid-publish, retry). Make handlers idempotent:

```ruby
class OrderCompletedSubscriber < Spree::Subscriber
  subscribes_to 'order.completed'
  on 'order.completed', :handle

  def handle(event)
    order = event.order
    # Idempotency key: order ID + state transition
    return if AccountingSync.where(order_id: order.id).exists?

    AccountingSync.create!(order: order, synced_at: Time.current)
    AccountingApiClient.push(order)
  end
end
```

For webhook receivers, use the event's unique ID + a processed_events table.

## Pattern: Multi-Store Scoping Discipline

Every customer-facing query should scope by store:

```ruby
# Bad
Spree::Product.active.featured

# Good
current_store.products.active.featured

# In a service / job, pass store explicitly
class MyApp::Service
  def initialize(store:)
    @store = store
  end

  def call
    @store.orders.complete
  end
end
```

Code reviews should flag any query that uses a bare `Spree::Order.…` or `Spree::Product.…` in customer-facing code.

## Pattern: Prefixed IDs (v5.4+)

API v3 exposes prefixed IDs (`prod_…`, `ord_…`). Don't expose raw DB IDs to external clients. The model gives you both:

```ruby
order.id           # 12345 (internal database ID)
order.prefixed_id  # "ord_01HXVZK..."
```

Treat prefixed IDs as opaque strings — sortable but otherwise meaningless to consumers.

## Pattern: Calculator Polymorphism

Spree's `Calculator` base class powers:
- Shipping cost (`ShippingMethod#calculator`)
- Promotion discounts (`PromotionAction#calculator`)
- Tax rates (`TaxRate#calculator`)

```ruby
class MyApp::Calculator::PercentOver100 < Spree::Calculator
  preference :percent, :decimal, default: 10

  def self.description
    'Percent off when cart exceeds 100'
  end

  def compute(object)
    return 0 if object.amount < 100
    object.amount * (preferred_percent / 100.0) * -1
  end
end
```

Register where appropriate:

```ruby
Rails.application.config.spree.calculators.promotion_actions.create_adjustment << MyApp::Calculator::PercentOver100
```

## Pattern: Service-Object Composition

Spree's service objects return either the result or raise. Common pattern:

```ruby
class MyApp::OrderProcessor
  def initialize(order:)
    @order = order
  end

  def call
    enrich_metadata
    notify_subscribers
    @order
  end

  private

  attr_reader :order

  def enrich_metadata
    order.metafields.find_or_create_by(namespace: 'my_app', key: 'processed_at') do |m|
      m.value = Time.current.iso8601
    end
  end

  def notify_subscribers
    Spree::Bus.publish('my_app.order_processed', order: order)
  end
end
```

For functional-style result handling, integrate `dry-monads`:

```ruby
class MyApp::OrderProcessor
  include Dry::Monads[:result]

  def call(order:)
    enriched = enrich_metadata(order)
    return Failure(:enrichment_failed) if enriched.nil?
    notify(order)
    Success(order)
  end
end
```

Use whichever style your team is consistent on.

## Pattern: Avoid `class_eval` Reopening

```ruby
# BAD
Spree::Product.class_eval do
  def display_name
    seo_title.presence || name
  end
end
```

This breaks autoloading in development and has no override semantics for `super`. Use a decorator module + `prepend` instead.

## Pattern: Avoid Deface in v5

Deface was a CSS-selector view-override engine for the legacy ERB frontend. In v5:
- Deface only works on ERB views — and v5 admin is Hotwire/Turbo with **partial slots** instead
- Deface overrides are silently no-ops on missing virtual paths
- The Page Builder + slot system replace Deface in modern Spree

If you find yourself wanting Deface, ask:
1. Can I use a partial slot? (Yes → use it)
2. Can I customize via Page Builder section? (Yes → use it)
3. Can I patch in the storefront repo? (Yes — for Next.js storefront customizations)

## Pattern: Hotwire / Turbo / Stimulus

Spree v5 admin is Hotwire-native. Conventions:

- **Turbo Frames** for partial page updates (lazy-loaded panels)
- **Turbo Streams** for server-driven DOM updates (after an action)
- **Stimulus** controllers for client-side interactivity

```javascript
// app/javascript/controllers/order_quick_actions_controller.js
import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
  static targets = ['button'];

  async refund(event) {
    event.preventDefault();
    const response = await fetch(this.buttonTarget.dataset.url, { method: 'POST', headers: this.headers() });
    if (response.ok) this.buttonTarget.disabled = true;
  }

  headers() {
    return {
      'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
      'Accept': 'text/vnd.turbo-stream.html'
    };
  }
}
```

```erb
<div data-controller="order-quick-actions">
  <%= button_to 'Refund', refund_order_path(order),
                method: :post,
                data: { 'order-quick-actions-target': 'button', action: 'order-quick-actions#refund' } %>
</div>
```

## Pattern: Sidekiq for Anything Non-Trivial

Anything that:
- Hits an external API
- Sends an email
- Processes an image
- Updates >100 records
- Could take >100ms

…belongs in a Sidekiq job, not a controller action.

```ruby
class MyApp::SyncToErpJob < ApplicationJob
  queue_as :default

  def perform(order_id)
    order = Spree::Order.find(order_id)
    ErpClient.upsert(order)
  end
end

# Enqueue from a subscriber
MyApp::SyncToErpJob.perform_later(order.id)
```

## Pattern: Don't Modify Core Files

Never edit `vendor/bundle/.../spree/...`. Two reasons:
1. Bundle install wipes your changes
2. Upgrades become impossible

Use decorators, dependencies, subscribers, and slots — that's why they exist.

## Pattern: Versioning Your Extension

```ruby
# lib/spree_my_extension/version.rb
module SpreeMyExtension
  VERSION = '1.2.3'
end
```

Tag releases, pin to Spree minor in gemspec:

```ruby
# spree_my_extension.gemspec
spec.add_dependency 'spree', '>= 5.4', '< 6.0'
```

Test against multiple Spree minors in CI.

## Pattern: Spree's AGENTS.md (v5.4+)

v5.4 ships an `AGENTS.md` at the repo root — AI-coding rules for tools like Claude Code and Cursor. Read it when you adopt a new Spree version; it codifies the customization hierarchy and code-style conventions.

## Anti-Pattern Roundup

- **Decorating to add a feature you could subscribe to** → use events
- **Class-reopening with `class_eval`** → use `prepend` decorator
- **Modifying Order totals manually** → use `Spree::OrderUpdater`
- **Storing API keys in browser code** → use httpOnly cookies + server actions
- **Skipping multi-store scoping** → leak attack
- **Ignoring `Spree::Dependencies` in favor of decorators** → tight coupling
- **Custom admin views instead of partial slots** → upgrade pain
- **Using Deface in v5** → silent no-op
- **Adding `spree_auth_devise` to a new v5 project** → archived gem
- **Building features in controllers instead of service objects** → untestable

---

Always read `AGENTS.md` (v5.4+) and the latest customization docs before designing a non-trivial extension. The patterns evolve; what was idiomatic in v4 is wrong in v5.
