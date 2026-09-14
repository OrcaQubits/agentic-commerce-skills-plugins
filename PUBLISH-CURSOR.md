# Publishing to Cursor

Cursor (as of 2.6, May 2026) has **three distinct publishing surfaces** for AI plugins. This repo is configured to use all three; the recommended primary path for this monorepo is the **Team Marketplace** because it supports all 16 plugins in one import without requiring Anysphere review.

| Surface | Best for | Audience | Approval needed |
|---------|----------|----------|-----------------|
| **Team Marketplace** (Cursor 2.6) | Multi-plugin GitHub repos like this one | Teams/Enterprise plan members | None — admin imports a GitHub URL |
| **Public Marketplace** (cursor.com/marketplace) | Single flagship plugin | Everyone | Anysphere review |
| **cursor.directory** | Community discovery | Everyone | None — auto-detected |

References:
- Marketplace storefront: https://cursor.com/marketplace
- Plugins overview: https://cursor.com/docs/plugins
- Schema reference: https://cursor.com/docs/reference/plugins
- Official plugins repo (spec + schemas): https://github.com/cursor/plugins
- Plugin template: https://github.com/cursor/plugin-template
- Team Marketplaces (2.6 forum post): https://forum.cursor.com/t/cursor-2-6-team-marketplaces-for-plugins/153484
- Cursor 2.5 launch (marketplace debut): https://cursor.com/changelog/2-5

## Repo layout

The repo is wired for direct Cursor consumption:

```
agentic-commerce-skills-plugins/
├── .cursor-plugin/
│   └── marketplace.json         # Team Marketplace manifest — enumerates 16 plugins
├── dist/cursor/<plugin>/
│   ├── .cursor-plugin/
│   │   └── plugin.json          # Per-plugin manifest (schema-validated)
│   ├── agents/<expert>.md
│   ├── rules/<expert>.mdc
│   ├── skills/<skill>/SKILL.md
│   ├── hooks/hooks.json
│   └── scripts/check_*.py
└── scripts/
    └── validate-cursor.mjs      # Mirror of Cursor's CI validator (ajv)
```

The root `.cursor-plugin/marketplace.json` is what Cursor's Team Marketplace import reads. The `source` field on each entry points at the converted plugin directory under `dist/cursor/`.

## Path 1 — Team Marketplace (recommended for this repo)

**No review, no submission form.** Admins of a Cursor Teams/Enterprise org import any GitHub repo URL.

### What an admin does

1. In Cursor: **Settings → Plugins → Team Marketplaces → Import**
2. Paste `https://github.com/OrcaQubits/agentic-commerce-skills-plugins`
3. Cursor parses the root `.cursor-plugin/marketplace.json` and surfaces all 16 plugins
4. Admin assigns plugins to **Access Groups** (e.g., "Engineering", "Commerce-team")
5. Members in those groups see the plugins in the Cursor Plugin browser and install with one click

Teams plan = 1 marketplace per org; Enterprise = unlimited.

### Updating the marketplace

When you bump a plugin version or add a new plugin:

```bash
# 1. Update sources under <plugin>/.claude-plugin/ as usual
# 2. Regenerate the Cursor output
python scripts/convert.py --platform cursor

# 3. (Only if you added a NEW plugin) regenerate root marketplace.json
python -c "
import json, pathlib
src = json.load(open('.claude-plugin/marketplace.json'))
plugins = [{'name': p['name'], 'source': f'dist/cursor/{p[\"name\"]}', 'description': p['description']} for p in src['plugins']]
out = {'name': 'agentic-commerce', 'owner': {'name': 'Rohit Bajaj, Julekha Khatun'}, 'metadata': {'description': '...', 'version': '1.0.0'}, 'plugins': plugins}
json.dump(out, open('.cursor-plugin/marketplace.json', 'w', encoding='utf-8', newline='\n'), indent=2, ensure_ascii=False)
"

# 4. Validate before committing
node scripts/validate-cursor.mjs

# 5. Commit and push
git add .cursor-plugin/marketplace.json dist/cursor/
git commit -m "chore(cursor): bump plugin X to vY.Y.Z"
git push
```

Team Marketplaces refresh automatically — no tag required (unlike Gemini).

## Path 2 — Public Cursor Marketplace

Submit one plugin (e.g., the UCP flagship, matching what we did for Gemini) at **https://cursor.com/marketplace/publish**. Anysphere reviews each plugin before listing.

### Submission checklist (per https://cursor.com/docs/reference/plugins)

