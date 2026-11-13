---
name: spree-upgrades
description: >
  Upgrade a Spree application — version-to-version migration paths (v4 → v5 is
  a major rewrite; v5.x → v5.y are simpler), Gemfile pinning strategy, decorator
  brittleness across versions, deprecated gems to remove (`spree_auth_devise`,
  `deface`, `spree_backend`), API v2 → v3 migration via `spree_legacy_api_v2`,
  admin Bootstrap → Tailwind transition, the upgrade guide workflow, and
  rollback strategy. Use when planning a Spree upgrade or auditing technical
  debt blocking one.
---

# Spree Upgrades

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/upgrades/quickstart for the canonical upgrade flow.
2. Read the release notes for **every minor** between your current and target versions at https://github.com/spree/spree/releases.
3. Cross-reference the announcement posts for each major (v5.0, v5.2, v5.4).
4. Check the deprecated-gems list — `spree_auth_devise`, `deface`, `spree_backend` are all archived.
5. Inspect your Gemfile + `gemfile.lock` against the target Spree version's `spree.gemspec`.

## Conceptual Architecture

### The Two Upgrade Shapes

| Path | Effort | Risk |
|------|--------|------|
| **v4.x → v5.0** | **Major** — admin rewrite, frontend removed, API restructure | High; plan as a project |
| **v5.x → v5.y** | Minor — Gemfile bump, migrations, regression test | Moderate |
| **v5.y → v5.y+1 patch** | Trivial — bundle update | Low |

### What Changed v4 → v5

The biggest single jump in Spree's history:
- **Admin rewritten** in Tailwind + Hotwire (was Bootstrap + jQuery). All v4 admin customizations break.
- **Legacy ERB frontend removed.** Sites on `spree_frontend` need to migrate to the Next.js storefront or `spree-rails-storefront`.
- **Engines consolidated.** `spree_backend`, `spree_frontend`, `spree_storefront_api_v2`, `spree_platform_api` merged into the `spree` umbrella gem.
- **`spree_auth_devise` deprecated.** v5 ships Devise auth in-core; old gem archived Feb 2026.
- **Deface deprecated.** It only worked on the v4 ERB frontend.
- **Metafields, Themes, Page Builder, CSV import/export added** as new features.
- **API v2 (JSON:API)** is still available in v5.0–5.3 in core; extracted to `spree_legacy_api_v2` in v5.4+.

### What Changed v5.0 → v5.4

| Version | Headline change |
|---------|----------------|
| **v5.1** | Advanced rule-based promotions engine |
| **v5.2** | `create-spree-app` CLI; Admin SDK; CSV importer overhaul; Tailwind 4 in storefront; `spree_dev_tools` gem; AI coding rules shipped |
| **v5.3** | Price Lists for customer-segment overrides |
| **v5.4** | **API v3 (flat JSON, prefixed IDs, OpenAPI 3.0, 10× faster)**, `@spree/sdk` TypeScript SDK, Next.js 16 storefront, Payment Sessions, Markets, MeiliSearch integration, Webhooks 2.0, EU Omnibus 30-day price history, multi-arch Docker images, AGENTS.md |

### Gemfile Pinning Strategy

```ruby
# Pin per minor for predictability
gem 'spree', '~> 5.4'   # accepts 5.4.0–5.4.99 patches
# Avoid
gem 'spree'             # any 5.x — surprise breakage
gem 'spree', '5.4.2'    # locks you to a patch; misses bug fixes
```

For extensions:
```ruby
spec.add_dependency 'spree', '>= 5.4', '< 6.0'
```

Run `bundle update spree` to take patch releases.

### Decorator Brittleness

Decorators (`*_decorator.rb` with `prepend`) are upgrade-fragile. When upgrading:
1. **Audit every decorator** — does the decorated method still exist? Same signature?
2. **Run the test suite** after the version bump
3. **Watch for `NoMethodError` in `super`** — the underlying method was renamed
4. **Watch for new validations** — your decorator may conflict with new core rules

Reduce risk by preferring **events** and **dependencies** over decorators (see `spree-extensions` skill).

### Deprecated Gems to Remove

| Gem | Action |
|-----|--------|
| `spree_auth_devise` | **Remove**; archived. v5 has built-in auth. |
| `spree_backend` | **Remove**; replaced by Tailwind admin in `spree` umbrella. |
| `spree_frontend` | **Remove**; replaced by Next.js storefront or `spree-rails-storefront`. |
| `deface` | **Remove** when fully off the ERB frontend. Use partial slots in v5 admin. |
| `spree_api` (separate gem) | **Remove**; now in `spree` umbrella. |
| `spree_storefront_api_v2` (separate gem) | **Remove**; either bundled or use `spree_legacy_api_v2`. |
| `spree_platform_api` (separate gem) | **Remove**; same. |

