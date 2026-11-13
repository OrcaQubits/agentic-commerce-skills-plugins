"""Inspect a captured HTTP response or MCP tool result without making payments."""
import argparse
import json
from pathlib import Path
from payment_challenges import classify_response, read_json, validate_x402


def validate_mcp(result):
    if not isinstance(result, dict) or result.get("isError") is not True:
        raise ValueError("payment-required tool result must have isError=true")
    doc = validate_x402(result.get("structuredContent"))
    content = result.get("content")
    if not isinstance(content, list) or not content or not isinstance(content[0], dict) or content[0].get("type") != "text":
        raise ValueError("missing MCP text fallback")
    if read_json(content[0].get("text")) != doc:
        raise ValueError("MCP text and structured challenges differ")
    return doc


def choose_payment(doc, policy):
    """Local one-request guard. No signing or aggregate budget accounting."""
    validate_x402(doc)
    if doc["resource"]["url"] != policy["resource"]:
        raise ValueError("resource is outside the approved policy")
    cap = policy["max_amount"]
    if not isinstance(cap, str) or not cap.isascii() or not cap.isdigit() or len(cap) > 78:
        raise ValueError("invalid policy amount")
    for item in doc["accepts"]:
        if (item["scheme"] == "exact" and item["network"].startswith("eip155:") and
                all(item[k] == policy[k] for k in ("network", "asset", "payTo")) and
                int(item["amount"]) <= int(cap) and
                item.get("extra", {}).get("assetTransferMethod", "eip3009") == "eip3009" and
                item.get("extra", {}).get("paymentFlow", "authorization") == "authorization"):
            return item
    raise ValueError("no supported alternative satisfies the explicit policy")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", type=Path, help="JSON: {status, headers, body} or MCP result")
    ap.add_argument("--transport", choices=("http", "mcp"), default="http")
    args = ap.parse_args()
    try:
        with args.capture.open("rb") as stream:
            capture = read_json(stream.read(16385))
        if args.transport == "mcp":
            validate_mcp(capture)
            result = [{"protocol": "x402", "version": 2, "status": "valid"}]
        else:
            if not isinstance(capture, dict) or not isinstance(capture.get("headers"), dict):
                raise ValueError("capture must contain a headers object")
            result = classify_response(capture.get("status"), capture["headers"], capture.get("body", ""))
        print(json.dumps({"observations": result, "payment_executed": False}, indent=2))
        return 0 if any(r["status"] == "valid" for r in result) else 1
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc), "payment_executed": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
