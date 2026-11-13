---
name: spree-performance
description: >
  Profile and optimize a Spree application — N+1 queries with bullet/scout,
  database indexing strategy for Spree's polymorphic associations, Rails
  fragment + Russian doll caching, ActiveStorage variant pre-generation, Sidekiq
  queue tuning, MeiliSearch vs Postgres FTS tradeoffs, Puma worker/thread
  sizing, CDN strategy for catalog pages, asset precompile time, and load
  testing. Use when Spree is slow, the database is hot, or you're preparing for
  a traffic spike (Black Friday, launch).
---

# Spree Performance

## Before writing code

**Fetch live docs**:
1. Search the Spree blog at https://spreecommerce.org/blog for performance posts (Black Friday case studies, scaling guides).
2. Inspect `Spree::OrderUpdater` and other "hot path" service objects in the live source for known bottlenecks.
3. Cross-reference Rails 7+ performance guides for caching primitives.
4. For Sidekiq tuning, fetch https://github.com/sidekiq/sidekiq/wiki/Best-Practices.
5. Check the v5.4 announcement (https://spreecommerce.org/announcing-spree-commerce-5-4/) for the API v3 "10x faster than v2" claim and what changed.

## Conceptual Architecture

### Where Spree Spends Time

Profiling typical Spree requests shows hotspots at:

1. **N+1 queries** in catalog views (variants, prices, images)
2. **Order recalculation** on cart updates (`OrderUpdater` traverses line items, adjustments, taxes)
3. **Tax calculation** (`Spree::TaxCalculator` per-line)
4. **Promotion eligibility** (rules evaluated per applicable promotion per order)
5. **Image processing** (ActiveStorage variants generated on first request)
6. **Search** (Postgres FTS or MeiliSearch query)
7. **Adapter overhead** on heavy use cases (JSON:API in v2 was a serializer bottleneck — fixed in v3 flat-JSON)

### v3 API is ~10× Faster than v2

The v5.4 v3 API rewrite cites 10× perf vs v2:
- Flat JSON serialization beats JSON:API
- Prefixed IDs lookup uses index
- Fewer DB round-trips per response
- Better Russian-doll caching support

If migrating from v2 → v3, expect significant catalog-page speedups.

### Common N+1 Sources

```ruby
# BAD — N+1 on variants, prices, images
Spree::Product.all.each { |p| puts p.master.price }

# GOOD
Spree::Product.includes(master: :prices).each { |p| puts p.master.price }

# Better for views — preload images and stores too
Spree::Product.includes(:images, :stores, master: [:prices, :stock_items])
```

Use **bullet** in dev/test:
```ruby
# Gemfile
group :development, :test do
  gem 'bullet'
end

# config/environments/development.rb
config.after_initialize do
  Bullet.enable = true
  Bullet.alert = true
  Bullet.rails_logger = true
  Bullet.add_footer = true
end
```

### Fragment Caching

```erb
<% cache product do %>
  <%= render product %>
<% end %>
```

Cache key auto-busts on `product.updated_at`. Combine with `touch: true` on associations for Russian-doll caching:

```ruby
class Spree::Variant < ApplicationRecord
  belongs_to :product, touch: true
end
```

### Catalog Page Caching

For PLPs that don't change per user:

```ruby
class CatalogController < ApplicationController
  def show
    expires_in 5.minutes, public: true   # CDN-cacheable
    @products = current_store.products.active.includes(:taxons, master: :prices)
  end
end
```

For per-user PDP (price varies):
- Cache the immutable bits as fragments
- Render user-specific bits without cache

### Database Indexing

Spree ships indexes for most common access patterns. Verify your queries hit them — `EXPLAIN ANALYZE` in psql. Common missing indexes after schema changes:

```sql
CREATE INDEX index_spree_orders_on_user_id_and_state ON spree_orders(user_id, state);
CREATE INDEX index_spree_adjustments_on_adjustable ON spree_adjustments(adjustable_type, adjustable_id);
```

For multi-store, scope indexes to `store_id` columns.

### ActiveStorage Variant Pre-Generation

```ruby
# Generate variants in background after upload
class Spree::Image < ApplicationRecord
  has_one_attached :attachment do |attachable|
    attachable.variant :small, resize_to_limit: [120, 120], preprocessed: true
    attachable.variant :large, resize_to_limit: [1200, 1200], preprocessed: true
  end
end
```

Without `preprocessed: true`, the first user request generates the variant — slow.

### Sidekiq Queue Strategy

```yaml
# config/sidekiq.yml
:concurrency: 25
:queues:
  - [critical, 5]
  - [webhooks, 3]
  - [mailers, 2]
  - [default, 1]
```

Tune `:concurrency` against DB pool size — each Sidekiq thread takes one DB connection.

### Puma Sizing

```ruby
# config/puma.rb
workers ENV.fetch('WEB_CONCURRENCY') { 2 }
threads_count = ENV.fetch('RAILS_MAX_THREADS') { 5 }
threads threads_count, threads_count
preload_app!
```

Math: `workers × threads_count ≤ DB connection pool`. Set `pool` in `database.yml` to `threads_count`.

### Reporting Queries

Reports over `Spree::Order` can scan millions of rows. Strategies:
- Materialized views for daily/monthly aggregates
- Replica DB for reporting (avoid contention on primary)
- Pre-computed via Sidekiq jobs cached in Redis
- Pagination with cursors (`starting_after`) not OFFSET

### Image CDN

Front ActiveStorage with a CDN:

```ruby
# config/storage.yml
amazon:
  service: S3
  access_key_id: <%= ENV['AWS_ACCESS_KEY_ID'] %>
  secret_access_key: <%= ENV['AWS_SECRET_ACCESS_KEY'] %>
  bucket: my-spree-bucket
  region: us-east-1
  public: true   # if you front with CDN
```

Set CloudFront / Cloudflare in front. URLs become `https://cdn.example.com/...`.

### MeiliSearch vs Postgres FTS

| Backend | Latency | Faceting | Typo tolerance |
|---------|---------|----------|----------------|
| MeiliSearch | <50ms typical | Yes | Yes (built-in) |
| Algolia | <50ms typical | Yes | Yes |
| Postgres FTS | 100-500ms | Limited | Trigram-based, manual |

MeiliSearch wins for catalog search above ~10k products.

### Order Recalc Cost

`Spree::OrderUpdater` runs on every line-item change. If profiling shows it dominant:
- Batch updates (`Spree::OrderMutations.batch { |order| ... }` — verify API)
- Defer to a Sidekiq job if not needed synchronously
- Swap `Spree::Dependencies.order_updater_class` with a leaner implementation if you don't use all features

## Implementation Guidance

### Profiling Setup

```ruby
# Gemfile
group :development do
  gem 'bullet'
  gem 'rack-mini-profiler'
  gem 'flamegraph'
  gem 'stackprof'
  gem 'memory_profiler'
end
```

Hit a slow page with `?pp=help` to see profiler menu.

### Identifying Slow Queries

Enable `pg_stat_statements`:

```sql
CREATE EXTENSION pg_stat_statements;

SELECT calls, mean_exec_time, query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### Cache Key Versioning

After a Spree minor upgrade, bust caches:

```ruby
# config/initializers/cache_version.rb
Rails.application.config.cache_classes_version = 'spree_5.4.2_v1'
```

(Add as fragment cache version suffix.)

### Black Friday Prep Playbook

1. **Capacity test 4 weeks before** — synthetic load = 5× expected peak
2. **DB read replica** for reporting queries
3. **Cache warming** — pre-generate ActiveStorage variants for all live products
4. **CDN cache TTLs raised** on catalog pages
5. **Sidekiq scaling test** — webhook backlog handling at burst
6. **Database connection pool** raised on primary
7. **Read-only mode plan** in case of overload
8. **War room runbook** — who is on call for what
9. **Disable expensive features** during peak (e.g., live carrier rate calls — fall back to flat rate)

### Common Pitfalls

- **`Spree::Order.all` in a controller** — full table scan; always scope.
- **`includes` not matching what the view uses** — N+1 sneaks back in.
- **Fragment cache without `touch: true`** — stale cards on inventory change.
- **Sidekiq concurrency exceeding DB pool** — connection-pool errors under load.
- **Image processing on web tier** — blocks request thread; do in Sidekiq.
- **OFFSET pagination over large tables** — slow; use cursors.
- **MeiliSearch index out of sync** — events not firing or job failures; monitor lag.
- **Ransack filters scanning unindexed columns** — admin order search slow over millions of rows.
- **Logging full response bodies** — log volume explodes; filter.
- **`spree:install` rake task in CI on every build** — slow; cache the test app.

Always profile before optimizing — assumptions about where the time goes are usually wrong. Spree's hot paths are well-known; community blog posts and Spree's own benchmarks are the best starting point.
