# Commerce fixes, x402, and Trusted Agent Protocol implementation plan

Status: implemented locally; see [validation evidence and remaining runtime limits](commerce-implementation-validation.md). No release has been published.

Prepared: 2026-11-13. Repository baseline: `30cd25c`.

## Outcome and scope

Ship two development plugins, `x402-agentic-payments` and `trusted-agent-protocol`, alongside targeted corrections to payment readiness, Shopify guidance, and plugin inventories. The new plugins should help developers implement and test real protocol behavior, with runnable examples and failure fixtures as well as skills.

The plugins have distinct responsibilities: x402 covers payment negotiation and settlement integration; Trusted Agent Protocol (TAP) covers agent recognition and verification of the applicable consumer/payment bindings. Existing AP2 skills remain responsible for AP2 mandates. TAP verification must not be presented as payment authorization, Visa approval, or certification.

This release does not require a hosted service, a wallet product, a new live MCP server, or additional commerce-platform plugins. MCP integration guidance belongs in the relevant skills. Do not introduce `.mcp.json` unless an actual supported server is shipped.

## Verified baseline

The canonical marketplace registers 16 plugins. Source inspection found 285 skill files, excluding generated distributions. `scripts/convert.py` reads `.claude-plugin/marketplace.json` and produces Gemini, Antigravity, Codex, OpenClaw, and Cursor distributions. Its resource copier already carries plugin-level `scripts/`, `audit/`, and `evals/` directories.

| Check run during planning | Result |
| --- | --- |
| `node scripts/validate_manifests.mjs` | Passed: 361 checks, 16 plugins |
| `python scripts/validate.py` | Passed: 3,414 checks, no warnings or errors |
| `python commerce-readiness/scripts/test_scoring.py` | Passed: 30 checks |
| `python commerce-readiness/scripts/test_mcp_server.py` | Unverified: the sandbox blocked localhost socket access with Windows error 10013 |

The MCP integration result is an environment limitation, not an established application defect. Re-run it in an environment that permits localhost sockets before release. The live Cursor schema check and a fresh distribution regeneration were not run as part of this planning baseline.

## Evidence driving the work

