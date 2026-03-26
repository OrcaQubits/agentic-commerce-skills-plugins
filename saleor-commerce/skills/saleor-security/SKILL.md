---
name: saleor-security
description: Secure Saleor applications — JWT authentication, OIDC integration, App tokens, permission model, rate limiting, CORS, and security headers. Use when configuring Saleor security.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Security

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io authentication JWT tokens` for current JWT authentication flow
2. Web-search `site:docs.saleor.io apps permissions` for App token authentication and permission model
3. Web-search `site:docs.saleor.io OIDC OpenID Connect` for OIDC integration configuration
4. Web-search `saleor webhook payload signature JWS verification` for webhook signature verification
5. Fetch `https://docs.saleor.io/docs/developer/app-store/apps/overview` for App authentication patterns
6. Web-search `saleor CORS security headers production` for CORS and header configuration

## JWT Authentication Flow

Saleor uses JSON Web Tokens for staff and customer authentication. Tokens are obtained via GraphQL mutations and passed as Bearer tokens.

### Token Lifecycle

| Operation | GraphQL Mutation | Token Type | Expiry |
|-----------|-----------------|------------|--------|
| **Customer login** | `tokenCreate` | Access + Refresh | Access: 5 min, Refresh: 30 days |
| **Staff login** | `tokenCreate` | Access + Refresh | Access: 5 min, Refresh: 30 days |
| **Refresh** | `tokenRefresh` | New access token | 5 min (configurable) |
| **Verify** | `tokenVerify` | Validity check | N/A |
| **Deactivate** | `tokensDeactivateAll` | Invalidate all | N/A |

### Token Usage

- Pass the access token in the `Authorization: Bearer <token>` header
- Refresh tokens are used only to obtain new access tokens
- Access tokens are short-lived by design to limit exposure
- CSRF token is required for cookie-based authentication (Dashboard)

## OIDC Integration

Saleor supports OpenID Connect for federated authentication. Saleor acts as an OAuth client, delegating login to an external identity provider.

### OIDC Configuration Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Saleor as OAuth client** | Delegates login to external IdP | SSO with corporate directory |
| **Authorization Code flow** | Standard OIDC flow with code exchange | Web applications |
| **ID token login** | Accept ID token from external IdP | Mobile or SPA apps |

### Key OIDC Settings

- `OIDC_JWKS_URL` — JSON Web Key Set endpoint of the IdP
- `OIDC_OAUTH_CLIENT_ID` — Client ID registered with IdP
- `OIDC_OAUTH_CLIENT_SECRET` — Client secret for code exchange
- Configured via an OIDC authentication App (not environment variables)

## App Token Authentication

Apps authenticate using App tokens (permanent Bearer tokens) rather than JWT:

| Token Type | Obtained Via | Expiry | Scope |
|-----------|-------------|--------|-------|
| **App token** | `appTokenCreate` mutation | Never (manual revoke) | App's declared permissions |
| **Auth token** (install handshake) | Token exchange during install | Session-scoped | Full App permissions |

- Apps declare required permissions in their manifest
- The store admin grants permissions during App installation
- App tokens are scoped to exactly the permissions granted

## Permission Model

Saleor uses a granular permission system applied to staff users, permission groups, and Apps.

### Core Permissions

| Permission | Grants Access To |
|-----------|-----------------|
| `MANAGE_PRODUCTS` | Create, update, delete products, variants, types |
| `MANAGE_ORDERS` | View and modify orders, fulfillments, returns |
| `MANAGE_APPS` | Install, configure, and remove Apps |
| `MANAGE_USERS` | Manage customer accounts |
| `MANAGE_STAFF` | Manage staff users and permission groups |
| `MANAGE_CHECKOUTS` | Access and modify checkouts |
| `MANAGE_CHANNELS` | Create and configure channels |
| `MANAGE_SHIPPING` | Configure shipping zones and methods |
| `MANAGE_DISCOUNTS` | Manage promotions, vouchers, gift cards |
| `MANAGE_TRANSLATIONS` | Manage translations for all entities |
| `MANAGE_SETTINGS` | Access to site-wide settings |
| `MANAGE_PAGE_TYPES_AND_ATTRIBUTES` | Manage page types and attribute schemas |
| `MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES` | Manage product types and attribute schemas |
| `HANDLE_PAYMENTS` | Process transactions and refunds |
| `HANDLE_TAXES` | Configure tax providers |

