---
name: tap-merchant-verification
description: Integrate TAP verification and replay protection into a merchant request path.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# tap-merchant-verification

Integrate TAP verification and replay protection into a merchant request path.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Map request capture, trusted proxy handling, provider lookup, cryptographic verification, replay consumption, and business authorization.
2. Reject ambiguous headers and untrusted key sources. Require all checks on supplied consumer/payment bindings before marking a request verified.
3. Consume a nonce atomically only after verification; scope replay identity to the trusted provider so key rotation cannot bypass it.
4. Keep denial outcomes separate from application authorization. Test concurrent replay, unavailable trust data, wrong intent, and altered requests.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Middleware integration, replay store semantics, failure behavior, and concurrency tests.

## Scope

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Example task

Six workers receive the same signed request concurrently. Ensure exactly one replay check succeeds.
