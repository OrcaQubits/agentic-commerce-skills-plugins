#!/usr/bin/env python3
"""AfterTool hook: detect hardcoded Magento/database secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'db-password["\s:=]+["\'][^"\']{3,}["\']', "Database password in config"),
    (r'db_password\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded db_password"),
    (r'admin-password["\s:=]+["\'][^"\']{3,}["\']', "Admin password in config"),
    (r'crypt/key["\s:=]+["\'][a-f0-9]+["\']', "Magento encryption key"),
    (r'MAGENTO_DB_PASSWORD\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded MAGENTO_DB_PASSWORD"),
    (r'MYSQL_PASSWORD\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded MYSQL_PASSWORD"),
    (r'MYSQL_ROOT_PASSWORD\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded MYSQL_ROOT_PASSWORD"),
    (r'encryption_key\s*=\s*["\'][a-f0-9]+["\']', "Hardcoded encryption key"),
    (r'oauth[_-]consumer[_-]secret\s*=\s*["\'][^"\']{10,}["\']', "OAuth consumer secret"),
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
            f"{', '.join(warnings)}. Use env.php, environment variables, or a secrets manager instead."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
