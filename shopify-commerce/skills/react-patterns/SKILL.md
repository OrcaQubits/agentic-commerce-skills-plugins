---
name: react-patterns
description: Build React applications with Remix — loaders, actions, hooks, Server/Client Components, nested routes, error boundaries, form handling, and streaming SSR. Use when building Shopify Hydrogen storefronts or Remix-based apps.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# React + Remix Patterns

## Before writing code

**Fetch live docs**:
1. Fetch `https://remix.run/docs/en/main` for Remix documentation
2. Fetch `https://react.dev/reference/react` for React API reference
3. Web-search `site:shopify.dev hydrogen remix patterns` for Hydrogen-specific patterns

## Why Remix (Not Next.js)

Shopify's Hydrogen is built on Remix:
- Server-first rendering with progressive enhancement
- Loaders and actions for server-side data fetching and mutations
- Nested routes for layout composition
- Built-in form handling without client-side state management
- Streaming SSR for fast perceived performance

## Core Remix Concepts

### Loaders (Data Fetching)

Server-side function that runs on every GET request:

```typescript
import { json, type LoaderFunctionArgs } from '@remix-run/node';

export async function loader({ context, params }: LoaderFunctionArgs) {
  const { storefront } = context;
  const { products } = await storefront.query(PRODUCTS_QUERY);
  return json({ products });
}

export default function ProductsPage() {
  const { products } = useLoaderData<typeof loader>();
  return <ProductGrid products={products} />;
}
```

### Actions (Mutations)

Server-side function for form submissions (POST/PUT/DELETE):

```typescript
import { redirect, type ActionFunctionArgs } from '@remix-run/node';

export async function action({ request, context }: ActionFunctionArgs) {
  const formData = await request.formData();
  const variantId = formData.get('variantId') as string;

  const { cart } = context;
  await cart.addLines([{ merchandiseId: variantId, quantity: 1 }]);

  return redirect('/cart');
}
```

### Nested Routes

Routes compose via `<Outlet>`:

```
app/routes/
├── ($locale)._index.tsx                    # Homepage
├── ($locale).products._index.tsx           # Product listing
├── ($locale).products.$handle.tsx          # Product detail
├── ($locale).collections.$handle.tsx       # Collection page
├── ($locale).cart.tsx                       # Cart page
└── ($locale).account.tsx                   # Account layout
    ├── ($locale).account._index.tsx        # Account dashboard
    └── ($locale).account.orders.tsx        # Order history
```

### Error Boundaries

Per-route error handling:

```typescript
export function ErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <div>
        <h1>{error.status}</h1>
        <p>{error.statusText}</p>
      </div>
    );
  }

  return <div>Something went wrong</div>;
}
```

## React Hooks

### Core Hooks

| Hook | Purpose |
|------|---------|
| `useState` | Local component state |
| `useEffect` | Side effects (client only) |
| `useRef` | Mutable ref / DOM access |
| `useMemo` | Memoized computation |
| `useCallback` | Memoized callback |
| `useContext` | Context consumption |
| `useReducer` | Complex state logic |

### Remix Hooks

| Hook | Purpose |
|------|---------|
| `useLoaderData` | Access loader data |
| `useActionData` | Access action response |
| `useFetcher` | Non-navigation data fetching |
| `useNavigation` | Navigation state (loading, submitting) |
| `useRouteError` | Error boundary data |
| `useSearchParams` | URL search parameters |
| `useParams` | Route parameters |
| `useMatches` | All matched routes data |

## Server vs Client Components

### Server Components

- Run only on the server
- Can use `async/await` directly
- Access databases, APIs, secrets
- No event handlers, no `useState`, no `useEffect`
- Default in Remix loaders

### Client Components

- Run in the browser
- Use `"use client"` directive (in React 19+)
- Handle interactivity: clicks, inputs, animations
- Use `useState`, `useEffect`, `useRef`

## Form Handling

Remix enhances HTML forms:

```typescript
import { Form, useNavigation } from '@remix-run/react';

function AddToCartForm({ variantId }: { variantId: string }) {
  const navigation = useNavigation();
  const isAdding = navigation.state === 'submitting';

  return (
    <Form method="post" action="/cart">
      <input type="hidden" name="variantId" value={variantId} />
      <button type="submit" disabled={isAdding}>
        {isAdding ? 'Adding...' : 'Add to Cart'}
      </button>
    </Form>
  );
}
```

### Fetcher (Non-Navigation)

For mutations that shouldn't navigate:

```typescript
function AddToCartButton({ variantId }: { variantId: string }) {
  const fetcher = useFetcher();
  const isAdding = fetcher.state === 'submitting';

  return (
    <fetcher.Form method="post" action="/cart">
      <input type="hidden" name="variantId" value={variantId} />
      <button disabled={isAdding}>
        {isAdding ? 'Adding...' : 'Add to Cart'}
      </button>
    </fetcher.Form>
  );
}
```

## Streaming SSR

Defer non-critical data for faster initial render:

```typescript
import { defer } from '@remix-run/node';
import { Await, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';

export async function loader({ context }: LoaderFunctionArgs) {
  const criticalData = await context.storefront.query(PRODUCT_QUERY);
  const recommendedProducts = context.storefront.query(RECOMMENDATIONS_QUERY);

  return defer({
    product: criticalData.product,
    recommended: recommendedProducts, // not awaited — streams later
  });
}

export default function ProductPage() {
  const { product, recommended } = useLoaderData<typeof loader>();

  return (
    <div>
      <ProductDetail product={product} />
      <Suspense fallback={<Spinner />}>
        <Await resolve={recommended}>
          {(data) => <RecommendedProducts products={data.products} />}
        </Await>
      </Suspense>
    </div>
  );
}
```

## Component Patterns

### Composition

```typescript
function ProductCard({ product, children }: { product: Product; children?: ReactNode }) {
  return (
    <article>
      <ProductImage image={product.featuredImage} />
      <ProductTitle title={product.title} />
      <ProductPrice price={product.priceRange} />
      {children}
    </article>
  );
}
```

### Custom Hooks

```typescript
function useCart() {
  const fetcher = useFetcher();
  const addToCart = (variantId: string) => {
    fetcher.submit({ variantId }, { method: 'post', action: '/cart' });
  };
  return { addToCart, isAdding: fetcher.state === 'submitting' };
}
```

## Best Practices

- Use loaders for data fetching — never fetch in components with `useEffect`
- Use actions for mutations — use Remix `<Form>` over manual `fetch`
- Use `useFetcher` for mutations that should not cause navigation
- Use `defer()` + `<Suspense>` for non-critical data (recommendations, reviews)
- Implement error boundaries at route level for graceful degradation
- Keep components small and focused — extract custom hooks for reusable logic
- Prefer server rendering — only use client-side state when interactivity requires it
- Avoid `useEffect` for data fetching — Remix loaders handle this
- Use TypeScript for type safety across loader → component data flow

Fetch the Remix and React documentation for exact API signatures, hook behavior, and streaming patterns before implementing.
