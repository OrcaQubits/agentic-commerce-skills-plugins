# Publishing to the Gemini CLI Extensions Gallery

This guide explains how this repo is wired for the [Gemini CLI Extensions Gallery](https://geminicli.com/extensions/), and how to refresh / re-tag it for new releases.

## Quick facts about the gallery

The Gemini CLI Extensions Gallery is a **decentralized, GitHub-backed catalog**:

- No `npm publish`-style flow. No PR to a registry repo. No Google review.
- Discovery is driven by a **single GitHub topic**: `gemini-cli-extension` (singular).
- The crawler runs **daily**, validates `gemini-extension.json`, and surfaces the repo in the gallery.
- Each repo lists **one extension** — `gemini-extension.json` must be at the repo root.
- Listings are ranked by **GitHub stars**.

References:
- Gallery: https://geminicli.com/extensions/
- Publishing flow: https://geminicli.com/docs/extensions/releasing/
- Manifest reference: https://geminicli.com/docs/extensions/reference/

## How this monorepo handles the "one extension per repo" rule

This repo is a monorepo of **15 commerce/agentic plugins**, but the gallery only accepts one manifest per repo. We chose **UCP (Universal Commerce Protocol) as the flagship extension** because:

- UCP is the umbrella protocol (Google + Shopify) tying together the other commerce protocols
- Its skill set covers all four transport bindings (REST, MCP, A2A, Embedded)
- It pairs well with the other 17 plugins as ecosystem context in the same install

So at the **repo root** you'll find UCP's extension files, copied from `dist/gemini/ucp-agentic-commerce/`:

```
agentic-commerce-skills-plugins/
├── gemini-extension.json     # UCP manifest — what the gallery indexes
├── GEMINI.md                 # UCP agent expertise — auto-loaded on install
├── hooks.json                # UCP's PostToolUse secret-detection hook
├── skills/                   # UCP's 15 skills (ucp-checkout-rest, ucp-mcp, ...)
└── scripts/
    └── check_secrets.py      # Hook implementation
```

The other 17 plugins remain **fully installable via path** (see below) and continue to be available for Claude Code / Codex / Cursor / Antigravity / OpenClaw via the standard conversion + install flow.

## Install paths for end users

### 1. UCP (via the gallery)

The flagship extension is discoverable in the gallery:

```bash
gemini extensions install https://github.com/OrcaQubits/agentic-commerce-skills-plugins
```

This installs UCP's manifest + GEMINI.md + 15 UCP skills + secret-detection hook.

### 2. Other plugins (via local directory)

For ACP, A2A, AP2, WebMCP, NLWeb, Stripe MPP, Magento, Shopify, Saleor, Medusa, BigCommerce, WooCommerce, Salesforce Commerce, or Spree:

```bash
git clone https://github.com/OrcaQubits/agentic-commerce-skills-plugins
cd agentic-commerce-skills-plugins
python scripts/convert.py --platform gemini

gemini extensions install ./dist/gemini/spree-commerce
gemini extensions install ./dist/gemini/acp-agentic-commerce
# ... etc.
```

These won't appear in the gallery search results (one repo = one gallery entry) but install and function identically.

## Refreshing the gallery listing

If the UCP plugin's source content changes (new skill, updated agent expertise, schema change):

1. **Update the canonical source** under `ucp-agentic-commerce/`.
2. **Re-run conversion**:
   ```bash
   python scripts/convert.py --platform gemini
   ```
3. **Sync the root copies** from `dist/gemini/ucp-agentic-commerce/`:
   ```bash
   cp dist/gemini/ucp-agentic-commerce/GEMINI.md ./GEMINI.md
   cp dist/gemini/ucp-agentic-commerce/hooks.json ./hooks.json
   cp dist/gemini/ucp-agentic-commerce/scripts/check_secrets.py ./scripts/check_secrets.py
   rm -rf skills && cp -r dist/gemini/ucp-agentic-commerce/skills ./skills
   ```
4. **Bump version** in the root `gemini-extension.json`.
5. **Commit and push**:
   ```bash
   git add gemini-extension.json GEMINI.md hooks.json scripts/check_secrets.py skills/
   git commit -m "chore(gemini): bump UCP extension to vX.Y.Z"
   git push
   ```
6. **Tag and release** with the matching version:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   gh release create v1.1.0 --title "v1.1.0" --notes "..."
   ```
7. **Wait ~24h** — the gallery crawler runs daily and will pick up the new release.

Note: the root manifest's `repository.url` must point at `https://github.com/OrcaQubits/agentic-commerce-skills-plugins`. Verify before pushing.

## Initial gallery onboarding (one-time)

Done once for this repo; documented here for reference:

```bash
# 1. Ensure topic is set
gh repo edit OrcaQubits/agentic-commerce-skills-plugins --add-topic gemini-cli-extension

# 2. Push the v1.0.0 tag
git tag v1.0.0
git push origin v1.0.0

# 3. Create a GitHub Release whose tag matches the manifest version
gh release create v1.0.0 --title "v1.0.0 — Agentic commerce skills for Gemini, Claude, Codex, Cursor, Antigravity, OpenClaw" --notes-file RELEASE_NOTES.md
```

The crawler discovers the repo via the topic and indexes daily.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Repo not appearing in gallery after 48h | Confirm topic is set: `gh repo view OrcaQubits/agentic-commerce-skills-plugins --json repositoryTopics`. Topic must be `gemini-cli-extension` (singular). |
| `gemini extensions install` fails with "manifest not found" | The user is on an old commit before the root manifest existed, or they're targeting a tag without the root files. Use `--ref main`. |
| Hook fires but reports script not found | Confirm `scripts/check_secrets.py` is committed at repo root (not just in `dist/gemini/.../scripts/`). |
| Gallery shows outdated version | The crawler reads the latest **GitHub Release**, not the latest commit. Tag a new release with the matching `version` field. |
| Want to remove the listing | Delete the `gemini-cli-extension` topic from the repo; the crawler stops indexing on its next pass. |
| Manifest validation failed | The reference is at https://geminicli.com/docs/extensions/reference/. Required fields: `name`, `version`, `description`. `name` is lowercase + digits + dashes (no underscores). `version` must match the GitHub release tag. |

## Reference

- Gallery: https://geminicli.com/extensions/
- Publishing flow: https://geminicli.com/docs/extensions/releasing/
- Manifest reference: https://geminicli.com/docs/extensions/reference/
- Writing extensions: https://geminicli.com/docs/extensions/writing-extensions/
- Best practices: https://geminicli.com/docs/extensions/best-practices/
- Google-built extensions (org): https://github.com/gemini-cli-extensions
- Gemini CLI repo: https://github.com/google-gemini/gemini-cli
- Google launch blog: https://blog.google/technology/developers/gemini-cli-extensions/
