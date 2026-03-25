---
name: shopify-functions
description: Build Shopify Functions — serverless WebAssembly extensions for discounts, delivery customization, payment customization, cart validation, cart transforms, and order routing. Use when extending Shopify's backend logic.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify Functions (Serverless Wasm Extensions)

## Before writing code

**Fetch live docs**:
1. Fetch `https://shopify.dev/docs/apps/build/functions` for Functions overview
2. Web-search `site:shopify.dev shopify functions input output` for I/O schemas
3. Web-search `site:shopify.dev shopify functions api reference` for function types

## What Are Shopify Functions

Serverless extensions that run on Shopify's infrastructure:
- Written in JavaScript or Rust
- Compiled to **WebAssembly** (Wasm)
- Execute within Shopify's checkout and backend pipeline
- **11 million instruction limit** and **5ms execution time limit** — must be extremely fast
- No network access, no filesystem — pure computation on provided input
- Wasm binary size limit: 256 KB, input JSON size limit: 64 KB

## Function Types

| Type | Purpose | Example |
|------|---------|---------|
| **Discount** | Custom discount logic | Buy X get Y, tiered discounts |
| **Delivery customization** | Modify shipping options | Rename, reorder, hide methods |
| **Payment customization** | Modify payment methods | Hide, reorder, rename gateways |
| **Cart validation** | Block or warn on cart conditions | Quantity limits, product combos |
| **Cart transform** | Modify cart contents | Bundle expansion, auto-add items |
| **Fulfillment constraints** | Control fulfillment behavior | Location priority, restrictions |
| **Order routing** | Direct orders to locations | Closest warehouse, priority |

## Input/Output Model

Functions receive structured JSON input and return structured JSON output:

### Input (simplified)

```json
{
  "cart": {
    "lines": [
      {
        "id": "gid://shopify/CartLine/1",
        "quantity": 2,
        "merchandise": {
          "__typename": "ProductVariant",
          "id": "gid://shopify/ProductVariant/123",
          "product": {
            "id": "gid://shopify/Product/456",
            "hasAnyTag": true
          }
        },
        "cost": {
          "amountPerQuantity": { "amount": "29.99", "currencyCode": "USD" }
        }
      }
    ]
  },
  "discountNode": {
    "metafield": {
      "value": "{\"percentage\": 10}"
    }
  }
}
```

### Output (discount example)

```json
{
  "discounts": [
    {
      "value": { "percentage": { "value": "10.0" } },
      "targets": [
        { "productVariant": { "id": "gid://shopify/ProductVariant/123" } }
      ],
      "message": "10% loyalty discount"
    }
  ],
  "discountApplicationStrategy": "FIRST"
}
```

## Project Structure

```
extensions/my-discount/
├── src/
│   └── run.js          # Function entry point
├── input.graphql       # Defines what data the function receives
├── shopify.extension.toml  # Extension configuration
└── package.json
```

### Configuration (shopify.extension.toml)

```toml
api_version = "2025-01"

[[extensions]]
name = "My Discount"
handle = "my-discount"
type = "function"

  [extensions.build]
  command = "npm exec -- shopify app function build"
  path = "dist/function.wasm"

  [extensions.ui]
  handle = "my-discount-ui"

  [extensions.input.variables]
  namespace = "my-app"
  key = "discount-config"
```

### Input Query (input.graphql)

Defines what Shopify data the function receives:

```graphql
query Input {
  cart {
    lines {
      id
      quantity
      merchandise {
        ... on ProductVariant {
          id
          product {
            id
            hasAnyTag(tags: ["vip"])
          }
        }
      }
      cost {
        amountPerQuantity {
          amount
          currencyCode
        }
      }
    }
  }
  discountNode {
    metafield(namespace: "my-app", key: "discount-config") {
      value
    }
  }
}
```

## JavaScript Example

```javascript
// src/run.js
export function run(input) {
  const config = JSON.parse(input.discountNode.metafield?.value || '{}');
  const percentage = config.percentage || 0;

  const targets = input.cart.lines
    .filter(line => line.merchandise?.product?.hasAnyTag)
    .map(line => ({
      productVariant: { id: line.merchandise.id }
    }));

  if (targets.length === 0) {
    return { discounts: [], discountApplicationStrategy: "FIRST" };
  }

  return {
    discounts: [{
      value: { percentage: { value: String(percentage) } },
      targets,
      message: `${percentage}% VIP discount`,
    }],
    discountApplicationStrategy: "FIRST",
  };
}
```

## Performance Constraints

- **11 million instruction limit** — function fails with `InstructionCountLimitExceededError` if exceeded
- **5ms execution time limit** — Wasm module is killed if it runs longer
- **Input JSON size limit: 64 KB** — large carts may hit this
- No async operations (no Promises, no setTimeout)
- No network calls (no fetch, no HTTP)
- No filesystem access
- No global state between invocations
- Wasm binary size limit: 256 KB
- Rust is more instruction-efficient than JavaScript — consider Rust for complex logic
- Pre-compute and store config in metafields

## Best Practices

- Keep function logic simple — no complex algorithms
- Use metafields for configuration (read via input query)
- Test with `shopify app function run` locally
- Use TypeScript for type safety (compiled to JS then Wasm)
- Handle edge cases: empty carts, missing metafields, zero quantities
- Return early when no action is needed (return empty discounts array)
- Validate all input — metafield values may be malformed JSON

Fetch the Shopify Functions documentation for exact I/O schemas, supported function types, and API version requirements before implementing.
