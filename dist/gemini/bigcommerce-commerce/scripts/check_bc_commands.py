#!/usr/bin/env python3
"""BeforeTool hook: block potentially destructive BigCommerce / Stencil CLI commands."""
import json, sys, re

# Commands that can cause data loss or production impact
DESTRUCTIVE_PATTERNS = [
    (r'stencil\s+push\s+.*--activate', "Stencil push with activate — immediately replaces the live theme"),
    (r'stencil\s+push\s+.*--delete', "Stencil push with delete — removes previous theme version"),
    (r'curl\s+.*-X\s*DELETE\s+.*api\.bigcommerce\.com', "DELETE request to BigCommerce API — may remove data"),
    (r'curl\s+.*-X\s*DELETE\s+.*\/v[23]\/catalog\/products\b', "Bulk product deletion via API"),
    (r'curl\s+.*-X\s*DELETE\s+.*\/v[23]\/orders\b', "Order deletion via API"),
    (r'curl\s+.*-X\s*DELETE\s+.*\/v[23]\/customers\b', "Customer deletion via API"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'stencil\s+push', "Stencil push — uploads theme to store"),
    (r'stencil\s+release', "Stencil release — publishes theme"),
    (r'curl\s+.*-X\s*PUT\s+.*api\.bigcommerce\.com', "PUT request to BigCommerce API — modifies data"),
    (r'curl\s+.*-X\s*POST\s+.*\/v[23]\/catalog\/products\/.*\/batch', "Batch product modification"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "run_shell_command":
        return

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only check commands that look like Stencil CLI or BigCommerce API calls
    if "stencil" not in command.lower() and "bigcommerce" not in command.lower():
        return

    # Check for destructive commands — block these
    for pattern, desc in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(
                f"Blocked: '{command}' — {desc}. "
                "This command is potentially destructive. "
                "Please confirm with the user before running.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Check for warning commands — add context but allow
    warnings = []
    for pattern, desc in WARNING_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(desc)

    if warnings:
        msg = (
            f"BigCommerce CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
