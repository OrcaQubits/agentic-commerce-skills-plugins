---
name: tap-setup
description: >
  Choose a TAP merchant integration profile and establish explicit trust
  configuration.
---

# tap-setup

Choose a TAP merchant integration profile and establish explicit trust configuration.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Determine whether verification belongs at the merchant application, edge, or both and identify the expected browsing/payment interaction.
2. Fetch current merchant specifications, RFC 9421, and the relevant provider profile; record any differences between examples and normative requirements.
3. Define trusted providers, public-key distribution, external request URL reconstruction, replay storage, and allowed algorithms before enabling acceptance.
4. Start with local synthetic captures and the bundled verifier. Treat program enrollment and production key provisioning as separate deployment requirements.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Profile decision, trust configuration, local proof of behavior, and production prerequisites.

## Scope

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Example task

A merchant wants to accept TAP agents but has no provider enrollment or production keys. Set up an honest local development path.
