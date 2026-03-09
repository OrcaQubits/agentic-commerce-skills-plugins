---
name: magento-performance
description: Optimize Magento 2 performance — full page cache (Varnish), Redis, indexer tuning, JavaScript/CSS optimization, database optimization, and profiling. Use when diagnosing slow pages, optimizing load times, or configuring caching.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Magento 2 Performance Optimization

## Before writing code

**Fetch live docs**:
1. Web-search `site:experienceleague.adobe.com commerce performance` for performance best practices
2. Web-search `site:experienceleague.adobe.com commerce configuration cache` for cache configuration
3. Web-search `site:developer.adobe.com commerce php development cache` for cache development guide

## Full Page Cache (FPC)

### Varnish (Recommended for Production)

- Serves cached pages from RAM before hitting the web server
- Dramatically reduces TTFB (time to first byte)
- Magento generates VCL (Varnish Configuration Language) files
- Configure at Stores > Configuration > Advanced > System > Full Page Cache
- Generate VCL: `bin/magento varnish:vcl:generate`

### Built-in FPC (Fallback)

- Filesystem-based cache — slower than Varnish
- Suitable for development only
- No separate service required

### Cache Invalidation

- Automatic on entity save (products, categories, CMS)
- Manual: `bin/magento cache:clean full_page`
- Cache tags track which pages contain which entities
- Hole-punching for dynamic content (customer name, cart count) via private content/sections

## Redis / Valkey

### Cache Backend

Store all Magento caches in Redis for fast reads:
- Configuration cache, layout cache, block HTML cache
- Configure in `app/etc/env.php` under `cache`

### Session Storage

Store PHP sessions in Redis instead of filesystem/database:
- Faster session reads/writes
- Better for load-balanced environments
- Configure in `app/etc/env.php` under `session`

## Indexer Tuning

- **Update by Schedule** (production) — cron-based, uses changelogs
- **Update on Save** (development) — immediate but resource-intensive
- Monitor indexer status: `bin/magento indexer:status`
- Tune cron frequency for indexer jobs

## JavaScript and CSS Optimization

### Production Mode

Static content is pre-deployed and minified:
```bash
bin/magento setup:static-content:deploy --jobs=N
```

### Minification

- JS minification: enabled via admin config
- CSS minification: enabled via admin config
- HTML minification: configurable

### Bundling

- Built-in JS bundling (basic)
- Advanced bundling with Magepack (community tool) for page-specific bundles
- Critical CSS extraction for above-the-fold rendering

### Hyva Performance Gain

If using Hyva themes: ~5 HTTP requests vs ~230, ~0.4MB vs ~3MB — eliminates most JS optimization needs.

## Database Optimization

- Use MySQL 8.0+/MariaDB 10.6+ for latest optimizer improvements
- Tune InnoDB buffer pool size (ideally 70-80% of available RAM on dedicated DB servers) and use MySQL 8.0 optimizer hints where applicable
- Optimize slow queries: enable slow query log, analyze with `EXPLAIN`
- Clean log tables periodically (cron handles this)
- Use persistent database connections in `app/etc/env.php`

## Profiling Tools

- **Magento Profiler**: enable in `app/etc/env.php` or via `bin/magento dev:profiler:enable`
- **New Relic**: APM integration built into Magento
- **Blackfire.io**: PHP profiling
- **MySQL slow query log**: database bottlenecks
- **Varnish stats**: cache hit rates

## Best Practices

- Always use production mode in production
- Varnish + Redis is the standard production stack
- Set all indexers to "Update by Schedule"
- Pre-deploy static content during build (not on production server)
- Monitor cache hit rates — low rates indicate misconfigured invalidation
- Profile before optimizing — measure, don't guess
- Use CDN for static assets
- Enable HTTP/2 on the web server
- Consider Hyva for frontend performance

Fetch the performance documentation for exact configuration paths, VCL generation options, and Redis configuration format before optimizing.
