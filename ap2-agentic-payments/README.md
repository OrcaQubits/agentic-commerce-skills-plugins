# AP2 Agentic Payments Plugin for Claude Code

A deeply expert Claude Code plugin for implementing the **AP2 (Agent Payments Protocol)** — Google's open protocol for secure, verifiable, and interoperable AI-driven payments in agentic commerce.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — VDC framework, mandate types, role-based architecture, transaction flows, cryptographic signing, risk signals, and dispute accountability patterns that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest schemas, SDK methods, and mandate structures.
- **Spec version is always cited** — generated code includes comments referencing the AP2 specification version it was written against.

## Plugin Structure

```
ap2-agentic-payments/
├── .claude-plugin/
│   └── plugin.json                            # Plugin manifest
├── agents/
│   └── ap2-expert.md                          # Subagent: full AP2 protocol expert
├── hooks/
│   ├── hooks.json                             # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                   # PostToolUse: detect PCI data & payment secrets
├── skills/
│   ├── ap2-setup/SKILL.md                     # Project scaffolding & SDK install
│   ├── ap2-vdc-framework/SKILL.md             # Verifiable Digital Credentials framework
│   ├── ap2-cart-mandate/SKILL.md              # Cart Mandate (human-present)
│   ├── ap2-intent-mandate/SKILL.md            # Intent Mandate (human-not-present)
│   ├── ap2-payment-mandate/SKILL.md           # Payment Mandate (network visibility)
│   ├── ap2-human-present-flow/SKILL.md        # Human-present 20-step transaction flow
│   ├── ap2-human-not-present-flow/SKILL.md    # Human-not-present autonomous flow
│   ├── ap2-shopping-agent/SKILL.md            # Shopping Agent role implementation
│   ├── ap2-merchant-agent/SKILL.md            # Merchant Agent role implementation
│   ├── ap2-credentials-provider/SKILL.md      # Credentials Provider role implementation
│   ├── ap2-payment-processor/SKILL.md         # Payment Processor role implementation
│   ├── ap2-cryptographic-signing/SKILL.md     # Signatures, attestation, key management
│   ├── ap2-challenge-stepup/SKILL.md          # 3DS2, OTP, redirect challenges
│   ├── ap2-risk-signals/SKILL.md              # Risk framework & fraud assessment
│   ├── ap2-a2a-extension/SKILL.md             # AP2 as A2A extension integration
│   ├── ap2-mcp-server/SKILL.md                # AP2 MCP server tools
│   ├── ap2-dispute-accountability/SKILL.md    # Dispute resolution & audit trails
│   └── ap2-dev-patterns/SKILL.md              # Architecture, UCP/x402, deployment
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "ap2-agentic-payments"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "ap2-agentic-payments": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/ap2-agentic-payments"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `ap2-agentic-payments:ap2-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves AP2:

```
Build an AP2 Shopping Agent that handles card payments
```

```
Implement a Merchant Agent with Cart Mandate creation and signing
```

```
Add a Credentials Provider for payment method tokenization
```

### Explicit invocation

