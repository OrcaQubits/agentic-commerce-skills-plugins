---
name: acp-capability-negotiation
description: Implement ACP capability negotiation — dynamic discovery of mutually supported capabilities, extensions, payment handlers, and interventions. Use when building multi-feature merchant servers or agents that adapt to merchant capabilities.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Capability Negotiation

## Before writing code

**Fetch live docs**:
1. Web-search `site:github.com agentic-commerce-protocol rfcs capability_negotiation` for the capability negotiation RFC
2. Fetch `https://developers.openai.com/commerce/specs/checkout/` for how capabilities appear in checkout requests/responses
3. Web-search `site:github.com agentic-commerce-protocol spec json-schema capabilities` for the capabilities JSON schema

## Conceptual Architecture

### What Capability Negotiation Does

ACP agents and merchants may support different features. Capability negotiation allows them to **dynamically discover** what they both support, so the session uses only mutually available features.

### How It Works

1. **Agent sends capabilities** — In the `create` request, the agent includes a `capabilities` object listing what it supports
2. **Merchant responds with capabilities** — The merchant intersects with its own capabilities and returns what's active for this session
3. **Intersection governs the session** — Only mutually supported features are used

### Capabilities Object Structure

The capabilities object contains:
- **`capabilities`** — Major features (checkout, orders, etc.)
- **`extensions[]`** — Optional add-ons (discount, intent traces, affiliate attribution)
- **`payment_handlers[]`** — Supported payment methods
- **`interventions`** — Structured object with sub-fields: `supported`, `required`, `enforcement`, `display_context`, `redirect_context`, `max_redirects`, `max_interaction_depth`

### Extension Pruning

Extensions declare a parent capability via `extends`. If the parent capability is not in the negotiated intersection, the extension is automatically pruned — no extra logic needed.

### Interventions

Interventions are actions that require human involvement. They are represented as a structured object (not a flat array) with sub-fields including `supported`, `required`, `enforcement`, `display_context`, `redirect_context`, `max_redirects`, and `max_interaction_depth`.

Intervention types include:
- **3D Secure** — Card authentication challenge
- **Biometric** — Fingerprint/face verification
- **Address Verification** — Address confirmation flow
- Other authentication or verification flows

The agent advertises which interventions it can handle. If the merchant requires an intervention the agent can't handle, the checkout may not proceed.

### Versioning in Negotiation

- Each capability has its own version
- Extensions are versioned independently (`discount@2026-01-27`)
- Payment handlers have their own version
- Version mismatches are resolved by intersection (both must support a compatible version)

### Use Cases

- Merchants that support different feature sets for different plans
- Agents that gradually adopt new protocol features
- Graceful degradation when features aren't mutually supported
- Multi-merchant agents that adapt per-merchant

### Best Practices

- Always include capabilities in the create request
- Advertise all capabilities you support — don't under-report
- Handle the case where the merchant supports fewer features than expected
- Log negotiated capabilities for debugging
- Test with minimal capability sets to ensure graceful degradation
- Update advertised capabilities as you adopt new spec features

Fetch the capability negotiation RFC for the exact capabilities object schema, extension pruning rules, and negotiation semantics before implementing.
