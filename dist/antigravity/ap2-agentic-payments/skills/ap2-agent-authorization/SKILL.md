---
name: ap2-agent-authorization
description: >
  Implement the AP2 Agent Authorization Framework — open vs closed mandates,
  the two-phase delegation/authorization process, the cryptographic
  authorization chain, Key Binding JWTs, and human-present vs human-not-present
  signing. Use when designing how a user authorizes an agent to act, before
  touching any specific mandate type.
---

# AP2 Agent Authorization Framework

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/ap2/agent_authorization/` for the framework itself — this is the foundational model everything else sits on.
2. Fetch `https://ap2-protocol.org/ap2/specification/` for the current mandate types and their schemas.
3. Fetch `https://ap2-protocol.org/glossary/` — AP2's terminology has changed across releases and the glossary is the fastest way to catch a rename.
4. Web-search `site:github.com google-agentic-commerce AP2 mandate open closed` for reference types under `code/`.

**Terminology warning**: AP2 renamed and restructured core objects between releases. Confirm the current names against the live glossary before writing any type. Never carry an object name forward from an older tutorial, blog post, or this skill.

## Conceptual Architecture

### The problem it solves

> Even well-behaving agents need to have their behavior tightly constrained above what a normal authorization model would require of human users.

A human authenticating to a site is authorizing *themselves*. An agent acting for a human is a delegation, and delegation needs an explicit, verifiable, bounded grant. The Agent Authorization Framework is that grant.

### Mandates are the authorization objects

Mandates represent user-approved permissions delegated to an agent, and they chain cryptographically to prove authorization end to end. The framework defines two **states**:

| State | Bound to a transaction? | Contains | Bound to |
|-------|------------------------|----------|----------|
| **Open** | No | Constraints on what a valid closed mandate may contain | A particular agent |
| **Closed** | Yes — via **Key Binding JWT** | The specific action being authorized | A specific transaction, presented to a verifier |

Open and closed are not two different objects; they are two states of the same authorization, and the open→closed transition is where the agent's discretion gets spent.

### Two-phase process

1. **Mandate delegation** — the user approves mandate content **on a trusted surface**, and the resulting mandate is passed to the agent.
2. **Action authorization** — the agent presents the mandate to a verifier; the verifier checks authorization and returns a **signed receipt**.

The trusted surface in phase 1 is load-bearing. An agent conversation is not a trusted surface — see `ap2-challenge-stepup` for why the same principle governs challenges.

### Human-present vs human-not-present

This is the cleanest way to hold the distinction:

- **Human present** — the user directly signs **closed** mandate content. They are looking at the actual transaction.
- **Human not present** — the user signs **open** mandate content carrying constraints. Later, the agent signs closed mandate content binding it to a real transaction, and presents the **full chain** to demonstrate authorization.

So human-not-present is not "less authorization". It is the same authorization, expressed as constraints up front and resolved into a specific transaction later, with both signatures preserved for accountability.

### The chain is the evidence

Because closed mandates bind to open mandates which bind to a user signature, the chain answers the dispute question directly: *was this specific purchase within what the user actually authorized?* See `ap2-dispute-accountability`.

## Implementation Guidance

- Treat the open mandate's constraints as the security boundary. Validate the closed mandate against them at the verifier, not only at the agent — an agent that produces an out-of-constraint closed mandate must be rejected downstream.
- Persist the entire chain, not just the final closed mandate. A closed mandate alone cannot prove authorization.
- Verify Key Binding JWT semantics against the live spec; key binding is what stops a captured mandate being replayed against a different transaction.
- Set expiry on open mandates deliberately. An open mandate with a long life is a standing grant.
- Related skills: `ap2-checkout-mandate` (formerly cart mandate), `ap2-payment-mandate`, `ap2-vdc-framework`, `ap2-human-present-flow`, `ap2-human-not-present-flow`.
