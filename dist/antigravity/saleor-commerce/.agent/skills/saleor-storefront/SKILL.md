---
name: saleor-storefront
description: >
  Build Next.js storefronts for Saleor — GraphQL client setup, channel routing,
  Tailwind CSS, server components, checkout flow, and SEO. Use when developing
  Saleor storefronts.
---

# Saleor Next.js Storefront

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/storefront` for storefront development guide
2. Web-search `site:docs.saleor.io storefront GraphQL client setup` for client configuration
3. Web-search `site:github.com saleor/storefront nextjs` for latest storefront starter source
4. Web-search `site:docs.saleor.io checkout flow storefront` for checkout integration
5. Web-search `site:docs.saleor.io channel storefront routing` for multi-channel setup

## Storefront Architecture

Saleor storefronts are headless -- they consume the GraphQL API over HTTP:

| Layer | Component |
|-------|-----------|
| Frontend | Next.js App Router (SSR / RSC) |
| GraphQL Client | urql, Apollo Client, or graphql-request |
| API | Saleor GraphQL endpoint (`/graphql/`) |
| Styling | Tailwind CSS (official starter) |
| Deployment | Vercel, Netlify, or any Node.js host |

## GraphQL Client Options

| Client | Strengths | Best For |
|--------|-----------|----------|
| `urql` | Lightweight, extensible, SSR-friendly | Official starter default |
| `Apollo Client` | Mature ecosystem, normalized cache | Complex caching needs |
| `graphql-request` | Minimal, no framework dependency | Simple server-side fetching |
| `fetch` (raw) | Zero dependencies | One-off queries in server components |

### Client Setup Pattern

```typescript
// lib/graphql-client.ts
// Fetch live docs for current client initialization
import { createClient, cacheExchange, fetchExchange } from "urql"

export const client = createClient({
  url: process.env.NEXT_PUBLIC_SALEOR_API_URL!,
  exchanges: [cacheExchange, fetchExchange],
})
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_SALEOR_API_URL` | Saleor GraphQL endpoint URL |
| `SALEOR_API_URL` | Server-side only API URL (if different) |
| `NEXT_PUBLIC_DEFAULT_CHANNEL` | Default channel slug |
| `NEXT_PUBLIC_STOREFRONT_URL` | Public storefront URL (for SEO) |

## Channel-Based URL Routing

Saleor channels enable multi-region storefronts from a single instance:

| URL Pattern | Channel | Currency |
|-------------|---------|----------|
| `/en-us/products` | `default-channel` | USD |
| `/en-gb/products` | `channel-uk` | GBP |
| `/de/products` | `channel-de` | EUR |

### Routing Strategy

| Approach | Implementation |
|----------|---------------|
| Path prefix | `/[channel]/products` in Next.js App Router |
| Subdomain | `us.store.com`, `uk.store.com` with middleware |
| Cookie/header | Single URL, channel detected from locale preference |

The channel slug is passed as an argument to every GraphQL query that returns channel-scoped data (products, pricing, collections).

## Key Storefront Pages

| Page | Route | Data Source |
|------|-------|-------------|
| Homepage | `/` | Featured products, collections |
| Product listing | `/products` | `products(channel, first, filter)` query |
| Product detail | `/products/[slug]` | `product(slug, channel)` query |
| Collection | `/collections/[slug]` | `collection(slug, channel)` query |
| Category | `/categories/[slug]` | `category(slug)` + products query |
| Cart | `/cart` | Local state + cart GraphQL object |
| Checkout | `/checkout` | `checkout` query and mutations |
| Account | `/account` | `me` query (authenticated) |
| Order history | `/account/orders` | `me { orders }` query |
| Search | `/search` | `products(filter: {search})` query |

## Server vs Client Component Split

| Pattern | Use For |
|---------|---------|
| Server Component (RSC) | Product listing, product detail, static content, SEO metadata |
| Client Component | Cart drawer, quantity selector, add-to-cart button, checkout form |
| Server Action | Cart mutations, checkout steps, address submission |
| Route Handler | Webhook receivers, revalidation triggers |

### Data Fetching in Server Components

```typescript
// app/products/[slug]/page.tsx
// Fetch live docs for current query patterns
export default async function ProductPage({ params }) {
  const { product } = await executeQuery(ProductBySlugDocument, {
    slug: params.slug, channel: DEFAULT_CHANNEL,
  })
  return <ProductTemplate product={product} />
}
```

## Checkout Flow

| Step | User Action | GraphQL Operation |
|------|-------------|-------------------|
| 1. Create checkout | First add-to-cart | `checkoutCreate` mutation |
| 2. Add lines | Add products to cart | `checkoutLinesAdd` mutation |
| 3. Update lines | Change quantity | `checkoutLinesUpdate` mutation |
| 4. Set email | Enter email | `checkoutEmailUpdate` mutation |
| 5. Shipping address | Enter address | `checkoutShippingAddressUpdate` mutation |
| 6. Billing address | Enter or same as shipping | `checkoutBillingAddressUpdate` mutation |
| 7. Select shipping | Choose method | `checkoutDeliveryMethodUpdate` mutation |
| 8. Payment | Enter payment details | `transactionInitialize` or gateway-specific |
| 9. Complete | Confirm order | `checkoutComplete` mutation |

Checkout ID is stored in a cookie for persistence across sessions and server-side access.

## Caching Strategies

| Strategy | Use Case | Implementation |
|----------|----------|----------------|
| ISR | Product pages | `revalidate` in `fetch` options |
| On-demand | After product update webhook | `revalidatePath` / `revalidateTag` |
| Client cache | Cart state | urql/Apollo normalized cache |
| Static | Homepage collections | `generateStaticParams` |
| No cache | Checkout, account | `cache: "no-store"` in fetch |

## SEO with Server Components

| SEO Aspect | Implementation |
|-----------|---------------|
| Title and meta | `generateMetadata` in page components |
| Open Graph | Product images and descriptions in OG tags |
| Structured data | JSON-LD `Product` schema in script tags |
| Sitemap | Dynamic `sitemap.xml` from product/collection queries |
| Canonical URLs | `alternates.canonical` in metadata |
| Robots | `robots.txt` via Next.js convention |

## Image Handling

| Aspect | Detail |
|--------|--------|
| Source | Saleor media URL from product image fields |
| Optimization | Next.js `<Image>` component with remote patterns |
| Thumbnails | Saleor generates thumbnails at configurable sizes |
| CDN | Configure `next.config.js` `remotePatterns` for Saleor domain |

## Best Practices

- Use Server Components for all data fetching -- minimize client-side JavaScript
- Store checkout ID in an HTTP-only cookie for security and SSR access
- Scope every storefront query with the `channel` argument
- Use `generateStaticParams` for product and collection pages for SEO and speed
- Implement on-demand revalidation via webhooks for real-time content updates
- Handle multi-channel at the layout or middleware level, not per-page
- Use GraphQL code generation for type safety across all queries and mutations
- Keep the checkout as a linear flow -- do not allow skipping steps

Fetch the Saleor storefront documentation for exact GraphQL query patterns, checkout mutation sequences, and channel routing strategies before implementing.
