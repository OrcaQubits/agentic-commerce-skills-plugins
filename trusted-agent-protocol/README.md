# Trusted Agent Protocol

Implement TAP merchant recognition, HTTP request signatures, trusted key management, consumer/payment binding checks, and offline cryptographic fixtures.

This development plugin includes an expert agent, 6 skills, an advisory secret hook, and executable local fixtures. Integration skills fetch current documentation; fixtures are pinned. See [source baseline and coverage](audit/source-baseline.md).

## Install and use

From this repository:

```text
claude --plugin-dir ./trusted-agent-protocol
```

Or register the repository marketplace and install `trusted-agent-protocol@agentic-commerce`. Invoke `/trusted-agent-protocol:tap-setup` or ask the `tap-expert` agent for an implementation review.

Converted bundles live under `dist/<platform>/trusted-agent-protocol`. Each bundle contains its own scripts, baseline, and evaluations. Locate the plugin root by walking upward from the installed skill to `scripts/test_conformance.py`; this also handles Antigravity's extra directory. Skills-only installers may omit executable resources: use the full bundle for conformance work.

## Skills (6)

| Skill | Purpose |
| --- | --- |
| `tap-setup` | Choose a TAP merchant integration profile and establish explicit trust configuration. |
| `tap-request-signatures` | Implement and test TAP HTTP signatures with explicit covered-component policy. |
| `tap-merchant-verification` | Integrate TAP verification and replay protection into a merchant request path. |
| `tap-key-management` | Design trusted TAP key lookup, rotation, revocation, and caching. |
| `tap-consumer-payment-binding` | Verify TAP consumer and payment-container signatures and their request bindings. |
| `tap-conformance` | Run local TAP cryptographic and replay fixtures and explain supported profile coverage. |

## Run the fixtures

Run from the plugin root. Python 3.11+ is required; the x402 SDK fixture additionally needs Node 22+ and npm. Dependency installation requires network access; fixture execution does not contact a facilitator or key service.

```text
python -m venv <temporary-venv>
# Activate that environment using your shell's activation command.
python -m pip install -r scripts/requirements-verifier.txt
python scripts/test_conformance.py
python scripts/make_fixture.py <temporary-fixture-directory> --bindings
python scripts/verify_request.py <temporary-fixture-directory>/capture.json <temporary-fixture-directory>/trust.json --replay-db <temporary-fixture-directory>/replay.db
```

The generator writes only a signed capture and public trust file; the private key stays in memory. Captures expire after two minutes. Repeating a successful capture against the same SQLite replay database must fail. `--tag agent-payer-auth` selects payment intent. `--profile tap-minimum` is an explicit reduced-coverage diagnostic mode. The default `merchant-strict` requires method/target and body-integrity coverage. SQLite is a single-host example; production hosts need a shared atomic replay store.

## Coverage

Read audit/source-baseline.md before using the local verifier. It implements a bounded Ed25519 recognition profile and an explicitly configured synthetic ordered-JSON container fixture; it does not certify Visa interoperability or validate identity tokens. The default merchant-strict profile adds signed method/target/body requirements beyond the TAP minimum. Do not infer TAP from a public JWKS, bypass merchant authorization, fetch a key URL from an untrusted keyid, or trust uncovered fields.

Trust configuration lists allowed authorities and key IDs with provider identity, public PEM, activation, expiry, and revocation state. No remote key fetch is implemented. Container checks require `binding_profile: ordered-json-ed25519-fixture-v1`; otherwise supplied containers are rejected. Identity JWTs require separate issuer/audience/expiry verification. Application authorization always remains false in fixture output.

## Structure

- `.claude-plugin/plugin.json`: source manifest.
- `agents/tap-expert.md`: expert instructions.
- `skills/`: implementation workflows.
- `hooks/`: advisory secret detection; platform hook availability varies.
- `scripts/`: validators, fixtures, dependency manifests.
- `audit/source-baseline.md`: exact revisions and coverage.
- `evals/scenarios.json`: runtime evaluation prompts.

## Attribution and references

These original fixtures are informed by public specifications. They are not vendor certifications or copied production services.

- [Official reference 1](https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications)
- [Official reference 2](https://github.com/visa/trusted-agent-protocol)
- [Official reference 3](https://www.rfc-editor.org/rfc/rfc9421)

Runtime evidence and unavailable platform checks are recorded in the repository's `docs/plans/commerce-implementation-validation.md`.
