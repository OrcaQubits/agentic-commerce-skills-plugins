#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded Salesforce secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'COMMERCE_CLIENT_ID\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Commerce Cloud client ID"),
    (r'COMMERCE_CLIENT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Commerce Cloud client secret"),
    (r'SFCC_OAUTH_CLIENT_ID\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded SFCC OAuth client ID"),
    (r'SFCC_OAUTH_CLIENT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded SFCC OAuth client secret"),
    (r'SF_ACCESS_TOKEN\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Salesforce access token"),
    (r'SFDX_AUTH_URL\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded SFDX auth URL"),
    (r'SALESFORCE_CLIENT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Salesforce client secret"),
    (r'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+', "Bearer JWT token"),
    (r'"client_secret"\s*:\s*"[^"]{10,}"', "Client secret in JSON"),
    (r'"password"\s*:\s*"[^"]{5,}"', "Password in dw.json or config"),
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private key material"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key (Salesforce Payments uses Stripe)"),
    (r'00D[a-zA-Z0-9]{12,15}', "Salesforce Org ID in auth string"),
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
