#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded secrets in WebMCP tool registration code."""
import json, sys, re

PATTERNS = [
    (r'["\']Bearer\s+[a-zA-Z0-9._-]{30,}["\']', "Hardcoded Bearer token string"),
    (r'api_key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded api_key value"),
    (r'API_KEY\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded API_KEY value"),
    (r'AUTH_TOKEN\s*=\s*["\'][a-zA-Z0-9._-]{20,}["\']', "Hardcoded AUTH_TOKEN value"),
    (r'client_secret\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded client_secret"),
    (r'OPENAI_API_KEY\s*=\s*["\']sk-[^"\']+["\']', "Hardcoded OpenAI API key"),
    (r'GOOGLE_API_KEY\s*=\s*["\']AIza[^"\']+["\']', "Hardcoded Google API key"),
    (r'ANTHROPIC_API_KEY\s*=\s*["\']sk-ant-[^"\']+["\']', "Hardcoded Anthropic API key"),
    (r'STRIPE_SECRET_KEY\s*=\s*["\']sk_(live|test)_[^"\']+["\']', "Hardcoded Stripe secret key"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe live secret key"),
    (r'shpat_[a-fA-F0-9]{32,}', "Shopify admin API token"),
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
