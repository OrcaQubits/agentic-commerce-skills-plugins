"""Keep installed readiness independent while sharing the inspected wire parser."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "x402-agentic-payments/scripts/payment_challenges.py"
target = ROOT / "commerce-readiness/scripts/lib/payment_challenges.py"
if __name__ == "__main__":
    target.write_bytes(source.read_bytes())
    print("Synchronized readiness payment parser")
