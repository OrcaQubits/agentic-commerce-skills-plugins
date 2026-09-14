---
name: nlweb-schema-org-grounding
description: Prepare and structure site content as Schema.org JSON-LD for NLWeb ingestion — covers the supported types (Recipe, Product, Movie, Event, Article, RealEstate, Course, etc.), per-type behavior in NLWeb's tool routing, JSON-LD embedding patterns in HTML, sites.xml registration, and how the `schema_object` flows through ranking back to agent results. Use when authoring or auditing the structured data on a site that will be exposed via NLWeb.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb Schema.org Grounding

> **Config layout changed upstream.** NLWeb replaced the single `site_types.xml` with two files in `config/`:
> **`sites.xml`** (site name → `itemType` list + description) and **`tools.xml`** (per-site / per-type tool
> definitions, prompts and examples, scoped by `<Site id="…">` / `<Item>` blocks). Older guidance — including any
> `site_type` / `extends` inheritance syntax — describes the retired file. **Fetch `config/sites.xml` and
> `config/tools.xml` from the live repo before editing anything.**

## Before writing code

**Fetch live references**:
1. Fetch https://schema.org/ for the canonical Schema.org vocabulary.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/sites.xml in the live repo for the **exact list of supported Schema.org types** and the tool inheritance tree per type.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-prompts.md for how per-type prompts and `<returnStruc>` shapes work.
4. Web-search `schema.org JSON-LD validator` — Google's Rich Results Test is a quick way to validate before ingest.
5. Check `AskAgent/python/methods/recipe_substitution.py`, `accompaniment.py`, `compare_items.py` for examples of how type-specific tools consume the `schema_object`.

## Conceptual Architecture

### Why Schema.org Matters to NLWeb

NLWeb's defining design choice: **results carry their full Schema.org object back to the agent**. Unlike a generic RAG system that returns text chunks, NLWeb returns structured JSON-LD — so an agent receiving a `Recipe` result gets `ingredients`, `cookTime`, `nutrition`, `recipeYield`, not just a paragraph of text. This is what makes NLWeb results *agent-actionable*.

