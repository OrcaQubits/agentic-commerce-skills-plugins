---
name: mpp-server-middleware
description: >
  Implement MPP server-side middleware for Hono, Express, Next.js, and Elysia.
  Use when protecting API routes with HTTP 402 payment gates, configuring
  payment methods, or setting up the Mppx server instance.
---

# MPP Server Middleware

## Before writing code

**Fetch live docs**:
1. Fetch `https://www.npmjs.com/package/mppx` for the current server middleware API and configuration options
2. Web-search `mppx server middleware hono express next.js elysia` for framework-specific integration patterns
3. Web-search `site:github.com stripe-samples machine-payments server` for official server sample code
4. Fetch `https://docs.stripe.com/payments/machine/mpp` for Stripe-side server configuration

## Conceptual Architecture

### What the Server Middleware Does

The `mppx` server middleware intercepts requests to protected routes and implements the full HTTP 402 challenge-response flow:

1. **Intercept** — Middleware runs before your route handler
2. **Challenge** — If no `Authorization: Payment` header, returns `402` with `WWW-Authenticate: Payment` challenge
3. **Verify** — If credential present, validates proof of payment (on-chain verification, SPT validation, etc.)
4. **Pass-through** — On successful verification, calls the next handler
5. **Receipt** — Adds `Payment-Receipt` header to the response

### Mppx.create() Configuration

The central factory creates the server instance:

```typescript
const mppx = Mppx.create({
  secretKey: process.env.MPP_SECRET_KEY,  // 32-byte hex for HMAC challenge binding
  methods: [/* payment method configurations */],
});
```

The `secretKey` is critical — it binds challenges to prevent forgery and replay attacks.

### Supported Frameworks

| Framework | Middleware Pattern | Notes |
|-----------|-------------------|-------|
| **Hono** | `app.get('/path', mppx.charge(...), handler)` | Native middleware chaining |
| **Express** | `app.get('/path', mppx.charge(...), handler)` | Standard Express middleware |
| **Next.js** | Route handler wrapping | App Router and Pages Router |
| **Elysia** | Plugin-style integration | Bun-native framework |

### Route Protection

Two middleware functions match the two payment intents:

- **`mppx.charge({ amount })`** — Per-request payment gate (charge intent)
- **`mppx.session({ maxAmount })`** — Session-based streaming payment gate (session intent)

### Amount Specification

- Amounts are strings representing the smallest currency unit
- For USDC: `'100'` = $0.01 (USDC has 6 decimals, so 100 = 0.000100, but convention varies by method)
- For Stripe: follows Stripe's minor-unit convention (cents)
- Always verify exact amount semantics in the SDK docs for your payment method

### Multiple Payment Methods

A single server can accept multiple payment methods simultaneously:

```typescript
const mppx = Mppx.create({
  secretKey: process.env.MPP_SECRET_KEY,
  methods: [
    tempo.charge({ /* Tempo config */ }),
    stripe.charge({ /* Stripe config */ }),
  ],
});
```

The client selects which method to use when fulfilling the challenge.

### Dynamic Pricing

For routes where the price depends on the request:

- Use a pricing function that receives the request and returns the amount
- Implement custom middleware that computes the price and passes it to `mppx.charge()`

### Error Responses

The middleware returns RFC 9457 Problem Details on payment errors:

| Status | Type | When |
|--------|------|------|
| 402 | `payment-required` | No credential provided |
| 402 | `verification-failed` | Invalid proof of payment |
| 402 | `payment-expired` | Challenge or credential expired |
| 402 | `malformed-credential` | Unparseable credential |

### Best Practices

- Always use environment variables for `secretKey`, never hardcode
- Set appropriate challenge expiration times (not too short for UX, not too long for security)
- Log payment verification results (without sensitive data) for debugging
- Implement health check endpoints outside the payment middleware
- Use HTTPS in production (TLS 1.2+ required by spec)
- Add CORS headers if the API is consumed from browsers

Fetch the latest mppx package README for exact middleware API signatures, configuration options, and framework-specific examples before implementing.
