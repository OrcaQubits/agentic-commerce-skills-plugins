#!/usr/bin/env python3
"""
R6 — Trust surface.

Agents transact only where identity and integrity are verifiable. Probes
the trust primitives the agentic commerce stack expects:

  OAuth      /.well-known/oauth-authorization-server discovery
  Signing    webhook signing keys published in the UCP profile
  Transport  HTTPS enforced (http:// redirects to https://), HSTS
  Errors     a structured JSON error shape on a bad request

Usage:
    python probe_trust.py https://shop.example.com [--json]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import fetch, get_json, check, evidence, run_cli


def probe(origin, host, deep=False):
    checks = []

    # --- OAuth discovery --------------------------------------------------
    oauth = get_json(origin + "/.well-known/oauth-authorization-server")
    o = oauth["json"] if isinstance(oauth["json"], dict) else {}
    oauth_ok = oauth["status"] == 200 and bool(
        o.get("issuer") and (o.get("authorization_endpoint") or o.get("token_endpoint")))
    checks.append(check(
        "OAuth authorization-server discovery",
        oauth_ok, 2, evidence(oauth),
        fix_skill="ucp-agentic-commerce:ucp-identity-linking",
    ))

    # --- signing keys in UCP profile ---------------------------------------
    ucp = get_json(origin + "/.well-known/ucp")
    if ucp["status"] != 200 or ucp["json"] is None:
        ucp = get_json(origin + "/.well-known/ucp.json")
    inner = (ucp["json"] or {}).get("ucp", ucp["json"]) if isinstance(ucp["json"], dict) else {}
    blob = json.dumps(inner).lower() if inner else ""
    keys_ok = any(k in blob for k in ('"signing_keys"', '"jwks"', '"keys"', '"public_key"'))
    checks.append(check(
        "webhook signing keys published in UCP profile",
        keys_ok, 2,
        "profile mentions signing_keys/jwks/keys: {}".format(keys_ok),
        fix_skill="ucp-agentic-commerce:ucp-orders-webhooks",
    ))

    # --- HTTPS enforced -----------------------------------------------------
    plain = fetch("http://" + host + "/", follow_redirects=False)
    https_ok = (plain["status"] in (301, 302, 307, 308)
                and plain["headers"].get("location", "").startswith("https://")) \
        or plain["url"].startswith("https://")
    checks.append(check(
        "http:// redirects to https://", https_ok, 1, evidence(plain)))

    home = fetch(origin + "/")
    hsts = "strict-transport-security" in home["headers"]
    checks.append(check(
        "HSTS header on origin", hsts, 1,
        "strict-transport-security: {!r}".format(
            home["headers"].get("strict-transport-security", "absent"))))

    # --- structured error shape ---------------------------------------------
    bad = fetch(origin + "/checkout_sessions", method="POST", body="{not json",
                headers={"Content-Type": "application/json"})
    d = {}
    try:
        d = json.loads(bad["body"]) if bad["body"] else {}
    except ValueError:
        pass
    err_ok = bad["status"] in (400, 401, 415, 422) and isinstance(d, dict) \
        and bool(d.get("type") or d.get("error") or d.get("message"))
    checks.append(check(
        "malformed request gets a structured JSON error (not an HTML 500)",
        err_ok, 1, evidence(bad),
        fix_skill="acp-agentic-commerce:acp-dev-patterns",
    ))

    return {
        "probe": "trust", "id": "r6", "module": "Trustworthy",
        "origin": origin, "impact": 4, "complexity": 3,
        "na_condition": None,
        "checks": checks,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
