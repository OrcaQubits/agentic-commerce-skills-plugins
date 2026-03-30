---
name: react-patterns
description: >
  Build React applications for PWA Kit — hooks, composition, SSR, Commerce SDK
  integration, Chakra UI components, getProps data fetching, and client-side
  state management. PWA Kit uses React (NOT Remix/Next.js). Use when building
  PWA Kit storefronts.
---

# PWA Kit React Patterns

## Before Writing Code

Always fetch the latest official documentation BEFORE building React components:

1. Web-search: "Salesforce PWA Kit React patterns 2026"
2. Web-search: "Salesforce Commerce SDK React hooks 2026"
3. Web-search: "Salesforce Retail React App reference architecture 2026"
4. Web-fetch: `https://developer.salesforce.com/docs/commerce/pwa-kit-managed-runtime/guide/getting-started.html`
5. Web-fetch: `https://developer.salesforce.com/docs/commerce/commerce-sdk-react/guide/getting-started.html`
6. Web-fetch: `https://github.com/SalesforceCommerceCloud/pwa-kit`

Verify PWA Kit version, available hooks, getProps API, and routing patterns against current documentation before writing any component code.

## Conceptual Architecture

### CRITICAL: PWA Kit is NOT Remix/Next.js

> **WARNING**: PWA Kit is a **custom React framework** built by Salesforce. It has its own SSR implementation, routing, and data fetching patterns. Do NOT use Next.js or Remix patterns -- they will not work.

| Pattern | PWA Kit | Next.js (DO NOT USE) | Remix (DO NOT USE) |
|---|---|---|---|
| Server data fetching | `getProps()` static method | `getServerSideProps` | `loader()` |
| Client routing | React Router (`react-router-dom`) | File-based routing | File-based routing |
| Deployment | Managed Runtime | Vercel / self-hosted | Vercel / self-hosted |
| Styling | Chakra UI (default) | Any | Any |
| Commerce SDK | Built-in hooks + typed clients | N/A | N/A |
| SSR server | `@salesforce/pwa-kit-runtime` | Built-in | Built-in |
| Data mutations | Commerce SDK mutation hooks | Server Actions | `action()` |
| Error boundaries | React error boundaries | `error.tsx` | `ErrorBoundary` export |

### PWA Kit-Specific APIs

| API / Pattern | Purpose | Where It Runs |
|---|---|---|
| `Component.getProps()` | Server-side data fetching (static method on page components) | Server (SSR) |
| `useServerContext()` | Access `req`, `res` during SSR | Server only |
| `getConfig()` | Read runtime configuration (`config/default.js`) | Server + Client |
| `RouteComponent` | Page-level component registered in route config | Both |
| Commerce SDK React hooks | Client-side SCAPI data fetching (useProduct, useBasket, etc.) | Client |
| `withReactQuery` (v3+) | React Query integration for data caching | Both |

### SSR and Hydration

PWA Kit renders React components on the server to produce initial HTML, which is sent to the browser. React then **hydrates** the HTML on the client -- attaching event listeners and initializing state so the app becomes fully interactive.

Key SSR constraints:

- `window`, `document`, `navigator`, and other browser APIs are **undefined** during SSR
- Use `useEffect` for any code that requires browser APIs (it only runs on the client)
- Ensure server-rendered HTML matches client-rendered HTML to avoid hydration mismatches
- PWA Kit supports streaming SSR with React 18+ for faster time-to-first-byte

### Component Architecture

| Layer | Role | Data Fetching | Example |
|---|---|---|---|
| Page component | Route-level, registered in `app/routes.jsx` | `getProps()` for SSR data | `ProductDetailPage` |
| Container component | Orchestrates data flow, connects to Commerce SDK | Commerce SDK hooks | `ProductListContainer` |
| Presentational component | Pure UI rendering, receives props | None (props only) | `ProductTile`, `PriceDisplay` |
| Layout component | Persistent shell (header, footer) | Minimal or none | `AppConfig` |

### PWA Kit Project Structure

| Path | Purpose |
|---|---|
| `app/pages/` | Page components (route-level) |
| `app/components/` | Shared/reusable components |
| `app/components/_app-config/` | Application shell (layout wrapper) |
| `app/routes.jsx` | Route definitions mapping URLs to page components |
| `app/ssr.js` | SSR server entry point |
| `config/default.js` | Default runtime configuration (Commerce API, sites) |
| `config/[env].js` | Environment-specific overrides |

### Commerce SDK React Hooks

