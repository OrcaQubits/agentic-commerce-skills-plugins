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
1. Fetch `https://ap2-protocol.org/ap2/specification/` for cryptographic signing requirements
2. Fetch `https://ap2-protocol.org/ap2/security_and_privacy_considerations/` for security architecture
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

### Merchant authorization envelope

> **Version-sensitive.** The exact envelope for the merchant's signature has changed across AP2 releases — earlier releases used a detached JWS over canonicalized cart contents; current releases carry a merchant-signed checkout JWT plus a checkout hash inside the mandate. **Fetch `https://ap2-protocol.org/ap2/checkout_mandate/` and implement what it says.** Everything below is the durable shape, not a schema.

The durable pattern, whatever the envelope:

- The merchant signs a **canonical** representation of the checkout, so serialization differences cannot change what was signed.
- A **hash** identifies the specific checkout and ties the signature to it.
- The verifier can reconstruct what was signed from data it already holds, rather than trusting a payload the agent supplies.

**Header claims** must carry, at minimum:
- the signing algorithm
- a key identifier — the verifier has to know *which* key signed, and key rotation depends on this

**Payload claims** typically carry issuer, audience, issued-at, expiry, a unique identifier, and the checkout hash. Confirm the exact claim names and the permitted algorithms against the live spec before implementing verification.

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

| Mandate | Signed by | What's covered |
|---------|-----------|----------------|
| Checkout Mandate (closed) | Merchant + User | Exact items, prices, totals, payment methods |
| Checkout Mandate (open) | User, then Agent on binding | Shopping constraints (allowed merchants, line items), expiry |
| Payment Mandate | User | Payment method selection, transaction amount |

The open form is where the former "Intent Mandate" lives — the user signs the constraints, the agent later signs the binding to a real transaction, and **both signatures are retained** as the authorization chain.

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
