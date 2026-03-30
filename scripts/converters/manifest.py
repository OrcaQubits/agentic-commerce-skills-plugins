"""Convert Claude Code plugin.json to Gemini / Antigravity manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_URL = "https://github.com/AgenticCommerce/agentic-commerce-claude-plugins"


def convert_plugin_json(
    plugin_json_path: Path, plugin_entry: dict | None = None
) -> dict:
    """Read a Claude Code plugin.json and produce a Gemini extension manifest.

    Keeps ``author`` and adds ``repository`` for marketplace discoverability,
    plus ``contextFileName: "GEMINI.md"``.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    gemini: dict = {
        "name": data["name"],
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", ""),
        "contextFileName": "GEMINI.md",
    }

    # Author — prefer plugin.json, fall back to marketplace entry
    author = data.get("author") or (plugin_entry or {}).get("author")
    if author:
        gemini["author"] = author

    # Repository
    gemini["repository"] = {"type": "git", "url": REPO_URL}

    return gemini


def write_gemini_manifest(manifest: dict, output_path: Path) -> None:
    """Write a gemini-extension.json file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# Antigravity package.json
# ---------------------------------------------------------------------------

def _parse_skill_frontmatter(skill_md_path: Path) -> dict | None:
    """Extract name and description from a SKILL.md YAML frontmatter."""
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return None

    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None

    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()

    if "name" not in fm:
        return None
    return {"name": fm["name"], "description": fm.get("description", "")}


def generate_antigravity_manifest(
    plugin_dir: Path, plugin_entry: dict
) -> dict:
    """Build a package.json manifest for an Antigravity plugin output."""
    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    data: dict = {}
    if plugin_json_path.is_file():
        with open(plugin_json_path, encoding="utf-8") as f:
            data = json.load(f)

    name = data.get("name", plugin_entry["name"])

    # Build displayName from slug: "saleor-commerce" → "Saleor Commerce"
    display_name = name.replace("-", " ").title()

    manifest: dict = {
        "name": name,
        "displayName": display_name,
        "version": data.get("version", plugin_entry.get("version", "1.0.0")),
        "description": data.get("description", plugin_entry.get("description", "")),
        "publisher": "orcaqubits-ai",
    }

    # Author
    author = data.get("author") or plugin_entry.get("author")
    if author:
        manifest["author"] = author

    # Repository
    manifest["repository"] = {"type": "git", "url": REPO_URL}

    # Keywords
    keywords = data.get("keywords", [])
    if keywords:
        manifest["keywords"] = keywords

    # Categories (VS Code-style)
    manifest["categories"] = ["AI", "Other"]

    # Skills — scan the source plugin's skills directory
    skills_dir = plugin_dir / "skills"
    skills_list: list[dict] = []
    if skills_dir.is_dir():
        for skill_sub in sorted(skills_dir.iterdir()):
            skill_md = skill_sub / "SKILL.md"
            if skill_md.is_file():
                info = _parse_skill_frontmatter(skill_md)
                if info:
                    skills_list.append(
                        {
                            "name": info["name"],
                            "description": info["description"],
                            "path": f".agent/skills/{skill_sub.name}/SKILL.md",
                        }
                    )
    if skills_list:
        manifest["skills"] = skills_list

    return manifest


def write_antigravity_manifest(manifest: dict, output_path: Path) -> None:
    """Write an Antigravity package.json file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
