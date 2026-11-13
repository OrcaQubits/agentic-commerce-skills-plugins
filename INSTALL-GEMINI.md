# Installing Agentic Commerce Plugins for Gemini CLI

Use the generated release bundles; no conversion is needed for installation. See [the release installation guide](INSTALL-RELEASE.md#gemini-cli) for exact tag selection and both new plugins.

From a checkout of the intended release:

```shell
gemini extensions install ./dist/gemini/x402-agentic-payments
gemini extensions install ./dist/gemini/trusted-agent-protocol
gemini extensions list
```

The path is positional. There is no `--path` install flag. Review the folder-trust and extension-consent prompts; `--consent` does not answer the folder-trust prompt. To work directly on a bundle during development, use `gemini extensions link ./dist/gemini/<plugin>`.

Installing the repository URL directly installs the root UCP extension. The other 17 extensions are separate directories under `dist/gemini/`; they are not all installed by the gallery entry.

Each bundle includes `gemini-extension.json`, `GEMINI.md`, `skills/`, hook configuration, and any `scripts/`, `audit/`, and `evals/` resources. Keep the directory intact. Local installations do not follow new GitHub releases automatically.

## Maintainer conversion

```shell
python scripts/convert.py --platform gemini
python scripts/validate.py
```

The converter maps Claude tool/event names and hook paths to Gemini equivalents. Platform support evolves; use the [official extension reference](https://geminicli.com/docs/extensions/reference/) when changing the converter. See [PUBLISH-GEMINI.md](PUBLISH-GEMINI.md) for the repository's UCP gallery entry.