```
Use the ap2-expert subagent to implement Payment Mandate creation
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest spec version on ap2-protocol.org
2. Fetch the relevant specification page for exact mandate schemas
3. Fetch the SDK source for current type definitions and sample patterns
4. Write code against the verified-current spec, citing the version

## Available Skills (18)

| Skill | Invocation | Description |
|---|---|---|
| **ap2-setup** | Auto + manual | Scaffold project, install SDK, configure roles |
| **ap2-vdc-framework** | Auto + manual | Verifiable Digital Credentials architecture |
| **ap2-cart-mandate** | Auto + manual | Cart Mandate — human-present authorization |
| **ap2-intent-mandate** | Auto + manual | Intent Mandate — human-not-present pre-auth |
| **ap2-payment-mandate** | Auto + manual | Payment Mandate — network/issuer visibility |
| **ap2-human-present-flow** | Auto + manual | 20-step interactive transaction flow |
| **ap2-human-not-present-flow** | Auto + manual | Autonomous agent shopping flow |
| **ap2-shopping-agent** | Auto + manual | Shopping Agent role — orchestrator |
| **ap2-merchant-agent** | Auto + manual | Merchant Agent role — catalog & cart |
| **ap2-credentials-provider** | Auto + manual | Credentials Provider — tokenization & methods |
| **ap2-payment-processor** | Auto + manual | Payment Processor — authorization & settlement |
| **ap2-cryptographic-signing** | Auto + manual | Signatures, attestation, key management |
| **ap2-challenge-stepup** | Auto + manual | 3DS2, OTP, redirect challenges |
| **ap2-risk-signals** | Auto + manual | Risk framework, fraud assessment, trust |
| **ap2-a2a-extension** | Auto + manual | AP2 as A2A protocol extension |
| **ap2-mcp-server** | Auto + manual | AP2 MCP server payment tools |
| **ap2-dispute-accountability** | Auto + manual | Dispute resolution & cryptographic evidence |
| **ap2-dev-patterns** | Auto + manual | Architecture, UCP/x402, deployment patterns |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for PCI data (card numbers, CVVs), hardcoded payment tokens, Stripe keys, signing/device keys, and private key material. Reinforces AP2's role-based data separation: Shopping Agents must never access PCI/PII. Non-blocking. |

Hooks require Python in PATH.

## AP2 Protocol at a Glance

### The Three Fundamental Questions

| Question | How AP2 Solves It |
|----------|-------------------|
| **Authorization** | User-signed mandates prove agent had authority |
| **Authenticity** | Cryptographic VDCs prove intent is genuine, not hallucinated |
| **Accountability** | Non-repudiable audit trail determines liability |

### Six Roles

| Role | What It Does |
|------|-------------|
| **User** | Human who delegates purchase authority |
| **Shopping Agent** | AI orchestrator — coordinates the transaction |
| **Credentials Provider** | Payment credential custodian — tokenization |
| **Merchant Endpoint** | Seller — catalog, cart, fulfillment |
| **Payment Processor** | Financial processing — authorization, settlement |
| **Network/Issuer** | Payment networks (Visa/MC) and banks |

### Three Mandate Types (VDCs)

| Mandate | Scenario | Created By | Signed By |
|---------|----------|-----------|-----------|
| **Cart Mandate** | Human-present | Merchant | Merchant + User |
| **Intent Mandate** | Human-not-present | Shopping Agent | User |
| **Payment Mandate** | All transactions | Shopping Agent | User |

### Transaction Flows

**Human-Present** (20 steps):
```
User → SA → Merchant → Cart Mandate → User confirms → Payment → Receipt
```

**Human-Not-Present**:
```
User signs Intent Mandate → leaves → SA shops autonomously → Payment → Notification
```

### Protocol Stack

```
AP2 (Mandates, VDCs, Cryptographic Signing)
  ↑ extends
A2A (Agent-to-Agent Tasks, Messages, Parts)
  ↑ complements
MCP (Agent-to-Tool/Data Access)
```

### Related Protocols

| Protocol | Relationship |
|----------|-------------|
| **A2A** | AP2 extends A2A for payment-specific communication |
| **MCP** | AP2 MCP servers provide payment tools to agents |
| **UCP** | UCP operationalizes AP2 (Checkout = Cart Mandate) |
| **x402** | Complementary crypto payment method AP2 can support |

## Official References

| Resource | URL |
|----------|-----|
| AP2 Website | https://ap2-protocol.org |
| Specification | https://ap2-protocol.org/specification/ |
| Core Concepts | https://ap2-protocol.org/topics/core-concepts/ |
| Privacy & Security | https://ap2-protocol.org/topics/privacy-and-security/ |
| Roadmap | https://ap2-protocol.org/roadmap/ |
| GitHub Repository | https://github.com/google-agentic-commerce/AP2 |
| Python Samples | https://github.com/google-agentic-commerce/AP2/tree/main/samples/python |
| Google ADK | https://google.github.io/adk-docs/ |
| x402 Integration | https://github.com/google-agentic-commerce/a2a-x402 |
| Google Cloud Blog | https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol |

## Endorsed By

Google, Mastercard, Adyen, PayPal, Coinbase, Visa, American Express, Stripe, and 60+ initial partners.
