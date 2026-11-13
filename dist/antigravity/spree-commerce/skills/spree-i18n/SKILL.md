---
name: spree-i18n
description: >
  Localize a Spree application — the `spree_i18n` gem with 60+ locale packs,
  the v5.4+ Translations Center for product/CMS content (CSV import/export),
  Rails i18n basics applied to Spree (translation files, locale switching,
  pluralization, interpolation), per-Market locale routing in the headless
  storefront, RTL languages, and translating extensions. Use when localizing a
  Spree store, adding a new locale, or building i18n-aware extensions.
---

# Spree i18n & Localization

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/translations for the v5+ translation model.
2. Fetch https://github.com/spree-contrib/spree_i18n (README) for the current locale-pack inventory.
3. Cross-reference https://guides.rubyonrails.org/i18n.html for Rails-side i18n basics.
4. Check the v5.4 announcement for Translations Center features.
5. Verify which locales ship vs. which require the `spree_i18n` gem on top of `spree`.

## Conceptual Architecture

### Two Layers of Localization

| Layer | What it translates |
|-------|--------------------|
| **`spree_i18n` gem** | UI labels — admin chrome, checkout strings, error messages, attribute names |
| **Translations Center (v5.4+)** | Per-record content — product names, descriptions, taxon names, CMS page bodies |

Both layers cooperate — `spree_i18n` localizes the UI shell; Translations Center localizes the *data inside* the shell.

### `spree_i18n` Inventory

Provides translation YAML files for 60+ locales (verify against the live gem). Add to Gemfile:

```ruby
gem 'spree_i18n'
```

Locales include English, Spanish, French, German, Italian, Portuguese (BR + PT), Dutch, Polish, Czech, Russian, Ukrainian, Japanese, Korean, Chinese (Simplified + Traditional), Arabic, Hebrew, Turkish, Hindi, and many more.

### Setting Available and Default Locales

```ruby
# config/application.rb
config.i18n.available_locales = %i[en de fr es it]
config.i18n.default_locale = :en
config.i18n.fallbacks = true
```

Per-Store locale (v5+):
```ruby
Spree::Store.default.update!(default_locale: 'de', supported_locales: 'en,de,fr')
```

### Locale Switching in Requests

In the storefront (Next.js), locale is part of the URL: `/de/products/...`. In Rails admin, locale comes from `current_user.locale` or a `?locale=de` param.

```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :set_locale

  def set_locale
    I18n.locale = params[:locale] || current_store.default_locale || I18n.default_locale
  end

  def default_url_options
    { locale: I18n.locale }
  end
end
```

### Translations Center (v5.4+)

For content stored in DB (product names, descriptions, taxon labels, CMS pages, blog posts), Spree v5.4+ provides the **Translations Center** — an admin UI + CSV import/export to manage per-record translations.

The underlying mechanism is **Mobility** (or similar — verify the gem Spree uses currently) which stores translations in JSON columns or sidecar tables:

```ruby
product.name        # current locale
I18n.with_locale(:de) { product.name }  # German
product.name_translations  # { 'en' => 'Tee', 'de' => 'T-Shirt' }
```

### CSV Import/Export Flow

1. Admin → Translations → Export → choose models + locales → download CSV
2. Send to translators (or feed to a translation service)
3. Re-import → Spree updates per-record translations
4. Background job (Sidekiq) processes large imports

### Per-Market Locale Routing (Headless)

The Next.js storefront's market routing handles locale:

```
/us/en/products/classic-tee     -> US market, English
/de/de/produkte/classic-tee     -> DE market, German
/eu/fr/produits/classic-tee     -> EU market, French
```

Routes are localizable — the storefront generates language-specific slugs.

### RTL Languages

Arabic, Hebrew, Persian. Tailwind 4 has built-in RTL support via `dir="rtl"` on the `<html>` element. The Spree storefront includes RTL CSS variants — verify on the current release.

```html
<html lang="ar" dir="rtl">
```

### Date / Currency / Number Formatting

Use Rails' built-in helpers:

```ruby
I18n.l(order.created_at, format: :short)   # localized date
number_to_currency(product.price, locale: I18n.locale)
```

### Translating an Extension

```yaml
# config/locales/en.yml
en:
  spree_my_extension:
    products:
      featured_label: "Featured"
      out_of_stock: "Currently unavailable"
```

```erb
<%= t('spree_my_extension.products.featured_label') %>
```

For other locales, ship parallel YAML files (`de.yml`, `fr.yml`).

## Implementation Guidance

### Adding a New Locale to an Existing Store

```bash
bundle add spree_i18n
```

```ruby
# config/application.rb
config.i18n.available_locales = config.i18n.available_locales + [:ja]
```

```ruby
# In admin or via console
Spree::Store.default.update!(supported_locales: 'en,ja')
```

Then translate per-record content via Translations Center.

### Translating Validation Messages

Spree's validation messages live in `spree_i18n`'s locale files. Override for a specific message:

```yaml
# config/locales/en.yml
en:
  errors:
    messages:
      blank: "is required"
  activerecord:
    errors:
      models:
        spree/order:
          attributes:
            email:
              blank: "We need your email to contact you"
```

### Localizing Email Templates

```ruby
# app/mailers/spree/order_mailer.rb (or decorator)
def confirm_email(order, resend = false)
  @order = order
  I18n.with_locale(order.user&.locale || order.store.default_locale) do
    mail(to: @order.email, subject: t('.subject', store: @order.store.name))
  end
end
```

### Translating Product Names Programmatically

```ruby
product.name_translations = { 'en' => 'Classic Tee', 'de' => 'Klassisches T-Shirt' }
product.save!
```

(Verify the exact column / method name for translation storage in your version.)

### URL Slug Translations

For SEO, taxons and products can have per-locale slugs:

```ruby
taxon.slug_translations  # { 'en' => 'shirts', 'de' => 'hemden' }
```

The storefront's router resolves `/de/hemden/...` to the right taxon.

### Pluralization

```yaml
en:
  cart:
    items:
      one: "1 item"
      other: "%{count} items"
```

```erb
<%= t('cart.items', count: @cart.line_items.sum(:quantity)) %>
```

For locales with complex plural rules (Polish, Russian, Arabic), Rails i18n + the cldr-rules backend handles them — verify the gem.

### Testing Translations

```ruby
RSpec.describe 'Checkout', type: :system do
  context 'in German' do
    before { I18n.locale = :de }
    after { I18n.locale = :en }

    it 'shows German UI' do
      visit '/de/cart'
      expect(page).to have_content('Warenkorb')
    end
  end
end
```

### Common Pitfalls

- **Forgetting to add the locale to `available_locales`** — Rails falls back to default silently.
- **Hardcoding strings in extension views** — extracts run finds untranslated ones; lint with `i18n-tasks`.
- **Per-store locales not enforced** — `Store#supported_locales` is descriptive; you still need URL routing to enforce.
- **CSV imports overwriting recent edits** — back up before bulk import.
- **RTL CSS bleeding into LTR sections** — test mixed-direction layouts.
- **Date formats inconsistent** — define `:short`, `:long`, `:default` formats per locale.
- **Slugs not translated** — fine for English-only sites, breaks SEO for multi-language.
- **Translation Center disabled** — older Spree versions don't have it; users hit a 404.

Always cross-reference `spree_i18n` for locale-pack coverage and the v5.4 Translations Center docs for per-record translation patterns.
