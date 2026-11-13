---
name: medusa-security
description: >
  Secure Medusa v2 applications — authentication strategies, API key types
  (publishable vs secret), CORS configuration, JWT and cookie secrets, admin vs
  store auth, and session management. Use when configuring security.
---

# Medusa v2 Security

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com authentication` for auth strategies and API key setup
2. Web-search `site:docs.medusajs.com api key publishable secret` for API key types
3. Web-search `site:docs.medusajs.com CORS configuration` for cross-origin resource sharing
4. Fetch `https://docs.medusajs.com/learn/fundamentals/api-routes/middlewares` for middleware and auth config
5. Web-search `site:docs.medusajs.com medusa-config auth providers` for auth provider registration

## Authentication Architecture

### Admin vs Store Authentication

Medusa v2 separates admin and storefront authentication into distinct flows:

| Aspect | Admin Auth | Store Auth |
|--------|-----------|------------|
| **Actor type** | `user` | `customer` |
| **API scope** | `/admin/*` routes | `/store/*` routes |
| **Default provider** | `emailpass` | `emailpass` |
| **Session cookie** | Admin session cookie | Store session cookie |
| **API key support** | Secret API key (Bearer) | Publishable API key (header) |
| **JWT usage** | Admin JWT token | Customer JWT token |
| **Middleware** | `authenticate("user", ...)` | `authenticate("customer", ...)` |

### Auth Provider System

```
Auth Module
├── emailpass    — email + password (default)
├── google       — OAuth 2.0 via Google
├── github       — OAuth 2.0 via GitHub
└── custom       — implement AbstractAuthModuleProvider
```

Auth providers are registered in `medusa-config.ts` under the `auth` module configuration. Each provider handles a specific identity verification strategy.

## API Key Types

| Key Type | Header | Purpose | Visibility |
|----------|--------|---------|------------|
| **Publishable** | `x-publishable-api-key` | Storefront API access, scopes to sales channels | Safe for client-side |
| **Secret** | `Authorization: Bearer <key>` | Admin API access, full permissions | Server-side only |

- Publishable keys are created in the admin dashboard and tied to sales channels
- Secret keys grant admin-level access and must never be exposed to browsers
- Store API routes require a publishable key header for sales channel scoping

## CORS Configuration

Configure CORS in `medusa-config.ts` under `projectConfig`:

| Setting | Purpose | Example |
|---------|---------|---------|
| `storeCors` | Allowed origins for Store API | `http://localhost:8000` |
| `adminCors` | Allowed origins for Admin API | `http://localhost:9000` |
| `authCors` | Allowed origins for Auth routes | `http://localhost:8000,http://localhost:9000` |

- Use comma-separated strings or regex patterns for multiple origins
- In production, restrict to exact domains — never use `*` wildcard
- `authCors` must include both storefront and admin origins

## JWT and Cookie Secrets

### Secret Configuration

| Secret | Environment Variable | Purpose |
|--------|---------------------|---------|
| **Cookie secret** | `COOKIE_SECRET` | Signs session cookies |
| **JWT secret** | `JWT_SECRET` | Signs JSON Web Tokens |
| **Admin JWT** | Configured per auth provider | Admin token signing |
| **Store JWT** | Configured per auth provider | Customer token signing |

- Both `COOKIE_SECRET` and `JWT_SECRET` must be set in production
- Use cryptographically random strings (minimum 32 characters)
- Rotate secrets by updating env vars and restarting the server

## Session Management

Sessions are managed via HTTP-only cookies with configurable options:

- **Session store** — in-memory by default; use Redis for production
- **Cookie flags** — `httpOnly`, `secure`, `sameSite`, `maxAge`
- **Session TTL** — configurable expiration; defaults vary by auth scope
- Redis session store ensures sessions survive server restarts and work across multiple instances

## API Route Authentication

### Middleware Configuration

Apply auth middleware in `src/api/middlewares.ts`:

```ts
// Fetch live docs for authenticate() middleware
// signature and actor type options
import { authenticate } from "@medusajs/medusa"
```

| Middleware Function | Actor Type | Use Case |
|-------------------|-----------|----------|
| `authenticate("user", ...)` | Admin user | Admin-only routes |
| `authenticate("customer", ...)` | Customer | Store auth-required routes |
| `authenticate("user", ["bearer","session"])` | Admin | Multiple auth strategies |

### Auth Scopes on Custom Routes

- Admin routes: place in `src/api/admin/` — auto-protected
- Store routes: place in `src/api/store/` — require publishable key
- Custom routes: manually apply `authenticate()` middleware

## Auth Provider Implementation

Custom auth providers extend `AbstractAuthModuleProvider`:

```ts
// Fetch live docs for AbstractAuthModuleProvider
// methods: authenticate, register, validateCallback
```

| Method | Purpose |
|--------|---------|
| `authenticate()` | Verify identity (login) |
| `register()` | Create new identity |
| `validateCallback()` | Handle OAuth redirect callbacks |

## Security Hardening Checklist

### Environment Variables

- Set unique `COOKIE_SECRET` and `JWT_SECRET` (never use defaults)
- Use `DATABASE_URL` with SSL mode for PostgreSQL connections
- Store secrets in environment variables, never in source code

### Network and Transport

- Enforce HTTPS in production for all API communication
- Restrict CORS origins to exact production domains
- Use `secure: true` and `sameSite: "strict"` on cookies in production

### API Keys and Access

- Create separate publishable keys per sales channel
- Rotate secret API keys on a regular schedule
- Audit admin user accounts and remove unused access
- Use the principle of least privilege for API key scoping

### Session and Token Security

- Use Redis as session store in production (not in-memory)
- Set appropriate session TTL values (short for admin, configurable for store)
- Implement token refresh logic in storefronts

## Best Practices

- **Auth provider selection** — use `emailpass` for standard flows; add OAuth providers for social login; register providers in `medusa-config.ts` under the auth module
- **Key management** — publishable keys are public and safe for client bundles; secret keys must only live on the server; never log or commit API keys
- **CORS discipline** — always set `storeCors`, `adminCors`, and `authCors` explicitly; test CORS headers before deploying; avoid wildcard origins in production
- **Cookie security** — enable `httpOnly`, `secure`, and `sameSite` flags; use Redis-backed sessions for multi-instance deployments; set reasonable TTLs

Fetch the Medusa authentication and security documentation for exact provider registration syntax, middleware options, and cookie configuration before implementing.
