---
name: sf-b2c-isml
description: "Write ISML templates for B2C Commerce — <isprint>, <isif>, <isloop>, <isset>, <isinclude>, <isdecorate>, expression syntax ${pdict.*}, Resource.msg() localization, content slots, and template inheritance. Use when building B2C storefront templates."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-b2c-isml

Build ISML (Internet Store Markup Language) templates for Salesforce B2C Commerce storefronts.

## Before Writing Code

**Fetch live documentation FIRST:**
- Search: "Salesforce B2C Commerce ISML reference 2026"
- Search: "B2C Commerce template best practices encoding modes"
- WebFetch: Official ISML tag reference from Salesforce docs
- WebFetch: Template best practices and encoding guidelines

**Why:** ISML syntax, tag attributes, encoding modes, and localization patterns evolve with each B2C Commerce release. Always verify current specs before generating template code.

## Conceptual Architecture

### ISML Key Tags

| Tag | Purpose | Key Attributes |
|-----|---------|----------------|
| `<isprint>` | Output with encoding | `value`, `encoding` (required for XSS safety) |
| `<isif>` / `<iselseif>` / `<iselse>` | Conditional rendering | `condition` |
| `<isloop>` | Iteration | `items`, `var`, `status`, `begin`, `end`, `step` |
| `<isset>` | Variable assignment | `name`, `value`, `scope` (page/request/session) |
| `<isinclude>` | Include partial template | `template` (path) or `url` (controller action) |
| `<isdecorate>` | Decorator/layout wrapper | `template` (decorator path) |
| `<isreplace>` | Insertion point in decorator | (no attributes) |
| `<isslot>` | Content slot | `id`, `context` (category/folder/global), `description` |
| `<iscache>` | Template-level caching | `type`, `hour`, `varyby` |
| `<isscript>` | Inline server-side JS | (use sparingly -- prefer controllers) |
| `<iscontent>` | Set content type/charset | `type`, `charset` |
| `<isstatus>` | Set HTTP status code | `code` |
| `<isredirect>` | Server-side redirect | `location` |
| `<iscomment>` | Server-side comment | (not rendered to client) |

### Encoding Modes for `<isprint>`

| Mode | Context | When to Use |
|------|---------|-------------|
| `htmlcontent` | HTML body text | Default for most output (de facto SFRA standard) |
| `htmlsinglequote` | Single-quoted HTML attributes | `<div title='...'>`  |
| `htmldoublequote` | Double-quoted HTML attributes | `<div title="...">` |
| `htmlunquote` | Unquoted HTML attributes | Rarely needed; prefer quoted attributes |
| `jshtml` | JavaScript strings in HTML | `<script>var x = '...';</script>` |
| `jsattribute` | JS in HTML event attributes | `onclick="..."` |
| `jsonvalue` | JSON values | JSON data output |
| `uricomponent` | URL query parameters | Query string values |
| `uristrict` | Full URI encoding | Path segments |
| `xmlcontent` | XML body content | XML/RSS feeds |
| `off` | No encoding | Trusted content ONLY -- avoid in production |

Always specify encoding. Choose based on output context. Never use raw `${variable}` for user-controlled data without encoding.

### Expression Syntax

**Pipeline Dictionary (pdict):**
- `${pdict.variableName}` -- access controller-passed data (SFRA: from `res.render()`)
- In SFRA, `pdict` contains only what the controller explicitly passed
- Legacy SiteGenesis globals (CurrentSession, CurrentRequest, etc.) are NOT available in SFRA controllers

**Object Navigation:**
- `${pdict.product.name}` -- dot notation for nested properties
- `${pdict.basket.totalGrossPrice.value}` -- deep property access
- Null-safe: always check for null/undefined before accessing nested properties

**Operators:** Arithmetic (`+`, `-`, `*`, `/`, `%`), comparison (`==`, `!=`, `<`, `>`), logical (`&&`, `||`, `!`), ternary (`${cond ? a : b}`).

### `<isloop>` Status Object

| Property | Type | Description |
|----------|------|-------------|
| `first` | Boolean | True on first iteration |
| `last` | Boolean | True on last iteration |
| `count` | Number | Current iteration (1-based) |
| `index` | Number | Current iteration (0-based) |

