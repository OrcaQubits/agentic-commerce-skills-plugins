---
name: shopify-agentic-ucp
description: Integrate Shopify UCP discovery, agent profiles, catalog/cart tools, and checkout handoff using the merchant's current schemas and trust tier.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify agentic UCP integration

Use for a Shopify-specific shopping agent or merchant integration. Generic protocol design belongs in `ucp-agentic-commerce:ucp-setup`; this workflow covers Shopify's current implementation.

## Fetch current references

- [Shopify agent development](https://shopify.dev/docs/agents)
- [Storefront MCP migration](https://shopify.dev/docs/apps/build/storefront-mcp)
- [Universal Commerce Protocol](https://ucp.dev/)

Follow the live agent documentation links for profiles, catalog, cart, checkout, and orders. Inspect the actual merchant's advertised capabilities and tool schemas before writing requests. Record the retrieval date, UCP version, and any SDK/CLI versions used. Prefer the official Shopify AI Toolkit/UCP CLI when it already provides the needed operation; this skill supplies implementation and validation guidance rather than duplicating that toolkit.

Fetch current endpoint locations, tool identifiers, request fields, update semantics,
and trust requirements. If those references are unavailable, limit work to conceptual
guidance or local fixture inspection; do not generate integration code from the
historical observations in `audit/agentic-ucp-baseline.md`.

## Workflow

1. Identify the merchant, buyer journey, agent profile, and allowed actions. Keep merchant Admin API access separate from buyer-facing UCP capabilities.
2. Configure discovery and the hosted agent profile; include it on every UCP request as currently specified. Validate the profile and any required signing material without embedding credentials.
3. Choose global versus merchant-scoped catalog search. Resolve actual variant identifiers, availability, and prices before building the cart.
4. Use the current cart tool schema. Preserve a complete desired cart state when updates replace the cart; test adding, removing, and retaining lines.
5. Create checkout and implement merchant handoff as the default completion path. Direct completion is available only when the live profile/trust tier and tool schema permit it. Do not infer access from discovery alone.
6. Handle changed prices, unavailable variants, buyer input requirements, and order tracking with the current tool results. Keep buyer confirmation and spending policy in the application flow.

## Validation and deliverable

Exercise discovery, signed/profile-bound request construction, catalog-to-variant mapping, cart updates retaining prior items, and checkout handoff using a development store or synthetic captured schemas. Test insufficient trust and missing buyer information. Report actual tests, remaining live-store requirements, and the exact versions used. Never treat a public endpoint as proof of direct-checkout permission.
