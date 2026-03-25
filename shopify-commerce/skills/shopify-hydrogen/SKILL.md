---
name: shopify-hydrogen
description: Build headless Shopify storefronts with Hydrogen — Remix-based framework, Oxygen deployment, storefront.query(), caching strategies, cart, customer accounts, SEO, and analytics. Use when building custom Shopify storefronts.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify Hydrogen (Headless Storefronts)

## Before writing code

**Fetch live docs**:
1. Fetch `https://shopify.dev/docs/storefronts/headless/hydrogen` for Hydrogen documentation
2. Web-search `site:shopify.dev hydrogen remix loader action` for data fetching patterns
3. Web-search `site:github.com shopify hydrogen` for source, examples, and demo store
4. Web-search `site:shopify.dev hydrogen cart` for current cart handler API
5. Web-search `site:shopify.dev hydrogen customer accounts` for authentication flow

## What Is Hydrogen

Hydrogen is Shopify's React-based framework for headless commerce:
- Built on **Remix** (not Next.js) — server-side rendering, loaders, actions, nested routes
- Deployed to **Oxygen** (Shopify's edge hosting) or any Node.js-compatible host
- Optimized for Shopify's Storefront API
- Includes commerce-specific utilities: cart, customer accounts, SEO, analytics

> **DEPRECATION:** The JS Buy SDK (EOL July 2025) should NOT be used. Use Hydrogen or the Storefront API directly.

## Scaffold a New Project

```bash
npm create @shopify/hydrogen@latest -- --template demo-store
# or
shopify hydrogen init
```

### Project Structure

```
app/
├── components/         # Shared React components
├── lib/
│   └── context.ts      # Storefront client setup
├── routes/
│   ├── _index.tsx       # Homepage
│   ├── products.$handle.tsx  # Product detail (dynamic route)
│   ├── collections.$handle.tsx
│   ├── cart.tsx         # Cart page
│   └── account.tsx      # Customer account
├── entry.server.tsx     # Server entry point
└── root.tsx             # Root layout
```

## Core Concepts

### Storefront Client

The storefront client is created in your app context and used in loaders:

```typescript
// Pattern: create storefront client in context
// Fetch live docs for current createStorefrontClient options
const { storefront } = createStorefrontClient({
  storeDomain: env.PUBLIC_STORE_DOMAIN,
  storefrontApiVersion: env.PUBLIC_STOREFRONT_API_VERSION,
  publicStorefrontToken: env.PUBLIC_STOREFRONT_API_TOKEN,
});
```

### Loader Pattern (Data Fetching)

```typescript
// Pattern: loader fetches data via storefront.query with caching
// Fetch live docs for current Storefront API fields and query syntax
export async function loader({ params, context }: LoaderFunctionArgs) {
  const { storefront } = context;

  const { product } = await storefront.query(PRODUCT_QUERY, {
    variables: { handle: params.handle },
    cache: CacheLong(), // apply caching strategy
  });

  if (!product) throw new Response("Not found", { status: 404 });
  return json({ product });
}

export default function ProductPage() {
  const { product } = useLoaderData<typeof loader>();
  return <div><h1>{product.title}</h1></div>;
}
```

> **Fetch live docs** for the current Storefront API product query fields — the schema expands quarterly.

### Action Pattern (Mutations)

```typescript
// Pattern: action handles form submissions (e.g., cart mutations)
export async function action({ request, context }: ActionFunctionArgs) {
  const { cart } = context;
  const formData = await request.formData();

  // Fetch live docs for current cart handler methods
  const result = await cart.addLines([
    { merchandiseId: formData.get("variantId"), quantity: 1 },
  ]);
  return json(result);
}
```

### Caching Strategies

| Strategy | Behavior | Use For |
|----------|----------|---------|
| `CacheLong()` | Long TTL + long SWR | Products, collections, pages |
| `CacheShort()` | Short TTL + short SWR | Cart, dynamic content |
| `CacheNone()` | No caching | Customer-specific data |
| `CacheCustom({...})` | Custom maxAge + SWR | Fine-tuned scenarios |

Applied as second argument to `storefront.query()`.

> **Fetch live docs** for exact TTL values — `CacheLong` and `CacheShort` default durations may change across Hydrogen versions.

### Streaming SSR with defer()

```typescript
// Pattern: defer non-critical data for progressive rendering
export async function loader({ context }: LoaderFunctionArgs) {
  // Critical — awaited before render
  const collection = await context.storefront.query(COLLECTION_QUERY);

  // Non-critical — streamed after initial render
  const recommendations = context.storefront.query(RECS_QUERY);

  return defer({ collection, recommendations });
}

export default function Page() {
  const { collection, recommendations } = useLoaderData<typeof loader>();
  return (
    <div>
      <h1>{collection.title}</h1>
      <Suspense fallback={<p>Loading...</p>}>
        <Await resolve={recommendations}>
          {(data) => <RecommendedProducts data={data} />}
        </Await>
      </Suspense>
    </div>
  );
}
```

### Error Boundaries

```typescript
// Pattern: route-level error handling
import { isRouteErrorResponse, useRouteError } from "@remix-run/react";

export function ErrorBoundary() {
  const error = useRouteError();
  if (isRouteErrorResponse(error)) {
    return <div><h1>{error.status === 404 ? "Not Found" : "Error"}</h1></div>;
  }
  return <div><h1>Something went wrong</h1></div>;
}
```

## Cart

Built-in cart management:
- `createCartHandler()` — server-side cart API
- Cart stored as Shopify cart ID in cookie
- Mutations: create, add lines, update lines, remove lines, update discount codes, update buyer identity
- Use `useFetcher` for cart mutations (avoids full page navigation)

> **Fetch live docs**: Web-search `site:shopify.dev hydrogen createCartHandler` for current cart handler methods and return types.

## Customer Accounts

New Customer Account API (OAuth-based):
- `/account/login` → redirects to Shopify-hosted login (passwordless)
- `/account/authorize` → callback with tokens
- Access customer data: orders, addresses, profile

> **Fetch live docs**: Web-search `site:shopify.dev hydrogen customer accounts` for current OAuth flow, Customer Account API queries, and route setup.

## SEO

Built-in SEO utilities:
- `getSeoMeta()` — generates meta tags from Storefront API data
- Structured data (JSON-LD) for products, collections, articles
- Canonical URLs, Open Graph, Twitter cards
- Sitemap generation from Storefront API

> **Fetch live docs**: Web-search `site:shopify.dev hydrogen seo` for current `getSeoMeta` API and structured data helpers.

## Oxygen Deployment

Shopify's edge hosting:
- Automatic deployments from GitHub
- Edge workers (V8 isolates)
- Automatic SSL and global CDN
- Environment variables managed in Shopify admin
- Staging environments for preview

Alternative hosts: Vercel, Cloudflare Workers, Node.js servers (any platform that runs Remix).

## Best Practices

- Use Remix loaders for data fetching — never fetch in components
- Apply appropriate cache strategies (`CacheLong` for stable data, `CacheShort` for dynamic)
- Use streaming SSR with `defer()` for non-critical data to avoid blocking render
- Implement error boundaries at every route level
- Use `<Await>` component for deferred data rendering
- Optimize images with Shopify CDN URL transforms (`?width=`, `?crop=`)
- Use `useFetcher` for cart mutations (avoids full page navigation)
- Preload critical routes with `<Link prefetch="intent">`
- Test on Oxygen staging before production deployment

Fetch the Hydrogen docs, Remix documentation, and Hydrogen GitHub source for exact loader/action patterns, caching APIs, cart handler methods, and deployment configuration before implementing.
