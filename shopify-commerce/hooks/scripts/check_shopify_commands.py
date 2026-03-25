#!/usr/bin/env python3
"""PreToolUse hook: block potentially destructive Shopify CLI commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'shopify\s+theme\s+push\s+.*--live', "Push to live theme — can break production storefront"),
    (r'shopify\s+theme\s+delete', "Theme deletion — permanent data loss"),
    (r'shopify\s+app\s+deploy\s+.*--force', "Force app deploy — bypasses safety checks"),
    (r'curl\s+.*-X\s+DELETE\s+.*myshopify\.com', "DELETE request to Shopify store — potential data loss"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'shopify\s+theme\s+push', "Theme push — will overwrite remote theme files"),
    (r'shopify\s+app\s+deploy', "App deploy — will publish app changes to merchants"),
    (r'shopify\s+app\s+release', "App release — will make new version available to all users"),
    (r'curl\s+.*-X\s+PUT\s+.*myshopify\.com', "PUT request to Shopify store — will modify data"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        return

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only check commands that look like Shopify CLI or Shopify API calls
    if "shopify" not in command.lower() and "myshopify.com" not in command.lower():
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
            f"Shopify CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
