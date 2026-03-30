---
name: mpp-dev-patterns
description: >
  Cross-cutting MPP development patterns — security, replay protection, HMAC
  challenge binding, receipt validation, error handling, retry logic, TLS
  requirements, and monitoring. Use when designing architecture or solving
  production concerns.
---

# MPP Development Patterns

## Before writing code

**Fetch live docs**:
- Specification: Fetch `https://paymentauth.org/` for canonical security and encoding requirements
- IETF draft: Web-search `site:datatracker.ietf.org draft-ryan-httpauth-payment` for the latest RFC draft
- Stripe docs: Fetch `https://docs.stripe.com/payments/machine/mpp` for production integration patterns
- SDK: Web-search `site:npmjs.com mppx` for error handling and retry APIs

## Pattern: HMAC Challenge Binding

The 32-byte `secretKey` is the server's core security primitive:

- Every challenge ID is HMAC-bound to the secret key
- Prevents challenge forgery — attackers cannot create valid challenges without the key
- Prevents replay attacks — each challenge is unique and bound to the request context
- Generate with `openssl rand -hex 32`
- Rotate periodically and support key rollover

```typescript
const mppx = Mppx.create({
  secretKey: process.env.MPP_SECRET_KEY,  // 32-byte hex
  methods: [/* ... */],
});
```

## Pattern: Replay Protection

Single-use proof semantics prevent double-payment:

- Each credential can only be used once
- Server must track consumed credentials (at least until expiration)
- Atomic verification — check + consume in a single operation
- Use database transactions or atomic operations for credential tracking
- For high-throughput: use in-memory stores (Redis) with TTL matching challenge expiration

## Pattern: Transport Security

MPP mandates TLS 1.2+ (TLS 1.3 recommended):

- All endpoints must serve over HTTPS (port 443)
- `Cache-Control: no-store` on all responses containing credentials
- Never log plaintext credentials or payment proofs
- Credentials are treated as sensitive bearer tokens

## Pattern: JSON Canonicalization

RFC 8785 canonical JSON is required for deterministic encoding:

- Challenges must use canonical JSON before base64url encoding
- Keeps challenges under 8KB (server-side)
- Clients must handle minimum 4KB challenges
- Use a library for RFC 8785 compliance rather than manual JSON serialization

## Pattern: Error Handling

MPP uses RFC 9457 Problem Details for error responses:

```json
{
  "type": "https://paymentauth.org/problems/payment-required",
  "status": 402,
  "detail": "Payment is required.",
  "challengeId": "..."
}
```

**Error types**:
- `payment-required` — Normal challenge, no payment attempted yet
- `verification-failed` — Invalid proof of payment
- `payment-expired` — Challenge or credential expired
- `malformed-credential` — Cannot parse the credential

**Client retry strategy**:
- `payment-required` — Normal flow, fulfill and retry
- `verification-failed` — Do NOT retry with same credential (likely invalid)
- `payment-expired` — Request a fresh challenge
- `malformed-credential` — Fix credential encoding, do not retry blindly

## Pattern: Receipt Validation

The `Payment-Receipt` header proves delivery:

- Contains payment status, method, timestamp, reference ID
- Clients should store receipts for accounting and disputes
- Servers should generate receipts atomically with resource delivery
- Receipts serve as proof in billing reconciliation

## Pattern: Rate Limiting

Even with payments, implement rate limiting:

- Prevents abuse from clients with large wallets
- Protects upstream resources from overload
- Return 429 with `Retry-After` header when exceeded
- Client-side: honor `Retry-After`, add jitter

## Pattern: Amount Safety

- All amounts as strings representing the smallest currency unit
- Never use floating-point for monetary calculations
- Validate amounts on both client and server
- Reject negative or zero amounts
- Verify amount matches the challenged amount in the credential

## Pattern: Secret Management

- `MPP_SECRET_KEY` — 32-byte hex, rotate periodically
- `STRIPE_SECRET_KEY` — Stripe API key, never in code
- `WALLET_PRIVATE_KEY` — Crypto wallet key, use key management service
- Never commit secrets to version control
- Use `.env` files for development, secrets manager for production
- Implement key rotation without downtime

## Pattern: Monitoring & Observability

- Log every payment challenge issued (without sensitive data)
- Track payment success/failure rates per method
- Monitor challenge expiration rates (too many = too short TTL)
- Alert on verification failure spikes (potential attack)
- Track revenue per endpoint for pricing optimization
- Monitor Tempo chain health and Stripe API availability
- Dashboard payment method distribution

## Pattern: Testing

- Use Tempo testnet for development (not mainnet)
- Use Stripe test mode keys and test card tokens
- Test the full 402 flow end-to-end
- Test challenge expiration handling
- Test replay rejection
- Test with multiple payment methods simultaneously
- Load test to verify payment verification throughput

## Pattern: Caching

- Service discovery responses (`/openapi.json`, `/llms.txt`) — cache aggressively
- Payment challenges — NEVER cache (time-bound, single-use)
- Credentials — NEVER cache (`Cache-Control: no-store`)
- Upstream API responses (for proxies) — cache if idempotent and appropriate

Fetch the latest MPP specification and IETF draft for current security requirements, encoding rules, and best practices before implementing.
