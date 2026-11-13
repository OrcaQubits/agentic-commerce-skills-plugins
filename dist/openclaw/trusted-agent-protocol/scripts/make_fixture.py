"""Create a synthetic signed capture and public trust file; private key stays in memory."""
import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from http_message_signatures import HTTPMessageSigner, HTTPSignatureKeyResolver
from requests import Request
from verify_request import VisaEd25519, ordered_binding_bytes


class SigningKey(HTTPSignatureKeyResolver):
    def __init__(self, key):
        self.key = key

    def resolve_private_key(self, key_id):
        return self.key


def make_fixture(*, key=None, key_id="fixture-key", nonce=None, created=None,
                 expires=None, bindings=False, components=None, tag="agent-browser-auth"):
    key = key or Ed25519PrivateKey.generate()
    now = int(time.time())
    created = now - 1 if created is None else created
    expires = now + 120 if expires is None else expires
    nonce = nonce or secrets.token_urlsafe(32)
    obj = {}
    if bindings:
        obj = {"agenticConsumer": {"nonce": nonce, "idToken": "synthetic-not-a-jwt",
                                   "contextualData": {}, "kid": key_id, "alg": "Ed25519"},
               "agenticPaymentContainer": {"nonce": nonce, "fixtureReference": "no-payment-credentials",
                                            "kid": key_id, "alg": "Ed25519"}}
        for value in obj.values():
            value["signature"] = base64.b64encode(key.sign(ordered_binding_bytes(value))).decode()
    body = json.dumps(obj, separators=(",", ":")).encode() if bindings else b""
    request = Request("POST" if bindings else "GET", "https://merchant.example/checkout",
                      headers={"Content-Type": "application/json"}, data=body).prepare()
    signer = HTTPMessageSigner(signature_algorithm=VisaEd25519, key_resolver=SigningKey(key))
    signer.sign(request, key_id=key_id, created=datetime.fromtimestamp(created, timezone.utc),
                expires=datetime.fromtimestamp(expires, timezone.utc), nonce=nonce, tag=tag,
                covered_component_ids=components or ("@authority", "@path", "@method", "@target-uri"),
                body=body)
    capture = {"method": request.method, "url": request.url, "headers": dict(request.headers),
               "body_base64": base64.b64encode(body).decode()}
    trust = {"authorities": ["merchant.example"], "binding_profile": "ordered-json-ed25519-fixture-v1",
             "keys": {key_id: {"provider": "synthetic-provider", "revoked": False,
                                "not_before": now - 3600, "expires": now + 3600,
                                "public_key_pem": key.public_key().public_bytes(
                                    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()}}}
    return capture, trust


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", type=Path)
    ap.add_argument("--bindings", action="store_true")
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    capture, trust = make_fixture(bindings=args.bindings)
    for name, value in (("capture.json", capture), ("trust.json", trust)):
        # Refuse to replace an existing capture or trust configuration.
        with (args.output / name).open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
    print("Created expiring synthetic capture and public trust configuration")
