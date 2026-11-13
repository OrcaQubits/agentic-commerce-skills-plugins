---
name: tap-request-signatures
description: Implement and test TAP HTTP signatures with explicit covered-component policy.
---

# tap-request-signatures

Implement and test TAP HTTP signatures with explicit covered-component policy.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Fetch current TAP signature fields and the signature library's API; pin a tested version and algorithm spelling for the chosen profile.
2. Use the library for parsing, canonicalization, signing, and verification. Do not rebuild an HTTP signature base with ad hoc string concatenation.
3. Require the chosen components and signature parameters, enforce timestamps and allowed intent tags, and reconstruct the external URL only from trusted configuration.
4. Test changes to each covered component. Compare the selected profile's requirements with actual signature coverage and identify every field the application uses without cryptographic protection.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Profile-specific verification code, signed-field inventory, and tamper tests.

## Scope

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Example task

A valid authority/path signature is replayed with a different method. Explain the coverage gap and implement merchant-strict verification.
