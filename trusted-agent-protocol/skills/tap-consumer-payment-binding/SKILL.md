---
name: tap-consumer-payment-binding
description: Verify TAP consumer and payment-container signatures and their request bindings.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# tap-consumer-payment-binding

Verify TAP consumer and payment-container signatures and their request bindings.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Fetch the exact provider container format, serialization, algorithm, key relationship, and nonce-binding rules; resolve ambiguity before integration.
2. Verify the outer request and each relevant container independently, then compare signed nonce and key identity with the request.
3. Validate an identity token under its own issuer/audience/expiry rules before using it as identity. Container-signature validity alone does not perform that validation.
4. Reject changed payloads and cross-request substitution. Use only synthetic identifiers and no real payment credentials in tests. The bundled ordered-JSON container profile is a local fixture agreement, not a production Visa container implementation.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Provider-specific serialization decision, independent signature/binding checks, and substitution tests.

## Scope

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Example task

A payment container has a valid signature but belongs to a different request nonce. Reject its use for this checkout.
