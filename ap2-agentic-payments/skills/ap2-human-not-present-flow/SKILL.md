---
name: ap2-human-not-present-flow
description: Implement the AP2 human-not-present transaction flow — autonomous agent shopping with Intent Mandate authorization, constraint enforcement, and merchant escalation. Use when building autonomous agent purchasing that works after the user has left.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Human-Not-Present Transaction Flow

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for the human-not-present flow specification
2. Web-search `site:github.com google-agentic-commerce AP2 human-not-present intent mandate` for samples
3. Fetch `https://ap2-protocol.org/topics/core-concepts/` for flow overview
4. Fetch `https://ap2-protocol.org/roadmap/` to check current support level (V0.1 scope)

## Conceptual Architecture

### What Human-Not-Present Means

In a human-not-present flow, the user **provides authorization upfront and then leaves**. The Shopping Agent acts autonomously within the constraints defined in the signed Intent Mandate.

### Important: Roadmap Status

The AP2 V0.1 specification focuses on **human-present scenarios**. Human-not-present support is on the V1.x roadmap. Check the latest specification for current support level.

### Flow Overview

```
Phase 1: Intent Capture (User Present)
  1. User → SA:       Expresses shopping intent ("Buy me running shoes under $150")
  2. SA → User:        Repeats back understanding for confirmation
  3. User:             Confirms via in-session authentication
  4. SA:               Creates Intent Mandate from user's expressed intent
  5. User → SA:        Signs the Intent Mandate (hardware-backed)
  6. User:             May go offline

Phase 2: Autonomous Shopping (User Absent)
  7. SA → Merchant:    Presents Intent Mandate
  8. Merchant:         Evaluates whether they can fulfill within constraints
  9. If uncertain →    Merchant may force user confirmation (escalate)
  10. If needs info →  Merchant asks clarification (update Intent Mandate)
  11. If can fulfill → Merchant creates Cart Mandate with offer

Phase 3: Authorization (May Require User)
  12. SA:              Evaluates Cart Mandate against Intent Mandate constraints
  13. If within bounds → SA proceeds with payment
  14. If outside bounds → SA rejects or escalates to user
  15. Payment processing (similar to human-present Phase 4-6)
```

### Key Differences from Human-Present

| Aspect | Human-Present | Human-Not-Present |
|--------|--------------|-------------------|
| **User involvement** | Throughout | Only at start (signing) |
| **Primary VDC** | Cart Mandate | Intent Mandate |
| **Specificity** | Exact items | Categories + constraints |
| **Agent autonomy** | Low (user confirms) | High (agent decides within bounds) |
| **Risk level** | Lower | Higher (needs more safeguards) |

### Merchant Escalation Paths

The merchant can escalate from human-not-present to human-present:

1. **SKU Selection Required** — Merchant has multiple matching products, needs user to choose → becomes human-present Cart Mandate flow
2. **Clarification Questions** — Merchant needs more information about requirements → Shopping Agent may auto-respond from Intent Mandate or ask user
3. **Force User Confirmation** — Merchant uncertain about matching, requires explicit human approval → full human-present authorization

### Constraint Evaluation

The Shopping Agent must enforce Intent Mandate constraints:
- **Price** — Is the offer within the authorized price range?
- **Category** — Does the product match authorized categories?
- **Brand** — Does the product match brand preferences?
- **Quality** — Does the product meet quality criteria?
- **TTL** — Is the Intent Mandate still valid (not expired)?

If any constraint is violated, the agent must:
- Reject the offer
- Try a different merchant
- Or escalate to the user for updated authorization

### Natural Language Audit

The Intent Mandate captures the user's actual words:
- "Buy me the cheapest running shoes under $150 in size 10"
- This natural language record provides accountability
- If the agent buys something outside this intent, the record shows the discrepancy

### Best Practices

- Capture the user's intent precisely — errors here propagate through the whole flow
- Set conservative TTLs for Intent Mandates
- Always enforce constraint checking before proceeding with payment
- Handle merchant escalation gracefully
- Implement clear logging of agent decisions for audit
- Support the escalation from human-not-present to human-present smoothly
- Notify the user of purchase completion (even though they're not present)
- Check the roadmap — full human-not-present may have limited V0.1 support

Fetch the specification for the current support level and exact Intent Mandate fields before implementing autonomous flows.