Access via the `status` attribute: `<isloop items="${list}" var="item" status="loopstate">`, then use `${loopstate.first}`, `${loopstate.index}`, etc.

### `<isset>` Scope Rules

| Scope | Lifetime | Use Case |
|-------|----------|----------|
| `page` | Current template render | Temporary computation within a template |
| `request` | Current HTTP request | Share data across included templates |
| `session` | Current user session | Persist across requests (use sparingly) |

Default scope is `session` -- always specify scope explicitly to avoid unintended session pollution.

### Localization (Resource Bundles)

```isml
${Resource.msg('key', 'bundleName', 'Default')}
${Resource.msgf('key', 'bundle', 'Default {0}', param)}
```

Common bundles: `forms`, `common`, `error`, `product`. Always provide meaningful default values. Resource bundles are `.properties` files in `templates/resources/`.

### Decorator Pattern (Template Inheritance)

Decorators wrap child content via `<isdecorate>` and `<isreplace>`:

```isml
<!-- Child template -->
<isdecorate template="common/layout/page">
    <h1>Page Content</h1>
    <!-- replaces <isreplace /> in decorator -->
</isdecorate>
```

The decorator template defines shared layout (header, footer, `<head>`) and uses `<isreplace />` to mark where child content is inserted. Nested decorators are supported.

### Common Patterns

```isml
<!-- Pattern: product loop skeleton -->
<!-- Fetch live docs for loopstate properties -->
<isloop items="${pdict.products}" var="product" status="loopstate">
    <isprint value="${product.name}" encoding="htmlcontent" />
</isloop>
```

```isml
<!-- Pattern: URL generation -->
<a href="${URLUtils.url('Product-Show', 'pid', product.ID)}">
    <isprint value="${product.name}" encoding="htmlcontent" />
</a>
```

### URL Generation Helpers

| Method | Purpose |
|--------|---------|
| `URLUtils.url()` | Generate absolute URL for controller action |
| `URLUtils.https()` | Force HTTPS URL |
| `URLUtils.staticURL()` | URL to static asset in cartridge |
| `URLUtils.absURL()` | Absolute URL with full domain |
| `URLUtils.home()` | Homepage URL |
| `URLUtils.continueURL()` | Current request URL for form returns |

### Content Slots

Configured in Business Manager. Slots support HTML, products, categories, or content assets. Use descriptive IDs (`home-banner-top`, `category-promo-sidebar`) and set appropriate context (global, category, folder). Slot rendering can be cached separately from template caching.

### Platform Warnings

- `<isscript>` executes on the server and can access the full SFCC API -- keep logic minimal and move heavy processing to controllers or scripts.
- `<isset scope="session">` persists across requests -- avoid session bloat by defaulting to `page` scope.
- SFRA templates do NOT support SiteGenesis pipeline dictionary globals; only data from `res.render()` is available.
- Template-level `<iscache>` is separate from CDN caching; both must be configured correctly.

## Best Practices

### Security
- Always encode output with the correct mode for context.
- Never use `encoding="off"` unless input is fully trusted.
- Use CSRF tokens on all state-changing forms.
- Validate user input in controllers before passing to templates.

### Performance
- Minimize `<isscript>` blocks -- move logic to controllers or scripts.
- Use `<isset>` to compute expensive values once and reuse.
- Avoid deeply nested loops and conditionals.
- Use `<iscache>` for templates that do not change per request.

### Maintainability
- Use decorators for consistent page layout across templates.
- Extract reusable components into separate templates with `<isinclude>`.
- Externalize all user-facing strings to resource bundles for i18n.
- Follow naming convention: lowercase-hyphenated template names.

### Template Organization

| Directory | Contents |
|-----------|----------|
| `common/layout/` | Decorators (page, checkout, account) |
| `components/` | Shared partials (header, footer, navigation) |
| `product/` | Product display templates |
| `search/` | Search results templates |
| `account/` | Customer account templates |
| `cart/` | Cart and mini-cart templates |
| `checkout/` | Checkout flow templates |

---

Fetch the ISML tag reference, encoding mode documentation, and resource bundle guide for exact tag attributes, encoding behaviors, and localization APIs before implementing.
