---
name: acp-extensions-authoring
description: Author custom ACP extensions — composable protocol add-ons with JSONPath targeting, schema composition, and independent versioning. Use when building proprietary or domain-specific extensions beyond the built-in ones.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Custom Extension Authoring

## Before writing code

**Fetch live docs**:
1. Web-search `site:github.com agentic-commerce-protocol rfcs extensions` for the extensions framework RFC
2. Web-search `site:github.com agentic-commerce-protocol examples` for extension examples
3. Fetch `https://developers.openai.com/commerce/specs/checkout/` for how extensions integrate with checkout
4. Study the built-in discount extension as a reference: web-search `site:github.com agentic-commerce-protocol rfcs discount_extension`

## Conceptual Architecture

### What Extensions Are

Extensions are **composable, optional add-ons** that augment ACP's core capabilities. They allow the protocol to grow without bloating the core spec — new features are added as extensions with independent lifecycles.

### Extension Properties

Every extension defines:
- **Name** — Core extensions use simple names (`discount`); third-party use reverse-domain (`com.example.loyalty`)
- **Version** — Calendar versioned (`YYYY-MM-DD`)
- **Parent capability** — `extends` field linking to the parent (e.g., extends `checkout`)
- **JSONPath targets** — Where in the core schema this extension adds fields
- **Schema** — JSON Schema for the extension's data

### JSONPath Targeting

Extensions use JSONPath (RFC 9535) to inject fields into core schema locations:
- `$.CheckoutSessionCreateRequest.discounts` — Add fields to the create request
- `$.CheckoutSession.discounts` — Add fields to the response
- Multiple targets per extension are allowed

### Extension Lifecycle

```
draft → experimental → stable → deprecated → retired
```

- **draft** — In development, not for production
- **experimental** — Available for testing, may change
- **stable** — Production-ready, backwards-compatible changes only
- **deprecated** — Still functional, but replacement available
- **retired** — No longer supported

### Schema Composition Rules

- Extension schemas are composed alongside (not inside) core schemas
- Extensions must not conflict with core fields
- Extensions must not introduce authentication bypasses
- Extension data follows the same PCI/PII rules as core fields
- Extensions can reference other extensions (dependency chain)

### Naming Conventions

- **Core extensions**: Simple lowercase names — `discount`, `intent_traces`, `affiliate_attribution`
- **Third-party**: Reverse-domain notation — `com.mycompany.loyalty`, `io.myplatform.subscription`

### Built-in Extensions as Reference

Study these before authoring custom extensions:
1. **Discount** — Discount codes, applied/rejected discounts, allocations
2. **Intent Traces** — Cart abandonment signals with reason codes
3. **Affiliate Attribution** — Privacy-preserving attribution tracking

### Custom Extension Ideas

- Loyalty program integration
- Subscription management
- Gift wrapping options
- Delivery instructions
- Tax exemption certificates
- Custom buyer preferences

### Best Practices

- Start in `draft` lifecycle, graduate through `experimental` to `stable`
- Use reverse-domain naming for all non-core extensions
- Define clear JSON Schemas with validation rules
- Document the extension's purpose, fields, and interaction with core checkout
- Test that your extension survives capability negotiation pruning
- Version independently from the core protocol

Fetch the extensions framework RFC for the exact extension manifest structure, JSONPath targeting syntax, and schema composition rules before implementing.
