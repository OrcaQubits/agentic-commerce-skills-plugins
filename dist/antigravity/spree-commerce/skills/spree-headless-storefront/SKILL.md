---
name: spree-headless-storefront
description: >
  Build with Spree's headless Next.js storefront — the official
  `spree/storefront` repo (Next.js 16 App Router with Server Actions and
  Turbopack, React 19 Server Components, Tailwind CSS 4, TypeScript 5,
  `@spree/sdk`, Sentry), server-only auth (httpOnly JWT cookies + publishable
  key), MeiliSearch faceted catalog, one-page checkout with Apple/Google
  Pay/Klarna/Affirm/SEPA, multi-region market routing, GA4 + JSON-LD SEO, and
  Vercel/Docker deployment. Use when forking or customizing the storefront, or
  evaluating headless adoption.
---

# Spree Headless Next.js Storefront

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/spree/storefront (README) for current setup and customization.
2. Fetch https://spreecommerce.org/docs/developer/storefront/nextjs/quickstart for the quickstart.
3. Fetch the Next.js 16 docs for App Router / Server Actions patterns the storefront uses.
4. Cross-reference https://spreecommerce.org/docs/developer/sdk/quickstart for SDK usage.
5. Check the v5.4 announcement for the storefront's release context.

## Conceptual Architecture

### The Two Repos

| Repo | Role |
|------|------|
| `spree/spree-starter` | Rails backend application |
| `spree/storefront` | Next.js headless storefront |

The storefront talks to the backend exclusively over API v3 (Store API).

### Tech Stack

| Layer | Tech |
|-------|------|
| Framework | Next.js 16 (App Router, Server Actions, Turbopack) |
| UI runtime | React 19 (Server Components + Client Components) |
| Styling | Tailwind CSS 4 |
| Type system | TypeScript 5 |
| API client | `@spree/sdk` with Zod schemas |
| Search | MeiliSearch faceted search |
| Auth | Server-only — httpOnly JWT cookies + publishable key |
| Payments | Stripe Elements / Apple Pay / Google Pay / Link / Klarna / Affirm / SEPA |
| Analytics | GA4, JSON-LD, OpenGraph |
| Error tracking | Sentry |
| Deploy | Vercel (recommended) or Docker |

### Prerequisites

- Node 20+
- Spree backend on **5.4+** (API v3 required)
- A publishable key (`pk_…`) from admin

### Project Layout

```
storefront/
├── app/
│   ├── (storefront)/      # public pages (App Router groups)
│   │   ├── [region]/[locale]/
│   │   │   ├── products/
│   │   │   ├── cart/
│   │   │   └── checkout/
│   │   └── account/
│   ├── api/                # Route Handlers for webhooks etc.
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                 # Tailwind-styled primitives
│   ├── product/
│   ├── cart/
│   └── checkout/
├── lib/
│   ├── spree.server.ts     # admin/auth client — never imported client-side
│   ├── spree.public.ts     # publishable-key client
│   ├── auth.ts             # Server Action helpers for sign in/out
│   └── meilisearch.ts
├── public/
├── tailwind.config.ts
├── next.config.ts
└── package.json
```

### Auth: Server-Only by Design

- The **publishable key** (`pk_…`) is the only Spree credential that may reach the browser.
- **User JWTs** live in **httpOnly cookies** set via Server Actions; never accessible to client JS.
- The **admin API key** never leaves the server bundle. The storefront should never have it set in env.
- Cart `order_token` also in httpOnly cookie.

```typescript
// app/api/auth/sign-in/route.ts (Route Handler)
import { cookies } from 'next/headers';
import { spreePublic } from '@/lib/spree.public';

export async function POST(req: Request) {
  const { email, password } = await req.json();
  const { access_token, refresh_token, expires_in } = await spreePublic.auth.signIn({ email, password });
  cookies().set('spree_jwt', access_token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: expires_in,
  });
  cookies().set('spree_refresh', refresh_token, { httpOnly: true, secure: true, sameSite: 'lax' });
  return Response.json({ ok: true });
}
```

### Market / Region Routing

URLs follow `/[region]/[locale]/...`:
- `/us/en/products/classic-tee`
- `/de/de/produkte/classic-tee`

The storefront resolves `current_market` from the URL, then passes it to the API so backend filters by market-allowed payment methods, shipping methods, prices.

### Faceted Catalog via MeiliSearch

The storefront's PLP (Product Listing Page) issues a MeiliSearch query (or hits a Spree API v3 endpoint that proxies to MeiliSearch — verify the live pattern). Facets: brand, color, size, price range, taxon. Typo-tolerant.

### Checkout Flow

1. **Cart page** — line items, totals, suggested upsells
2. **Address page** — bill/ship; pre-filled for logged-in users
3. **Delivery page** — pick shipping method (one per shipment)
4. **Payment page** — pick payment method, render gateway UI
   - Stripe → Stripe Elements / Apple Pay / Google Pay / Link
   - Klarna, Affirm, SEPA — Stripe-backed
