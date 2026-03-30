---
name: nextjs-react
description: >
  Build Next.js and React applications for Saleor — App Router, server and
  client components, GraphQL client integration, MacawUI in Apps, and Tailwind
  CSS. Use when building Saleor storefronts or Apps with Next.js.
---

# Next.js & React for Saleor

## Before writing code

**Fetch live docs**:
1. Web-search `site:nextjs.org docs app` for current Next.js App Router documentation
2. Web-search `site:docs.saleor.io storefront` for Saleor storefront development guide
3. Web-search `site:github.com saleor storefront` for the official Saleor storefront template source
4. Web-search `site:github.com saleor macaw-ui` for MacawUI component library reference
5. Web-search `saleor app template Next.js saleor-app-sdk` for App development patterns
6. Fetch `https://docs.saleor.io/docs/developer/app-store/apps/overview` for App architecture

## Next.js App Router Conventions

### File Conventions

| File | Purpose | Rendering |
|------|---------|-----------|
| `layout.tsx` | Shared layout wrapping child routes | Server component (default) |
| `page.tsx` | Unique UI for a route segment | Server component (default) |
| `loading.tsx` | Loading UI (React Suspense) | Server component |
| `error.tsx` | Error boundary for route segment | Client component (required) |
| `not-found.tsx` | 404 UI for route segment | Server component |
| `template.tsx` | Re-rendered layout (no state persistence) | Server component |
| `route.ts` | API route handler | Server-only |

### Routing Patterns for Saleor Storefronts

| Route | Segment | Purpose |
|-------|---------|---------|
| `/[channel]` | Dynamic channel | Multi-channel routing |
| `/[channel]/products` | Product listing | Category/collection pages |
| `/[channel]/products/[slug]` | Product detail | Single product page |
| `/[channel]/cart` | Cart | Shopping cart |
| `/[channel]/checkout` | Checkout | Checkout flow |
| `/[channel]/account` | Account | Customer dashboard |
| `/[channel]/search` | Search | Product search results |

- Use dynamic segments `[channel]` for multi-channel support
- Use route groups `(storefront)` and `(dashboard)` to organize layouts

## Server vs Client Components

### Decision Matrix

| Criterion | Server Component | Client Component |
|-----------|-----------------|-----------------|
| **Data fetching** | Fetch directly (no waterfall) | Use `useQuery` hooks |
| **SEO critical** | Yes (HTML in response) | No (client-rendered) |
| **Interactivity** | None (static output) | Click, input, state |
| **Hooks** | Cannot use hooks | `useState`, `useEffect`, etc. |
| **Bundle size** | Zero JS sent to client | Included in JS bundle |

### Component Patterns for Saleor

| Component | Type | Reason |
|-----------|------|--------|
| **Product list page** | Server | SEO, data fetching |
| **Product detail page** | Server | SEO, data fetching |
| **Add to cart button** | Client | Interactivity, state |
| **Cart sidebar** | Client | State management, animation |
| **Checkout form** | Client | Form state, validation |
| **Search bar** | Client | Input handling, debounce |
| **Navigation** | Server | Static, SEO links |
| **Price display** | Server | Channel-aware, static |

- Default to server components — add `"use client"` only when needed; pass server-fetched data as props to client components

## GraphQL Client Integration

### urql (Saleor Recommended)

| Package | Purpose |
|---------|---------|
| `@urql/core` | Core urql client |
| `@urql/next` | Next.js App Router integration |
| `graphql` | GraphQL parsing (peer dependency) |

### Setup Pattern

| Concern | Implementation |
|---------|---------------|
| **Server client** | Create urql client in server utility, use in server components |
| **Client provider** | Wrap client components with `UrqlProvider` in layout |
| **Auth header** | Add `Authorization: Bearer <token>` via `fetchOptions` |
| **Channel header** | Add `saleor-channel: <slug>` via `fetchOptions` |
| **SSR** | Use `@urql/next` for SSR data hydration |

### Apollo Client Alternative

- Use `@apollo/client` with `@apollo/experimental-nextjs-app-support`
- Provides normalized caching (useful for complex state)
- Heavier bundle than urql

## Data Fetching Patterns

