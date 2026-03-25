"""Convert SKILL.md files for Gemini CLI, Antigravity, Codex CLI, OpenClaw, and Cursor.

Strips Claude-specific frontmatter fields (disable-model-invocation,
allowed-tools) while preserving name, description, and the full markdown body.
For Cursor, only allowed-tools is stripped — disable-model-invocation is kept.
"""

from __future__ import annotations

from pathlib import Path

from .frontmatter import (
    parse_frontmatter,
    remap_for_antigravity,
    remap_for_codex,
    remap_for_cursor,
    remap_for_gemini,
    remap_for_openclaw,
    serialize_frontmatter,
)


def convert_skill(
    skill_path: Path,
    platform: str,
) -> str:
    """Return the converted SKILL.md content for *platform*."""
    text = skill_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if platform == "gemini":
        fm = remap_for_gemini(fm, is_agent=False)
    elif platform == "codex":
        fm = remap_for_codex(fm, is_agent=False)
    elif platform == "openclaw":
        fm = remap_for_openclaw(fm, is_agent=False)
    elif platform == "cursor":
        fm = remap_for_cursor(fm, is_agent=False)
    else:
        fm = remap_for_antigravity(fm, is_agent=False)

    return serialize_frontmatter(fm, body)


def convert_all_skills(
    plugin_dir: Path,
    output_dir: Path,
    platform: str,
) -> list[Path]:
    """Convert every SKILL.md under *plugin_dir*/skills/ into *output_dir*.

    For Gemini:       output_dir/skills/<skill>/SKILL.md
    For Antigravity:  output_dir/.agent/skills/<skill>/SKILL.md
    For Codex:        output_dir/.agents/skills/<skill>/SKILL.md
    For OpenClaw:     output_dir/skills/<skill>/SKILL.md

    Returns a list of written file paths.
    """
    skills_src = plugin_dir / "skills"
    if not skills_src.is_dir():
        return []

    if platform == "codex":
        skills_dest = output_dir / ".agents" / "skills"
    elif platform == "antigravity":
        skills_dest = output_dir / ".agent" / "skills"
    else:
        skills_dest = output_dir / "skills"

    written: list[Path] = []

    for skill_dir in sorted(skills_src.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        content = convert_skill(skill_md, platform)

        out_path = skills_dest / skill_dir.name / "SKILL.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8", newline="\n")
        written.append(out_path)

    return written
