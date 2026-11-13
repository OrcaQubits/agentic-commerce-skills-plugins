---
name: x402-setup
description: Set up an x402 client, resource server, or facilitator integration.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-setup

Set up an x402 client, resource server, or facilitator integration.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Identify the role, runtime, transport, scheme, network, asset, recipient, and deployment constraints from the repository.
2. Fetch the official core specification and relevant SDK package exports; record exact versions in the implementation.
3. Choose one supported scheme/network pair and scaffold its explicit configuration. Keep secrets outside source and require spending policy before wallet access.
4. Run the bundled wire and SDK fixtures before substituting a real facilitator; document mocked versus live behavior.

## Validation and output

Run `scripts/test_conformance.py` for the bundled core fixture. The CLI inspector
expects an HTTP capture (`status`, `headers`, optional `body`) or an MCP result;
do not pass raw `scripts/fixtures/challenge.json` directly as an HTTP capture.

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Role diagram, pinned dependency/config changes, fixture commands, and remaining deployment prerequisites.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

A developer needs a paid EVM API but has no funded wallet. Produce a local implementation and validation approach without spending.
