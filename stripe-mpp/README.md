# Stripe MPP Plugin for Claude Code

A deeply expert Claude Code plugin for implementing the **Machine Payments Protocol (MPP)** — the open standard co-authored by Stripe and Tempo Labs for HTTP 402-based machine-to-machine payments, enabling AI agents to pay for API calls, data, and services autonomously.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — HTTP 402 challenge-response flow, charge and session payment intents, Tempo blockchain settlement, Stripe SPT integration, service discovery, and security model that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest mppx SDK API, Stripe endpoint schemas, Tempo chain parameters, and IETF draft header formats.
- **Spec version is always cited** — generated code includes comments referencing the specification version and SDK version it was written against.

## Plugin Structure

```
stripe-mpp/
├── .claude-plugin/
│   └── plugin.json                              # Plugin manifest
├── agents/
│   └── mpp-expert.md                            # Subagent: full MPP protocol expert
├── hooks/
│   ├── hooks.json                               # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                     # PostToolUse: detect payment/crypto secrets
├── skills/
│   ├── mpp-setup/SKILL.md                       # Project scaffolding & SDK installation
│   ├── mpp-server-middleware/SKILL.md            # Server middleware (Hono/Express/Next.js/Elysia)
│   ├── mpp-client-fetch/SKILL.md                # Client-side mppx.fetch() transparent payments
│   ├── mpp-charge-flow/SKILL.md                 # One-time charge intent implementation
│   ├── mpp-session-flow/SKILL.md                # Session/streaming micropayment implementation
│   ├── mpp-tempo-method/SKILL.md                # Tempo blockchain payment method
│   ├── mpp-stripe-method/SKILL.md               # Stripe SPT payment method
│   ├── mpp-service-discovery/SKILL.md           # OpenAPI x-payment-info & llms.txt
│   ├── mpp-proxy/SKILL.md                       # Payment proxy for existing APIs
│   ├── mpp-dev-patterns/SKILL.md                # Security, retry, receipts, monitoring
│   ├── mpp-spt-lifecycle/SKILL.md               # SPT creation, usage, webhooks
│   └── mpp-conformance/SKILL.md                 # Spec compliance & production readiness
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "stripe-mpp"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "stripe-mpp": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/stripe-mpp"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `stripe-mpp:mpp-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves MPP:

```
Build a paid API using HTTP 402 and machine payments
```

```
Add Tempo payment support to my Hono server with mppx
```

```
Create an AI agent client that pays for API calls automatically
```

### Explicit invocation

```
Use the mpp-expert subagent to implement streaming session payments
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest mppx SDK version and API surface on npm
2. Fetch the IETF specification from paymentauth.org for exact header formats
3. Fetch Stripe machine payments docs for PaymentIntent and SPT integration
4. Check the stripe-samples/machine-payments repo for reference code
5. Write code against the verified-current spec and SDK, citing versions

## Available Skills

| Skill | Command | Invocation | Description |
|---|---|---|---|
| **mpp-setup** | `/stripe-mpp:mpp-setup` | Manual | Scaffold project, install mppx, configure payment methods |
| **mpp-server-middleware** | auto | Auto + manual | Server middleware for Hono, Express, Next.js, Elysia |
| **mpp-client-fetch** | auto | Auto + manual | Client-side transparent 402 payment handling |
| **mpp-charge-flow** | auto | Auto + manual | One-time per-request payment gates |
| **mpp-session-flow** | auto | Auto + manual | Session/streaming micropayment flows |
| **mpp-tempo-method** | auto | Auto + manual | Tempo blockchain USDC payment configuration |
| **mpp-stripe-method** | auto | Auto + manual | Stripe card/SPT payment configuration |
| **mpp-service-discovery** | auto | Auto + manual | OpenAPI x-payment-info, llms.txt, directory listing |
| **mpp-proxy** | auto | Auto + manual | Wrap existing APIs with 402 payment gates |
| **mpp-dev-patterns** | auto | Auto + manual | Security, HMAC binding, replay protection, monitoring |
| **mpp-spt-lifecycle** | auto | Auto + manual | SPT creation, consumption, webhooks, reconciliation |
| **mpp-conformance** | `/stripe-mpp:mpp-conformance` | Manual | Spec compliance validation & production readiness |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Stripe keys (`sk_live_`, `sk_test_`, `whsec_`), MPP secret keys, crypto wallet private keys, SPT tokens, and Bearer tokens. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## MPP Protocol at a Glance

### Core Concept

MPP formalizes the HTTP 402 ("Payment Required") status code into a proper authentication scheme, enabling machine-to-machine payments over standard HTTP.

### HTTP 402 Challenge-Response Flow

```
Client: GET /resource
Server: 402 Payment Required
        WWW-Authenticate: Payment <challenge>
