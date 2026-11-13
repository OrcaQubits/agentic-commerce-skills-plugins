---
name: x402-migration
description: Migrate legacy x402 v1 integrations to the supported v2 core and transports.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-migration

Migrate legacy x402 v1 integrations to the supported v2 core and transports.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Inventory legacy headers, response bodies, network names, SDK versions, and persisted payment/retry state.
2. Fetch both applicable version specifications and current SDK migration guidance before editing code.
3. Map changed envelope, transport, and network identifiers explicitly; maintain an intentional compatibility boundary rather than accepting every shape.
4. Add fixtures for old-client detection, supported new requests, malformed mixed versions, and uncertain in-flight payments; stage rollout with telemetry.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Migration map, compatibility policy, code changes, and rollout/rollback criteria.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

A client still reads v1 body challenges and sends an old payment header. Produce a versioned migration with regression tests.
