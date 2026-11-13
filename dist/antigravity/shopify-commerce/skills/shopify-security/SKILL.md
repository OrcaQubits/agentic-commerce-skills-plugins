---
name: shopify-security
description: >
  Secure Shopify applications — HMAC webhook verification, session token
  validation, OAuth scope management, Content Security Policy, GDPR mandatory
  webhooks, input validation, and secure coding practices. Use when implementing
  Shopify security features.
---

# Shopify Security

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev security best practices` for security guidelines
2. Web-search `site:shopify.dev webhook verification hmac` for HMAC implementation
3. Web-search `site:shopify.dev session token` for session token verification

## HMAC Webhook Verification

Every webhook includes `X-Shopify-Hmac-SHA256`:

```typescript
import crypto from 'crypto';

function verifyShopifyWebhook(
  rawBody: Buffer,
  hmacHeader: string,
  secret: string,
): boolean {
  const calculated = crypto
    .createHmac('sha256', secret)
    .update(rawBody)
    .digest('base64');

  return crypto.timingSafeEqual(
    Buffer.from(calculated),
    Buffer.from(hmacHeader),
  );
}
```

**Critical:** Use `timingSafeEqual` to prevent timing attacks. Use raw body buffer, not parsed JSON.

## Session Token Verification

For embedded apps using App Bridge:

```typescript
import jwt from 'jsonwebtoken';

function verifySessionToken(token: string, apiSecret: string) {
  const decoded = jwt.verify(token, apiSecret, {
    algorithms: ['HS256'],
  });

  // Verify issuer is a valid Shopify shop
  const iss = decoded.iss as string;
  if (!iss.match(/^https:\/\/[a-zA-Z0-9-]+\.myshopify\.com\/admin$/)) {
    throw new Error('Invalid issuer');
  }

  return decoded;
}
```

Session token claims:
- `iss` — shop admin URL
- `dest` — shop URL
- `sub` — user ID
- `exp` — expiration (1 minute)
- `nbf` — not before
- `iat` — issued at
- `jti` — unique token ID

## OAuth Scope Management

### Principle of Least Privilege

- Request only scopes your app needs
- Separate read and write scopes
- Review scopes when adding features

### Scope Verification

Verify the access token has expected scopes:
- Store granted scopes during OAuth callback
- Check before making API calls that require specific permissions

## Content Security Policy (CSP)

For embedded apps in Shopify admin:
- Shopify admin sets strict CSP headers
- Your app must comply: no inline scripts, no `eval()`, no external fonts without proper headers
- Use `frame-ancestors` header for iframe embedding:
  ```
  Content-Security-Policy: frame-ancestors https://*.myshopify.com https://admin.shopify.com;
  ```

## GDPR Mandatory Webhooks

Every app MUST implement:

1. **`customers/data_request`** — respond within 30 days with customer data
2. **`customers/redact`** — delete customer data within 30 days
3. **`shop/redact`** — delete ALL store data within 48 hours of uninstall

Failing to implement these results in app rejection.

## Input Validation

### API Data

- Validate and sanitize all input from Shopify webhooks
- Verify webhook topic matches expected schema
- Validate metafield values (may contain arbitrary JSON)

### Theme/Liquid

- Apply `| escape` filter to user-generated content
- Use `| json` filter for embedding data in JavaScript
- Never output raw `customer` data without escaping

### GraphQL

- Use parameterized queries (variables, not string interpolation)
- Validate and sanitize user input before passing as variables
- Handle `userErrors` in mutation responses

## Secrets Management

- Never hardcode API keys, secrets, or tokens in source code
- Use environment variables or platform secret management
- Rotate access tokens periodically
- Store tokens encrypted at rest
- Use `.env` files locally (excluded from version control)

## Best Practices

- Verify HMAC on every webhook — never skip verification
- Use `timingSafeEqual` for all secret comparisons
- Validate session tokens on every embedded app request
- Implement all GDPR mandatory webhooks before submitting for app review
- Apply CSP headers for embedded apps
- Escape all user input in Liquid templates
- Use parameterized GraphQL queries — never interpolate user input into queries
- Log security events but never log tokens or secrets
- Keep dependencies updated — run `npm audit` regularly

Fetch the Shopify security documentation for exact HMAC implementation, session token structure, and CSP requirements before implementing.
