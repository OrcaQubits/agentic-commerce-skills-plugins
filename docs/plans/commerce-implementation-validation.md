# Commerce plugin implementation and validation

Implemented locally on 2026-11-13 against initial repository commit `30cd25c`. No release, commit, or external publication was performed.

## Delivered

- `x402-agentic-payments` version 0.1.0: seven skills, expert agent, advisory hook, bounded HTTP/MCP challenge inspection, policy fixtures, pinned SDK integration, and a settlement-operation guard example.
- `trusted-agent-protocol` version 0.1.0: six skills, expert agent, advisory hook, library-backed Ed25519 HTTP signature verification, explicit local key trust, consumer/payment binding fixtures, and atomic SQLite replay protection.
- Payment readiness now distinguishes valid supported MPP/x402 envelopes from unrelated or malformed 402 responses, continues scanning after an invalid response, preserves its six-point R5 denominator, and carries protocol observations into CLI/MCP output.
- Two Shopify skills cover UCP integration and Storefront MCP migration, including full-cart replacement and checkout access constraints. The existing Shopify expert points to them.
- MPP/AP2 comparisons, README inventories, secondary catalogs, and the stale Medusa JS SDK reference were corrected. There are now **18 source plugins and 300 source skills**.
- Five distributions were regenerated. CI includes inventory, payment, TAP, SDK, independent-bundle, and Windows hook/path checks. Secondary catalog and payment-parser synchronization scripts prevent drift.

## Executed checks

| Check | Observed result |
| --- | --- |
| Source/distribution manifests | 410 checks passed; 18 plugins |
| Generated bundle validation | 3,630 checks passed, zero warnings/errors |
| Inventory and skill/remediation references | 18 plugins; zero errors |
| Existing readiness scoring | 30 checks passed |
| Readiness payment regressions | Three unittest groups passed, including scan continuation and unchanged score weight |
| Readiness MCP integration | 21 checks passed, including CLI/MCP payment evidence equivalence and SSRF/deep-mode refusals |
| x402 Python conformance | Seven unittest groups passed, including malformed inputs, legacy versions, MCP agreement, and unsupported policy alternatives |
| TAP conformance | Ten unittest groups passed with real synthetic signatures, altered requests/bindings, trust/time failures, concurrent replay, and key rotation |
| Locked x402 SDK fixture | Passed with Node 25 and CI's Node 22: HTTP negotiation, independent local signature verification/tamper rejection, mocked verification/settlement outcomes, and duplicate/concurrent operation guards |
| Independent installed resources | Both new plugins copied away from the repository and tested on all five distribution layouts; ten bundle suites passed; source/converted hook tests passed |
| Claude native manifest validation | Both plugin manifests passed `claude plugin validate` |
| Claude runtime smoke | All 15 new skills and both expert-agent definitions invoked in Claude Code 2.1.280; sessions completed successfully without permission denials |
| Cursor official schemas | 19 manifests/catalog checked, zero errors under Node 22 |
| Documentation links | 474 URLs checked; zero broken links after correction/retry; two existing access warnings |
| Regeneration | Consecutive conversions compared by file path and SHA-256, including untracked additions; byte-identical output |
| Diff whitespace | `git diff --check` passed |

The CLI/runtime smoke sessions were read-only instruction tests; they did not implement or execute a live merchant checkout. The executable fixtures listed above were run separately. The x402 facilitator skill received a focused follow-up case and correctly retained an unknown settlement/budget hold after authorization expiry. The setup instructions also explicitly distinguish a core challenge payload from the HTTP capture accepted by the inspector.

## Environment and resolved issues

Local fixture execution used Windows and Python 3.11. The CI workflow specifies Python 3.12 and Node 22. The initial localhost restriction was resolved by running the MCP integration test with permitted socket access. Test dependencies were installed in an isolated temporary environment, using public PyPI after the workstation's private package index rejected access.

Node 25 completed Cursor schema checks but crashed during shutdown; a repeat using the CI Node 22 runtime exited successfully. An npm cache lock error was resolved using a separate temporary cache. A transient GitHub 500 disappeared on the link-check rerun. The two remaining link warnings concern an existing marketplace site returning 429 and an existing OpenAI site returning 403; neither is a new plugin reference.

Automatic approval review initially rejected additional Claude sessions because they could transfer repository content to an authenticated external service. The user explicitly approved those runtime tests, and the read-only tests then completed. No unresolved approval block remains.

## Coverage limits

Follow-up instruction review: strengthened live-reference requirements in all
15 new skills and both new agents. Dated Shopify endpoint/tool observations now
live in a separate audit snapshot. Missing live references permit conceptual
guidance and local fixture inspection, not new integration code based on stale
snapshots. The runtime smoke results above preceded this wording refinement;
the refinement was checked through source/distribution validators and regeneration.

The x402 inspector establishes bounded envelope structure, not merchant authenticity, scheme execution, or settlement. The SDK fixture uses the real pinned SDK and local signatures with a mocked facilitator; it sends no funds and makes no blockchain RPC calls. The spending helper covers a single request. Its settlement guard is in-memory demonstration code; production requires durable, atomic operation/budget storage and reconciliation against authoritative receipts or finalized ledger state.

The TAP executable supports the documented Ed25519 recognition subset and a stricter merchant policy. Its optional ordered-JSON consumer/payment container format is an explicit synthetic fixture agreement, not certified Visa production interoperability. It does not verify identity JWTs, perform provider enrollment, establish consumer consent, or authorize charges. SQLite replay protection is a single-host example, and production proxy reconstruction and remote key distribution require integration-specific testing. See each plugin's `audit/source-baseline.md` for exact sources and pins.

The five generated layouts passed independent executable-resource smoke tests. Native Gemini, Codex, Cursor, Antigravity, and OpenClaw interactive sessions were not exercised; schema/resource results do not claim native UI or hook-runtime parity on those hosts. Shopify's new skills were checked against official documentation and invoked in Claude, but no authenticated development store was connected for live cart/checkout operations.
