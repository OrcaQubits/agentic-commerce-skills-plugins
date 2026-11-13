"""Synchronize secondary marketplace registration from the Claude marketplace."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))["plugins"]
    for platform, path in (("codex", ".agents/plugins/marketplace.json"),
                           ("cursor", ".cursor-plugin/marketplace.json")):
        target = ROOT / path
        doc = json.loads(target.read_text(encoding="utf-8"))
        existing = {p["name"]: p for p in doc["plugins"]}
        entries = []
        for plugin in source:
            name = plugin["name"]
            entry = existing.get(name)
            if entry is None:
                entry = {"name": name, "description": plugin["description"]}
                if platform == "codex":
                    entry.update(category="Agentic Commerce", policy={"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
            entry["source"] = ({"source": "local", "path": "./dist/codex/" + name}
                               if platform == "codex" else "dist/cursor/" + name)
            entries.append(entry)
        doc["plugins"] = entries
        meta = doc["interface"] if platform == "codex" else doc["metadata"]
        if "x402" not in meta["description"]:
            meta["description"] += ", x402, Trusted Agent Protocol"
        target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Synchronized", path)


if __name__ == "__main__":
    main()
