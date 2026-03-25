"""Convert Claude Code hooks to Gemini CLI format.

Gemini CLI hooks reference:
  https://geminicli.com/docs/hooks/reference/

Mapping:
  - Event:   PostToolUse -> AfterTool,  PreToolUse -> BeforeTool
  - Matcher: Write|Edit -> write_file|edit_file,  Bash -> run_shell_command
  - Path:    ${CLAUDE_PLUGIN_ROOT} -> ${extensionPath}${/}
  - Scripts: hooks/scripts/*.py -> scripts/*.py  (extension root-relative)
  - Timeout: seconds -> milliseconds
  - Async:   stripped (Gemini hooks are synchronous; exit code controls flow)
  - Layout:  hooks.json at extension root (not hooks/hooks.json)

Also adapts Python hook scripts to use Gemini tool names.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# Event name mapping
EVENT_MAP = {
    "PostToolUse": "AfterTool",
    "PreToolUse": "BeforeTool",
}

# Tool name mapping in matchers (regex alternation patterns)
TOOL_MATCHER_MAP = {
    "Write": "write_file",
    "Edit": "edit_file",
    "Bash": "run_shell_command",
    "Read": "read_file",
    "Glob": "list_files",
    "Grep": "search_files",
}

# Tool name mapping inside Python scripts (string literals)
SCRIPT_TOOL_MAP = {
    '"Write"': '"write_file"',
    '"Edit"': '"edit_file"',
    '"Bash"': '"run_shell_command"',
    '"Read"': '"read_file"',
    "'Write'": "'write_file'",
    "'Edit'": "'edit_file'",
    "'Bash'": "'run_shell_command'",
    "'Read'": "'read_file'",
}


def _remap_matcher(matcher: str) -> str:
    """Remap a Claude matcher pattern like ``Write|Edit`` to Gemini equivalents."""
    parts = matcher.split("|")
    remapped = [TOOL_MATCHER_MAP.get(p.strip(), p.strip()) for p in parts]
    return "|".join(remapped)


def _remap_command(command: str) -> str:
    """Remap command paths for Gemini CLI extension layout.

    - Replace ``${CLAUDE_PLUGIN_ROOT}`` with ``${extensionPath}${/}``
    - Replace ``hooks/scripts/`` with ``scripts/`` (Gemini convention)
    """
    result = command.replace("${CLAUDE_PLUGIN_ROOT}", "${extensionPath}${/}")
    # Normalise script paths: hooks/scripts/ -> scripts/
    result = result.replace("/hooks/scripts/", "/scripts/")
    return result


def convert_hooks_json(hooks_json_path: Path) -> dict:
    """Convert a Claude Code hooks.json to Gemini CLI hooks format.

    Gemini CLI hooks.json schema (at extension root):
    {
      "hooks": {
        "<EventName>": [{
          "matcher": "<regex>",
          "sequential": false,
          "hooks": [{
            "type": "command",
            "command": "<shell command>",
            "timeout": <ms>,
            "name": "<optional>",
            "description": "<optional>"
          }]
        }]
      }
    }
    """
    with open(hooks_json_path, encoding="utf-8") as f:
        data = json.load(f)

    source_hooks = data.get("hooks", {})
    converted_hooks: dict = {}

    for event_name, hook_list in source_hooks.items():
        gemini_event = EVENT_MAP.get(event_name, event_name)
        converted_entries = []

        for entry in hook_list:
            converted_entry: dict = {}

            # Remap matcher
            if "matcher" in entry:
                converted_entry["matcher"] = _remap_matcher(entry["matcher"])

            # Convert individual hooks
            converted_hook_items = []
            for hook in entry.get("hooks", []):
                item: dict = {"type": hook.get("type", "command")}

                if "command" in hook:
                    item["command"] = _remap_command(hook["command"])

                # Convert timeout from seconds to milliseconds
                if "timeout" in hook:
                    item["timeout"] = hook["timeout"] * 1000

                # Strip async (not supported in Gemini — exit code 2 blocks)
                # hook.get("async") is intentionally not copied

                converted_hook_items.append(item)

            converted_entry["hooks"] = converted_hook_items
            converted_entries.append(converted_entry)

        converted_hooks[gemini_event] = converted_entries

    # Top-level structure: only "hooks" key (no description — not part of Gemini schema)
    return {"hooks": converted_hooks}


def adapt_hook_script(script_path: Path) -> str:
    """Adapt a Python hook script for Gemini CLI tool names.

    Replaces Claude tool name string literals with Gemini equivalents.
    """
    content = script_path.read_text(encoding="utf-8")

    for old, new in SCRIPT_TOOL_MAP.items():
        content = content.replace(old, new)

    # Also update docstring references
    content = content.replace("PostToolUse", "AfterTool")
    content = content.replace("PreToolUse", "BeforeTool")

    return content


def convert_all_hooks(
    plugin_dir: Path,
    output_dir: Path,
) -> list[Path]:
    """Convert hooks.json and all hook scripts for Gemini CLI.

    Gemini CLI layout:
      output_dir/hooks.json          (extension root)
      output_dir/scripts/*.py        (hook scripts)

    Returns list of written paths.
    """
    written: list[Path] = []

    # Convert hooks.json -> extension root
    hooks_json = plugin_dir / "hooks" / "hooks.json"
    if hooks_json.is_file():
        converted = convert_hooks_json(hooks_json)
        out_path = output_dir / "hooks.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(converted, f, indent=2, ensure_ascii=False)
            f.write("\n")
        written.append(out_path)

    # Convert hook scripts -> scripts/
    scripts_dir = plugin_dir / "hooks" / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.glob("*.py")):
            adapted = adapt_hook_script(script)
            out_path = output_dir / "scripts" / script.name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(adapted, encoding="utf-8", newline="\n")
            written.append(out_path)

    return written
