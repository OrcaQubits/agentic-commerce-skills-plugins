"""Bounded payment surface inspection, not authentication or settlement.

Canonical copy; scripts/sync_payment_parser.py copies this into readiness.
Spec revisions and intentionally unsupported cases: audit/source-baseline.md.
"""
import base64
import binascii
import json
import re
from urllib.parse import urlsplit

LIMIT = 16384
TOKEN = r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
PARAM = re.compile(r'^(' + TOKEN + r')\s*=\s*("(?:[^"\\\r\n]|\\[\x20-\x7e])*"|' + TOKEN + r')$')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def read_json(value):
    if not isinstance(value, (str, bytes)) or len(value) > LIMIT:
        raise ValueError("JSON exceeds inspection limit")
    try:
        return json.loads(value, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite number")))
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid JSON encoding or depth") from exc


def decode_json(value, urlsafe=False):
    if not isinstance(value, str) or not value or len(value) > LIMIT:
        raise ValueError("invalid encoded size")
    pattern = r"[A-Za-z0-9_-]+" if urlsafe else r"[A-Za-z0-9+/]+={0,2}"
    if not re.fullmatch(pattern, value):
        raise ValueError("invalid base64 alphabet")
    try:
        wire = value + "=" * (-len(value) % 4) if urlsafe else value
        raw = base64.b64decode(wire, altchars=b"-_" if urlsafe else None, validate=True)
        return read_json(raw)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("invalid encoded JSON") from exc


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_x402(doc):
    """Validate the v2 core envelope; scheme and extension semantics are separate."""
    if not isinstance(doc, dict):
        raise ValueError("challenge must be an object")
    if type(doc.get("x402Version")) is not int or doc["x402Version"] != 2:
        raise ValueError("unsupported x402 version")
    resource = doc.get("resource")
    if not isinstance(resource, dict) or not nonempty(resource.get("url")):
        raise ValueError("resource.url is required")
    for key in ("description", "mimeType"):
        if key in resource and not isinstance(resource[key], str):
            raise ValueError("invalid resource " + key)
    def short_ascii(s):
        return isinstance(s, str) and len(s) <= 32 and all(32 <= ord(c) <= 126 for c in s)
    if "serviceName" in resource and not short_ascii(resource["serviceName"]):
        raise ValueError("invalid serviceName")
    if "tags" in resource and (not isinstance(resource["tags"], list) or
                              len(resource["tags"]) > 5 or not all(map(short_ascii, resource["tags"]))):
        raise ValueError("invalid resource tags")
    if "iconUrl" in resource:
        icon = resource["iconUrl"]
        if not isinstance(icon, str) or len(icon) > 2048 or urlsplit(icon).scheme not in ("https", "http") or not urlsplit(icon).netloc:
            raise ValueError("invalid iconUrl")
    if "error" in doc and not isinstance(doc["error"], str):
        raise ValueError("invalid error")
    accepts = doc.get("accepts")
    if not isinstance(accepts, list) or not 1 <= len(accepts) <= 32:
        raise ValueError("accepts must contain 1..32 alternatives")
    for requirement in accepts:
        if not isinstance(requirement, dict):
            raise ValueError("invalid payment requirement")
        for key in ("scheme", "network", "asset", "payTo"):
            if not nonempty(requirement.get(key)):
                raise ValueError("missing " + key)
        if not re.fullmatch(r"[-a-z0-9]{3,8}:[-_a-zA-Z0-9]{1,32}", requirement["network"]):
            raise ValueError("invalid CAIP-2 network")
        if not isinstance(requirement.get("amount"), str) or not re.fullmatch(r"[0-9]{1,78}", requirement["amount"]):
            raise ValueError("amount must be an unsigned atomic-unit integer string")
        timeout = requirement.get("maxTimeoutSeconds")
        if type(timeout) is not int or timeout <= 0:
            raise ValueError("invalid maxTimeoutSeconds")
        if "extra" in requirement and not isinstance(requirement["extra"], dict):
            raise ValueError("invalid extra")
    extensions = doc.get("extensions", {})
    if not isinstance(extensions, dict):
        raise ValueError("invalid extensions")
    for extension in extensions.values():
        if not isinstance(extension, dict) or not isinstance(extension.get("info"), dict) or not isinstance(extension.get("schema"), dict):
            raise ValueError("extension must contain info and schema objects")
    return doc


def auth_challenges(header):
    """Split RFC 9110 challenge lists without splitting commas inside quotes."""
    if not isinstance(header, str) or len(header) > LIMIT or any(c in header for c in "\r\n"):
        raise ValueError("invalid authentication header")
    parts, start, quoted, escaped = [], 0, False, False
    for index, char in enumerate(header):
        if escaped:
            escaped = False
        elif quoted and char == "\\":
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif char == "," and not quoted:
            parts.append(header[start:index].strip())
            start = index + 1
    if quoted or escaped:
        raise ValueError("unterminated authentication quote")
    parts.append(header[start:].strip())
    groups = []
    for part in parts:
        if PARAM.fullmatch(part) and groups:
            groups[-1][1].append(part)
        else:
            found = re.fullmatch(r"(" + TOKEN + r")(?:\s+(.*))?", part)
            if not found:
                raise ValueError("invalid authentication syntax")
            groups.append((found[1].lower(), [found[2]] if found[2] else []))
    return groups


def validate_mpp(parts):
    params = {}
    for part in parts:
        match = PARAM.fullmatch(part)
        if not match or match[1].lower() in params:
            raise ValueError("invalid or duplicate Payment parameter")
        key, val = match[1].lower(), match[2]
        params[key] = re.sub(r"\\(.)", r"\1", val[1:-1]) if val.startswith('"') else val
    for key in ("id", "realm", "method", "intent", "request"):
        if not nonempty(params.get(key)):
            raise ValueError("missing Payment " + key)
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", params["method"]):
        raise ValueError("invalid Payment method")
    if params["intent"] not in ("charge", "session", "subscription"):
        raise ValueError("unsupported Payment intent")
    if not isinstance(decode_json(params["request"], urlsafe=True), dict):
        raise ValueError("Payment request must be an object")
    return params


def classify_response(status, headers, body=""):
    """Return only bounded diagnostic metadata; never expose credentials."""
    if status != 402:
        return []
    normalized = {}
    for key, value in headers.items():
        name = key.lower()
        if name in normalized:
            return [{"protocol": "unknown", "status": "malformed", "detail": "duplicate header names"}]
        normalized[name] = value
    results = []
    if "payment-required" in normalized:
        try:
            doc = decode_json(normalized["payment-required"])
            if isinstance(doc, dict) and type(doc.get("x402Version")) is int and doc["x402Version"] != 2:
                results.append({"protocol": "x402", "version": doc["x402Version"], "status": "unsupported", "detail": "unsupported version"})
            else:
                validate_x402(doc)
                results.append({"protocol": "x402", "version": 2, "status": "valid", "detail": "v2 core envelope; scheme/settlement unverified"})
        except ValueError as exc:
            results.append({"protocol": "x402", "status": "malformed", "detail": str(exc)})
    www = normalized.get("www-authenticate", "")
    if www:
        try:
            for scheme, parts in auth_challenges(www):
                if scheme == "payment":
                    try:
                        validate_mpp(parts)
                        results.append({"protocol": "mpp", "status": "valid", "detail": "Payment envelope; method/JCS/binding unverified"})
                    except ValueError as exc:
                        results.append({"protocol": "mpp", "status": "malformed", "detail": str(exc)})
        except ValueError as exc:
            results.append({"protocol": "unknown", "status": "malformed", "detail": str(exc)})
    if not results:
        try:
            legacy = read_json(body)
            if isinstance(legacy, dict) and legacy.get("x402Version") == 1:
                results.append({"protocol": "x402", "version": 1, "status": "unsupported", "detail": "legacy body transport; migrate explicitly"})
        except ValueError:
            pass
    return results or [{"protocol": "unknown", "status": "unrecognized", "detail": "402 alone is not protocol evidence"}]
