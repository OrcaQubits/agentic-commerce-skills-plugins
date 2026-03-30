---
name: sf-b2b-apex
description: >
  Build B2B Commerce Apex extensions using the CartExtension namespace —
  PricingCartCalculator, ShippingCartCalculator, TaxCartCalculator,
  InventoryCartCalculator implementations, governor limits, bulkification, test
  coverage (75% minimum), and checkout flow customization. Use when implementing
  server-side B2B commerce logic.
---

# Salesforce B2B Commerce Apex Extensions (CartExtension Namespace)

## Before Writing Code

**ALWAYS fetch live documentation BEFORE writing any Apex code:**

1. Web-search: "Salesforce B2B Commerce Apex developer guide 2026"
2. Web-search: "Salesforce B2B Commerce checkout integration Spring 2026"
3. Web-fetch official Salesforce documentation for:
   - B2B Commerce ConnectApi namespace reference
   - CartExtension namespace and AbstractCartCalculator class
   - Apex governor limits (latest release notes)
   - Test class requirements and best practices
4. Web-fetch: `https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/`
5. Web-fetch: `https://developer.salesforce.com/docs/commerce/salesforce-commerce/guide/b2b-cart-calculate.html`

**Why this matters:** Salesforce releases three times per year (Spring, Summer, Winter). Commerce APIs, CartExtension interfaces, and governor limits change. Live docs prevent using deprecated patterns.

## Conceptual Architecture

### CartExtension Namespace Overview

Salesforce B2B Commerce uses the `CartExtension` namespace to provide extension points for customizing checkout logic. Each calculator extends `CartExtension.AbstractCartCalculator` and overrides the `calculate()` method.

| Extension Point | Purpose | Example Use Cases |
|---|---|---|
| `PricingCartCalculator` | Custom pricing calculations | Volume discounts, contract pricing, tiered pricing |
| `ShippingCartCalculator` | Shipping rate determination | Carrier integration, zone-based rates |
| `TaxCartCalculator` | Tax calculations | Avalara, Vertex, custom tax engines |
| `InventoryCartCalculator` | Real-time inventory validation | Warehouse checks, ATP calculations |

### Calculator Lifecycle

1. Customer adds items to cart or initiates checkout
2. Platform invokes registered calculator's `calculate()` method
3. Calculator receives `CartCalculateCalculatorRequest` with access to the full cart
4. Calculator reads cart items via `request.getCart()`, which returns a `CartExtension.Cart`
5. Calculator performs business logic (SOQL queries, external callouts, computations)
6. Calculator writes results back to cart items (prices, tax amounts, shipping methods, inventory status)
7. Platform validates results and continues to the next checkout step

### Key CartExtension Objects

| Object | Access Method | Purpose |
|---|---|---|
| `Cart` | `request.getCart()` | Root cart object with all items and delivery groups |
| `CartItemList` | `cart.getCartItems()` | Iterable list of all line items |
| `CartItem` | `cartItems.get(index)` | Individual line item with product, quantity, pricing |
| `CartDeliveryGroupList` | `cart.getCartDeliveryGroups()` | Shipping delivery groups |
| `CartDeliveryGroup` | `deliveryGroups.get(index)` | Address, shipping method, delivery charges |
| `CartDeliveryGroupMethod` | Constructor-based | Shipping option with name, cost, carrier |

Note: `CartItemList` uses index-based access (`get(i)`) and `size()`, not enhanced for-loops.

### Calculator Registration (UI-Only)

Register calculators via the Salesforce UI. There is **NO** custom metadata type (`B2B_Commerce_Hook__mdt` or similar) for registration.

1. Navigate to **Commerce Setup > Integrations > Register Cart Calculator**
2. Select the calculator type (Pricing, Shipping, Tax, or Inventory)
3. Assign your Apex class that extends the appropriate abstract class
4. Registration is per-store -- each B2B store can have its own calculator implementations
5. Only one calculator per type per store can be active at a time

### Governor Limits

| Limit | Synchronous | Asynchronous |
|---|---|---|
| SOQL queries | 100 | 200 |
| DML statements | 150 | 150 |
| CPU time | 10,000 ms | 60,000 ms |
| Heap size | 6 MB | 12 MB |
| Callouts per transaction | 100 | 100 |
| Callout timeout (per call) | 10 s (configurable up to 120 s) | 10 s |
| Callout total response size | 12 MB | 12 MB |
| Future calls per transaction | 50 | 0 (not allowed from async) |
| Queueable jobs per transaction | 50 | 1 |

Custom Metadata queries do **NOT** count against SOQL limits. Always verify these limits against the current release notes -- values change across Salesforce releases.

### Bulkification Rules

B2B carts can have hundreds of line items. All calculator code must be bulkified:

- Collect all product IDs in a single pass over cart items
- Execute one SOQL query using `WHERE Id IN :idSet`
- Use `Map<Id, SObject>` for O(1) lookups when applying results
- Never place SOQL or DML inside a loop
- Use `List<SObject>` for batch DML operations
- Use relationship queries (parent-child SOQL) to reduce query count further

