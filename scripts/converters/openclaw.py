"""Convert Claude Code plugins to OpenClaw format.

OpenClaw conventions (verified against docs.openclaw.ai, March 2026):
  - Manifest:   openclaw.plugin.json (required: id, configSchema;
                optional: name, description, version, skills)
  - Context:    AGENTS.md (workspace-level operational rules file)
  - Skills:     skills/<skill>/SKILL.md (name + description frontmatter)
  - Sub-agents: Managed via agents.list[] in JSON config, not standalone files.
                Agent expertise is delivered via AGENTS.md context.

Hooks:
  OpenClaw hooks are TypeScript-based (HOOK.md + handler.ts) with events:
    command:new, command:reset, command:stop, message:received,
    message:transcribed, message:preprocessed, message:sent,
    session:compact:before, session:compact:after, agent:bootstrap,
    gateway:startup, tool_result_persist.
  There are NO tool-level lifecycle hooks (no PostToolUse/PreToolUse).
  Claude Code hook scripts CANNOT be ported and are copied as standalone
  utilities (for git pre-commit or CI integration).

Model mapping (provider/model format):
  opus -> anthropic/claude-opus-4-6, sonnet -> anthropic/claude-sonnet-4-5,
  haiku -> anthropic/claude-haiku-4-5
"""

from __future__ import annotations

import json
from pathlib import Path


def generate_openclaw_manifest(plugin_json_path: Path, skills_dir: Path | None = None) -> dict:
    """Generate an openclaw.plugin.json dict from a Claude plugin.json.

    The ``skills`` array is auto-populated by scanning *skills_dir* if provided,
    otherwise from the source plugin's ``skills/`` directory.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Discover skill directories
    skill_refs: list[str] = []
    scan_dir = skills_dir or plugin_json_path.parent.parent / "skills"
    if scan_dir.is_dir():
        for skill_dir in sorted(scan_dir.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
                skill_refs.append(f"skills/{skill_dir.name}")

    return {
        "id": data.get("name", ""),
        "name": data.get("name", "").replace("-", " ").title(),
        "description": data.get("description", ""),
        "version": data.get("version", "1.0.0"),
        "skills": skill_refs,
        "configSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    }


def copy_hook_scripts(
    plugin_dir: Path,
    output_dir: Path,
) -> list[Path]:
    """Copy hook scripts as standalone utilities.

    OpenClaw hooks are TypeScript-based with different events — no tool-level
    lifecycle hooks.  Python scripts are provided for manual use, git
    pre-commit hooks, or CI pipeline integration.
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


def convert_all_openclaw(
    plugin_dir: Path,
    output_dir: Path,
    plugin_name: str,
    plugin_json_path: Path,
) -> list[Path]:
    """Write openclaw.plugin.json and copy hook scripts.

    Creates:
      output_dir/openclaw.plugin.json  (plugin manifest)
      output_dir/scripts/*.py          (hook scripts as standalone utilities)

    Returns list of written paths.
    """
    written: list[Path] = []

    # 1. openclaw.plugin.json — use output skills dir for auto-population
    if plugin_json_path.is_file():
        skills_dir = output_dir / "skills"
        manifest = generate_openclaw_manifest(plugin_json_path, skills_dir=skills_dir)
        out_path = output_dir / "openclaw.plugin.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(out_path)

    # 2. Hook scripts as standalone utilities
    written.extend(copy_hook_scripts(plugin_dir, output_dir))

    return written
