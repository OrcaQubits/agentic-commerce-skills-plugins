"""Run new-plugin fixtures from independent installed copies on all five targets."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("x402-agentic-payments", "trusted-agent-protocol")
PLATFORMS = ("gemini", "antigravity", "codex", "openclaw", "cursor")


def check_hook(script, platform):
    name = "write_file" if platform == "gemini" else "Write"
    # Construct fake material at runtime so no credential-shaped fixture is stored.
    secret = "-----BEGIN " + "PRIVATE KEY-----"
    payload = {"tool_name": name, "tool_input": {"content": secret, "file_path": "fixture.py"}}
    result = subprocess.run([sys.executable, str(script)], input=json.dumps(payload),
                            text=True, capture_output=True, check=True)
    assert "systemMessage" in json.loads(result.stdout), (script, result.stdout)
    assert secret not in result.stdout
    for content in ("{invalid-json", "[]", '{"tool_input":null}', json.dumps({"tool_name": name, "tool_input": {"content": "a public transaction hash: 0x" + "a" * 64}})):
        clean = subprocess.run([sys.executable, str(script)], input=content,
                               text=True, capture_output=True, check=True)
        assert not clean.stdout.strip(), (script, clean.stdout)


def main():
    for plugin in PLUGINS:
        check_hook(ROOT / plugin / "hooks/scripts/check_secrets.py", "claude")
    with tempfile.TemporaryDirectory(prefix="commerce-bundles-") as work:
        stage = Path(work)
        for platform in PLATFORMS:
            for plugin in PLUGINS:
                source = ROOT / "dist" / platform / plugin
                target = stage / platform / plugin
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
                skills = list(target.rglob("SKILL.md"))
                assert skills, source
                for skill in skills:
                    found = next((p for p in skill.parents if (p / "scripts/test_conformance.py").is_file()), None)
                    assert found == target, (skill, found)
                assert (target / "audit/source-baseline.md").is_file()
                assert (target / "evals/scenarios.json").is_file()
                subprocess.run([sys.executable, str(target / "scripts/test_conformance.py")], cwd=stage, check=True)
                if plugin == "x402-agentic-payments":
                    for name in ("package.json", "package-lock.json", "fixture.mjs", "settlement_guard.mjs"):
                        assert (target / "scripts/sdk" / name).is_file()
                for hook in target.rglob("check_secrets.py"):
                    check_hook(hook, platform)
                print("PASS independent bundle:", platform, plugin)
    print("10 independent bundle fixture suites and source/converted advisory hooks passed")


if __name__ == "__main__":
    main()
