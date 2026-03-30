#!/usr/bin/env python3
"""Validate generated Gemini CLI / Antigravity / Codex CLI / OpenClaw / Cursor output.

Checks:
  1. All JSON files are syntactically valid.
  2. gemini-extension.json has required fields (name, version, description, contextFileName).
  3. hooks.json uses Gemini event names (AfterTool/BeforeTool), not Claude names.
  4. No Claude-specific frontmatter fields leaked into generated SKILL.md / agent .md files.
  5. Every SKILL.md has at least name + description in frontmatter.
  6. Antigravity .agent/ directories have expected structure.
  7. Codex .codex/agents/*.toml have correct fields and no Claude model leaks.
  8. OpenClaw openclaw.plugin.json has required fields (id, configSchema) and no Claude model leaks.
  9. Cursor .cursor-plugin/plugin.json has required fields, agents have model: inherit,
     rules/*.mdc have frontmatter, hooks use camelCase event names.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from converters.frontmatter import CLAUDE_SKILL_FIELDS, CURSOR_SKILL_FIELDS, parse_frontmatter

# Fields that must NOT appear in generated output
CLAUDE_LEAKED_FIELDS = CLAUDE_SKILL_FIELDS  # disable-model-invocation, allowed-tools

# Fields that must NOT appear in Gemini hooks
CLAUDE_HOOK_EVENTS = {"PostToolUse", "PreToolUse"}


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checks_passed = 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self) -> None:
        self.checks_passed += 1

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = [
            f"Checks passed: {self.checks_passed}",
            f"Warnings:      {len(self.warnings)}",
            f"Errors:        {len(self.errors)}",
        ]
        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        if self.errors:
            lines.append("\nErrors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


def validate_json_file(path: Path, result: ValidationResult) -> dict | None:
    """Validate that a file contains valid JSON. Returns parsed data or None."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        result.ok()
        return data
    except json.JSONDecodeError as exc:
        result.error(f"Invalid JSON in {path}: {exc}")
        return None


def validate_gemini_manifest(path: Path, result: ValidationResult) -> None:
    """Validate a gemini-extension.json file."""
    data = validate_json_file(path, result)
    if data is None:
        return

    required = {"name", "version", "description", "contextFileName"}
    missing = required - set(data.keys())
    if missing:
        result.error(f"{path}: missing required fields: {missing}")
    else:
        result.ok()

    # Should not have Claude-specific fields (author and repository are now
    # intentionally included for marketplace discoverability)
    for field in ("keywords", "license"):
        if field in data:
            result.error(f"{path}: Claude-specific field '{field}' should be stripped")


def validate_hooks_json(path: Path, result: ValidationResult) -> None:
    """Validate a Gemini hooks.json file."""
    data = validate_json_file(path, result)
    if data is None:
        return

    hooks = data.get("hooks", {})
    for event_name in hooks:
        if event_name in CLAUDE_HOOK_EVENTS:
            expected = {"PostToolUse": "AfterTool", "PreToolUse": "BeforeTool"}.get(event_name)
            result.error(
                f"{path}: Claude event '{event_name}' leaked — should be '{expected}'"
            )
        else:
            result.ok()

        # Check individual hooks don't have 'async'
        for entry in hooks[event_name]:
            for hook in entry.get("hooks", []):
                if "async" in hook:
                    result.error(f"{path}: 'async' field should be stripped for Gemini")
                # Timeout should be in milliseconds (>= 1000 for any reasonable value)
                timeout = hook.get("timeout")
                if timeout is not None and timeout < 100:
                    result.warn(
                        f"{path}: timeout={timeout} looks like seconds, not milliseconds"
                    )
                else:
                    result.ok()