- [ ] Valid `.cursor-plugin/plugin.json` matching the JSON Schema (we validate via `node scripts/validate-cursor.mjs`)
- [ ] Unique kebab-case `name` (pattern `^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$`)
- [ ] All paths in the manifest are relative; no `..` traversal
- [ ] Every rule / skill / agent / command has frontmatter
- [ ] `README.md` documents usage clearly
- [ ] Optional `logo` is committed and referenced relatively
- [ ] For multi-plugin: `.cursor-plugin/marketplace.json` at repo root (we have this)

### Flow

1. Polish the flagship plugin's README + logo
2. Test locally by dropping it at `~/.cursor/plugins/local/<plugin-name>/` and reloading Cursor
3. Submit via the web form at https://cursor.com/marketplace/publish OR email Cursor's plugin team at `kniparko@anysphere.com` (path documented in cursor/plugin-template)
4. Wait for review

**Don't submit PRs to https://github.com/cursor/plugins** — that repo is reserved for first-party Cursor-authored plugins (all 11 entries are by Anysphere staff).

## Path 3 — cursor.directory community listing

The lowest-friction discovery surface.

1. Visit **https://cursor.directory/plugins/new**
2. Paste the GitHub repo URL
3. cursor.directory auto-detects components following the "Open Plugins" standard
4. Listing appears in the community catalog

cursor.directory is owned by the `cursor` GitHub org (https://github.com/cursor/community-plugins) but isn't gate-kept. Good for SEO and community visibility alongside whichever primary path you choose.

## Local development install

For a developer testing a plugin without going through any marketplace:

```bash
# Generate Cursor output
python scripts/convert.py --platform cursor

# Symlink (or copy) the plugin to Cursor's local plugins dir
ln -s "$(pwd)/dist/cursor/spree-commerce" ~/.cursor/plugins/local/spree-commerce

# Reload Cursor window
# (Command Palette → "Developer: Reload Window")
```

## Pre-commit validation

This repo ships `scripts/validate-cursor.mjs` which mirrors Cursor's CI validator (`ajv` against the official schemas):

```bash
npm install --no-save ajv ajv-formats
node scripts/validate-cursor.mjs
```

It checks:
- The root `.cursor-plugin/marketplace.json` validates against `marketplace.schema.json`
- Every `dist/cursor/<plugin>/.cursor-plugin/plugin.json` validates against `plugin.schema.json`
- Every `source` in `marketplace.json` resolves to a real `plugin.json`

Run before tagging any release. Cursor's own CI runs the same checks during Team Marketplace import.

## Schema notes (gotchas learned the hard way)

- **`additionalProperties: false`** on the plugin schema — any unknown key (e.g., `author.url`, which was in our pre-fix output) fails validation. The converter has been patched to drop `url` and move it to top-level `homepage`.
- **`author` object shape**: `{name, email}` only. `homepage` is a separate top-level field.
- **Name pattern**: lowercase + digits + hyphens/periods, alphanumeric at start and end.
- **`hooks` field**: accepts a string path (`"./hooks/hooks.json"`) or an inline object. The converter emits the path string when `hooks/hooks.json` exists.
- **`.mdc` rule frontmatter**: only `description`, `alwaysApply`, `globs` are recognized. No `type`, `priority`, `attachAlways`, etc.
- **MCP servers** go in a top-level `mcp.json` file (auto-discovered) OR via the `mcpServers` manifest field. Our current plugins don't ship MCP servers.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Team Marketplace import fails with schema error | Run `node scripts/validate-cursor.mjs` to find the offending plugin. |
| `additionalProperties NOT allowed` | The converter emitted an unknown key. Pull the latest converter from this repo or remove the key. |
| Plugins list as "0 plugins" after import | The `source` paths in `marketplace.json` don't resolve. Confirm `dist/cursor/` is committed (not gitignored). |
| Plugin installs but rules don't activate | Check `.mdc` frontmatter — `alwaysApply: true` for global rules, or set `globs` and `alwaysApply: false` for path-scoped. |
| Hook script not found | The converter emits `${CURSOR_PLUGIN_ROOT}/scripts/check_*.py`. Confirm `scripts/` is committed at the plugin's root. |
| Want to remove a plugin from the marketplace | Drop its entry from `.cursor-plugin/marketplace.json` and commit. Imported teams refresh automatically. |

## Reference URLs

- https://cursor.com/marketplace
- https://cursor.com/marketplace/publish
- https://cursor.com/docs/plugins
- https://cursor.com/docs/reference/plugins
- https://github.com/cursor/plugins (schemas + first-party plugins)
- https://github.com/cursor/plugin-template
- https://forum.cursor.com/t/cursor-2-6-team-marketplaces-for-plugins/153484
- https://cursor.directory/plugins
- https://cursor.com/changelog/2-5 (marketplace launch)
- https://cursor.com/blog/new-plugins (March 2026 plugin cohort)
