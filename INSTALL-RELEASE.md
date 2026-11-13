# Install x402 and Trusted Agent Protocol from a release

Both plugins are in this repository's Claude, Codex, and Cursor catalogs. A GitHub release does not automatically publish them to the platforms' curated public directories or to ClawHub.

Use **v1.1.1** for corrected Antigravity and OpenClaw bundles and repository metadata. The original **v1.1.0 tag remains unchanged**. Its Claude, Codex, Gemini, and Cursor bundles can be installed using the routes below with `v1.1.0` substituted for `v1.1.1`. For OpenClaw on v1.1.0, install the source plugin directories instead of `dist/openclaw/`. The v1.1.0 Antigravity directories lack a native plugin manifest; use the corrected release for native plugin installation.

## Get the exact release

```shell
git clone --depth 1 --branch v1.1.1 https://github.com/OrcaQubits/agentic-commerce-skills-plugins.git
cd agentic-commerce-skills-plugins
```

The release already contains generated bundles. Conversion is for maintainers; users do not need Python to discover or install the plugins. Executing their fixtures requires Python 3.11+; x402's SDK fixture also requires Node 22+ and npm. Install TAP's pinned verifier dependencies into a virtual environment before running its fixtures.

## Claude Code

```shell
claude plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins#v1.1.1
claude plugin install x402-agentic-payments@agentic-commerce
claude plugin install trusted-agent-protocol@agentic-commerce
claude plugin list
```

For a checkout of the tag, `claude plugin marketplace add .` also works. If `agentic-commerce` is already registered, check its source/ref before installing; remove and re-add that marketplace when changing the pinned release. The plugins appear in `/plugin` → Discover under this marketplace. Invoke `/x402-agentic-payments:x402-setup` or `/trusted-agent-protocol:tap-setup` in a new session.

## Codex

```shell
codex plugin marketplace add OrcaQubits/agentic-commerce-skills-plugins --ref v1.1.1
codex plugin list
codex plugin add x402-agentic-payments@agentic-commerce
codex plugin add trusted-agent-protocol@agentic-commerce
```

On clients without `plugin add`, use the `/plugins` browser after registering the marketplace. Both entries resolve to complete `dist/codex/<plugin>/` bundles. For a tag checkout, `codex plugin marketplace add .` is an equivalent local source. Existing registrations must point to the intended ref; inspect with `codex plugin marketplace list`. Keep the full bundle, including its `scripts/`, `audit/`, and `evals/` directories.

## Gemini CLI

From the tag checkout:

```shell
gemini extensions install ./dist/gemini/x402-agentic-payments
gemini extensions install ./dist/gemini/trusted-agent-protocol
gemini extensions list
```

The local path is a **positional argument**, not a `--path` option. Review and accept the source-folder trust and extension-consent prompts. `--consent` alone does not bypass folder trust. Both extensions should be listed, with seven x402 skills and six TAP skills. Installing the repository URL directly installs the root UCP extension; it does not install these two subdirectory extensions. Local copies do not automatically track GitHub releases: update the checkout and reinstall when upgrading.

## Cursor

For an exact release, copy each **entire** bundle from `dist/cursor/` into a separate directory under `~/.cursor/plugins/local/`, including hidden files:

```shell
mkdir -p ~/.cursor/plugins/local
cp -R ./dist/cursor/x402-agentic-payments ~/.cursor/plugins/local/
cp -R ./dist/cursor/trusted-agent-protocol ~/.cursor/plugins/local/
```

On PowerShell, use `New-Item -ItemType Directory -Force "$env:USERPROFILE/.cursor/plugins/local"` and `Copy-Item -Recurse -LiteralPath <bundle-path> -Destination "$env:USERPROFILE/.cursor/plugins/local"`. Start with a destination where these plugin directories do not already exist; follow Cursor's update flow for existing installs.

Reload Cursor and inspect Customize → Plugins/Skills. Local imports must be allowed by your organization. Do not use a symlink to a checkout elsewhere on disk: current Cursor skips external symlink targets. Copying only `skills/` loses the executable resources. Team admins can instead import the repository's `.cursor-plugin/marketplace.json` through Team Marketplaces, but that follows the configured branch and is not proof of an exact tagged install. No public Cursor Marketplace listing is claimed.

## Antigravity

From the corrected tag checkout:

```shell
agy plugin validate ./dist/antigravity/x402-agentic-payments
agy plugin validate ./dist/antigravity/trusted-agent-protocol
agy plugin install ./dist/antigravity/x402-agentic-payments
agy plugin install ./dist/antigravity/trusted-agent-protocol
agy plugin list --json
```

The native `plugin.json`, root `skills/`, and `rules/` directories support plugin discovery. Legacy `.agent/` files remain for existing workspace integrations. Install the entire bundle to retain each plugin's resource root; do not merge the two plugins' `scripts/` directories because their filenames overlap. Verify that the native inventory includes all seven x402 skills and all six TAP skills, not merely an installed plugin name.

## OpenClaw

From the corrected tag checkout:

```shell
openclaw plugins install ./dist/openclaw/x402-agentic-payments
openclaw plugins install ./dist/openclaw/trusted-agent-protocol
openclaw plugins list
openclaw skills list
```

Review and accept the local-source trust prompt. In a non-interactive environment, append `--force` only after reviewing the bundle to explicitly acknowledge that trust. These are content bundles detected through `.claude-plugin/plugin.json`. They contain no native JavaScript plugin entry point. Their Python advisory scripts are available as utilities; no automatic hook enforcement is claimed.

For an unchanged v1.1.0 checkout, use its Claude-format source bundles instead:

```shell
openclaw plugins install ./x402-agentic-payments
openclaw plugins install ./trusted-agent-protocol
```

The `@orcaqubits/openclaw-*` names in package metadata are publishing identifiers, not evidence of an existing ClawHub listing. Use the local release bundles unless registry publication has been verified separately.

## Verify resources after installation

Locate the installed plugin root, then run `python scripts/test_conformance.py` from that root after installing any required dependencies. It must retain `audit/source-baseline.md`, `evals/scenarios.json`, and the complete `scripts/` directory. The x402 bundle also includes the locked SDK fixture under `scripts/sdk/`. Skills-only installers can omit these resources; they are not equivalent to installing a full plugin.

## Current platform references

- [Claude plugin installation](https://code.claude.com/docs/en/discover-plugins)
- [Codex plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins)
- [Gemini extension installation](https://geminicli.com/docs/extensions/reference/)
- [Cursor local plugins and marketplaces](https://cursor.com/docs/plugins)
- [Antigravity plugin layout](https://antigravity.google/docs/build-plugins)
- [OpenClaw content bundles](https://docs.openclaw.ai/plugins/bundles)
