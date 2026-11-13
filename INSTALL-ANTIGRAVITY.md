# Installing Agentic Commerce Plugins for Antigravity

Use the native plugin bundles in v1.1.1 or later. The v1.1.0 Antigravity output lacks `plugin.json` and cannot be installed as a native plugin. See [the release installation guide](INSTALL-RELEASE.md#antigravity) for release pinning and fixture prerequisites.

```shell
agy plugin validate ./dist/antigravity/x402-agentic-payments
agy plugin validate ./dist/antigravity/trusted-agent-protocol
agy plugin install ./dist/antigravity/x402-agentic-payments
agy plugin install ./dist/antigravity/trusted-agent-protocol
agy plugin list --json
```

Install the entire directory. Confirm that the inventory contains seven x402 skills and six TAP skills, not just plugin names. The bundles include a native `plugin.json`, root `skills/`, `rules/AGENTS.md`, and the scripts, source baselines, and evaluations used by conformance skills.

The older `.agent/skills/` and `.agent/rules/` layout remains for compatibility with existing workspace integrations. Native installation uses root `skills/`. Copying or merging only `.agent/` drops the plugins' resource roots; do not merge the two `scripts/` directories, whose filenames overlap. Windsurf compatibility is limited to the instruction files that its current client supports; an Antigravity plugin install is not a Windsurf-native installation.

## Maintainer conversion

```shell
python scripts/convert.py --platform antigravity
python scripts/test_distribution_install.py
python scripts/validate.py
```

See [Antigravity's plugin layout](https://antigravity.google/docs/build-plugins) and [skill discovery](https://antigravity.google/docs/skills). This converter supplies skills and context; it does not claim automatic hook enforcement or a curated public marketplace listing.
