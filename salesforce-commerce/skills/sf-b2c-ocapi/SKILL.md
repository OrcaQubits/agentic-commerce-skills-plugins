---
name: sf-b2c-ocapi
description: "MIGRATION SKILL: OCAPI (Open Commerce API) — Shop API and Data API endpoints, authentication, pagination, and OCAPI-to-SCAPI migration guide. OCAPI is in maintenance-only mode with no new features. Use this skill only for maintaining legacy integrations or planning migration to SCAPI."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# OCAPI -- Open Commerce API (Maintenance-Only)

> **MAINTENANCE-ONLY NOTICE**
>
> OCAPI is in **maintenance-only mode**. Salesforce is **not adding new features** and has positioned
> **SCAPI** as the successor for all new storefront development. OCAPI receives only critical security
> patches and bug fixes. It has NOT been formally deprecated with a sunset date.
>
> **Use this skill ONLY for:** maintaining legacy integrations, planning OCAPI-to-SCAPI migration,
> or debugging production OCAPI issues.
>
> **Do NOT build new features against OCAPI.** Use the `sf-b2c-scapi` skill for all new work.

## Before Writing Code

**Fetch live documentation BEFORE writing any code.**

1. Web-search `site:developer.salesforce.com OCAPI reference B2C Commerce` for latest reference docs
2. Web-search `site:developer.salesforce.com SCAPI migration OCAPI` for migration guides
3. Web-search `Salesforce B2C Commerce OCAPI maintenance mode 2026` for deprecation timeline updates
4. WebFetch: `developer.salesforce.com/docs/commerce/b2c-commerce/guide/b2c-ocapi-overview.html`
5. Confirm OCAPI version support on your instance via Business Manager > Administration > Site Development > Open Commerce API Settings

## Conceptual Architecture

### Shop API vs Data API

| Aspect | Shop API | Data API |
|--------|----------|----------|
| **Purpose** | Storefront operations (browse, cart, checkout) | Admin/integration operations (catalog, config, batch) |
| **Audience** | Shoppers / frontend apps | Admins / ERP / PIM integrations |
| **Site scope** | Site-specific (`/s/{site_id}/dw/shop/`) | Global (`/s/-/dw/data/`) |
| **Auth** | Client ID header or customer JWT | JWT bearer token from Account Manager |
| **Typical consumers** | PWA, mobile apps, kiosks | ERP connectors, OMS, back-office tools |

### Authentication Types Overview

| Auth Type | API | Use Case |
|-----------|-----|----------|
| Client ID header (`x-dw-client-id`) | Shop API | Anonymous browsing |
| Customer JWT (via `/customers/auth`) | Shop API | Registered customer sessions |
| OAuth JWT (Account Manager) | Data API | Server-to-server integrations |
| BM User Grant | Data API | Operations requiring BM user context |

Access control is configured via JSON in Business Manager, granting each client specific resources and methods.

### Pagination

OCAPI uses offset-based pagination with `count` (page size) and `start` (offset) parameters. Responses include `total`, `hits`, `next`, and `previous` fields.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `count` | 25 | Results per page (max varies, typically 200) |
| `start` | 0 | Zero-based offset |

Use the `expand` parameter to include related data (images, prices, variations) in a single request, reducing round-trips. Use `select` to request only needed fields, reducing payload size.

### Versioning

OCAPI requires an explicit version in the URL path (e.g., `v24.5`). Each B2C Commerce release may introduce a new version. Pin your version and do not upgrade unless required for a security patch.

### Key Differences: OCAPI vs SCAPI

| Aspect | OCAPI | SCAPI |
|--------|-------|-------|
| **Auth** | Client ID header + Basic auth | SLAS (OAuth 2.1 with PKCE) |
| **Naming** | `snake_case` fields | `camelCase` fields |
| **Versioning** | Frequent version bumps (`v24.5`) | Stable (`v1`) |
| **SDK** | No official SDK | Commerce SDK (Node.js/TypeScript) |
| **CDN** | Separate CDN config | eCDN built-in |
| **Search** | POST with JSON body | GET with query params |
| **Status** | Maintenance-only | Active development |

### Migration Guidance (OCAPI to SCAPI)

Migration should be **incremental, not big-bang**:

1. **Migrate authentication first** -- move to SLAS, which unblocks all SCAPI calls
2. **Replace endpoints one at a time** -- run OCAPI and SCAPI in parallel during transition
3. **Build a field-name mapping layer** -- `snake_case` to `camelCase` for downstream consumers
4. **Adopt the Commerce SDK** -- handles auth token management and provides TypeScript types
5. **Migrate search last** -- product search has the most complex integration (refinements, sorting, custom attributes)
6. **Update error handling** -- SCAPI error responses differ from OCAPI fault documents

### Fault Handling

OCAPI returns faults in a standard envelope with `_type: "fault"` and a nested `fault` object containing `type` and `message`. Common fault types:

| Fault Type | HTTP Status |
|------------|-------------|
| `InvalidParameterException` | 400 |
| `AuthenticationFailedException` | 401 |
| `AuthorizationFailedException` | 403 |
| `NotFoundException` | 404 |
| `RateLimitExceededException` | 429 |

## Best Practices

### Legacy Maintenance
- Minimize changes to working OCAPI integrations; focus effort on migration planning
- Pin your OCAPI version -- avoid unnecessary version bumps
- Monitor Salesforce release notes quarterly for deprecation timeline updates
- Document every OCAPI endpoint your system calls (frequency, criticality) to prepare for migration

### Security
- Rotate client credentials on a schedule
- Never expose Data API credentials or SLAS secrets in frontend code
- Restrict OCAPI resource access to minimum required endpoints/methods in BM config
- Audit OCAPI access logs for unexpected usage patterns

### Performance
- Cache product/category responses (5-15 min for products, 1 hour for categories)
- Use `expand` to fetch related data in one call instead of multiple requests
- Implement exponential backoff on 429 responses
- Avoid deep pagination -- use refinements to narrow result sets

Fetch the latest OCAPI reference docs, SCAPI migration guide, and Salesforce release notes for exact endpoint schemas, version availability, and deprecation timelines before implementing.
