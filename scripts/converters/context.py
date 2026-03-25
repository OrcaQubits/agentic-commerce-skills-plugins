"""Generate GEMINI.md and AGENTS.md context files.

GEMINI.md  — Plugin context file for Gemini CLI (referenced by gemini-extension.json).
AGENTS.md  — Cross-tool rules file for Antigravity / Cursor / Windsurf / etc.
"""

from __future__ import annotations

from pathlib import Path

from .agents import extract_agent_body


def generate_gemini_md(plugin_dir: Path, plugin_name: str, description: str) -> str:
    """Generate a GEMINI.md context file from the plugin's agent body.

    The GEMINI.md is loaded automatically by Gemini CLI as the extension's
    context (specified via ``contextFileName`` in gemini-extension.json).
    """
    sections: list[str] = [
        f"# {plugin_name}\n",
        f"{description}\n",
    ]

    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_md in sorted(agents_dir.glob("*.md")):
            _name, _desc, body = extract_agent_body(agent_md)
            sections.append(body.strip())
            sections.append("")

    return "\n".join(sections) + "\n"


def generate_root_agents_md(
    plugins: list[dict],
    repo_root: Path,
    platform: str = "",
) -> str:
    """Generate a root-level AGENTS.md summarising all plugins.

    This goes at dist/<platform>/AGENTS.md and provides an overview
    with links to each per-plugin AGENTS.md.
    """
    # Platform-specific skills directory
    if platform == "cursor":
        skills_dir = ".cursor/skills/"
    elif platform == "codex":
        skills_dir = ".agents/skills/"
    else:
        skills_dir = ".agent/skills/"

    lines: list[str] = [
        "# Agentic Commerce — Agent Rules\n",
        "This repository contains expert knowledge for agentic commerce protocols "
        "and platforms. Each plugin directory has its own AGENTS.md with detailed "
        f"rules and skills.\n",
        "## Plugins\n",
        "| Plugin | Description |",
        "|--------|-------------|",
    ]

    for plugin in plugins:
        name = plugin["name"]
        desc = plugin.get("description", "")
        lines.append(f"| [{name}](./{name}/AGENTS.md) | {desc} |")

    lines.append("")
    lines.append(
        "## How to Use\n\n"
        "Copy or symlink the plugin directories you need into your project. "
        "Your AI dev tool will automatically pick up the AGENTS.md files "
        f"and the skills in `{skills_dir}`.\n"
    )

    return "\n".join(lines) + "\n"
