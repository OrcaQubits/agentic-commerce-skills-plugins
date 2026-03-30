#!/usr/bin/env python3
"""AfterTool hook: detect hardcoded BigCommerce secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'X-Auth-Token["\s:=]+["\'][a-z0-9]{20,}["\']', "BigCommerce API auth token"),
    (r'ACCESS_TOKEN\s*[=:]\s*["\'][a-z0-9]{20,}["\']', "Hardcoded access token"),
    (r'CLIENT_SECRET\s*[=:]\s*["\'][a-z0-9]{20,}["\']', "Hardcoded client secret"),
    (r'CLIENT_ID\s*[=:]\s*["\'][a-z0-9]{20,}["\']', "Hardcoded client ID"),
    (r'STORE_HASH\s*[=:]\s*["\'][a-z0-9]+["\']', "Hardcoded store hash"),
    (r'API_TOKEN\s*[=:]\s*["\'][a-z0-9]{20,}["\']', "Hardcoded API token"),
    (r'BIGCOMMERCE_ACCESS_TOKEN\s*=\s*["\'][^"\']{10,}["\']', "BigCommerce access token in env"),
    (r'BIGCOMMERCE_CLIENT_SECRET\s*=\s*["\'][^"\']{10,}["\']', "BigCommerce client secret in env"),
    (r'stencil_token\s*[=:]\s*["\'][^"\']{10,}["\']', "Stencil CLI token"),
    (r'STRIPE_SECRET_KEY\s*[=:]\s*["\']sk_live_[^"\']+["\']', "Live Stripe secret key"),
    (r'PAYPAL_CLIENT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "PayPal client secret"),
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

    if tool_name == "write_file":
        content = tool_input.get("content", "")
    elif tool_name == "edit_file":
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
