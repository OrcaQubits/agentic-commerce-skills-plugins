---
name: shopify-app-dev
description: Build Shopify apps — app types, Remix template, App Bridge, session tokens, OAuth flow, app extensions, embedded admin apps. Use when developing Shopify apps or integrations.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify App Development

## Before writing code

**Fetch live docs**:
1. Fetch `https://shopify.dev/docs/apps/build` for app development overview
2. Web-search `site:shopify.dev app bridge` for current App Bridge APIs and CDN version
3. Web-search `site:shopify.dev shopify-app-template-remix` for Remix template patterns
4. Web-search `site:shopify.dev shopify-app-remix authenticate` for authentication APIs
5. Web-search `site:github.com shopify shopify-app-template-remix` for latest template source

## App Types

### Public Apps (App Store)
- Listed on Shopify App Store
- Installed by any merchant via OAuth flow
- Must pass Shopify app review
- Use session tokens for authentication

### Custom Apps
- Built for a single store
- Installed directly from admin (Settings > Apps)
- Simpler auth: custom app access token (`shpca_` prefix)

### Private Apps (Legacy)
- Deprecated — migrate to custom apps
- Used hardcoded credentials (`shppa_` prefix)

## Remix App Architecture

The official template (`shopify-app-template-remix`):

```bash
shopify app init
# Select "Remix" template
# Provides: auth, session storage, webhook handling, Polaris UI
```

### Key Files

| File | Purpose |
|------|---------|
| `app/shopify.server.ts` | Initializes `@shopify/shopify-app-remix` (auth, sessions, webhooks) |
| `app/routes/auth.$.tsx` | Handles OAuth callback |
| `app/routes/webhooks.tsx` | Webhook endpoint |
| `app/routes/app._index.tsx` | Main app UI (embedded in admin) |
| `app/routes/app.tsx` | App layout with App Bridge provider |
| `shopify.app.toml` | App configuration (scopes, URLs, extensions) |
| `prisma/schema.prisma` | Database schema for session storage |

> **Fetch live docs** for the current template file structure — files and patterns evolve with `@shopify/shopify-app-remix` versions.

### Minimal Pattern: Authenticated Loader

```typescript
// Pattern: authenticate admin request, call GraphQL, return data
// Fetch live docs for current authenticate.admin() API shape
import { json, type LoaderFunctionArgs } from "@remix-run/node";
import { authenticate } from "../shopify.server";

export const loader = async ({ request }: LoaderFunctionArgs) => {
  const { admin } = await authenticate.admin(request);
  const response = await admin.graphql(`{ shop { name } }`);
  const { data } = await response.json();
  return json({ shopName: data.shop.name });
};
```

## OAuth Flow

1. Merchant clicks "Install" → redirected to Shopify consent screen
2. Shopify shows requested scopes → merchant approves
3. Shopify redirects to your app with authorization code
4. Your app exchanges code for access token (`shpua_` prefix)
5. Token stored in session storage (Prisma, SQLite, Redis, etc.)
6. Subsequent requests use session tokens (JWT) via App Bridge

The Remix template handles steps 1-5 automatically via `authenticate.admin()`.

> **Fetch live docs**: Web-search `site:shopify.dev oauth flow app installation` for current OAuth endpoints and token exchange details.

## Session Tokens

Modern Shopify apps use JWT session tokens instead of cookies:
- App Bridge sends token in `Authorization: Bearer` header
- Token is verified server-side using the app's API secret
- Contains: `iss` (shop domain), `dest` (shop URL), `sub` (user ID), `aud` (API key)
- Short-lived (1 minute), auto-refreshed by App Bridge
- Never use cookies for auth in embedded apps

> **Fetch live docs**: Web-search `site:shopify.dev session tokens jwt` for current token payload structure and verification.

## App Bridge

JavaScript library for embedded apps to communicate with Shopify admin:

| Feature | Description |
|---------|-------------|
| Navigation | Redirect to admin pages, products, orders |
| Toast | Temporary notifications (success/error) |
| Modal | Dialog overlays |
| Resource picker | Select products, collections, customers |
| Title bar | Set title and action buttons |
| Full-screen | Toggle full-screen mode |
| Loading indicator | Show/hide loading state |

**Note:** App Bridge v1/v2 are superseded. Use the current CDN-hosted version (automatically included with `@shopify/shopify-app-remix`).

> **Fetch live docs**: The App Bridge API surface changes frequently. Web-search `site:shopify.dev app bridge` for current methods, resource picker options, and modal API.

## App Configuration (shopify.app.toml)

```toml
# Stable structure — fetch live docs for current field names
name = "My Shopify App"
client_id = "your-api-key"

[access_scopes]
scopes = "read_products,write_products,read_orders"

[auth]
redirect_urls = ["https://your-app.com/auth/callback"]

[webhooks]
api_version = "2025-01"  # Update to latest stable version
```

> **Fetch live docs**: Web-search `site:shopify.dev shopify.app.toml configuration` for current TOML fields — new sections are added for extensions, app proxy, POS, etc.

## App Extensions

Apps can provide extensions that appear in various Shopify surfaces:

| Extension Type | Location | Use Case |
|---------------|----------|----------|
| Theme app extension | Storefront (in theme) | Product badges, custom sections |
| Checkout UI extension | Checkout page | Custom fields, upsells |
| Post-purchase extension | After payment | Upsell/cross-sell |
| POS UI extension | Point of Sale | Custom POS actions |
| Admin action extension | Admin pages | Bulk actions, custom workflows |
| Admin block extension | Resource pages | Embedded cards in admin |

> **Fetch live docs**: Extension types expand regularly. Web-search `site:shopify.dev app extensions types` for the current list and configuration patterns.

## Scopes

Request minimum necessary scopes:

| Scope | Access |
|-------|--------|
| `read_products` / `write_products` | Products, variants, collections |
| `read_orders` / `write_orders` | Orders, transactions |
| `read_customers` / `write_customers` | Customer records |
| `read_inventory` / `write_inventory` | Inventory levels |
| `read_fulfillments` / `write_fulfillments` | Fulfillment orders |
| `read_shipping` / `write_shipping` | Shipping and carrier services |
| `read_content` / `write_content` | Pages, blogs, articles |
| `read_themes` / `write_themes` | Theme files |

> **Fetch live docs**: New scopes are added with new API features. Web-search `site:shopify.dev access scopes` for the full current list.

## Webhook Handler Pattern

```typescript
// Pattern: authenticate webhook, switch on topic, process
// Fetch live docs for current webhook topic constants
export const action = async ({ request }: ActionFunctionArgs) => {
  const { topic, shop, payload } = await authenticate.webhook(request);

  switch (topic) {
    case "APP_UNINSTALLED":
      // Clean up shop data
      break;
    case "CUSTOMERS_DATA_REQUEST":
    case "CUSTOMERS_REDACT":
    case "SHOP_REDACT":
      // Handle mandatory GDPR webhooks
      break;
  }
  return new Response();
};
```

## Best Practices

- Use the Remix template (`shopify app init`) — do not build from scratch
- Use session tokens over cookies for embedded apps
- Request minimum OAuth scopes needed
- Handle webhook deduplication with idempotency keys
- Implement all mandatory GDPR webhooks (`customers/data_request`, `customers/redact`, `shop/redact`)
- Use App Bridge for navigation and UI — do not build custom admin chrome
- Store access tokens encrypted, never in client-side code
- Test with development stores before submitting for review
- Use `authenticate.admin()` in every loader/action that needs store data

Fetch the Shopify app development guide, App Bridge docs, and Remix template source for exact APIs, session token structure, and extension patterns before implementing.
