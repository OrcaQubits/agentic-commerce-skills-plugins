#!/usr/bin/env python3
"""Convert Agentic Commerce Claude Code plugins to Gemini CLI, Antigravity, Codex CLI, OpenClaw, or Cursor format.

Usage:
    python scripts/convert.py                              # Convert all plugins for all platforms
    python scripts/convert.py --platform gemini             # Gemini CLI only
    python scripts/convert.py --platform antigravity        # Antigravity only
    python scripts/convert.py --platform codex              # Codex CLI only
    python scripts/convert.py --platform openclaw           # OpenClaw only
    python scripts/convert.py --platform cursor             # Cursor only
    python scripts/convert.py --plugin ucp-agentic-commerce # Single plugin
    python scripts/convert.py --output-dir build/           # Custom output directory
    python scripts/convert.py --dry-run                     # Preview without writing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the repo root is on sys.path so converters can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from converters.agents import convert_agents_antigravity, generate_plugin_agents_md
from converters.codex import convert_all_codex
from converters.context import generate_gemini_md, generate_root_agents_md
from converters.cursor import convert_all_cursor
from converters.hooks import convert_all_hooks
from converters.manifest import convert_plugin_json, write_gemini_manifest
from converters.openclaw import convert_all_openclaw
from converters.skills import convert_all_skills


def load_marketplace(repo_root: Path) -> list[dict]:
    """Load the plugin list from .claude-plugin/marketplace.json."""
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    with open(marketplace_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("plugins", [])


def resolve_plugin_dir(repo_root: Path, plugin_entry: dict) -> Path:
    """Resolve the plugin source directory from a marketplace entry."""
    source = plugin_entry.get("source", f"./{plugin_entry['name']}")
    return (repo_root / source).resolve()


def convert_plugin_gemini(
    plugin_dir: Path,
    plugin_entry: dict,
    output_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """Convert a single plugin for Gemini CLI.

    Gemini CLI extension layout:
      gemini-extension.json   # Required manifest
      GEMINI.md               # Context file (auto-loaded)
      hooks.json              # Lifecycle hooks (extension root)
      scripts/*.py            # Hook scripts
      skills/*/SKILL.md       # Agent skills

    Note: Agents are NOT part of extensions — Gemini agents live in
    .gemini/agents/.  Agent expertise is delivered via GEMINI.md context.

    Returns a list of file paths (relative to output_root) that were or
    would be written.
    """
    name = plugin_entry["name"]
    out_dir = output_root / "gemini" / name
    files: list[str] = []

    # 1. gemini-extension.json
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if plugin_json.is_file():
        manifest = convert_plugin_json(plugin_json)
        path = out_dir / "gemini-extension.json"
        files.append(str(path.relative_to(output_root)))
        if not dry_run:
            write_gemini_manifest(manifest, path)

    # 2. GEMINI.md (includes agent expertise body)
    gemini_md = generate_gemini_md(
        plugin_dir, name, plugin_entry.get("description", "")
    )
    path = out_dir / "GEMINI.md"
    files.append(str(path.relative_to(output_root)))
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(gemini_md, encoding="utf-8", newline="\n")

    # 3. Hooks (hooks.json at extension root, scripts in scripts/)
    if not dry_run:
        written = convert_all_hooks(plugin_dir, out_dir)
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        hooks_json = plugin_dir / "hooks" / "hooks.json"
        if hooks_json.is_file():
            files.append(str((out_dir / "hooks.json").relative_to(output_root)))
        scripts_dir = plugin_dir / "hooks" / "scripts"
        if scripts_dir.is_dir():
            for py in sorted(scripts_dir.glob("*.py")):
                files.append(
                    str((out_dir / "scripts" / py.name).relative_to(output_root))
                )

    # 4. Skills
    if not dry_run:
        written = convert_all_skills(plugin_dir, out_dir, "gemini")
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        skills_src = plugin_dir / "skills"
        if skills_src.is_dir():
            for skill_dir in sorted(skills_src.iterdir()):
                if (skill_dir / "SKILL.md").is_file():
                    files.append(
                        str(
                            (out_dir / "skills" / skill_dir.name / "SKILL.md").relative_to(
                                output_root
                            )
                        )
                    )

    return files


def convert_plugin_antigravity(
    plugin_dir: Path,
    plugin_entry: dict,
    output_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """Convert a single plugin for Antigravity.

    Returns a list of file paths (relative to output_root) that were or
    would be written.
    """
    name = plugin_entry["name"]
    out_dir = output_root / "antigravity" / name
    files: list[str] = []

    # 1. AGENTS.md + .agent/rules/<plugin>-rules.md
    if not dry_run:
        written = convert_agents_antigravity(plugin_dir, out_dir, name)
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        agents_src = plugin_dir / "agents"
        if agents_src.is_dir() and any(agents_src.glob("*.md")):
            files.append(str((out_dir / "AGENTS.md").relative_to(output_root)))
            files.append(
                str(
                    (out_dir / ".agent" / "rules" / f"{name}-rules.md").relative_to(
                        output_root
                    )
                )
            )

    # 2. GEMINI.md (also useful in Antigravity as supplemental context)
    gemini_md = generate_gemini_md(
        plugin_dir, name, plugin_entry.get("description", "")
    )
    path = out_dir / "GEMINI.md"
    files.append(str(path.relative_to(output_root)))
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(gemini_md, encoding="utf-8", newline="\n")

    # 3. Skills (into .agent/skills/)
    if not dry_run:
        written = convert_all_skills(plugin_dir, out_dir, "antigravity")
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        skills_src = plugin_dir / "skills"
        if skills_src.is_dir():
            for skill_dir in sorted(skills_src.iterdir()):
                if (skill_dir / "SKILL.md").is_file():
                    files.append(
                        str(
                            (
                                out_dir
                                / ".agent"
                                / "skills"
                                / skill_dir.name
                                / "SKILL.md"
                            ).relative_to(output_root)
                        )
                    )

    # Note: No hooks for Antigravity (no hooks system)

    return files


def convert_plugin_codex(
    plugin_dir: Path,
    plugin_entry: dict,
    output_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """Convert a single plugin for OpenAI Codex CLI.

    Codex CLI layout:
      AGENTS.md                        # Agent expertise as context
      .codex/agents/<name>.toml        # Subagent definitions
      .agents/skills/<skill>/SKILL.md  # Skills (stripped frontmatter)
      scripts/*.py                     # Hook scripts as standalone utilities

    Note: No config.toml is generated.  Codex CLI does not support per-tool
    lifecycle hooks.  Hook scripts are copied as standalone utilities.

    Returns a list of file paths (relative to output_root) that were or
    would be written.
    """
    name = plugin_entry["name"]
    out_dir = output_root / "codex" / name
    files: list[str] = []

    # 1. AGENTS.md (reuse existing generator from agents.py)
    agents_md = generate_plugin_agents_md(plugin_dir, name)
    if agents_md:
        path = out_dir / "AGENTS.md"
        files.append(str(path.relative_to(output_root)))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(agents_md, encoding="utf-8", newline="\n")

    # 2. .codex/agents/*.toml + scripts/*.py (no config.toml — no hooks system)
    if not dry_run:
        written = convert_all_codex(plugin_dir, out_dir, name)
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        agents_src = plugin_dir / "agents"
        if agents_src.is_dir():
            for agent_md in sorted(agents_src.glob("*.md")):
                files.append(
                    str(
                        (out_dir / ".codex" / "agents" / f"{agent_md.stem}.toml").relative_to(
                            output_root
                        )
                    )
                )
        scripts_dir = plugin_dir / "hooks" / "scripts"
        if scripts_dir.is_dir():
            for py in sorted(scripts_dir.glob("*.py")):
                files.append(
                    str((out_dir / "scripts" / py.name).relative_to(output_root))
                )

    # 3. Skills (into .agents/skills/)
    if not dry_run:
        written = convert_all_skills(plugin_dir, out_dir, "codex")
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        skills_src = plugin_dir / "skills"
        if skills_src.is_dir():
            for skill_dir in sorted(skills_src.iterdir()):
                if (skill_dir / "SKILL.md").is_file():
                    files.append(
                        str(
                            (
                                out_dir
                                / ".agents"
                                / "skills"
                                / skill_dir.name
                                / "SKILL.md"
                            ).relative_to(output_root)
                        )
                    )

    return files


def convert_plugin_openclaw(
    plugin_dir: Path,
    plugin_entry: dict,
    output_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """Convert a single plugin for OpenClaw.

    OpenClaw layout:
      openclaw.plugin.json              # Plugin manifest (id, configSchema, skills)
      AGENTS.md                         # Agent expertise as context
      skills/<skill>/SKILL.md           # Skills (stripped frontmatter)
      scripts/*.py                      # Hook scripts as standalone utilities

    Note: OpenClaw manages sub-agents via agents.list[] in JSON config, not
    standalone definition files.  Agent expertise is delivered via AGENTS.md.
    OpenClaw hooks are TypeScript-based with different events — no tool-level
    lifecycle hooks.  Hook scripts are copied as standalone utilities.

    Returns a list of file paths (relative to output_root) that were or
    would be written.
    """
    name = plugin_entry["name"]
    out_dir = output_root / "openclaw" / name
    files: list[str] = []

    # 1. AGENTS.md (reuse existing generator from agents.py)
    agents_md = generate_plugin_agents_md(plugin_dir, name)
    if agents_md:
        path = out_dir / "AGENTS.md"
        files.append(str(path.relative_to(output_root)))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(agents_md, encoding="utf-8", newline="\n")

    # 2. Skills (into skills/ — must come before manifest so skill scan works)
    if not dry_run:
        written = convert_all_skills(plugin_dir, out_dir, "openclaw")
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        skills_src = plugin_dir / "skills"
        if skills_src.is_dir():
            for skill_dir in sorted(skills_src.iterdir()):
                if (skill_dir / "SKILL.md").is_file():
                    files.append(
                        str(
                            (out_dir / "skills" / skill_dir.name / "SKILL.md").relative_to(
                                output_root
                            )
                        )
                    )

    # 3. openclaw.plugin.json + scripts/*.py
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if not dry_run:
        written = convert_all_openclaw(plugin_dir, out_dir, name, plugin_json)
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        if plugin_json.is_file():
            files.append(
                str((out_dir / "openclaw.plugin.json").relative_to(output_root))
            )
        scripts_dir = plugin_dir / "hooks" / "scripts"
        if scripts_dir.is_dir():
            for py in sorted(scripts_dir.glob("*.py")):
                files.append(
                    str((out_dir / "scripts" / py.name).relative_to(output_root))
                )

    return files


def convert_plugin_cursor(
    plugin_dir: Path,
    plugin_entry: dict,
    output_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """Convert a single plugin for Cursor.

    Cursor plugin layout:
      .cursor-plugin/plugin.json      # Plugin manifest (with component paths)
      agents/<name>-expert.md         # Subagent definitions (model: inherit)
      rules/<name>-expert.mdc         # Agent expertise as .mdc rules
      skills/<skill>/SKILL.md         # Skills (keep disable-model-invocation)
      hooks/hooks.json                # Hooks with Cursor event names
      scripts/*.py                    # Hook scripts

    Returns a list of file paths (relative to output_root) that were or
    would be written.
    """
    name = plugin_entry["name"]
    out_dir = output_root / "cursor" / name
    files: list[str] = []

    # 1. AGENTS.md (reuse existing generator)
    agents_md = generate_plugin_agents_md(plugin_dir, name)
    if agents_md:
        path = out_dir / "AGENTS.md"
        files.append(str(path.relative_to(output_root)))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(agents_md, encoding="utf-8", newline="\n")

    # 2. Skills (into skills/ — must come before manifest so skill scan works)
    if not dry_run:
        written = convert_all_skills(plugin_dir, out_dir, "cursor")
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        skills_src = plugin_dir / "skills"
        if skills_src.is_dir():
            for skill_dir in sorted(skills_src.iterdir()):
                if (skill_dir / "SKILL.md").is_file():
                    files.append(
                        str(
                            (out_dir / "skills" / skill_dir.name / "SKILL.md").relative_to(
                                output_root
                            )
                        )
                    )

    # 3. Manifest + agents + rules + hooks + scripts
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if not dry_run:
        written = convert_all_cursor(plugin_dir, out_dir, name, plugin_json)
        files.extend(str(p.relative_to(output_root)) for p in written)
    else:
        if plugin_json.is_file():
            files.append(
                str((out_dir / ".cursor-plugin" / "plugin.json").relative_to(output_root))
            )
        agents_src = plugin_dir / "agents"
        if agents_src.is_dir():
            for agent_md in sorted(agents_src.glob("*.md")):
                files.append(
                    str((out_dir / "agents" / agent_md.name).relative_to(output_root))
                )
                files.append(
                    str(
                        (out_dir / "rules" / f"{agent_md.stem}.mdc").relative_to(output_root)
                    )
                )
        hooks_json = plugin_dir / "hooks" / "hooks.json"
        if hooks_json.is_file():
            files.append(
                str((out_dir / "hooks" / "hooks.json").relative_to(output_root))
            )
        scripts_dir = plugin_dir / "hooks" / "scripts"
        if scripts_dir.is_dir():
            for py in sorted(scripts_dir.glob("*.py")):
                files.append(
                    str((out_dir / "scripts" / py.name).relative_to(output_root))
                )

    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Claude Code plugins to Gemini CLI / Antigravity / Codex CLI / OpenClaw / Cursor format."
    )
    parser.add_argument(
        "--platform",
        choices=["gemini", "antigravity", "codex", "openclaw", "cursor", "all"],
        default="all",
        help="Target platform (default: all)",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        default=None,
        help="Convert only this plugin (by name from marketplace.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dist",
        help="Output directory (default: dist/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be generated without writing them",
    )

    args = parser.parse_args()

    output_root = (REPO_ROOT / args.output_dir).resolve()
    plugins = load_marketplace(REPO_ROOT)

    # Filter to single plugin if requested
    if args.plugin:
        plugins = [p for p in plugins if p["name"] == args.plugin]
        if not plugins:
            print(f"Error: plugin '{args.plugin}' not found in marketplace.json", file=sys.stderr)
            sys.exit(1)

    platforms = (
        ["gemini", "antigravity", "codex", "openclaw", "cursor"]
        if args.platform == "all"
        else [args.platform]
    )

    all_files: list[str] = []

    for plugin_entry in plugins:
        plugin_dir = resolve_plugin_dir(REPO_ROOT, plugin_entry)
        name = plugin_entry["name"]

        if not plugin_dir.is_dir():
            print(f"Warning: plugin directory not found: {plugin_dir}", file=sys.stderr)
            continue

        for platform in platforms:
            if platform == "gemini":
                files = convert_plugin_gemini(
                    plugin_dir, plugin_entry, output_root, dry_run=args.dry_run
                )
            elif platform == "codex":
                files = convert_plugin_codex(
                    plugin_dir, plugin_entry, output_root, dry_run=args.dry_run
                )
            elif platform == "openclaw":
                files = convert_plugin_openclaw(
                    plugin_dir, plugin_entry, output_root, dry_run=args.dry_run
                )
            elif platform == "cursor":
                files = convert_plugin_cursor(
                    plugin_dir, plugin_entry, output_root, dry_run=args.dry_run
                )
            else:
                files = convert_plugin_antigravity(
                    plugin_dir, plugin_entry, output_root, dry_run=args.dry_run
                )
            all_files.extend(files)

            if not args.dry_run:
                print(f"  [{platform}] {name}: {len(files)} files")

    # Generate root-level AGENTS.md for platforms that use it
    for plat in ("antigravity", "codex", "openclaw", "cursor"):
        if plat in platforms:
            root_agents = generate_root_agents_md(plugins, REPO_ROOT, platform=plat)
            path = output_root / plat / "AGENTS.md"
            rel = str(path.relative_to(output_root))
            all_files.append(rel)
            if not args.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(root_agents, encoding="utf-8", newline="\n")
                print(f"  [{plat}] root AGENTS.md")

    # Summary
    if args.dry_run:
        print(f"Dry run — {len(all_files)} files would be generated:\n")
        for f in sorted(all_files):
            print(f"  {f}")
    else:
        print(f"\nDone — {len(all_files)} files generated in {output_root}")


if __name__ == "__main__":
    main()
