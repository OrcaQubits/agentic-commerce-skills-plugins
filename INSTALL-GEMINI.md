# Installing Agentic Commerce Plugins for Gemini CLI

This guide explains how to convert and install the agentic commerce plugins for [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## Prerequisites

- Python 3.9+
- Gemini CLI installed and authenticated

## Step 1: Generate Gemini CLI Extensions

From the repo root, run the conversion script:

```shell
python scripts/convert.py --platform gemini
```

This generates `dist/gemini/<plugin-name>/` for each of the 10 plugins, containing:

```
dist/gemini/<plugin-name>/
  gemini-extension.json      # Extension manifest (required)
  GEMINI.md                  # Context file (auto-loaded by contextFileName)
  hooks.json                 # Lifecycle hooks at extension root
  scripts/*.py               # Hook scripts adapted for Gemini tool names
  skills/<skill>/SKILL.md    # Skills with Claude-specific fields stripped
```

### Dry Run

Preview what will be generated without writing files:

```shell
python scripts/convert.py --platform gemini --dry-run
```

### Single Plugin

Convert only one plugin:

```shell
python scripts/convert.py --platform gemini --plugin ucp-agentic-commerce
```

## Step 2: Link the Extension

Link each plugin you want to use:

```shell
gemini extensions link dist/gemini/ucp-agentic-commerce
gemini extensions link dist/gemini/acp-agentic-commerce
gemini extensions link dist/gemini/a2a-multi-agent
# ... etc.
```

## Step 3: Verify

Check that the extension is loaded:

```shell
/extensions list
```

You should see each linked plugin. The `GEMINI.md` context file is loaded automatically, providing the expert knowledge from the agent body to Gemini.

## Step 4: Validate (Optional)

Run the validation script to confirm the generated output is well-formed:

```shell
python scripts/validate.py
```

This checks:
- All JSON files are syntactically valid
- No Claude-specific fields leaked (e.g., `allowed-tools`, `disable-model-invocation`)
- Hooks use Gemini event names (`AfterTool`/`BeforeTool`) and are at extension root
- No top-level `description` in hooks.json (not part of Gemini schema)
- All skills have required frontmatter (`name`, `description`)

## What Gets Converted

| Aspect | Claude Code (source) | Gemini CLI (generated) |
|--------|---------------------|----------------------|
| Skills | `skills/*/SKILL.md` | `skills/*/SKILL.md` (stripped `disable-model-invocation`, `allowed-tools`) |
| Manifest | `.claude-plugin/plugin.json` | `gemini-extension.json` (with `contextFileName`) |
| Context | Agent `.md` body | `GEMINI.md` (agent expertise as extension context) |
| Hooks | `hooks/hooks.json` | `hooks.json` (at extension root) |
| Hook scripts | `hooks/scripts/*.py` | `scripts/*.py` (Gemini tool names) |
| Agents | `agents/*-expert.md` | Not generated (expertise in GEMINI.md) |

### Why No agents/ Directory?

Gemini CLI extensions provide context and skills, not bundled agents. Agents are configured separately in `.gemini/agents/` (project) or `~/.gemini/agents/` (user). The agent expertise from the Claude plugins is embedded in the `GEMINI.md` context file, which Gemini CLI loads automatically.

If you want subagent functionality, you can manually create agent files in `.gemini/agents/` referencing the extension's context.

### Hooks Conversion

| Aspect | Claude Code | Gemini CLI |
|--------|------------|-----------|
| Event names | `PostToolUse` / `PreToolUse` | `AfterTool` / `BeforeTool` |
| Matcher | `Write\|Edit` / `Bash` | `write_file\|edit_file` / `run_shell_command` |
| File location | `hooks/hooks.json` | `hooks.json` (extension root) |
| Scripts location | `hooks/scripts/*.py` | `scripts/*.py` |
| Path variable | `${CLAUDE_PLUGIN_ROOT}` | `${extensionPath}${/}` |
| Timeout | Seconds (`30`) | Milliseconds (`30000`) |
| Async | `"async": true` | Stripped (Gemini hooks are synchronous; exit code 2 blocks) |

### Skill Field Changes

| Field | Claude Code | Gemini CLI |
|-------|-------------|-----------|
| `name` | Kept | Kept |
| `description` | Kept | Kept |
| `disable-model-invocation` | Present | Stripped (not recognized) |
| `allowed-tools` | Present | Stripped (not recognized) |

## Known Limitations

- **Hooks are synchronous**: Gemini CLI hooks block execution until they return. The `async: true` flag from Claude Code is stripped. Hooks are fast (~1s) so impact is minimal. Use exit code 2 from stderr to block a tool (equivalent to Claude's `sys.exit(2)`).
- **No bundled agents**: Gemini CLI extensions deliver expertise via `GEMINI.md` context, not as separate agent files. For subagent functionality, create agents in `.gemini/agents/` separately.
- **Model remapping is approximate**: Claude `opus` maps to `gemini-2.5-pro`, but capabilities may differ. The live docs fetching pattern in each skill ensures correct code regardless of model.

## Updating

When the source plugins are updated, re-run the conversion:

```shell
python scripts/convert.py --platform gemini
```

Then verify with:

```shell
python scripts/validate.py
```

## Topics

`gemini-cli` `gemini-extensions` `gemini-cli-plugin` `agentic-commerce` `ai-agents` `ai-shopping` `ai-checkout` `ai-payments` `mcp` `model-context-protocol` `a2a-protocol` `ucp` `universal-commerce-protocol` `acp` `ap2` `stripe-mpp` `webmcp` `magento2` `bigcommerce` `woocommerce` `shopify` `shopify-hydrogen` `shopify-liquid` `shopify-functions` `ecommerce` `headless-commerce` `multi-agent` `llm-tools` `ai-commerce` `google-gemini` `gemini-2` `multi-platform` `cross-platform-plugins` `ai-dev-tools`
