---
name: mpp-conformance
description: Validate MPP implementations against the specification — verify HTTP 402 challenge-response compliance, header formats, payment method correctness, service discovery, and production readiness. Use when auditing an MPP integration or preparing for production launch.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
disable-model-invocation: true
---

# MPP Conformance & Production Readiness

## Before writing code

**Fetch live docs**:
1. Fetch `https://paymentauth.org/` for the canonical specification requirements
2. Fetch `https://datatracker.ietf.org/doc/draft-ryan-httpauth-payment/` for the IETF draft compliance requirements
3. Web-search `site:docs.stripe.com payments machine mpp production` for Stripe production readiness
4. Web-search `site:paymentauth.org draft-payment-discovery` for service discovery compliance

## Protocol Compliance Checklist

### HTTP 402 Response

- [ ] Returns `402 Payment Required` status code for unpaid requests
- [ ] Includes `WWW-Authenticate: Payment <base64url-challenge>` header
- [ ] Challenge contains required fields: `id`, `realm`, `method`, `intent`, `request`
- [ ] Challenge JSON is RFC 8785 canonicalized before base64url encoding
- [ ] Challenge size under 8KB
- [ ] Error body follows RFC 9457 Problem Details format

### Authorization Header

- [ ] Accepts `Authorization: Payment <base64url-credential>` header
- [ ] Parses credential correctly (base64url decode → JSON)
- [ ] Validates payment proof against the payment method
- [ ] Returns appropriate error for invalid credentials

### Payment-Receipt Header

- [ ] Returns `Payment-Receipt: <base64url-receipt>` on successful payment
- [ ] Receipt contains: status, method, timestamp, reference
- [ ] Receipt is delivered atomically with the resource

### Challenge Binding

- [ ] Uses 32-byte secret key for HMAC challenge binding
- [ ] Challenge IDs are unique and non-guessable
- [ ] Challenges have expiration timestamps
- [ ] Expired challenges are rejected
- [ ] Each challenge can only be consumed once (replay protection)

### Transport Security

- [ ] TLS 1.2+ on all endpoints (TLS 1.3 recommended)
- [ ] HTTPS only (port 443)
- [ ] `Cache-Control: no-store` on responses with credentials
- [ ] No plaintext credential logging

### Payment Methods

- [ ] At least one payment method configured
- [ ] Tempo: correct chain ID (4217), valid USDC contract address, valid recipient
- [ ] Stripe: valid API key, correct SPT handling
- [ ] Payment verification is atomic (no partial states)

### Service Discovery

- [ ] `GET /openapi.json` returns valid OpenAPI 3.x document
- [ ] `x-service-info` extension present with categories and docs
- [ ] `x-payment-info` extension on each payable operation
- [ ] All payable operations declare `402` response
- [ ] OpenAPI document under 64 KB
- [ ] `Cache-Control: max-age=300` on discovery endpoints
- [ ] `llms.txt` available with service description

### Error Handling

- [ ] `payment-required` for initial challenges
- [ ] `verification-failed` for invalid proofs
- [ ] `payment-expired` for expired challenges/credentials
- [ ] `malformed-credential` for unparseable credentials
- [ ] All errors include RFC 9457 `type` URLs

## Production Readiness Checklist

### Security

- [ ] Secret key stored in environment variable or secrets manager
- [ ] No hardcoded Stripe keys, wallet keys, or SPT tokens
- [ ] Key rotation strategy documented
- [ ] Rate limiting implemented
- [ ] DDoS protection (Cloudflare, AWS Shield, etc.)

### Monitoring

- [ ] Payment success/failure metrics collected
- [ ] Challenge issuance rate tracked
- [ ] Revenue per endpoint dashboarded
- [ ] Alert on verification failure spikes
- [ ] Tempo chain health monitored (if using Tempo)
- [ ] Stripe API availability monitored (if using Stripe)

### Reliability

- [ ] Health check endpoint (outside payment gate)
- [ ] Graceful degradation if payment provider is down
- [ ] Credential store (Redis/DB) for replay protection has failover
- [ ] Load tested with expected traffic volume

### Operations

- [ ] Deployment does not interrupt active payment sessions
- [ ] Secret key rotation does not invalidate in-flight challenges
- [ ] Refund process documented and tested
- [ ] Billing reconciliation process defined

Fetch the latest specification and IETF draft for any newly added compliance requirements before running conformance checks.
