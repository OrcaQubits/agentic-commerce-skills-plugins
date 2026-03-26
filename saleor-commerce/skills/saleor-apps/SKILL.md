---
name: saleor-apps
description: Develop Saleor Apps — App manifest, saleor-app-sdk, Next.js template, permissions, token exchange, APL, App Bridge, and lifecycle management. Use when building Saleor App extensions.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor App Development

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/extending/apps/overview` for Apps architecture
2. Web-search `site:docs.saleor.io saleor app manifest structure` for manifest reference
3. Web-search `site:docs.saleor.io saleor-app-sdk token exchange APL` for SDK utilities
4. Web-search `site:github.com saleor/saleor-app-template` for latest Next.js App template
5. Web-search `site:docs.saleor.io app permissions` for permission enumeration
6. Web-search `site:docs.saleor.io app bridge dashboard extensions` for Bridge API

## App Architecture

Saleor Apps are standalone web applications that extend Saleor functionality. They are not monolithic plugins embedded in the core -- each App is an independent service that communicates with Saleor via GraphQL and webhooks.

| Aspect | Detail |
|--------|--------|
| Deployment | Standalone web app (any host) |
| Communication | GraphQL API + webhooks |
| Framework | Any (official template uses Next.js) |
| Registration | Installed via manifest URL |
| Authentication | App token issued during installation |
| Dashboard UI | Rendered in an iframe via App Bridge |

### Legacy Plugins Deprecation

Saleor's legacy plugin system (Python classes in `saleor/plugins/`) is deprecated. All new extensions should be built as Apps. Legacy plugins will be removed in a future major version.

## App Manifest

The manifest is a JSON document served at a public URL that describes the App:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | string | Unique identifier for the App |
| `version` | string | Semantic version |
| `name` | string | Display name |
| `about` | string | Short description |
| `permissions` | string[] | Required Saleor permissions |
| `appUrl` | string | Main App URL (loaded in Dashboard iframe) |
| `configurationUrl` | string | App settings page URL |
| `tokenTargetUrl` | string | URL that receives the auth token during install |
| `dataPrivacyUrl` | string | Privacy policy URL |
| `homepageUrl` | string | App homepage URL |
| `supportUrl` | string | Support contact URL |
| `webhooks` | object[] | Webhook subscriptions |
| `extensions` | object[] | Dashboard mounting points |

The manifest URL is provided when installing the App via the Dashboard or the `appInstall` mutation.

## saleor-app-sdk

The official TypeScript SDK provides core utilities for building Saleor Apps:

| Utility | Purpose |
|---------|---------|
| `SaleorApp` | Main App class coordinating APL, manifest, handlers |
| `createManifestHandler` | Next.js API route handler for manifest endpoint |
| `createAppRegisterHandler` | Handler for the token exchange callback |
| `withRegisteredSaleorDomainHeader` | Middleware to verify request origin |
| `verifyJWT` | Verify Saleor-issued JWTs in webhook requests |
| `getAppId` | Retrieve the App's ID from the token |
| `SALEOR_API_URL_HEADER` | Standard header name for Saleor instance URL |
| `SALEOR_AUTHORIZATION_BEARER_HEADER` | Standard header for App auth token |

Install via `npm install @saleor/app-sdk` -- fetch live docs for the current version.

## Auth Persistence Layer (APL)

The APL stores the mapping between Saleor instance URLs and the App's auth tokens:

| APL Type | Storage | Use Case |
|----------|---------|----------|
| `FileAPL` | Local JSON file | Development only |
| `UpstashAPL` | Upstash Redis | Serverless production |
| `SaleorCloudAPL` | Saleor Cloud | Apps deployed to Saleor Cloud |
| `EnvAPL` | Environment variable | Single-tenant simple deployments |
| Custom | Any store | Implement the APL interface |

The APL is critical -- without it, the App cannot authenticate requests from Saleor after a server restart.

## App Installation Flow

| Step | Actor | Action |
|------|-------|--------|
| 1 | Admin | Provides manifest URL in Dashboard |
| 2 | Saleor | Fetches manifest, validates permissions |
| 3 | Saleor | Sends auth token to `tokenTargetUrl` |
| 4 | App | Stores token in APL |
| 5 | Saleor | Marks App as installed |
| 6 | App | Uses stored token for all future API calls |

## App Permissions

| Permission | Scope |
|------------|-------|
| `MANAGE_PRODUCTS` | Create, update, delete products |
| `MANAGE_ORDERS` | View and manage orders |
| `MANAGE_CHECKOUTS` | Manage checkout sessions |
| `MANAGE_USERS` | View and manage customers |
| `MANAGE_SHIPPING` | Configure shipping methods |
| `MANAGE_DISCOUNTS` | Create and manage promotions |
| `MANAGE_CHANNELS` | Configure channels |
| `MANAGE_APPS` | Install and manage other Apps |
| `HANDLE_PAYMENTS` | Process payment transactions |
| `HANDLE_TAXES` | Calculate taxes for checkout |

Request only the permissions your App actually needs -- the principle of least privilege.

## App Template (Next.js)

The official `saleor-app-template` scaffolds a Next.js App with all SDK wiring:

| File | Purpose |
|------|---------|
| `pages/api/manifest.ts` | Serves the App manifest |
| `pages/api/register.ts` | Handles token exchange |
| `pages/api/webhooks/*.ts` | Webhook handler endpoints |
| `pages/index.tsx` | Main App page (Dashboard iframe) |
| `saleor-app.ts` | SaleorApp instance and APL configuration |
| `lib/saleor-client.ts` | Authenticated GraphQL client factory |

Scaffold with `npx @saleor/cli app create` -- fetch live docs for current template version.

## Local Development

| Task | Command / Tool |
|------|---------------|
| Start dev server | `npm run dev` (Next.js on port 3000) |
| Expose locally | `saleor app tunnel` or `ngrok` |
| Install in Saleor | Provide tunnel URL as manifest URL |
| View logs | Check terminal output and Saleor Dashboard App logs |
| Test webhooks | Use tunnel + Saleor triggers |

The tunnel is required because Saleor must reach your App over HTTPS to deliver webhooks and fetch the manifest.

## Authenticated GraphQL Client

After installation, use the stored auth token to call the Saleor API:

```typescript
// lib/saleor-client.ts
// Fetch live docs for current client setup pattern
import { createGraphQLClient } from "@saleor/apps-shared"

export function createClient(saleorApiUrl: string, token: string) {
  return createGraphQLClient({ saleorApiUrl, token })
}
```

## Best Practices

- Build all new extensions as Apps, not legacy plugins
- Store auth tokens securely using an appropriate APL for your deployment target
- Request only the permissions your App needs -- follow least privilege
- Use subscription queries in webhook definitions for precise payload control
- Verify webhook signatures (JWS default since 3.5+, HMAC deprecated) before processing any payload
- Use `saleor app tunnel` during development for reliable webhook delivery
- Handle the `SALEOR_API_URL_HEADER` to support multi-tenant App installations
- Test the full install/uninstall lifecycle before deploying to production

Fetch the Saleor Apps documentation for exact manifest fields, SDK method signatures, and APL configuration patterns before implementing.
