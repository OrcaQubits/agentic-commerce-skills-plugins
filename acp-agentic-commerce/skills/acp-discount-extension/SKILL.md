---
name: acp-discount-extension
description: Implement the ACP discount extension — discount codes, applied discounts, rejected codes, and line-item allocations. Use when adding coupon/promo code support to checkout flows.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# ACP Discount Extension

## Before writing code

**Fetch live docs**:
1. Web-search `site:github.com agentic-commerce-protocol rfcs discount_extension` for the discount extension RFC
2. Web-search `site:github.com agentic-commerce-protocol examples discount-extension` for discount examples
3. Fetch `https://developers.openai.com/commerce/specs/checkout/` for how discounts interact with checkout
4. Web-search `site:github.com agentic-commerce-protocol spec json-schema discount` for the discount JSON schema

## Conceptual Architecture

### What the Discount Extension Does

The discount extension adds coupon/promo code support to ACP checkout sessions. It's a **built-in extension** that follows the extensions framework with independent versioning.

### Extension Identity

- **Name**: `discount`
- **Version**: Calendar versioned (e.g., `discount@2026-01-27`)
- **JSONPath target**: `$.CheckoutSessionCreateRequest.discounts` and related locations

### Three Components

1. **Submitted Codes** — Agent sends `discounts.codes[]` with discount codes the buyer wants to apply
2. **Applied Discounts** — Merchant responds with successfully applied discounts, including coupon details and monetary allocations to line items
3. **Rejected Codes** — Merchant responds with codes that couldn't be applied, including error reasons

### Discount Error Codes

When a code is rejected, the merchant returns a reason:
- `discount_code_expired` — Code has expired
- `discount_code_invalid` — Code doesn't exist
- `discount_code_combination_disallowed` — Can't combine with other active discounts
- `discount_code_minimum_not_met` — Cart total below minimum threshold
- `discount_code_usage_limit_reached` — Code has been used too many times
- `discount_code_already_applied` — Code is already active on this session
- `discount_code_user_not_logged_in` — Discount requires an authenticated user
- `discount_code_user_ineligible` — User does not qualify for this discount

### Discount Allocations

When a discount is applied, the merchant shows how the discount is distributed:
- Allocations map discount amounts to specific line items using a JSONPath `path` field (e.g., `$.line_items[0]`)
- Each allocation specifies the JSONPath `path` to the target line item and the discount amount
- This allows the agent to explain exactly how the discount was applied

### Interaction with Totals

Applied discounts affect the `totals[]` array:
- `items_discount` — Total discount on items
- `discount` — Order-level discounts
- These reduce the `total` accordingly

### Extension Negotiation

The discount extension follows capability negotiation:
1. Agent includes `discount` in `capabilities.extensions[]`
2. Merchant confirms support in the response
3. If not negotiated, discount fields are ignored

### Best Practices

- Validate codes against your promotion system before applying
- Return clear error codes with human-readable messages
- Support multiple concurrent discount codes if your business allows
- Include allocations so the agent can explain the discount to the buyer
- Handle edge cases: expired during session, minimum not met after item removal
- Test code combination rules thoroughly

Fetch the discount extension RFC and JSON schema for exact field names, error code enumeration, and allocation structure before implementing.
