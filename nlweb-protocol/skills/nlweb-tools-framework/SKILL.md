---
name: nlweb-tools-framework
description: Design and implement NLWeb tools — the per-Schema.org-type handlers that turn a query into a specialized response (search, item_details, compare_items, ensemble, recipe_substitution, accompaniment, conversation_search, etc.). Covers `tools.xml`, the ToolSelector router, builtin handlers in `methods/`, writing a custom tool with a `<returnStruc>` contract, and disabling tool selection for raw retrieval. Use when extending NLWeb beyond the default query → results flow.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# NLWeb Tools Framework

> **Config layout changed upstream.** NLWeb replaced the single `site_types.xml` with two files in `config/`:
> **`sites.xml`** (site name → `itemType` list + description) and **`tools.xml`** (per-site / per-type tool
> definitions, prompts and examples, scoped by `<Site id="…">` / `<Item>` blocks). Older guidance — including any
> `site_type` / `extends` inheritance syntax — describes the retired file. **Fetch `config/sites.xml` and
> `config/tools.xml` from the live repo before editing anything.**

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/tools.md for the canonical tools framework reference.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/sites.xml for the **per-type tool inheritance tree**.
3. Read `AskAgent/python/core/router.py::ToolSelector` for how routing actually picks a tool.
4. Read existing handlers in `AskAgent/python/methods/`: `generate_answer.py`, `item_details.py`, `compare_items.py`, `ensemble_tool.py`, `recipe_substitution.py`, `accompaniment.py`.
5. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-prompts.md for the `<returnStruc>` JSON contract that handlers must satisfy.

## Conceptual Architecture

### What a "Tool" Is in NLWeb

Confusingly, "tool" means **two different things** in NLWeb depending on context:

1. **Internal tool / handler** — a Python module in `methods/` that the `ToolSelector` routes a query to (e.g., `compare_items.py`). This is the meaning used in this skill.
2. **MCP tool** — the JSON-RPC tool exposed at `/mcp` (`ask`, `list_sites`, `who`). See the `nlweb-mcp-server` skill for that meaning.

When NLWeb's docs say "tools framework," they mean (1).

### The Tool Routing Flow

For every `/ask` request:

1. `ToolSelector` (`core/router.py`) inspects the decontextualized query + detected Schema.org type.
2. It consults `tools.xml` / `tools.xml` for the candidate tools for that type.
3. It makes an LLM call (with a strict `<returnStruc>` JSON output schema) asking "which tool fits?"
4. The selected handler in `methods/<tool>.py` is invoked.
5. The handler runs retrieval + ranking + any tool-specific logic, then emits results.

### Built-In Handlers

| Handler | Purpose |
|---------|---------|
| `generate_answer.py` | RAG synthesis — used for `mode=generate` |
| `item_details.py` | Deep-dive on a single result |
| `compare_items.py` | Side-by-side comparison of 2+ results |
| `ensemble_tool.py` | Multi-tool composition (e.g., "find a recipe and pair a wine") |
| `recipe_substitution.py` | Suggest ingredient swaps in a Recipe |
| `accompaniment.py` | "Goes with" suggestions (wine for food, sides for entrée) |
| `multi_site_query.py` | Query that spans multiple sites |
| `conversation_search.py` | Search within prior conversation context |
| `statistics_handler.py` | Aggregations over indexed data |

There are also demo-specific handlers like `cricketLens.py` / `cricket_query.py` showing how to build a deeply specialized domain tool.

### The `<returnStruc>` Contract

Every LLM call NLWeb makes is paired with a `<returnStruc>` block in `prompts.xml` defining the exact JSON shape expected back. Example for tool selection:

```xml
<returnStruc>
{
  "selected_tool": "compare_items",
  "confidence": 0.92,
  "reasoning": "User explicitly asked to compare two products"
}
</returnStruc>
```

This is **mixed-mode programming** in action — the LLM output is parsed as JSON and drives Python control flow. Handlers themselves use `<returnStruc>` for their own LLM calls (rank results, generate summary, extract key fields).

