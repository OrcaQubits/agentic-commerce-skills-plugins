# Installing Agentic Commerce Plugins for Codex

The repository marketplace registers 18 plugins. See [the release installation guide](INSTALL-RELEASE.md#codex) for pinned releases, upgrade considerations, and fixture prerequisites.

```shell
codex plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins --ref v1.1.1
codex plugin list
codex plugin add x402-agentic-payments@agentic-commerce
codex plugin add trusted-agent-protocol@agentic-commerce
```

On clients without `plugin add`, install through the `/plugins` browser after adding the marketplace. For a local release checkout, use `codex plugin marketplace add .`. Inspect existing source registrations with `codex plugin marketplace list` before changing release pins.

The catalog is `.agents/plugins/marketplace.json`; entries point to `dist/codex/<plugin>/`. Each full bundle contains `.codex-plugin/plugin.json`, `skills/`, `agents/`, context, hooks, and executable/reference resources. These are plugin-root paths: the generated bundle does not contain the old `.codex/agents` and `.agents/skills` source layout. Use the native plugin installer to preserve all resources.

Start a new session after installation. Confirm that the plugin is enabled and its skills are listed; a marketplace entry alone is not an installed plugin.

## Maintainer conversion

```shell
python scripts/convert.py --platform codex
python scripts/validate_inventory.py
python scripts/test_distribution_install.py
```

See [official plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins). Repository marketplaces are separate from OpenAI's curated public plugin directory; this repository's registration does not imply a public listing.
