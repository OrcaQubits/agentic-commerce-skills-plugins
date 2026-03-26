---
name: node-backend
description: Build Node.js backends for Salesforce Commerce — SFCC server-side JavaScript (not actual Node.js runtime), PWA Kit backend (Express-like SSR server), Commerce SDK for server-side SCAPI access, and async patterns for external service integration. Use when building server-side commerce logic.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Salesforce Commerce Server-Side JavaScript

## Before Writing Code

Always fetch the latest official documentation BEFORE building server-side logic:

1. Web-search: "Salesforce B2C Commerce server-side JavaScript Script API 2026"
2. Web-search: "Salesforce PWA Kit server-side rendering 2026"
3. Web-search: "Salesforce Commerce SDK Node.js 2026"
4. Web-fetch: `https://developer.salesforce.com/docs/commerce/b2c-commerce/references/b2c-commerce-script-api`
5. Web-fetch: `https://developer.salesforce.com/docs/commerce/pwa-kit-managed-runtime/guide/getting-started.html`
6. Web-fetch: `https://www.npmjs.com/package/@salesforce/commerce-sdk`

Verify API methods, module paths, and runtime constraints against current documentation before writing any code.

## Conceptual Architecture

### CRITICAL: SFCC Server-Side JavaScript is NOT Node.js

> **WARNING**: SFCC uses a **Rhino-based** JavaScript engine, NOT V8/Node.js. Code that works in Node.js will fail in SFCC. Never assume Node.js APIs or patterns are available.

| Feature | SFCC (Rhino) | Node.js / PWA Kit |
|---|---|---|
| Runtime engine | Rhino (Java-based) | V8 |
| npm packages | NOT available | Available |
| async/await | NOT available | Available |
| Promises | NOT available | Available |
| ES6 modules (import/export) | NOT available | Available |
| Filesystem access | Only via `dw.io` (IMPEX sandbox) | Full `fs` module |
| HTTP client | `dw.net.HTTPClient` only | fetch, axios, etc. |
| Module system | CommonJS-like (`require()`) | CommonJS or ESM |
| var vs let/const | `var` only (Rhino) | `let`, `const`, `var` |
| Arrow functions | NOT available | Available |
| Template literals | NOT available | Available |
| Destructuring | NOT available | Available |
| Classes (ES6) | NOT available | Available |
| for...of loops | NOT available | Available |

### Common SFCC Mistakes to Avoid

| Mistake | Why It Fails | Correct Approach |
|---|---|---|
| `const x = ...` | Rhino does not support `const` | Use `var x = ...` |
| `arr.forEach(item => ...)` | No arrow functions | Use `function(item) { ... }` |
| `` `Hello ${name}` `` | No template literals | Use `'Hello ' + name` |
| `async function f()` | No async/await | Synchronous code only |
| `require('lodash')` | No npm packages | Use `dw.*` APIs or bundle in cartridge |
| `import x from 'y'` | No ES6 modules | Use `require('y')` |

### dw.* Namespace Purposes

All SFCC server-side functionality is provided through the `dw.*` namespace:

| Namespace | Purpose | Key Classes |
|---|---|---|
| `dw.web` | Request/response, URL generation, i18n | Resource, URLUtils, FormElement |
| `dw.catalog` | Product search, catalog management | ProductMgr, CatalogMgr, ProductSearchModel |
| `dw.order` | Basket and order management | BasketMgr, OrderMgr, ShippingMgr |
| `dw.customer` | Customer profiles, auth | CustomerMgr, AuthenticationManager |
| `dw.system` | Transaction, logging, session, site | Transaction, Logger, Session, Site |
| `dw.net` | HTTP callouts, FTP, email | HTTPClient, FTPClient, Mail |
| `dw.io` | File I/O (IMPEX sandbox only) | File, FileReader, FileWriter, XMLStreamReader |
| `dw.crypto` | Encoding, hashing, encryption | Encoding, MessageDigest, Mac |
| `dw.util` | Collections and utilities | ArrayList, HashMap, Iterator, Calendar |
| `dw.content` | Content management | ContentMgr, ContentAsset |
| `dw.campaign` | Promotions and coupons | PromotionMgr, CouponMgr |
| `dw.value` | Money and quantity types | Money, Quantity |

### Transaction Handling

All database modifications in SFCC must be wrapped in `Transaction.wrap()` for atomicity. If any statement inside the transaction throws, all changes are rolled back. Transactions are implicit for job steps but must be explicit in controllers and hooks.

