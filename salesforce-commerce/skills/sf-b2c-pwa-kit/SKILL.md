---
name: sf-b2c-pwa-kit
description: Build headless B2C storefronts with PWA Kit — React-based framework (NOT Remix/Next.js), Managed Runtime deployment, Commerce SDK integration, server-side rendering, Chakra UI components, and extensible application shell. Use when building headless Salesforce Commerce storefronts.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# PWA Kit (Headless B2C Storefronts)

## Before Writing Code

**Fetch live docs:**
1. Fetch `https://developer.salesforce.com/docs/commerce/pwa-kit-managed-runtime/overview` for PWA Kit documentation
2. Web-search `site:github.com SalesforceCommerceCloud pwa-kit` for source, examples, and starter templates
3. Web-search `site:developer.salesforce.com pwa-kit commerce-sdk` for Commerce SDK integration
4. Web-search `site:developer.salesforce.com pwa-kit managed-runtime deployment` for deployment docs

**Why:** PWA Kit versions, Commerce SDK hooks, and Managed Runtime deployment procedures change across releases. Always verify the version in use (v2 vs v3+) before generating code.

## Conceptual Architecture

### What Is PWA Kit

PWA Kit is Salesforce's React-based framework for headless B2C Commerce:

| Aspect | Detail |
|--------|--------|
| Framework | React with custom SSR (NOT Remix, NOT Next.js) |
| Hosting | Managed Runtime (Salesforce CDN/edge) or self-hosted Node.js |
| API Layer | Commerce SDK -- typed access to SCAPI (Shopper APIs) |
| Authentication | SLAS (Shopper Login and API Access Service) |
| UI Library | Chakra UI (accessible, themeable components) |
| Extensibility | Override templates/components without forking |

### Project Structure

```
pwa-kit-storefront/
├── app/
│   ├── pages/          # Route-based page components
│   ├── components/     # Shared React components
│   ├── hooks/          # Commerce SDK React hooks
│   └── routes.jsx      # Centralized route definitions
├── config/default.js   # Site config (API credentials, locales)
└── ssr.js              # SSR server entry point
```

### Core Concepts

| Concept | Description |
|---------|-------------|
| Data Fetching (v2) | `getProps` static method on page components -- runs server-side on initial load |
| Data Fetching (v3+) | `withReactQuery` and React Query hooks replace `getProps` |
| Routing | Centralized in `app/routes.jsx` (NOT file-based like Next.js); React Router syntax |
| SSR | Custom server-side rendering via `ssr.js`; hydration on client |
| Commerce SDK Hooks | `useProduct`, `useCategories`, `useBasket`, `useCustomer`, `useSearchParams` |
| Chakra UI | Box, Flex, Grid, Stack for layout; responsive array syntax `fontSize={['sm', 'md']}` |
| SLAS Auth | Guest tokens (automatic), registered login (OAuth), token refresh (transparent via SDK) |

### Key Platform Warnings

- **NOT file-based routing**: routes must be explicitly defined in `routes.jsx`.
- **NOT Remix or Next.js**: do not use Remix loaders/actions or Next.js `getServerSideProps`.
- **Version matters**: v2 uses `getProps`; v3+ uses React Query. Check `package.json` before coding.
- **Managed Runtime constraints**: environment variables are set in Runtime Admin, not `.env` in production.
- **No direct SCAPI calls**: always use Commerce SDK; it handles auth, proxying, and token management.

### Commerce SDK Configuration

The Commerce SDK is configured in `config/default.js` with Commerce API credentials (clientId, organizationId, shortCode, siteId). These values come from environment variables in production. The SDK handles SLAS authentication, token refresh, and SCAPI proxy routing transparently.

### Commerce SDK Hook Patterns

| Hook | Purpose | Returns |
|------|---------|---------|
| `useProduct(id)` | Fetch product by ID | Product object with variants, images, prices |
| `useCategories(id)` | Fetch category tree | Category with subcategories |
| `useBasket()` | Cart management | Basket object with line items, totals |
| `useCustomer()` | Customer profile | Customer data, authentication state |
| `useSearchParams()` | Search and filtering | Search results with facets, pagination |

Fetch live docs for current hook signatures -- return types and parameters evolve across SDK versions.

### Routing

Routes are defined explicitly in `app/routes.jsx` using React Router syntax. Page components in `app/pages/` are NOT auto-discovered. Each route maps a URL pattern to a component with optional data fetching.

```jsx
// Pattern: route definition skeleton
// Fetch live docs for current route config API
const routes = [
  { path: '/', component: Home, exact: true },
  { path: '/product/:productId', component: ProductDetail },
]
```

### Server-Side Rendering

| Phase | Description |
|-------|-------------|
| Server render | `ssr.js` processes the request; `getProps` (v2) or React Query (v3+) fetches data |
| HTML delivery | Fully rendered HTML sent to browser with embedded state |
| Client hydration | React hydrates the server-rendered HTML and attaches event handlers |
| Client navigation | Subsequent navigation is client-side via React Router |

### Deployment Overview

| Target | Method |
|--------|--------|
| Managed Runtime | `npm run push -- -m "message"` via CLI; global CDN, auto-SSL, environment management |
| Self-hosted | Any Node.js host (AWS, Heroku, Vercel); manual SCAPI proxy configuration needed |

Managed Runtime environments: development, staging, production. Each environment has independent configuration in Runtime Admin.

### Extensibility Framework

Override templates and components without forking the base:
- **Template overrides**: replace specific pages or components via configuration.
- **Component overrides**: wrap or replace standard components.
- **Hook overrides**: customize data fetching logic.
- **Theme overrides**: extend Chakra UI theme with custom tokens and component styles.

### Chakra UI Theming

Chakra UI is the default component library. Customize via `extendTheme()`:
- **Colors, fonts, spacing**: override design tokens globally.
- **Component styles**: customize default props and variants per component.
- **Responsive**: array syntax `fontSize={['sm', 'md', 'lg']}` maps to breakpoints.
- **Accessibility**: built-in ARIA attributes, keyboard navigation, focus management.

### Scaffold Pattern

```bash
# Pattern: create new PWA Kit project
# Fetch live docs for current CLI options
npx @salesforce/pwa-kit-create-app
```

```jsx
// Pattern: page component skeleton
// Fetch live docs for current data fetching API
const MyPage = ({ data }) => <Box>{data.name}</Box>
export default MyPage
```

## Best Practices

### Development
- Use Commerce SDK hooks for client-side interactions (add to cart, search).
- Leverage Chakra UI for consistent, accessible design.
- Use the extensibility framework to customize -- do not fork the base template.
- Keep `config/default.js` environment-aware; never hardcode API credentials.

### Performance
- Use server-side data fetching (`getProps` or React Query) -- never `useEffect` for initial data.
- Optimize images with responsive sizing and lazy loading.
- Configure proper caching headers for CDN delivery.
- Minimize bundle size by code-splitting pages and lazy-loading non-critical components.

### Deployment
- Deploy to Managed Runtime for optimal SCAPI integration and CDN performance.
- Test SSR rendering and client-side hydration before pushing.
- Manage environment variables in Runtime Admin, not in code.
- Use separate environments (dev, staging, prod) with independent configurations.

---

Fetch the PWA Kit docs, Commerce SDK reference, and Managed Runtime deployment guide for exact component APIs, SDK method signatures, and configuration options before implementing.