R.V. Guha (NLWeb's author) co-created Schema.org for exactly this reason — the data was already structured; NLWeb finally exposes it to agents.

### Schema.org Types NLWeb Knows About

`tools.xml` enumerates the types with per-type tool / prompt overrides. Common types (verify the live file):

| Type | Use Case | Type-Specific Tools |
|------|----------|---------------------|
| `Recipe` | Cooking sites | recipe_substitution, accompaniment |
| `Product` | E-commerce | compare_items, item_details |
| `Movie` / `TVSeries` | Streaming/reviews | compare_items |
| `Event` | Calendars, ticketing | item_details |
| `Article` / `NewsArticle` / `BlogPosting` | News, blogs | summarize-mode default |
| `RealEstate` / `Apartment` / `House` | Listings | item_details, compare |
| `Course` | EdTech | item_details |
| `Restaurant` / `LocalBusiness` | Maps, directories | accompaniment, item_details |
| `Book` | Catalogs | compare, item_details |
| `Person` / `Organization` | Profiles | item_details |

NLWeb falls back to a default tool set for any Schema.org type not explicitly enumerated.

### JSON-LD Embedding Patterns

Schema.org JSON-LD is typically embedded in HTML via a `<script type="application/ld+json">` tag:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Recipe",
  "name": "Classic Tomato Soup",
  "url": "https://example.com/recipes/tomato-soup",
  "image": "https://example.com/images/tomato-soup.jpg",
  "author": { "@type": "Person", "name": "Jane Doe" },
  "datePublished": "2025-09-12",
  "description": "A simple weeknight tomato soup.",
  "recipeIngredient": ["6 ripe tomatoes", "1 onion", "..."],
  "recipeInstructions": [...],
  "nutrition": { "@type": "NutritionInformation", "calories": "200" },
  "cookTime": "PT30M",
  "recipeYield": "4 servings"
}
</script>
```

NLWeb's URL-list ingest path extracts this directly. The richer the JSON-LD, the more useful the result.

### The `schema_object` Field in Responses

Every NLWeb result contains:

```json
{
  "url": "...",
  "name": "...",
  "site": "...",
  "score": 0.87,
  "description": "...",
  "schema_object": { /* the full JSON-LD as ingested */ }
}
```

Agents can pattern-match on `schema_object.@type` to render appropriately, extract specific properties (e.g., `offers.price` for products), or chain to a follow-up tool call.

### sites.xml and Per-Site Registration

In addition to `config_nlweb.yaml`'s `sites:` allowlist, the demo data ships with a `sites.xml`-style registry tying site names to crawl sources and Schema.org type defaults. Check the live repo for the current registration convention — this is an area that's been evolving.

### Schema.org Required Fields by Type (high-signal subset)

| Type | Always include |
|------|----------------|
| Recipe | name, url, image, recipeIngredient, recipeInstructions, cookTime, recipeYield |
| Product | name, url, image, description, offers (price, priceCurrency, availability) |
| Article | headline, url, image, author, datePublished, description, articleBody (or summary) |
| Event | name, url, startDate, location, description |
| Movie | name, url, image, director, datePublished, genre, description |
| RealEstate | name, url, image, address, numberOfRooms, floorSize, price |

The fewer fields populated, the worse the result quality — especially for `mode=generate` answers.

### Per-Type Prompt and Tool Inheritance

`tools.xml` defines a tree:
- Root prompts apply to all types
- Per-type overrides specialize ranking, summarization, and tool selection

This is **mixed-mode programming** in action — small, type-aware LLM calls drive the response.

## Implementation Guidance

### Auditing an Existing Site

Before ingest:
1. Visit a representative page and view source — look for `<script type="application/ld+json">`.
2. Validate with Google's Rich Results Test or Schema.org validator.
3. Confirm the `@type` is one NLWeb's `tools.xml` knows about — if not, results still work but use default prompts.

### Authoring JSON-LD for NLWeb

- **Always set `@context: "https://schema.org"`** — NLWeb's parser keys off this.
- **Always include `url`** — it's the deduplication key across retrieval backends.
- **Use specific subtypes** (e.g., `Recipe` not `CreativeWork`) so type-specific tools activate.
- **Embed images and dates** — agents use them for rendering and freshness checks.
- **Nest related objects** with `@type` discriminators (e.g., `author` as `Person`, `offers` as `Offer`).

### Validating Schema Quality Post-Ingest

After loading, hit a result and inspect `schema_object`:

```bash
curl 'http://localhost:8000/ask?query=quick+dinners&site=recipes&streaming=false&mode=list' | jq '.results[0].schema_object'
```

If `schema_object` is missing key fields, fix the source HTML — not NLWeb's config.

### Adding a New Schema.org Type

If you want a custom domain (say, `Podcast` episodes) with type-specific tools:
1. Add a `<site_type>` entry in `tools.xml` referencing your `@type` value.
2. Define type-specific prompts in `prompts.xml` (or inherit defaults).
3. Optionally write a handler in `methods/` (see `nlweb-tools-framework`).
4. Reload and re-test.

### Mapping Non-Schema.org Sources

If your source isn't JSON-LD (CSV, proprietary API), map fields to Schema.org **at ingest time**, not query time. Update `rss2schema.py` or write a small adapter that emits Schema.org JSON before calling `db_load`. The richer the mapping, the better the agent experience.

### Common Pitfalls

- **`@type` is missing or non-Schema.org** — results work but type-specific tools never fire.
- **`url` is relative** — breaks deduplication; always emit absolute URLs.
- **Date format is non-ISO** — `datePublished: "2025-09-12"` works; `"Sept 12, 2025"` does not.
- **`offers` is a bare string instead of an `Offer` object** — agents lose the price field.
- **Description is too short / too generic** — ranking suffers because retrieval relies on description embeddings.

Always validate JSON-LD with an external tool before assuming ingest will work — silent parser failures are common.
