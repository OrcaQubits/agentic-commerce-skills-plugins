"""Convert agent .md files for Gemini CLI and Antigravity.

Gemini:       Remap tools/model in frontmatter, keep body.
Antigravity:  Extract body into AGENTS.md and .agent/rules/ rule files.
"""

from __future__ import annotations

from pathlib import Path

from .frontmatter import (
    parse_frontmatter,
    remap_for_antigravity,
    remap_for_gemini,
    serialize_frontmatter,
)


def convert_agent_gemini(agent_path: Path) -> str:
    """Return the converted agent .md content for Gemini CLI."""
    text = agent_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    fm = remap_for_gemini(fm, is_agent=True)
    return serialize_frontmatter(fm, body)


def convert_agents_gemini(
    plugin_dir: Path,
    output_dir: Path,
) -> list[Path]:
    """Convert all agents under *plugin_dir*/agents/ for Gemini CLI.

    Writes to output_dir/agents/<name>.md.
    Returns list of written paths.
    """
    agents_src = plugin_dir / "agents"
    if not agents_src.is_dir():
        return []

    agents_dest = output_dir / "agents"
    written: list[Path] = []

    for agent_md in sorted(agents_src.glob("*.md")):
        content = convert_agent_gemini(agent_md)
        out_path = agents_dest / agent_md.name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", newline="\n")
        written.append(out_path)

    return written


def extract_agent_body(agent_path: Path) -> tuple[str, str, str]:
    """Extract (name, description, body) from an agent .md file."""
    text = agent_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    return fm.get("name", agent_path.stem), fm.get("description", ""), body


def generate_plugin_agents_md(plugin_dir: Path, plugin_name: str) -> str:
    """Generate a per-plugin AGENTS.md for Antigravity from agent bodies.

    Combines agent descriptions and bodies into a single cross-tool rules file.
    """
    agents_src = plugin_dir / "agents"
    if not agents_src.is_dir():
        return ""

    sections: list[str] = [
        f"# {plugin_name} — Agent Rules\n",
        "This file contains expert knowledge and rules extracted from the "
        f"{plugin_name} plugin. It works across AI dev tools that read "
        "AGENTS.md (Antigravity, Cursor, Windsurf, etc.).\n",
    ]

    for agent_md in sorted(agents_src.glob("*.md")):
        name, description, body = extract_agent_body(agent_md)
        sections.append(f"## {name}\n")
        sections.append(f"**When to use:** {description}\n")
        sections.append(body.strip())
        sections.append("")

    return "\n".join(sections) + "\n"


def generate_plugin_rule(plugin_dir: Path, plugin_name: str) -> str:
    """Generate a concise rule file for .agent/rules/<plugin>-rules.md."""
    agents_src = plugin_dir / "agents"
    if not agents_src.is_dir():
        return ""

    sections: list[str] = [f"# {plugin_name} Rules\n"]

    for agent_md in sorted(agents_src.glob("*.md")):
        name, description, body = extract_agent_body(agent_md)
        sections.append(f"## {name}\n")
        sections.append(f"{description}\n")
        sections.append(body.strip())
        sections.append("")

    return "\n".join(sections) + "\n"


def convert_agents_antigravity(
    plugin_dir: Path,
    output_dir: Path,
    plugin_name: str,
) -> list[Path]:
    """Generate Antigravity agent outputs for a plugin.

    Creates:
    - output_dir/AGENTS.md  (per-plugin expertise)
    - output_dir/.agent/rules/<plugin_name>-rules.md

    Returns list of written paths.
    """
    written: list[Path] = []

    # AGENTS.md
    agents_md = generate_plugin_agents_md(plugin_dir, plugin_name)
    if agents_md:
        out = output_dir / "AGENTS.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(agents_md, encoding="utf-8", newline="\n")
        written.append(out)

    # .agent/rules/<plugin>-rules.md
    rule = generate_plugin_rule(plugin_dir, plugin_name)
    if rule:
        out = output_dir / ".agent" / "rules" / f"{plugin_name}-rules.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rule, encoding="utf-8", newline="\n")
        written.append(out)

    return written