### Tool Inheritance via tools.xml

`tools.xml` maps Schema.org `@type` values to allowed tools, with inheritance:

```xml
<site_type name="Recipe" extends="CreativeWork">
  <tool>search</tool>
  <tool>item_details</tool>
  <tool>recipe_substitution</tool>
  <tool>accompaniment</tool>
</site_type>
```

Tools inherit from parent types; specific overrides take precedence. The `default` site_type catches everything not enumerated.

### Disabling Tool Selection

For debugging or raw retrieval, set in `config_nlweb.yaml`:
```yaml
tool_selection_enabled: false
```

This bypasses the router entirely — every query goes through plain retrieval + ranking. Useful for:
- Diagnosing whether bad results come from retrieval or tool routing
- Reducing LLM call count on a budget
- Sites where every query has the same shape

### Tool vs Mode

Don't confuse these:
- `mode` (request param) = `list` / `summarize` / `generate` — controls the output style
- "Tool" = which handler module processes the request

A `mode=generate` query may be routed through `compare_items`, `recipe_substitution`, or `generate_answer` depending on what the router picks.

## Implementation Guidance

### Writing a Custom Tool

Add a new handler in `methods/<your_tool>.py`:

```python
# Sketch — verify base class signature in current methods/*.py files
class YourToolHandler:
    name = "your_tool"
    description = "Handles queries of pattern X for type Y"

    async def handle(self, query, site, schema_type, context, stream):
        # 1. Retrieve relevant items
        items = await context.retriever.search(query, site=site)
        # 2. Rank
        ranked = await context.ranker.rank(items, query)
        # 3. Run any tool-specific LLM call(s)
        # 4. Stream results back
        await stream.send({"results": ranked[:5]})
```

Register the tool:
1. Add to `tools.xml` (or `config_tools.yaml` if that's where the registry lives in current code).
2. Add the tool name to relevant `site_type` entries in `tools.xml`.
3. Add a `<promptString>` entry in `prompts.xml` if your tool needs an LLM call with a `<returnStruc>`.

### When to Build a Custom Tool vs Use Built-Ins

Build a custom tool if:
- Your domain has a specific query pattern not covered (e.g., "compatibility check" for hardware parts).
- Results need post-processing beyond ranking (e.g., merging two records into one).
- You need to call an external API as part of the response (e.g., live pricing lookup).

Use a built-in if:
- It's a vanilla "find + summarize" — `generate_answer.py` handles it.
- You want comparison or details — `compare_items` / `item_details`.

### Crafting a Good `<returnStruc>`

- **Be strict** about field names and types — the parser is unforgiving.
- **Include reasoning fields** (`reasoning`, `confidence`) — helps debugging and lets you log model decisions.
- **Use enums for categorical fields** — reduces hallucinations.
- **Keep it small** — every extra field is more LLM tokens and more parsing failure surface.

### Testing a Custom Tool

```bash
# Force the router to pick your tool:
curl 'http://localhost:8000/ask?query=test&site=X&streaming=false&forced_tool=your_tool'
```

(Verify `forced_tool` param name in current code — may be a different name or only available in `mode: development`.)

### Tool Ordering and Conflicts

If multiple tools could fit a query, `ToolSelector` picks one. To bias selection:
- Make your tool's description more specific
- Adjust `tools.xml` to put your tool earlier in the list for relevant types
- Increase the `<returnStruc>` `confidence` threshold in `prompts.xml`

### Common Pitfalls

- **Tool registered but never picked** — its `<promptString>` description is too vague; the router can't tell when to use it.
- **Tool runs but returns nothing** — handler is using the wrong retriever or filtering too aggressively.
- **LLM returns invalid JSON** — `<returnStruc>` is too complex or the model tier is too low; bump to `high` for that call.
- **Inheritance not applying** — `tools.xml` `extends` attribute typo'd or the parent type not defined.

Always cross-reference `methods/` and `tools.xml` in the live repo — both move fast.
