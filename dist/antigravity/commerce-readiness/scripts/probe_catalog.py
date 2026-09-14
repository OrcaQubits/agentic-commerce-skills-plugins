#!/usr/bin/env python3
"""
R3 — Catalog comprehension.

Once an agent reaches a product page, can it actually *understand* what is
for sale? Structured data is the difference between an agent quoting your
price and an agent guessing it. Probes a product page (found via sitemap)
for Product JSON-LD with Offer, price, currency, and availability.

Usage:
    python probe_catalog.py https://shop.example.com [--json]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import (fetch, check, evidence, extract_jsonld,
                       find_product_url, run_cli)


def _as_list(x):
    return x if isinstance(x, list) else [x] if x is not None else []


def probe(origin, host, deep=False):
    checks = []

    pdp_url = find_product_url(origin)
    checks.append(check(
        "product URL discoverable from sitemap",
        bool(pdp_url), 1,
        pdp_url or "no /product|/p|/item leaf URL in sitemap.xml",
    ))

    products = []
    pdp_ev = "no product page to fetch"
    if pdp_url:
        pdp = fetch(pdp_url)
        pdp_ev = evidence(pdp)
        if pdp["status"] == 200:
            objs = extract_jsonld(pdp["body"])
            # Accept both Product and ProductGroup (the variant-aware type);
            # ProductGroup nests its purchasable Products under hasVariant.
            products = [o for o in objs
                        if {"Product", "ProductGroup"} & set(_as_list(o.get("@type")))]

    checks.append(check(
        "product page carries Product/ProductGroup JSON-LD",
        bool(products), 2, pdp_ev if not products
        else "{} object(s): {}".format(
            len(products), [p.get("@type") for p in products]),
        fix_skill="nlweb-protocol:nlweb-schema-org-grounding",
    ))

    # Walk offers on the products themselves AND on ProductGroup variants.
    offer_carriers = list(products)
    for prod in products:
        offer_carriers.extend(
            v for v in _as_list(prod.get("hasVariant")) if isinstance(v, dict))

    offer_ok = price_ok = avail_ok = False
    offer_ev = "no Product JSON-LD"
    for prod in offer_carriers:
        for offer in _as_list(prod.get("offers")):
            if not isinstance(offer, dict):
                continue
            offer_ok = True
            price = offer.get("price") or offer.get("lowPrice")
            currency = offer.get("priceCurrency")
            if price is not None and currency:
                price_ok = True
            if offer.get("availability"):
                avail_ok = True
            offer_ev = "offers: price={!r} priceCurrency={!r} availability={!r}".format(
                price, currency, offer.get("availability"))
    checks.append(check(
        "Offer object present on Product", offer_ok, 1, offer_ev))
    checks.append(check(
        "Offer declares price + priceCurrency", price_ok, 2, offer_ev))
    checks.append(check(
        "Offer declares availability", avail_ok, 1, offer_ev))

    return {
        "probe": "catalog", "id": "r3", "module": "Comprehensible",
        "origin": origin, "impact": 4, "complexity": 2,
        "na_condition": "site sells nothing (no product URLs anywhere)",
        "product_url": pdp_url,
        "checks": checks,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
