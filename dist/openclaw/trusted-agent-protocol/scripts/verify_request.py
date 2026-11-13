"""Offline TAP merchant fixture verifier. No key retrieval or payment submission.

See audit/source-baseline.md for the supported profile and binding limitations.
"""
import argparse
import base64
from contextlib import closing
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlsplit

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from http_message_signatures import HTTPMessageVerifier, HTTPSignatureKeyResolver, algorithms
from requests import Request

MAX_CAPTURE = 131072
MAX_AGE = 480


class VisaEd25519(algorithms.ED25519):
    # Visa's merchant examples use this spelling. Crypto stays in the library.
    algorithm_id = "Ed25519"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def load_json(raw):
    if len(raw) > MAX_CAPTURE:
        raise ValueError("capture too large")
    try:
        return json.loads(raw, object_pairs_hook=unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid JSON encoding/depth") from exc


class LocalKeys(HTTPSignatureKeyResolver):
    def __init__(self, entries, now):
        self.entries = entries
        self.now = now

    def entry(self, key_id):
        entry = self.entries.get(key_id)
        if not isinstance(entry, dict) or entry.get("revoked") is not False:
            raise ValueError("key absent or revoked")
        if not isinstance(entry.get("provider"), str) or not entry["provider"]:
            raise ValueError("provider trust identity missing")
        if not (type(entry.get("not_before")) is int and type(entry.get("expires")) is int and
                entry["not_before"] <= self.now < entry["expires"]):
            raise ValueError("key outside trust validity window")
        return entry

    def resolve_public_key(self, key_id):
        entry = self.entry(key_id)
        key = serialization.load_pem_public_key(entry["public_key_pem"].encode())
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError("profile requires an Ed25519 key")
        return key


class ReplayStore:
    """Atomic single-host replay store. Share the file across local workers."""
    def __init__(self, path):
        self.path = str(path)
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS replay (provider TEXT, nonce_hash TEXT, expires INTEGER, PRIMARY KEY(provider, nonce_hash))")

    def consume(self, provider, nonce, expires, now):
        digest = hashlib.sha256(nonce.encode()).hexdigest()
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM replay WHERE expires <= ?", (now,))
            try:
                db.execute("INSERT INTO replay VALUES (?, ?, ?)", (provider, digest, expires))
            except sqlite3.IntegrityError as exc:
                raise ValueError("replayed nonce") from exc


def ordered_binding_bytes(obj):
    """Agreed fixture serialization, not a universal Visa container encoding."""
    return json.dumps({k: v for k, v in obj.items() if k != "signature"},
                      ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def verify_binding(obj, key, key_id, nonce, consumer=False):
    if not isinstance(obj, dict) or obj.get("kid") != key_id or obj.get("nonce") != nonce:
        raise ValueError("container key/nonce binding mismatch")
    if obj.get("alg") != "Ed25519":
        raise ValueError("unsupported container algorithm")
    if consumer and ("idToken" not in obj or not isinstance(obj.get("contextualData"), dict)):
        raise ValueError("consumer recognition fields missing")
    if not consumer and not any(k not in ("nonce", "kid", "alg", "signature") for k in obj):
        raise ValueError("payment container has no payload")
    signature = obj.get("signature")
    if not isinstance(signature, str) or len(signature) > 128:
        raise ValueError("invalid container signature")
    key.verify(base64.b64decode(signature, validate=True), ordered_binding_bytes(obj))


def verify_capture(capture, trust, replay, *, profile="merchant-strict", tag="agent-browser-auth"):
    """Return verified facts only; caller still makes every authorization decision."""
    if profile not in ("merchant-strict", "tap-minimum") or tag not in ("agent-browser-auth", "agent-payer-auth"):
        raise ValueError("unsupported profile or intent tag")
    now = int(time.time())
    if not isinstance(capture, dict) or not isinstance(trust, dict):
        raise ValueError("capture and trust must be objects")
    url = capture.get("url", "")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("capture needs an absolute HTTPS URL without userinfo/fragment")
    if parsed.netloc not in trust.get("authorities", []):
        raise ValueError("authority outside merchant trust configuration")
    headers = capture.get("headers")
    if not isinstance(headers, dict) or len(headers) > 64:
        raise ValueError("invalid headers")
    normalized = {}
    for name, value in headers.items():
        if not isinstance(value, str) or len(value) > 16384 or any(c in name + value for c in "\r\n") or name.lower() in normalized:
            raise ValueError("invalid/duplicate header")
        normalized[name.lower()] = value
    # Signature canonicalization must use the configured external URL. Never
    # derive it from an untrusted Forwarded or X-Forwarded-* header.
    if "host" in normalized and normalized["host"] != parsed.netloc:
        raise ValueError("Host disagrees with configured URL")
    body = base64.b64decode(capture.get("body_base64", ""), validate=True)
    if len(body) > MAX_CAPTURE:
        raise ValueError("body exceeds fixture limit")
    method = capture.get("method")
    if method not in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
        raise ValueError("invalid method")
    request = Request(method, url, headers=normalized, data=body).prepare()
    if request.url != url:
        raise ValueError("capture URL must already be normalized; do not rewrite signed bytes")
    resolver = LocalKeys(trust.get("keys", {}), now)
    verifier = HTTPMessageVerifier(signature_algorithm=VisaEd25519, key_resolver=resolver)
    required = ("@authority", "@path")
    if profile == "merchant-strict":
        required += ("@method", "@target-uri")
    verified = verifier.verify(request, max_age=timedelta(seconds=MAX_AGE), expect_tag=tag,
                               require_components=required, body=body if profile == "merchant-strict" else None)
    if len(verified) != 1:
        raise ValueError("fixture profile requires exactly one matching signature")
    result = verified[0]
    params = result.parameters
    for field in ("created", "expires", "keyid", "alg", "tag", "nonce"):
        if field not in params:
            raise ValueError("missing signature parameter: " + field)
    created, expires, nonce = params["created"], params["expires"], params["nonce"]
    if type(created) is not int or type(expires) is not int or not created <= now < expires or not 0 < expires - created <= MAX_AGE:
        raise ValueError("signature outside the eight-minute validity window")
    if not isinstance(nonce, str) or not 1 <= len(nonce) <= 256:
        raise ValueError("invalid nonce")
    entry = resolver.entry(params["keyid"])
    bindings = {}
    if body:
        obj = load_json(body)
        if not isinstance(obj, dict):
            raise ValueError("fixture JSON body must be an object")
        for name in ("agenticConsumer", "agenticPaymentContainer"):
            if name in obj:
                if trust.get("binding_profile") != "ordered-json-ed25519-fixture-v1":
                    raise ValueError("container serialization profile not explicitly configured")
                verify_binding(obj[name], resolver.resolve_public_key(params["keyid"]),
                               params["keyid"], nonce, consumer=name == "agenticConsumer")
                bindings[name] = "signature-and-binding-verified"
    # Consume only after every supplied signature/binding check succeeds.
    replay.consume(entry["provider"], nonce, expires, now)
    return {"signature_valid": True, "provider_trusted": True, "provider": entry["provider"],
            "profile": profile, "tag": tag, "bindings": bindings,
            "body_integrity_verified": result.body is not None,
            "identity_token_verified": False, "authorized": False,
            "verified_components": list(result.covered_components)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", type=Path)
    ap.add_argument("trust", type=Path)
    ap.add_argument("--replay-db", required=True, type=Path)
    ap.add_argument("--profile", choices=("merchant-strict", "tap-minimum"), default="merchant-strict")
    ap.add_argument("--tag", choices=("agent-browser-auth", "agent-payer-auth"), default="agent-browser-auth")
    args = ap.parse_args()
    try:
        def read(path):
            with path.open("rb") as stream:
                return load_json(stream.read(MAX_CAPTURE + 1))
        result = verify_capture(read(args.capture), read(args.trust), ReplayStore(args.replay_db),
                                profile=args.profile, tag=args.tag)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        # Do not print library exception text: it can include signed headers.
        print(json.dumps({"signature_valid": False, "authorized": False,
                          "error_type": type(exc).__name__, "error": "verification rejected"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
