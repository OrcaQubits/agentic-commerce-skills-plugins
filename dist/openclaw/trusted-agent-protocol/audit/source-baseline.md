# Executable baseline and limits

Checked 2026-11-13. Protocol source: [Visa merchant specifications](https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications). Reference implementation inspected at [commit 16d59bdf3f8a542bc538d0962edbb80ea30a02af](https://github.com/visa/trusted-agent-protocol/tree/16d59bdf3f8a542bc538d0962edbb80ea30a02af). HTTP canonicalization uses [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421) through `http-message-signatures==3.0.0`; crypto uses `cryptography==50.0.2`. Full environment pins are in `scripts/requirements-verifier.txt`.

The merchant web document is unversioned. Its recognition profile as retrieved on this date requires authority/path coverage and created, expires, keyid, alg, nonce, and an allowed browsing/payment tag, with an eight-minute maximum validity interval. The implementation records these requirements here instead of claiming the sample repository is a normative conformance suite. Samples and the web document differ; do not copy the sample's custom canonicalizer into production.

## Profiles

| Profile | What the verifier establishes |
| --- | --- |
| `tap-minimum` | Ed25519 recognition, required authority/path and metadata, explicit local key trust, strict time window, atomic replay consumption. It makes no method/query/body-integrity claim unless those fields were verified. |
| `merchant-strict` (default) | The same checks plus method and complete target URI coverage and a signed digest for nonempty bodies. This is additional merchant policy, not a claim that TAP universally mandates those components. |
| `ordered-json-ed25519-fixture-v1` | Optional local agreement for synthetic consumer/payment objects: preserve JSON member order, omit only `signature`, compact UTF-8 serialization, Ed25519 signature, matching request nonce and key ID. It is not a certified production Visa container serialization. |

The library's Ed25519 primitive is reused unchanged with the `Ed25519` algorithm identifier spelling in Visa's merchant examples. Other algorithm spellings/profiles are deliberately unsupported, not silently normalized. The verifier never fetches a key from `keyid` or a request-provided URL.

The container profile is enabled only by explicit local trust configuration. Without that selection, supplied containers fail closed. The outer object signature does not validate an identity JWT, payment credential, consumer consent, available funds, or permission to charge. The fixture's `idToken` is deliberately a synthetic non-JWT and output explicitly says identity-token verification has not occurred. Production bindings require an agreed provider serialization and independent token verification.

## Operational boundaries

Synthetic keys are generated during each test and never saved. The fixture generator exports only public keys and expiring signed captures. SQLite uses atomic inserts scoped by provider and nonce hash, with expiry cleanup, and closes connections on Windows. It is a single-host example; distributed deployments need shared atomic replay storage and rate limits. Trust-file provisioning, key refresh, and revocation distribution are operator responsibilities. No remote provider enrollment, certification, real payment, or consumer data is involved.

The capture's URL must be the externally observed, normalized URL reconstructed by trusted infrastructure. The verifier does not trust forwarded headers to choose its target. Preserve signed bytes at the ingress boundary; test any proxy rewrite before deploying.

These fixtures were authored independently using synthetic keys. No Visa source code or static vendor private keys are copied. All tests are implementation evidence for the stated profiles, not official Visa certification vectors.
