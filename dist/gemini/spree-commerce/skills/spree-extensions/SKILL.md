---
name: spree-extensions
description: >
  Build Spree extensions as Rails engines — gem scaffolding, `bin/rails g
  spree:extension`, mounting routes/migrations/assets, the modern `prepend`
  decorator pattern (`*_decorator.rb` with `self.prepended(base)`), generators
  (`spree:model_decorator`, `spree:controller_decorator`), the four
  customization surfaces in preference order (Events > Webhooks > Dependencies >
  Decorators), Spree::Dependencies for swapping service objects, gem
  release/versioning, and the deprecated Deface engine. Use when building a
  reusable Spree extension or adding non-trivial customization to an app.
---

# Spree Extensions & Decorators

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/customization/decorators for the modern `prepend` pattern.
2. Fetch https://spreecommerce.org/docs/developer/customization/decorators to confirm Deface deprecation status.
3. Inspect any official Spree extension gem (`spree_stripe`, `spree_klaviyo`) for current engine scaffolding.
4. Check the v5.2 announcement for the generator suite added then.
5. Verify the current `Spree::Dependencies` registry by reading `lib/spree/dependencies.rb` in the live gem.

## Conceptual Architecture

### What an Extension Is

A Spree extension is a **Rails engine packaged as a gem**. It can ship:
- Models / migrations / decorators
- Controllers / routes
- Views / assets / JavaScript
- Subscribers / job classes
- Initializers wiring into `Spree::Dependencies` and event bus
- Admin navigation entries

Used the same way as `spree_stripe`, `spree_klaviyo`, `spree_paypal_checkout`.

### Four Customization Surfaces (in preference order)

1. **Events + Webhooks** — react to `Spree::Event` publications via `Spree::Subscriber` or external HTTP receivers. Stable across upgrades.
2. **Dependencies** — swap services via `Spree::Dependencies.foo_service = MyService`. Spree publishes a well-defined registry of replaceable services.
3. **Admin Navigation + Partials** — declarative `Spree.admin.navigation` API + partial injection slots. No code modification.
4. **Decorators (last resort)** — `prepend` to extend a core class. Most fragile; ties you to internals.

Reach for the highest-numbered tool only when lower-numbered tools can't express what you need.

### Generating a New Extension

```bash
gem install spree_cmd   # or use the bundled generator
bin/rails g spree:extension spree_my_extension
```

(Verify the current generator name and flags — `spree_cmd` may have been replaced by the in-`spree` generator suite added in v5.2.)

Produces:

```
spree_my_extension/
├── app/
│   ├── controllers/
│   ├── models/
│   ├── views/
│   ├── subscribers/        # event subscribers
│   ├── decorators/         # _decorator.rb files
│   └── assets/
├── config/
│   ├── routes.rb
│   ├── locales/
│   └── initializers/spree_my_extension.rb
├── db/migrate/             # migrations
├── lib/
│   ├── spree_my_extension/
│   │   ├── engine.rb
│   │   └── version.rb
│   └── spree_my_extension.rb
├── spec/                    # RSpec test suite
├── spree_my_extension.gemspec
└── Gemfile
```

### The Engine File

```ruby
# lib/spree_my_extension/engine.rb
module SpreeMyExtension
  class Engine < ::Rails::Engine
    require 'spree/core'

    isolate_namespace SpreeMyExtension if defined?(SpreeMyExtension)

    engine_name 'spree_my_extension'

    initializer 'spree_my_extension.environment', before: :load_config_initializers do |app|
      # Boot-time wiring (registries, dependencies)
    end

    def self.activate
      cache_klasses = "#{config.root}/app/**/*_decorator*.rb"
      Dir.glob(cache_klasses) do |c|
        Rails.configuration.cache_classes ? require(c) : load(c)
      end
    end

    config.to_prepare(&method(:activate).to_proc)
  end
end
```

The `to_prepare` hook ensures decorators reload in development.

### The Decorator Pattern

Modern Spree decorators use **`Module#prepend`**, not `class_eval` reopening. File naming convention: `app/models/spree/product_decorator.rb` (suffix `_decorator.rb`).

```ruby
# app/models/spree/product_decorator.rb
module SpreeMyExtension::ProductDecorator
  def self.prepended(base)
    base.has_many :promotional_videos, class_name: 'SpreeMyExtension::PromotionalVideo'
    base.validates :seo_title, length: { maximum: 70 }, allow_nil: true
    base.scope :featured, -> { where(featured: true) }
  end

  def display_name
    seo_title.presence || super  # `super` walks up the prepend chain
  end
end

Spree::Product.prepend(SpreeMyExtension::ProductDecorator) unless Spree::Product.include?(SpreeMyExtension::ProductDecorator)
```

**Why `prepend` not `include`**: `prepend` inserts the module *above* the class in the method lookup chain — `super` walks back to the original implementation. This is what allows overriding methods.

### Decorator Generators (v5.2+)

```bash
bin/rails g spree:model_decorator Spree::Product
bin/rails g spree:controller_decorator Spree::Admin::ProductsController
```

