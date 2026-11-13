---
name: tap-conformance
description: >
  Run local TAP cryptographic and replay fixtures and explain supported profile
  coverage.
---

# tap-conformance

Run local TAP cryptographic and replay fixtures and explain supported profile coverage.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Locate this installed plugin root by walking upward until scripts/test_conformance.py exists; read audit/source-baseline.md.
2. Create an isolated Python environment and install scripts/requirements-verifier.txt, then run python scripts/test_conformance.py from the plugin root.
3. For a manual exercise, run python scripts/make_fixture.py <temporary-output-directory> --bindings and verify the resulting capture with scripts/verify_request.py and a persistent --replay-db path.
4. Verify the first request succeeds and repetition fails. Report profile coverage, library versions, and identity-token/provider-enrollment limitations.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Actual positive/negative results, replay behavior, and a precise coverage statement.

## Scope

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Example task

Run the bundled TAP fixture and state whether it proves Visa approval or permission to charge a consumer.
