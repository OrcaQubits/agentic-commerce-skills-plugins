---
name: ap2-cryptographic-signing
description: >
  Implement AP2 cryptographic signing — hardware-backed user signatures,
  merchant entity signatures, VDC integrity, key management, and attestation
  flows. Use when building the signing, verification, and key management
  components of AP2 mandates.
---

# AP2 Cryptographic Signing

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for cryptographic signing requirements
2. Fetch `https://ap2-protocol.org/topics/privacy-and-security/` for security architecture
3. Web-search `site:github.com google-agentic-commerce AP2 signature mandate` for signing implementations
4. Web-search `ap2 protocol VDC signing cryptographic hardware-backed` for community guides

## Conceptual Architecture

### Why Cryptographic Signing Matters

AP2's core innovation is **verifiable intent** — cryptographic proof that:
- The user authorized a specific transaction
- The merchant committed to specific terms
- Neither party can deny what they agreed to (non-repudiation)
- No intermediary tampered with the mandate (integrity)

### VDC Credential Format

AP2 VDCs use the **SD-JWT with Key Binding (+kb)** format, enabling selective disclosure and cryptographic holder binding.

### Supported Signing Algorithms

AP2 supports **ECDSA** with the following algorithm/curve combinations:
- **ES256** — ECDSA with P-256 curve
- **ES384** — ECDSA with P-384 curve
- **ES512** — ECDSA with P-521 curve

### JSON Canonicalization (JCS)

Before signing, JSON payloads are canonicalized using **JCS (RFC 8785)** to produce a deterministic byte representation. This ensures that logically equivalent JSON objects produce the same signature regardless of key ordering or whitespace.

### Detached JWS for Merchant Authorization

The `merchant_authorization` field on Cart Mandates uses **Detached JWS** format:
```
<base64url-header>..<base64url-signature>
```
Note the **double dots** — the payload is omitted from the JWS because it is the JCS-canonicalized CartContents, which the verifier already possesses.

### JWT Header and Payload Requirements

**JWT header** MUST include:
- `alg` — The signing algorithm (ES256, ES384, or ES512)
- `kid` — Key identifier for the signing key

**JWT payload** for merchant_authorization includes:
- `iss` — Issuer (merchant identifier)
- `aud` — Audience
- `iat` — Issued-at timestamp
- `exp` — Expiration timestamp
- `jti` — Unique JWT identifier
- `cart_hash` — Hash of the canonicalized cart contents

### Two Types of Signatures

#### User Signatures
- **Hardware-backed device keys** — Generated and stored in secure hardware (TPM, Secure Enclave)
- **In-session authentication** — User must authenticate (biometric, PIN) at signing time
- **Attestation** — Device provides cryptographic proof of the signing context
- **Purpose** — Proves the user explicitly authorized the transaction

#### Merchant Signatures
- **Entity-level** — Signed by the merchant organization, not by the AI agent
- **Fulfillment guarantee** — Commits the merchant to the stated terms
- **Key management** — Organizational-level key infrastructure
- **Purpose** — Proves the merchant committed to specific products/prices

### What Gets Signed

| VDC | Signed By | What's Covered |
|-----|-----------|---------------|
| Cart Mandate | Merchant + User | Exact items, prices, totals, payment methods |
| Intent Mandate | User | Shopping constraints, categories, intent, TTL |
| Payment Mandate | User | Payment method selection, transaction amount |

### Trusted Device Surface

The user signing step (especially for Cart and Payment Mandates) involves:
1. Shopping Agent triggers redirect to trusted device surface
2. User's device displays the transaction summary
3. User authenticates (biometric, PIN, passkey)
4. Device generates signature using hardware-backed key
5. Attestation object created proving the signing context
6. Signature + attestation returned to Shopping Agent

This is a **load-bearing security step** — the agent cannot bypass it.

### Signature Verification

Verifiers check:
1. **Signature validity** — Cryptographic verification against the signer's public key
2. **Signer identity** — Public key belongs to the claimed entity
3. **Content integrity** — Signed content matches the mandate contents
4. **Temporal validity** — Signature was created within acceptable timeframe
5. **Attestation validity** — Device attestation is genuine (for user signatures)

### Non-Repudiation

Signed mandates provide non-repudiation for disputes:
- User can't deny they authorized a purchase (their device signed it)
- Merchant can't deny their offer terms (their entity signed it)
- The cryptographic evidence is deterministic, not inferred

### Key Management Considerations

- **User keys**: Managed by the user's device secure hardware
- **Merchant keys**: Managed at the organization level (HSM or key vault)
- **Key rotation**: Support for rotating keys without breaking verification
- **Key revocation**: Ability to revoke compromised keys
- **Certificate chain**: Trust chain from key to identity

### Man-in-the-Middle Prevention

VDC signatures prevent MITM attacks:
- An attacker cannot modify mandate contents without invalidating signatures
- End-to-end integrity from creation to verification
- Digital signatures cover the complete mandate payload

### Best Practices

- Always use hardware-backed keys for user signatures when available
- Never store private signing keys in agent code or config
- Implement proper key rotation procedures
- Verify all signatures before trusting mandate contents
- Store signed mandates with signatures for dispute resolution
- Use standard cryptographic libraries — don't implement crypto primitives
- Test with both valid and invalid signatures
- Handle signature verification failures gracefully with clear errors
- Log all signing and verification events for audit

Fetch the specification for exact signature formats, supported algorithms, attestation requirements, and verification procedures before implementing.
