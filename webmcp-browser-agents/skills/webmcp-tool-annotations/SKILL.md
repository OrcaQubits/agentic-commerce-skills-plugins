---
name: webmcp-tool-annotations
description: Implement WebMCP tool annotations — readOnlyHint, destructiveHint, idempotentHint safety hints that inform browser permission prompts and agent behavior. Use when marking tools with appropriate safety metadata.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# WebMCP Tool Annotations

## Before writing code

**Fetch live docs**:
1. Fetch `https://webmachinelearning.github.io/webmcp/` for the annotations specification
2. Web-search `webmcp tool annotations readOnlyHint destructiveHint idempotentHint` for annotation field details
3. Web-search `site:developer.chrome.com webmcp annotations permissions` for how Chrome uses annotations
4. Web-search `site:github.com mcp-b annotations` for polyfill support for annotations

## Conceptual Architecture

### What Annotations Are

Tool annotations are optional metadata attached to a tool definition that inform the browser and agent about the tool's behavior and safety characteristics. The browser uses annotations to decide whether to prompt the user for confirmation before allowing agent invocation.

### Available Annotations

| Annotation | Type | Default | Meaning |
|------------|------|---------|---------|
| `readOnlyHint` | boolean | `false` | Tool only reads data, does not modify any state |
| `destructiveHint` | boolean | `false` | Tool performs irreversible or significant actions |
| `idempotentHint` | boolean | `false` | Multiple calls with the same input produce the same effect as one call |

### How the Browser Uses Annotations

- **readOnlyHint: true** — Browser may allow agent to invoke without user confirmation
- **destructiveHint: true** — Browser should require explicit user consent before invocation
- **idempotentHint: true** — Browser may allow retries without additional confirmation
- No annotations — Browser applies its default permission policy

### Annotation Combinations

| readOnly | destructive | idempotent | Example | Browser Behavior |
|:--------:|:-----------:|:----------:|---------|-----------------|
| true | false | true | `searchProducts` | Likely auto-approved |
| false | false | true | `addToCart` | May auto-approve or prompt once |
| false | false | false | `updateProfile` | Likely prompts user |
| false | true | false | `placeOrder` | Always prompts user |
| false | true | true | `cancelSubscription` | Always prompts user (destructive overrides) |

### Commerce Tool Annotation Guide

| Tool | readOnly | destructive | idempotent |
|------|:--------:|:-----------:|:----------:|
| `searchProducts` | true | false | true |
| `viewProductDetails` | true | false | true |
| `getCartContents` | true | false | true |
| `addToCart` | false | false | true |
| `removeFromCart` | false | false | true |
| `updateCartQuantity` | false | false | true |
| `applyCoupon` | false | false | true |
| `checkout` | false | **true** | false |
| `placeOrder` | false | **true** | false |
| `initiateReturn` | false | **true** | false |
| `cancelOrder` | false | **true** | false |
| `deleteAccount` | false | **true** | false |
| `updateShippingAddress` | false | false | true |
| `getOrderHistory` | true | false | true |

### Implementation

```js
navigator.modelContext.registerTool({
  name: "searchProducts",
  description: "Search the product catalog",
  inputSchema: { /* ... */ },
  annotations: {
    readOnlyHint: true,
    idempotentHint: true
  },
  async execute(input) { /* ... */ }
});

navigator.modelContext.registerTool({
  name: "placeOrder",
  description: "Complete the purchase and charge the payment method",
  inputSchema: { /* ... */ },
  annotations: {
    destructiveHint: true
  },
  async execute(input, client) { /* ... with requestUserInteraction */ }
});
```

### Annotation Accuracy Matters

Incorrect annotations are a security risk:
- Marking a purchase tool as `readOnlyHint: true` could let agents bypass user confirmation
- Marking a search tool as `destructiveHint: true` creates unnecessary friction
- Annotations are **hints**, not guarantees — the tool must still implement proper checks

### Best Practices

- Annotate every tool — even if using defaults, explicit annotations make intent clear
- Combine `destructiveHint` with `requestUserInteraction()` for defense-in-depth
- Review annotations in code review as carefully as you review access control
- Test annotation behavior with real agents to verify browser permission prompts appear when expected
- Document the annotation rationale for each tool

Fetch the specification for any new annotation types, exact field names, and browser interpretation rules before implementing.
