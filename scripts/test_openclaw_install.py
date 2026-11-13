"""Run the native OpenClaw installer in a temporary profile (no gateway or model)."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("x402-agentic-payments", "trusted-agent-protocol")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, help="Path to openclaw.mjs")
    parser.add_argument("--bundle-root", type=Path, default=ROOT / "dist/openclaw")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="commerce-openclaw-install-") as temporary:
        profile = Path(temporary)
        env = {**os.environ, "OPENCLAW_STATE_DIR": str(profile),
               "OPENCLAW_CONFIG_PATH": str(profile / "openclaw.json"), "NO_COLOR": "1"}

        def run(*command):
            result = subprocess.run(["node", args.cli, *command], cwd=profile, env=env,
                                    capture_output=True, text=True, encoding="utf-8", timeout=180)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            return result.stdout

        for plugin in PLUGINS:
            # Explicitly trust these reviewed repository bundles in the isolated
            # CI profile; the native CLI otherwise cancels non-interactive installs.
            print(run("plugins", "install", str((args.bundle_root / plugin).resolve()),
                      "--force", "--accept-capabilities"), flush=True)
        installed = json.loads(run("plugins", "list", "--json"))
        entries = installed["plugins"] if isinstance(installed, dict) else installed
        for plugin in PLUGINS:
            entry = next(item for item in entries if item["id"] == plugin)
            assert entry.get("status") != "error", entry
            assert entry.get("enabled") is not False, entry
        inventory = json.loads(run("skills", "list", "--json"))
        skills = inventory["skills"] if isinstance(inventory, dict) else inventory
        expected = {path.parent.name for plugin in PLUGINS
                    for path in (args.bundle_root / plugin / "skills").glob("*/SKILL.md")}
        found = {skill["name"] for skill in skills}
        assert expected <= found, (expected - found)
        for plugin in PLUGINS:
            roots = [path.parent.parent for path in profile.rglob("scripts/test_conformance.py")
                     if path.parent.parent.name == plugin]
            assert roots, f"Installed {plugin} lost its executable resources"
            for root in roots:
                assert (root / "audit/source-baseline.md").is_file()
                assert (root / "evals/scenarios.json").is_file()
        print(f"PASS native OpenClaw installs: 2 plugins, {len(expected)} skills, executable resources retained")


if __name__ == "__main__":
    main()
