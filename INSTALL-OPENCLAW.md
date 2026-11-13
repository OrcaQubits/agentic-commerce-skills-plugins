# Installing Agentic Commerce Plugins for OpenClaw

Use full content bundles from the selected release. See [the release installation guide](INSTALL-RELEASE.md#openclaw) for exact tag selection and the v1.1.0 workaround.

```shell
openclaw plugins install ./dist/openclaw/x402-agentic-payments
openclaw plugins install ./dist/openclaw/trusted-agent-protocol
openclaw plugins list
openclaw skills list
```

The corrected bundles use `.claude-plugin/plugin.json` for OpenClaw's content-bundle detection. They contain `skills/`, `AGENTS.md`, and executable/reference resources. They deliberately omit `openclaw.plugin.json`, which selects the native-code loader and requires a runtime entry point these content packages do not provide.

For an unchanged v1.1.0 checkout, install the source bundles instead:

```shell
openclaw plugins install ./x402-agentic-payments
openclaw plugins install ./trusted-agent-protocol
```

Review and accept OpenClaw's local-source trust prompt. Non-interactive installs require `--force` to acknowledge trust after reviewing the bundle; CI uses this only for this repository's known bundles in temporary profiles. Confirm both plugins and all 13 skills are visible. Keep their `scripts/`, `audit/`, and `evals/` directories intact. Advisory Python scripts are standalone utilities; the bundle does not provide OpenClaw-native hook enforcement.

## Registry discovery

GitHub releases and ClawHub publication are separate. Package metadata names such as `@orcaqubits/openclaw-x402-agentic-payments` do not prove a published ClawHub package exists. These two plugins are installable from the repository bundles; use registry install commands only after verifying publication. See [PUBLISH-CLAWHUB.md](PUBLISH-CLAWHUB.md) for the maintainer workflow.

## Maintainer conversion

```shell
python scripts/convert.py --platform openclaw
python scripts/test_distribution_install.py
python scripts/validate.py
```

CI additionally exercises the native OpenClaw installer in a temporary profile, checks skill discovery, and verifies that executable resources survive installation. See [OpenClaw's bundle documentation](https://docs.openclaw.ai/plugins/bundles).
