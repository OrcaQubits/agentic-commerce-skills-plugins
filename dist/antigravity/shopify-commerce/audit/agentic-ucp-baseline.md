# Historical Shopify migration observations

Observed 2026-11-13 during implementation. This snapshot records what informed
the migration scenarios; it is not the authority for new integration code.
Fetch the current [migration guide](https://shopify.dev/docs/apps/build/storefront-mcp),
[agent documentation](https://shopify.dev/docs/agents), and merchant tool schemas
before selecting endpoints, tool names, fields, or behavior.

At that date, the guide described removal of catalog/cart tools at `/api/mcp`
and replacement capabilities at `/api/ucp/mcp`. It listed catalog operations
`search_catalog`, `lookup_catalog`, and `get_product`, and cart operations
`create_cart`, `get_cart`, `update_cart`, and `cancel_cart`.

The guide described explicit cart creation and full replacement by `update_cart`.
This motivated regression scenarios that preserve existing lines when adding or
removing another line. The general invariant is preservation of intended cart
state; the request shape must follow the current schema.

The agent documentation required a profile on requests and described trust-based
tool access, including direct checkout completion. Customer Account MCP was
separate from this Storefront migration. Reverify both boundaries before changes.
