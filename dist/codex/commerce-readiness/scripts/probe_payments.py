#!/usr/bin/env python3
"""
R5 — Payment readiness.

An agent that can open a checkout but not pay is a window-shopper. Probes
the payment surfaces the agentic payment stack defines:

  Payment handlers  declared in the UCP profile
  ACP               delegate_payment surface
  MPP / x402        HTTP 402 with a structurally valid protocol challenge
  AP2               mandate support signalled in UCP profile extensions

Default mode is GET/OPTIONS-only; `--deep` sends the discovery-shaped
delegate_payment POST (intentionally incomplete body — the correct server
response is a validation error, never a real delegation).

Usage:
    python probe_payments.py https://shop.example.com [--deep] [--json]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import (fetch, get_json, check, evidence, run_cli,
                       catchall_baseline, distinct_surface)
from lib.payment_challenges import classify_response


def probe(origin, host, deep=False):
    checks = []

    ucp = get_json(origin + "/.well-known/ucp")
    if ucp["status"] != 200 or ucp["json"] is None:
        ucp = get_json(origin + "/.well-known/ucp.json")
    ucp_doc = ucp["json"] if isinstance(ucp["json"], dict) else {}
    inner = ucp_doc.get("ucp", ucp_doc)

    # --- payment handlers declared in UCP profile ------------------------
    handlers = inner.get("payment_handlers") or inner.get("paymentHandlers") or []
    blob = json.dumps(inner).lower() if inner else ""
    handler_signal = bool(handlers) or '"payment"' in blob or "payment_handler" in blob
    checks.append(check(
        "payment handlers declared in UCP profile",
        handler_signal, 2,
        "{} handler entries; profile mentions payment: {}".format(
            len(handlers) if isinstance(handlers, list) else "?", handler_signal),
        fix_skill="ucp-agentic-commerce:ucp-payment-handlers",
    ))

    # --- AP2 mandate support signalled -----------------------------------
    ap2_signal = "ap2" in blob or "mandate" in blob
    checks.append(check(
        "AP2 mandate support signalled in UCP profile",
        ap2_signal, 1,
        "profile mentions ap2/mandate: {}".format(ap2_signal),
        fix_skill="ap2-agentic-payments:ap2-setup",
    ))

    # --- ACP delegate_payment surface ------------------------------------
    acp = get_json(origin + "/.well-known/acp.json")
    acp_doc = acp["json"] if isinstance(acp["json"], dict) else {}
    acp_base = (acp_doc.get("api_base_url") or origin).rstrip("/")
    dp_path = acp_base + "/agentic_commerce/delegate_payment"

    if deep:
        dp = fetch(dp_path, method="POST",
                   body=json.dumps({"allowance": {"max_amount": {
                       "amount": "1.00", "currency": "USD"}}}),
                   headers={"Idempotency-Key": "readiness-audit-dp-001"})
        d = {}
        try:
            d = json.loads(dp["body"]) if dp["body"] else {}
        except ValueError:
            pass
        dp_ok = (dp["status"] in (200, 201)
                 and (d.get("object") in ("delegated_payment", "delegate_payment")
                      or "vault_token" in d or "allowance" in d)) \
            or (isinstance(d, dict) and bool(d.get("type")) and bool(d.get("message")))
    else:
        dp = fetch(dp_path, method="OPTIONS")
        dp_ok = distinct_surface(dp, catchall_baseline(acp_base))
    checks.append(check(
        "ACP delegate_payment surface answers",
        dp_ok, 2, evidence(dp),
        fix_skill="acp-agentic-commerce:acp-delegated-payment",
    ))

    # Observe only a bounded set of likely endpoints; never submit payment.
    payment_ok, payment_ev, protocols, observed = False, [], set(), []
    for path in ("/api/paid", "/api/premium", "/paid", "/x402", "/api"):
        r = fetch(origin + path)
        classifications = classify_response(r["status"], r["headers"], r["body"])
        for item in classifications:
            observed.append(dict(item, path=path))
            if item["status"] == "valid":
                payment_ok = True
            if item["protocol"] in ("mpp", "x402"):
                protocols.add(item["protocol"])
        payment_ev.append("{} {} {}".format(path, r["status"], ", ".join(
            "{} {} ({})".format(i["protocol"], i["status"], i["detail"]) for i in classifications)))
    fix = {"x402": "x402-agentic-payments:x402-http-payments",
           "mpp": "stripe-mpp:mpp-server-middleware"}
    checks.append(check(
        "HTTP 402 payment challenge surface (MPP or x402)",
        payment_ok, 1, "; ".join(payment_ev) + "; sampled paths only; payment execution unverified",
        fix_skill=fix[next(iter(protocols))] if len(protocols) == 1 else
                  "commerce-readiness:readiness-fix-plan",
    ))

    return {
        "probe": "payments", "id": "r5", "module": "Payable",
        "origin": origin, "impact": 4, "complexity": 4,
        "na_condition": "site does not transact (R4 fully N/A)",
        "deep": deep,
        "checks": checks,
        "payment_challenges": observed,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
