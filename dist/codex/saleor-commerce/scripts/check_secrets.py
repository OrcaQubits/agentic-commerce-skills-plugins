#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded Saleor / database secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key"),
    (r'pk_live_[a-zA-Z0-9]{20,}', "Live Stripe publishable key"),
    (r'SECRET_KEY\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Django SECRET_KEY"),
    (r'DATABASE_URL\s*[=:]\s*["\']postgres(ql)?://[^"\']{10,}["\']', "Hardcoded database URL with credentials"),
    (r'REDIS_URL\s*[=:]\s*["\']redis://[^"\']{10,}["\']', "Hardcoded Redis URL with credentials"),
    (r'CELERY_BROKER_URL\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Celery broker URL with credentials"),
    (r'ALLOWED_HOSTS\s*[=:]\s*\[?\s*["\']?\*["\']?\s*\]?', "Wildcard ALLOWED_HOSTS — potential security risk"),
    (r'SALEOR_[A-Z_]*SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Saleor secret"),
    (r'JWT_[A-Z_]*SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded JWT secret"),
    (r'RSA_PRIVATE_KEY\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded RSA private key value"),
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
