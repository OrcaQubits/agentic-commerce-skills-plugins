---
name: x402-http-payments
description: Implement x402 HTTP payment challenges and paid-resource handling.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-http-payments

Implement x402 HTTP payment challenges and paid-resource handling.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Locate protected routes and identify their HTTP methods, resource identities, prices, and side effects.
2. Fetch the current HTTP transport specification; implement the version's challenge, payment-payload, and settlement-response locations exactly.
3. Validate advertised requirements before signing. Reject resource, recipient, asset, network, or budget mismatches and bound untrusted input sizes.
4. Follow the selected payment flow's execution order. Test verification rejection, settlement failure, CORS exposure, and resource delivery independently.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Middleware/client changes, supported transport/version statement, and positive/negative fixtures.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

An HTML error page returns 402 before a valid paid endpoint. Diagnose it without reporting MPP or submitting a payment.
