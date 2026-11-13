---
name: sf-performance
description: >
  Optimize Salesforce Commerce performance — B2C (cartridge caching, CDN
  configuration, ISML rendering optimization, lazy loading) and B2B (SOQL
  optimization, LWC lazy loading, Apex bulkification). Both platforms target
  Core Web Vitals and image optimization.
---

# sf-performance

Optimize Salesforce Commerce performance across B2C Commerce (SFCC) and B2B Commerce Cloud platforms.

## Before Writing Code

**Always fetch live documentation first:**

1. **B2C Commerce Performance**
   - Search: "Salesforce B2C Commerce performance optimization 2026"
   - Search: "SFCC caching strategies page cache template cache"
   - Search: "Salesforce eCDN configuration and cache invalidation"

2. **B2B Commerce Performance**
   - Search: "Lightning Web Components performance optimization 2026"
   - WebFetch: `developer.salesforce.com/docs/component-library/documentation/en/lwc/lwc.reference_performance`

3. **Core Web Vitals**
   - Search: "Core Web Vitals 2026 targets LCP INP CLS" (INP replaced FID in March 2024)
   - WebFetch: `web.dev/vitals/`

## Conceptual Architecture

### Cache Levels (B2C)

| Level | Mechanism | Scope | Use Case |
|-------|-----------|-------|----------|
| **Page Cache** | `res.cachePeriod` / `res.cachePeriodUnit` | Full controller response | Product pages, category pages |
| **Template Cache** | `<iscache>` ISML tag | Individual template fragment | Reusable components, static content |
| **Object Cache** | `CacheMgr.getCache()` | Arbitrary data | API responses, computed results |
| **CDN Cache** | Salesforce eCDN | Static assets + pages | Images, CSS, JS, edge-cached HTML |

**Page cache types:**
- **Public cache**: Shared content (product, category pages)
- **Private cache**: User-specific content (cart, account)
- **No cache**: Checkout, payment pages

**Template cache varyby**: Fetch live docs for current supported `varyby` attribute values -- they are limited and version-specific.

### Core Web Vitals Targets

| Metric | Good | Needs Improvement | What It Measures |
|--------|------|-------------------|-----------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | < 4.0s | Main content load time |
| **INP** (Interaction to Next Paint) | < 200ms | < 500ms | Input responsiveness (replaced FID) |
| **CLS** (Cumulative Layout Shift) | < 0.1 | < 0.25 | Visual stability |

**Optimization strategies per metric:**
- **LCP**: Optimize hero images, reduce render-blocking resources, use CDN
- **INP**: Minimize JS execution, optimize event handlers, defer non-critical work
- **CLS**: Reserve space for images/ads, avoid dynamic content injection above fold

### Performance Budget Guidelines

| Resource | Target |
|----------|--------|
| Total page weight | < 1 MB (mobile), < 2 MB (desktop) |
| JavaScript bundle | < 300 KB (gzipped) |
| CSS bundle | < 100 KB (gzipped) |
| Images per page | < 500 KB total |
| Third-party scripts | < 100 KB total, < 5 requests |

### Caching TTL Concepts (B2C)

| Content Type | Recommended TTL | Cache Type |
|-------------|----------------|------------|
| Product pages | 24 hours | Public |
| Category pages | 24 hours | Public |
| Static assets (CSS/JS) | 30 days (versioned) | CDN |
| Cart / checkout | No cache | Private |
| API responses (CacheMgr) | 5-15 minutes | Object |

### CDN Overview (Salesforce eCDN)

- Static assets (images, CSS, JS) served via CDN automatically
- Cache headers (`Cache-Control`, `max-age`, `s-maxage`) control edge behavior
- Cache invalidation: automatic on code deployment, manual purge via Business Manager
- Geographic distribution reduces latency for global storefronts

### Lazy Loading Concepts

| Technique | Platform | Approach |
|-----------|----------|----------|
| Image lazy loading | Both | `loading="lazy"` attribute on `<img>` |
| Below-fold content | B2C | Deferred AJAX includes for non-critical sections |
| Deferred scripts | B2C | `<script defer>` or `<script async>` |
| Code splitting | PWA Kit | `React.lazy()` + `Suspense` |
| Dynamic imports | LWC (B2B) | `await import('c/heavyComponent')` |

### ISML Rendering Optimization (B2C)

- Minimize `<isloop>` iterations -- pre-calculate data in controllers
- Avoid complex expressions inside loops
- Use `<isinclude>` sparingly (each include has overhead)
- Pre-compute discount maps and data structures before passing to templates

### B2B Performance Considerations

B2B performance is covered in detail by other skills:
- **SOQL optimization and Apex bulkification**: See `sf-b2b-apex` skill
- **LWC performance**: See `sf-b2b-lwc` skill (lazy loading, wire adapter caching, `refreshApex`)
- **Experience Site caching**: Configure CDN headers via Experience Builder site settings

## Best Practices

### B2C Performance
- Cache aggressively: use page, template, and object caching in layers
- Optimize ISML: pre-calculate data in controllers, minimize loop iterations
- Leverage Salesforce eCDN for all static assets
- Target 80%+ cache hit rates for public pages

### Cross-Platform
- Meet Core Web Vitals "Good" thresholds for all three metrics
- Use WebP images with JPEG/PNG fallback, responsive srcset, and lazy loading
- Apply code splitting and tree shaking to minimize JS bundles
- Async-load third-party scripts; enforce performance budgets

### Monitoring
- Run Lighthouse audits regularly (target 90+ performance score)
- Use Real User Monitoring (RUM) with `web-vitals` library
- Review cache hit rates in Business Manager dashboards
- Profile ISML templates and controller response times in development

Fetch Salesforce performance guides, eCDN documentation, and Core Web Vitals specs for exact cache configuration, CDN setup, and current metric thresholds before implementing.
