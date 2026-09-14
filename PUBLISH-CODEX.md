# Publishing to OpenAI Codex CLI

OpenAI Codex CLI shipped a first-class plugin marketplace system in **v0.128.0 (April 30, 2026)**. This repo is wired to be added as a Codex marketplace in one command.

## What Codex's marketplace model looks like

Per https://developers.openai.com/codex/plugins/build:

- **No centralized OpenAI-hosted directory.** Anyone can publish.
- **A "marketplace" is a Git repo** containing `.agents/plugins/marketplace.json` at its root.
- **Users register a marketplace** with `codex plugin marketplace add owner/repo`.
- **Plugins are bundles** with `.codex-plugin/plugin.json` + `skills/` + `agents/` + `hooks/`.
- **Installation happens via the TUI** `/plugins` browser after a marketplace is added.

This is structurally similar to Claude Code's marketplace model — which is intentional, since both use the cross-tool `.agents/` namespace.

## Repo layout for Codex

```
agentic-commerce-skills-plugins/
├── .agents/
│   └── plugins/
│       └── marketplace.json         # Codex marketplace manifest — 16 plugins enumerated
├── dist/codex/<plugin>/
│   ├── .codex-plugin/
│   │   └── plugin.json              # Per-plugin manifest (name, version, interface, hooks)
│   ├── AGENTS.md                    # Auto-loaded context
│   ├── agents/<expert>.toml         # Subagent definitions (bundle-source path)
│   ├── skills/<skill>/SKILL.md      # Skills (bundle-source path)
│   ├── hooks/hooks.json             # Plugin-bundled hooks (v0.128+)
│   └── scripts/check_*.py           # Hook scripts as standalone utilities
```

Note: the bundle-source paths are `agents/` and `skills/` (not `.codex/agents/` and `.agents/skills/`). Codex's runtime relocates them to their canonical install locations when the plugin is installed.

## Install (end users)

### Add the marketplace and install plugins

```bash
# 1. Install Codex CLI if not present
npm install -g @openai/codex
# or
brew install --cask codex

# 2. Register this repo as a marketplace
codex plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins

# 3. Inside the Codex TUI, browse and install plugins
codex
/plugins
```

The TUI surfaces all 16 plugins. Pick one to install — Codex caches it under `~/.codex/plugins/cache/agentic-commerce/<plugin-name>/<version>/` and activates its skills, subagents, and hooks.

### Optional flags

```bash
# Pin to a specific ref (tag, branch, or commit)
codex plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins --ref v1.0.0

# Sparse-checkout (only fetch what's needed for plugin discovery)
codex plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins --sparse .agents/plugins
```

## Publishing flow (maintainer)

There's no submission step for OpenAI — anyone can publish, anyone can subscribe. The repo just needs:

1. `.agents/plugins/marketplace.json` at root (already present)
2. Each plugin bundle reachable at the `source.path` listed in the marketplace.json
3. Each plugin's `.codex-plugin/plugin.json` validates per [the manifest spec](https://developers.openai.com/codex/plugins/build)

When you bump a plugin version or add a new plugin:

```bash
# 1. Update sources under <plugin>/.claude-plugin/ and skills/ as usual
# 2. Regenerate the Codex output
python scripts/convert.py --platform codex

# 3. (Only if you added a NEW plugin) regenerate root marketplace.json
python -c "
import json, pathlib
# ... see scripts/convert.py for marketplace gen logic
"

# 4. Commit + push
git add .agents/plugins/marketplace.json dist/codex/
git commit -m 'chore(codex): bump plugin X to vY.Y.Z'
git push
```

Marketplaces refresh automatically on `codex plugin marketplace upgrade <name>` or on next cache miss — no tag required (unlike Gemini), but tagging a release helps users pin.

## Bonus: contribute to OpenAI's curated skills catalog

OpenAI maintains a separate official catalog at https://github.com/openai/skills with `.system`, `.curated`, and `.experimental` tiers. Standalone skills (without a plugin wrapper) can be submitted via PR for inclusion in the `.curated` tier. Useful as a second discovery surface — installable via Codex's built-in `$skill-installer` tool.

This is independent of the marketplace flow above.

## Plugin manifest reference (what our converter emits)

`dist/codex/<plugin>/.codex-plugin/plugin.json` conforms to https://developers.openai.com/codex/plugins/build. Fields:

| Field | Purpose |
|-------|---------|
| `name` | kebab-case plugin slug |
| `version` | semver |
| `description` | summary |
| `license` | MIT |
| `keywords` | array — surfaced in marketplace search |
| `author` | `{name, email?}` — author metadata |
| `homepage` | URL — surfaced in marketplace UI |
| `repository` | string — Git source URL |
| `hooks` | path to `./hooks/hooks.json` |
| `interface.displayName` | human-readable name |
| `interface.shortDescription` | tile/card subtitle |
| `interface.longDescription` | detail view body |
| `interface.category` | filtering category |
| `interface.websiteURL` | external link |
| `interface.developerName` | byline |

Optional fields not currently emitted: `interface.composerIcon`, `interface.logo`, `interface.screenshots`, `interface.brandColor`, `interface.privacyPolicyURL`, `interface.termsOfServiceURL`. Can be added later to enrich marketplace listings.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `codex plugin marketplace add` fails with "marketplace.json not found" | Confirm `.agents/plugins/marketplace.json` is at repo root. |
| Plugin shows in `/plugins` but won't install | The bundle's `source.path` doesn't resolve. Confirm `dist/codex/<plugin>/` is committed (not gitignored). |
| Subagent not invocable after install | Check Codex version — subagent TOML format is "evolving" per docs and minor breaks are possible across versions. |
| Hooks don't fire | Codex v0.128+ supports plugin-bundled hooks but the path-variable convention may differ from Claude's `${CLAUDE_PLUGIN_ROOT}`. Our converter copies hooks.json verbatim; scripts run as standalone utilities regardless. |
| Want to retract a plugin | Drop its entry from `.agents/plugins/marketplace.json` and commit. |

## Reference URLs

- https://developers.openai.com/codex/plugins
- https://developers.openai.com/codex/plugins/build (manifest + marketplace spec)
- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/subagents
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/changelog
- https://github.com/openai/codex (CLI source)
- https://github.com/openai/skills (curated skills catalog)
- https://agents.md (cross-tool AGENTS.md standard)