Generates the boilerplate file with the right naming convention.

### Spree::Dependencies — Swappable Services

```ruby
# config/initializers/spree.rb
Spree::Dependencies.cart_add_item_service = MyApp::CartAddItemService
Spree::Dependencies.shipping_rate_estimator = MyApp::CustomEstimator
Spree::Dependencies.order_updater_class = MyApp::OrderUpdater
```

Common replaceable services (verify against `lib/spree/dependencies.rb`):
- `cart_add_item_service`, `cart_remove_item_service`, `cart_update_service`
- `order_updater_class`, `order_recalculator`, `order_canceller`
- `shipping_rate_estimator`, `stock_splitter`, `package_factory`
- `tax_calculator`
- `payment_create_service`, `payment_capture_service`
- `pricing_options_factory`

Always implement the **same public contract** as the service you replace.

### When to Decorate vs. Use Dependencies

| Need | Approach |
|------|----------|
| Add a column to Product | Migration (or Metafield, no decorator) |
| Add a validation to Product | Decorator |
| Add a method to Product | Decorator |
| Change cart-add behavior globally | `Spree::Dependencies.cart_add_item_service = ...` |
| React to an order completing | Subscriber |
| Change how shipping rates are computed | Replace `shipping_rate_estimator` |
| Add an admin menu item | `Spree.admin.navigation.register(...)` |
| Override an admin view | Partial injection slots; avoid Deface in v5 |

### Deface (Deprecated in v5)

Deface used CSS-selector view overrides on ERB:

```ruby
# DEPRECATED — only works on legacy v4 ERB frontend
Deface::Override.new(
  virtual_path: 'spree/admin/products/index',
  name: 'add_button',
  insert_top: "table.product-list",
  text: '<th>Custom Column</th>'
)
```

In v5+:
- Admin views: use partial injection slots (`store_products_nav_partials`, etc.)
- Storefront views: customize the Next.js storefront directly

### Versioning Extensions

Pin the gemspec to Spree version ranges:

```ruby
# spree_my_extension.gemspec
spec.add_dependency 'spree', '~> 5.4'
```

Test against multiple Spree minor versions in CI before releasing.

## Implementation Guidance

### Adding a Field to a Spree Model

**First, try Metafields** (no migration, upgrade-safe):

```ruby
product.metafields.create!(namespace: 'my_app', key: 'editor_pick', value: 'true')
```

**If you need indexed / queryable data, write a migration**:

```ruby
# db/migrate/20260512_add_editor_pick_to_spree_products.rb
class AddEditorPickToSpreeProducts < ActiveRecord::Migration[7.1]
  def change
    add_column :spree_products, :editor_pick, :boolean, default: false, null: false
    add_index :spree_products, :editor_pick
  end
end
```

Plus a thin decorator if you need scopes/validations:

```ruby
module MyApp::ProductDecorator
  def self.prepended(base)
    base.scope :editor_picks, -> { where(editor_pick: true) }
  end
end
Spree::Product.prepend(MyApp::ProductDecorator)
```

### Replacing a Service Object

```ruby
# app/services/my_app/cart_add_item_service.rb
module MyApp
  class CartAddItemService < Spree::Cart::AddItem
    def call(order:, variant:, quantity: 1, options: {})
      # custom logic
      result = super
      # post-processing
      result
    end
  end
end

# config/initializers/spree.rb
Spree::Dependencies.cart_add_item_service = MyApp::CartAddItemService
```

Always extend rather than rewrite — call `super` to preserve core behavior.

### Avoiding Common Decorator Pitfalls

- **Don't decorate to call observers** — emit/subscribe to events instead.
- **Don't decorate controllers to add filters** — use Rails middleware or before_action in a sibling controller.
- **Don't open `Spree::Order` and add methods directly** — wrap in a decorator module so it's reloadable.
- **Don't forget `unless Spree::Foo.include?` guard** — double-prepend on autoload chains causes infinite loops.

### Testing Decorators

```ruby
# spec/models/spree/product_decorator_spec.rb
require 'rails_helper'

RSpec.describe Spree::Product do
  describe '#display_name' do
    let(:product) { build(:product, seo_title: 'Premium Tee') }

    it 'returns seo_title when present' do
      expect(product.display_name).to eq('Premium Tee')
    end
  end
end
```

### Common Pitfalls

- **Forgetting `to_prepare` reload hook** — decorators don't reload in dev; only fire once at boot.
- **`include` instead of `prepend`** — method override doesn't work; `super` goes wrong way.
- **Decorating before the class is loaded** — autoloading gotchas. Use the engine's `activate` pattern.
- **Adding a `_decorator.rb` outside `app/`** — won't be picked up.
- **Engine asset paths** — Rails 7 propshaft and importmaps require explicit asset declaration.
- **Pinning Spree too tightly** — `gem 'spree', '5.4.2'` breaks on every patch. Use `~> 5.4` instead.

Always verify the engine scaffolding and generator names against current `spree` gem docs — the generator suite is evolving (v5.2 added Admin SDK generators).
