#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded Shopify/Google commerce secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'shpat_[a-f0-9]{32,}', "Shopify access token (shpat_)"),
    (r'shpss_[a-f0-9]{32,}', "Shopify shared secret (shpss_)"),
    (r'SHOPIFY_API_KEY\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded SHOPIFY_API_KEY"),
    (r'SHOPIFY_API_SECRET\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded SHOPIFY_API_SECRET"),
    (r'GOOGLE_API_KEY\s*=\s*["\']AIza[^"\']+["\']', "Hardcoded Google API key"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key"),
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private key material"),
]

SKIP_EXTENSIONS = {".md", ".txt", ".rst", ".csv", ".svg", ".png", ".jpg", ".gif"}


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")
    else:
        return

    file_path = tool_input.get("file_path", "")
    if any(file_path.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        return

    warnings = []
    for pattern, desc in PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            warnings.append(desc)

    if warnings:
        msg = (
            f"Security notice: Possible hardcoded secret(s) detected in {file_path}: "
            f"{', '.join(warnings)}. Consider using environment variables instead."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
