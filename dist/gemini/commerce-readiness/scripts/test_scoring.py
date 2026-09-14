#!/usr/bin/env python3
"""Synthetic tests for scoring paths that can't be exercised against live sites."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.probe import (surface_answers, ucp_endpoints, origin_of, extract_jsonld,
                       distinct_surface)
import readiness_audit as ra

fails = []
COUNT = 0
def ok(cond, name):
    global COUNT
    COUNT += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# --- surface_answers ---
ok(not surface_answers({"status": 404, "headers": {}}), "404 -> no")
ok(not surface_answers({"status": 0, "headers": {}}), "network dead -> no")
ok(not surface_answers({"status": 200, "headers": {"content-type": "text/html; charset=utf-8"}}), "SPA catch-all 200 html -> no")
ok(surface_answers({"status": 200, "headers": {"content-type": "application/json"}}), "200 json -> yes")
ok(surface_answers({"status": 405, "headers": {"content-type": "text/html"}}), "405 (even html) -> yes")
ok(surface_answers({"status": 401, "headers": {}}), "401 -> yes")
ok(not surface_answers({"status": 307, "headers": {"content-type": "text/plain"}}), "307 router fallback -> no")

# --- distinct_surface: catch-all baseline calibration ---
mk = lambda st, hdrs={}: {"status": st, "headers": hdrs}
base405 = mk(405, {"content-type": "text/html"})
ok(not distinct_surface(mk(405, {"content-type": "text/html"}), base405),
   "405 identical to catchall 405 -> no (the orcaqubits nginx case)")
ok(distinct_surface(mk(401), base405), "401 vs 405 baseline -> yes (differs)")
ok(distinct_surface(mk(405, {"allow": "POST, OPTIONS", "content-type": "text/html"}), base405),
   "405 with Allow header baseline lacks -> yes")
ok(distinct_surface(mk(405, {"content-type": "application/json"}), base405),
   "405 json vs html baseline -> yes")
ok(not distinct_surface(mk(200, {"content-type": "text/html"}), mk(404)),
   "200-html never a surface even against 404 baseline")
ok(not distinct_surface(mk(307, {"content-type": "text/plain"}), mk(404)),
   "3xx never a surface regardless of baseline")

# --- ucp_endpoints both shapes ---
canonical = {"services": {"dev.ucp.shopping": [
    {"transport": "mcp", "endpoint": "https://x/api/ucp/mcp"},
    {"transport": "rest", "endpoint": "https://x/api/ucp"},
    {"transport": "embedded"}]}}
simple = {"services": {"rest": {"endpoint": "https://y/rest"}, "mcp": {"endpoint": "https://y/mcp"}}}
ok(ucp_endpoints(canonical) == {"mcp": "https://x/api/ucp/mcp", "rest": "https://x/api/ucp"}, "canonical services shape")
ok(ucp_endpoints(simple) == {"rest": "https://y/rest", "mcp": "https://y/mcp"}, "simplified services shape")
ok(ucp_endpoints({}) == {}, "empty profile")
ok(ucp_endpoints({"services": None}) == {}, "null services")

# --- origin_of ---
ok(origin_of("shop.example.com/store?x=1") == ("https://shop.example.com", "shop.example.com"), "bare host with path")
ok(origin_of("http://a.b") == ("http://a.b", "a.b"), "explicit http kept")

# --- extract_jsonld: @graph + list + broken block ---
html = """<html><body>
<script type="application/ld+json">{"@context":"x","@graph":[{"@type":"Product","name":"A"},{"@type":"BreadcrumbList"}]}</script>
<script type="application/ld+json">[{"@type":"Offer"},{"@type":"Thing"}]</script>
<script type="application/ld+json">{broken json</script>
</body></html>"""
objs = extract_jsonld(html)
types = [o.get("@type") for o in objs]
ok("Product" in types and "Offer" in types and "BreadcrumbList" in types, "jsonld graph+list flatten, broken block skipped")

# --- score_module thresholds ---
def mod(id_, checks, impact=4, complexity=2):
    return {"id": id_, "module": id_, "impact": impact, "complexity": complexity, "checks": checks}
c = lambda p, w: {"name": "x", "pass": p, "weight": w, "evidence": ""}
m_pass = ra.score_module(mod("a", [c(True, 6), c(False, 1)]))          # 6/7 = 85.7%
m_part = ra.score_module(mod("b", [c(True, 3), c(False, 4)]))          # 3/7 = 43%
m_fail = ra.score_module(mod("c", [c(False, 5), c(True, 1)]))          # 1/6 = 17%
m_skip = ra.score_module(mod("d", [c(True, 2), c(False, 0)]))          # w0 excluded -> 2/2
ok(m_pass["status"] == "pass", "85%+ -> pass")
ok(m_part["status"] == "partial", "30-84% -> partial")
ok(m_fail["status"] == "fail", "<30% -> fail")
ok(m_skip["status"] == "pass" and m_skip["weight_total"] == 2, "weight-0 rows excluded from total")
ok(m_pass["priority"] == 4 * (6 - 2), "priority formula")

# --- blocked exclusion from weighted score ---
m_blocked = ra.score_module(mod("e", [c(True, 8)]), blocked=True)
got, total = ra.counted([m_pass, m_blocked])
ok(m_blocked["status"] == "blocked", "blocked status set")
ok((got, total) == (6, 7), "blocked module excluded from counted points AND total")

# --- render report with a blocker ---
rep = ra.render_report("https://x.example", [m_pass, m_blocked], deep=False, blocker=True)
ok("excluded from the score" in rep, "report explains blocked exclusion")
ok("(not counted)" in rep, "findings row marks blocked as not counted")
ok("Score 6 / 7" in rep, "headline score excludes blocked weight")

print("\n%d checks, %d failures" % (COUNT, len(fails)))
sys.exit(1 if fails else 0)