5. **Review page** — final totals, place order
6. **Confirmation** — redirect to order page with `ord_…`

Implemented as one-page with progressive disclosure in the official storefront.

### Server Actions for Mutating Calls

```typescript
// app/(storefront)/cart/actions.ts
'use server';

import { cookies } from 'next/headers';
import { revalidatePath } from 'next/cache';
import { spreePublic } from '@/lib/spree.public';

export async function addToCart(variantId: string, quantity = 1) {
  const orderToken = cookies().get('spree_cart_token')?.value;
  const result = await spreePublic.cart.addItem({ variantId, quantity, orderToken });
  if (!orderToken) {
    cookies().set('spree_cart_token', result.token, { httpOnly: true, secure: true, sameSite: 'lax' });
  }
  revalidatePath('/cart');
  return result;
}
```

### SEO

- **JSON-LD** for Product, BreadcrumbList, Offer, Organization
- **OpenGraph** + Twitter Cards
- **Sitemap** generated by `next-sitemap` or similar
- **robots.txt**
- Translated meta tags per locale
- Canonical URLs respecting the region/locale prefix

### Analytics

- **GA4** loaded server-side via `next/script`
- **E-commerce events**: `view_item`, `add_to_cart`, `begin_checkout`, `purchase` — fired client-side after Server Action completion
- **JSON-LD** + Schema.org for structured data

## Implementation Guidance

### Cloning and Running

```bash
git clone https://github.com/spree/storefront my-storefront
cd my-storefront
cp .env.example .env.local
# Set:
#   SPREE_API_URL=http://localhost:4000   (your Spree backend)
#   NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY=pk_test_...
#   MEILISEARCH_HOST=http://localhost:7700
#   MEILISEARCH_PUBLIC_KEY=...
npm install
npm run dev  # http://localhost:3000
```

### Customizing Pages

The App Router structure makes customization file-system-based — add or replace files under `app/`. For shared layout changes, edit the relevant `layout.tsx`.

### Customizing Components

Override Tailwind tokens in `tailwind.config.ts`:

```typescript
export default {
  theme: {
    extend: {
      colors: {
        brand: { 500: '#0066ff', 600: '#0052cc' }
      },
      fontFamily: {
        display: ['"Inter Display"', 'sans-serif']
      }
    }
  }
}
```

For Tailwind 4 specifically, prefer the `@theme` directive in CSS:

```css
@import 'tailwindcss';

@theme {
  --color-brand-500: oklch(0.6 0.2 250);
  --font-display: 'Inter Display', sans-serif;
}
```

### Adding a New Page

```typescript
// app/(storefront)/[region]/[locale]/about/page.tsx
export default async function AboutPage({ params }: { params: Promise<{ region: string; locale: string }> }) {
  const { locale } = await params;
  return <main>About {locale}</main>;
}
```

Next.js 16 wraps `params` in a Promise — `await` it.

### Hooking Custom Backend Data

If you've added a Metafield or extension field on the backend:

```typescript
const product = await spreePublic.products.find('prod_...', { expand: ['metafields'] });
const launchDate = product.metafields?.my_app?.launch_date;
```

Augment SDK types via `types/spree.d.ts` if you want type safety.

### Caching Strategy

| Page | Strategy |
|------|----------|
| Homepage | ISR — `revalidate: 60` |
| Product detail | ISR — `revalidate: 300` (5 min) |
| Cart | Dynamic — `dynamic = 'force-dynamic'` |
| Account | Dynamic |
| Order confirmation | Dynamic |

### Deployment

**Vercel (recommended)**:
- Hook the GitHub repo
- Set env vars (`SPREE_API_URL`, `NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY`, MeiliSearch creds, Sentry DSN)
- Build command: `npm run build`
- Output: standalone

**Docker**:
- The repo ships a `Dockerfile`
- Multi-stage build to reduce image size
- Deploy to any container runtime

### Common Pitfalls

- **Importing `spree.server.ts` from a Client Component** — Next.js's `'use server'` enforcement is essential; opt into it.
- **Storing tokens in localStorage** — XSS-vulnerable; use httpOnly cookies via Server Actions.
- **Hardcoding region/locale** — breaks multi-market deployments.
- **Forgetting `revalidatePath` after Server Actions** — stale UI.
- **MeiliSearch index drift** — backend reindexes async; staging vs prod can disagree.
- **Hardcoding payment-method visibility in UI** — let the backend's Market config drive it.
- **Bundling Sentry on the client with the server DSN** — leaks credentials. Use the public DSN.
- **Pinning Next.js too aggressively** — the storefront repo bumps Next.js minor versions; match the storefront's pin.

Always re-fetch the storefront repo's README before customizing — the codebase iterates rapidly with each Spree release.
