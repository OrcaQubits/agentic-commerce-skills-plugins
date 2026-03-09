---
name: ap2-a2a-extension
description: Implement AP2 as an A2A extension — mandate DataParts in A2A messages, Agent Card AP2 capabilities, payment-specific task flows, and inter-agent payment communication. Use when integrating AP2 payment capabilities into A2A multi-agent systems.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 as an A2A Extension

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for the A2A extension specification
2. Fetch `https://ap2-protocol.org/topics/ap2-a2a-and-mcp/` for protocol integration details
3. Web-search `site:github.com google-agentic-commerce AP2 a2a extension` for reference implementation
4. Web-search `site:github.com google-agentic-commerce AP2 samples a2a` for A2A-based samples

## Conceptual Architecture

### AP2 Extends A2A

AP2 is designed as a **direct extension of the A2A protocol**. It adds payment-specific capabilities to A2A's general-purpose agent-to-agent communication:

- A2A provides: tasks, messages, parts, streaming, agent cards
- AP2 adds: mandates, payment flows, VDCs, cryptographic signing, risk signals

### Why A2A is Required

As the documentation states: "A2A is required to standardize intra-agent communication — as soon as you have more than one agent you need A2A." AP2 adds payment standardization on top.

### How AP2 Rides on A2A

#### Agent Cards with AP2 Capabilities

AP2 agents declare payment support in their Agent Card:
```json
{
  "name": "MerchantAgent",
  "capabilities": {
    "extensions": [
      {
        "description": "AP2 Payment Extension",
        "required": true,
        "uri": "https://ap2-protocol.org/extension/v1"
      }
    ]
  },
  "skills": [
    {
      "id": "checkout",
      "name": "Cart and Payment",
      "description": "Handles product search and cart creation",
      "tags": ["ap2", "payment", "commerce"]
    }
  ],
  "security": [...],
  "securitySchemes": {...}
}
```

#### Mandates as A2A DataParts

AP2 mandates are transmitted as **DataParts** within A2A messages:
- Intent Mandate → DataPart in message from Shopping Agent to Merchant
- Cart Mandate → DataPart in response from Merchant to Shopping Agent
- Payment Mandate → DataPart in payment flow messages

#### A2A Tasks for Payment Flows

Each phase of the AP2 flow maps to A2A tasks:
- Product search → A2A task (SA → Merchant)
- Payment method query → A2A task (SA → CP)
- Payment processing → A2A task (Merchant → MPP)
- Challenge handling → A2A messages within existing tasks

### Message Structure

A2A messages carrying AP2 mandates include:
```json
{
  "role": "user",
  "parts": [
    {
      "type": "text",
      "text": "I want to buy a coffee maker"
    },
    {
      "type": "data",
      "data": {
        "intent_mandate": { ... }
      }
    }
  ]
}
```

### Protocol Stack

```
┌─────────────────────────────┐
│ AP2 (Mandates, VDCs, Signing)│
├─────────────────────────────┤
│ A2A (Tasks, Messages, Parts) │
├─────────────────────────────┤
│ HTTP / JSON-RPC 2.0          │
└─────────────────────────────┘
```

### Discovery

Shopping Agents discover AP2-capable merchants by:
1. Fetching Agent Cards (from `.well-known/agent-card.json` or registries)
2. Checking for AP2 extension in `capabilities.extensions[]`
3. Examining skills for payment-related capabilities
4. Verifying authentication requirements

### Watch Log

The reference samples include a `watch.log` that captures:
- Raw HTTP data (methods, URLs, request/response bodies)
- A2A message data (instructions and DataParts)
- AP2 protocol data (IntentMandate, CartMandate, PaymentMandate objects)

This is valuable for debugging the A2A ↔ AP2 integration.

### Best Practices

- Declare AP2 extension in Agent Cards for discoverable payment capabilities
- Use A2A DataParts (not TextParts) for mandate transmission
- Follow A2A task lifecycle for payment flow state management
- Implement A2A streaming for real-time payment status updates
- Use A2A authentication alongside AP2 mandate signing
- Test the full A2A + AP2 integration with the official samples
- Log both A2A and AP2 protocol data for debugging

Fetch the specification for exact A2A extension schema, DataPart structures for mandates, and Agent Card AP2 capability declaration before implementing.
