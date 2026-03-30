---
name: js-modern
description: >
  Write modern JavaScript and TypeScript — ES6+ features, async/await, modules,
  destructuring, optional chaining, TypeScript types. Covers SFCC server-side JS
  (CommonJS, limited ES6), PWA Kit (full modern JS/TS), and LWC JavaScript
  (Lightning Locker constraints). Use when writing JavaScript for Salesforce
  Commerce.
---

# js-modern

Write modern JavaScript and TypeScript for Salesforce Commerce platforms.

## Before Writing Code

Always fetch the latest official documentation BEFORE writing JavaScript:

- **MDN JavaScript Reference**: WebSearch "MDN JavaScript reference ES6 2026" and WebFetch official docs
- **TypeScript Documentation**: WebSearch "TypeScript handbook 2026" and WebFetch official docs
- **Platform-Specific Docs**: WebSearch for "Salesforce B2C Commerce server-side JavaScript API 2026" (SFCC), "PWA Kit JavaScript TypeScript 2026" (PWA Kit), or "Lightning Web Components JavaScript 2026" (LWC)

This ensures you're using the latest syntax, APIs, and best practices for each platform.

## Conceptual Architecture

### Platform Runtime Constraints

This is the most critical concept. Three Salesforce Commerce platforms have fundamentally different JavaScript runtimes:

| Constraint | SFCC Server-Side | PWA Kit | LWC (B2B) |
|-----------|-----------------|---------|------------|
| **Engine** | Rhino (Java-based) | Node.js + V8 | Browser (V8/SpiderMonkey) |
| **Module system** | CommonJS (`require`) | ES Modules (`import`) | ES Modules (`import`) |
| **async/await** | Not supported | Fully supported | Fully supported |
| **Promises** | Not supported | Fully supported | Fully supported |
| **Template literals** | Limited contexts | Fully supported | Fully supported |
| **Arrow functions** | Supported | Supported | Supported |
| **Destructuring** | Supported | Supported | Supported |
| **Optional chaining** | Not supported | Supported | Supported |
| **Classes** | Not supported | Supported | Required (extends LightningElement) |
| **Decorators** | Not applicable | Not applicable | Required (@api, @track, @wire) |
| **DOM access** | Not applicable | Standard DOM | Shadow DOM only (Locker/LWS) |

### SFCC Server-Side JavaScript

The Rhino engine imposes strict limitations. Every SFCC script must account for these:

- Use `var` or `let`/`const` (recent versions) -- verify against your instance
- No `async`/`await`, no `Promise` -- all I/O is synchronous
- No ES modules -- use `require('dw/...')` and `module.exports`
- Access platform APIs via `dw.*` namespace (e.g., `dw/catalog/ProductMgr`)
- Use `module.superModule` for cartridge overlay inheritance

```javascript
// Pattern: SFCC module import
var ProductMgr = require('dw/catalog/ProductMgr');
// Fetch live docs for dw.* API signatures
```

```javascript
// Pattern: module.superModule extension
var base = module.superModule;
// Fetch live docs for superModule behavior
```

### PWA Kit JavaScript/TypeScript

Full modern JavaScript and TypeScript are available:

| Feature | Stack |
|---------|-------|
| React | 17+ with hooks |
| TypeScript | Full support, recommended |
| Node.js SSR | Server-side rendering |
| Commerce SDK | `commerce-sdk-isomorphic` |
| Bundler | Webpack with code splitting |

```typescript
// Pattern: PWA Kit component with Commerce SDK
// Fetch live docs for useProducts hook API
import { useProducts } from '@salesforce/commerce-sdk-react';
```

### LWC JavaScript Constraints

LWC uses modern ES modules but enforces security boundaries:

| Allowed | Not Allowed |
|---------|-------------|
| ES modules (`import`/`export`) | Direct `window`/`document` manipulation |
| `async`/`await`, Promises | `eval()`, `Function()` constructor |
| Template literals, destructuring | Third-party DOM libraries (jQuery) |
| `@api`, `@track`, `@wire` decorators | `setTimeout(string)` |
| `this.template.querySelector()` | `document.getElementById()` |
| `NavigationMixin` | `window.location = ...` |

```javascript
// Pattern: LWC component skeleton
// Fetch live docs for decorator behavior
import { LightningElement, api, wire } from 'lwc';
```

### Module Systems Comparison

| System | Syntax | Platform |
|--------|--------|----------|
| CommonJS | `require()` / `module.exports` | SFCC server-side |
| ES Modules | `import` / `export` | PWA Kit, LWC |
| SFCC Overlay | `module.superModule` | SFCC cartridge extension |
| SFCC Wildcard | `require('*/cartridge/...')` | Cross-cartridge resolution |

## Best Practices

### Platform Adaptation
- Always verify which JS features your target platform supports before coding
- SFCC: Use CommonJS, avoid async/await, leverage `dw.*` API
- PWA Kit: Use full modern JS/TS, React hooks, Commerce SDK
- LWC: Use ES modules, decorators, respect Lightning Web Security

### Code Quality
- Use `const` by default, `let` when reassignment is needed, never `var` (except SFCC if required)
- Prefer modern array methods (`map`, `filter`, `reduce`) over imperative loops
- Use optional chaining (`?.`) and nullish coalescing (`??`) where supported
- Destructure to extract values for cleaner, more readable code

### TypeScript (PWA Kit)
- Use TypeScript for type safety and better IDE support
- Leverage Commerce SDK types for API responses
- Use `Partial<T>`, `Pick<T>`, `Omit<T>` for flexible type definitions

Fetch MDN, TypeScript handbook, and platform-specific Salesforce docs for exact syntax support and API signatures before implementing.
