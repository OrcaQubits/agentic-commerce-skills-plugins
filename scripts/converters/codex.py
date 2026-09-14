"""Convert Claude Code plugins to OpenAI Codex CLI format.

Codex CLI conventions (verified against developers.openai.com/codex, May 2026):
  - Plugin manifest:  .codex-plugin/plugin.json (required for distribution
                      via `codex plugin marketplace add owner/repo`)
  - Context:          AGENTS.md (walked from git root down to cwd, concatenated)
  - Skills:           skills/<skill>/SKILL.md  (bundle-source layout; Codex's
                      runtime mounts these at .agents/skills/ on install)
  - Subagents:        agents/<name>.toml  (bundle-source layout; runtime mounts
                      these at .codex/agents/ on install)

Marketplace publishing (April 2026, Codex v0.128+):
  A Codex marketplace is a Git repo containing .agents/plugins/marketplace.json
  at its root, listing per-plugin source paths.  Users register a marketplace
  with::

      codex plugin marketplace add owner/repo

  Then install plugins from the TUI ``/plugins`` browser.  See
  https://developers.openai.com/codex/plugins/build for the full spec.

Hooks:
  Codex CLI v0.128+ supports plugin-bundled hooks via ``hooks/hooks.json``
  referenced from plugin.json. Earlier versions had only ``notify`` and
  Starlark execution-policy rules.  Hook scripts are also copied as
  standalone utilities for git pre-commit / CI integration.

Model mapping:
  opus -> gpt-5.4, sonnet -> gpt-5.4-mini, haiku -> gpt-5.4-mini
"""

from __future__ import annotations

import json
from pathlib import Path

from .frontmatter import CODEX_MODEL_MAP, parse_frontmatter


def _escape_toml_multiline(text: str) -> str:
    """Escape text for use inside TOML triple-quoted strings.

    TOML multi-line basic strings (triple double-quotes) only need to escape
    sequences of three or more consecutive double-quotes inside.
    """
    result = text
    while '"""' in result:
        result = result.replace('"""', '""\\\"')
    return result


def generate_agent_toml(agent_path: Path) -> str:
    """Generate a Codex CLI subagent TOML definition from an agent .md file.

    Output format::

        name = "ucp-expert"
        description = "..."
        model = "gpt-5.4"
        developer_instructions = \"\"\"
        ...(full agent body)...
        \"\"\"
    """
    text = agent_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    name = fm.get("name", agent_path.stem)
    description = fm.get("description", "")
    model = CODEX_MODEL_MAP.get(fm.get("model", "opus"), "gpt-5.4")

    escaped_body = _escape_toml_multiline(body.strip())

    lines = [
        f'name = "{name}"',
        f'description = "{description}"',
        f'model = "{model}"',
        f'developer_instructions = """',
        escaped_body,
        '"""',
        "",
    ]

    return "\n".join(lines)


def copy_hook_scripts(
    plugin_dir: Path,
    output_dir: Path,
) -> list[Path]:
    """Copy hook scripts as standalone utilities.

    Codex CLI has no per-tool lifecycle hooks, so these scripts cannot run
    automatically.  They are provided for manual use, git pre-commit hooks,
    or CI pipeline integration.
    """
    written: list[Path] = []

    scripts_dir = plugin_dir / "hooks" / "scripts"
    if not scripts_dir.is_dir():
        return written

    for script in sorted(scripts_dir.glob("*.py")):
        content = script.read_text(encoding="utf-8")
        out_path = output_dir / "scripts" / script.name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", newline="\n")
        written.append(out_path)

    return written


def generate_codex_plugin_manifest(plugin_json_path: Path) -> dict:
    """Generate a .codex-plugin/plugin.json from a Claude plugin.json.

    Conforms to https://developers.openai.com/codex/plugins/build .
    The plugin runtime reads ``name``, ``version``, ``description`` and the
    ``interface`` block for marketplace UI metadata.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    plugin_name = data.get("name", "")
    description = data.get("description", "")
    short_desc = description.split(".")[0][:120] if description else plugin_name

    manifest: dict = {
        "name": plugin_name,
        "version": data.get("version", "1.0.0"),
        "description": description,
        "license": data.get("license", "MIT"),
        "keywords": list(data.get("keywords", [])),
        "interface": {
            "displayName": plugin_name.replace("-", " ").title(),
            "shortDescription": short_desc,
            "longDescription": description,
            "category": "Commerce",
        },
    }

    # author / homepage / repository
    src_author = data.get("author")
    if isinstance(src_author, dict):
        author_obj: dict = {}
        if src_author.get("name"):
            author_obj["name"] = src_author["name"]
        if src_author.get("email"):
            author_obj["email"] = src_author["email"]
        if author_obj:
            manifest["author"] = author_obj
        if src_author.get("url"):
            manifest["homepage"] = src_author["url"]
            manifest["interface"]["websiteURL"] = src_author["url"]
            manifest["interface"]["developerName"] = src_author.get("name", "")
    elif isinstance(src_author, str):
        manifest["author"] = {"name": src_author}

    # Codex's plugin.json spec types `repository` as a plain URL string
    # (see plugin-json-spec.md in openai/codex) — not the npm-style object.
    # Same class of failure as OrcaQubits/agentic-commerce-skills-plugins#6
    # on the Claude side: an object here fails manifest validation.
    manifest["repository"] = (
        data["repository"]
        if isinstance(data.get("repository"), str)
        else "https://github.com/OrcaQubits/agentic-commerce-skills-plugins"
    )

    plugin_dir = plugin_json_path.parent.parent
    if (plugin_dir / "hooks" / "hooks.json").is_file():
        manifest["hooks"] = "./hooks/hooks.json"

    return manifest


def convert_all_codex(
    plugin_dir: Path,
    output_dir: Path,
    plugin_name: str,
) -> list[Path]:
    """Convert agents, write plugin manifest, and copy scripts for Codex CLI.

    Produces a plugin-bundle layout matching
    https://developers.openai.com/codex/plugins/build ::

        output_dir/
        ├── .codex-plugin/plugin.json   (marketplace manifest — REQUIRED)
        ├── agents/<name>.toml           (subagent definitions)
        ├── scripts/*.py                  (hook scripts as standalone utilities)

    Skills and AGENTS.md are written separately by convert_plugin_codex().

    Returns list of written paths.
    """
    written: list[Path] = []

    # 1. .codex-plugin/plugin.json (required for `codex plugin marketplace`)
    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if plugin_json_path.is_file():
        manifest = generate_codex_plugin_manifest(plugin_json_path)
        out_path = output_dir / ".codex-plugin" / "plugin.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(out_path)

    # 2. Subagent TOML files — bundle-source path is plugin-root agents/
    agents_src = plugin_dir / "agents"
    if agents_src.is_dir():
        for agent_md in sorted(agents_src.glob("*.md")):
            toml_content = generate_agent_toml(agent_md)
            out_path = output_dir / "agents" / f"{agent_md.stem}.toml"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(toml_content, encoding="utf-8", newline="\n")
            written.append(out_path)

    # 3. hooks/hooks.json (plugin-bundled hook config, Codex v0.128+)
    hooks_json_src = plugin_dir / "hooks" / "hooks.json"
    if hooks_json_src.is_file():
        hooks_out = output_dir / "hooks" / "hooks.json"
        hooks_out.parent.mkdir(parents=True, exist_ok=True)
        hooks_out.write_text(
            hooks_json_src.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
        written.append(hooks_out)

    # 4. Hook scripts as standalone utilities
    written.extend(copy_hook_scripts(plugin_dir, output_dir))

    return written
