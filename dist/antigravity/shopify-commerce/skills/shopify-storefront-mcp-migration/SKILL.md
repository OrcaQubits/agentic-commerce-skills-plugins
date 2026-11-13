---
name: shopify-storefront-mcp-migration
description: >
  Migrate removed Shopify Storefront MCP catalog/cart tools to UCP, including
  renamed tools, agent profiles, full-cart replacement semantics, and checkout
  handoff.
---

# Migrate Shopify Storefront MCP to UCP

Fetch the [official migration guide](https://shopify.dev/docs/apps/build/storefront-mcp) and [agent documentation](https://shopify.dev/docs/agents) before modifying integrations. Resolve current endpoint locations, removal status, tool names, request schemas, and update semantics from these references and the merchant's advertised schema. Record the retrieval date and selected versions. Historical observations are in `audit/agentic-ucp-baseline.md`; they must not substitute for live verification. If current references are unavailable, explain the gap and limit work to inventory and conceptual migration planning.

## Migration workflow

1. Find old endpoints, tool names, cart persistence, checkout links, and retry handlers. Distinguish Storefront MCP from Customer Account MCP; do not migrate the account service merely because both use MCP.
2. Build an old-to-new endpoint and tool map from official documentation and the live merchant schema. Identify catalog search/detail operations and cart creation, retrieval, update, and cancellation capabilities without assuming their names or parameters.
3. Add the agent profile on each UCP request and configure the current authentication/signing requirements. Keep profile trust tiers explicit.
4. Verify whether cart creation is explicit and whether updates patch or replace state. Implement the documented semantics; if updates replace the cart, reconstruct all desired lines and retained fields from trusted state instead of sending only a newly added item.
5. Use the current checkout tool and buyer handoff flow. Request direct completion only when the agent's current access tier permits it. Migrate policy/FAQ calls through the documented Ask capability.
6. Maintain an intentional compatibility boundary for persisted carts; do not reinterpret a legacy cart ID as a UCP cart without checking the migration contract. Add telemetry for old-client calls and remove the old path after the rollout criteria are met.

## Required regressions

- A cart with two lines keeps both when a third line is added.
- Removing a line produces the complete desired replacement cart.
- Missing profile or insufficient trust produces an actionable result without an unauthorized checkout attempt.
- Account MCP behavior is preserved unless its own documentation requires a change.
- Stale prices, invalid variant IDs, changed schemas, and unknown legacy cart IDs are handled explicitly.

Deliver a mapping table, versioned integration changes, synthetic or development-store regression results, and rollout/rollback criteria. Link to `shopify-commerce:shopify-agentic-ucp` for the full replacement workflow.
