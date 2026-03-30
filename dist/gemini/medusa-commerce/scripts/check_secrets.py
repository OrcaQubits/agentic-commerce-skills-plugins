#!/usr/bin/env python3
"""AfterTool hook: detect hardcoded Medusa / database secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key"),
    (r'pk_live_[a-zA-Z0-9]{20,}', "Live Stripe publishable key"),
    (r'MEDUSA_ADMIN_[A-Z_]*\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded Medusa admin secret"),
    (r'DATABASE_URL\s*[=:]\s*["\']postgres(ql)?://[^"\']{10,}["\']', "Hardcoded database URL with credentials"),
    (r'REDIS_URL\s*[=:]\s*["\']redis://[^"\']{10,}["\']', "Hardcoded Redis URL with credentials"),
    (r'JWT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded JWT secret"),
    (r'COOKIE_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "Hardcoded cookie secret"),
    (r'STORE_CORS\s*[=:]\s*["\']\*["\']', "Wildcard STORE_CORS — potential security risk"),
    (r'ADMIN_CORS\s*[=:]\s*["\']\*["\']', "Wildcard ADMIN_CORS — potential security risk"),
    (r'AUTH_CORS\s*[=:]\s*["\']\*["\']', "Wildcard AUTH_CORS — potential security risk"),
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
