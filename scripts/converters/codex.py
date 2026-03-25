"""Convert Claude Code plugins to OpenAI Codex CLI format.

Codex CLI conventions (verified against developers.openai.com/codex, March 2026):
  - Context:    AGENTS.md (walked from git root down to cwd, concatenated)
  - Skills:     .agents/skills/<skill>/SKILL.md (name + description frontmatter)
  - Subagents:  .codex/agents/<name>.toml (TOML with name, description, model,
                developer_instructions)
  - No manifest file (unlike Gemini's gemini-extension.json)

Hooks:
  Codex CLI does NOT have per-tool lifecycle hooks (no PostToolUse, PreToolUse,
  AfterToolUse equivalents).  It has only:
    - ``notify`` (array of strings) for end-of-turn notifications
    - Starlark execution-policy rules for command approval
  Therefore Claude Code hooks CANNOT be ported.  Hook scripts are copied as
  standalone utilities (for git pre-commit or CI integration).

Model mapping:
  opus -> gpt-5.4, sonnet -> gpt-5.4-mini, haiku -> gpt-5.4-mini
"""

from __future__ import annotations

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


def convert_all_codex(
    plugin_dir: Path,
    output_dir: Path,
    plugin_name: str,
) -> list[Path]:
    """Convert agents and copy scripts for Codex CLI.

    Creates:
      output_dir/.codex/agents/<name>.toml   (subagent definitions)
      output_dir/scripts/*.py                 (hook scripts as standalone utilities)

    Note: No config.toml is generated.  Codex CLI does not support per-tool
    lifecycle hooks (PostToolUse/PreToolUse).  Hook scripts are copied as
    standalone utilities for git pre-commit or CI integration.

    Returns list of written paths.
    """
    written: list[Path] = []

    # 1. Agent TOML files
    agents_src = plugin_dir / "agents"
    if agents_src.is_dir():
        for agent_md in sorted(agents_src.glob("*.md")):
            toml_content = generate_agent_toml(agent_md)
            out_path = output_dir / ".codex" / "agents" / f"{agent_md.stem}.toml"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(toml_content, encoding="utf-8", newline="\n")
            written.append(out_path)

    # 2. Hook scripts as standalone utilities (no config.toml — no hook system)
    written.extend(copy_hook_scripts(plugin_dir, output_dir))

    return written
