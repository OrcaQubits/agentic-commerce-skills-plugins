#!/usr/bin/env python3
"""AfterTool hook: detect hardcoded Stripe, crypto, and MPP secrets in written code."""
import json, sys, re

PATTERNS = [
    # Stripe keys
    (r'sk_live_[a-zA-Z0-9]{20,}', "Live Stripe secret key (sk_live_)"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Test Stripe secret key (sk_test_)"),
    (r'rk_live_[a-zA-Z0-9]{20,}', "Stripe restricted key (rk_live_)"),
    (r'whsec_[a-zA-Z0-9]{20,}', "Stripe webhook secret (whsec_)"),
    (r'STRIPE_SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_SECRET_KEY"),
    (r'STRIPE_API_KEY\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_API_KEY"),
    (r'STRIPE_WEBHOOK_SECRET\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded STRIPE_WEBHOOK_SECRET"),
    # MPP secret key (32-byte key for challenge binding)
    (r'MPP_SECRET_KEY\s*=\s*["\'][a-fA-F0-9]{32,}["\']', "Hardcoded MPP_SECRET_KEY (challenge binding key)"),
    (r'secretKey\s*:\s*["\'][a-fA-F0-9]{32,}["\']', "Hardcoded MPP secretKey in config"),
    # Crypto wallet private keys
    (r'0x[a-fA-F0-9]{64}', "Possible Ethereum/Tempo private key (64-hex)"),
    (r'WALLET_PRIVATE_KEY\s*=\s*["\'][^"\']{20,}["\']', "Hardcoded WALLET_PRIVATE_KEY"),
    (r'PRIVATE_KEY\s*=\s*["\']0x[a-fA-F0-9]{64}["\']', "Hardcoded crypto private key"),
    # General auth
    (r'Authorization["\s:=]+Bearer\s+[a-zA-Z0-9._-]{30,}', "Hardcoded Bearer token"),
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private key material"),
    # SPT tokens (should come from API, not hardcoded)
    (r'spt_[a-zA-Z0-9]{20,}', "Hardcoded Shared Payment Token (spt_)"),
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
            f"Security notice: Possible hardcoded payment secret(s) or crypto key(s) detected in "
            f"{file_path}: {', '.join(warnings)}. MPP requires all secrets (Stripe keys, MPP secret "
            f"keys, wallet private keys, SPTs) to be managed via environment variables or a secrets "
            f"manager. Never commit secrets to source control."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
