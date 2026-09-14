#!/usr/bin/env python3
"""Offline integration tests for the readiness-audit MCP server.

Spins a fixture 'storefront' and the MCP server on loopback, then exercises
the full JSON-RPC loop: tools/list shape, a real quick-check audit against
the fixture, SSRF refusal, deep-mode refusal, unknown tool, initialize
compat, and health. No external network.

Run: python scripts/test_mcp_server.py   (exit 0 = all pass)
"""
import json
import os
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

fails = []
COUNT = 0


def ok(cond, name):
    global COUNT
    COUNT += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


# ---------------------------------------------------------------------------
# Fixture storefront: robots + llms.txt + sitemap, 404 for everything else
# ---------------------------------------------------------------------------
class Fixture(BaseHTTPRequestHandler):
    ROUTES = {
        "/": ("text/html", "<!doctype html><html><body>Fixture shop, plenty of "
                           "words to make a body " + "x" * 400 + "</body></html>"),
        "/robots.txt": ("text/plain", "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"),
        "/llms.txt": ("text/plain", "# Fixture Shop\nAn offline storefront fixture "
                                    "for MCP server tests.\n"),
        "/sitemap.xml": ("application/xml",
                         '<?xml version="1.0"?><urlset><url><loc>http://HOST/product/x'
                         '</loc></url></urlset>'),
    }

    def do_GET(self):
        route = self.ROUTES.get(self.path.split("?")[0])
        if route:
            ct, body = route
            body = body.replace("HOST", self.headers.get("Host", ""))
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    do_OPTIONS = do_GET
    do_POST = do_GET

    def log_message(self, *a):
        pass


def rpc(port, payload):
    req = urllib.request.Request(
        "http://127.0.0.1:{}/mcp".format(port),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, json.loads(r.read().decode())


def main():
    # fixture on an ephemeral port
    fx = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    fx_port = fx.server_address[1]
    threading.Thread(target=fx.serve_forever, daemon=True).start()

    # MCP server in-process: private targets allowed (we probe loopback),
    # deep NOT allowed (so the refusal path is testable)
    os.environ["MCP_ALLOW_PRIVATE"] = "1"
    os.environ.pop("READINESS_ALLOW_DEEP", None)
    import mcp_server
    srv = ThreadingHTTPServer(("127.0.0.1", 0), mcp_server.Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.2)
    target = "http://127.0.0.1:{}".format(fx_port)

    # --- health -------------------------------------------------------------
    with urllib.request.urlopen("http://127.0.0.1:{}/healthz".format(port), timeout=10) as r:
        ok(r.status == 200 and b"ok" in r.read(), "GET /healthz -> ok")

    # --- initialize compat ---------------------------------------------------
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-06-18"}})
    ok(st == 200 and j["result"]["serverInfo"]["name"] == "commerce-readiness-mcp",
       "initialize answered (handshake-era compat)")
    ok(j["result"]["protocolVersion"] == "2025-06-18", "initialize echoes client revision")

    # --- tools/list ----------------------------------------------------------
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = j["result"]["tools"]
    names = [t["name"] for t in tools]
    ok(st == 200 and j["result"].get("resultType") == "complete", "tools/list resultType complete")
    ok(names == ["readiness_audit", "readiness_quick_check"], "both tools listed, stable order")
    ok(all(isinstance(t.get("inputSchema"), dict) and t["inputSchema"].get("type") == "object"
           for t in tools), "every tool has an object inputSchema")

    # --- real audit against the fixture --------------------------------------
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                       "params": {"name": "readiness_quick_check",
                                  "arguments": {"url": target}}})
    res = j["result"]
    sc = res.get("structuredContent") or {}
    ok(st == 200 and res.get("isError") is False, "quick check runs without error")
    ok(sc.get("scope") == ["r1", "r2"], "quick check scoped to r1+r2")
    mods = {m["id"]: m for m in sc.get("modules", [])}
    ok(mods.get("r1", {}).get("status") in ("pass", "partial"),
       "fixture is reachable (r1 {} {}/{})".format(
           mods.get("r1", {}).get("status"), mods.get("r1", {}).get("points"),
           mods.get("r1", {}).get("weight_total")))
    r2_names = {c["name"]: c["pass"] for c in mods.get("r2", {}).get("checks", [])}
    ok(r2_names.get("llms.txt") is True, "audit found the fixture's llms.txt")
    ok(res["content"][0]["type"] == "text" and "%" in res["content"][0]["text"],
       "human summary in content[0]")
    ok(json.loads(res["content"][1]["text"]) == sc,
       "content[1] serializes structuredContent (back-compat rule)")

    # --- deep refused ---------------------------------------------------------
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                       "params": {"name": "readiness_audit",
                                  "arguments": {"url": target, "deep": True,
                                                "modules": ["r1"]}}})
    res = j["result"]
    ok(res.get("isError") is True and "deep" in res["content"][0]["text"],
       "deep mode refused without READINESS_ALLOW_DEEP")

    # --- SSRF guard -----------------------------------------------------------
    os.environ.pop("MCP_ALLOW_PRIVATE")
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                       "params": {"name": "readiness_quick_check",
                                  "arguments": {"url": "http://127.0.0.1:{}".format(fx_port)}}})
    res = j["result"]
    ok(res.get("isError") is True and "non-public" in res["content"][0]["text"],
       "loopback target refused (SSRF guard)")
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                       "params": {"name": "readiness_quick_check",
                                  "arguments": {"url": "http://169.254.169.254/latest/meta-data/"}}})
    ok(j["result"].get("isError") is True, "cloud metadata IP refused (SSRF guard)")
    os.environ["MCP_ALLOW_PRIVATE"] = "1"

    # --- protocol errors --------------------------------------------------------
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                       "params": {"name": "nope", "arguments": {}}})
    ok(j.get("error", {}).get("code") == -32602, "unknown tool -> -32602 protocol error")
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 8, "method": "bogus/method", "params": {}})
    ok(j.get("error", {}).get("code") == -32601, "unknown method -> -32601")
    st, j = rpc(port, {"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                       "params": {"name": "readiness_audit", "arguments": {}}})
    ok(j["result"].get("isError") is True and "url" in j["result"]["content"][0]["text"],
       "missing url -> actionable tool error, not a 500")

    print("\n%d checks, %d failures" % (COUNT, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
