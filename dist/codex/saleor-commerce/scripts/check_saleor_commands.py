#!/usr/bin/env python3
"""PreToolUse hook: block potentially destructive Saleor / Django commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'python\s+manage\.py\s+flush', "Database flush — wipes all data"),
    (r'python\s+manage\.py\s+reset_db', "Database reset — drops and recreates database"),
    (r'python\s+manage\.py\s+migrate\s+.*--fake', "Fake migration — corrupts migration state"),
    (r'DROP\s+(TABLE|DATABASE)', "SQL DROP statement — permanent data loss"),
    (r'TRUNCATE\s+TABLE', "SQL TRUNCATE statement — deletes all table data"),
    (r'rm\s+(-rf?|.*-r)\s+.*(saleor|media)', "Remove Saleor/media directories — data loss"),
    (r'docker[-\s]compose\s+.*down\s+.*-v', "Docker volumes removal — destroys persistent data"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'python\s+manage\.py\s+migrate', "Database migration — will modify database schema"),
    (r'python\s+manage\.py\s+createsuperuser', "Creates admin superuser"),
    (r'docker[-\s]compose\s+.*up', "Starting Docker services"),
    (r'saleor\s+deploy', "Deployment action — affects production"),
    (r'celery\s+.*purge', "Purging Celery task queue"),
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

    # Only check commands that look like Saleor/Django/database operations
    lower = command.lower()
    if not any(kw in lower for kw in ("manage.py", "saleor", "drop ", "truncate ", "celery", "docker")):
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
            f"Saleor CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
