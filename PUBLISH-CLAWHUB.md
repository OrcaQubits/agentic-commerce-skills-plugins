# Publishing to ClawHub

This guide walks through publishing every plugin in this repo to the [ClawHub](https://docs.openclaw.ai/clawhub) marketplace so OpenClaw users can install them with one command.

## What gets published

The repo ships **16 plugins**, each with a Spree-style bundle of skills + agent context + hook scripts. ClawHub supports two publishing granularities and we use **both**:

| Path | Granularity | What users install |
|------|-------------|--------------------|
| `clawhub package publish` (per plugin, family `bundle-plugin`) | One slug per plugin | The whole bundle: e.g., `spree-commerce` → all 22 Spree skills + AGENTS.md + scripts in one install |
| `clawhub sync` (per skill, walks `dist/openclaw/`) | One slug per skill | A single skill: e.g., `spree-checkout` standalone, installable without the rest |

End-users get to choose: install the whole platform plugin, or pick à la carte skills.

## Prerequisites

1. **Node.js 20+** and the ClawHub CLI installed globally:

   ```bash
   npm i -g clawhub
   ```

2. **Authenticate** with ClawHub:

   ```bash
   clawhub login                 # browser flow (default)
   # or
   clawhub login --token clh_…   # headless / CI
   # or
   clawhub login --device        # device flow for remote sessions
   ```

   Verify with:

   ```bash
   clawhub whoami
   ```

3. **Generate the OpenClaw build output** from the repo root:

   ```bash
   python scripts/convert.py --platform openclaw
   ```

   This populates `dist/openclaw/<plugin-name>/` for every plugin with:

   ```
   dist/openclaw/<plugin>/
   ├── package.json              # ClawHub publish manifest (required)
   ├── .clawhubignore            # publish-ignore patterns
   ├── openclaw.plugin.json      # OpenClaw runtime manifest
   ├── AGENTS.md                 # Agent expertise as context
   ├── skills/<skill>/SKILL.md   # Each skill in its own folder
   └── scripts/*.py              # Hook scripts as standalone utilities
   ```

## Configuration

Override the defaults via environment variables before running `scripts/convert.py`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAWHUB_SCOPE` | `@orcaqubits` | npm-style scope; controls `package.json#name`. Pass `--owner <scope-without-@>` at publish time too. |
| `CLAWHUB_PLUGIN_API` | `>=2026.3.24-beta.2` | `openclaw.compat.pluginApi` semver range |
| `CLAWHUB_OPENCLAW_VERSION` | `2026.3.24-beta.2` | `openclaw.build.openclawVersion` |
| `CLAWHUB_REPO_URL` | `https://github.com/OrcaQubits/agentic-commerce-claude-plugins` | Embedded in `package.json#repository` |

Example: publish under a different scope:

```bash
CLAWHUB_SCOPE=@my-org python scripts/convert.py --platform openclaw
python scripts/publish-clawhub.py --owner my-org
```

## Publishing

Use the helper script `scripts/publish-clawhub.py`. It loops over the 16 plugins, runs `clawhub package publish` for each, and (optionally) runs `clawhub sync` for individual skills.

### Dry run first (recommended)

```bash
python scripts/publish-clawhub.py --dry-run
```

This prints every command that would run, validates `package.json` for each plugin, and uploads nothing. Always do this before a real publish.

### Publish everything

```bash
python scripts/publish-clawhub.py
```

Output:

```
=== Publishing 15 plugin(s) as bundle-plugin ===
[ucp-agentic-commerce]
  $ clawhub package publish dist/openclaw/ucp-agentic-commerce --family bundle-plugin --owner orcaqubits
  ...

=== Publishing individual skills via 'clawhub sync' ===
  $ clawhub sync --root dist/openclaw --all

=== Summary ===
  succeeded: 16
    + plugin:ucp-agentic-commerce
    + plugin:acp-agentic-commerce
    ...
    + skills-sync
```

### Granular targets

```bash
# Bundle plugins only
python scripts/publish-clawhub.py --mode plugins

# Individual skills only (clawhub sync)
python scripts/publish-clawhub.py --mode skills

# A single plugin
python scripts/publish-clawhub.py --plugin spree-commerce

# Plugin under a specific ClawHub owner/scope
python scripts/publish-clawhub.py --owner orcaqubits
```

### Manual single-plugin publish

If you prefer to invoke `clawhub` directly:

```bash
clawhub package publish dist/openclaw/spree-commerce \
  --family bundle-plugin \
  --owner orcaqubits \
  --version 1.0.0 \
  --dry-run

clawhub package publish dist/openclaw/spree-commerce \
  --family bundle-plugin \
  --owner orcaqubits
```

## After publishing

Verify each plugin landed:

```bash
clawhub package inspect openclaw-spree-commerce
clawhub package explore agentic
```

Once live, end users install with:

```bash
# Whole plugin
clawhub install spree-commerce

# One skill
clawhub install spree-checkout
```

## Versioning a new release

1. Bump `version` in `<plugin>/.claude-plugin/plugin.json`.
2. Update `.claude-plugin/marketplace.json` to match.
3. Re-run `python scripts/convert.py --platform openclaw`.
4. Publish:

   ```bash
   python scripts/publish-clawhub.py --plugin <plugin-name>
   ```

ClawHub creates a new immutable semantic-version release each time.

## Rate limits

ClawHub enforces server-side rate limits that affect publish strategy:

- **Bundle plugins**: no per-hour cap observed; all 16 plugins in this repo publish in a single run.
- **Individual skills (`clawhub sync`)**: **max 5 new skills per hour, per user**. With ~290 skills across all plugins, exhaustive per-skill publishing would take ~58 hours.

**Recommended strategy**: publish bundle plugins (`--mode plugins`) as the primary install path. Users get all skills automatically when they install a bundle. Use per-skill `sync` only for the most prominent skills you want individually discoverable in catalog search.

To trickle-publish skills over time, set up a scheduled task (cron / GitHub Actions) that runs once per hour:

```bash
# Pick one plugin to advance each hour, in rotation
clawhub --workdir dist/openclaw/$PLUGIN --dir skills sync --all
```

ClawHub will accept the first 5 new skills then return `Rate limit: max 5 new skills per hour`. Schedule the next run an hour later.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `clawhub: command not found` | `npm i -g clawhub` (Node 20+) |
| `Not authenticated` | `clawhub login`; check `clawhub whoami` |
| `package.json missing required openclaw.compat.pluginApi` | Re-run `python scripts/convert.py --platform openclaw`; the converter writes this field. |
| `Scoped package names must match the selected owner` | Either set `CLAWHUB_SCOPE` to match your ClawHub handle, or pass `--owner <handle>` matching the scope. |
| `Version 1.0.0 already exists` | Bump `version` in `<plugin>/.claude-plugin/plugin.json` (and `marketplace.json`), re-run convert, retry. |
| `Rate limit: max 5 new skills per hour` | Server-side limit on new-skill creates. Bundles are unaffected — fall back to `--mode plugins`, or schedule hourly skill batches. |
| `Scan held` after publish | ClawHub runs automated security scans; held content is visible in `clawhub dashboard` and may be released after review. |
| Plugin published but skills not searchable as individual slugs | This is expected — bundle-plugin publish does NOT auto-split into per-skill slugs. Use `clawhub sync` per plugin (subject to the rate limit above) to register individual slugs. |
| Want to retract a release | `clawhub package delete <name>` (soft delete; `undelete` to restore). |

## Reference

- ClawHub docs index: https://docs.openclaw.ai/clawhub
- CLI reference: https://docs.openclaw.ai/clawhub/cli
- Skill format spec: https://docs.openclaw.ai/clawhub/skill-format
- ClawHub Web UI / dashboard: https://docs.openclaw.ai/clawhub (login required)

All ClawHub-published content is licensed under MIT-0 by ClawHub policy. This repo's source is licensed MIT (see `LICENSE`).
