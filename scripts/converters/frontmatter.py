"""Zero-dependency YAML frontmatter parser, serializer, and transformer.

Handles the subset of YAML used in Claude Code plugin agent and skill files:
simple key-value pairs with optional multi-line values (folded `>` blocks).
"""

from __future__ import annotations

import re
from typing import Optional

# Frontmatter delimiters
_FM_PATTERN = re.compile(r"\A---\r?\n(.*?\r?\n)---\r?\n?", re.DOTALL)

# Claude-only fields that must be stripped for Gemini / Antigravity
CLAUDE_SKILL_FIELDS = {"disable-model-invocation", "allowed-tools"}
CLAUDE_AGENT_FIELDS: set[str] = set()  # None to strip — we remap instead

# Model mapping
MODEL_MAP = {
    "opus": "gemini-2.5-pro",
    "sonnet": "gemini-2.5-flash",
    "haiku": "gemini-2.0-flash-lite",
}

CODEX_MODEL_MAP = {
    "opus": "gpt-5.4",
    "sonnet": "gpt-5.4-mini",
    "haiku": "gpt-5.4-mini",
}

OPENCLAW_MODEL_MAP = {
    "opus": "anthropic/claude-opus-4-6",
    "sonnet": "anthropic/claude-sonnet-4-5",
    "haiku": "anthropic/claude-haiku-4-5",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from a markdown file.

    Returns (frontmatter_dict, body) where body is everything after the
    closing ``---``.  If no frontmatter is found, returns ({}, full_text).
    """
    match = _FM_PATTERN.match(text)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    body = text[match.end():]

    fm: dict[str, str] = {}
    current_key: Optional[str] = None
    current_value_lines: list[str] = []
    is_folded = False

    for line in raw_yaml.splitlines():
        # Check for a new key
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)", line)
        if key_match:
            # Save previous key
            if current_key is not None:
                fm[current_key] = _finalise_value(current_value_lines, is_folded)

            current_key = key_match.group(1)
            value_part = key_match.group(2).strip()
            if value_part == ">":
                is_folded = True
                current_value_lines = []
            else:
                is_folded = False
                current_value_lines = [value_part]
        elif current_key is not None:
            # Continuation line for multi-line value
            current_value_lines.append(line.strip())

    # Save last key
    if current_key is not None:
        fm[current_key] = _finalise_value(current_value_lines, is_folded)

    return fm, body


def _finalise_value(lines: list[str], is_folded: bool) -> str:
    if is_folded:
        return " ".join(l for l in lines if l)
    return lines[0] if lines else ""


def serialize_frontmatter(fm: dict[str, str], body: str) -> str:
    """Serialize a frontmatter dict + body back into a markdown file."""
    if not fm:
        return body

    lines = ["---"]
    for key, value in fm.items():
        # Use folded scalar for long descriptions
        if key == "description" and len(value) > 80:
            lines.append(f"{key}: >")
            # Wrap at ~78 chars
            words = value.split()
            current_line: list[str] = []
            current_len = 0
            for word in words:
                if current_len + len(word) + 1 > 78 and current_line:
                    lines.append("  " + " ".join(current_line))
                    current_line = [word]
                    current_len = len(word)
                else:
                    current_line.append(word)
                    current_len += len(word) + 1
            if current_line:
                lines.append("  " + " ".join(current_line))
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")  # blank line after frontmatter

    return "\n".join(lines) + body


def strip_claude_fields(fm: dict[str, str], field_set: set[str] | None = None) -> dict[str, str]:
    """Remove Claude-specific frontmatter fields."""
    fields = field_set or CLAUDE_SKILL_FIELDS
    return {k: v for k, v in fm.items() if k not in fields}


def remap_for_gemini(fm: dict[str, str], *, is_agent: bool = False) -> dict[str, str]:
    """Remap frontmatter fields for Gemini CLI compatibility.

    For agents: remap ``model`` and ``tools``.
    For skills: strip ``disable-model-invocation`` and ``allowed-tools``.
    """
    result = dict(fm)

    if is_agent:
        # Remap model
        if "model" in result:
            result["model"] = MODEL_MAP.get(result["model"], "gemini-2.5-pro")
        # Remap tools to wildcard
        if "tools" in result:
            result["tools"] = '["*"]'
    else:
        # Strip Claude-only skill fields
        result = strip_claude_fields(result, CLAUDE_SKILL_FIELDS)

    return result


def remap_for_codex(fm: dict[str, str], *, is_agent: bool = False) -> dict[str, str]:
    """Remap frontmatter fields for Codex CLI compatibility.

    For agents: remap ``model``, strip ``tools`` (subagent TOML handles these).
    For skills: strip ``disable-model-invocation`` and ``allowed-tools``.
    """
    result = dict(fm)

    if is_agent:
        if "model" in result:
            result["model"] = CODEX_MODEL_MAP.get(result["model"], "gpt-5.4")
        result.pop("tools", None)
    else:
        result = strip_claude_fields(result, CLAUDE_SKILL_FIELDS)

    return result


def remap_for_openclaw(fm: dict[str, str], *, is_agent: bool = False) -> dict[str, str]:
    """Remap frontmatter fields for OpenClaw compatibility.

    For agents: remap ``model`` to provider/model format, strip ``tools``.
    For skills: strip ``disable-model-invocation`` and ``allowed-tools``
                (OpenClaw skills don't recognize these fields).
    """
    result = dict(fm)

    if is_agent:
        if "model" in result:
            result["model"] = OPENCLAW_MODEL_MAP.get(result["model"], "anthropic/claude-opus-4-6")
        result.pop("tools", None)
    else:
        result = strip_claude_fields(result, CLAUDE_SKILL_FIELDS)

    return result


CURSOR_SKILL_FIELDS = {"allowed-tools"}  # Keep disable-model-invocation — Cursor supports it!


def remap_for_cursor(fm: dict[str, str], *, is_agent: bool = False) -> dict[str, str]:
    """Remap frontmatter fields for Cursor compatibility.

    For agents: set model to 'inherit', strip tools.
    For skills: strip only allowed-tools (keep disable-model-invocation).
    """
    result = dict(fm)

    if is_agent:
        result["model"] = "inherit"
        result.pop("tools", None)
    else:
        result = strip_claude_fields(result, CURSOR_SKILL_FIELDS)

    return result


def remap_for_antigravity(fm: dict[str, str], *, is_agent: bool = False) -> dict[str, str]:
    """Remap frontmatter fields for Antigravity compatibility.

    For agents: strip ``model`` and ``tools`` (not used — expertise goes in AGENTS.md).
    For skills: strip ``disable-model-invocation`` and ``allowed-tools``.
    """
    result = dict(fm)

    if is_agent:
        result.pop("model", None)
        result.pop("tools", None)
    else:
        result = strip_claude_fields(result, CLAUDE_SKILL_FIELDS)

    return result