| Pattern | Where | How |
|---------|-------|-----|
| **Server component fetch** | `page.tsx`, `layout.tsx` | `await client.query()` directly |
| **Client query hook** | `"use client"` components | `useQuery(Document, { variables })` |
| **Server action** | Form submissions | `"use server"` functions calling GraphQL |
| **Route handler** | `route.ts` | API endpoint calling Saleor GraphQL |
| **Parallel fetching** | Server component | `Promise.all([query1, query2])` |

- Fetch data as high in the component tree as possible
- Use `Promise.all` for parallel independent queries
- Use server actions for mutations (checkout updates, cart modifications)

## Caching Strategies

| Strategy | Scope | Configuration |
|----------|-------|---------------|
| **Static** | Build time | `export const revalidate = false` |
| **ISR** | Time-based revalidation | `export const revalidate = 60` (seconds) |
| **On-demand** | Webhook-triggered | `revalidatePath()` or `revalidateTag()` |
| **No cache** | Always fresh | `export const dynamic = "force-dynamic"` |

### Saleor Caching Recommendations

| Page | Strategy | Rationale |
|------|----------|-----------|
| **Product listing** | ISR (60s) | Content changes infrequently |
| **Product detail** | ISR (60s) + on-demand | Revalidate on product webhook |
| **Cart / Checkout** | No cache | User-specific, transactional |
| **Static pages** | Static | CMS content, rarely changes |

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_SALEOR_API_URL` | Client + Server | Saleor GraphQL endpoint |
| `SALEOR_API_URL` | Server only | Server-side GraphQL endpoint |
| `NEXT_PUBLIC_DEFAULT_CHANNEL` | Client + Server | Default channel slug |
| `SALEOR_APP_TOKEN` | Server only | App token for authenticated queries |

- Prefix with `NEXT_PUBLIC_` for client-accessible variables
- Keep secrets (App tokens, API keys) server-only (no prefix)

## Tailwind CSS Setup

| Step | Action |
|------|--------|
| **Install** | `npm install -D tailwindcss @tailwindcss/postcss postcss` |
| **Configure** | Add `@tailwindcss/postcss` to `postcss.config.js` |
| **Content paths** | Set `content` in `tailwind.config.ts` to include all component files |
| **Global import** | Add `@import "tailwindcss"` to `globals.css` |

- The official Saleor storefront template uses Tailwind CSS
- Use CSS custom properties for theme tokens (channel-specific branding)

## MacawUI Integration for Apps

MacawUI is the Saleor Dashboard component library used in Saleor Apps:

| Component Category | Examples |
|-------------------|----------|
| **Layout** | `Box`, `Layout`, `Sidebar` |
| **Forms** | `Input`, `Select`, `Checkbox`, `Multiselect` |
| **Data display** | `List`, `Table`, `Chip`, `Tag` |
| **Feedback** | `Alert`, `Banner`, `Skeleton` |
| **Actions** | `Button`, `IconButton`, `Dropdown` |

| Context | UI Library | Reason |
|---------|-----------|--------|
| **Saleor App (Dashboard iframe)** | MacawUI | Consistent Dashboard look and feel |
| **Storefront** | Tailwind CSS / custom | Brand-specific design |

- Install via `npm install @saleor/macaw-ui`
- Wrap App root with `<ThemeProvider>` from MacawUI
- MacawUI follows the Saleor design system (spacing, colors, typography)

## Image Optimization

| Feature | Configuration |
|---------|---------------|
| **next/image** | Use for all product and media images |
| **Remote patterns** | Add Saleor media domain to `next.config.js` `images.remotePatterns` |
| **Sizes** | Set `sizes` attribute for responsive images |
| **Priority** | Add `priority` to above-the-fold images (hero, first product) |
| **Formats** | Next.js auto-serves WebP/AVIF when supported |

## Best Practices

- Default to server components and add `"use client"` only for interactivity
- Fetch data in server components and pass as props to client components
- Use the App Router file conventions (`page.tsx`, `layout.tsx`, `error.tsx`) consistently
- Set up GraphQL code generation for type-safe queries and mutations
- Use ISR with on-demand revalidation for product pages (webhook-triggered)
- Include `saleor-channel` header in all GraphQL client configurations
- Use MacawUI for Dashboard App UI and Tailwind CSS for storefronts
- Optimize images with `next/image` and configure remote patterns for Saleor media
- Keep environment variables separated between server-only and client-accessible

Fetch the Next.js and Saleor storefront documentation for current App Router patterns, GraphQL client setup, and component conventions before implementing.
