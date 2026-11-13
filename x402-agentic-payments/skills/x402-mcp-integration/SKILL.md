---
name: x402-mcp-integration
description: Add x402 payment negotiation to MCP tools using the current MCP transport.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# x402-mcp-integration

Add x402 payment negotiation to MCP tools using the current MCP transport.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Identify the paid tool, request arguments, side effects, and the MCP transport used by the application.
2. Fetch the MCP transport specification and current SDK guide. Keep tool-level payment negotiation distinct from HTTP authentication.
3. Produce the required tool error with consistent structured and text challenge representations. Read and write payment metadata using documented keys.
4. Bind retries to the intended tool operation and original arguments; preserve caller authorization and prevent duplicate business side effects.

## Validation and output

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Tool integration, transport-specific fixtures, and a clear distinction between tool errors and JSON-RPC errors.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

A paid MCP tool has conflicting structuredContent and text challenges. Reject the ambiguity and show a valid fixture.