### Callout Patterns Within calculate()

| Pattern | Returns Value? | Accepts Complex Params? | Use in calculate()? |
|---|---|---|---|
| Synchronous HTTP | Yes | Yes | Yes -- preferred for real-time data |
| `@future(callout=true)` | No (void only) | No (primitives only) | Not for return values |
| `Queueable` | No (async) | Yes | For post-processing follow-up |

- Always use **Named Credentials** (`callout:MyCredential/path`) -- never hardcode auth headers
- Set explicit timeouts on all callouts (`req.setTimeout(10000)`)
- Implement fallback logic when external services are unavailable

### ConnectApi Namespace

The `ConnectApi` namespace provides programmatic cart and checkout operations:

| Class | Purpose |
|---|---|
| `ConnectApi.CommerceCart` | Create, retrieve, delete carts; add items |
| `ConnectApi.CommerceCatalog` | Product search, category browse |
| `ConnectApi.CheckoutInput` / `CartCheckoutOutput` | Start and manage checkout |

`ConnectApi` classes are not constructable in test context by default. Use wrapper/mock patterns or `Test.isRunningTest()` guards for testability.

### Test Requirements

- 75% minimum code coverage required for deployment; aim for 85%+ for calculators
- Use `@TestSetup` to create shared test data (Account, Product2, WebStore, WebCart, CartDeliveryGroup, CartItem)
- `CartCalculateCalculatorRequest` is not directly constructable in tests -- test business logic methods separately
- Use `Test.setMock(HttpCalloutMock.class, ...)` for callout tests
- Assert governor limits with `Limits.getQueries()`, `Limits.getDmlStatements()`, `Limits.getCpuTime()`
- Required test scenarios: empty cart, null product reference, zero quantity, bulk (200+ items), callout success, callout failure, graceful degradation

### Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Calculator class | `[Purpose]Calculator` | `VolumePricingCalculator` |
| Test class | `[ClassName]Test` | `VolumePricingCalculatorTest` |
| Test data factory | `B2BCommerceTestDataFactory` | Shared across test classes |
| Custom Metadata | `Commerce_Config__mdt` | Configuration without SOQL cost |
| Platform Cache | `local.CommerceCache` | Frequently accessed pricing data |
| Queueable job | `[Purpose]Job` | `ShippingRateLoggerJob` |

## Code Examples

**Pattern: CartExtension calculator skeleton**

```apex
public class MyCalculator extends CartExtension.PricingCartCalculator {
    public override void calculate(
        CartExtension.CartCalculateCalculatorRequest request
    ) {
        CartExtension.Cart cart = request.getCart();
        // Fetch live docs for CartCalculateCalculatorRequest API
    }
}
```

**Pattern: Bulkified query + map lookup**

```apex
Set<Id> ids = new Set<Id>();
// ... collect ids from cart items ...
Map<Id, Product2> products = new Map<Id, Product2>(
    [SELECT Id, Field__c FROM Product2 WHERE Id IN :ids]
);
// ... apply via products.get(itemProductId) ...
```

**Pattern: HttpCalloutMock for tests**

```apex
private class MockResponse implements HttpCalloutMock {
    public HttpResponse respond(HttpRequest req) {
        // Fetch live docs for HttpCalloutMock interface
    }
}
```

**Pattern: Graceful error handling in calculate()**

```apex
try {
    applyPricing(cartItems);
} catch (CalloutException e) {
    CommerceLogger.logError('Calculator', 'calculate', e);
    // Allow checkout to continue with existing prices
}
```

## Best Practices

### Bulkification and Performance
- Collect IDs first, single SOQL, map lookup -- never query in a loop
- Use Platform Cache (`Cache.Org`) for frequently accessed configuration data
- Use Custom Metadata for calculator configuration (free of SOQL limits)
- Use relationship queries to pull parent and child data in a single SOQL

### Error Handling
- Wrap calculator logic in try/catch; log errors but allow checkout to continue (graceful degradation)
- Set item-level messages via `item.setMessage()` for validation errors visible to the buyer
- Distinguish `QueryException`, `CalloutException`, and generic `Exception`
- Never re-throw exceptions unless the error should halt the entire checkout

### Testing
- Create a `B2BCommerceTestDataFactory` class for reusable test data
- Test happy path, empty cart, null product, bulk (200+ items), callout success, and callout failure
- Monitor governor limits in test assertions using `Limits` class methods
- Use `@TestVisible` annotation to expose private helper methods for unit testing

### Async Processing
- Use `Queueable` (not `@future`) for complex async post-processing after `calculate()`
- Implement `Database.AllowsCallouts` on Queueable classes that make HTTP calls
- Enqueue at end of `calculate()` with `System.enqueueJob()`
- Chain Queueable jobs for multi-step async workflows

---

Fetch the latest Salesforce B2B Commerce Apex developer guide and CartExtension namespace reference for exact method signatures and current governor limits before implementing.
