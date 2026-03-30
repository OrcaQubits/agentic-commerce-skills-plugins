#!/usr/bin/env python3
"""PreToolUse hook: block potentially destructive Salesforce CLI commands."""
import json, sys, re

# Commands that can cause data loss or production outage
DESTRUCTIVE_PATTERNS = [
    (r'sfcc-ci\s+code:activate\s+.*(production|prod-|prd-)', "Activate code on production — can break live storefront"),
    (r'sfcc-ci\s+code:delete', "Code version deletion — permanent data loss"),
    (r'sfcc-ci\s+sandbox:delete', "Sandbox deletion — permanent data loss"),
    (r'sf\s+org\s+delete|sfdx\s+force:org:delete', "Org deletion — permanent data loss"),
    (r'sf\s+project\s+deploy\s+start\s+.*(production|--production)', "Deploy to production — can break live storefront"),
    (r'curl\s+.*-X\s+DELETE\s+.*(salesforce\.com|demandware\.net)', "DELETE request to Salesforce — potential data loss"),
]

# Commands that should only be run after confirmation
WARNING_PATTERNS = [
    (r'sfcc-ci\s+code:activate', "Code activation — will change running code version on instance"),
    (r'sfcc-ci\s+instance:upload', "Instance upload — will upload data to instance"),
    (r'sf\s+project\s+deploy\s+start', "Project deploy — will push metadata/code to org"),
    (r'sf\s+org\s+login', "Org login — will authenticate to a Salesforce org"),
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

    # Only check commands that look like Salesforce CLI or Salesforce API calls
    cmd_lower = command.lower()
    if not any(kw in cmd_lower for kw in ("sfcc", "salesforce", "demandware", "sfdx")):
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
            f"Salesforce CLI notice for '{command}': {'; '.join(warnings)}. "
            "Ensure this is intentional."
        )
        json.dump({"systemMessage": msg}, sys.stdout)


if __name__ == "__main__":
    main()
