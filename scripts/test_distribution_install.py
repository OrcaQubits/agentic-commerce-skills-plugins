"""Check marketplace resolution and real bundle entry points before release."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = {"x402-agentic-payments": 7, "trusted-agent-protocol": 6}
REPOSITORY = "https://github.com/OrcaQubits/agentic-commerce-skills-plugins"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


class DistributionInstallTests(unittest.TestCase):
    def test_marketplace_discovery_resolves_both_plugins(self):
        for platform, catalog in (
            ("claude", ".claude-plugin/marketplace.json"),
            ("codex", ".agents/plugins/marketplace.json"),
            ("cursor", ".cursor-plugin/marketplace.json"),
        ):
            entries = read(ROOT / catalog)["plugins"]
            for name, count in PLUGINS.items():
                with self.subTest(platform=platform, plugin=name):
                    matches = [entry for entry in entries if entry["name"] == name]
                    self.assertEqual(len(matches), 1)
                    source = matches[0]["source"]
                    folder = ROOT / (source["path"] if isinstance(source, dict) else source)
                    self.assertTrue(folder.resolve().is_relative_to(ROOT))
                    self.assertEqual(read(folder / f".{platform}-plugin/plugin.json")["name"], name)
                    self.assertEqual(len(list((folder / "skills").glob("*/SKILL.md"))), count)

    def test_installed_bundle_entry_points_and_resources(self):
        # Copy the whole package just as native local installers do. Inspect only
        # declared/default discovery roots, not an indiscriminate recursive scan.
        with tempfile.TemporaryDirectory(prefix="commerce-install-") as temporary:
            for platform in ("claude", "codex", "cursor", "gemini", "antigravity", "openclaw"):
                for name, count in PLUGINS.items():
                    with self.subTest(platform=platform, plugin=name):
                        source = ROOT / name if platform == "claude" else ROOT / "dist" / platform / name
                        target = Path(temporary) / platform / name
                        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
                        if platform == "gemini":
                            manifest = read(target / "gemini-extension.json")
                            self.assertTrue((target / manifest["contextFileName"]).is_file())
                        elif platform == "antigravity":
                            manifest = read(target / "plugin.json")
                            self.assertTrue((target / "rules/AGENTS.md").is_file())
                        else:
                            kind = "claude" if platform == "openclaw" else platform
                            manifest = read(target / f".{kind}-plugin/plugin.json")
                        self.assertEqual(manifest["name"], name)
                        if platform != "cursor":
                            repository = manifest["repository"]
                            self.assertEqual(repository.get("url") if isinstance(repository, dict) else repository, REPOSITORY)
                        skill_roots = manifest.get("skills", ["skills"]) if platform == "antigravity" else ["skills"]
                        discovered = []
                        for root in skill_roots:
                            skill_root = target / root
                            self.assertTrue(skill_root.resolve().is_relative_to(target))
                            discovered.extend(skill_root.glob("*/SKILL.md"))
                        self.assertEqual(len(discovered), count)
                        for skill in discovered:
                            resources = next((p for p in skill.parents if (p / "scripts/test_conformance.py").is_file()), None)
                            self.assertEqual(resources, target)
                        for resource in ("scripts/test_conformance.py", "audit/source-baseline.md", "evals/scenarios.json"):
                            self.assertEqual((target / resource).read_bytes(), (ROOT / name / resource).read_bytes())
                        if platform == "openclaw":
                            self.assertFalse((target / "openclaw.plugin.json").exists(), "Native marker shadows bundle detection")
                            package = read(target / "package.json")
                            self.assertNotIn("extensions", package["openclaw"])
                            self.assertEqual(package["openclaw"]["manifest"], "./.claude-plugin/plugin.json")


if __name__ == "__main__":
    unittest.main()
