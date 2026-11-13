---
name: sf-b2c-sfra
description: >
  Build B2C Commerce storefronts with SFRA (Storefront Reference Architecture)
  — cartridge overlay system, MVC pattern, app_storefront_base,
  module.superModule inheritance, middleware chain, and site-specific
  customizations. Use when developing SFRA-based storefronts.
---

# Salesforce B2C Commerce SFRA Development

## Before Writing Code

**Fetch live docs:**
1. WebFetch `github.com/SalesforceCommerceCloud/storefront-reference-architecture` for SFRA source
2. Web-search `site:developer.salesforce.com SFRA architecture MVC` for MVC patterns
3. Web-search `site:developer.salesforce.com SFRA cartridge overlay` for overlay best practices
4. Web-search `site:developer.salesforce.com module.superModule` for extension patterns
5. Web-search `site:developer.salesforce.com SFRA getting started` for latest docs

## Conceptual Architecture

### SFRA Overview

SFRA (Storefront Reference Architecture) is the reference implementation for B2C Commerce storefronts:

- **Server-side MVC** -- Models, Views (ISML), Controllers
- **Cartridge overlay system** -- stack custom cartridges on top of base
- **module.superModule** -- extend base functionality without copying code
- **Client-side build** -- Webpack bundles JS and SCSS
- **Page Designer** -- visual page building with reusable components

### Four Key Principles

| Principle | Rule |
|-----------|------|
| **Overlay** | Never modify `app_storefront_base` -- create custom cartridges that layer on top |
| **Extend** | Use `module.superModule` to inherit and augment, not replace |
| **Hooks** | Use commerce hooks for order, payment, and shipping customization |
| **Services** | Use the Service Framework for external integrations (payment gateways, ERP) |

### Cartridge Path Resolution

The cartridge path (configured in Business Manager) resolves files left-to-right. The **leftmost cartridge wins**.

Example path: `app_custom:app_storefront_base`
- Request for `controllers/Product.js` checks `app_custom` first, falls back to `app_storefront_base`
- Templates, models, and scripts follow the same resolution

### Cartridge Directory Structure

```
app_custom/cartridge/
├── controllers/        # Route handlers
├── models/             # Data models
├── scripts/            # Helpers, services
├── templates/          # ISML templates
├── experience/         # Page Designer
└── client/default/     # JS + SCSS source (Webpack)
```

### module.superModule

`module.superModule` resolves to the next cartridge in the path that provides the same module. This is how you extend without duplicating:

- **Controllers**: `var base = module.superModule; server.extend(base);` then use `append`/`prepend`/`replace`
- **Models**: Call base constructor with `base.call(this, apiProduct, options)`, then add properties
- **Scripts**: Import base, extend functions, re-export with spread

### MVC Pattern

| Layer | Location | Role |
|-------|----------|------|
| **Controller** | `controllers/*.js` | Route handling via `server` module |
| **Model** | `models/**/*.js` | Transform API data to view-friendly objects |
| **View** | `templates/default/**/*.isml` | ISML templates for HTML rendering |
| **Client JS** | `client/default/js/` | Browser-side behavior (Webpack bundled) |
| **SCSS** | `client/default/scss/` | Styles (compiled to CSS) |

### Extend vs Replace Controllers

| Approach | When | Trade-off |
|----------|------|-----------|
| `server.extend(base)` + `append` | Adding data, logging, analytics | Keeps base logic; auto-receives base updates |
| `server.replace('Route', fn)` | Fundamentally different logic | You own the entire implementation; no base updates |

Prefer `extend` + `append` in nearly all cases. Only `replace` when the base logic is wrong for your use case.

### Client-Side Build

SFRA uses Webpack to build client assets from `client/default/js/` and `client/default/scss/`. Output goes to `cartridge/static/default/`. Client JS can extend base modules:

```javascript
// Pattern: Extend base client module
var base = require('base/product/detail');
// Fetch live docs for base module API
```

### Site Preferences and Custom Objects

- **Site Preferences**: `Site.getCurrent().getCustomPreferenceValue('prefName')` -- store-level configuration
- **Custom Objects**: `CustomObjectMgr.getCustomObject('Type', 'key')` -- custom data structures
- Both are managed in Business Manager and accessed via `dw.*` API

## Best Practices

### Cartridge Overlay
- Never modify `app_storefront_base`
- Name custom cartridges consistently: `app_custom_[sitename]` or `int_custom_[feature]`
- Use `module.superModule` to extend -- avoid code duplication
- Test overlays after base cartridge updates

### Controllers and Models
- Use `server.extend()` to inherit base routes
- Keep controllers thin -- move logic to models and scripts
- Call base model constructor, then add properties
- Always call `next()` in middleware chain

### Templates and Client Code
- Use `<isinclude>` for reusable components
- Use resource bundles for all text: `Resource.msg('key', 'bundle', null)`
- Import and extend base client JS modules
- Minimize jQuery -- prefer vanilla JS for performance

### Security and Performance
- Use `Transaction.wrap()` for all database writes
- Encode output in templates to prevent XSS
- Use CSRF tokens for state-changing operations
- Cache expensive operations via `CacheMgr`

Fetch the SFRA GitHub repository, developer documentation, and module.superModule guide for exact patterns, API references, and best practices before implementing.