Client: [Fulfills payment off-band]
Client: GET /resource
        Authorization: Payment <credential>
Server: 200 OK
        Payment-Receipt: <receipt>
```

### Two Payment Intents

| Intent | Model | Use Case |
|--------|-------|----------|
| **Charge** | One-time, per-request | API calls, data queries, file downloads |
| **Session** | Streaming, pay-as-you-go | Per-token billing, data feeds, compute metering |

### Supported Payment Methods

| Method | Settlement | Fiat Support |
|--------|-----------|-------------|
| **Tempo** | Sub-second (blockchain) | Via Stripe balance |
| **Stripe** | Standard Stripe settlement | Yes (cards, wallets) |
| **Lightning** | Near-instant (Bitcoin) | No |
| **Card** | Card network settlement | Yes (Visa spec) |
| **Custom** | Developer-defined | Developer-defined |

### Key Participants

| Entity | Role |
|--------|------|
| **Stripe** | Co-author, payment infrastructure, PaymentIntents |
| **Tempo Labs** | Co-author, Tempo blockchain, mppx SDK |
| **Visa** | Card specification and SDK for card-based MPP |
| **Cloudflare** | Edge deployment (Cloudflare Workers) |
| **IETF** | Standardization (draft-ryan-httpauth-payment) |

### SDKs

| Language | Package | Install |
|----------|---------|---------|
| TypeScript | `mppx` | `npm install mppx` |
| Python | `pympp` | `pip install pympp` |
| Rust | See mpp.dev | Check mpp.dev for current crate name |

### MPP vs x402

| Dimension | MPP | x402 |
|-----------|-----|------|
| Sessions | Yes (streaming) | No (per-request only) |
| Fiat support | Yes (Stripe SPTs) | No (crypto only) |
| Settlement | Sub-second (Tempo) | Varies by chain |
| Best for | Enterprise, high-frequency, hybrid | Open, decentralized, indie |

### MPP vs ACP

| Dimension | MPP | ACP |
|-----------|-----|-----|
| Focus | HTTP-level payment for any service | Agent-mediated merchant checkout |
| Protocol | HTTP 402 authentication scheme | REST/MCP checkout API |
| Scope | Pay for API calls, data, compute | Buy physical/digital products |
| Payment | Crypto (Tempo) + fiat (Stripe SPT) | Delegated payment via SPT |
| Session | Per-call, checkout flow | Full shopping journey |

Both protocols use Stripe SPTs — they are complementary, serving different use cases in the agentic commerce ecosystem.

## Official References

| Resource | URL |
|----------|-----|
| MPP Overview | https://mpp.dev/overview |
| MPP Specification (IETF) | https://paymentauth.org/ |
| IETF Draft | https://datatracker.ietf.org/doc/draft-ryan-httpauth-payment/ |
| Spec Repository | https://github.com/tempoxyz/mpp-specs |
| Stripe Blog: MPP | https://stripe.com/blog/machine-payments-protocol |
| Stripe Machine Payments | https://docs.stripe.com/payments/machine |
| Stripe MPP Docs | https://docs.stripe.com/payments/machine/mpp |
| Stripe SPT Docs | https://docs.stripe.com/agentic-commerce/concepts/shared-payment-tokens |
| mppx SDK (TypeScript) | https://www.npmjs.com/package/mppx |
| pympp SDK (Python) | https://pypi.org/project/pympp/ |
| Rust SDK | https://mpp.dev/overview |
| Sample Code | https://github.com/stripe-samples/machine-payments |
| MPP Services Directory | https://mpp.dev/services |
| Service Discovery Spec | https://paymentauth.org/draft-payment-discovery-00.html |
| Cloudflare MPP | https://developers.cloudflare.com/agents/agentic-payments/mpp/ |
| Visa Card Spec for MPP | https://corporate.visa.com/en/sites/visa-perspectives/innovation/visa-card-specification-sdk-for-machine-payments-protocol.html |
| Claude Code Plugins Docs | https://code.claude.com/docs/en/plugins |
| Claude Code Subagents Docs | https://code.claude.com/docs/en/sub-agents |
| Claude Code Skills Docs | https://code.claude.com/docs/en/skills |

## Endorsed By

**Co-Authors**: Stripe, Tempo Labs (incubated by Stripe and Paradigm)

**IETF Authors**: Brendan Ryan, Jake Moxey, Tom Meagher (Tempo), Jeff Weinstein, Steve Kaliski (Stripe)

**Ecosystem Partners**: Visa, Lightspark, Cloudflare, 100+ integrated services