### API v2 → v3 Migration

Side-by-side strategy:
1. v5.4+ project includes both `/api/v3/` (built-in) and `/api/v2/` (via `spree_legacy_api_v2`)
2. Build new clients on v3
3. Migrate existing clients one surface at a time
4. Monitor v2 traffic; sunset after N weeks of zero usage
5. Eventually remove `spree_legacy_api_v2` from Gemfile

### Admin Customization Migration

- **Deface overrides** → translate to partial injection slots OR opt out (often the slot system is sufficient)
- **Bootstrap CSS** → translate to Tailwind classes (use the Spree v5 admin views as reference)
- **Custom admin layouts** → re-implement against v5's Tailwind/Hotwire base layout
- **jQuery code** → port to Stimulus controllers

### Storefront Migration

- **Legacy ERB frontend** → either:
  - Fork `spree/storefront` (Next.js) and migrate over weeks
  - Use `spree-rails-storefront` (Tailwind page-builder ERB storefront) for minimal change

Plan as a separate project, not a Gemfile bump.

## Implementation Guidance

### Pre-Upgrade Audit

Before changing the Gemfile:

1. **Inventory decorators** — `grep -r '_decorator.rb' app/` and `grep -r '.prepend(' app/`
2. **Inventory Deface overrides** — `grep -r 'Deface::Override' app/`
3. **Inventory custom admin views** — `find app/views/spree/admin -name '*.erb'`
4. **Inventory custom controllers** — `find app/controllers/spree -name '*.rb'`
5. **Inventory subscribers** — `find app/subscribers -name '*.rb'`
6. **Inventory custom payment methods, calculators, services**
7. **Map all current Gemfile entries** to their v5 fate (kept / removed / replaced)
8. **List all third-party Spree extensions** — verify each has v5 support

### Upgrade Workflow (v5.x to v5.y)

```bash
# 1. Branch
git checkout -b upgrade-spree-5.x

# 2. Bump
bundle update spree spree_admin spree_emails

# 3. Run migrations
bin/rails db:migrate

# 4. Run specs
bundle exec rspec

# 5. Smoke test admin + storefront
bin/rails server
# manually browse, place a test order

# 6. Deploy to staging
# run a fuller regression suite

# 7. Deploy to prod
```

### Upgrade Workflow (v4 → v5) — Project-Sized

1. **Stand up a parallel v5 environment** with same data (use `db/structure.sql` import + data export)
2. **Migrate decorators** one model at a time
3. **Migrate admin customizations** to partial slots / new conventions
4. **Choose storefront path** — Next.js (highest-fidelity for modern UX) or `spree-rails-storefront` (least change)
5. **Migrate frontend** — this is often 50%+ of the project
6. **Migrate payment integrations** — install v5-compatible gateway gems
7. **Cutover plan** — data migration, DNS switch, monitoring

### Rolling Back

- **Always tag the release** before deploying
- **Database migrations**: design backward-compatible (additive only; drops in a later release)
- **Rolling deploy with multiple pods** lets you halt mid-deploy if alerts fire
- **DB rollback** is a last resort — `bin/rails db:rollback` only works if migrations are reversible

### Test Coverage as Upgrade Insurance

Before upgrading:
- **System specs** covering: cart → checkout → order placement
- **API specs** for every consumer-facing v3 endpoint
- **Subscriber specs** for each event you handle
- **Decorator specs** for each model decoration

If coverage is thin, **write tests first**, then upgrade. The cost of bad coverage during an upgrade is far higher than the cost of writing tests.

### Common Upgrade Pitfalls

- **Skipping minors** — v5.0 → v5.4 in one jump misses the v5.2 generator changes that interact with v5.3 PriceList. Step through.
- **Decorator `super` calls a method that no longer exists** — manifests as `NoMethodError` at runtime, not boot.
- **Removed admin views referenced by Deface** — Deface silently no-ops; visual regression.
- **API v2 client breakage when removing the legacy gem** — confirm zero v2 traffic for weeks before removal.
- **Payment gateway gem behind on Spree compatibility** — verify each gem supports the target Spree before bumping.
- **Sidekiq queue names changed** — webhook delivery queue renamed in some minor; check release notes.
- **Migrations slow on large tables** — `add_column` on a 50M-row `spree_orders` can lock. Use `algorithm: :concurrently` for indexes.
- **Tailwind 4 upgrade missed** — v5 admin requires Tailwind 4; v3 syntax doesn't compile.
- **Importmap pinning out of date** — old JS pins resolve to missing modules.
- **`config/credentials.yml.enc` re-encryption** required when Rails version bumps include encryption-format changes.

Always read **every** minor release note from current to target before kicking off — even single-minor upgrades can have caveats hidden in the notes.
