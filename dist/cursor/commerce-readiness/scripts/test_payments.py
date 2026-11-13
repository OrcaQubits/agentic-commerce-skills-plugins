"""Payment probe regressions using mocked network responses."""
import base64
import json
import unittest
from unittest.mock import patch
import probe_payments


DOC = {"x402Version": 2, "resource": {"url": "https://shop.example/paid"},
       "accepts": [{"scheme": "exact", "network": "eip155:84532", "amount": "1000",
                    "asset": "USDC", "payTo": "merchant", "maxTimeoutSeconds": 60}]}


def response(status=404, headers=None, body=""):
    return {"status": status, "headers": headers or {}, "body": body, "json": None,
            "error": None, "url": "https://shop.example", "elapsed_ms": 1}


class PaymentProbe(unittest.TestCase):
    def run_probe(self, paid):
        calls = []
        def fetch(url, **kwargs):
            calls.append((url, kwargs.get("method", "GET")))
            return paid.get(url.rsplit("/", 1)[-1], response())
        with patch.object(probe_payments, "fetch", side_effect=fetch), \
             patch.object(probe_payments, "get_json", return_value=response()), \
             patch.object(probe_payments, "catchall_baseline", return_value=response()), \
             patch.object(probe_payments, "distinct_surface", return_value=False):
            result = probe_payments.probe("https://shop.example", "shop.example")
        self.assertTrue(all(method in ("GET", "OPTIONS") for _, method in calls))
        self.assertEqual(sum(c["weight"] for c in result["checks"]), 6)
        return result

    def test_unknown_402(self):
        result = self.run_probe({"paid": response(402, body="payment needed")})
        self.assertFalse(result["checks"][-1]["pass"])
        self.assertEqual(result["checks"][-1]["fix_skill"], "commerce-readiness:readiness-fix-plan")

    def test_scan_continues_and_records_version(self):
        header = base64.b64encode(json.dumps(DOC).encode()).decode()
        result = self.run_probe({"paid": response(402, body="<html>pay</html>"),
                                 "x402": response(402, {"PAYMENT-REQUIRED": header})})
        row = result["checks"][-1]
        self.assertTrue(row["pass"])
        self.assertEqual(row["weight"], 1)
        self.assertEqual(row["fix_skill"], "x402-agentic-payments:x402-http-payments")
        self.assertIn("sampled paths only", row["evidence"])
        self.assertTrue(any(o.get("version") == 2 for o in result["payment_challenges"]))

    def test_legacy_not_counted(self):
        result = self.run_probe({"x402": response(402, body='{"x402Version":1}')})
        self.assertFalse(result["checks"][-1]["pass"])


if __name__ == "__main__":
    unittest.main()