def validate_skill_md(path: Path, result: ValidationResult, platform: str = "") -> None:
    """Validate a generated SKILL.md file.

    For Cursor, only ``allowed-tools`` is checked as a leak —
    ``disable-model-invocation`` is valid in Cursor skills.
    """
    text = path.read_text(encoding="utf-8")
    fm, _body = parse_frontmatter(text)

    if not fm:
        result.warn(f"{path}: no frontmatter found")
        return

    # Must have name and description
    if "name" not in fm:
        result.error(f"{path}: missing 'name' in frontmatter")
    else:
        result.ok()

    if "description" not in fm:
        result.error(f"{path}: missing 'description' in frontmatter")
    else:
        result.ok()

    # Must NOT have Claude-specific fields
    # For Cursor: only allowed-tools is invalid (disable-model-invocation is kept)
    leaked_fields = CURSOR_SKILL_FIELDS if platform == "cursor" else CLAUDE_LEAKED_FIELDS
    for field in leaked_fields:
        if field in fm:
            result.error(f"{path}: Claude-specific field '{field}' leaked")


def validate_agent_md(path: Path, result: ValidationResult, platform: str) -> None:
    """Validate a generated agent .md file."""
    text = path.read_text(encoding="utf-8")
    fm, _body = parse_frontmatter(text)

    if not fm:
        result.warn(f"{path}: no frontmatter found")
        return

    if "name" not in fm:
        result.error(f"{path}: missing 'name' in frontmatter")
    else:
        result.ok()

    if platform == "gemini":
        # Model should be a Gemini model, not Claude
        model = fm.get("model", "")
        if model in ("opus", "sonnet", "haiku"):
            result.error(f"{path}: Claude model '{model}' leaked — should be remapped")
        elif model:
            result.ok()


