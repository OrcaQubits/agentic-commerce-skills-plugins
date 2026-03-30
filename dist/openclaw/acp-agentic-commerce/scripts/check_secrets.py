#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded Stripe/ACP payment secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key (sk_live_)"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Test Stripe secret key (sk_test_)"),
    (r'rk_live_[a-zA-Z0-9]{20,}', "Stripe restricted key (rk_live_)"),
    (r'whsec_[a-zA-Z0-9]{20,}', "Stripe webhook secret (whsec_)"),
    (r'STRIPE_SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_SECRET_KEY"),
    (r'STRIPE_API_KEY\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_API_KEY"),
    (r'STRIPE_WEBHOOK_SECRET\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_WEBHOOK_SECRET"),
    (r'Authorization["\s:=]+Bearer\s+[a-zA-Z0-9._-]{30,}', "Hardcoded Bearer token"),
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
            f"Security notice: Possible hardcoded payment secret(s) detected in {file_path}: "
            f"{', '.join(warnings)}. Use environment variables or a secrets manager instead."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
