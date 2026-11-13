"""Offline wire and spending-policy regressions; no settlement or wallet access."""
import base64
import copy
import json
from pathlib import Path
import unittest
from payment_challenges import classify_response, validate_x402, read_json, LIMIT
from validate_challenge import choose_payment, validate_mcp

FIXTURE = json.loads((Path(__file__).parent / "fixtures/challenge.json").read_text())


def encode(doc):
    return base64.b64encode(json.dumps(doc).encode()).decode()


class Conformance(unittest.TestCase):
    def test_http(self):
        results = classify_response(402, {"PaYmEnT-ReQuIrEd": encode(FIXTURE)})
        self.assertEqual(results[0]["status"], "valid")
        self.assertEqual(classify_response(200, {"payment-required": encode(FIXTURE)}), [])

    def test_malformed(self):
        for value in ("!", "a" * (LIMIT + 1), encode([]), encode({}), encode({"x402Version": True})):
            with self.subTest(value=value[:20]):
                self.assertEqual(classify_response(402, {"payment-required": value})[0]["status"], "malformed")
        for key, value in (("amount", 1), ("amount", "-1"), ("amount", "1.2"), ("network", "base"),
                           ("maxTimeoutSeconds", True), ("maxTimeoutSeconds", 0), ("payTo", ""), ("extra", [])):
            doc = copy.deepcopy(FIXTURE)
            doc["accepts"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_x402(doc)
        for value in ([], None, [None]):
            doc = dict(FIXTURE, accepts=value)
            with self.assertRaises(ValueError):
                validate_x402(doc)

    def test_duplicate_json(self):
        with self.assertRaises(ValueError):
            read_json('{"x402Version":2,"x402Version":1}')
        with self.assertRaises(ValueError):
            read_json('{"amount":NaN}')

    def test_versions_and_unknown(self):
        for version in (1, 3):
            self.assertEqual(classify_response(402, {"payment-required": encode(dict(FIXTURE, x402Version=version))})[0]["status"], "unsupported")
        self.assertEqual(classify_response(402, {}, '{"x402Version":1}')[0]["status"], "unsupported")
        self.assertEqual(classify_response(402, {}, "<html>pay</html>")[0]["protocol"], "unknown")

    def test_mpp(self):
        request = base64.urlsafe_b64encode(b'{"amount":"1000"}').decode().rstrip("=")
        challenge = 'Payment id="fixture", realm="shop, example", method="tempo", intent="charge", request="' + request + '"'
        for header in (challenge, 'Basic realm="public", ' + challenge, challenge + ', Bearer realm="account"'):
            self.assertTrue(any(r["status"] == "valid" for r in classify_response(402, {"WWW-Authenticate": header})))
        for header in ("NotPayment realm=x", 'Basic realm="Payment"', challenge + ', id="duplicate"',
                       challenge.replace('id="fixture"', 'id=""'), challenge.replace(request, "="), 'Payment id="unterminated'):
            with self.subTest(header=header):
                self.assertFalse(any(r["status"] == "valid" for r in classify_response(402, {"www-authenticate": header})))
        mixed = classify_response(402, {"payment-required": encode(FIXTURE), "www-authenticate": challenge})
        self.assertEqual({r["protocol"] for r in mixed}, {"mpp", "x402"})

    def test_mcp(self):
        result = {"isError": True, "structuredContent": FIXTURE,
                  "content": [{"type": "text", "text": json.dumps(FIXTURE)}]}
        self.assertEqual(validate_mcp(result), FIXTURE)
        for change in ({"isError": False}, {"content": []}, {"content": [{"type": "text", "text": "{}"}]}):
            with self.assertRaises(ValueError):
                validate_mcp(dict(result, **change))

    def test_policy(self):
        policy = {k: FIXTURE["accepts"][0][k] for k in ("network", "asset", "payTo")}
        policy.update(resource=FIXTURE["resource"]["url"], max_amount="1000")
        self.assertEqual(choose_payment(FIXTURE, policy)["amount"], "1000")
        for key, value in (("resource", "https://evil.example"), ("max_amount", "999"), ("network", "eip155:1"),
                           ("asset", "other"), ("payTo", "other")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                choose_payment(FIXTURE, dict(policy, **{key: value}))
        unknown = copy.deepcopy(FIXTURE)
        unknown["accepts"][0]["scheme"] = "future-scheme"
        validate_x402(unknown)  # Wire validity is independent of executable support.
        with self.assertRaises(ValueError):
            choose_payment(unknown, policy)
        for extra in ({"paymentFlow": "upfront"}, {"assetTransferMethod": "future-method"}):
            unsupported = copy.deepcopy(FIXTURE)
            unsupported["accepts"][0]["extra"].update(extra)
            validate_x402(unsupported)
            with self.assertRaises(ValueError):
                choose_payment(unsupported, policy)


if __name__ == "__main__":
    unittest.main()
