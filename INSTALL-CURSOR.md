# Installing Agentic Commerce Plugins for Cursor

See [the release installation guide](INSTALL-RELEASE.md#cursor) for exact release selection, Windows commands, and both new plugins.

## Install an exact release locally

From the chosen tag checkout, copy each complete bundle, including `.cursor-plugin/`, into Cursor's local plugin directory:

```shell
mkdir -p ~/.cursor/plugins/local
cp -R ./dist/cursor/x402-agentic-payments ~/.cursor/plugins/local/
cp -R ./dist/cursor/trusted-agent-protocol ~/.cursor/plugins/local/
```

Use a destination where those plugin directories do not already exist; follow Cursor's update flow for existing installations. Reload Cursor and inspect Customize for the plugins and their seven x402 / six TAP skills. Local plugin imports must be permitted by organization policy.

Copy the entire bundle: `skills/`, `rules/`, `agents/`, `hooks/`, `scripts/`, `audit/`, and `evals/` belong together. Copying just the skills drops conformance resources. External symlinks into `~/.cursor/plugins/local` are skipped by current Cursor, so copy the directories instead.

## Team marketplace discovery

An administrator can import this repository through Dashboard → Plugins & MCPs → Team Marketplaces. The root `.cursor-plugin/marketplace.json` registers all 18 plugins, including x402 and Trusted Agent Protocol. Review marketplace access and refresh settings, then find and install plugins in Customize. This tracks the configured branch; use a local tag checkout for a reproducible release audit. No public Cursor Marketplace listing is claimed.

## Maintainer conversion

```shell
python scripts/convert.py --platform cursor
node scripts/validate-cursor.mjs
python scripts/test_distribution_install.py
```

The Node validator requires `ajv` and `ajv-formats` and fetches current official schemas. See [Cursor's plugin documentation](https://cursor.com/docs/plugins) for current local-import and marketplace behavior.
