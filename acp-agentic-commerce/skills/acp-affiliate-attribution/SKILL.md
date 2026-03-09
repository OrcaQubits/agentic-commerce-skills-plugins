---
name: acp-affiliate-attribution
description: Implement ACP affiliate attribution — privacy-preserving affiliate tracking without cookies using token-based first-touch and last-touch attribution. Use when building affiliate programs, referral tracking, or partnership attribution.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Affiliate Attribution

## Before writing code

**Fetch live docs**:
1. Web-search `site:github.com agentic-commerce-protocol rfcs affiliate_attribution` for the affiliate attribution RFC
2. Fetch `https://developers.openai.com/commerce/specs/checkout/` for how attribution integrates with checkout
3. Web-search `site:github.com agentic-commerce-protocol spec json-schema affiliate` for the schema

## Conceptual Architecture

### What Affiliate Attribution Does

ACP's affiliate attribution extension provides **privacy-preserving affiliate tracking without cookies**. It replaces traditional cookie-based tracking with structured tokens that respect buyer privacy while enabling fair commission attribution.

### Key Properties

- **Write-only** — Attribution data is sent to the merchant but NEVER echoed back in responses. This prevents information leakage.
- **Privacy-preserving** — No third-party cookies, no cross-site tracking, no browser fingerprinting
- **Token-based** — Attribution uses opaque tokens rather than personally identifiable data
- **Two attribution models**: First-touch and last-touch

### Attribution Models

| Model | Description |
|-------|-------------|
| **First-touch** | Credit goes to the first affiliate that referred the buyer |
| **Last-touch** | Credit goes to the most recent affiliate before purchase |

### How It Works

1. Affiliate generates a tracking token (opaque identifier)
2. When buyer clicks affiliate link, the agent receives the attribution token
3. Agent includes first-touch attribution data on create (`POST /checkout_sessions`) and last-touch attribution data on complete (`POST /checkout_sessions/{id}/complete`)
4. Merchant receives attribution and records it for commission processing
5. Merchant NEVER returns attribution in responses (write-only)

### Data Flow

```
Affiliate → Token → Agent → Checkout Session (attribution field) → Merchant
                                                                      ↓
                                                              Commission Processing
```

### Privacy Compliance

- No PII in attribution tokens
- Tokens are opaque — cannot be reverse-engineered to identify individuals
- Write-only prevents downstream data leakage
- Compliant with GDPR/CCPA by design
- No cross-session tracking without buyer consent

### Extension Negotiation

Like all extensions, affiliate attribution must be negotiated:
1. Agent includes `affiliate_attribution` in `capabilities.extensions[]`
2. Merchant confirms support
3. Only then is attribution data included in requests

### Use Cases

- Affiliate marketing programs
- Influencer referral tracking
- Partnership commission attribution
- Referral program management
- Marketing channel attribution

### Best Practices

- Generate unique, opaque tokens per affiliate
- Support both first-touch and last-touch models
- Process attribution asynchronously — don't block checkout
- Never echo attribution data in responses (enforce write-only)
- Build commission reports from stored attribution data
- Test with multiple attribution scenarios (direct, single affiliate, multiple affiliates)

Fetch the affiliate attribution RFC for exact token format, attribution object structure, and write-only enforcement rules before implementing.
