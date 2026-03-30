---
name: ap2-vdc-framework
description: >
  Implement the AP2 Verifiable Digital Credentials (VDC) framework —
  tamper-evident, cryptographically signed credentials that form the trust
  foundation for agentic payments. Use when working with the overall VDC
  architecture, credential issuance, verification, and holder binding.
---

# AP2 Verifiable Digital Credentials (VDC) Framework

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for the VDC framework specification
2. Fetch `https://ap2-protocol.org/topics/core-concepts/` for VDC conceptual overview
3. Web-search `site:github.com google-agentic-commerce AP2 src/ap2/types mandate` for VDC type definitions
4. Web-search `ap2 protocol verifiable digital credentials VDC` for community guides

## Conceptual Architecture

### What VDCs Are

Verifiable Digital Credentials (VDCs) are **tamper-evident, portable, and cryptographically signed digital objects** that serve as the trust building blocks for AP2 transactions. They provide:
- **Non-repudiation** — Signed credentials prove who authorized what
- **Tamper evidence** — Any modification invalidates the signature
- **Portability** — Credentials can be passed between agents and systems
- **Selective disclosure** — Only necessary data is revealed to each party

### VDC Credential Format

AP2 VDCs use the **SD-JWT with Key Binding (+kb)** format, enabling selective disclosure and cryptographic holder binding.

JSON payloads are canonicalized using **JCS (RFC 8785)** before signing to ensure deterministic serialization.

### Three VDC Types in AP2

1. **Cart Mandate** — Human-present authorization for a specific cart/transaction
2. **Intent Mandate** — Human-not-present pre-authorization with constraints
3. **Payment Mandate** — Payment ecosystem visibility into agentic transaction context

### VDC Lifecycle

```
1. Creation     → Mandate generated (by Merchant for Cart, by SA for Intent)
2. Signing      → User signs with hardware-backed device key
3. Presentation → Mandate presented to verifying party
4. Verification → Signature and contents validated
5. Usage        → Mandate used to authorize payment
6. Archival     → Mandate stored for dispute resolution/audit
```

### Credential Structure

Every VDC follows a common structure:
- **Contents** — The actual data (transaction details, intent, payment info)
- **Signatures** — Cryptographic signatures from relevant parties
- **Metadata** — Timestamps, IDs, version information

### Trust Model

The VDC trust model involves:
- **Issuer** — Entity that creates and signs the credential (Merchant for Cart, SA for Intent)
- **Holder** — Entity that holds and presents the credential (Shopping Agent)
- **Verifier** — Entity that validates the credential (Payment Processor, Network)
- **Subject** — The user whose authorization the credential represents

### W3C Alignment

AP2 VDCs align with W3C standards:
- **W3C Payment Request API** — Mandate details follow Payment Request structure
- **W3C Verifiable Credentials** — Mandates are expressed as W3C Verifiable Credentials

Cart Mandates receive both **merchant authorization** (a detached JWS JWT) and **user signature** (hardware-backed device key), forming a dual-authorization model.

### Verification Process

To verify a VDC:
1. **Check signature validity** — Verify cryptographic signatures
2. **Check signer identity** — Confirm the signer is who they claim
3. **Check contents integrity** — Ensure contents haven't been modified
4. **Check temporal validity** — Verify TTL hasn't expired (for Intent Mandates)
5. **Check holder binding** — Confirm the presenter is authorized

### Best Practices

- Always verify VDC signatures before trusting the contents
- Store VDCs with their signatures for audit and dispute resolution
- Use hardware-backed keys for user signatures when available
- Implement proper key rotation and management
- Log all VDC creation and verification events
- Never expose raw VDC signing keys to Shopping Agents
- Test with both valid and invalid signatures to ensure verification works

Fetch the specification for exact VDC schemas, signature formats, and verification algorithms before implementing.
