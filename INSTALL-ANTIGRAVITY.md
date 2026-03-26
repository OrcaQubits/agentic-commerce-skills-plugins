# Installing Agentic Commerce Plugins for Antigravity

This guide explains how to convert and install the agentic commerce plugins for [Antigravity](https://antigravity.dev) (and other AI dev tools that read `AGENTS.md` and `.agent/` directories, such as Windsurf).

> **Cursor users:** For Cursor 2.5+, use the native Cursor conversion instead — see [INSTALL-CURSOR.md](./INSTALL-CURSOR.md). It supports hooks, `disable-model-invocation`, and native subagent definitions.

## Prerequisites

- Python 3.9+
- Antigravity (or compatible AI dev tool) installed

## Step 1: Generate Antigravity Output

From the repo root, run the conversion script:

```shell
python scripts/convert.py --platform antigravity
```

This generates `dist/antigravity/` with the following structure:

```
dist/antigravity/
  AGENTS.md                          # Root summary of all 11 plugins
  <plugin-name>/                     # Per-plugin directory (x11)
    AGENTS.md                        # Expert knowledge and rules
    GEMINI.md                        # Supplemental context
    .agent/
      rules/<plugin>-rules.md        # Rule file for the plugin
      skills/<skill>/SKILL.md        # Skills with Claude fields stripped
```

### Dry Run

Preview what will be generated without writing files:

```shell
python scripts/convert.py --platform antigravity --dry-run
```

### Single Plugin

Convert only one plugin:

```shell
python scripts/convert.py --platform antigravity --plugin ucp-agentic-commerce
```

## Step 2: Install into Your Project

Copy or symlink the plugin directories you need into your project:

```shell
# Copy a single plugin
cp -r dist/antigravity/ucp-agentic-commerce/.agent/ /path/to/your/project/.agent/
cp dist/antigravity/ucp-agentic-commerce/AGENTS.md /path/to/your/project/

# Or symlink for automatic updates
ln -s "$(pwd)/dist/antigravity/ucp-agentic-commerce/.agent" /path/to/your/project/.agent
ln -s "$(pwd)/dist/antigravity/ucp-agentic-commerce/AGENTS.md" /path/to/your/project/AGENTS.md
```

### Using Multiple Plugins

To use multiple plugins, merge their `.agent/` directories:

```shell
# Copy skills from multiple plugins
mkdir -p /path/to/your/project/.agent/skills
cp -r dist/antigravity/ucp-agentic-commerce/.agent/skills/* /path/to/your/project/.agent/skills/
cp -r dist/antigravity/acp-agentic-commerce/.agent/skills/* /path/to/your/project/.agent/skills/

# Copy rules from multiple plugins
mkdir -p /path/to/your/project/.agent/rules
cp dist/antigravity/ucp-agentic-commerce/.agent/rules/* /path/to/your/project/.agent/rules/
cp dist/antigravity/acp-agentic-commerce/.agent/rules/* /path/to/your/project/.agent/rules/

# Use the root AGENTS.md as your project's AGENTS.md
cp dist/antigravity/AGENTS.md /path/to/your/project/AGENTS.md
```

## Step 3: Verify

Open your project in Antigravity. The skills should appear in the skill discovery panel, and the agent rules should be loaded from `AGENTS.md`.

## Step 4: Validate (Optional)

Run the validation script to confirm the generated output is well-formed:

```shell
python scripts/validate.py
```

## What Gets Converted

| Aspect | Claude Code (source) | Antigravity (generated) |
|--------|---------------------|------------------------|
| Skills | `skills/*/SKILL.md` | `.agent/skills/*/SKILL.md` (stripped frontmatter) |
| Agent knowledge | `agents/*-expert.md` | `AGENTS.md` + `.agent/rules/` |
| Context | Agent `.md` body | `GEMINI.md` (supplemental) |
| Hooks | `hooks/hooks.json` | N/A (not supported) |

### Fields Stripped

The following Claude-specific frontmatter fields are removed from SKILL.md files:

- `disable-model-invocation` — not recognized by Antigravity
- `allowed-tools` — not recognized by Antigravity

The `name` and `description` fields are preserved.

## Known Limitations

- **No hooks system**: Antigravity does not have lifecycle hooks. The secret detection and destructive command protection hooks from Claude Code cannot be ported. Consider using git pre-commit hooks or CI checks as alternatives.
- **No sub-agent delegation**: Antigravity does not have a sub-agent system. Expert knowledge is delivered through `AGENTS.md` and `.agent/rules/` instead of dedicated agent processes.
- **Skill discovery varies**: Different AI dev tools discover skills in different ways. If skills are not appearing, check your tool's documentation for the expected directory structure.

## Compatibility

The generated output follows the open Agent Skills standard (agentskills.io) and should work with any tool that supports:

- `AGENTS.md` — project-level agent rules
- `.agent/skills/` — skill directory convention
- `.agent/rules/` — rule file convention

This includes Antigravity, Windsurf, and other compatible AI dev tools.

## Updating

When the source plugins are updated, re-run the conversion:

```shell
python scripts/convert.py --platform antigravity
```

Then verify with:

```shell
python scripts/validate.py
```

## Topics

`antigravity` `windsurf` `windsurf-plugin` `agents-md` `agent-skills` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `ucp` `universal-commerce-protocol` `acp` `ap2` `stripe-mpp` `webmcp` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `salesforce-commerce` `sfcc` `commerce-cloud` `b2c-commerce` `b2b-commerce` `sfra` `scapi` `pwa-kit` `apex-commerce` `lwc-commerce` `einstein-ai` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `multi-platform` `cross-platform-plugins` `ai-dev-tools`
