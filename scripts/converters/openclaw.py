"""Convert plugins to OpenClaw content bundles.

The .claude-plugin/plugin.json marker selects OpenClaw's bundle loader. Do not
emit openclaw.plugin.json: that selects the native JavaScript plugin loader.
Skills and executable/reference resources stay together. Python hooks remain
standalone utilities; no native hook enforcement is supplied by this converter.
Package metadata supports a separate ClawHub publishing workflow and does not
establish registry availability. See https://docs.openclaw.ai/plugins/bundles.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


# ClawHub publish defaults — override via env vars before running convert.py.
DEFAULT_CLAWHUB_SCOPE = os.environ.get("CLAWHUB_SCOPE", "@orcaqubits")
DEFAULT_PLUGIN_API = os.environ.get("CLAWHUB_PLUGIN_API", ">=2026.3.24-beta.2")
DEFAULT_OPENCLAW_VERSION = os.environ.get("CLAWHUB_OPENCLAW_VERSION", "2026.3.24-beta.2")
DEFAULT_REPO_URL = os.environ.get(
    "CLAWHUB_REPO_URL",
    "https://github.com/OrcaQubits/agentic-commerce-skills-plugins",
)


def generate_clawhub_package_json(plugin_json_path: Path) -> dict:
    """Generate a ClawHub-publish-ready ``package.json`` from a Claude plugin.json.

    Required fields per https://docs.openclaw.ai/clawhub/cli :

    * ``openclaw.compat.pluginApi``  — semver range
    * ``openclaw.build.openclawVersion`` — exact build version

    The package ``name`` is scoped (``@orcaqubits/openclaw-<plugin>``) so
    ``clawhub package publish --owner orcaqubits`` works.  Override the scope
    by setting ``CLAWHUB_SCOPE`` before running ``convert.py``.
    """
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    plugin_name = data.get("name", "")
    scope = DEFAULT_CLAWHUB_SCOPE.rstrip("/")
    package_name = (
        f"{scope}/openclaw-{plugin_name}"
        if scope and scope.startswith("@")
        else f"openclaw-{plugin_name}"
    )

    pkg = {
        "name": package_name,
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", ""),
        "type": "module",
        "license": data.get("license", "MIT"),
        "keywords": ["openclaw", "clawhub-plugin"] + list(data.get("keywords", [])),
        "repository": {"type": "git", "url": DEFAULT_REPO_URL},
        "openclaw": {
            "compat": {"pluginApi": DEFAULT_PLUGIN_API},
            "build": {"openclawVersion": DEFAULT_OPENCLAW_VERSION},
            "hostTargets": ["openclaw"],
            "manifest": "./.claude-plugin/plugin.json",
        },
    }

    author = data.get("author")
    if isinstance(author, dict):
        pkg["author"] = author
    elif isinstance(author, str):
        pkg["author"] = author

    return pkg


CLAWHUB_IGNORE_CONTENT = """# ClawHub publish ignore patterns
.git/
.DS_Store
node_modules/
*.log
.env
.env.*
"""


def generate_openclaw_manifest(plugin_json_path: Path) -> dict:
    """Use OpenClaw's Claude content-bundle loader, without native-code markers."""
    with open(plugin_json_path, encoding="utf-8") as f:
        data = json.load(f)

    return {key: data[key] for key in
            ("name", "version", "description", "author", "repository", "license", "keywords")
            if key in data}


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
    """Write the bundle marker, ClawHub package.json, .clawhubignore, and copy hook scripts.

    Creates:
      output_dir/.claude-plugin/plugin.json (content-bundle marker)
      output_dir/package.json          (ClawHub publish manifest — bundle-plugin family)
      output_dir/.clawhubignore        (publish-ignore patterns)
      output_dir/scripts/*.py          (hook scripts as standalone utilities)

    Returns list of written paths.
    """
    written: list[Path] = []

    if plugin_json_path.is_file():
        # A native marker takes precedence over bundle detection and requires a
        # JavaScript entry point. These packages contain skills, not native code.
        (output_dir / "openclaw.plugin.json").unlink(missing_ok=True)
        manifest = generate_openclaw_manifest(plugin_json_path)
        out_path = output_dir / ".claude-plugin" / "plugin.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(out_path)

        # 2. package.json — required by `clawhub package publish`
        pkg = generate_clawhub_package_json(plugin_json_path)
        pkg_path = output_dir / "package.json"
        pkg_path.write_text(
            json.dumps(pkg, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(pkg_path)

        # 3. .clawhubignore — keep publish payload tidy
        ignore_path = output_dir / ".clawhubignore"
        ignore_path.write_text(CLAWHUB_IGNORE_CONTENT, encoding="utf-8", newline="\n")
        written.append(ignore_path)

    # 4. Hook scripts as standalone utilities
    written.extend(copy_hook_scripts(plugin_dir, output_dir))

    return written
