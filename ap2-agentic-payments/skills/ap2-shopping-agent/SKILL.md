---
name: ap2-shopping-agent
description: Build an AP2 Shopping Agent — the main orchestrator that handles user requests, creates mandates, coordinates with merchants and credentials providers, and manages the transaction flow. Use when implementing the Shopping Agent role.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Shopping Agent Implementation

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for Shopping Agent responsibilities
2. Web-search `site:github.com google-agentic-commerce AP2 samples roles shopping_agent` for reference implementation
3. Web-search `site:github.com google-agentic-commerce AP2 samples python src roles` for source code structure
4. Fetch SDK docs for agent framework classes (Google ADK)

## Conceptual Architecture

### What the Shopping Agent Does

The Shopping Agent (SA) is the **primary orchestrator** of AP2 transactions. It acts as the user's representative, coordinating between all other roles:

1. **Receives user intent** — Understands what the user wants to buy
2. **Creates Intent Mandates** — Formalizes user intent into structured mandates
3. **Discovers merchants** — Finds merchants that can fulfill the intent
4. **Negotiates with merchants** — Presents mandates, receives Cart Mandates
5. **Coordinates with Credentials Provider** — Gets payment methods, handles tokenization
6. **Manages user interaction** — Presents options, collects confirmations
7. **Orchestrates the full flow** — Drives the human-present transaction flow

Note: The Shopping Agent does **not** create Payment Mandates. Payment Mandates are constructed by the **Merchant Payment Processor (MPP)**.

### Agent Card

The Shopping Agent's Agent Card declares:
- AP2 extension support in `capabilities.extensions[]`
- Skills related to shopping (product search, cart management, payment)
- Authentication requirements for users
- Supported input/output modes

### Key Responsibilities

#### Intent Capture
- Parse user's natural language shopping request
- Extract: what to buy, constraints (price, brand, quality), preferences
- Present structured understanding back to user for confirmation
- Create and present Intent Mandate for signing

#### Merchant Interaction
- Discover merchant agents (via Agent Cards or registry)
- Present Intent Mandate to relevant merchants
- Receive and evaluate Cart Mandates
- Handle merchant clarification requests
- Support multi-merchant scenarios (compare offers)

#### Payment Coordination
- Query Credentials Provider for available payment methods
- Present payment options to user
- Request payment method tokenization
- Relay payment context to Merchant/MPP (the MPP constructs the Payment Mandate)
- Handle the trusted device surface attestation flow

#### User Communication
- Display product options clearly
- Show pricing breakdowns
- Present payment method choices
- Redirect to trusted device surface for confirmation
- Deliver receipts and confirmations

### What the Shopping Agent Must NOT Do

Critical security constraints:
- **Never access raw payment credentials** — Only tokenized references (DPANs)
- **Never store PCI data** — Card numbers, CVVs stay with Credentials Provider
- **Never store PII beyond needed scope** — Minimize data retention
- **Never forge user signatures** — Signatures come from user's device
- **Never auto-approve beyond Intent Mandate bounds** — Respect constraints

### Implementation with Google ADK

The reference implementation uses Google ADK:
- ADK agent with Gemini 2.5 Flash for reasoning
- A2A server for receiving user messages
- A2A client for communicating with other agents
- Port 8000 with ADK web UI

### Verbose Mode

Include "verbose" in the initial prompt to enable:
- Detailed agent explanations of each step
- Display of all mandate JSON payloads
- Full DataPart visibility
- Useful for debugging and development

### Best Practices

- Use the LLM for understanding intent, but validate mandates deterministically
- Always present clear summaries to the user before requesting signatures
- Handle timeouts for user responses
- Implement retry logic for failed agent-to-agent communications
- Log all mandate creation and agent interactions
- Support the escalation from autonomous to human-present flows
- Test with multiple merchants to verify comparison logic
- Never bypass the trusted device surface confirmation

Fetch the sample Shopping Agent source code for exact implementation patterns, ADK configuration, and A2A message handling before building.
