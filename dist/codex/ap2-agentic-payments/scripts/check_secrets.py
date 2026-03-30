#!/usr/bin/env python3
"""PostToolUse hook: detect hardcoded PCI data and payment secrets in AP2 code."""
import json, sys, re

PATTERNS = [
    # PCI data patterns
    (r'["\'][45]\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}["\']', "Possible credit card number (Visa/MC)"),
    (r'cvv\s*=\s*["\']?\d{3,4}["\']?', "Hardcoded CVV/CVC value"),
    (r'card_number\s*=\s*["\'][0-9\s-]{13,19}["\']', "Hardcoded card_number"),
    # Payment secret patterns
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key (sk_live_)"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Test Stripe secret key (sk_test_)"),
    (r'payment_token\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Hardcoded payment_token"),
    # Cryptographic material
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private key material — use key management service"),
    (r'signing_key\s*=\s*["\'][a-zA-Z0-9/+=]{20,}["\']', "Hardcoded signing_key"),
    (r'device_key\s*=\s*["\'][a-zA-Z0-9/+=]{20,}["\']', "Hardcoded device_key"),
    # General auth
    (r'GOOGLE_API_KEY\s*=\s*["\']AIza[^"\']+["\']', "Hardcoded Google API key"),
    (r'Authorization["\s:=]+Bearer\s+[a-zA-Z0-9._-]{30,}', "Hardcoded Bearer token"),
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
            f"Security notice: Possible hardcoded payment secret(s) or PCI data detected in "
            f"{file_path}: {', '.join(warnings)}. AP2 requires role-based data separation — "
            f"Shopping Agents must never access PCI/PII data. Use environment variables, "
            f"key management services, or Credentials Provider for payment data."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
