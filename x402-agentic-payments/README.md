# x402 Agentic Payments

Implement and test x402 payment negotiation, facilitator integration, paid MCP tools, spending controls, and v1-to-v2 migration.

This development plugin includes an expert agent, 7 skills, an advisory secret hook, and executable local fixtures. Integration skills fetch current documentation; fixtures are pinned. See [source baseline and coverage](audit/source-baseline.md).

## Install and use

From this repository:

```text
claude --plugin-dir ./x402-agentic-payments
```

Or register the repository marketplace and install `x402-agentic-payments@agentic-commerce`. Invoke `/x402-agentic-payments:x402-setup` or ask the `x402-expert` agent for an implementation review.

Converted bundles live under `dist/<platform>/x402-agentic-payments`. Each bundle contains its own scripts, baseline, and evaluations. Locate the plugin root by walking upward from the installed skill to `scripts/test_conformance.py`; this also handles Antigravity's extra directory. Skills-only installers may omit executable resources: use the full bundle for conformance work.

## Skills (7)

| Skill | Purpose |
| --- | --- |
| `x402-setup` | Set up an x402 client, resource server, or facilitator integration. |
| `x402-http-payments` | Implement x402 HTTP payment challenges and paid-resource handling. |
| `x402-facilitators` | Integrate facilitator capabilities, verification, settlement, and reconciliation. |
| `x402-mcp-integration` | Add x402 payment negotiation to MCP tools using the current MCP transport. |
| `x402-spend-policy` | Enforce explicit payment limits before constructing an x402 payment payload. |
| `x402-conformance` | Run x402 wire, MCP, policy, and mocked SDK interoperability fixtures. |
| `x402-migration` | Migrate legacy x402 v1 integrations to the supported v2 core and transports. |

## Run the fixtures

Run from the plugin root. Python 3.11+ is required; the x402 SDK fixture additionally needs Node 22+ and npm. Dependency installation requires network access; fixture execution does not contact a facilitator or key service.

```text
python scripts/test_conformance.py
python scripts/run_sdk_fixture.py
python scripts/validate_challenge.py capture.json
python scripts/validate_challenge.py mcp-result.json --transport mcp
```

HTTP capture input is a JSON object with `status`, `headers`, and optional `body`. MCP input is the tool result object, not a JSON-RPC envelope. The inspector returns exit 0 only for a recognized structurally valid challenge. `scripts/fixtures/challenge.json` is a synthetic v2 core payload. The SDK runner installs its locked dependencies in a temporary directory with lifecycle scripts disabled and runs against a mocked facilitator.

## Coverage

The bundled inspector handles v2 core envelopes; it does not authenticate challenges or settle payments. The SDK fixture signs with a fresh synthetic key and mocks the facilitator. Production spending requires an atomic aggregate budget, recipient/resource allowlists, and reconciliation of uncertain outcomes. Never retry an uncertain payment automatically. Do not treat arbitrary HTTP 402 bodies as protocol evidence.

The single-request policy helper does not implement a daily budget ledger. SDK coverage is EVM `exact` authorization flow with the Base Sepolia network identifier and synthetic local keys; no funded wallet is used. Local signature verification and tampering are tested independently of the mocked facilitator. The settlement guard demonstrates operation deduplication and distinct settled/rejected/unknown states in one process; production requires durable atomic storage and reconciliation. Valid v2 schemes can be recognized without being executable by this fixture. MPP method semantics and JCS/challenge authentication remain unverified.

## Structure

- `.claude-plugin/plugin.json`: source manifest.
- `agents/x402-expert.md`: expert instructions.
- `skills/`: implementation workflows.
- `hooks/`: advisory secret detection; platform hook availability varies.
- `scripts/`: validators, fixtures, dependency manifests.
- `audit/source-baseline.md`: exact revisions and coverage.
- `evals/scenarios.json`: runtime evaluation prompts.

## Attribution and references

These original fixtures are informed by public specifications. They are not vendor certifications or copied production services.

- [Official reference 1](https://docs.x402.org/)
- [Official reference 2](https://github.com/x402-foundation/x402)
- [Official reference 3](https://docs.x402.org/guides/mcp-server-with-x402)

Runtime evidence and unavailable platform checks are recorded in the repository's `docs/plans/commerce-implementation-validation.md`.
