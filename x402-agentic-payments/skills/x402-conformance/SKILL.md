---
name: x402-conformance
description: Run x402 wire, MCP, policy, and mocked SDK interoperability fixtures.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-conformance

Run x402 wire, MCP, policy, and mocked SDK interoperability fixtures.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Locate this installed plugin root by walking upward from this skill until scripts/test_conformance.py exists; do not assume a fixed number of parents.
2. Read audit/source-baseline.md and run python scripts/test_conformance.py from that root.
3. Run python scripts/run_sdk_fixture.py from the plugin root when dependency downloads are available. It installs pinned packages in an isolated temporary directory.
4. Classify failures as envelope, policy, transport, SDK integration, or mocked settlement. State what remains untested; never call mocked settlement a live payment.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Commands, actual results, exact baseline versions, and explicit unsupported cases.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

Validate a captured 402 response and explain whether it proves that a payment will settle.
