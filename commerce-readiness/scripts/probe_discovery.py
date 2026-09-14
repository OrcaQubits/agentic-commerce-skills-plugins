#!/usr/bin/env python3
"""
R2 — Agentic commerce discovery surface.

Can an agent *find out* that this site does commerce, and which protocols it
speaks? Probes the well-known discovery documents each protocol defines:

  UCP   /.well-known/ucp (or ucp.json)        — services, capabilities, keys
  ACP   /.well-known/acp.json                 — api_base_url, versions
  A2A   /.well-known/agent-card.json          — agent card
  llms.txt, sitemap.xml, product feed         — the generic agent surface

Usage:
    python probe_discovery.py https://shop.example.com [--json]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import fetch, get_json, check, evidence, run_cli


def probe(origin, host, deep=False):
    checks = []

    # --- UCP profile -----------------------------------------------------
    ucp = get_json(origin + "/.well-known/ucp")
    if ucp["status"] != 200 or ucp["json"] is None:
        ucp = get_json(origin + "/.well-known/ucp.json")
    ucp_doc = ucp["json"] if isinstance(ucp["json"], dict) else {}
    inner = ucp_doc.get("ucp", ucp_doc)
    ucp_ok = ucp["status"] == 200 and bool(
        inner.get("services") or inner.get("capabilities"))
    checks.append(check(
        "UCP profile at /.well-known/ucp declares services/capabilities",
        ucp_ok, 2, evidence(ucp),
        fix_skill="ucp-agentic-commerce:ucp-setup",
    ))

    # --- ACP discovery ---------------------------------------------------
    acp = get_json(origin + "/.well-known/acp.json")
    if acp["status"] != 200 or acp["json"] is None:
        acp = get_json(origin + "/.well-known/agentic-commerce")
    acp_doc = acp["json"] if isinstance(acp["json"], dict) else {}
    proto = acp_doc.get("protocol") or {}
    acp_ok = acp["status"] == 200 and (
        str(proto.get("name", "")).lower() == "acp" or "api_base_url" in acp_doc)
    checks.append(check(
        "ACP discovery doc (acp.json / agentic-commerce) with api_base_url",
        acp_ok, 2, evidence(acp),
        fix_skill="acp-agentic-commerce:acp-setup",
    ))

    # --- A2A agent card --------------------------------------------------
    card = get_json(origin + "/.well-known/agent-card.json")
    if card["status"] != 200 or card["json"] is None:
        card = get_json(origin + "/.well-known/agent.json")
    card_doc = card["json"] if isinstance(card["json"], dict) else {}
    card_ok = card["status"] == 200 and bool(
        card_doc.get("skills") or card_doc.get("capabilities")
        or card_doc.get("url") or card_doc.get("name"))
    checks.append(check(
        "A2A agent card at /.well-known/agent-card.json",
        card_ok, 1, evidence(card),
        fix_skill="a2a-multi-agent:a2a-agent-card",
    ))

    # --- generic agent surface -------------------------------------------
    llms = fetch(origin + "/llms.txt")
    checks.append(check(
        "llms.txt", llms["status"] == 200 and len(llms["body"]) > 40, 1,
        evidence(llms),
        fix_skill="nlweb-protocol:nlweb-schema-org-grounding",
    ))

    sm = fetch(origin + "/sitemap.xml")
    sm_ok = sm["status"] == 200 and ("<urlset" in sm["body"] or "<sitemapindex" in sm["body"])
    checks.append(check("sitemap.xml", sm_ok, 1, evidence(sm)))

    feed_ok, feed_ev = False, []
    for path in ("/feeds/products.xml", "/products.tsv", "/product-feed.xml"):
        f = fetch(origin + path)
        if f["status"] == 200 and len(f["body"]) >= 1024:
            feed_ok = True
            feed_ev.append("{} 200 ({} bytes)".format(path, len(f["body"])))
            break
        feed_ev.append("{} {}".format(path, f["status"]))
    checks.append(check(
        "product feed served (feeds/products.xml | products.tsv)",
        feed_ok, 1, "; ".join(feed_ev),
        fix_skill="acp-agentic-commerce:acp-product-feed",
    ))

    discovered = {
        "ucp": inner if ucp_ok else None,
        "acp": acp_doc if acp_ok else None,
        "a2a": card_doc if card_ok else None,
    }

    return {
        "probe": "discovery", "id": "r2", "module": "Discoverable",
        "origin": origin, "impact": 5, "complexity": 1,
        "na_condition": None,
        "discovered": discovered,
        "checks": checks,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
