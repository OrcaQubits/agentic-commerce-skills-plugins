---
name: ap2-dispute-accountability
description: Implement AP2 dispute resolution and accountability — cryptographic evidence, liability allocation, chargeback handling, and audit trail construction. Use when building dispute handling, fraud investigation, or compliance systems for agentic payments.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Dispute Resolution and Accountability

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for the accountability model
2. Fetch `https://ap2-protocol.org/topics/core-concepts/` for dispute resolution details
3. Web-search `ap2 protocol dispute accountability liability mandate evidence` for accountability framework
4. Web-search `ap2 protocol chargeback fraud resolution` for dispute handling patterns

## Conceptual Architecture

### Why Accountability Matters

In agentic commerce, the traditional dispute model breaks down:
- **Who's responsible when an AI agent buys the wrong item?**
- **How do you prove the user authorized a purchase?**
- **What evidence settles a dispute between a user, agent, and merchant?**

AP2's VDC-based accountability model provides **cryptographic evidence** for every dispute scenario.

### Liability Allocation Table

| Scenario | Key Evidence | Accountability |
|----------|-------------|---------------|
| **First-party misuse** | User-signed Cart/Intent Mandate | User — signature proves authorization |
| **Agent mispick (user approved cart)** | Cart Mandate shows item, user signed | User — they approved the specific cart |
| **Agent mispick (unapproved)** | Intent Mandate vs cart discrepancy | Shopping Agent/Platform — exceeded intent |
| **Merchant non-fulfillment** | Valid mandate + payment confirmation vs absent delivery | Merchant — committed via signature |
| **Account takeover** | Authentication signals during session | CP/User — depends on auth strength evidence |
| **Man-in-the-middle** | Digital signature verification | Attack prevented — signatures invalid if tampered |
| **Price discrepancy** | Merchant-signed Cart Mandate vs charged amount | Merchant — signed specific prices |
| **Unauthorized transaction** | Absence of user signature on mandate | Platform/Agent — no valid user authorization |

### Evidence Chain

For every transaction, AP2 preserves:
1. **User's original intent** — Natural language captured in Intent Mandate
2. **User's authorization** — Cryptographic signature on the mandate
3. **Merchant's commitment** — Merchant entity signature on Cart Mandate
4. **Payment authorization** — Payment Mandate with user signature
5. **Challenge completion** — Records of 3DS/OTP challenges
6. **Transaction receipt** — Payment confirmation from MPP

### Dispute Investigation Process

1. **Collect mandates** — Gather all signed VDCs for the transaction
2. **Verify signatures** — Confirm all signatures are valid and match claimed identities
3. **Compare intent vs outcome** — Check if the purchase matches the authorized intent
4. **Check constraint compliance** — For Intent Mandates, verify constraints were respected
5. **Review risk signals** — Assess the risk context at transaction time
6. **Determine liability** — Apply the accountability rules based on evidence

### Audit Trail Requirements

Store for the full retention period (at least the refund period):
- All signed mandates (Cart, Intent, Payment)
- Agent-to-agent message logs
- Challenge records
- Payment receipts
- Risk signal snapshots
- User session authentication records

### Chargeback Handling

When a chargeback is filed:
1. Retrieve the transaction's VDC evidence
2. Verify mandate signatures
3. Compare the disputed transaction against signed mandates
4. Provide evidence to the payment network
5. The cryptographic evidence resolves most disputes definitively

### Fraud Scenarios

**AI Agent Fraud Prevention:**
- Intent Mandate captures user's exact words → agent can't claim different intent
- Cart Mandate requires user signature → agent can't forge approval
- Payment Mandate requires device attestation → agent can't self-authorize

**Merchant Fraud Prevention:**
- Merchant signs Cart Mandate → can't deny offered prices/products
- Payment receipt confirms delivery obligation
- Fulfillment tracking compared against commitment

### Best Practices

- Store all VDCs with their signatures for the full retention period
- Implement automated signature verification in dispute workflows
- Build dashboards showing intent vs outcome comparisons
- Log all risk signals at transaction time (they can't be recreated later)
- Implement the accountability table as deterministic rules
- Support both manual and automated dispute investigation
- Provide clear evidence reports for payment networks
- Test dispute scenarios explicitly during development
- Consider regulatory requirements for evidence retention (varies by jurisdiction)

Fetch the specification for exact accountability rules, evidence requirements, and retention policies before implementing dispute handling.