def validate_gemini(dist_dir: Path, result: ValidationResult) -> None:
    """Validate the dist/gemini/ tree.

    Expected Gemini CLI extension layout per official docs:
      gemini-extension.json   (required)
      GEMINI.md               (context file)
      hooks.json              (at extension root, NOT hooks/hooks.json)
      scripts/*.py            (hook scripts)
      skills/*/SKILL.md       (agent skills)
    """
    gemini_dir = dist_dir / "gemini"
    if not gemini_dir.is_dir():
        result.warn("dist/gemini/ not found — skipping Gemini validation")
        return

    for plugin_dir in sorted(gemini_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # gemini-extension.json (required)
        manifest = plugin_dir / "gemini-extension.json"
        if manifest.is_file():
            validate_gemini_manifest(manifest, result)
        else:
            result.error(f"{plugin_dir.name}: missing gemini-extension.json")

        # GEMINI.md (context file)
        gemini_md = plugin_dir / "GEMINI.md"
        if gemini_md.is_file():
            result.ok()
        else:
            result.error(f"{plugin_dir.name}: missing GEMINI.md")

        # hooks.json at extension root (Gemini CLI standard)
        hooks = plugin_dir / "hooks.json"
        if hooks.is_file():
            validate_hooks_json(hooks, result)

        # Warn if old hooks/hooks.json layout is present
        old_hooks = plugin_dir / "hooks" / "hooks.json"
        if old_hooks.is_file():
            result.error(
                f"{plugin_dir.name}: hooks.json at hooks/hooks.json — "
                "should be at extension root per Gemini CLI standard"
            )

        # No agents/ directory expected (agents go in .gemini/agents/, not extensions)
        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            result.warn(
                f"{plugin_dir.name}: agents/ directory present — "
                "Gemini CLI extensions don't bundle agents (use .gemini/agents/ instead)"
            )

        # skills
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_md in sorted(skills_dir.rglob("SKILL.md")):
                validate_skill_md(skill_md, result)

        # Validate hooks.json has no top-level description (not part of Gemini schema)
        if hooks.is_file():
            with open(hooks, encoding="utf-8") as f:
                hooks_data = json.load(f)
            if "description" in hooks_data:
                result.error(
                    f"{plugin_dir.name}: hooks.json has top-level 'description' — "
                    "not part of Gemini CLI hooks schema"
                )


def validate_antigravity(dist_dir: Path, result: ValidationResult) -> None:
    """Validate the dist/antigravity/ tree."""
    anti_dir = dist_dir / "antigravity"
    if not anti_dir.is_dir():
        result.warn("dist/antigravity/ not found — skipping Antigravity validation")
        return

    # Root AGENTS.md
    root_agents = anti_dir / "AGENTS.md"
    if root_agents.is_file():
        result.ok()
    else:
        result.error("dist/antigravity/AGENTS.md missing")

    for plugin_dir in sorted(anti_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # package.json manifest
        pkg_json = plugin_dir / "package.json"
        if pkg_json.is_file():
            pkg_data = validate_json_file(pkg_json, result)
            if pkg_data is not None:
                for field in ("name", "displayName", "version", "description", "publisher"):
                    if field in pkg_data:
                        result.ok()
                    else:
                        result.error(f"{pkg_json}: missing required field '{field}'")
        else:
            result.error(f"{plugin_dir.name}: missing package.json")

        # AGENTS.md
        agents_md = plugin_dir / "AGENTS.md"
        if agents_md.is_file():
            result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing AGENTS.md")

        # .agent/skills/
        agent_skills = plugin_dir / ".agent" / "skills"
        if agent_skills.is_dir():
            for skill_md in sorted(agent_skills.rglob("SKILL.md")):
                validate_skill_md(skill_md, result)
        else:
            result.warn(f"{plugin_dir.name}: missing .agent/skills/ directory")

        # .agent/rules/
        agent_rules = plugin_dir / ".agent" / "rules"
        if agent_rules.is_dir():
            result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing .agent/rules/ directory")


# Claude model names that must NOT appear in Codex agent .toml
CLAUDE_MODEL_NAMES = {"opus", "sonnet", "haiku"}


def validate_codex_agent_toml(path: Path, result: ValidationResult) -> None:
    """Validate a Codex CLI agent .toml file.

    Checks:
    - Contains name, description, developer_instructions
    - No Claude model names (opus, sonnet, haiku)
    """
    text = path.read_text(encoding="utf-8")

    required_keys = {"name", "description", "developer_instructions"}
    found_keys: set[str] = set()

    for line in text.splitlines():
        stripped = line.strip()
        for key in required_keys:
            if stripped.startswith(f"{key} =") or stripped.startswith(f"{key}="):
                found_keys.add(key)

    for key in required_keys:
        if key in found_keys:
            result.ok()
        else:
            result.error(f"{path}: missing required field '{key}'")

    # Check for Claude model leaks
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("model"):
            parts = stripped.split("=", 1)
            if len(parts) == 2:
                value = parts[1].strip().strip('"').strip("'")
                if value in CLAUDE_MODEL_NAMES:
                    result.error(
                        f"{path}: Claude model '{value}' leaked — should be remapped"
                    )
                else:
                    result.ok()


def validate_codex(dist_dir: Path, result: ValidationResult) -> None:
    """Validate the dist/codex/ tree.

    Expected Codex CLI layout per plugin:
      AGENTS.md                        (agent expertise as context)
      .codex/agents/<name>.toml        (subagent definitions)
      .agents/skills/<skill>/SKILL.md  (skills)
      scripts/*.py                     (standalone hook scripts)

    Note: No config.toml is expected — Codex CLI does not have per-tool
    lifecycle hooks.
    """
    codex_dir = dist_dir / "codex"
    if not codex_dir.is_dir():
        result.warn("dist/codex/ not found — skipping Codex validation")
        return

    # Root AGENTS.md
    root_agents = codex_dir / "AGENTS.md"
    if root_agents.is_file():
        result.ok()
    else:
        result.error("dist/codex/AGENTS.md missing")

    for plugin_dir in sorted(codex_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # AGENTS.md
        agents_md = plugin_dir / "AGENTS.md"
        if agents_md.is_file():
            result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing AGENTS.md")

        # No config.toml expected (Codex has no per-tool hooks)
        config_toml = plugin_dir / ".codex" / "config.toml"
        if config_toml.is_file():
            result.warn(
                f"{plugin_dir.name}: .codex/config.toml present but should not "
                "be generated — Codex CLI has no per-tool lifecycle hooks"
            )

        # .codex/agents/*.toml
        codex_agents_dir = plugin_dir / ".codex" / "agents"
        if codex_agents_dir.is_dir():
            for toml_file in sorted(codex_agents_dir.glob("*.toml")):
                validate_codex_agent_toml(toml_file, result)
        else:
            result.warn(f"{plugin_dir.name}: missing .codex/agents/ directory")

        # .agents/skills/
        agents_skills = plugin_dir / ".agents" / "skills"
        if agents_skills.is_dir():
            for skill_md in sorted(agents_skills.rglob("SKILL.md")):
                validate_skill_md(skill_md, result)
        else:
            result.warn(f"{plugin_dir.name}: missing .agents/skills/ directory")


def validate_openclaw_manifest(path: Path, result: ValidationResult) -> None:
    """Validate an openclaw.plugin.json file."""
    data = validate_json_file(path, result)
    if data is None:
        return

    # Required fields
    required = {"id", "configSchema"}
    missing = required - set(data.keys())
    if missing:
        result.error(f"{path}: missing required fields: {missing}")
    else:
        result.ok()

    # Check for Claude model names in the manifest (string representation)
    manifest_str = json.dumps(data)
    for model in CLAUDE_MODEL_NAMES:
        # Check for bare model names that aren't part of provider/model format
        if f'"{model}"' in manifest_str:
            result.error(f"{path}: Claude model name '{model}' leaked in manifest")


def validate_openclaw(dist_dir: Path, result: ValidationResult) -> None:
    """Validate the dist/openclaw/ tree.

    Expected OpenClaw layout per plugin:
      openclaw.plugin.json              (plugin manifest)
      AGENTS.md                         (agent expertise as context)
      skills/<skill>/SKILL.md           (skills)
      scripts/*.py                      (standalone hook scripts)
    """
    openclaw_dir = dist_dir / "openclaw"
    if not openclaw_dir.is_dir():
        result.warn("dist/openclaw/ not found — skipping OpenClaw validation")
        return

    # Root AGENTS.md
    root_agents = openclaw_dir / "AGENTS.md"
    if root_agents.is_file():
        result.ok()
    else:
        result.error("dist/openclaw/AGENTS.md missing")

    for plugin_dir in sorted(openclaw_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # openclaw.plugin.json (required)
        manifest = plugin_dir / "openclaw.plugin.json"
        if manifest.is_file():
            validate_openclaw_manifest(manifest, result)
        else:
            result.error(f"{plugin_dir.name}: missing openclaw.plugin.json")

        # AGENTS.md
        agents_md = plugin_dir / "AGENTS.md"
        if agents_md.is_file():
            result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing AGENTS.md")

        # skills/
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_md in sorted(skills_dir.rglob("SKILL.md")):
                validate_skill_md(skill_md, result)
        else:
            result.warn(f"{plugin_dir.name}: missing skills/ directory")


def validate_cursor_manifest(path: Path, result: ValidationResult) -> None:
    """Validate a .cursor-plugin/plugin.json file."""
    data = validate_json_file(path, result)
    if data is None:
        return

    # Required field: name
    if "name" not in data:
        result.error(f"{path}: missing required field 'name'")
    else:
        result.ok()


def validate_cursor_hooks_json(path: Path, result: ValidationResult) -> None:
    """Validate a Cursor hooks/hooks.json file."""
    data = validate_json_file(path, result)
    if data is None:
        return

    # version field
    if data.get("version") == 1:
        result.ok()
    else:
        result.error(f"{path}: missing or wrong 'version' (expected 1)")

    hooks = data.get("hooks", {})
    for event_name, entries in hooks.items():
        if event_name in CLAUDE_HOOK_EVENTS:
            expected = {"PostToolUse": "postToolUse", "PreToolUse": "preToolUse"}.get(
                event_name
            )
            result.error(
                f"{path}: Claude event '{event_name}' leaked — should be '{expected}'"
            )
        else:
            result.ok()

        # Validate flat structure (each entry should have command directly)
        for entry in entries:
            if "command" in entry:
                result.ok()
                # Check for Claude path variable leak
                cmd = entry["command"]
                if "${CLAUDE_PLUGIN_ROOT}" in cmd:
                    result.error(
                        f"{path}: ${{CLAUDE_PLUGIN_ROOT}} leaked in command — "
                        "should be ${{CURSOR_PLUGIN_ROOT}}"
                    )
            else:
                result.error(f"{path}: hook entry missing 'command' field")
            # Should NOT have nested "hooks" array (Claude structure leak)
            if "hooks" in entry:
                result.error(
                    f"{path}: nested 'hooks' array leaked — "
                    "Cursor uses flat entries (command + matcher at same level)"
                )


def validate_cursor(dist_dir: Path, result: ValidationResult) -> None:
    """Validate the dist/cursor/ tree.

    Expected Cursor plugin layout per plugin:
      .cursor-plugin/plugin.json    (plugin manifest)
      AGENTS.md                     (agent expertise as context)
      agents/<name>.md              (subagent definitions)
      rules/<name>.mdc              (agent expertise as rules)
      skills/<skill>/SKILL.md       (skills — disable-model-invocation allowed)
      hooks/hooks.json              (hooks with Cursor event names)
      scripts/*.py                  (hook scripts)
    """
    cursor_dir = dist_dir / "cursor"
    if not cursor_dir.is_dir():
        result.warn("dist/cursor/ not found — skipping Cursor validation")
        return

    # Root AGENTS.md
    root_agents = cursor_dir / "AGENTS.md"
    if root_agents.is_file():
        result.ok()
    else:
        result.error("dist/cursor/AGENTS.md missing")

    for plugin_dir in sorted(cursor_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        # .cursor-plugin/plugin.json (required)
        manifest = plugin_dir / ".cursor-plugin" / "plugin.json"
        if manifest.is_file():
            validate_cursor_manifest(manifest, result)
        else:
            result.error(f"{plugin_dir.name}: missing .cursor-plugin/plugin.json")

        # AGENTS.md
        agents_md = plugin_dir / "AGENTS.md"
        if agents_md.is_file():
            result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing AGENTS.md")

        # agents/*.md
        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            for agent_md in sorted(agents_dir.glob("*.md")):
                text = agent_md.read_text(encoding="utf-8")
                fm, _body = parse_frontmatter(text)
                if "name" not in fm:
                    result.error(f"{agent_md}: missing 'name' in frontmatter")
                else:
                    result.ok()
                # Model should NOT be a bare Claude name
                model = fm.get("model", "")
                if model in CLAUDE_MODEL_NAMES:
                    result.error(
                        f"{agent_md}: Claude model '{model}' leaked — should be 'inherit'"
                    )
                elif model:
                    result.ok()
        else:
            result.warn(f"{plugin_dir.name}: missing agents/ directory")

        # rules/*.mdc
        rules_dir = plugin_dir / "rules"
        if rules_dir.is_dir():
            for mdc_file in sorted(rules_dir.glob("*.mdc")):
                text = mdc_file.read_text(encoding="utf-8")
                fm, _body = parse_frontmatter(text)
                if fm:
                    result.ok()
                else:
                    result.error(f"{mdc_file}: missing frontmatter")
        else:
            result.warn(f"{plugin_dir.name}: missing rules/ directory")

        # skills/ (disable-model-invocation IS allowed for Cursor)
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_md in sorted(skills_dir.rglob("SKILL.md")):
                validate_skill_md(skill_md, result, platform="cursor")
        else:
            result.warn(f"{plugin_dir.name}: missing skills/ directory")

        # hooks/hooks.json
        hooks = plugin_dir / "hooks" / "hooks.json"
        if hooks.is_file():
            validate_cursor_hooks_json(hooks, result)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate generated plugin output.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dist",
        help="Output directory to validate (default: dist/)",
    )
    args = parser.parse_args()

    dist_dir = (REPO_ROOT / args.output_dir).resolve()

    if not dist_dir.is_dir():
        print(f"Error: output directory not found: {dist_dir}", file=sys.stderr)
        sys.exit(1)

    result = ValidationResult()

    validate_gemini(dist_dir, result)
    validate_antigravity(dist_dir, result)
    validate_codex(dist_dir, result)
    validate_openclaw(dist_dir, result)
    validate_cursor(dist_dir, result)

    print(result.summary())

    if not result.passed:
        sys.exit(1)
    else:
        print("\nAll checks passed.")


if __name__ == "__main__":
    main()
