---
name: sf-b2c-cartridges
description: >
  Build B2C Commerce cartridges — cartridge directory structure (controllers/,
  models/, scripts/, templates/, static/), cartridge stacking, naming
  conventions (app_custom_*, plugin_*, int_*), cartridge path configuration, and
  certification requirements. Use when creating or modifying SFCC cartridges.
---

# sf-b2c-cartridges

Build B2C Commerce cartridges following Salesforce Commerce Cloud architecture patterns.

## Before Writing Code

**Fetch live documentation FIRST:**

1. **Web-search** for:
   - "Salesforce B2C Commerce SFRA cartridge structure 2026"
   - "SFCC cartridge naming conventions best practices"
   - "Salesforce Commerce Cloud cartridge overlay documentation"

2. **Web-fetch** official sources:
   - https://github.com/SalesforceCommerceCloud/storefront-reference-architecture (SFRA GitHub repo)
   - Salesforce B2C Commerce cartridge development documentation
   - SFCC LINK marketplace certification requirements

3. **Verify** before coding:
   - Current SFRA version and directory structure
   - Cartridge naming prefix standards
   - Required metadata fields in cartridge.properties
   - Build tool configuration (sgmf-scripts, webpack)

## Conceptual Architecture

### Cartridge Directory Structure

```
app_custom_mysite/
├── cartridge/
│   ├── controllers/    # Route handlers
│   ├── models/         # Business logic
│   ├── scripts/        # Helpers, middleware
│   ├── templates/      # ISML + i18n resources
│   └── static/         # Compiled CSS/JS/images
└── cartridge.properties
```

### Key Directories Explained

| Directory | Contents | Notes |
|-----------|----------|-------|
| `controllers/` | Server-side JS route handlers | Each file exports route actions (e.g., `Product-Show`) |
| `models/` | Data models and business logic | Keep controllers thin; move logic here |
| `scripts/` | Utility helpers, middleware, services | Subdirs: `helpers/`, `middleware/`, `services/` |
| `templates/default/` | ISML templates per locale | `default/` is the fallback locale |
| `templates/resources/` | i18n `.properties` files | Resource bundles for `Resource.msg()` |
| `forms/default/` | XML form definitions | Server-side validation rules |
| `static/default/` | Compiled CSS, JS, images | Built from `client/default/` source |
| `client/default/` | Source SCSS and JS | Input for webpack/sgmf-scripts build |
| `experience/components/` | Page Designer components | Visual merchandising building blocks |

### Cartridge Naming Conventions

| Prefix | Purpose | Example |
|--------|---------|---------|
| `app_custom_*` | Site-specific customizations | `app_custom_mysite` |
| `plugin_*` | Reusable feature modules | `plugin_wishlists` |
| `int_*` | Third-party integrations | `int_paypal`, `int_stripe` |
| `bm_*` | Business Manager extensions | `bm_custom_admin` |
| `app_storefront_base` | Base SFRA cartridge | Core framework (do not modify) |
| `modules/` | Shared modules (non-cartridge) | Utility libraries consumed by cartridges |

### Cartridge Path and Overlay System

The **cartridge path** defines file resolution order (configured in Business Manager > Site Settings):

```
app_custom_mysite:plugin_wishlists:int_paypal:app_storefront_base
```

**Resolution**: Left to right. When SFCC resolves a file (e.g., `controllers/Product.js`), it searches each cartridge in path order and uses the first match. This enables **non-destructive customization** -- overlay specific files without modifying base cartridges.

**Overlay constraints:**
- File must have the same relative path inside `cartridge/` to override
- Controllers can extend base controllers via `module.superModule`
- Templates override entirely (no partial merge)
- Static assets (CSS/JS) override entirely per file
- Resource bundles merge at the property level (keys from left cartridge win)

### Cartridge Types

