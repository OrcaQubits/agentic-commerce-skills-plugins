"""Convert Claude Code plugins to Cursor format.

Cursor conventions (verified against cursor.com/docs, March 2026):
  - Manifest:   .cursor-plugin/plugin.json (required: name; optional: displayName,
                version, description, author, keywords, license, rules, skills,
                agents, hooks)
  - Context:    AGENTS.md (standard cross-tool), plus .cursor/rules/*.mdc
  - Skills:     skills/<skill>/SKILL.md (name + description frontmatter;
                disable-model-invocation IS supported)
  - Agents:     agents/*.md (name, description, model as inherit/fast/explicit ID)
  - Rules:      rules/*.mdc (description, globs, alwaysApply frontmatter)
  - Hooks:      hooks/hooks.json (preToolUse, postToolUse, sessionStart, etc.)

Hooks:
  Cursor supports tool-level lifecycle hooks.  Event names differ in casing:
  PostToolUse -> postToolUse, PreToolUse -> preToolUse.  The Claude nested
  structure (matcher -> hooks[]) is flattened to Cursor's flat format
  (command + matcher at same level).  Tool names in matchers are Claude-
  compatible (Write, Edit, Bash, etc.) — no remapping needed.
  - ``${CLAUDE_PLUGIN_ROOT}`` is remapped to ``${CURSOR_PLUGIN_ROOT}``
  - ``type`` is kept (Cursor supports "command" | "prompt")
  - ``async`` is stripped (not in Cursor's hook schema)
  - Timeout is kept in seconds (same as Claude)
  - A top-level ``"version": 1`` is added.

Model mapping:
  All agent models are set to ``inherit`` — defers to the user's Cursor model
  selection rather than specifying a particular model.
"""

from __future__ import annotations

import json
from pathlib import Path

from .frontmatter import parse_frontmatter, remap_for_cursor, serialize_frontmatter


# Event name mapping (Claude PascalCase -> Cursor camelCase)
CURSOR_EVENT_MAP = {
    "PostToolUse": "postToolUse",
    "PreToolUse": "preToolUse",
}


