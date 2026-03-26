# Installing Agentic Commerce Plugins for OpenAI Codex CLI

This guide explains how to convert and install the agentic commerce plugins for [OpenAI Codex CLI](https://github.com/openai/codex).

## Prerequisites

- Python 3.9+
- OpenAI Codex CLI installed

## Step 1: Generate Codex CLI Output

From the repo root, run the conversion script:

```shell
python scripts/convert.py --platform codex
```

This generates `dist/codex/` with the following structure:

```
dist/codex/
  AGENTS.md                              # Root summary of all 11 plugins
  <plugin-name>/                         # Per-plugin directory (x11)
    AGENTS.md                            # Agent expertise as context
    .codex/
      agents/<name>-expert.toml          # Subagent definition
    .agents/
      skills/<skill>/SKILL.md            # Skills with Claude fields stripped
    scripts/*.py                         # Hook scripts (standalone utilities)
```

### Dry Run

Preview what will be generated without writing files:

```shell
python scripts/convert.py --platform codex --dry-run
```

### Single Plugin

Convert only one plugin:

```shell
python scripts/convert.py --platform codex --plugin ucp-agentic-commerce
```

## Step 2: Install into Your Project

Copy the plugin directories you need into your project:

```shell
# Copy a single plugin
cp -r dist/codex/ucp-agentic-commerce/.codex/ /path/to/your/project/.codex/
cp -r dist/codex/ucp-agentic-commerce/.agents/ /path/to/your/project/.agents/
cp dist/codex/ucp-agentic-commerce/AGENTS.md /path/to/your/project/AGENTS.md
```

### Using Multiple Plugins

To use multiple plugins, merge their directories:

```shell
# Copy subagents from multiple plugins
mkdir -p /path/to/your/project/.codex/agents
cp dist/codex/ucp-agentic-commerce/.codex/agents/* /path/to/your/project/.codex/agents/
cp dist/codex/acp-agentic-commerce/.codex/agents/* /path/to/your/project/.codex/agents/

# Copy skills from multiple plugins
mkdir -p /path/to/your/project/.agents/skills
cp -r dist/codex/ucp-agentic-commerce/.agents/skills/* /path/to/your/project/.agents/skills/
cp -r dist/codex/acp-agentic-commerce/.agents/skills/* /path/to/your/project/.agents/skills/

# Use the root AGENTS.md as your project's AGENTS.md
cp dist/codex/AGENTS.md /path/to/your/project/AGENTS.md
```

## Step 3: Verify

Open your project directory and run `codex`. Codex walks from the git root down to your current working directory, concatenating all `AGENTS.md` files it finds. Skills in `.agents/skills/` are auto-discovered.

Verify subagents are loaded:

```shell
# Check that .codex/agents/*.toml files are present
ls .codex/agents/
```

## Step 4: Validate (Optional)

Run the validation script to confirm the generated output is well-formed:

```shell
python scripts/validate.py
```

This checks:
- `AGENTS.md` exists for each plugin
- `.codex/agents/*.toml` files contain required fields (`name`, `description`, `developer_instructions`)
- No Claude model names (`opus`, `sonnet`, `haiku`) leaked into agent TOML files
- All skills have required frontmatter (`name`, `description`)
- No Claude-specific fields leaked (`disable-model-invocation`, `allowed-tools`)

## What Gets Converted

| Aspect | Claude Code (source) | Codex CLI (generated) |
|--------|---------------------|----------------------|
| Skills | `skills/*/SKILL.md` | `.agents/skills/*/SKILL.md` (stripped `disable-model-invocation`, `allowed-tools`) |
| Agents | `agents/*-expert.md` | `.codex/agents/*.toml` (TOML subagent definition) |
| Context | Agent `.md` body | `AGENTS.md` (agent expertise as context) |
| Hook scripts | `hooks/scripts/*.py` | `scripts/*.py` (standalone utilities for manual/CI use) |
| Hooks | `hooks/hooks.json` | Not ported (see Known Limitations) |
| Manifest | `.claude-plugin/plugin.json` | Not generated (Codex has no manifest) |

### Model Remapping

| Claude Model | Codex Model |
|-------------|-------------|
| `opus` | `gpt-5.4` |
| `sonnet` | `gpt-5.4-mini` |
| `haiku` | `gpt-5.4-mini` |

### Skill Field Changes

| Field | Claude Code | Codex CLI |
|-------|-------------|-----------|
| `name` | Kept | Kept |
| `description` | Kept | Kept |
| `disable-model-invocation` | Present | Stripped (not recognized) |
| `allowed-tools` | Present | Stripped (not recognized) |

## Known Limitations

- **No per-tool lifecycle hooks**: Codex CLI does not have `PostToolUse`, `PreToolUse`, or any per-tool-execution hook equivalent. Claude Code's async secret detection hooks and destructive command protection hooks (Magento 2, WooCommerce, BigCommerce) cannot be ported. The Python scripts are copied to `scripts/` as standalone utilities — you can integrate them into git pre-commit hooks or CI pipelines instead.
- **Codex uses execution policy rules instead of hooks**: For command protection, Codex uses Starlark-based [execution policy rules](https://developers.openai.com/codex/rules) in `~/.codex/rules/`. These are a different paradigm from Claude Code's `PreToolUse` hooks.
- **No manifest file**: Unlike Gemini CLI (which uses `gemini-extension.json`), Codex CLI has no extension manifest. Plugin metadata (name, version, description) is not carried over.
- **Model remapping is approximate**: Claude `opus` maps to `gpt-5.4`, but capabilities differ. The live docs fetching pattern in each skill ensures correct code regardless of model. You can change the model in each `.toml` file or in your `~/.codex/config.toml`.
- **AGENTS.md size limit**: Codex imposes a 32 KiB limit (`project_doc_max_bytes`) on concatenated `AGENTS.md` content. If using multiple plugins, the combined context may approach this limit. Consider using only the plugins you need, or increase the limit in your `~/.codex/config.toml`.

## Updating

When the source plugins are updated, re-run the conversion:

```shell
python scripts/convert.py --platform codex
```

Then verify with:

```shell
python scripts/validate.py
```

## Topics

`codex-cli` `openai-codex` `codex-agents` `codex-plugin` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `ucp` `universal-commerce-protocol` `acp` `ap2` `stripe-mpp` `webmcp` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `salesforce-commerce` `sfcc` `commerce-cloud` `b2c-commerce` `b2b-commerce` `sfra` `scapi` `pwa-kit` `apex-commerce` `lwc-commerce` `einstein-ai` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `multi-platform` `cross-platform-plugins` `ai-dev-tools`
