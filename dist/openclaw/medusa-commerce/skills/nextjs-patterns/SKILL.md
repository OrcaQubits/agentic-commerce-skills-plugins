---
name: nextjs-patterns
description: >
  Build Next.js 15 storefronts for Medusa v2 — App Router conventions, server
  vs client components, Medusa JS SDK integration, data fetching, caching, and
  server actions. Use when building Medusa storefronts with Next.js.
---

# Next.js 15 Storefront Patterns for Medusa v2

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com storefront nextjs` for Medusa storefront guides
2. Fetch `https://docs.medusajs.com/resources/references/js-sdk` for JS SDK method reference
3. Web-search `site:nextjs.org docs app router` for latest Next.js 15 App Router conventions
4. Web-search `site:docs.medusajs.com nextjs starter storefront` for starter template patterns
5. Web-search `site:docs.medusajs.com publishable api key storefront` for API authentication setup

## App Router Conventions

### Directory Structure

```
src/app/
├── layout.tsx        — Root layout (providers, SDK)
├── page.tsx          — Home page
├── (main)/products/  — Product listing + [handle]/
├── (main)/cart/      — Cart, checkout, account
└── lib/medusa.ts     — SDK client initialization
```

### Key App Router Concepts

| Concept | File Convention | Purpose in Medusa Storefront |
|---------|----------------|------------------------------|
| Layout | `layout.tsx` | Wrap pages with providers, header, footer |
| Page | `page.tsx` | Route entry point (server component default) |
| Loading | `loading.tsx` | Streaming fallback UI |
| Error | `error.tsx` | Error boundary per route segment |
| Not Found | `not-found.tsx` | 404 page for invalid product handles, etc. |
| Route Groups | `(group)/` | Organize without affecting URL |
| Dynamic Routes | `[param]/` | Product handles, category slugs |
| Parallel Routes | `@slot/` | Simultaneous layout regions |

## Server vs Client Components

### Decision Matrix

| Criterion | Server Component | Client Component |
|-----------|-----------------|-----------------|
| **Data fetching** | Fetch from Medusa API directly | Use Tanstack Query hooks |
| **SEO** | Full HTML rendered on server | Not indexed by crawlers |
| **Interactivity** | No event handlers | onClick, onChange, etc. |
| **State** | No `useState`/`useEffect` | Full React hooks |
| **Examples** | Product listing, product detail, categories | Cart actions, quantity selector, search |
| **Directive** | None (default) | `"use client"` at top |

### Component Split Pattern

```
ProductPage (server)
├── ProductInfo (server)      — Title, description, price
├── ProductImages (server)    — Image gallery markup
├── AddToCart (client)        — "use client", quantity, button
└── RelatedProducts (server)  — Fetched server-side
```

## Medusa JS SDK Integration

### SDK Initialization and Configuration

| Option | Purpose | Example Value |
|--------|---------|---------------|
| `baseUrl` | Medusa server URL | `http://localhost:9000` |
| `publishableKey` | Store API authentication | From admin dashboard |
| `auth.type` | Authentication strategy | `"session"` or `"jwt"` |

### Common SDK Methods

| Domain | Method Pattern | Component Type |
|--------|---------------|---------------|
| Products | `sdk.store.product.list()` | Server (listing) |
| Products | `sdk.store.product.retrieve(id)` | Server (detail) |
| Cart | `sdk.store.cart.create()` | Client (interaction) |
| Cart | `sdk.store.cart.addLineItem()` | Client (interaction) |
| Cart | `sdk.store.cart.update()` | Client (interaction) |
| Checkout | `sdk.store.cart.addShippingMethod()` | Client (checkout flow) |
| Customer | `sdk.auth.login()` | Client (auth form) |
| Customer | `sdk.store.customer.retrieve()` | Server or Client |
| Regions | `sdk.store.region.list()` | Server (layout) |
| Collections | `sdk.store.collection.list()` | Server (navigation) |

## Data Fetching Patterns

### Server Component Fetching

Call the Medusa SDK directly in server components — no hooks needed:

```ts
// Fetch live docs for server-side SDK
// usage and async component patterns
```

| Pattern | Use Case |
|---------|----------|
| Direct `await sdk.store.*` | Server components with async data |
| `generateMetadata()` | Dynamic SEO metadata from product data |
| `generateStaticParams()` | ISR/SSG for product and category pages |

### Client Component Fetching (Tanstack Query)

| Hook / Concern | Purpose |
|----------------|---------|
| `useQuery` | Read data with caching and automatic refetch |
| `useMutation` | Write operations (add to cart, login) |
| `useQueryClient` | Invalidate cache after mutations |
| Query keys | Use consistent keys like `["cart", cartId]` |
| Optimistic updates | Update cart UI immediately, rollback on error |
| Prefetching | Prefetch product data on hover for navigation |

## Caching Strategies

### Next.js Caching Layers

| Layer | Scope | Medusa Use Case |
|-------|-------|-----------------|
| **Request Memoization** | Per-request dedup | Multiple components fetching same product |
| **Data Cache** | Cross-request | Product catalog data (revalidate periodically) |
| **Full Route Cache** | Entire page | Static product pages (ISR) |
| **Router Cache** | Client-side | Navigation between cached pages |

### Revalidation Patterns

| Strategy | Method | Use Case |
|----------|--------|----------|
| Time-based | `revalidate: 60` (seconds) | Product listings, category pages |
| On-demand | `revalidatePath()` / `revalidateTag()` | After admin product update |
| No cache | `cache: "no-store"` | Cart, checkout, customer data |

### Cache Configuration per Data Type

| Data Type | Cache Strategy | Reasoning |
|-----------|---------------|-----------|
| Products | `revalidate: 60-300` | Changes infrequently |
| Collections | `revalidate: 300-3600` | Rarely changes |
| Cart | `no-store` | User-specific, changes constantly |
| Customer | `no-store` | Private, per-session |
| Regions | `revalidate: 3600` | Almost never changes |
| Prices | `revalidate: 60` | May change with promotions |

## Server Actions

Server actions handle form submissions and mutations from server components:

```ts
// Fetch live docs for Next.js server actions
// with Medusa SDK mutation patterns
"use server"
```

| Use Case | Action Pattern |
|----------|---------------|
| Add to cart | Server action calling `sdk.store.cart.addLineItem()` |
| Update quantity | Server action with `revalidatePath` |
| Apply discount | Server action calling `sdk.store.cart.update()` |
| Customer login | Server action wrapping `sdk.auth.login()` |

Use server actions for simple form mutations. Use API routes when external systems need to call your storefront.

## Storefront Environment Variables

| Variable | Purpose | Where Used |
|----------|---------|-----------|
| `NEXT_PUBLIC_MEDUSA_BACKEND_URL` | Medusa server URL | Client + Server |
| `NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY` | Store API key | Client + Server |
| `REVALIDATE_WINDOW` | Default ISR revalidation time | Server only |

## Best Practices

- **Component boundaries** — default to server components; add `"use client"` only for interactive elements; split pages into server (data) and client (interaction) sub-components
- **SDK usage** — initialize once in a shared module; use server-side calls in server components for SEO; use Tanstack Query in client components for reactivity and caching
- **Caching discipline** — cache product and collection data aggressively; never cache cart or customer data; use on-demand revalidation for admin-triggered updates; monitor cache hit rates
- **Performance** — use `loading.tsx` for streaming with Suspense boundaries; prefetch data for likely navigation targets; optimize images with `next/image` and Medusa media URLs

Fetch the Medusa Next.js storefront documentation and JS SDK reference for exact method signatures, query key conventions, and starter template patterns before implementing.
