# trusted-agent-protocol Rules

## tap-expert

Implement TAP merchant recognition, HTTP request signatures, trusted key management, consumer/payment binding checks, and offline cryptographic fixtures. Fetches official documentation before implementation.

# Trusted Agent Protocol Expert

## Live Documentation Rule

Before writing integration code, fetch the official specification and SDK documentation for the selected integration version. Record the exact revision, SDK/library versions, and retrieval date. Resolve schemas, identifiers, algorithms, and limits from those references. If current documentation cannot be fetched, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection; do not generate new integration code from an unverified snapshot.

- https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications
- https://github.com/visa/trusted-agent-protocol
- https://www.rfc-editor.org/rfc/rfc9421

Executable fixtures deliberately use the revisions in `audit/source-baseline.md`. Updating a skill's live guidance does not silently update that test baseline.

## Conceptual Architecture

An HTTP request signature proves integrity only for its covered components. A configured trusted key source associates a key with a provider. Consumer recognition and payment containers have separate signatures and request bindings. Cryptographic validity, provider trust, consumer identity, business authorization, and payment acceptance are separate decisions.

## Implementation Workflow

1. Inspect the application's existing request path, trust/payment boundaries, test runner, and deployment conventions.
2. Choose the smallest supported profile that meets the user's concrete use case and document its assumptions.
3. Fetch official implementation references, inspect actual library exports, and pin the tested versions.
4. Implement the successful path with explicit failure and unknown-outcome handling.
5. Exercise synthetic positive, negative, and concurrency fixtures before adding real credentials or external services.
6. Report changed files, commands run, observed results, supported combinations, and unresolved interoperability requirements.

## Coverage and Boundaries

Read `audit/source-baseline.md` for the local verifier's fixed profiles, algorithms, and synthetic-container limitations. Fetch the current provider profile for a new integration; do not promote fixture choices into protocol requirements. Signature validity, provider trust, identity validation, and authorization remain separate decisions. Never trust uncovered fields or a key source selected solely by an untrusted request.

## Skills

- `tap-setup`: Choose a TAP merchant integration profile and establish explicit trust configuration.
- `tap-request-signatures`: Implement and test TAP HTTP signatures with explicit covered-component policy.
- `tap-merchant-verification`: Integrate TAP verification and replay protection into a merchant request path.
- `tap-key-management`: Design trusted TAP key lookup, rotation, revocation, and caching.
- `tap-consumer-payment-binding`: Verify TAP consumer and payment-container signatures and their request bindings.
- `tap-conformance`: Run local TAP cryptographic and replay fixtures and explain supported profile coverage.

## Installed Resources

Locate this plugin's root from the installed agent/skill location by walking up to the directory containing `scripts/test_conformance.py` and `audit/source-baseline.md`. Read the plugin README for executable commands. Do not assume a source checkout or another plugin is installed.
