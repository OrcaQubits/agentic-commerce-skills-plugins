---
name: webmcp-declarative-forms
description: Implement the WebMCP Declarative API — annotate HTML forms with toolname and tooldescription attributes for automatic tool extraction. Use when making existing forms agent-ready with minimal code changes.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# WebMCP Declarative Forms

## Before writing code

**Fetch live docs**:
1. Fetch `https://webmachinelearning.github.io/webmcp/` for the declarative form attribute specification
2. Web-search `webmcp declarative form toolname tooldescription HTML attributes` for attribute syntax and behavior
3. Web-search `site:developer.chrome.com webmcp declarative forms` for Chrome implementation details
4. Web-search `webmcp SubmitEvent agentInvoked` for the agent submission event API

## Conceptual Architecture

### What Declarative Forms Are

The Declarative API lets developers make existing HTML forms agent-ready by adding attributes — no JavaScript required for basic cases. Chrome auto-extracts form tools and exposes them to agents.

### HTML Attributes

| Attribute | Applied To | Purpose |
|-----------|-----------|---------|
| `toolname` | `<form>` | Unique tool name (becomes the tool's `name`) |
| `tooldescription` | `<form>` | Natural-language description for the agent |
| Standard `name`, `type` | `<input>`, `<select>`, `<textarea>` | Mapped to JSON Schema properties automatically |

### How It Works

1. Developer adds `toolname` and `tooldescription` to a `<form>` element
2. Browser auto-extracts form fields into a JSON Schema (input names become properties, types are inferred)
3. The form becomes a registered tool visible to agents
4. When an agent invokes the tool, the browser fills the form fields and submits
5. A `SubmitEvent` fires with `agentInvoked` property set to `true`
6. The site can detect agent submissions and handle them accordingly

### Basic Example

```html
<form toolname="searchProducts" tooldescription="Search the product catalog by keyword and price range">
  <label>
    Search: <input name="query" type="text" required />
  </label>
  <label>
    Max Price: <input name="maxPrice" type="number" min="0" />
  </label>
  <label>
    Category:
    <select name="category">
      <option value="all">All</option>
      <option value="electronics">Electronics</option>
      <option value="clothing">Clothing</option>
    </select>
  </label>
  <button type="submit">Search</button>
</form>
```

### Detecting Agent Submissions

```js
form.addEventListener("submit", (event) => {
  if (event.agentInvoked) {
    // Agent submitted this form — handle programmatically
    event.preventDefault();
    const data = new FormData(form);
    handleAgentSearch(Object.fromEntries(data));
  }
  // Otherwise, normal user submission
});
```

### Schema Inference

The browser infers JSON Schema from form fields:
- `<input type="text">` → `{ type: "string" }`
- `<input type="number">` → `{ type: "number" }`
- `<input type="email">` → `{ type: "string", format: "email" }`
- `<input required>` → Added to `required` array
- `<select>` → `{ type: "string", enum: [...options] }`
- `<input type="checkbox">` → `{ type: "boolean" }`

### When to Use Declarative vs Imperative

| Scenario | Recommended |
|----------|-------------|
| Simple search or filter forms | Declarative |
| Legacy server-rendered pages | Declarative |
| Complex multi-step interactions | Imperative |
| Dynamic SPA with state management | Imperative |
| Quick agent enablement of existing forms | Declarative |
| Tools that need user confirmation dialogs | Imperative |
| Both simple and complex on one page | Both |

### Combining Both APIs

A page can use both declarative forms and imperative tools simultaneously:
- Simple forms get `toolname`/`tooldescription` attributes
- Complex interactions use `navigator.modelContext.registerTool()`
- Both appear in the agent's tool list together

### Best Practices

- Use descriptive `toolname` values that clearly identify the action
- Write `tooldescription` for the agent, not the user — explain what the form does and what it returns
- Ensure form field `name` attributes are semantic (`query` not `q`, `maxPrice` not `mp`)
- Handle `agentInvoked` submissions gracefully — return structured data, not HTML redirects
- Test with agents to verify the auto-inferred schema matches expectations
- Add `required` attributes to mandatory fields so the schema reflects them

Fetch the specification for exact attribute names, SubmitEvent properties, and schema inference rules before implementing.
