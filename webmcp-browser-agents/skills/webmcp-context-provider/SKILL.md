---
name: webmcp-context-provider
description: Implement the WebMCP provideContext API — bulk tool registration, contextual metadata, page state sharing, and dynamic context updates. Use when providing rich context and multiple tools to agents simultaneously.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# WebMCP Context Provider

## Before writing code

**Fetch live docs**:
1. Fetch `https://webmachinelearning.github.io/webmcp/` for the `provideContext` method specification
2. Web-search `webmcp provideContext specification` for the API shape and options
3. Web-search `webmcp context metadata agent` for contextual data patterns
4. Web-search `site:developer.chrome.com webmcp context` for Chrome-specific context features

## Conceptual Architecture

### What provideContext Does

`navigator.modelContext.provideContext(options)` is a method for bulk registration of multiple tools and providing additional contextual metadata to agents. While `registerTool` adds one tool at a time, `provideContext` can set up an entire tool surface in a single call.

**Note:** This API is still being specified and may change. Always fetch the latest spec before implementing.

### Why Context Matters

Agents make better decisions when they understand the current page state:
- What page the user is on (product detail, cart, checkout)
- User's authentication state and preferences
- Current cart contents and totals
- Available promotions or special offers
- Site capabilities and limitations

### provideContext vs registerTool

| Aspect | registerTool | provideContext |
|--------|-------------|----------------|
| **Granularity** | One tool at a time | Multiple tools + metadata |
| **Metadata** | Tool-level only | Page-level context included |
| **Use case** | Dynamic, individual tools | Page initialization, bulk setup |
| **Lifecycle** | Register/unregister individually | Set/clear entire context |

### Contextual Metadata Patterns

Provide agents with situational awareness:

**Product page context:**
```js
navigator.modelContext.provideContext({
  tools: [viewDetails, addToCart, compareProducts],
  metadata: {
    pageType: "product-detail",
    productId: "sku-12345",
    productName: "Wireless Headphones",
    price: 79.99,
    inStock: true,
    userAuthenticated: true
  }
});
```

**Cart page context:**
```js
navigator.modelContext.provideContext({
  tools: [updateQuantity, removeItem, applyCoupon, checkout],
  metadata: {
    pageType: "shopping-cart",
    itemCount: 3,
    subtotal: 247.50,
    currency: "USD",
    hasShippingAddress: true,
    hasSavedPayment: true
  }
});
```

### Dynamic Context Updates

Update context as the page state changes:

```js
// Initial page load — browse tools
navigator.modelContext.provideContext({
  tools: [searchProducts, viewDetails],
  metadata: { pageType: "catalog", authenticated: false }
});

// User logs in — expand tools
navigator.modelContext.clearContext();
navigator.modelContext.provideContext({
  tools: [searchProducts, viewDetails, addToCart, getCartContents, checkout],
  metadata: { pageType: "catalog", authenticated: true, userName: "Alice" }
});

// Navigate to cart — switch tools
navigator.modelContext.clearContext();
navigator.modelContext.provideContext({
  tools: [updateQuantity, removeItem, applyCoupon, checkout],
  metadata: { pageType: "cart", itemCount: 3 }
});
```

### SPA Route-Based Context

In single-page applications, update context on route changes:

```js
router.on("routeChange", (route) => {
  navigator.modelContext.clearContext();

  switch (route.name) {
    case "catalog":
      provideCatalogContext();
      break;
    case "product":
      provideProductContext(route.params.id);
      break;
    case "cart":
      provideCartContext();
      break;
    case "checkout":
      provideCheckoutContext();
      break;
  }
});
```

### Best Practices

- Use `provideContext` for initial page setup; use `registerTool` / `unregisterTool` for incremental changes
- Include page type and user state in metadata so agents understand the current context
- Clear context on navigation and re-provide for the new page
- Keep metadata lightweight — summaries, not full data dumps
- Avoid including sensitive user data (email, address) in metadata — agents don't need it
- Update context when significant state changes occur (login, cart update, page navigation)

Fetch the specification for the exact `provideContext` options shape, metadata fields, and any new features before implementing.
