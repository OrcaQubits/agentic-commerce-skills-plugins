#!/usr/bin/env python3
"""
R4 — Transactability.

Can an agent actually *do* commerce here — open a checkout, call a tool,
ask a question? Probes the transaction surfaces of the four families:

  ACP    POST {api_base_url}/checkout_sessions   (underscore)
  UCP    POST {rest endpoint}/checkout-sessions  (hyphen — yes, they differ)
  MCP    an advertised MCP endpoint answering JSON-RPC
  NLWeb  POST /ask

Default mode sends OPTIONS/GET only. `--deep` enables the POST probes —
they are discovery-shaped calls (demo SKU, no payment), but on a live
merchant a created session can still trigger inventory holds or
abandoned-cart emails, so it is opt-in.

Shape matters more than status: a stub that answers 200 with a
non-canonical body is NOT ready — agents parse fields, not vibes.

Usage:
    python probe_transact.py https://shop.example.com [--deep] [--json]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import (fetch, get_json, check, evidence, run_cli,
                       ucp_endpoints, surface_answers)

ACP_STATUSES = {"not_ready_for_payment", "ready_for_payment", "completed", "canceled"}
UCP_STATUSES = {"incomplete", "ready_for_complete", "completed", "canceled"}


def _discovery(origin):
    """Re-resolve the discovery docs (kept independent of probe_discovery)."""
    ucp = get_json(origin + "/.well-known/ucp")
    if ucp["status"] != 200 or ucp["json"] is None:
        ucp = get_json(origin + "/.well-known/ucp.json")
    acp = get_json(origin + "/.well-known/acp.json")
    if acp["status"] != 200 or acp["json"] is None:
        acp = get_json(origin + "/.well-known/agentic-commerce")
    ucp_doc = ucp["json"] if isinstance(ucp["json"], dict) else {}
    acp_doc = acp["json"] if isinstance(acp["json"], dict) else {}
    return ucp_doc.get("ucp", ucp_doc), acp_doc


def _acp_error_shaped(d):
    return isinstance(d, dict) and bool(d.get("type")) and bool(d.get("message"))


def probe(origin, host, deep=False):
    checks = []
    ucp_doc, acp_doc = _discovery(origin)

    # ---------------- ACP checkout ----------------
    acp_base = (acp_doc.get("api_base_url") or origin).rstrip("/")
    acp_versions = (acp_doc.get("protocol") or {}).get("supported_versions") \
        or [acp_doc.get("protocol", {}).get("version") or "2026-04-17"]
    acp_ver = acp_versions[0]

    opt = fetch(acp_base + "/checkout_sessions", method="OPTIONS")
    allow = (opt["headers"].get("allow", "") + " "
             + opt["headers"].get("access-control-allow-methods", "")).upper()
    # surface_answers guards against SPA catch-alls that 200-html every path
    acp_surface = "POST" in allow or (
        surface_answers(opt)
        and opt["status"] in (200, 204, 400, 401, 405, 415, 422))
    checks.append(check(
        "ACP /checkout_sessions surface answers (OPTIONS)",
        acp_surface, 1,
        "OPTIONS {} ct={} allow={!r}".format(
            opt["status"], opt["headers"].get("content-type", "-").split(";")[0],
            allow.strip() or "-"),
        fix_skill="acp-agentic-commerce:acp-checkout-rest",
    ))

    if deep:
        body = json.dumps({
            "items": [{"id": "sku_readiness_demo", "quantity": 1}],
            "currency": "usd",
        })
        cs = fetch(acp_base + "/checkout_sessions", method="POST", body=body,
                   headers={"API-Version": acp_ver,
                            "Idempotency-Key": "readiness-audit-001",
                            "Request-Id": "readiness-req-001"})
        d = {}
        try:
            d = json.loads(cs["body"]) if cs["body"] else {}
        except ValueError:
            pass
        reachable = cs["status"] in (200, 201) or _acp_error_shaped(d)
        checks.append(check(
            "ACP create_checkout_session reachable (200/201 or ACP-shaped error)",
            reachable, 2, evidence(cs),
            fix_skill="acp-agentic-commerce:acp-checkout-rest",
        ))
        canonical = (
            cs["status"] in (200, 201)
            and (d.get("object") == "checkout_session"
                 or str(d.get("protocol", "")).upper() == "ACP")
            and d.get("status") in ACP_STATUSES
            and isinstance(d.get("line_items"), list)
            and bool(d.get("totals"))
        )
        checks.append(check(
            "ACP response is a canonical CheckoutSession "
            "(object, status enum, top-level line_items[], totals)",
            canonical, 2,
            "object={!r} status={!r} line_items={} totals={}".format(
                d.get("object"), d.get("status"),
                type(d.get("line_items")).__name__, bool(d.get("totals")))
            if d else evidence(cs),
            fix_skill="acp-agentic-commerce:acp-checkout-rest",
        ))
        ver_ok = (cs["headers"].get("api-version") == acp_ver
                  or d.get("api_version") == acp_ver)
        checks.append(check(
            "ACP echoes negotiated API-Version", ver_ok, 1,
            "requested {} — header {!r} body {!r}".format(
                acp_ver, cs["headers"].get("api-version"), d.get("api_version")),
            fix_skill="acp-agentic-commerce:acp-capability-negotiation",
        ))
    else:
        checks.append(check(
            "ACP create_checkout_session (deep)", False, 0,
            "skipped — rerun with --deep to POST a demo cart",
        ))

    # ---------------- UCP checkout ----------------
    endpoints = ucp_endpoints(ucp_doc)
    ucp_base = (endpoints.get("rest") or origin).rstrip("/")

    uopt = fetch(ucp_base + "/checkout-sessions", method="OPTIONS")
    uallow = (uopt["headers"].get("allow", "") + " "
              + uopt["headers"].get("access-control-allow-methods", "")).upper()
    checks.append(check(
        "UCP /checkout-sessions surface answers (OPTIONS)",
        surface_answers(uopt), 1,
        "OPTIONS {} ct={} allow={!r}".format(
            uopt["status"], uopt["headers"].get("content-type", "-").split(";")[0],
            uallow.strip() or "-"),
        fix_skill="ucp-agentic-commerce:ucp-checkout-rest",
    ))

    if deep:
        ub = json.dumps({"line_items": [{"id": "sku_readiness_demo", "quantity": 1}],
                         "currency": "usd"})
        us = fetch(ucp_base + "/checkout-sessions", method="POST", body=ub,
                   headers={"UCP-Agent": "CommerceReadinessAudit/1.0"})
        ud = {}
        try:
            ud = json.loads(us["body"]) if us["body"] else {}
        except ValueError:
            pass
        u_canonical_body = (
            ud.get("status") in UCP_STATUSES
            or isinstance(ud.get("line_items"), list)
            or bool(ud.get("messages"))
        )
        # A 4xx carrying a UCP/ACP-shaped error body also proves the surface
        # speaks the protocol — same rule as the ACP reachability check.
        u_ok = (us["status"] in (200, 201) and u_canonical_body) \
            or (us["status"] in (400, 401, 415, 422) and _acp_error_shaped(ud))
        checks.append(check(
            "UCP checkout-session canonical (status enum / line_items[] / "
            "messages, or a shaped 4xx error)",
            u_ok, 2,
            evidence(us),
            fix_skill="ucp-agentic-commerce:ucp-checkout-rest",
        ))
    else:
        checks.append(check(
            "UCP create checkout-session (deep)", False, 0,
            "skipped — rerun with --deep",
        ))

    # ---------------- MCP endpoint ----------------
    mcp_url = endpoints.get("mcp")
    candidates = [u for u in (mcp_url, origin + "/mcp", origin + "/api/mcp") if u]
    # tools/list is a pure read — safe in every mode, no deep gating needed.
    mcp_ok, mcp_ev = False, []
    for u in candidates:
        r = fetch(u, method="POST", body=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}),
            headers={"Accept": "application/json, text/event-stream"})
        j = {}
        try:
            j = json.loads(r["body"]) if r["body"] else {}
        except ValueError:
            pass
        ok = r["status"] == 200 and (j.get("jsonrpc") == "2.0"
                                     or "result" in j or "error" in j
                                     or "event:" in r["body"][:200])
        mcp_ev.append("{} → {}".format(u, r["status"]))
        if ok:
            mcp_ok = True
            break
    checks.append(check(
        "MCP endpoint answers tools/list (JSON-RPC)",
        mcp_ok, 2, "; ".join(mcp_ev),
        fix_skill="ucp-agentic-commerce:ucp-checkout-mcp",
    ))

    # ---------------- NLWeb /ask ----------------
    if deep:
        ask = fetch(origin + "/ask", method="POST",
                    body=json.dumps({"query": "what do you sell?"}))
        ask_ct = ask["headers"].get("content-type", "")
        # require an API content-type: an HTML page containing the word
        # "answer" is not an /ask endpoint
        ask_ok = (ask["status"] == 200
                  and ("application/json" in ask_ct or "text/event-stream" in ask_ct)
                  and ("results" in ask["body"][:2000] or "answer" in ask["body"][:2000]))
    else:
        ask = fetch(origin + "/ask", method="OPTIONS")
        ask_ok = surface_answers(ask)
    checks.append(check(
        "NLWeb /ask endpoint answers", ask_ok, 1, evidence(ask),
        fix_skill="nlweb-protocol:nlweb-ask-endpoint",
    ))

    return {
        "probe": "transact", "id": "r4", "module": "Transactable",
        "origin": origin, "impact": 5, "complexity": 4,
        "na_condition": "non-commerce site with no checkout intent",
        "deep": deep,
        "checks": checks,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
