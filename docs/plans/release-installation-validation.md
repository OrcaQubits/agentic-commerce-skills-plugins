# Release installation audit — 2026-11-13

## Baseline and scope

Audited a fresh GitHub clone of tag `v1.1.0`, resolving to `f687d6e719aa6f17abe855a6f251a58ab9a6a494`. Both plugins were registered in the Claude, Codex, and Cursor marketplaces, and all five generated platform directories were present. Presence and fixture execution alone did not establish native installation compatibility.

Native tests used isolated temporary profiles and installed complete bundles. No model session, payment, blockchain call, or merchant operation was run. No normal user plugin configuration was changed.

## Findings and resolution

| Platform | v1.1.0 finding | Verification / correction |
| --- | --- | --- |
| Claude Code | Both entries resolve and install. | Native marketplace add, installation, and JSON inventory passed for both 0.1.0 plugins. |
| Codex | Both entries resolve and install; old manual-copy instructions referenced nonexistent paths. | Native marketplace add, `plugin add`, and JSON inventory passed for both; documented full-bundle installation. |
| Gemini CLI | Both extensions install with positional local paths. The documented `--path` flag was invalid. | Native installation and inventory showed all 13 skills and retained scripts. Folder trust is separate from extension `--consent`; the initial unattended attempt waited for this prompt. |
| Cursor | Registered bundles and manifests are valid; documented external symlinks are rejected by current Cursor. Copying only skills also drops resources. | Checked live official schemas and full-copy resource/discovery layout. Updated to complete local copies. Cursor IDE/CLI was unavailable, so native UI discovery and organization import policy were not exercised. |
| Antigravity | Native validation failed: missing `plugin.json`. A manifest alone still produced an empty installed component inventory on the installed client. | Added native manifest, root skills, and rule context. Native install processed seven x402 and six TAP skills; installed copies retained their conformance resource roots. |
| OpenClaw | `openclaw.plugin.json` selected the native-code loader despite the absence of an entry point. | Changed generated output to a Claude-format content bundle. CI runs the native installer, skill discovery, and resource checks for corrected bundles and the unchanged v1.1.0 source-bundle workaround. |

The generated Gemini and Antigravity metadata also pointed to an obsolete repository owner/name; OpenClaw package metadata used the former repository name. All now use the canonical repository URL.

## Repeatable checks

- `python scripts/test_distribution_install.py`: resolves all three catalogs and checks both plugins' real discovery roots and copied resources across six platforms.
- `python scripts/test_plugin_bundles.py`: executes fixtures and advisory script checks from independent copies of all five generated layouts.
- `python scripts/test_openclaw_install.py --cli <openclaw.mjs>`: installs both bundles in a temporary native OpenClaw profile, checks plugin/skill inventories, and verifies retained resources.
- Existing manifest, inventory, live Cursor-schema, generated-output, and Linux/Windows fixture checks remain enabled.

`v1.1.1` supplies corrected bundles and plugin versions 0.1.1; it does not rewrite the original release. Public directory approval, ClawHub publication, and native Cursor UI operation are not claimed. See [release installation instructions](../../INSTALL-RELEASE.md) for platform-specific routes.

## Official references consulted

- [Claude installation and tag pinning](https://code.claude.com/docs/en/discover-plugins)
- [Codex marketplaces and plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Gemini extension reference](https://geminicli.com/docs/extensions/reference/)
- [Cursor local plugin imports and team marketplaces](https://cursor.com/docs/plugins)
- [Antigravity native plugin layout](https://antigravity.google/docs/build-plugins)
- [OpenClaw bundle detection precedence](https://docs.openclaw.ai/plugins/bundles)