### SFCC Script Module Pattern

Scripts live in cartridges at `cartridge/scripts/` and export functions via `module.exports`. Use the `*/cartridge/` prefix for cross-cartridge imports that follow the cartridge path overlay. The cartridge path is configured in Business Manager and determines module resolution order.

### SFCC Controller Pattern

Controllers in SFRA (Storefront Reference Architecture) live at `cartridge/controllers/` and use the `server` module to define routes. Controllers handle HTTP verbs (`get`, `post`, `use`) and render templates or return JSON.

### PWA Kit Backend

PWA Kit runs on **actual Node.js** (V8) via Salesforce Managed Runtime. It uses an Express-like server created with `@salesforce/pwa-kit-runtime`. Full modern JavaScript (async/await, ESM, npm packages) is available.

| Aspect | Detail |
|---|---|
| Server creation | `createApp()` from `@salesforce/pwa-kit-runtime/ssr/server/express` |
| Data fetching | `getProps()` static method on page components |
| Configuration | `config/default.js` with environment overrides |
| Deployment | Salesforce Managed Runtime (auto-scaling, CDN) |
| Custom middleware | Express-style `app.use()` and `app.get()` |
| Environment variables | Set via Managed Runtime dashboard |

### Commerce SDK

The `@salesforce/commerce-sdk` npm package provides TypeScript-typed clients for all Shopper APIs:

| Client | Purpose |
|---|---|
| `ShopperProducts` | Get products, categories, recommendations |
| `ShopperSearch` | Product search with facets, sorting |
| `ShopperBaskets` | Create/update baskets, add items, apply coupons |
| `ShopperOrders` | Create orders from baskets |
| `ShopperCustomers` | Customer registration, login, profiles |

It handles SLAS authentication automatically via `helpers.getShopperToken()`. All SDK methods return Promises. Use Commerce SDK typed clients instead of raw HTTP calls to SCAPI for type safety and automatic auth management.

## Code Examples

**Pattern: SFCC script module**

```javascript
var ProductMgr = require('dw/catalog/ProductMgr');
var Transaction = require('dw/system/Transaction');
module.exports.execute = function(params) {
    // Fetch live docs for dw.catalog.ProductMgr API
};
```

**Pattern: PWA Kit getProps server-side fetch**

```javascript
ProductDetail.getProps = async ({ params, api }) => {
    const product = await api.shopperProducts.getProduct({
        parameters: { id: params.productId }
    });
    return { product };
};
```

**Pattern: SFCC HTTPClient callout**

```javascript
var httpClient = new (require('dw/net/HTTPClient'))();
httpClient.open('POST', endpoint);
httpClient.send(JSON.stringify(payload));
// Fetch live docs for dw.net.HTTPClient response handling
```

**Pattern: SFCC Transaction.wrap**

```javascript
var Transaction = require('dw/system/Transaction');
Transaction.wrap(function() {
    // All database modifications are atomic here
    // Fetch live docs for Transaction rollback behavior
});
```

## Best Practices

### SFCC Server-Side
- Use `var` (not `let`/`const`), function expressions (not arrows), and `try/catch` (not Promises)
- Always wrap data mutations in `Transaction.wrap()`
- Use `dw/system/Logger` for logging -- never `console.log` (it does not persist)
- Place third-party libraries directly in `cartridge/scripts/lib/` -- no npm available

### PWA Kit Backend
- Use `getProps()` for SSR data fetching, Commerce SDK hooks for client-side data
- Configure environments via `config/default.js` and environment-specific overrides
- Use Commerce SDK typed clients instead of raw HTTP calls to SCAPI
- Deploy to Managed Runtime for auto-scaling and CDN integration

### Error Handling
- SFCC: synchronous try/catch with `dw.system.Logger` error logging at appropriate levels
- PWA Kit: async try/catch, structured logging, implement retry with exponential backoff
- Both: validate all inputs, handle null/missing data gracefully, never expose stack traces to clients

### Performance
- Minimize external callouts (SFCC has per-request time limits)
- Cache frequently accessed data (SFCC: custom cache, PWA Kit: HTTP cache headers)
- Use parallel `Promise.all()` in PWA Kit for independent API calls
- Batch operations where supported by Commerce APIs
- Use SFCC Pipeline Profiler and Request Logs to identify bottlenecks

---

Fetch the latest SFCC Script API reference and PWA Kit developer guide for exact method signatures, runtime constraints, and deployment procedures before implementing.