| Finding | Repository consequence |
| --- | --- |
| `commerce-readiness/scripts/probe_payments.py` treats any nonempty HTTP 402 body as MPP and stops at the first 402. | Replace the heuristic with bounded, protocol-aware challenge parsing and regression tests. |
| The README inventory omits Medusa and Saleor and has stale UCP, ACP, and AP2 skill counts. | Derive inventory checks from registered source plugins and correct the documentation. |
| x402 is now defined by a versioned core specification and separate transport specifications. | Build around an explicit supported version and transport matrix, rather than old header examples. See the [x402 v2 core](https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md) and [HTTP transport](https://github.com/x402-foundation/x402/blob/main/specs/transports-v2/http.md). |
| Official wallet skills already cover x402 wallet operations and monetization. | Focus this repository's new plugin on implementation, interoperability, failure handling, and conformance. Link to the [official wallet skills](https://github.com/coinbase/agentic-wallet-skills) where appropriate. |
| TAP publishes merchant-facing specifications and reference implementation material. | Ground the verification skills in the [Visa specifications](https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications) and [reference repository](https://github.com/visa/trusted-agent-protocol), distinguishing the protocol from program enrollment. |
| Shopify removed catalog/cart tools on `/api/mcp` and documents `/api/ucp/mcp` as their replacement. | Add focused Shopify UCP and migration skills, based on the [official migration guide](https://shopify.dev/docs/apps/build/storefront-mcp). |

The priority and packaging choices below are recommendations based on these findings. Upstream documentation on a moving branch is discovery evidence; executable fixtures must record immutable revisions before implementation is accepted.

## Delivery sequence

### 1. Correct payment readiness and establish source baselines

Files: `commerce-readiness/scripts/probe_payments.py`, a new `commerce-readiness/scripts/lib/payment_challenges.py`, `commerce-readiness/scripts/test_payments.py`, `commerce-readiness/audit/r5.md`, related readiness reporting tests, and `.github/workflows/validate.yml`.

- Replace the body-presence and substring checks with parsers for the pinned MPP Payment authentication challenge and x402 v2 HTTP challenge. Use the [MPP specification index](https://paymentauth.org/) to select and record the exact authentication specification revision.
- Decode bounded inputs; validate required fields and types; handle header names case-insensitively. Separate supported valid challenges, recognizable legacy/unsupported versions, malformed challenges, and unrelated 402 responses.
- Validate protocol structure independently of the schemes/networks supported by the example runtime. A structurally valid challenge for an unsupported scheme must not imply that the plugin can execute that scheme.
- Continue the bounded endpoint scan after an unrelated or malformed 402. Record which endpoints were checked and say when no supported challenge was observed there; do not claim exhaustive discovery of all paid resources.
- Preserve the existing one-point machine-payment surface check and R5 total of six. A valid supported MPP or x402 challenge can satisfy that check. Supporting both must not add points. Detect and report multiple advertised protocols independently.
- Keep shallow mode observational: no payment submission, wallet creation, signatures, or settlement. Preserve the existing URL/SSRF protections and network bounds.
- Keep report changes backward-compatible and test CLI and MCP result consistency. Select remediation links from detected evidence; do not recommend MPP as the only remedy for every unidentified 402. Activate the x402 skill link only after that plugin is registered in step 2.
- Correct MPP/x402 comparisons in `stripe-mpp/` and introductory x402 material in `ap2-agentic-payments/`. State protocol/version-specific differences and remove unsupported absolute claims about supported payment patterns.

Acceptance: valid fixtures pass; HTML/text error bodies, misleading authentication names, invalid JSON/base64, oversized payloads, and missing fields do not. A malformed first endpoint cannot hide a valid later endpoint. Existing scoring and catch-all protections still pass.

### 2. Add `x402-agentic-payments`

Create the standard manifest, `agents/x402-expert.md`, README, applicable secret-check hook, skills, and executable resources. Start at version `0.1.0`; follow existing manifest types, agent frontmatter, and hook interpreter fallback conventions.

| Skill | Deliverable |
| --- | --- |
| `x402-setup` | Choose client/server/facilitator roles, fetch current official references, and scaffold a version-pinned integration. |
| `x402-http-payments` | Implement HTTP negotiation and paid-resource handling with explicit version and transport requirements. |
| `x402-facilitators` | Integrate supported-scheme discovery, verification, settlement, and reconciliation of uncertain outcomes. |
| `x402-mcp-integration` | Integrate paid MCP operations using the documented transport and SDK behavior. |
| `x402-spend-policy` | Enforce explicit asset, network, recipient, resource, and spending constraints before signing. |
| `x402-conformance` | Run offline protocol fixtures and explain which properties were actually tested. |
| `x402-migration` | Identify legacy v1 assumptions and migrate to the supported v2 profile. |

Executable scope:

- Ship `scripts/validate_challenge.py` and `scripts/test_conformance.py`, with fixtures under `scripts/fixtures/`; keep challenge inspection independent of wallet credentials.
- Add a small SDK-backed client/server integration fixture for one documented v2 scheme/network combination, initially EVM `exact`, with mocked facilitator responses. Pin SDK versions and exercise negotiation, verification failure, successful settlement, rejected settlement, and uncertain settlement without sending funds.
- Test malformed transport data, unsupported versions, numeric amount representation, network identifiers, recipient/resource mismatch, and spending-policy rejection. Do not equate JSON validation with cryptographic verification or settlement success.
- Cover safe handling of retries and duplicate requests using the supported extension and facilitator semantics. Do not promise global idempotency or automatically re-pay an uncertain outcome. Consult the [payment identifier extension](https://docs.x402.org/extensions/payment-identifier).
- Include an MCP transport fixture derived from the [official MCP integration guide](https://docs.x402.org/guides/mcp-server-with-x402), rather than assuming HTTP headers transfer unchanged to every MCP transport.
- Put the source/version matrix in `audit/source-baseline.md` and realistic skill prompts with expected outcomes in `evals/`. Install SDK dependencies into a temporary workspace outside the plugin source directory.
- Register the plugin and enable the protocol-specific readiness remediation link in the same change. Keep the readiness package self-contained; it must not import a sibling installed plugin. Use shared protocol vectors or a consistency test to prevent drift between their independently packaged parsers.

Acceptance: all offline fixtures pass; the skill outputs identify supported versions and unsupported combinations; no real payment is needed for CI. Documentation names mocked settlement as mocked settlement. Any optional testnet recipe is separately invoked and is not required for default installation.

### 3. Add `trusted-agent-protocol`

Create the standard manifest, `agents/tap-expert.md`, README, applicable secret-check hook, skills, and executable resources. Describe it as a plugin for the Visa-published Trusted Agent Protocol, without implying affiliation or certification.

| Skill | Deliverable |
| --- | --- |
| `tap-setup` | Select the applicable TAP profile, integration point, trust configuration, and current specification. |
| `tap-request-signatures` | Generate and verify request signatures with the profile's required covered components. |
| `tap-merchant-verification` | Integrate verification at the merchant edge/application and enforce local acceptance policy. |
| `tap-key-management` | Configure trusted key sources, key selection, caching, rotation, and revocation behavior. |
| `tap-consumer-payment-binding` | Verify the applicable consumer-recognition and payment-container bindings and their relationship to the request. |
| `tap-conformance` | Run positive and negative cryptographic fixtures and explain protocol/profile coverage. |

Executable scope:

- Begin with a bounded library compatibility check against the pinned TAP profile and official reference vectors. Select a maintained RFC 9421 implementation; [Python http-message-signatures](https://github.com/pyauth/http-message-signatures) is a candidate. Pin the selected library and cryptographic dependencies after verifying required algorithms, covered components, and signature parameters. Do not implement cryptographic primitives or HTTP signature canonicalization from scratch.
- Ship `scripts/verify_request.py`, `scripts/test_conformance.py`, and a separate pinned verifier dependency file. The verifier accepts a local request capture and explicit local trust configuration; verification must never fetch an arbitrary URL supplied by an untrusted key identifier.
- Generate synthetic keys during tests. Test an accepted signature and rejection of changes to components required by the selected profile, expired/future signatures, missing required parameters, unsupported algorithms, untrusted or unknown keys, and invalid consumer/payment bindings.
- Provide a local merchant example using atomic replay protection with bounded retention. Test duplicate and concurrent replay attempts, key rotation, and trust-source failure behavior. Document the example's storage limits and the production requirements for a distributed replay store.
- Verify body or container integrity wherever the profile requires it. Treat uncovered request fields as unverified. Define trusted proxy reconstruction explicitly so forwarded headers cannot silently change what is verified.
- Keep cryptographic validity, configured provider trust, and business authorization as separate results. A valid signature alone must not grant checkout, payment, or bypass privileges.
- Store profile revisions, reference-vector provenance, and supported algorithms in `audit/source-baseline.md`; include skill evaluations in `evals/`. Attribute any reused reference material and preserve its license requirements.
- Keep TAP diagnostics outside the public readiness score for this release. A public JWKS or HTTP signature header does not demonstrate a working TAP verifier, and absence of TAP must not add a universal merchant-readiness penalty.

Acceptance: real cryptographic positive and negative fixtures pass offline; replay and trust decisions are tested; dependencies are reproducibly installed; no real consumer information, payment credentials, or production private keys are committed.

### 4. Update Shopify guidance and repository inventories

- Add `shopify-agentic-ucp` and `shopify-storefront-mcp-migration` within the existing Shopify plugin. Cover store discovery, agent profiles, current catalog/cart mappings, checkout handoff, and the access conditions for direct completion. Keep Storefront and Customer Account MCP changes distinct and use the current [Shopify agent documentation](https://shopify.dev/docs/agents).
- Link Shopify-specific implementation instructions to existing UCP concepts instead of copying the generic protocol skills. Validate the migration against actual current tool schemas, including changed update semantics.
- Correct the root README table, add the two new plugins, and update affected plugin README counts and cross-references. Recompute counts from registered source directories; do not count `dist/` copies.
- Update `.claude-plugin/marketplace.json` plus the Codex and Cursor marketplace catalogs to include both plugins. Respect each catalog's existing source-path conventions. The converter's canonical registry is the Claude marketplace; do not assume running it updates all root catalogs.
- Extend the existing manifest validator, or add a small inventory validator, to catch registered plugins missing from advertised catalogs and broken skill/remediation references. Validate meaningful inventory relationships rather than exact prose formatting.
- Treat the root Gemini manifest, `GEMINI.md`, hooks, and root skills as the existing UCP convenience surface. Do not silently convert that surface into a different all-plugin package.

Acceptance: 18 plugins are consistently registered and documented; actual source skill counts match the published inventory; all new cross-plugin links resolve. Existing plugins install independently of the two new additions.

### 5. Regenerate, test, and release the complete set

- Keep executable files, fixture data, dependency manifests, and reference baselines inside the converter's supported resource directories. Arbitrary sibling files next to `SKILL.md` are not currently copied. Use paths that resolve from each target platform's actual skill location.
- Generate all five `dist/` targets with `python scripts/convert.py`; never hand-edit generated files. Keep virtual environments, `node_modules`, downloaded SDKs, generated keys, and transient test outputs out of plugin resource trees.
- Add the new fixture suites and inventory checks to CI. Keep hooks and the readiness parser on the Python standard library; install TAP verifier dependencies only for the verifier/test job and keep SDK integration dependencies isolated.
- Add focused Windows coverage for hook interpreter fallback and installed-resource paths. Preserve the existing Ubuntu validation workflow and its localhost integration test.
- For every implementation change that affects a distributed plugin, regenerate its artifacts in that same PR. Each intermediate PR must pass existing CI; defer neither broken references nor stale distributions to a final cleanup PR.

Run the existing release checks:

```text
node scripts/validate_manifests.mjs
python scripts/validate.py
node scripts/validate-cursor.mjs
python commerce-readiness/scripts/test_scoring.py
python commerce-readiness/scripts/test_mcp_server.py
node scripts/check_links.mjs
python scripts/convert.py
git diff --exit-code -- dist
```

The Cursor schema check needs its existing `ajv`/`ajv-formats` installation and network access. Link checking also needs network access. Check the final regeneration diff against a tree containing the intended generated artifacts; a second generation must produce no changes.

Add these planned checks, installing the pinned verifier dependencies first:

```text
python commerce-readiness/scripts/test_payments.py
python x402-agentic-payments/scripts/test_conformance.py
python trusted-agent-protocol/scripts/test_conformance.py
```

Also run the pinned x402 SDK integration fixture and the inventory check using the commands documented with their implementation. Add both to CI rather than leaving them as manual-only checks.

Follow `CONTRIBUTING.md` by exercising every new skill and both expert agents in real Claude Code sessions. Use benign local fixtures. Run an installation/resource smoke test for each generated platform and report platform-specific limitations explicitly; passing manifest schemas alone is not runtime compatibility evidence.

Acceptance: all existing and new checks pass in suitable environments; generated files are reproducible; installed fixtures resolve without the source checkout or sibling plugins; runtime smoke-test results are recorded with platform/version details.

## Dependencies and merge boundaries

Implement the readiness correction first, with a neutral remediation for unknown challenges. Build x402 and TAP as separate reviewable changes; TAP does not depend on x402. The Shopify additions can follow independently. Registration, applicable catalog updates, tests, and generated output accompany each plugin's introducing PR. Finish with the full release matrix and any remaining cross-plugin documentation corrections.

Record exact upstream spec revisions and SDK/library versions before creating protocol fixtures. If a selected library cannot support the pinned TAP profile, resolve that compatibility issue before claiming a runnable verifier. Upstream production access or provider enrollment is not necessary for the offline development-plugin release, and must not be implied by passing its tests.

## Definition of done

- Unrelated HTTP 402 responses no longer pass as MPP; valid supported MPP and x402 challenges are classified with bounded, accurate evidence.
- Both plugins contain complete skills, expert agents, manifests, documentation, and meaningful executable fixtures.
- TAP tests prove the stated cryptographic and policy behavior; x402 tests distinguish wire validation, mocked integration, and any separately performed live settlement.
- Shopify guidance follows the current migration and checkout access model.
- All 18 source plugins, marketplace catalogs, README inventories, and five generated distributions agree.
- Required CI checks and runtime smoke tests pass; any unavailable platform verification is explicitly recorded before release claims are made.
- The previously blocked readiness MCP integration test has been re-run successfully in an environment that permits localhost sockets.
