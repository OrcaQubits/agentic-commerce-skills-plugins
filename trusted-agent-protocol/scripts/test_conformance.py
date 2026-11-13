"""Real signature and merchant-policy regressions with synthetic in-memory keys."""
import base64
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from http_message_signatures import HTTPMessageSigner
from requests import Request
from datetime import datetime, timezone
from make_fixture import make_fixture, SigningKey
from verify_request import ReplayStore, VisaEd25519, load_json, verify_capture


class Conformance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = ReplayStore(Path(self.temp.name) / "replay.db")

    def verify(self, capture, trust, **kw):
        return verify_capture(capture, trust, self.store, **kw)

    def test_positive_and_replay(self):
        capture, trust = make_fixture()
        result = self.verify(capture, trust)
        self.assertTrue(result["signature_valid"])
        self.assertFalse(result["authorized"])
        with self.assertRaisesRegex(ValueError, "replayed"):
            self.verify(capture, trust)

    def test_tampering(self):
        for field, value in (("method", "DELETE"), ("url", "https://merchant.example/different"),
                             ("url", "https://merchant.example/checkout?q=changed"),
                             ("url", "https://evil.example/checkout")):
            capture, trust = make_fixture()
            capture[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(Exception):
                self.verify(capture, trust)
        capture, trust = make_fixture(bindings=True)
        capture["body_base64"] = base64.b64encode(b'{"modified":true}').decode()
        with self.assertRaises(Exception):
            self.verify(capture, trust)

    def test_time_and_required_parameters(self):
        now = int(time.time())
        for created, expires in ((now-200, now-1), (now+30, now+60), (now-1, now+481)):
            capture, trust = make_fixture(created=created, expires=expires)
            with self.subTest(created=created, expires=expires), self.assertRaises(Exception):
                self.verify(capture, trust)
        capture, trust = make_fixture()
        capture["headers"]["Signature-Input"] = capture["headers"]["Signature-Input"].replace(';alg="Ed25519"', "")
        with self.assertRaises(Exception):
            self.verify(capture, trust)

    def test_trust_rejection(self):
        for change in ({"revoked": True}, {"expires": 0}, {"provider": ""},
                       {"public_key_pem": "invalid"}):
            capture, trust = make_fixture()
            trust["keys"]["fixture-key"].update(change)
            with self.subTest(change=change), self.assertRaises(Exception):
                self.verify(capture, trust)
        capture, trust = make_fixture(key_id="https://untrusted.example/key")
        trust["keys"] = {}
        with self.assertRaises(Exception):
            self.verify(capture, trust)  # No network lookup exists.

    def test_wrong_key_algorithm_and_intent(self):
        capture, trust = make_fixture()
        _, other = make_fixture()
        trust["keys"] = other["keys"]
        with self.assertRaises(Exception):
            self.verify(capture, trust)
        capture, trust = make_fixture()
        capture["headers"]["Signature-Input"] = capture["headers"]["Signature-Input"].replace('alg="Ed25519"', 'alg="hmac-sha256"')
        with self.assertRaises(Exception):
            self.verify(capture, trust)
        capture, trust = make_fixture(tag="agent-payer-auth")
        with self.assertRaises(Exception):
            self.verify(capture, trust)
        self.assertTrue(self.verify(capture, trust, tag="agent-payer-auth")["signature_valid"])

    def test_minimum_does_not_claim_method_or_query_integrity(self):
        capture, trust = make_fixture(components=("@authority", "@path"))
        with self.assertRaises(Exception):
            self.verify(capture, trust)
        capture["method"] = "HEAD"
        result = self.verify(capture, trust, profile="tap-minimum")
        self.assertNotIn('"@method"', result["verified_components"])
        self.assertFalse(result["body_integrity_verified"])

    def test_bindings(self):
        capture, trust = make_fixture(bindings=True)
        result = self.verify(capture, trust)
        self.assertEqual(len(result["bindings"]), 2)
        self.assertFalse(result["identity_token_verified"])
        capture, trust = make_fixture(bindings=True)
        trust.pop("binding_profile")
        with self.assertRaisesRegex(ValueError, "serialization"):
            self.verify(capture, trust)

    def test_binding_mismatch_with_valid_outer_signature(self):
        # Re-sign the outer request after corrupting a container: failures must
        # come from container verification, not just Content-Digest mismatch.
        for field, value in (("nonce", "other-nonce"), ("kid", "other-key"),
                             ("fixtureReference", "tampered"), ("alg", "PS256")):
            key = Ed25519PrivateKey.generate()
            capture, trust = make_fixture(key=key, bindings=True)
            body = json.loads(base64.b64decode(capture["body_base64"]))
            body["agenticPaymentContainer"][field] = value
            body_bytes = json.dumps(body, separators=(",", ":")).encode()
            request = Request(capture["method"], capture["url"], data=body_bytes).prepare()
            nonce = body["agenticConsumer"]["nonce"]
            now = int(time.time())
            HTTPMessageSigner(signature_algorithm=VisaEd25519, key_resolver=SigningKey(key)).sign(
                request, key_id="fixture-key", nonce=nonce, tag="agent-browser-auth",
                created=datetime.fromtimestamp(now-1, timezone.utc), expires=datetime.fromtimestamp(now+100, timezone.utc),
                covered_component_ids=("@authority", "@path", "@method", "@target-uri"), body=body_bytes)
            capture.update(headers=dict(request.headers), body_base64=base64.b64encode(body_bytes).decode())
            with self.subTest(field=field), self.assertRaises(Exception):
                self.verify(capture, trust)

    def test_concurrent_replay_and_key_rotation(self):
        capture, trust = make_fixture(nonce="same-session")
        def attempt(_):
            try:
                self.verify(copy.deepcopy(capture), trust)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=6) as pool:
            self.assertEqual(sum(pool.map(attempt, range(6))), 1)
        rotated, rotated_trust = make_fixture(key_id="rotated", nonce="same-session")
        with self.assertRaisesRegex(ValueError, "replayed"):
            self.verify(rotated, rotated_trust)
        fresh, fresh_trust = make_fixture(key_id="rotated")
        self.assertTrue(self.verify(fresh, fresh_trust)["signature_valid"])

    def test_ambiguous_input_and_proxy_host(self):
        with self.assertRaises(ValueError):
            load_json('{"nonce":"a","nonce":"b"}')
        capture, trust = make_fixture()
        capture["headers"]["Host"] = "evil.example"
        with self.assertRaisesRegex(ValueError, "Host"):
            self.verify(capture, trust)
        capture, trust = make_fixture()
        capture["headers"]["signature-input"] = capture["headers"]["Signature-Input"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.verify(capture, trust)


if __name__ == "__main__":
    unittest.main()
