#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded Shopify secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'shpat_[a-fA-F0-9]{32}', "Shopify Admin API access token (shpat_)"),
    (r'shpss_[a-fA-F0-9]{32}', "Shopify API shared secret (shpss_)"),
    (r'shpca_[a-fA-F0-9]{32}', "Shopify custom app access token (shpca_)"),
    (r'shppa_[a-fA-F0-9]{32}', "Shopify private app access token (shppa_)"),
    (r'shpua_[a-fA-F0-9]{32}', "Shopify user access token (shpua_)"),
    (r'SHOPIFY_API_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Shopify API secret"),
    (r'SHOPIFY_API_KEY\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Shopify API key"),
    (r'SHOPIFY_ACCESS_TOKEN\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Shopify access token"),
    (r'X-Shopify-Access-Token["\s:=]+["\'][a-zA-Z0-9_]{10,}["\']', "Shopify access token in header"),
    (r'STOREFRONT_TOKEN\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Storefront API token"),
    (r'MULTIPASS_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Multipass secret"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key (Shopify Payments uses Stripe)"),
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
            f"{', '.join(warnings)}. Use environment variables or a secrets manager instead."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
