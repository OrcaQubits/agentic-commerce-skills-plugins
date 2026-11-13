---
name: spree-deployment
description: >
  Deploy Spree to production — PostgreSQL + Redis + Sidekiq stack, Docker
  multi-arch images on GHCR, the `spree-starter` Dockerfile + Compose,
  Heroku/Render/Fly.io/AWS targets, env-var conventions, RAILS_MASTER_KEY, asset
  precompilation (Tailwind 4 + Propshaft), Action Cable, MeiliSearch indexing,
  S3 / ActiveStorage for media, log/observability setup, zero-downtime deploys,
  and migration strategy. Use when going from local dev to production, scaling
  Spree, or troubleshooting deploys.
---

# Spree Deployment

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/deployment/database for the database setup story.
2. Inspect the `spree-starter` `Dockerfile` and `docker-compose.yml` for the current production stack.
3. Check the v5.4 announcement for multi-arch GHCR images and Docker improvements.
4. For your target platform, fetch its own Spree / Rails deployment guide (Heroku Ruby buildpack, Render Rails template, Fly.io Rails recipe).
5. Verify Sidekiq + Redis versions against the Gemfile.lock.

## Conceptual Architecture

### The Production Stack

| Tier | Component |
|------|-----------|
| **Web** | Puma serving the Rails app (Spree API + admin) |
| **Worker** | Sidekiq processing background jobs |
| **DB** | PostgreSQL 14+ (recommended) or MySQL 8 |
| **Cache + Jobs** | Redis 7+ |
| **Search** | MeiliSearch (v5.4+) or Algolia or Postgres FTS |
| **Media** | S3-compatible (ActiveStorage) |
| **Email** | SMTP (SendGrid, Postmark, SES) |
| **CDN** | CloudFront, Cloudflare, or platform-native |
| **Front-end (headless)** | Vercel for Next.js storefront |
| **Observability** | Sentry, Datadog, New Relic, AppSignal |

### What Each Component Does

