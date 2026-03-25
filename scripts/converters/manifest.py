"""Convert Claude Code plugin.json to Gemini CLI gemini-extension.json."""

from __future__ import annotations

import json
from pathlib import Path


def convert_plugin_json(plugin_json_path: Path) -> dict:
    """Read a Claude Code plugin.json and produce a Gemini extension manifest.

    Strips ``author``, ``keywords``, ``license`` and adds
    ``contextFileName: "GEMINI.md"``.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    gemini: dict = {
        "name": data["name"],
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", ""),
        "contextFileName": "GEMINI.md",
    }

    return gemini


def write_gemini_manifest(manifest: dict, output_path: Path) -> None:
    """Write a gemini-extension.json file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
