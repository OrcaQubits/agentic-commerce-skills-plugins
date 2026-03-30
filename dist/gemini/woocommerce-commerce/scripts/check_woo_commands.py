#!/usr/bin/env python3
"""BeforeTool hook: block potentially destructive WordPress/WooCommerce CLI commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'wp\s+db\s+reset', "Database reset — causes complete data loss"),
    (r'wp\s+db\s+drop', "Database drop — causes complete data loss"),
    (r'wp\s+site\s+empty', "Site empty — deletes all content"),
    (r'wp\s+plugin\s+uninstall\s+woocommerce', "WooCommerce uninstall — removes all WC data"),
    (r'wp\s+plugin\s+delete\s+woocommerce', "WooCommerce deletion — removes plugin files"),
    (r'wp\s+wc\s+tool\s+reset', "WooCommerce tool reset — can cause data loss"),
    (r'wp\s+db\s+query\s+.*DROP\s+TABLE', "DROP TABLE — irreversible data loss"),
    (r'wp\s+db\s+query\s+.*TRUNCATE', "TRUNCATE TABLE — irreversible data loss"),
    (r'wp\s+option\s+delete\s+woocommerce', "Deleting WooCommerce options — may break store"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'wp\s+cache\s+flush', "Cache flush — may cause temporary performance degradation"),
    (r'wp\s+transient\s+delete\s+--all', "Delete all transients — may cause temporary slowdown"),
    (r'wp\s+wc\s+update', "WooCommerce database update — runs migrations"),
    (r'wp\s+plugin\s+update\s+woocommerce', "WooCommerce update — may require database migration"),
    (r'wp\s+plugin\s+deactivate\s+woocommerce', "WooCommerce deactivation — disables store"),
    (r'wp\s+rewrite\s+flush', "Permalink flush — may affect cached routes"),
    (r'wp\s+search-replace', "Search-replace — modifies database content"),
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

    # Only check commands that look like WP-CLI
    if "wp " not in command and "wp-cli" not in command.lower():
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
            f"WP-CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
