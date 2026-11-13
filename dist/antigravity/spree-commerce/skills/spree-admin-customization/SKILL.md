---
name: spree-admin-customization
description: >
  Customize the Spree v5 Admin Dashboard — Tailwind 4 + Hotwire/Turbo/Stimulus
  stack, the `Spree.admin.navigation` declarative API (v5.2+) for menu items,
  partial injection slots (`store_nav_partials`, `store_products_nav_partials`,
  `store_orders_nav_partials`, `settings_nav_partials`), the Admin SDK
  components + form builder, custom dashboard reports, the Page Builder for
  storefront editing, and theme management. Use when adding admin pages,
  injecting UI into existing screens, or building admin extensions.
---

# Spree Admin Customization

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/admin/navigation for the `Spree.admin.navigation` API.
2. Fetch the v5.2 announcement (https://spreecommerce.org/announcing-spree-5-2/) for the Admin SDK introduction.
3. Inspect the live `spree_admin` (or `spree` umbrella admin) source for current partial slot names — they evolve.
4. For Hotwire/Stimulus patterns, fetch the Rails edge guides plus the live admin codebase.
5. Check release notes for any admin-specific changes (the dashboard was rewritten in v5.0 — v4 patterns don't apply).

## Conceptual Architecture

### The v5 Admin Stack

| Layer | Tech |
|-------|------|
| CSS | Tailwind CSS 4 |
| JS framework | Hotwire (Turbo + Stimulus) |
| Asset pipeline | Propshaft + Importmap (or esbuild) |
| Templates | ERB (server-rendered) |
| Forms | Spree Admin SDK form builder (v5.2+) |

The Bootstrap-based `spree_backend` engine is **archived** — don't port v4 patterns.

### Admin Navigation API (v5.2+)

Declaratively register top-level menu items:

```ruby
# config/initializers/spree.rb
Spree.admin.navigation.register(
  key: :my_reports,
  label: 'My Reports',
  url: '/admin/my_reports',
  icon: 'chart-bar',
  position: 50,
  match_path: %r{^/admin/my_reports}
)
```

Properties (verify against live API):
- `key` — unique symbol
- `label` — display text (i18n key works)
- `url` — relative or named-route helper
- `icon` — Tailwind / Heroicons name
- `position` — sort order
- `match_path` — regex/string for "active" highlighting
- `if:` — proc returning bool for visibility (e.g., role check)

For nested items, use `navigation.register_child` (verify exact API).

### Partial Injection Slots

In v5, admin views expose **partial injection slots** at structural points:

| Slot | Where it lives |
|------|----------------|
| `store_nav_partials` | Main sidebar |
| `store_products_nav_partials` | Product detail/list pages |
| `store_orders_nav_partials` | Order detail/list pages |
| `settings_nav_partials` | Settings section |

Register a partial:

```ruby
# config/initializers/spree.rb
Spree::Admin::NavigationHelper.store_orders_nav_partials << 'my_app/admin/order_extra_actions'
```

Then create the partial:

```erb
<%# app/views/my_app/admin/_order_extra_actions.html.erb %>
<% if local_assigns[:order] %>
  <%= link_to 'Sync to ERP', sync_order_path(order), class: 'btn btn-secondary' %>
<% end %>
```

The slot system replaces the old Deface engine — same goal (inject content into core views) without the CSS-selector fragility.

### Admin SDK (v5.2+)

A set of helpers / components for building admin extensions:

- **Components** — reusable UI elements (cards, tables, action menus) styled to match the dashboard
- **Form builder** — generate Tailwind-styled form fields with built-in validation rendering
- **Stimulus controllers** — for interactive elements

Verify the exact component/helper inventory in the live admin docs.

### Custom Admin Pages

Subclass the Spree admin base controller:

```ruby
# app/controllers/spree/admin/my_reports_controller.rb
module Spree::Admin
  class MyReportsController < Spree::Admin::BaseController
    def index
      @daily_sales = Spree::Order.complete.group_by_day(:completed_at).sum(:total)
    end
  end
end
```

Mount the route:

```ruby
# config/routes.rb
Rails.application.routes.draw do
  Spree::Core::Engine.routes.draw do
    namespace :admin do
      resources :my_reports, only: [:index]
    end
  end
end
```

(Verify the route-drawing helper name — it's occasionally renamed.)

### Authorization

Spree uses **CanCanCan** for authorization. Inject abilities:

```ruby
# app/models/spree/ability_decorator.rb
module SpreeMyExtension::AbilityDecorator
  def initialize(user)
    super
    return unless user.has_spree_role?(:report_viewer)
    can :read, MyApp::Report
  end
end

Spree::Ability.prepend(SpreeMyExtension::AbilityDecorator)
```

### Custom Dashboard Reports

v5 admin has a pluggable reports engine. Register a report:

```ruby
# config/initializers/spree.rb
Spree::Admin::Reports.register(
  key: :my_custom_report,
  name: 'My Custom Report',
  description: 'Daily sales by store',
  partial: 'my_app/admin/reports/my_custom'
)
```

(Verify the live API — reports registry has evolved.)

### Page Builder & Themes

The v5.0+ admin ships a no-code Page Builder for editing storefront pages. Sections (hero, product carousel, blog list, FAQ) compose into pages. Each section is an ERB partial registered with the builder.

Theme management lives in Settings → Themes. Themes bundle:
- A logo, colors, fonts
- A set of section configurations
- Layout choices

Custom sections register via:

```ruby
Spree::PageBuilder::Sections.register(
  key: :featured_grid,
  partial: 'my_app/page_sections/featured_grid',
  schema: { rows: { type: :number, default: 2 } }
)
```

(Verify against live source — Page Builder is new in v5.)

### Stimulus Controllers

Add interactivity via Stimulus:

```javascript
// app/javascript/controllers/my_admin_widget_controller.js
import { Controller } from '@hotwired/stimulus';

export default class extends Controller {
  static targets = ['output'];

  connect() {
    this.outputTarget.textContent = 'Hello from extension';
  }
}
```

Register through importmap:

```ruby
# config/importmap.rb
pin 'controllers/my_admin_widget_controller', to: 'my_admin_widget_controller.js'
```

(Or via esbuild config if the project uses esbuild instead.)

## Implementation Guidance

### Adding an Admin Page From Scratch

1. Add navigation entry in `config/initializers/spree.rb`
2. Create controller under `app/controllers/spree/admin/`
3. Create views under `app/views/spree/admin/`
4. Mount routes under the Spree engine namespace
5. Update `Ability` decorator for permissions
6. Style with Tailwind classes that match admin conventions

### Injecting Into an Existing Page

Always prefer **partial slots** over view overrides:

```ruby
Spree::Admin::NavigationHelper.store_products_nav_partials << 'my_app/admin/product_seo_tools'
```

If no slot exists for what you need, prefer **opening a PR upstream** to add one rather than overriding the whole view.

### Building With the Admin SDK

```erb
<%# Using the SDK form builder %>
<%= spree_admin_form_for @product do |f| %>
  <%= f.text_field :name, label: t('.name'), required: true %>
  <%= f.rich_text_field :description %>
  <%= f.collection_select :tax_category_id, Spree::TaxCategory.all, :id, :name, label: 'Tax Category' %>
  <%= f.submit %>
<% end %>
```

(Verify against live SDK helper names.)

### Theming for Tailwind 4

Configure brand colors via Tailwind 4's `@theme` directive (Spree v5 uses Tailwind 4):

```css
/* app/assets/tailwind/application.css */
@import 'tailwindcss';

@theme {
  --color-spree-primary: oklch(0.6 0.18 250);
  --color-spree-secondary: oklch(0.55 0.12 320);
}
```

### Reports With Time-Series

Use the `groupdate` gem for time-grouped queries:

```ruby
@daily_sales = current_store.orders.complete
  .where(completed_at: 30.days.ago..)
  .group_by_day(:completed_at)
  .sum(:total)
```

Render with a chart library like Chartkick, registered as a section partial.

### Common Pitfalls

- **Porting Bootstrap classes from v4 admin** — they won't match v5's Tailwind tokens.
- **Modifying admin views directly** — breaks on upgrade. Use partial slots.
- **Forgetting `Spree::Admin::BaseController`** — without it, you lose auth + layout.
- **Adding routes outside the Spree engine** — admin URL helpers won't generate.
- **Stimulus controller not connecting** — importmap pinning wrong, or `data-controller` attribute wrong.
- **Ability decorator not loaded** — engine `to_prepare` hook missing.
- **Building a page that bypasses CanCanCan** — security regression; always `authorize!` in controllers.

Always re-fetch the live admin navigation API and partial slot list — they're the parts of the admin most likely to evolve.
