---
name: spree-typescript-sdk
description: >
  Build storefronts and integrations using `@spree/sdk` — the official
  TypeScript SDK for Spree's API v3 (v5.4+). Covers installation, the
  resource-builder pattern (`spree.products.list`, `spree.checkout.create`,
  etc.), Zod schema validation, server-only auth (httpOnly JWTs, never exposing
  API keys), error handling, typing customizations, and pinning SDK versions to
  backend Spree releases. Use when integrating Spree into a Next.js / Node.js /
  TypeScript project.
---

# Spree TypeScript SDK (`@spree/sdk`)

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/sdk/quickstart for the SDK's current API surface.
2. Inspect the SDK's source / README on GitHub (likely under https://spreecommerce.org/docs/developer/sdk/quickstart or as part of the `storefront` repo) for resource names and parameter shapes.
3. Check the npm registry page for `@spree/sdk` for the current version aligned to your Spree backend release.
4. Read the v5.4 announcement (https://spreecommerce.org/announcing-spree-commerce-5-4/) for the SDK's release context.
5. For the Next.js usage pattern, fetch https://spreecommerce.org/docs/developer/storefront/nextjs/quickstart.

## Conceptual Architecture

### Why an SDK?

Hand-writing API v3 clients works, but `@spree/sdk` gives you:
- **TypeScript types** generated against the same OpenAPI spec the backend ships
- **Zod validation** of responses so runtime drift is caught
- **Resource-builder pattern** (`spree.products.list(...)`) that mirrors the API
- **Auth handling** — token storage, refresh, cookies
- **Idempotency-key** plumbing for safe retries
- **Error mapping** from HTTP responses to typed exceptions

### Installation

```bash
npm install @spree/sdk
# or
pnpm add @spree/sdk
```

Pin to the version matching your backend Spree release:

```json
{ "dependencies": { "@spree/sdk": "5.4.x" } }
```

When upgrading Spree, bump both together.

### Client Initialization

```typescript
import { createSpreeClient } from '@spree/sdk';

const spree = createSpreeClient({
  apiUrl: process.env.SPREE_API_URL!,                         // https://your-spree.com
  publishableKey: process.env.NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY!, // pk_live_…
  // For admin calls (server-side only):
  // adminApiKey: process.env.SPREE_ADMIN_API_KEY,
});
```

(Verify the actual factory name and option shape against the live `@spree/sdk` docs.)

### Resource Builder Pattern

The SDK exposes resources mirroring the API:

```typescript
// Read
const products = await spree.products.list({ limit: 20, expand: ['default_variant', 'images'] });
const product  = await spree.products.find('prod_…', { expand: ['variants'] });
const taxons   = await spree.taxons.list();

// Cart
const cart = await spree.cart.create();
const cart2 = await spree.cart.addItem({ variantId: 'var_…', quantity: 1 });

// Checkout
await spree.checkout.update({ email: 'guest@example.com', shippingAddress: { ... } });
const session = await spree.checkout.createPaymentSession({ paymentMethodId: 'pm_…' });
const order = await spree.checkout.complete();

// Customer
await spree.auth.signIn({ email, password });
const me = await spree.account.find();

// Admin (server-side only)
await spree.admin.orders.update('ord_…', { internalNote: '...' });
```

Method names are illustrative — verify against live SDK docs.

### Zod Schemas

Responses are parsed through Zod schemas:

```typescript
import { ProductSchema } from '@spree/sdk/schemas';

const product = await spree.products.find('prod_…');
// product is fully typed and validated; runtime mismatches throw
```

This catches API shape drift (e.g., your backend is on 5.4.1 but the SDK expects 5.4.3 conventions).

### Server-Only Auth Pattern

**Never expose the admin API key to the browser.** In Next.js:

```typescript
// app/api/account/route.ts (Server Action / Route Handler)
import { cookies } from 'next/headers';
import { createSpreeClient } from '@spree/sdk';

export async function GET() {
  const token = cookies().get('spree_jwt')?.value;
  const spree = createSpreeClient({
    apiUrl: process.env.SPREE_API_URL!,
    publishableKey: process.env.NEXT_PUBLIC_SPREE_PUBLISHABLE_KEY!,
    userToken: token,
  });
  const me = await spree.account.find();
  return Response.json(me);
}
```

User JWTs go in **httpOnly cookies** set server-side. Cart tokens go in httpOnly cookies. Public publishable key (`pk_…`) is fine in browser code (that's its purpose).

### Idempotency Keys

```typescript
const order = await spree.checkout.complete({
  idempotencyKey: crypto.randomUUID(),
});
```

Generate per logical operation; resend on transient failure to avoid double-charging.

### Error Handling

```typescript
import { SpreeError, ValidationError } from '@spree/sdk';

try {
  await spree.cart.addItem({ variantId: 'var_…', quantity: 99 });
} catch (err) {
  if (err instanceof ValidationError) {
    err.fieldErrors;  // { quantity: 'exceeds inventory' }
  } else if (err instanceof SpreeError) {
    err.code;         // e.g. 'invalid_variant'
    err.requestId;    // for support
  }
}
```

### Typing Customizations

If your Spree backend exposes custom Metafields or extension fields, extend the SDK's types via module augmentation:

```typescript
// types/spree.d.ts
declare module '@spree/sdk' {
  interface Product {
    metafields: {
      my_app: {
        launch_date?: string;
        editor_pick?: boolean;
      };
    };
  }
}
```

### Version Pinning

The SDK is generated against a specific OpenAPI spec version. Mismatches cause Zod validation failures. Strategy:
- Pin `@spree/sdk` to the exact backend Spree minor (`5.4.x`).
- Upgrade in lockstep with backend deploys.
- CI: run a smoke test against your staging backend before promoting.

## Implementation Guidance

### Recommended Project Layout (Next.js)

```
src/
├── lib/
│   ├── spree.server.ts    # createSpreeClient with adminApiKey — server-only
│   └── spree.public.ts    # createSpreeClient with publishableKey — safe for browser
├── app/
│   ├── (storefront)/      # public pages
│   └── api/               # Server Actions / Route Handlers
└── types/
    └── spree.d.ts          # type augmentations
```

**Never import `spree.server.ts` from a Client Component** — Next.js will yell, but it's also a credential leak.

### Caching API Responses

Use Next.js `fetch` cache or React `cache()`:

```typescript
import { cache } from 'react';

export const getProducts = cache(async () => {
  return await spree.products.list({ limit: 20 });
});
```

For ISR / revalidate:
```typescript
const products = await spree.products.list({}, { next: { revalidate: 60 } });
```

(Verify whether `@spree/sdk` exposes `fetch` options pass-through.)

### Webhook Verification Sidekick

The SDK may expose webhook signature verification helpers:

```typescript
import { verifyWebhookSignature } from '@spree/sdk/webhooks';

const event = verifyWebhookSignature({
  payload: rawBody,
  signature: request.headers['x-spree-webhook-signature'],
  secret: process.env.SPREE_WEBHOOK_SECRET!,
});
```

Verify in the live SDK docs.

### Pagination

```typescript
let cursor: string | undefined;
do {
  const page = await spree.products.list({ limit: 100, starting_after: cursor });
  for (const product of page.data) { /* process */ }
  cursor = page.has_more ? page.data[page.data.length - 1].id : undefined;
} while (cursor);
```

### Common Pitfalls

- **Importing the admin client from a Client Component** — exposes the admin key.
- **Pinning to `^5.4.0` instead of `5.4.x`** — minor releases can change generated schema shapes.
- **Storing JWT in localStorage** — XSS-vulnerable; use httpOnly cookies.
- **Not awaiting Zod parse errors** — silent stringy responses break runtime.
- **Using the SDK in browser code with admin key** — Next.js' server-only enforcement is your friend; opt into it.
- **Ignoring Idempotency-Key** — duplicate checkouts on retry.

Always verify resource names, method signatures, and option shapes against the live `@spree/sdk` README and the SDK's TypeScript declarations — the SDK is the youngest part of the Spree ecosystem and is iterating fast.
