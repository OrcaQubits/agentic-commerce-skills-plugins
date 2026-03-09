---
name: ap2-merchant-agent
description: Build an AP2 Merchant Agent — the seller-side agent that receives intent mandates, searches product catalogs, creates signed cart mandates, and represents the merchant in agentic transactions. Use when implementing the Merchant Endpoint role.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Merchant Agent Implementation

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for Merchant Endpoint responsibilities
2. Web-search `site:github.com google-agentic-commerce AP2 samples roles merchant_agent` for reference implementation
3. Web-search `site:github.com google-agentic-commerce AP2 merchant cart mandate` for Cart Mandate creation
4. Fetch SDK docs for merchant-side agent patterns

## Conceptual Architecture

### What the Merchant Agent Does

The Merchant Agent (ME) **represents the seller** in AP2 transactions:

1. **Receives Intent Mandates** from Shopping Agents
2. **Searches product catalog** for matching items
3. **Creates Cart Mandates** with specific product offers, prices, and totals
4. **Signs Cart Mandates** with the merchant entity's signature
5. **Handles clarification requests** when intent is ambiguous
6. **Supports the payment flow** by forwarding to Payment Processor

### Agent Card

The Merchant Agent's Agent Card advertises:
- AP2 extension support with supported payment methods
- Skills related to product search, cart creation, order management
- Product categories and capabilities
- Authentication requirements for Shopping Agents

### Key Responsibilities

#### Intent Processing
- Parse incoming Intent Mandates from Shopping Agents
- Match intent against product catalog
- Determine if the intent can be fulfilled within constraints
- Decide whether to proceed, request clarification, or reject

#### Cart Mandate Creation
- Select matching products from catalog
- Calculate prices, taxes, shipping, and totals
- Build the Cart Mandate with W3C Payment Request API structure
- Include all line items with individual pricing
- Sign the Cart Mandate with the merchant entity's key

#### Merchant Signature
The merchant signature is critical:
- It's an **entity-level** signature (the merchant organization, not the AI agent)
- It guarantees product availability at the stated prices
- It commits the merchant to fulfillment
- Key management must be handled at the organization level

#### Escalation Decisions
When facing ambiguous intent, the merchant can:
- **Offer choices** — Present multiple matching products for user selection
- **Ask clarifications** — Request more specific requirements
- **Force human-present** — Require the user to confirm directly
- **Reject** — Decline the intent if it can't be fulfilled

### Catalog Integration

The Merchant Agent needs access to:
- **Product catalog** — Names, descriptions, SKUs, images
- **Inventory** — Real-time stock availability
- **Pricing** — Current prices, discounts, taxes
- **Shipping** — Available shipping methods, costs, timeframes
- **Policies** — Return policy, refund period, terms

### Payment Method Advertisement

Cart Mandates include supported payment methods:
```json
"method_data": [
  {
    "supportedMethods": "https://processor.example.com/pay",
    "data": { "merchant_id": "..." }
  }
]
```

### Multi-Merchant Scenarios

A Shopping Agent may contact multiple merchants:
- Each merchant independently evaluates the Intent Mandate
- Each returns their own Cart Mandate
- The Shopping Agent compares offers on behalf of the user
- The merchant should respond quickly to be competitive

### Best Practices

- Sign Cart Mandates at the entity level, not the agent level
- Include all items with clear descriptions and prices
- Respond to Intent Mandates promptly — the Shopping Agent may be comparing merchants
- Handle out-of-stock gracefully with alternatives or clear messaging
- Implement proper key management for merchant signing keys
- Validate incoming Intent Mandates for authenticity
- Keep catalog data fresh — stale prices cause disputes
- Log all Cart Mandate creation for audit trail

Fetch the specification for exact Merchant Agent requirements, Cart Mandate creation process, and signing formats before implementing.