The `@salesforce/commerce-sdk-react` package provides hooks that wrap SCAPI calls with React Query for caching, loading states, and error handling.

| Hook Category | Examples | Purpose |
|---|---|---|
| Product hooks | `useProduct`, `useProducts`, `useSearchProducts` | Fetch product data |
| Basket hooks | `useBasket`, `useShopperBasketsMutation` | Cart operations |
| Customer hooks | `useCustomer`, `useShopperLoginMutation` | Auth and profile |
| Category hooks | `useCategories`, `useCategory` | Navigation and browse |
| Promotion hooks | `usePromotions` | Active promotions |

All hooks return `{ data, isLoading, error, isError }` and support React Query options (staleTime, cacheTime, refetchOnWindowFocus, enabled). Mutation hooks return `{ mutate, mutateAsync, isLoading, error }`.

### Client-Side Routing

PWA Kit uses `react-router-dom`. Routes are defined in `app/routes.jsx` and map URL patterns to page components.

| Router API | Purpose |
|---|---|
| `<Link to="...">` | Declarative navigation (client-side) |
| `useNavigate()` | Programmatic navigation |
| `useParams()` | Access URL parameters |
| `useLocation()` | Current URL, search params |
| `useSearchParams()` | Read/write URL query parameters |

### State Management

| State Type | Tool | Scope | Examples |
|---|---|---|---|
| Server/remote state | Commerce SDK hooks (React Query) | Cached, shared | Products, basket, customer |
| Global client state | React Context | App-wide | User session, locale, currency |
| Local component state | `useState` / `useReducer` | Single component | Form inputs, UI toggles, selections |
| URL state | `useSearchParams` | Shareable | Filters, pagination, sort order |

Avoid duplicating server state in client state -- let Commerce SDK hooks be the source of truth for remote data.

### Performance Optimization Concepts

| Technique | React API | When to Use |
|---|---|---|
| Memoize expensive computations | `useMemo` | Filtering, sorting large lists |
| Stable callback references | `useCallback` | Functions passed as props to child components |
| Component memoization | `React.memo` | Prevent re-render when props unchanged |
| Code splitting | `React.lazy` + `Suspense` | Large components not needed on initial render |
| Deferred updates | `useDeferredValue` (React 18+) | Non-urgent UI updates |

## Code Examples

**Pattern: Page component with getProps**

```javascript
const ProductDetailPage = ({ product }) => {
    return <div>{product.name}</div>;
};
ProductDetailPage.getProps = async ({ params, api }) => {
    // Fetch live docs for Commerce SDK shopperProducts API
    return { product };
};
export default ProductDetailPage;
```

**Pattern: Commerce SDK hook usage**

```javascript
const { data, isLoading, error } = useProduct({
    parameters: { id: productId }
});
// Fetch live docs for @salesforce/commerce-sdk-react hooks
```

**Pattern: App shell layout**

```javascript
const AppConfig = ({ children }) => (
    <Box>
        <Header />
        <Box as="main">{children}</Box>
        <Footer />
    </Box>
);
```

**Pattern: SSR-safe browser API access**

```javascript
useEffect(() => {
    // This only runs on the client, never during SSR
    // Fetch live docs for useEffect SSR behavior
}, []);
```

## Best Practices

### Data Fetching
- Use `getProps()` for SEO-critical, initial page load data (runs on server)
- Use Commerce SDK React hooks for interactive, client-side data updates
- Use `Promise.all()` inside `getProps()` for parallel data fetching
- Never duplicate server-fetched data into local state

### Component Design
- Keep components small and single-purpose (page, container, presentational)
- Use composition and `children` props over deep prop drilling
- Use React Context only for truly global state (user, basket, locale)
- Memoize expensive computations with `useMemo` and stable callbacks with `useCallback`

### SSR Safety
- Never access `window`, `document`, or browser APIs during render -- use `useEffect`
- Test components in SSR mode to catch hydration mismatches early
- Return `null` or fallback UI for client-only features during SSR
- Ensure conditional rendering is deterministic between server and client

### Styling and UI
- Use Chakra UI components as the default component library in PWA Kit
- Leverage Chakra theme tokens for consistent spacing, colors, and typography
- Use responsive array syntax for breakpoint-based styling (e.g., `w={['100%', '50%', '33%']}`)
- Override theme at the project level in `app/theme/` rather than inline styles

---

Fetch the latest PWA Kit developer guide, Commerce SDK React documentation, and Retail React App source for exact hook signatures, route configuration, and getProps API before implementing.
