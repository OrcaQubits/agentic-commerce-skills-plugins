#!/usr/bin/env python3
"""AfterTool hook: detect hardcoded WordPress/WooCommerce secrets in written code."""
import json, sys, re

PATTERNS = [
    (r'DB_PASSWORD["\s,=:]+["\'][^"\']{3,}["\']', "Database password in config"),
    (r'db_password\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded db_password"),
    (r'NONCE_SALT\s*[,=]\s*["\'][^"\']{10,}["\']', "Hardcoded NONCE_SALT"),
    (r'AUTH_KEY\s*[,=]\s*["\'][^"\']{10,}["\']', "Hardcoded AUTH_KEY"),
    (r'SECURE_AUTH_KEY\s*[,=]\s*["\'][^"\']{10,}["\']', "Hardcoded SECURE_AUTH_KEY"),
    (r'LOGGED_IN_KEY\s*[,=]\s*["\'][^"\']{10,}["\']', "Hardcoded LOGGED_IN_KEY"),
    (r'AUTH_SALT\s*[,=]\s*["\'][^"\']{10,}["\']', "Hardcoded AUTH_SALT"),
    (r'STRIPE_SECRET_KEY\s*[=:]\s*["\']sk_live_[^"\']+["\']', "Live Stripe secret key"),
    (r'PAYPAL_CLIENT_SECRET\s*[=:]\s*["\'][^"\']{10,}["\']', "PayPal client secret"),
    (r'consumer_secret\s*[=:>]\s*["\']cs_[^"\']+["\']', "WooCommerce consumer secret"),
    (r'woocommerce_api_key\s*=\s*["\'][^"\']{10,}["\']', "WooCommerce API key"),
    (r'MYSQL_PASSWORD\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded MYSQL_PASSWORD"),
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
            f"{', '.join(warnings)}. Use wp-config.php constants, environment variables, "
            "or a secrets manager instead."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
