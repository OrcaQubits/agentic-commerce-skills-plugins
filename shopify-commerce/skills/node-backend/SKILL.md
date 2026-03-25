---
name: node-backend
description: Build Node.js backends for Shopify apps — Remix server, @shopify/shopify-app-remix, session storage, OAuth handling, API proxy, webhook processing, and deployment. Use when building the server-side component of Shopify apps.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Node.js Backend for Shopify Apps

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev app remix server` for Remix app server patterns
2. Web-search `site:github.com shopify shopify-app-js` for Shopify Node.js libraries
3. Web-search `site:shopify.dev session storage` for session management options

## App Server Architecture

### Typical Stack

```
Shopify Admin (iframe)
    ↓ App Bridge session token
Remix Server (@shopify/shopify-app-remix)
    ↓ GraphQL Admin API calls
Shopify APIs
    ↓ Webhooks
Your Webhook Handler
```

### Key Packages

| Package | Purpose |
|---------|---------|
| `@shopify/shopify-app-remix` | Remix integration (auth, session, billing, webhooks) |
| `@shopify/shopify-api` | Low-level Shopify API client |
| `@shopify/app-bridge-react` | App Bridge React components |
| `@shopify/polaris` | Admin UI components |

### Project Structure

```
shopify-app/
├── app/
│   ├── routes/
│   │   ├── app._index.tsx        # App dashboard
│   │   ├── app.products.tsx      # Products page
│   │   ├── auth.$.tsx            # OAuth callback handler
│   │   └── webhooks.tsx          # Webhook endpoint
│   ├── shopify.server.ts         # Shopify API client initialization
│   ├── db.server.ts              # Database connection
│   └── root.tsx                  # Root layout
├── prisma/
│   └── schema.prisma             # Database schema (session storage)
├── extensions/                   # App extensions (Functions, checkout UI)
├── shopify.app.toml              # App configuration
├── .env
└── package.json
```

## Shopify App Remix Setup

### Server Initialization

```typescript
// app/shopify.server.ts
import "@shopify/shopify-app-remix/adapters/node";
import { AppDistribution, shopifyApp } from "@shopify/shopify-app-remix/server";
import { PrismaSessionStorage } from "@shopify/shopify-app-session-storage-prisma";
import { prisma } from "./db.server";

const shopify = shopifyApp({
  apiKey: process.env.SHOPIFY_API_KEY!,
  apiSecretKey: process.env.SHOPIFY_API_SECRET!,
  appUrl: process.env.SHOPIFY_APP_URL!,
  scopes: process.env.SCOPES?.split(","),
  authPathPrefix: "/auth",
  sessionStorage: new PrismaSessionStorage(prisma),
  distribution: AppDistribution.AppStore,
  webhooks: {
    APP_UNINSTALLED: {
      deliveryMethod: "http",
      callbackUrl: "/webhooks",
    },
  },
  hooks: {
    afterAuth: async ({ session }) => {
      // Register webhooks after successful auth
      shopify.registerWebhooks({ session });
    },
  },
});

export default shopify;
export const apiVersion = shopify.apiVersion;
export const addDocumentResponseHeaders = shopify.addDocumentResponseHeaders;
export const authenticate = shopify.authenticate;
export const registerWebhooks = shopify.registerWebhooks;
```

### Authentication in Loaders

```typescript
// app/routes/app._index.tsx
import { json, type LoaderFunctionArgs } from "@remix-run/node";
import { authenticate } from "../shopify.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const { admin } = await authenticate.admin(request);

  const response = await admin.graphql(`
    query {
      products(first: 10) {
        edges {
          node {
            id
            title
          }
        }
      }
    }
  `);

  const { data } = await response.json();
  return json({ products: data.products.edges });
}
```

### Webhook Handler

```typescript
// app/routes/webhooks.tsx
import type { ActionFunctionArgs } from "@remix-run/node";
import { authenticate } from "../shopify.server";

export async function action({ request }: ActionFunctionArgs) {
  const { topic, shop, payload } = await authenticate.webhook(request);

  switch (topic) {
    case "APP_UNINSTALLED":
      // Clean up shop data
      await deleteShopData(shop);
      break;
    case "CUSTOMERS_DATA_REQUEST":
      // Handle GDPR data request
      break;
    case "CUSTOMERS_REDACT":
      // Delete customer data
      break;
    case "SHOP_REDACT":
      // Delete all shop data
      break;
  }

  return new Response();
}
```

## Session Storage Options

| Storage | Package | Use Case |
|---------|---------|----------|
| Prisma | `@shopify/shopify-app-session-storage-prisma` | Production (SQL databases) |
| SQLite | `@shopify/shopify-app-session-storage-sqlite` | Development, small apps |
| Redis | `@shopify/shopify-app-session-storage-redis` | High-traffic apps |
| Memory | `@shopify/shopify-app-session-storage-memory` | Testing only |
| DynamoDB | `@shopify/shopify-app-session-storage-dynamodb` | AWS deployments |

## GraphQL Admin Client

The authenticated admin client handles:
- Automatic token management
- Rate limiting (retries on 429)
- API versioning
- Type-safe queries (with codegen)

```typescript
// Make a GraphQL call
const response = await admin.graphql(`
  mutation ProductCreate($input: ProductInput!) {
    productCreate(input: $input) {
      product { id title }
      userErrors { field message }
    }
  }
`, {
  variables: {
    input: { title: "New Product" },
  },
});
```

## REST Client (Legacy)

For endpoints not yet available in GraphQL:

```typescript
const response = await admin.rest.get({
  path: 'themes',
});
```

**Note:** REST is deprecated. Use GraphQL whenever possible.

## Deployment

### Shopify-Hosted (Spin)

For apps using `shopify app deploy`:
- Automatic hosting
- Managed infrastructure
- Environment variables in Shopify admin

### Self-Hosted Options

| Platform | Setup |
|----------|-------|
| Vercel | `vercel deploy` |
| Fly.io | `fly deploy` |
| Railway | `railway deploy` |
| Render | Git push |
| AWS (ECS/Lambda) | SAM/CDK |

### Environment Variables

```
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_SECRET=your-api-secret
SHOPIFY_APP_URL=https://your-app.example.com
SCOPES=read_products,write_products,read_orders
DATABASE_URL=file:./dev.db
```

## Best Practices

- Use `@shopify/shopify-app-remix` — do not build auth/session from scratch
- Use Prisma for session storage in production (not SQLite or memory)
- Authenticate every request with `authenticate.admin(request)`
- Register webhooks in `afterAuth` hook — they need valid access tokens
- Implement all GDPR webhooks in the webhook handler
- Use GraphQL over REST for all API calls
- Handle `userErrors` in GraphQL mutations — 200 status does not mean success
- Store environment variables securely — never commit `.env`
- Use `shopify app dev` for local development (handles tunneling and auth)

Fetch the Shopify Remix app documentation and @shopify/shopify-app-remix package docs for exact initialization, authentication, and deployment patterns before implementing.
