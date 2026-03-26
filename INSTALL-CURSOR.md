# Installing Agentic Commerce Plugins for Cursor

This guide explains how to convert and install the agentic commerce plugins for [Cursor](https://cursor.com) (2.5+), which has a native plugin system with support for rules, skills, agents, hooks, and MCP servers.

## Prerequisites

- Python 3.9+
- Cursor 2.5+ installed

## Step 1: Generate Cursor Output

From the repo root, run the conversion script:

```shell
python scripts/convert.py --platform cursor
```

This generates `dist/cursor/` with the following structure:

```
dist/cursor/
  AGENTS.md                              # Root summary of all 11 plugins
  <plugin-name>/                         # Per-plugin directory (x11)
    .cursor-plugin/
      plugin.json                        # Cursor plugin manifest
    agents/
      <name>-expert.md                   # Subagent definition (model: inherit)
    rules/
      <name>-expert.mdc                  # Agent expertise as .mdc rule (alwaysApply: true)
    skills/<skill>/SKILL.md              # Skills (disable-model-invocation kept)
    hooks/
      hooks.json                         # Hooks with Cursor event names (preToolUse/postToolUse)
    scripts/*.py                         # Hook scripts (referenced via ${CURSOR_PLUGIN_ROOT})
```

### Dry Run

Preview what will be generated without writing files:

```shell
python scripts/convert.py --platform cursor --dry-run
```

### Single Plugin

Convert only one plugin:

```shell
python scripts/convert.py --platform cursor --plugin ucp-agentic-commerce
```

## Step 2: Install into Cursor

### Option A: Copy into Project (Recommended)

Copy the plugin components into your project's `.cursor/` directories. This is the most reliable method and works with both Cursor IDE and Cursor CLI:

```shell
# Create project-level directories
mkdir -p /path/to/your/project/.cursor/rules
mkdir -p /path/to/your/project/.cursor/agents
mkdir -p /path/to/your/project/.cursor/skills

# Copy rules, agents, skills
cp dist/cursor/ucp-agentic-commerce/rules/*.mdc /path/to/your/project/.cursor/rules/
cp dist/cursor/ucp-agentic-commerce/agents/*.md /path/to/your/project/.cursor/agents/
cp -r dist/cursor/ucp-agentic-commerce/skills/* /path/to/your/project/.cursor/skills/

# Copy AGENTS.md to project root (optional context file)
cp dist/cursor/ucp-agentic-commerce/AGENTS.md /path/to/your/project/
```

**Using multiple plugins:**

```shell
for plugin in ucp-agentic-commerce acp-agentic-commerce a2a-multi-agent; do
  cp dist/cursor/$plugin/rules/*.mdc /path/to/your/project/.cursor/rules/
  cp dist/cursor/$plugin/agents/*.md /path/to/your/project/.cursor/agents/
  cp -r dist/cursor/$plugin/skills/* /path/to/your/project/.cursor/skills/
done

# Use the root AGENTS.md for a combined overview
cp dist/cursor/AGENTS.md /path/to/your/project/AGENTS.md
```

### Option B: Local Plugin Directory (Cursor IDE Only)

For the Cursor desktop IDE, you can install as a local plugin:

```shell
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)/dist/cursor/ucp-agentic-commerce" ~/.cursor/plugins/local/ucp-agentic-commerce
```

> **Note**: The Cursor CLI (`agent` command) has limited plugin discovery — it finds agents from `plugins/local/` but may not discover skills and rules. For full CLI support, use Option A above.

### Option C: Marketplace

If these plugins are published to the Cursor Marketplace, browse and install them directly from within Cursor.

## Step 3: Verify

Restart Cursor and open your project. Check that:

- Rules from `.mdc` files are loaded (check via Cursor settings > Rules)
- Skills are discoverable (type `/` in Agent chat to browse)
- Subagents appear (check via agent panel or `/agent-name` in chat)
- Hooks fire on tool use (check Cursor's output panel for hook logs)

## Step 4: Validate (Optional)

Run the validation script to confirm the generated output is well-formed:

```shell
python scripts/validate.py
```

## What Gets Converted

| Aspect | Claude Code (source) | Cursor (generated) |
|--------|---------------------|-------------------|
| Manifest | `.claude-plugin/plugin.json` | `.cursor-plugin/plugin.json` (keeps author, keywords, license) |
| Skills | `skills/*/SKILL.md` | `skills/*/SKILL.md` (`allowed-tools` stripped, `disable-model-invocation` **kept**) |
| Agent definitions | `agents/*-expert.md` | `agents/*-expert.md` (model: inherit, tools stripped) |
| Agent expertise | Agent `.md` body | `rules/*.mdc` (alwaysApply: true) + `AGENTS.md` |
| Hooks | `hooks/hooks.json` | `hooks/hooks.json` (portable! event names remapped) |
| Hook scripts | `hooks/scripts/*.py` | `scripts/*.py` (referenced via `${CURSOR_PLUGIN_ROOT}`) |

### Key Advantages Over Other Platforms

Cursor is the most complete conversion target:

- **Hooks are portable** — Cursor supports `preToolUse`/`postToolUse` lifecycle hooks, so secret detection hooks actually work (unlike Antigravity, Codex, or OpenClaw where hooks are copied as standalone scripts)
- **`disable-model-invocation` is kept** — Cursor recognizes this skill field, so skills that should not auto-invoke maintain that behavior (stripped on all other platforms)
- **Native subagent definitions** — agents are `.md` files with frontmatter (`name`, `description`, `model`, `readonly`, `is_background`)
- **Full plugin manifest** — `.cursor-plugin/plugin.json` with auto-discovery of components
- **`.mdc` rules** — agent expertise is delivered as Cursor's persistent context system

### Model Approach

All agent models are set to `inherit`, which defers to your Cursor model selection. This means:

- If you have Cursor configured to use Claude, the agents use your Claude model
- If you switch to another provider, the agents adapt automatically
- No hardcoded model IDs that could become stale

To use a specific model instead, edit `agents/*.md` frontmatter after conversion (supported values: `inherit`, `fast`, or an explicit model ID like `claude-opus-4-6`).

### Fields Stripped

The following Claude-specific fields are removed:

- `allowed-tools` — not part of Cursor's skill schema
- `tools` (in agents) — Cursor agents inherit tools from the parent agent

The following fields are **preserved** (unlike other platforms):

- `disable-model-invocation` — Cursor supports this natively
- `author`, `keywords`, `license` — kept in the plugin manifest

### Hook Conversion Details

| Aspect | Claude Code | Cursor |
|--------|-------------|--------|
| Event names | `PostToolUse`, `PreToolUse` | `postToolUse`, `preToolUse` |
| Structure | Nested (matcher -> hooks[]) | Flat (command + matcher at same level) |
| Tool names in matchers | `Write\|Edit` | `Write\|Edit` (same — Claude-compatible) |
| Script path variable | `${CLAUDE_PLUGIN_ROOT}` | `${CURSOR_PLUGIN_ROOT}` |
| Timeout | Seconds | Seconds (same) |
| `type` field | `"command"` | `"command"` (kept — Cursor also supports `"prompt"`) |
| `async` field | Supported | Stripped (not in Cursor hook schema) |
| Top-level version | Not present | `"version": 1` added |

## Known Limitations

- **Model set to `inherit`**: Agent model defers to your Cursor model selection rather than specifying a particular model.
- **Hook structure flattened**: Claude's nested matcher->hooks[] is flattened to Cursor's flat command+matcher format. Multi-hook entries become separate flat entries.
- **No `allowed-tools`**: Cursor agents inherit tool access from the parent agent, not via frontmatter.
- **Agent `readonly` and `is_background`**: Not set by default. Edit `agents/*.md` to add `readonly: true` or `is_background: true` if needed.

## Updating

When the source plugins are updated, re-run the conversion:

```shell
python scripts/convert.py --platform cursor
```

Then verify with:

```shell
python scripts/validate.py
```

## Topics

`cursor-ai` `cursor-plugin` `cursor-rules` `cursor-mdc` `cursor-agents` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `ucp` `universal-commerce-protocol` `acp` `ap2` `stripe-mpp` `webmcp` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `salesforce-commerce` `sfcc` `commerce-cloud` `b2c-commerce` `b2b-commerce` `sfra` `scapi` `pwa-kit` `apex-commerce` `lwc-commerce` `einstein-ai` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `multi-platform` `cross-platform-plugins` `ai-dev-tools`
