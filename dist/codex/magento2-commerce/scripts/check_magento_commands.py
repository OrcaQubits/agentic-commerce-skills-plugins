#!/usr/bin/env python3
"""PreToolUse hook: block potentially destructive Magento CLI commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'setup:db:rollback', "Database rollback — can cause data loss"),
    (r'setup:uninstall', "Full Magento uninstall"),
    (r'indexer:reset\s+--all', "Reset all indexers — causes full reindex on next run"),
    (r'catalog:images:resize\s+--all.*--force', "Force resize all images — heavy I/O operation"),
    (r'module:uninstall', "Module removal — may break dependencies"),
    (r'deploy:mode:set\s+developer', "Switch to developer mode — unsafe in production"),
    (r'setup:rollback', "Setup rollback — can cause data loss"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'cache:clean', "Cache clean — may cause temporary performance degradation"),
    (r'cache:flush', "Cache flush — clears all caches including external storage"),
    (r'setup:upgrade', "Setup upgrade — runs database migrations"),
    (r'setup:di:compile', "DI compilation — resource-intensive operation"),
    (r'setup:static-content:deploy', "Static content deploy — resource-intensive operation"),
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

    # Only check commands that look like Magento CLI
    if "magento" not in command.lower() and "bin/magento" not in command:
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
            f"Magento CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
