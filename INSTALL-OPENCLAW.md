# Installing Agentic Commerce Plugins for OpenClaw

This guide explains how to convert and install the agentic commerce plugins for [OpenClaw](https://openclaw.ai).

## Prerequisites

- Python 3.9+
- OpenClaw installed (`npm install -g openclaw@latest`)

## Step 1: Generate OpenClaw Output

From the repo root, run the conversion script:

```shell
python scripts/convert.py --platform openclaw
```

This generates `dist/openclaw/` with the following structure:

```
dist/openclaw/
  AGENTS.md                              # Root summary of all 10 plugins
  <plugin-name>/                         # Per-plugin directory (x10)
    openclaw.plugin.json                 # Plugin manifest (id, configSchema, skills)
    AGENTS.md                            # Agent expertise as context
    skills/<skill>/SKILL.md              # Skills with Claude fields stripped
    scripts/*.py                         # Hook scripts (standalone utilities)
```

### Dry Run

Preview what will be generated without writing files:

```shell
python scripts/convert.py --platform openclaw --dry-run
```

### Single Plugin

Convert only one plugin:

```shell
python scripts/convert.py --platform openclaw --plugin ucp-agentic-commerce
```

## Step 2: Install into Your Workspace

OpenClaw discovers plugins from configured paths. Copy a plugin directory into your workspace and register it via `plugins.load.paths` in your OpenClaw config:

```shell
# Copy a single plugin into your workspace
cp -r dist/openclaw/ucp-agentic-commerce/ /path/to/your/workspace/ucp-agentic-commerce/
```

Then add the plugin path to your OpenClaw configuration (`~/.openclaw/config.json` or workspace config):

```json
{
  "plugins": {
    "load": {
      "paths": ["/path/to/your/workspace/ucp-agentic-commerce"]
    }
  }
}
```

OpenClaw reads the `openclaw.plugin.json` manifest and auto-discovers skills listed in the `skills` array. The `AGENTS.md` file provides agent expertise as workspace context — copy it to your workspace root.

### Using Skills Directly (Without Plugin Registration)

You can also copy individual skills into OpenClaw's skill directories for immediate use without plugin registration:

```shell
# Per-workspace skills (highest precedence)
cp -r dist/openclaw/ucp-agentic-commerce/skills/* /path/to/your/workspace/skills/

# Or shared skills (available across all workspaces)
cp -r dist/openclaw/ucp-agentic-commerce/skills/* ~/.openclaw/skills/
```

Verify with: `openclaw skills list`

### Using Multiple Plugins

To use multiple plugins, copy each plugin directory and register their paths:

```shell
# Copy multiple plugin directories
cp -r dist/openclaw/ucp-agentic-commerce/ /path/to/your/workspace/ucp-agentic-commerce/
cp -r dist/openclaw/acp-agentic-commerce/ /path/to/your/workspace/acp-agentic-commerce/

# Use the root AGENTS.md for a summary of all plugins
cp dist/openclaw/AGENTS.md /path/to/your/workspace/AGENTS.md
```

```json
{
  "plugins": {
    "load": {
      "paths": [
        "/path/to/your/workspace/ucp-agentic-commerce",
        "/path/to/your/workspace/acp-agentic-commerce"
      ]
    }
  }
}
```

## Step 3: Verify

Start a new session with `/new` or restart the gateway (`openclaw gateway restart`). OpenClaw will read the `openclaw.plugin.json` manifests and discover the skills automatically.

## Step 4: Validate (Optional)

Run the validation script to confirm the generated output is well-formed:

```shell
python scripts/validate.py
```

This checks:
- Root `AGENTS.md` exists
- Each plugin has `openclaw.plugin.json` with required `id` and `configSchema` fields
- Each plugin has `AGENTS.md`
- All skills have required frontmatter (`name`, `description`)
- No Claude-specific fields leaked (`disable-model-invocation`, `allowed-tools`)
- No bare Claude model names (`opus`, `sonnet`, `haiku`) in manifests

## What Gets Converted

| Aspect | Claude Code (source) | OpenClaw (generated) |
|--------|---------------------|---------------------|
| Skills | `skills/*/SKILL.md` | `skills/*/SKILL.md` (stripped `disable-model-invocation`, `allowed-tools`) |
| Agents | `agents/*-expert.md` | `AGENTS.md` (agent expertise as context) |
| Context | Agent `.md` body | `AGENTS.md` (combined agent knowledge) |
| Hook scripts | `hooks/scripts/*.py` | `scripts/*.py` (standalone utilities for manual/CI use) |
| Hooks | `hooks/hooks.json` | Not ported (see Known Limitations) |
| Manifest | `.claude-plugin/plugin.json` | `openclaw.plugin.json` (with `id`, `configSchema`, `skills`) |

### Model Remapping

Unlike Gemini/Codex which use their own model providers, OpenClaw uses `provider/model` format so models are remapped to `anthropic/claude-*`:

| Claude Model | OpenClaw Model |
|-------------|---------------|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-5` |
| `haiku` | `anthropic/claude-haiku-4-5` |

### Skill Field Changes

| Field | Claude Code | OpenClaw |
|-------|-------------|----------|
| `name` | Kept | Kept |
| `description` | Kept | Kept |
| `disable-model-invocation` | Present | Stripped (not recognized) |
| `allowed-tools` | Present | Stripped (not recognized) |

## Publishing to ClawHub

You can publish individual skills to [ClawHub](https://clawhub.ai), the public registry for OpenClaw skills:

```shell
clawhub publish dist/openclaw/<plugin>/skills/<skill> \
  --slug <skill-name> \
  --name "Skill Display Name" \
  --version 1.0.0
```

Required flags: `--slug` (skill identifier), `--name` (display name), `--version` (semver). Optional: `--changelog`, `--tags`.

Requirements: GitHub account must be at least one week old. Each skill's `SKILL.md` must have valid `name` and `description` frontmatter.

## Known Limitations

- **No hook porting**: OpenClaw hooks are TypeScript-based (`HOOK.md` + `handler.ts`) with specific events: `command:new`, `command:reset`, `command:stop`, `message:received`, `message:transcribed`, `message:preprocessed`, `message:sent`, `session:compact:before`, `session:compact:after`, `agent:bootstrap`, `gateway:startup`, and `tool_result_persist`. There are no tool-level lifecycle events (no `PostToolUse`/`PreToolUse` equivalents). Claude Code's async secret detection hooks and destructive command protection hooks cannot be ported. The Python scripts are copied to `scripts/` as standalone utilities — you can integrate them into git pre-commit hooks or CI pipelines instead.
- **No sub-agent definition files**: OpenClaw manages agents via `agents.list[]` in JSON config, not standalone `.md` or `.toml` definition files. Agent expertise is delivered via `AGENTS.md` context instead.
- **Model remapping preserves Claude models**: Unlike Gemini (which maps to `gemini-*`) and Codex (which maps to `gpt-*`), OpenClaw uses `provider/model` format so we map to `anthropic/claude-*` models. The models stay on the Anthropic provider, just reformatted.
- **Skill name convention**: OpenClaw recommends `snake_case` for the `name` field in `SKILL.md` frontmatter (e.g., `hello_world`). The source Claude Code skills use `kebab-case` (e.g., `ucp-checkout-rest`) and this is preserved as-is during conversion. If you encounter issues, rename skill `name` fields to `snake_case` in the generated files.

## Updating

When the source plugins are updated, re-run the conversion:

```shell
python scripts/convert.py --platform openclaw
```

Then verify with:

```shell
python scripts/validate.py
```

## Topics

`openclaw` `clawhub` `openclaw-plugin` `openclaw-skills` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `ucp` `universal-commerce-protocol` `acp` `ap2` `stripe-mpp` `webmcp` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `multi-platform` `cross-platform-plugins` `ai-dev-tools`
