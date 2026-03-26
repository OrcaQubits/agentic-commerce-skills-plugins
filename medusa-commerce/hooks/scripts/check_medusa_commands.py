#!/usr/bin/env python3
"""PreToolUse hook: block potentially destructive Medusa CLI commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'medusa\s+db:rollback', "Database rollback — can cause data loss"),
    (r'medusa\s+db:migrate\s+.*--force', "Forced database migration — bypasses safety checks"),
    (r'rm\s+(-rf?|.*-r)\s+.*\.medusa', "Remove .medusa directory — destroys server data"),
    (r'DROP\s+(TABLE|DATABASE)', "SQL DROP statement — permanent data loss"),
    (r'TRUNCATE\s+TABLE', "SQL TRUNCATE statement — deletes all table data"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'medusa\s+db:migrate', "Database migration — will modify database schema"),
    (r'medusa\s+build', "Production build — creates optimized build output"),
    (r'medusa\s+start', "Start production server — not for development use"),
    (r'npx\s+medusa\s+db:migrate', "Database migration via npx — will modify database schema"),
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

    # Only check commands that look like Medusa CLI or database operations
    if "medusa" not in command.lower() and "drop " not in command.lower() and "truncate " not in command.lower():
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
            f"Medusa CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
