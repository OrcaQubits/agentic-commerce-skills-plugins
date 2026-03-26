---
name: sf-b2b-lwc
description: Build B2B Commerce LWC components — Lightning Web Components with @api/@track/@wire decorators, commerce-specific wire adapters, custom events, Lightning Web Security, Jest unit testing, and component lifecycle. Use when building B2B storefront UI components.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-b2b-lwc

Build Lightning Web Components for Salesforce B2B Commerce storefronts.

## Before Writing Code

**Fetch live docs BEFORE writing code:**

1. **Web-search** the latest:
   - "Salesforce Lightning Web Components Developer Guide 2026"
   - "Salesforce B2B Commerce LWC documentation 2026"
   - "lightning/commerce wire adapters 2026"
   - "Lightning Web Security LWC 2026"

2. **Web-fetch** official sources:
   - `developer.salesforce.com/docs/component-library/documentation/en/lwc`
   - `developer.salesforce.com/docs/commerce/salesforce-commerce/guide/lwc-for-b2b.html`
   - `developer.salesforce.com/docs/platform/lwc/guide/reference-wire-adapters-intro.html`

3. **Verify** current decorator syntax, commerce wire adapters, Jest testing patterns, and Lightning Web Security vs Locker behavior.

## Conceptual Architecture

### Component Structure (4 Parts)

| File | Purpose | Notes |
|------|---------|-------|
| `componentName.html` | Template | `{property}` binding, `lwc:if`/`lwc:else`, `for:each` |
| `componentName.js` | Controller | ES6 class extending `LightningElement`, decorators, lifecycle hooks |
| `componentName.css` | Styles | Component-scoped, `:host` selector, CSS custom properties |
| `componentName.js-meta.xml` | Metadata | API version, targets (Experience Builder, App Builder), exposed properties |

### Decorators

| Decorator | Purpose | Reactivity |
|-----------|---------|-----------|
| `@api` | Public property (parent-settable) or public method | Re-renders on change from parent |
| `@track` | Deep reactivity for objects/arrays | Only needed for nested mutation (e.g., `this.obj.nested = val`) |
| `@wire` | Reactive data fetching from wire adapters | Re-fetches when reactive (`$`-prefixed) params change |

**Important:** Primitive class fields are auto-tracked in modern LWC -- `@track` is only needed for deep object/array mutation. Reassigning the entire object triggers reactivity without `@track`.

### Lifecycle Hooks

| Hook | When | Use For |
|------|------|---------|
| `constructor()` | Instance created | Initialize non-reactive state; cannot access DOM or properties |
| `connectedCallback()` | Inserted into DOM | Initialization, subscriptions (LMS, platform events) |
| `renderedCallback()` | After every render | DOM access; use sparingly (called frequently) |
| `disconnectedCallback()` | Removed from DOM | Cleanup listeners, unsubscribe channels, release resources |
| `errorCallback(error, stack)` | Child component error | Error boundary; log or display user-friendly messages |

### Wire Adapters

Wire adapters provide reactive, cached data fetching. Two binding styles exist:

- **Property binding**: `@wire(adapter, params) propertyName;` -- result is `{ data, error }`
- **Function binding**: `@wire(adapter, params) functionName({ data, error }) { ... }` -- for custom handling

Commerce-specific adapters live under the `lightning/commerce` and `commerce/*` namespaces. Fetch live docs for the current list of available commerce wire adapters (products, pricing, cart, inventory).

```javascript
// Pattern: Wire adapter usage
// Fetch live docs for adapter params
@wire(getProduct, { productId: '$productId' })
product;
```

### Custom Events

Communication from child to parent uses `CustomEvent`:

| Property | Purpose |
|----------|---------|
| `detail` | Event payload (keep minimal) |
| `bubbles` | Propagate up the DOM tree |
| `composed` | Cross shadow DOM boundary |

Parent listens via `on[eventname]` attribute in template (all lowercase).

### Component Communication Patterns

| Direction | Mechanism |
|-----------|-----------|
| Parent to Child | `@api` properties set in parent template |
| Child to Parent | `CustomEvent` dispatched from child |
| Sibling / Unrelated | Lightning Message Service (LMS) via `publish`/`subscribe` |

### Security: Lightning Web Security (LWS)

LWS (default since Spring '23) replaces the legacy Locker Service:
- Native browser security via JavaScript sandboxing
- Shadow DOM enforcement for component isolation
- CSP (Content Security Policy) compliance
- Better performance than legacy Locker
- Supports modern browser APIs

**Restrictions:** No `eval()`, no `Function()`, no `setTimeout(string)`. Use `@salesforce/resourceUrl` for static resources. Follow CRUD/FLS patterns for data access.

### Experience Builder Integration

Components are exposed to Experience Builder via the `js-meta.xml` file:
- Set `<isExposed>true</isExposed>`
- Add `lightningCommunity__Page` and `lightningCommunity__Default` targets
- Define configurable `<property>` elements (String, Integer, Boolean, etc.)
- Properties appear in the Experience Builder property panel for drag-and-drop configuration

### Jest Testing

LWC components are unit-tested with `@salesforce/sfdx-lwc-jest`. Key concepts:
- Mock wire adapters and Apex methods with `jest.mock()`
- Use `createElement` from `lwc` to instantiate components
- Access rendered DOM via `element.shadowRoot.querySelector()`
- Emit mock data from wire adapters; assert DOM changes after `Promise.resolve()`
- Clean up DOM in `afterEach` to avoid test pollution

```javascript
// Pattern: Jest test skeleton
// Fetch live docs for mock utilities
import { createElement } from 'lwc';
import MyComponent from 'c/myComponent';
```

## Best Practices

### Data Fetching
- Use `@wire` for read-only data (reactive, cached via Lightning Data Service)
- Use imperative Apex for mutations (create, update, delete)
- Batch API calls to reduce server round-trips

### Performance
- Minimize `renderedCallback` logic (runs on every render)
- Use getters for computed values (lazy evaluation)
- Debounce user input handlers
- Lazy-load large components via dynamic imports

### Testing
- Write Jest tests for all components
- Mock wire adapters and Apex; test user interactions and error states
- Test accessibility: ARIA attributes, keyboard navigation

### B2B Commerce Specific
- Respect buyer context (account, buyer group, entitlements)
- Handle guest vs authenticated experiences
- Display correct per-account pricing and product visibility
- Support multi-currency display in buyer's currency

Fetch the LWC Developer Guide, B2B Commerce LWC docs, and wire adapter reference for exact decorator behavior, adapter parameters, and testing utilities before implementing.
