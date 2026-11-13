"""Catch missing marketplace entries, stale advertised counts, and broken skill refs."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    canonical = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))["plugins"]
    names = {p["name"] for p in canonical}
    skills = {name: {p.parent.name for p in (ROOT / name / "skills").glob("*/SKILL.md")} for name in names}
    for platform, filename in (("codex", ".agents/plugins/marketplace.json"), ("cursor", ".cursor-plugin/marketplace.json")):
        entries = json.loads((ROOT / filename).read_text(encoding="utf-8"))["plugins"]
        if {p["name"] for p in entries} != names or len(entries) != len(names):
            errors.append(filename + ": registration differs from canonical marketplace")
        for entry in entries:
            expected = ("./" if platform == "codex" else "") + "dist/" + platform + "/" + entry["name"]
            actual = entry["source"]["path"] if platform == "codex" else entry["source"]
            if actual != expected:
                errors.append(filename + ": invalid source for " + entry["name"])
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in sorted(names):
        rows = [line for line in readme.splitlines() if line.startswith("| [" + name + "](")]
        if len(rows) != 1 or "**Skills ({}):**".format(len(skills[name])) not in rows[0]:
            errors.append("README inventory missing or stale: " + name)
    ref = re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r"):([a-z0-9]+(?:-[a-z0-9]+)+)")
    for name in names:
        agents = {p.stem for p in (ROOT / name / "agents").glob("*.md")}
        skills[name] |= agents
    for name in names:
        for path in (ROOT / name).rglob("*"):
            if path.suffix not in (".md", ".py"):
                continue
            for plugin, skill in ref.findall(path.read_text(encoding="utf-8")):
                if skill not in skills[plugin]:
                    errors.append(str(path.relative_to(ROOT)) + ": unresolved " + plugin + ":" + skill)
    if (ROOT / "x402-agentic-payments/scripts/payment_challenges.py").read_bytes() != (ROOT / "commerce-readiness/scripts/lib/payment_challenges.py").read_bytes():
        errors.append("payment parser copies differ; run scripts/sync_payment_parser.py")
    for error in sorted(set(errors)):
        print("ERROR", error)
    print("Inventory:", len(names), "plugins;", len(set(errors)), "errors")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
