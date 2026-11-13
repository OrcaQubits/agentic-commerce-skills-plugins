---
name: x402-spend-policy
description: Enforce explicit payment limits before constructing an x402 payment payload.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-spend-policy

Enforce explicit payment limits before constructing an x402 payment payload.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Obtain the user-approved per-operation and aggregate limits, allowed resources, recipients, networks, assets, and time window.
2. Evaluate every advertised alternative against policy before selecting or signing; compare atomic-unit amounts without floating point.
3. Use atomic reserve/commit/release accounting for aggregate budgets. Preserve reservations while settlement is unknown and enforce concurrency limits.
4. Test manipulated amounts, alternate recipients, changed resources, concurrent requests, and unsupported flows. The bundled choose_payment helper demonstrates only a single-request guard.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Policy model, enforcement point before signing, concurrency tests, and reconciliation behavior.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

Two simultaneous paid requests each fit a per-call limit but together exceed the daily budget. Design the atomic rejection path.
