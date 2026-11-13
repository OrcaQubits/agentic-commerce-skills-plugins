"""Install locked SDK dependencies outside the plugin and run the offline fixture."""
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    node = shutil.which("node")
    if not npm or not node:
        raise SystemExit("Node 22+ and npm are required")
    version = subprocess.check_output([node, "--version"], text=True).strip()
    if int(version.lstrip("v").split(".")[0]) < 22:
        raise SystemExit("Node 22+ is required; found " + version)
    source = Path(__file__).resolve().parent / "sdk"
    with tempfile.TemporaryDirectory(prefix="x402-sdk-") as work:
        for name in ("package.json", "package-lock.json", "fixture.mjs", "settlement_guard.mjs"):
            shutil.copy2(source / name, Path(work) / name)
        subprocess.run([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund",
                        "--registry=https://registry.npmjs.org"], cwd=work, check=True)
        subprocess.run([node, "fixture.mjs"], cwd=work, check=True)


if __name__ == "__main__":
    main()
