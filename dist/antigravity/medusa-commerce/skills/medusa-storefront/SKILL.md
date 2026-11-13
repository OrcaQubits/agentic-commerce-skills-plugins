---
name: medusa-storefront
description: >
  Build Medusa v2 storefronts with Next.js 15 — App Router, JS SDK client
  setup, Tanstack Query, server components, product pages, cart, and checkout
  flow. Use when developing headless storefronts.
---

# Medusa v2 Storefront with Next.js

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/resources/storefront-development` for storefront overview
2. Web-search `site:docs.medusajs.com nextjs starter storefront` for starter template
3. Web-search `site:docs.medusajs.com JS SDK client setup` for Medusa SDK configuration
4. Web-search `site:docs.medusajs.com storefront API reference` for Store API endpoints
5. Web-search `site:github.com medusajs nextjs-starter-medusa` for latest starter source

## Storefront Architecture

Medusa v2 storefronts are headless -- they consume the Store API over HTTP:

| Layer | Component |
|-------|-----------|
| Frontend | Next.js App (SSR/RSC) |
| HTTP Client | Medusa JS SDK |
| Backend | Medusa Backend (`/store/*` API routes) |
| Storage | PostgreSQL / Redis |

## Next.js Starter Structure

| Directory | Key Files |
|-----------|-----------|
| `app/` | `layout.tsx`, `page.tsx` (homepage) |
| `app/(main)/products/` | `page.tsx` (listing), `[handle]/page.tsx` (detail) |
| `app/(main)/collections/` | `[handle]/page.tsx` (collection) |
| `app/(main)/cart/`, `app/(main)/checkout/` | Cart page, checkout flow |
| `app/(auth)/`, `app/account/` | Login/register, customer dashboard |
| `lib/` | `sdk.ts` (Medusa client), `data/` (fetching), `util/` |
| `components/` | `products/`, `cart/`, `checkout/`, `layout/` |
| Root | `next.config.js`, `.env.local` |

## JS SDK Client Setup

### SDK Installation

The Medusa JS SDK provides typed access to the Store API:

```typescript
// lib/sdk.ts — Fetch live docs for Medusa SDK initialization
import Medusa from "@medusajs/js-sdk"

export const sdk = new Medusa({
  baseUrl: process.env.NEXT_PUBLIC_MEDUSA_BACKEND_URL!,
  // Fetch live docs for publishableKey and other options
})
```

### Environment Variables

```
NEXT_PUBLIC_MEDUSA_BACKEND_URL=http://localhost:9000
NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY=pk_...
```

The publishable API key is required for Store API requests and scopes them to a specific sales channel.

## Key Store API Domains

| Domain | SDK Namespace | Key Operations |
|--------|--------------|----------------|
| Products | `sdk.store.product` | List, retrieve by handle |
| Collections | `sdk.store.collection` | List, retrieve |
| Categories | `sdk.store.category` | List, tree |
| Cart | `sdk.store.cart` | Create, add items, update |
| Checkout | `sdk.store.cart` | Add shipping, complete |
| Customer | `sdk.store.customer` | Register, login, profile |
| Orders | `sdk.store.order` | List customer orders |
| Regions | `sdk.store.region` | List regions and currencies |
| Shipping | `sdk.store.fulfillment` | List shipping options |

> **Fetch live docs** for the complete SDK namespace list and method signatures.

## Server Components vs Client Components

| Pattern | Use For |
|---------|---------|
| Server Component (RSC) | Product listing, product detail, static content |
| Client Component | Cart interactions, checkout form, quantity selectors |
| Server Action | Cart mutations, checkout submission |

### Data Fetching in Server Components

```typescript
// app/(main)/products/[handle]/page.tsx
// Fetch live docs for SDK method signatures
export default async function ProductPage({ params }) {
  const { product } = await sdk.store.product.retrieve(params.handle)
  return <ProductTemplate product={product} />
}
```

## Cart Flow

| Step | Action | SDK Method |
|------|--------|-----------|
| 1. Create cart | On first add-to-cart | `sdk.store.cart.create()` |
| 2. Add line item | User adds product | `sdk.store.cart.addLineItem()` |
| 3. Update quantity | User changes qty | `sdk.store.cart.updateLineItem()` |
| 4. Remove item | User removes product | `sdk.store.cart.removeLineItem()` |
| 5. Set region | Auto or user selection | `sdk.store.cart.update()` |

Cart ID is typically stored in a cookie or localStorage for persistence across sessions.

## Checkout Flow

| Step | Required Data | SDK Call |
|------|--------------|---------|
| 1. Address | Shipping + billing address | `sdk.store.cart.update()` |
| 2. Shipping | Selected shipping option | `sdk.store.cart.addShippingMethod()` |
| 3. Payment | Payment provider session | `sdk.store.cart.initiatePaymentSession()` |
| 4. Complete | Confirmation | `sdk.store.cart.complete()` |

## Customer Authentication

| Flow | Description |
|------|-------------|
| Registration | Create customer account via Store API |
| Login | Authenticate and receive session token |
| Session | Token stored in cookie, sent with requests |
| Profile | Update customer info, addresses |
| Orders | View past orders linked to customer |

```typescript
// Fetch live docs for customer auth SDK methods
await sdk.auth.login("customer", "emailpass", {
  email: "user@example.com",
  password: "password",
})
```

## Region and Currency Handling

- Medusa supports multiple regions with different currencies
- Storefront should detect or let the user select a region
- All product prices are region-aware
- Cart is tied to a region which determines currency and tax rules

## Performance Considerations

| Technique | Implementation |
|-----------|---------------|
| Static Generation (SSG) | Use `generateStaticParams` for product pages |
| ISR | Revalidate product pages periodically |
| Streaming | Use Suspense boundaries for slow data |
| Image optimization | Use Next.js `<Image>` with Medusa image URLs |
| Prefetching | Use `<Link>` for product navigation |

## Best Practices

- Use Server Components for data fetching -- minimize client-side JavaScript
- Store the cart ID in a cookie for cross-tab and SSR access
- Use the publishable API key to scope requests to the correct sales channel
- Handle region/currency at the layout level, not per-page
- Implement optimistic UI updates for cart operations to improve perceived performance
- Use `generateStaticParams` for product and collection pages for SEO and speed
- Keep checkout as a linear flow -- do not allow skipping steps

Fetch the Medusa storefront documentation and Next.js starter source for exact SDK method signatures, component patterns, and checkout flow details before implementing.