### Permission Groups

- Staff users are assigned to permission groups
- Each group has a set of permissions
- A staff user inherits the union of all group permissions
- Superuser (`is_superuser`) bypasses all permission checks

## Rate Limiting

- Configure via `THROTTLE_CLASSES` in Django settings
- Default throttle rates for anonymous, authenticated, and mutation requests
- Per-IP and per-user rate limiting available
- Webhook endpoints should have separate rate limits
- Plugin/App-specific rate limiting via middleware

## CORS Configuration

| Setting | Description | Example |
|---------|-------------|---------|
| `ALLOWED_ORIGINS` | Origins permitted to make requests | `["https://storefront.example.com"]` |
| `ALLOWED_HOSTS` | Hostnames the server responds to | `["api.example.com"]` |
| `CORS_ALLOW_CREDENTIALS` | Allow cookies cross-origin | `true` for Dashboard |
| `CORS_ALLOW_HEADERS` | Additional allowed headers | `["authorization-bearer", "content-type"]` |

- Use `django-cors-headers` middleware (included in Saleor)
- Never use `CORS_ALLOW_ALL_ORIGINS = True` in production
- Restrict origins to known storefronts, Dashboard, and Apps

## Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforce HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-type sniffing |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Prevent clickjacking |
| `Content-Security-Policy` | Directive-based | Restrict resource loading |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limit referrer leakage |

## Django SECRET_KEY Management

- Generate a strong random key: at least 50 characters
- Store in environment variable `SECRET_KEY`, never in source code
- Rotate periodically — existing sessions and tokens are invalidated on rotation
- Use separate keys for each environment (dev, staging, production)

## SSL/TLS Enforcement

- Set `SECURE_SSL_REDIRECT = True` in Django settings
- Set `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` behind a reverse proxy
- Use `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`
- All GraphQL API traffic must use HTTPS in production

## Webhook Payload Signature Verification

Saleor signs every webhook with the `Saleor-Signature` header. Since 3.5+, the default is **JWS (RS256)** using a public key from `/.well-known/jwks.json`. Legacy HMAC-SHA256 (via App secret) is deprecated and will be removed in 4.0.
- Verify JWS signatures by fetching the public key from `<saleor-domain>/.well-known/jwks.json`
- Use the `saleor-app-sdk` built-in middleware for automatic verification
- Reject requests with missing or invalid signatures

## Security Hardening Checklist

| Item | Action |
|------|--------|
| HTTPS | Enable `SECURE_SSL_REDIRECT`, set cookie secure flags |
| SECRET_KEY | Strong random value, environment variable only |
| ALLOWED_HOSTS | Restrict to actual domain names |
| CORS | Restrict to known origins |
| DEBUG | Set `DEBUG = False` in production |
| Database | Use SSL connections, restrict network access |
| App tokens | Rotate periodically, grant minimal permissions |
| Webhook signatures | Always verify JWS/HMAC on every webhook handler |
| Rate limiting | Enable throttling on all public endpoints |
| Dependencies | Pin versions, audit with `pip-audit` or `safety` |
| Admin access | Use permission groups with least-privilege |
| Logs | Never log tokens, secrets, or PII |

## Best Practices

- Always verify webhook signatures (JWS default, HMAC deprecated) before processing payloads
- Use short-lived JWT access tokens and refresh tokens for session management
- Grant Apps the minimum permissions required for their functionality
- Store all secrets (SECRET_KEY, database password, App secrets) in environment variables
- Enable HTTPS everywhere and set all security-related Django settings
- Use OIDC for single sign-on rather than managing passwords directly
- Implement rate limiting to protect against brute-force and denial-of-service attacks
- Audit permission groups regularly to enforce least-privilege access
- Keep Saleor and all Python dependencies up to date with security patches
- Use `ALLOWED_HOSTS` and CORS to prevent host header attacks and cross-origin abuse

Fetch the security documentation for current JWT authentication flow, OIDC configuration, and permission model before implementing.
