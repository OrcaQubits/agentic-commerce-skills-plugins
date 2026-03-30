---
name: ucp-setup
description: >
  Set up a UCP project — scaffold a merchant server or platform client with
  discovery profile, SDK installation, and project structure. Use when starting
  a new UCP implementation.
disable-model-invocation: true
---

# UCP Project Setup

## Before writing any code

1. **Web-search** `site:ucp.dev specification overview` to confirm the latest spec version.
2. **Fetch** the latest SDK READMEs:
   - Python: https://github.com/Universal-Commerce-Protocol/python-sdk
   - JS/TS: https://github.com/Universal-Commerce-Protocol/js-sdk
3. **Fetch** the sample servers for reference architecture:
   - https://github.com/Universal-Commerce-Protocol/samples

## What to scaffold

### 1. Determine the role
Ask the user: are they building a **Business** (merchant server that exposes checkout), a **Platform** (AI agent that drives checkout), or both?

### 2. Install the SDK
- **Python**: Clone the official python-sdk repo and use `uv sync`, or install FastUCP via `pip install fastucp-python` for decorator-based approach. **Note**: `fastucp-python` is a **community/third-party** package, not an official UCP SDK.
- **JS/TS**: `npm install @ucp-js/sdk` for TypeScript types and Zod schemas.
- Always verify the latest install instructions from the live GitHub README before running.

### 3. Discovery profile (`/.well-known/ucp`)
Every Business MUST publish a discovery profile. This is the **first thing to implement**.

The profile declares:
- Protocol version
- Services (which transport bindings are supported, with endpoint URLs)
- Capabilities (checkout, orders, identity linking — each with version and schema URI)
- Extensions (fulfillment, discount, buyer consent, AP2 — each declaring which capability they extend)
- Payment handlers (accepted payment methods with configuration)
- Signing keys (EC P-256 public keys for webhook signatures)

**Fetch** https://ucp.dev/specification/overview/ and https://developers.google.com/merchant/ucp/guides/ucp-profile for the exact current schema before generating the profile.

### 4. Project structure (Business server)
```
my-ucp-server/
├── app/
│   ├── main.py (or index.ts)         # Server entrypoint
│   ├── discovery.py                   # /.well-known/ucp endpoint
│   ├── checkout/
│   │   ├── routes.py                  # Checkout CRUD + complete + cancel
│   │   ├── models.py                  # Checkout data models (from SDK)
│   │   └── negotiation.py            # Capability negotiation logic
│   ├── orders/
│   │   ├── routes.py                  # Order management
│   │   ├── webhooks.py               # Webhook delivery + signing
│   │   └── models.py
│   ├── payments/
│   │   ├── handlers.py               # Payment handler configuration
│   │   └── processing.py             # Credential processing
│   ├── fulfillment/
│   │   └── routes.py                 # Fulfillment extension logic
│   └── common/
│       ├── headers.py                # UCP-Agent, Idempotency-Key parsing
│       ├── errors.py                 # UCP error/message model
│       └── crypto.py                # JWT signing for webhooks
├── tests/
│   └── conformance/                  # Conformance test runner
├── .well-known/
│   └── ucp (or served dynamically)
├── .env                              # API keys, signing key paths
└── pyproject.toml (or package.json)
```

### 5. Environment configuration
- Store signing private keys securely (env vars or secrets manager)
- Never hardcode payment handler credentials
- Use `.env` + `.gitignore` for all secrets

### 6. Verify setup
- Serve the discovery profile and validate its JSON against the schema from https://ucp.dev/specification/reference/
- Use the UCP Playground at https://ucp.dev/playground/ to test discovery step
