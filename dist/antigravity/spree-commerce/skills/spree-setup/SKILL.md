---
name: spree-setup
description: >
  Bootstrap a new Spree project — `create-spree-app` CLI (v5.2+),
  `spree-starter` Rails backend, the Next.js storefront repo, `bin/rails g
  spree:install`, sample data, Docker Compose, and the PostgreSQL + Redis +
  Sidekiq prerequisites. Use when starting a new Spree project from scratch or
  onboarding an existing repo.
---

# Spree Setup

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/cli/quickstart for the current `create-spree-app` flags and Node/Ruby version requirements.
2. Fetch https://github.com/spree/spree-starter (README) for the Rails-backend starter setup.
3. Fetch https://github.com/spree/storefront (README) for the Next.js storefront prerequisites.
4. Web-search the latest release tag at https://github.com/spree/spree/releases — confirm the current minor version and matching `spree-starter` / `storefront` branch.
5. Check the v5.2 announcement (https://spreecommerce.org/announcing-spree-5-2/) for CLI changes if working on an older project.

## Conceptual Architecture

### Two Repos, One Project

A modern Spree project typically combines:

1. **`spree-starter`** (Rails 7+) — the backend application running the `spree` umbrella gem, admin, APIs, webhooks
2. **`storefront`** (Next.js 16+) — the headless storefront talking to the Rails backend over API v3

The `create-spree-app` CLI scaffolds both. Older projects often have only the Rails app — the headless storefront is opt-in.

### Prerequisites

- **Ruby 3.2+**, **Rails 7.1+** (verify against the Spree version's Gemfile)
- **Node 20+** (for the storefront and admin asset pipeline)
- **PostgreSQL 14+** (MySQL works but Postgres is the recommended path)
- **Redis 7+** (Sidekiq, cache, Action Cable)
- **ImageMagick** or **libvips** for image processing
- **MeiliSearch** (optional, for v5.4+ faceted catalog)

### What `spree:install` Does

The Spree installer initializes:
- Database migrations for all Spree tables
- Default admin user (prompts for email/password)
- Routes mounted at `/admin`, `/api/v3/`, `/api/v2/` (legacy via gem)
- Default `Store`, `Country`, `Zone`, `ShippingMethod`, `PaymentMethod`, `TaxRate`
- Spree initializers (`config/initializers/spree.rb`)
- Optional sample data (`spree_sample:load`)

### Bootstrap Sequences

**Path A — `create-spree-app` (recommended in v5.2+)**:

```bash
npx create-spree-app@latest my-store
cd my-store
# Follow prompts: backend? storefront? Docker? sample data?
```

**Path B — Clone `spree-starter` directly**:

```bash
git clone https://github.com/spree/spree-starter my-store
cd my-store
docker compose up -d        # PostgreSQL + Redis + MeiliSearch
bin/setup                    # bundle install, db:create, db:migrate, spree:install
```

**Path C — Add Spree to an existing Rails app**:

```bash
bundle add spree
bundle add spree_admin       # optional: admin dashboard
bundle add spree_emails      # optional: transactional emails
bin/rails g spree:install
bin/rails db:migrate
```

### Adding the Next.js Storefront

```bash
git clone https://github.com/spree/storefront my-storefront
cd my-storefront
cp .env.example .env.local
# Set SPREE_API_URL and NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY
npm install
npm run dev   # http://localhost:3000
```

The publishable key (`pk_…`) comes from your Spree admin → Settings → API Keys.

### Sample Data

```bash
bin/rails spree_sample:load
```

Loads ~25 demo products, taxonomies, payment methods, shipping methods. Idempotent unless `--force`. Useful for dev, never run in production.

### Docker Compose (from spree-starter)

The starter ships a `docker-compose.yml` with:
- `db` — PostgreSQL 16
- `redis` — Redis 7
- `meilisearch` — MeiliSearch v1 (v5.4+)
- `web` — Puma serving the Rails app
- `sidekiq` — background job worker

### Environment Variables

| Var | Purpose |
|-----|---------|
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection (used by Sidekiq, cache, Action Cable) |
| `SECRET_KEY_BASE` | Rails session/cookie signing key |
| `RAILS_MASTER_KEY` | For `config/credentials.yml.enc` |
| `MEILISEARCH_HOST`, `MEILISEARCH_API_KEY` | v5.4+ search backend |
| `SPREE_API_URL` | Storefront's URL to hit the Rails backend |
| `NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY` | Public publishable key (`pk_…`) for the storefront |

### Setup Decision Checklist

- **Spree version** — pin to the latest stable (verify on releases page); v5.4+ for API v3 + Payment Sessions + `@spree/sdk`.
- **Storefront** — Next.js (recommended), Rails storefront (`spree-rails-storefront`), or headless-only (API-only deployment)?
- **Payment gateway** — Stripe (`spree_stripe`), Adyen (`spree_adyen`), PayPal (`spree_paypal_checkout`)?
- **Search** — MeiliSearch (v5.4+ default), Algolia (community gem), or Postgres full-text only?
- **Auth** — Devise (in-core v5+; never re-add the archived `spree_auth_devise`)? OAuth providers?
- **Multi-store** — single store or multi-store from day one?

### Common Setup Failures

- **`bin/setup` fails on `spree:install`**: missing `imagemagick` / `libvips`. Install OS dependency.
- **`pg gem fails to build`**: install `libpq-dev` (Debian) or `postgresql@16` headers (macOS).
- **Storefront 401s against API**: publishable key not set, or storefront pointed at the wrong `SPREE_API_URL`.
- **MeiliSearch connection refused**: starter expects MeiliSearch on `http://meilisearch:7700` in Docker; on bare-metal, set `MEILISEARCH_HOST=http://localhost:7700`.
- **Admin login 500s**: missing `RAILS_MASTER_KEY` — set the env var or recreate credentials.

Always re-verify against the live `spree-starter` README — bootstrap commands and Docker compose versions move quickly.
