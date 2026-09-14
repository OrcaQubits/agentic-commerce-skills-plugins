---
name: nlweb-prompts-customization
description: Customize NLWeb's LLM prompts and per-Schema.org-type behavior via `prompts.xml` and `tools.xml` — covers the `<promptString>` template format, `<returnStruc>` JSON schemas, prompt inheritance, decontextualization/ranking/generate templates, per-site overrides, and pitfalls of editing prompts in place. Use when tuning answer quality, supporting a new domain, or localizing prompts.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb Prompts Customization

> **Config layout changed upstream.** NLWeb replaced the single `site_types.xml` with two files in `config/`:
> **`sites.xml`** (site name → `itemType` list + description) and **`tools.xml`** (per-site / per-type tool
> definitions, prompts and examples, scoped by `<Site id="…">` / `<Item>` blocks). Older guidance — including any
> `site_type` / `extends` inheritance syntax — describes the retired file. **Fetch `config/sites.xml` and
> `config/tools.xml` from the live repo before editing anything.**

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-prompts.md for the prompts framework reference.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/prompts.xml for the **canonical prompt templates currently shipped** — these change between releases.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/sites.xml for per-type prompt inheritance.
4. Inspect `AskAgent/python/core/prompts.py` to see how prompts are loaded and parameterized.
5. Cross-reference with handlers in `methods/` to see which prompt each LLM call site uses.

## Conceptual Architecture

### Two XML Files Drive Prompt Behavior

| File | Purpose |
|------|---------|
| `prompts.xml` | Defines `<promptString>` templates and their `<returnStruc>` JSON output contracts |
| `tools.xml` | Maps Schema.org `@type` → tool list + per-type prompt overrides, with inheritance |

### The `<promptString>` Template

A typical prompt entry:

```xml
<promptString name="decontextualize_query">
  <description>Rewrite the user's query to be standalone, given prior conversation.</description>
  <input>
    <field name="prev_queries" type="array" />
    <field name="current_query" type="string" />
  </input>
  <text>
Given the prior queries: {prev_queries}
And the current query: {current_query}
Return a standalone version of the current query.
  </text>
  <returnStruc>
{
  "decontextualized": "the standalone query as a single string"
}
  </returnStruc>
</promptString>
```

The exact tag names may differ — verify the live `prompts.xml`. The pattern: human-readable description, input schema, prompt text with `{placeholders}`, JSON output contract.

### Per-Type Prompt Inheritance

`tools.xml` uses `extends` to inherit prompts up a type hierarchy:

```xml
<site_type name="Recipe" extends="CreativeWork">
  <prompt name="rank_results" override="rank_results_recipe" />
  <tool>recipe_substitution</tool>
</site_type>
```

When the handler asks for the `rank_results` prompt at runtime, it walks the type chain: `Recipe → CreativeWork → default`, taking the first override.

### Prompt Categories

Common prompt types (verify against live file):

| Category | Used For |
|----------|----------|
| `decontextualize_query` | Rewrite "what about the second one?" → "tell me about <item X>" |
| `detect_item_type` | Identify Schema.org type the user is asking about |
| `select_tool` | Router decides which `methods/` handler to invoke |
| `rank_results` | LLM scores retrieved items by relevance |
| `summarize_results` | `mode=summarize` condensation |
| `generate_answer` | `mode=generate` RAG synthesis |
| `extract_key_fields` | Pull specific Schema.org properties for the answer |

### The `<returnStruc>` Contract

Every LLM call has a strict JSON output schema. NLWeb parses the response as JSON and crashes if it doesn't validate. This is intentional — mixed-mode programming requires deterministic parsing.

Tips for writing `<returnStruc>`:
- Keep the JSON **minimal** — every field is more tokens.
- Use **enums** for categorical outputs to reduce hallucinations.
- Always include a `reasoning` field — invaluable for debugging.
- Don't nest arbitrarily — flat JSON parses more reliably.

### Localization

Prompts are plain text — translate them to localize. NLWeb doesn't have first-class i18n; site operators fork the prompt file per locale (or load locale-specific files). Verify whether the runtime supports per-request locale selection in the current release.

### Custom Domain Prompts

To add prompts for a new Schema.org type (or a custom type):

1. Add `<site_type name="YourType" extends="..."/>` in `tools.xml`.
2. Add `<promptString>` entries with names like `rank_results_yourtype`, `generate_answer_yourtype` in `prompts.xml`.
3. Reference them via `<prompt name="rank_results" override="rank_results_yourtype"/>` in the site_type.
4. Restart; verify by query.

## Implementation Guidance

### Editing a Prompt Safely

Prompts are upgrade-fragile. Strategy:
1. **Fork `prompts.xml`** to a site-specific file (e.g., `prompts_mysite.xml`).
2. Load it via the config option (verify whether NLWeb supports a `prompts_file:` setting per site — varies by release).
3. If no per-site option exists, accept that you'll re-merge on upgrade.

### Tuning Answer Quality

In order of cost-effectiveness:

1. **Fix the data** (better Schema.org → better answers). Most "bad answer" complaints are upstream of the prompt.
2. **Increase the model tier** for the failing call site (low → high in `config_llm.yaml`).
3. **Tighten the `<returnStruc>`** so the model can't ramble.
4. **Edit the prompt text** to give clearer instructions or examples.
5. **Add per-type overrides** so each domain gets a tailored prompt.

### Debugging a Prompt

- Set `tool_selection_enabled: false` to bypass routing and isolate the prompt under test.
- Hit `/ask` with `mode=list` to skip generate-mode prompts entirely.
- Add a `reasoning` field to the `<returnStruc>` and log it.
- Run the prompt manually in the LLM provider's playground with realistic inputs.
- Use a debugger / log breakpoint in `core/prompts.py` to see the fully-interpolated prompt.

### Common Prompt Failures

- **Model returns invalid JSON** — `<returnStruc>` is too complex, model tier too low, or prompt text is ambiguous. Bump to high tier and simplify.
- **Model returns extra fields** — make the schema stricter; explicitly forbid extras in the prompt text.
- **Inheritance doesn't apply** — typo in `extends` or `override` attribute; check exact XML attribute names against the live file.
- **Localized prompts break parsing** — `<returnStruc>` field names must stay English; only the human-facing prompt text translates.
- **Long prompts cost too much** — every `/ask` triggers multiple LLM calls; even a small prompt-length increase multiplies.

### Prompts Are Per-Call-Site, Not Per-Query

A single `/ask` invocation may use 3-5 different prompts (decontextualize, select tool, rank, summarize). Editing one only affects that call site. Use call-site logs to confirm which prompt fired.

### Versioning Prompt Changes

Prompts are config — version them in git alongside your other config files. When upgrading NLWeb, diff the upstream `prompts.xml` against yours to catch new prompts you should adopt.

Always re-fetch `prompts.xml` and `tools.xml` from the live repo before customizing — XML attribute names and prompt template syntax evolve.
