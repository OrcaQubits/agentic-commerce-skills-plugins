"""Async advisory hook; stdlib only, no secret values in output."""
import json
import re
import sys

PATTERNS = (
    r"-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----",
    r"(?:private[_-]?key|wallet[_-]?secret|api[_-]?key)\s*[:=]\s*[\"'][a-zA-Z0-9_+/.=-]{24,}[\"']",
    r"\b(?:sk_live_|rk_live_|whsec_)[A-Za-z0-9]{20,}",
)

def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, EOFError):
        return
    if not isinstance(data, dict):
        return
    inputs = data.get("tool_input")
    if not isinstance(inputs, dict):
        return
    name = data.get("tool_name")
    content = inputs.get("content", "") if name == "write_file" else inputs.get("new_string", "") if name == "edit_file" else ""
    if isinstance(content, str) and any(re.search(p, content, re.I) for p in PATTERNS):
        json.dump({"systemMessage": "Possible embedded signing/payment secret detected. Replace it with a secret-manager reference; never include secret values in reports."}, sys.stdout)

if __name__ == "__main__":
    main()
