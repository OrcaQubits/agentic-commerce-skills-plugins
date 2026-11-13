---
name: x402-facilitators
description: >
  Integrate facilitator capabilities, verification, settlement, and
  reconciliation.
---

# x402-facilitators

Integrate facilitator capabilities, verification, settlement, and reconciliation.

## Before implementation

Inspect the relevant repository and reuse its request handling, configuration, and tests. Fetch official documentation before generating integration code:

- https://docs.x402.org/
- https://github.com/x402-foundation/x402
- https://docs.x402.org/guides/mcp-server-with-x402

Record the specification revision, retrieval date, and SDK/library versions in generated code or its accompanying documentation. Fetch exact schemas, identifiers, algorithms, limits, and SDK methods for the selected integration version; do not infer them from bundled fixtures. If current references are unavailable, explain the gap and limit work to conceptual guidance or explicitly versioned local fixture inspection. Do not generate new integration code from an unverified snapshot.

## Workflow

1. Fetch the facilitator interface and inspect the actual supported scheme/network and extension response.
2. Match server configuration to advertised capabilities; reject unsupported combinations before serving a misleading payment gate.
3. Separate verification from settlement and record an application operation identifier before side effects.
4. Model rejection, timeout, and unknown settlement outcomes explicitly. Consult payment-identifier extension semantics before allowing a retry; verification success alone is not a receipt.

## Validation and output

Fetch the [payment identifier extension](https://docs.x402.org/extensions/payment-identifier)
before describing retry guarantees. Expiration of a payment authorization alone
does not establish that an earlier settlement failed: check the facilitator's
documented status/receipt mechanism and the relevant ledger's finality rules.
Keep ambiguous operations reserved for reconciliation; do not release funds or
construct another payment solely because a timeout or `validBefore` elapsed.

Exercise a successful case and failures that cross the relevant payment/trust boundary. Use synthetic data and report the actual result of each command. Do not label an unrun check as passed.

Deliver: Capability checks, state transitions, redacted operational evidence, and failure-path tests.

## Scope

The bundled tests have deliberately fixed coverage: read `audit/source-baseline.md` for their versions and supported combinations. Those pins are test inputs, not defaults for new integrations. Structural validity, payment authorization, and settlement are separate observations. Enforce explicit spending policy and reconcile uncertain outcomes before another payment.

## Example task

The facilitator times out after receiving a settle request. Explain and implement reconciliation without another automatic payment.
