---
name: ucp-location
description: >
  Implement the UCP Location capability (`dev.ucp.common.location`) — Search
  and Lookup for physical locations (stores, restaurants, lockers) with spatial
  relations, operating hours, amenities, and item availability. Use when
  building local pickup discovery, store finders, or fulfillment-area
  verification.
---

# UCP Location Capability

## Before writing code

**Fetch live spec**: Web-search `site:ucp.dev specification common location` and fetch the capability page plus its `search` and `lookup` operation pages for the exact Location schema, relation semantics, and filter vocabulary.

## Conceptual Architecture

### Scope

Location lives in the **common** service (`dev.ucp.common.location`), not shopping — it is shared infrastructure rather than a commerce-specific capability. It exposes physical entities: retail stores, restaurants, brand lockers, service counters.

Two flows drive it: **local pickup discovery** (where can I collect this?) and **fulfillment area verification** (do you serve this address?).

### Two operations

| Operation | Namespace | Purpose |
|-----------|-----------|---------|
| Search | `dev.ucp.common.location.search` | Free-text query + spatial relations + filters |
| Lookup | `dev.ucp.common.location.lookup` | Full details for one or more locations by identifier |

Lookup accepts the same relations and filters as Search, so a client can resolve known identifiers *and* refine by serviceability in one call.

### Spatial relations

Two relations, and the distinction is the core of the capability:

- **`distance`** — proximity to a centre point. "Stores near me."
- **`serves`** — serviceability to a target address. "Stores that will deliver here."

These are not interchangeable. The nearest store may not serve the buyer's address, and a store that serves it may not be nearby. Pick the relation that matches the question being asked.

### Filters

- **`hours`** — open at a given time
- **`amenities`** — static features, services, or capabilities, expressed as a map keyed by **reverse-DNS identifiers** with buyer-facing descriptions. The reverse-DNS keying is what lets a business declare proprietary amenities without colliding with anyone else's vocabulary.
- **`items`** — whether the business can provide referenced items at that candidate location. This is what turns a store finder into a *pickup* finder.

### Operating hours

Two layers:

- `hours` — the regular weekly schedule
- `exception_hours` — date-specific overrides (holidays, one-off closures)

Both are interpreted in the location's **IANA timezone**, which is carried on the location. Do not resolve hours against the caller's timezone or against UTC — a store's "open at 9" is local, always.

### Bindings

Location is exposed over **REST** and **MCP**.

## Implementation Guidance

- Always return the IANA timezone with a location; hours are meaningless without it.
- Apply `exception_hours` over `hours` rather than merging — an exception replaces the day, it does not add to it.
- When implementing `serves`, be explicit about what "serves" means for your business (delivery zone, shipping zone, service radius) and keep it consistent across responses.
- Combine `items` with `distance` for the common agent query — "where can I pick this up today near here" — and return the item-availability result per location rather than making the client re-check.
- Reference implementation: https://github.com/Universal-Commerce-Protocol/samples