- **Puma** — serves HTTP. The default config in spree-starter is multi-worker, multi-thread.
- **Sidekiq** — webhook delivery, email sending, image processing, search indexing, CSV imports.
- **PostgreSQL** — primary data store. Use pg_search (built-in to v5+ for full-text search if MeiliSearch isn't used).
- **Redis** — Sidekiq queues, Rails cache, Action Cable broadcasts.
- **MeiliSearch** — faceted product search (v5.4+ default).
- **S3** — product images, asset uploads, CSV import/export files.
- **CDN** — static assets + (optionally) full HTML response caching for catalog pages.

### Docker on GHCR (v5.4+)

Spree publishes multi-arch (ARM + x86) Docker images to GitHub Container Registry:

```
ghcr.io/spree/spree:5.4.2
ghcr.io/spree/spree-starter:latest
ghcr.io/spree/storefront:5.4.2
```

(Verify the exact image tags against the GHCR releases.)

### `spree-starter` Dockerfile

The starter ships a production-ready Dockerfile with:
- Multi-stage build (builder → runner)
- Asset precompilation in build stage
- `bootsnap` precompile for faster boot
- Tini as PID 1
- Non-root user

### Environment Variables

| Var | Purpose |
|-----|---------|
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` |
| `REDIS_URL` | `redis://host:6379/0` |
| `RAILS_ENV` | `production` |
| `RAILS_MASTER_KEY` | Decrypts `config/credentials.yml.enc` |
| `SECRET_KEY_BASE` | If not in credentials |
| `RAILS_LOG_TO_STDOUT` | `true` for containerized envs |
| `RAILS_SERVE_STATIC_FILES` | `true` if no CDN in front |
| `WEB_CONCURRENCY` | Puma worker count |
| `RAILS_MAX_THREADS` | Threads per Puma worker |
| `MEILISEARCH_HOST`, `MEILISEARCH_API_KEY` | Search backend |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BUCKET`, `AWS_REGION` | ActiveStorage S3 |
| `SMTP_*` | Email |
| `SENTRY_DSN` | Error tracking |
| `STRIPE_*`, `ADYEN_*`, `PAYPAL_*` | Payment gateways |
| `SPREE_API_URL` | (Storefront-side) backend URL |
| `NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY` | (Storefront-side) publishable key |

### Asset Precompilation

Spree v5 uses **Propshaft** + **Tailwind CSS 4**. In Dockerfile:

```dockerfile
RUN bin/rails assets:precompile RAILS_ENV=production
```

For Tailwind, `tailwindcss-rails` watches files at runtime in dev; in production, precompile bakes the final CSS. If using esbuild, run `bin/rails javascript:build` too.

### Database Migrations on Deploy

Run before traffic flips:

```bash
bin/rails db:migrate
```

For zero-downtime:
1. **Backward-compatible migrations only** (no column drops; no NOT NULL without default)
2. Migrate → deploy new code → wait one release cycle → drop deprecated columns

### Sidekiq Configuration

```ruby
# config/initializers/sidekiq.rb
Sidekiq.configure_server do |config|
  config.redis = { url: ENV['REDIS_URL'] }
end

Sidekiq.configure_client do |config|
  config.redis = { url: ENV['REDIS_URL'] }
end
```

```yaml
# config/sidekiq.yml
:concurrency: 10
:queues:
  - critical
  - default
  - webhooks
  - mailers
  - low
```

Webhook delivery uses Sidekiq — without it, webhooks don't fire.

### Action Cable

For real-time admin updates (e.g., live order list refresh), Action Cable runs on the same Puma process. Redis is the broadcast adapter.

### MeiliSearch Indexing

After deploy:
```bash
bin/rails spree:search:reindex
```

(Verify the rake task name.) Run on a worker, not the web tier — long-running.

### Background Job Queues to Watch

- **Webhook delivery** — usually low-volume but bursty on bulk operations
- **Mailers** — high volume; separate queue helps prioritize
- **Image processing** — `ActiveStorage::AnalyzeJob` etc.; can fall behind on bulk uploads
- **Search indexing** — bursty on bulk product imports

### Backup Strategy

- PostgreSQL daily snapshots + WAL archive (or managed service backup)
- Redis is **ephemeral** — Sidekiq jobs lost on Redis loss is acceptable; recreate via re-publishing events
- S3 bucket versioning + cross-region replication
- `config/credentials.yml.enc` backed up alongside `RAILS_MASTER_KEY` (keep separate)

## Implementation Guidance

### Deploying to Heroku

```bash
heroku create my-spree
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0
heroku addons:create sendgrid:starter
heroku buildpacks:add heroku/ruby
heroku buildpacks:add heroku/nodejs   # for asset compilation
heroku config:set RAILS_MASTER_KEY=$(cat config/master.key)
heroku config:set RAILS_LOG_TO_STDOUT=true
heroku config:set RAILS_SERVE_STATIC_FILES=true
git push heroku main
heroku run bin/rails db:migrate
heroku run bin/rails spree:install
```

Run Sidekiq on a worker dyno:
```bash
heroku ps:scale web=2 worker=1
```

Procfile:
```
web: bundle exec puma -C config/puma.rb
worker: bundle exec sidekiq -C config/sidekiq.yml
release: bin/rails db:migrate
```

### Deploying to Docker (production)

```bash
docker build -t spree:latest .
docker run -d --name spree-web \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e RAILS_MASTER_KEY=... \
  -p 3000:3000 \
  spree:latest

docker run -d --name spree-worker \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e RAILS_MASTER_KEY=... \
  spree:latest bundle exec sidekiq
```

For Kubernetes, use separate Deployments for `web` and `worker`, plus a Job for `db:migrate` on each release.

### Deploying the Next.js Storefront

**Vercel**:
- Connect repo → set env vars → deploy
- Vercel auto-detects Next.js and configures build

**Docker / self-hosted**:
- Multi-stage Dockerfile (the storefront repo ships one)
- Deploy to Fly.io / Railway / Cloud Run

### Caching Strategy

| Layer | What to cache |
|-------|---------------|
| **CDN** | Static assets (`/assets/*`, `/packs/*`) |
| **Rails fragment cache** | Product cards on PLP (busted by `product.updated`) |
| **Rails low-level cache** | Computed totals, settings |
| **Database query cache** | Per-request (default Rails behavior) |
| **Sidekiq result cache** | Webhook delivery dedup |

### Zero-Downtime Deploys

1. **Pre-migrate**: only backward-compatible migrations
2. **Boot new pods/dynos** before terminating old
3. **Drain old workers** — let Sidekiq finish in-flight jobs (`SIGTSTP` then `SIGTERM`)
4. **Health check** — readiness probe on `/admin/login_check` or similar low-overhead path
5. **Post-deploy cleanup migrations** — run after the next release cycle removes references

### Monitoring Checklist

- **Puma queue depth** — saturation indicator
- **Sidekiq queue latency** — webhook deliveries falling behind = retries pile up
- **Database connections** — Spree apps consume aggressively; tune pool size
- **PostgreSQL slow queries** — Spree's polymorphic associations sometimes generate full table scans
- **Redis memory** — Sidekiq retries can pile up
- **Search index health** — drift between PG and MeiliSearch
- **Error rate per endpoint** — `/api/v3/*` separate from admin

### Common Pitfalls

- **`RAILS_MASTER_KEY` not set** — app crashes at boot with cryptic error.
- **Missing Redis** — Spree silently degrades (cache misses), but Sidekiq won't start.
- **Forgetting `RAILS_SERVE_STATIC_FILES=true` without a CDN** — 404s on assets.
- **Skipping `db:migrate` on release** — runtime errors.
- **Single Puma worker on multi-CPU host** — leaving 80% of CPU idle.
- **Sidekiq concurrency too high** — exhausts DB connection pool.
- **No backup verification** — backups exist but aren't testable.
- **Storefront deployed with backend on different version** — API contract mismatch; pin in lockstep.
- **MeiliSearch index out of sync after deploy** — reindex after every release.
- **Heroku slug too large** — exclude `tmp/`, `log/`, `node_modules/` from slug.

Always cross-reference your platform's current Rails 7+ guide and the `spree-starter` repo's deployment notes — both move with each Spree release.