| Type | Contains | When to Use |
|------|----------|-------------|
| Storefront | Controllers, templates, static assets | Customer-facing site logic |
| Integration | Service definitions, API clients | Third-party system connections |
| Plugin | Self-contained feature | Reusable cross-site features |
| Business Manager | BM extensions, custom modules | Admin panel customizations |

### Controller Extension Pattern

Controllers can extend base behavior using `module.superModule`:

```javascript
// Pattern: extend base controller
// Fetch live docs for server.extend() API
var server = require('server');
server.extend(module.superModule);
// Add or override route actions here
```

This avoids duplicating the entire base controller when you only need to modify one action.

### Cartridge Metadata (cartridge.properties)

Required fields: cartridge ID and multi-language flag. Optional: version and compatibility version. Fetch live docs for the exact property key format (`demandware.cartridges.<id>.*`) before creating this file.

### Build Tools

SFRA uses `sgmf-scripts` for compiling client-side SCSS and JS. Source files live in `cartridge/client/default/` and compile to `cartridge/static/default/`. Webpack configuration maps entry points for JS bundles and SCSS compilation.

| Tool | Purpose |
|------|---------|
| `sgmf-scripts --compile js` | Compile client-side JavaScript |
| `sgmf-scripts --compile css` | Compile SCSS to CSS |
| `sgmf-scripts --watch` | Watch mode for development |
| `sfcc-ci` | CLI for code upload and deployment automation |

### LINK Marketplace Certification

| Category | Key Requirements |
|----------|-----------------|
| Technical | Compatible with latest SFRA; no hardcoded credentials; passes code profiler |
| Documentation | Installation guide, BM configuration steps, troubleshooting guide |
| Security | Input validation, CSRF protection, secure credential storage |
| Testing | Unit tests, integration tests, performance benchmarks, multi-site compatibility |

### Deployment

Pattern: upload cartridge code to a **code version** on the sandbox/instance, then activate that version in Business Manager. Use WebDAV upload or the `sfcc-ci` CLI tool for automation.

| Step | Action |
|------|--------|
| 1 | Upload code to a named code version via WebDAV or `sfcc-ci` |
| 2 | Set the active code version in BM > Administration > Code Deployment |
| 3 | Update cartridge path in BM > Site Settings if new cartridges were added |
| 4 | Clear caches and verify storefront behavior |

```bash
# Pattern: scaffold a new cartridge
# Fetch live docs for sgmf-scripts CLI options
mkdir -p app_custom_mysite/cartridge/{controllers,models,scripts,templates/default}
```

## Best Practices

### Cartridge Organization
- Keep site-specific code in `app_custom_*`; reusable features in `plugin_*`.
- Minimize cartridge count -- each cartridge adds file resolution overhead.
- Match `app_storefront_base` directory layout for clean overlays.
- Use `module.superModule` to extend controllers rather than copying entire files.

### Code Modularity
- Extract reusable functions to `scripts/helpers/`; keep controllers thin.
- Use models for business logic; templates for presentation only.
- Break large ISML files into `<isinclude>` components.
- Keep Page Designer components self-contained with clear input/output contracts.

### Version Control and Deployment
- Increment `cartridge.properties` version on each release.
- Use semantic versioning tags in Git; maintain a CHANGELOG.
- Always deploy to sandbox first; activate code versions after validation.
- Use `sfcc-ci` for CI/CD pipeline integration.

### Security
- Never commit secrets -- use Business Manager custom preferences or site preferences.
- Validate all inputs via form definitions and server-side checks.
- Follow OWASP guidelines, especially for payment integrations.
- Use service credentials (BM > Services) for external API keys.

### Performance
- Minimize cartridge path length to reduce file resolution overhead.
- Serve only compiled, minified assets in production.
- Configure cache headers in Business Manager for static resources.
- Profile cartridge code with the SFCC code profiler before release.

---

Fetch the SFRA GitHub repo, B2C Commerce cartridge development docs, and LINK certification guidelines for exact directory conventions, build tool APIs, and deployment procedures before implementing.