def generate_cursor_manifest(plugin_json_path: Path) -> dict:
    """Generate a .cursor-plugin/plugin.json dict from a Claude plugin.json.

    Unlike Gemini (which strips author/keywords/license), Cursor keeps them.
    Components are auto-discovered from default directories (rules/, skills/,
    agents/, hooks/) so explicit path fields are not needed.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    manifest: dict = {
        "name": data["name"],
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", ""),
    }

    # Cursor keeps author, keywords, license (unlike Gemini which strips them)
    if "author" in data:
        manifest["author"] = data["author"]
    if "keywords" in data:
        manifest["keywords"] = data["keywords"]
    if "license" in data:
        manifest["license"] = data["license"]

    # Note: Component paths (rules/, skills/, agents/, hooks/) are NOT listed
    # here because Cursor auto-discovers from these default directories.

    return manifest


def convert_agent_cursor(agent_path: Path) -> str:
    """Return the converted agent .md content for Cursor.

    Sets model to 'inherit', strips tools field.
    """
    text = agent_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    fm = remap_for_cursor(fm, is_agent=True)
    return serialize_frontmatter(fm, body)


def generate_rule_mdc(agent_path: Path) -> str:
    """Generate a .mdc rule file from an agent .md file.

    Extracts agent name/description/body and formats as a Cursor rule
    with alwaysApply: true frontmatter.
    """
    text = agent_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    name = fm.get("name", agent_path.stem)
    description = fm.get("description", "")

    lines = [
        "---",
        f"description: {name} — {description}",
        "alwaysApply: true",
        "---",
        "",
        body.strip(),
        "",
    ]

    return "\n".join(lines)


def _remap_cursor_command(command: str) -> str:
    """Remap command paths for Cursor plugin layout.

    - Replace ``${CLAUDE_PLUGIN_ROOT}`` with ``${CURSOR_PLUGIN_ROOT}``
    - Rewrite ``hooks/scripts/`` to ``scripts/`` (scripts/ at plugin root)
    """
    # Rewrite Claude path variable to Cursor equivalent
    result = command.replace("${CLAUDE_PLUGIN_ROOT}", "${CURSOR_PLUGIN_ROOT}")
    # Normalise script paths: hooks/scripts/ -> scripts/
    result = result.replace("/hooks/scripts/", "/scripts/")
    return result


def convert_hooks_cursor(plugin_dir: Path, output_dir: Path) -> list[Path]:
    """Convert hooks.json and copy hook scripts for Cursor.

    Cursor hooks layout:
      output_dir/hooks/hooks.json   (Cursor event names)
      output_dir/scripts/*.py       (hook scripts)

    Conversion:
    1. Remap event names: PostToolUse -> postToolUse, PreToolUse -> preToolUse
    2. Flatten Claude's nested structure (matcher -> hooks[]) into Cursor's
       flat format (command + matcher at same level)
    3. No tool name remapping needed (Cursor uses Claude tool names)
    4. Remap script paths: ${CLAUDE_PLUGIN_ROOT} -> ${CURSOR_PLUGIN_ROOT},
       hooks/scripts/ -> scripts/
    5. Keep ``type`` field (Cursor supports "command" | "prompt")
    6. Strip ``async`` field (not in Cursor hook schema)
    7. Keep ``timeout`` in seconds
    8. Add ``"version": 1`` at top level

    Returns list of written paths.
    """
    written: list[Path] = []

    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if hooks_json.is_file():
        with open(hooks_json, encoding="utf-8") as f:
            data = json.load(f)

        source_hooks = data.get("hooks", {})
        converted_hooks: dict = {}

        for event_name, hook_list in source_hooks.items():
            cursor_event = CURSOR_EVENT_MAP.get(event_name, event_name)
            converted_entries = []

            for entry in hook_list:
                for hook in entry.get("hooks", []):
                    flat_entry: dict = {}

                    # Keep matcher from parent entry
                    if "matcher" in entry:
                        flat_entry["matcher"] = entry["matcher"]

                    # Remap command path
                    if "command" in hook:
                        flat_entry["command"] = _remap_cursor_command(hook["command"])

                    # Keep type (Cursor supports "command" | "prompt")
                    if "type" in hook:
                        flat_entry["type"] = hook["type"]

                    # Keep timeout in seconds (Cursor uses seconds, same as Claude)
                    if "timeout" in hook:
                        flat_entry["timeout"] = hook["timeout"]

                    # Strip async (not in Cursor hook schema)
                    converted_entries.append(flat_entry)

            converted_hooks[cursor_event] = converted_entries

        result = {"version": 1, "hooks": converted_hooks}

        out_path = output_dir / "hooks" / "hooks.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(out_path)

    # Copy hook scripts to scripts/
    scripts_dir = plugin_dir / "hooks" / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.glob("*.py")):
            content = script.read_text(encoding="utf-8")
            out_path = output_dir / "scripts" / script.name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8", newline="\n")
            written.append(out_path)

    return written


def convert_all_cursor(
    plugin_dir: Path,
    output_dir: Path,
    plugin_name: str,
    plugin_json_path: Path,
) -> list[Path]:
    """Convert agents, rules, hooks, and manifest for Cursor.

    Creates:
      output_dir/.cursor-plugin/plugin.json   (plugin manifest)
      output_dir/agents/<name>.md              (subagent definitions)
      output_dir/rules/<name>.mdc              (agent expertise as rules)
      output_dir/hooks/hooks.json              (hooks with Cursor event names)
      output_dir/scripts/*.py                  (hook scripts)

    Returns list of written paths.
    """
    written: list[Path] = []

    # 1. Plugin manifest
    if plugin_json_path.is_file():
        manifest = generate_cursor_manifest(plugin_json_path)
        out_path = output_dir / ".cursor-plugin" / "plugin.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(out_path)

    # 2. Agent .md files + .mdc rules
    agents_src = plugin_dir / "agents"
    if agents_src.is_dir():
        for agent_md in sorted(agents_src.glob("*.md")):
            # Agent definition
            content = convert_agent_cursor(agent_md)
            out_path = output_dir / "agents" / agent_md.name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8", newline="\n")
            written.append(out_path)

            # Rule .mdc
            rule_content = generate_rule_mdc(agent_md)
            rule_path = output_dir / "rules" / f"{agent_md.stem}.mdc"
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            rule_path.write_text(rule_content, encoding="utf-8", newline="\n")
            written.append(rule_path)

    # 3. Hooks + scripts
    written.extend(convert_hooks_cursor(plugin_dir, output_dir))

    return written
