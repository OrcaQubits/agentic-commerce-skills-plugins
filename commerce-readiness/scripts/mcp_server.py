#!/usr/bin/env python3
"""
MCP server exposing the agentic-commerce readiness audit as callable tools.

Any MCP client (Claude, ChatGPT, Gemini, a shopping agent) can POST
JSON-RPC to this endpoint and audit a storefront:

    tools/list   -> readiness_audit, readiness_quick_check
    tools/call   -> runs the probes, returns score.json as structuredContent

Design:
- Python 3.8+ stdlib only, like the probes it wraps. No pip installs.
- Stateless: every POST is independent. Written against the 2026-07-28
  MCP revision (resultType, structuredContent); also answers the
  handshake-era `initialize` / `notifications/initialized` so older
  clients work. Re-verify shapes against the live spec before extending:
  https://modelcontextprotocol.io/specification/
- Safe by default:
    * SSRF guard - target hosts resolving to loopback/private/link-local/
      reserved ranges are refused (the server fetches caller-supplied
      URLs from wherever it is deployed). Override for local testing
      only: MCP_ALLOW_PRIVATE=1.
    * deep mode (POST probes that create demo checkout sessions on the
      TARGET site) is refused unless the operator sets
      READINESS_ALLOW_DEEP=1. A public endpoint must not let anonymous
      callers aim deep probes at third parties.
    * bounded concurrency - at most MAX_CONCURRENT_AUDITS run at once;
      excess calls get a tool-execution error telling the model to retry.
    * rate limiting beyond that belongs to the fronting proxy (nginx).

Usage:
    python mcp_server.py                       # 127.0.0.1:8765, path /mcp
    python mcp_server.py --host 0.0.0.0 --port 8765 --path /mcp
    curl -sS -X POST localhost:8765/mcp -H 'content-type: application/json' \
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
"""

import argparse
import ipaddress
import json
import os
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.probe import origin_of, force_utf8_stdout  # noqa: E402
import readiness_audit  # noqa: E402

SERVER_INFO = {"name": "commerce-readiness-mcp", "version": "1.0.0"}
PROTOCOL_VERSION = "2026-07-28"
MAX_CONCURRENT_AUDITS = int(os.environ.get("MAX_CONCURRENT_AUDITS", "4"))
_audit_slots = threading.Semaphore(MAX_CONCURRENT_AUDITS)

TOOLS = [
    {
        "name": "readiness_audit",
        "title": "Agentic Commerce Readiness Audit",
        "description": (
            "Audit a live website's readiness for AI-agent commerce. Runs six "
            "HTTP-evidence probe modules - r1 Reachable (agent-UA access), "
            "r2 Discoverable (UCP/ACP/A2A discovery docs, llms.txt, feed), "
            "r3 Comprehensible (Product JSON-LD), r4 Transactable (checkout/"
            "MCP/NLWeb surfaces), r5 Payable, r6 Trustworthy - and returns a "
            "weighted Pass/Partial/Fail scorecard with per-check evidence and "
            "a fix skill for every gap. Shallow (GET/OPTIONS) probes only; "
            "takes up to ~60 seconds. Scores measure capability, not adoption."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Site to audit, e.g. https://shop.example.com",
                },
                "modules": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["r1", "r2", "r3", "r4", "r5", "r6"]},
                    "description": "Subset of modules to run (default: all six)",
                },
                "deep": {
                    "type": "boolean",
                    "description": (
                        "Enable POST probes (demo checkout creates). Refused "
                        "unless the server operator has allowed deep mode - "
                        "created sessions can trigger side effects on the "
                        "target site."
                    ),
                },
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
    {
        "name": "readiness_quick_check",
        "title": "Readiness Quick Check",
        "description": (
            "Sixty-second triage: can AI agents reach this site (r1), and can "
            "they discover that it does commerce (r2)? GET-only, safe against "
            "any public site. Use before the full readiness_audit."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Site to check"},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
]


# ---------------------------------------------------------------------------
# SSRF guard
# ---------------------------------------------------------------------------
def ssrf_reject_reason(url):
    """Non-empty string when the target must be refused."""
    if os.environ.get("MCP_ALLOW_PRIVATE") == "1":
        return None
    origin, host = origin_of(url)
    scheme = urlparse(origin).scheme
    if scheme not in ("http", "https"):
        return "only http(s) targets are allowed"
    bare = host.split(":")[0].strip("[]")
    try:
        infos = socket.getaddrinfo(bare, None)
    except socket.gaierror:
        return "hostname does not resolve"
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return ("target resolves to a non-public address ({}) - refusing "
                    "to probe internal networks".format(ip))
    return None


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------
def run_audit(url, modules=None, deep=False):
    """Execute probes via readiness_audit's module registry; returns payload dict."""
    origin, host = origin_of(url)
    wanted = [m for m in (modules or list(readiness_audit.MODULES))
              if m in readiness_audit.MODULES]
    if not wanted:
        raise ToolError("no valid modules; valid ids: r1..r6")

    results = {}
    for m in wanted:
        try:
            results[m] = readiness_audit.MODULES[m](origin, host, deep)
        except Exception as e:  # a probe crash is evidence, not a 500
            results[m] = {"probe": m, "id": m, "module": m, "origin": origin,
                          "impact": 3, "complexity": 3, "checks": [
                              {"name": "probe crashed", "pass": False,
                               "weight": 1, "evidence": repr(e)}]}

    blocker = bool(results.get("r1", {}).get("blocker"))
    mods = [readiness_audit.score_module(
                results[m], blocked=(blocker and m in ("r2", "r3", "r4", "r5")))
            for m in wanted]
    got, total = readiness_audit.counted(mods)
    return {
        "host": host,
        "deep": deep,
        "scope": wanted,
        "scoreboard": {
            "pass": sum(1 for x in mods if x["status"] == "pass"),
            "partial": sum(1 for x in mods if x["status"] == "partial"),
            "fail": sum(1 for x in mods if x["status"] == "fail"),
            "blocked": sum(1 for x in mods if x["status"] == "blocked"),
            "weighted": {"points": got, "total": total,
                         "pct": int(round(100 * got / total)) if total else 0},
        },
        "blockers": ([{"id": "A", "title": "WAF blocks agent fetchers",
                       "gates": ["r2", "r3", "r4", "r5"]}] if blocker else []),
        "modules": mods,
    }


class ToolError(Exception):
    """Actionable tool-execution error (isError:true, model can retry)."""


def call_tool(name, args):
    if name not in ("readiness_audit", "readiness_quick_check"):
        return None  # protocol error, handled by caller

    url = args.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ToolError("'url' is required, e.g. https://shop.example.com")
    reason = ssrf_reject_reason(url)
    if reason:
        raise ToolError(reason)

    if name == "readiness_quick_check":
        payload = run_audit(url, modules=["r1", "r2"], deep=False)
    else:
        deep = bool(args.get("deep"))
        if deep and os.environ.get("READINESS_ALLOW_DEEP") != "1":
            raise ToolError(
                "deep mode is disabled on this server: deep probes POST demo "
                "checkout sessions to the target site, which can trigger real "
                "side effects. Re-run with deep=false, or ask the operator to "
                "set READINESS_ALLOW_DEEP=1 for internal use.")
        payload = run_audit(url, modules=args.get("modules"), deep=deep)

    sb = payload["scoreboard"]
    summary = "{}: {} - {}/{} ({}%) | {} pass, {} partial, {} fail{}".format(
        name, payload["host"],
        sb["weighted"]["points"], sb["weighted"]["total"], sb["weighted"]["pct"],
        sb["pass"], sb["partial"], sb["fail"],
        ", {} blocked (excluded from score)".format(sb["blocked"]) if sb["blocked"] else "")
    return {
        "resultType": "complete",
        "content": [
            {"type": "text", "text": summary},
            {"type": "text", "text": json.dumps(payload)},
        ],
        "structuredContent": payload,
        "isError": False,
    }


# ---------------------------------------------------------------------------
# JSON-RPC over HTTP
# ---------------------------------------------------------------------------
def handle_rpc(msg):
    """One JSON-RPC message -> response dict, or None for notifications."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return _err(None, -32600, "Invalid Request: expected JSON-RPC 2.0 object")
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}

    if method == "notifications/initialized":
        return None  # handshake-era compat: acknowledge silently
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "initialize":  # handshake-era compat
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": params.get("protocolVersion") or PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
        }}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid,
                "result": {"resultType": "complete", "tools": TOOLS}}
    if method == "tools/call":
        name = (params or {}).get("name")
        args = (params or {}).get("arguments") or {}
        if not _audit_slots.acquire(blocking=False):
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "resultType": "complete", "isError": True,
                "content": [{"type": "text", "text":
                             "server at capacity ({} concurrent audits); retry "
                             "shortly".format(MAX_CONCURRENT_AUDITS)}]}}
        try:
            result = call_tool(name, args)
            if result is None:
                return _err(mid, -32602, "Unknown tool: {}".format(name))
            return {"jsonrpc": "2.0", "id": mid, "result": result}
        except ToolError as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "resultType": "complete", "isError": True,
                "content": [{"type": "text", "text": str(e)}]}}
        except Exception as e:
            return _err(mid, -32603, "Internal error: {}".format(repr(e)[:200]))
        finally:
            _audit_slots.release()
    return _err(mid, -32601, "Method not found: {}".format(method))


def _err(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


class Handler(BaseHTTPRequestHandler):
    server_version = "commerce-readiness-mcp/1.0"
    mcp_path = "/mcp"

    def _send(self, status, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            return self._send(200, {"status": "ok", "server": SERVER_INFO})
        return self._send(405, {"error": "POST JSON-RPC to {}".format(self.mcp_path)})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") not in (self.mcp_path.rstrip("/"), ""):
            return self._send(404, {"error": "MCP endpoint is {}".format(self.mcp_path)})
        try:
            length = min(int(self.headers.get("Content-Length", 0)), 1024 * 1024)
            raw = self.rfile.read(length)
            msg = json.loads(raw.decode("utf-8"))
        except (ValueError, TypeError):
            return self._send(400, _err(None, -32700, "Parse error"))
        resp = handle_rpc(msg)
        if resp is None:  # notification
            self.send_response(202)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        return self._send(200, resp)

    def log_message(self, fmt, *args):  # quiet by default; nginx logs access
        if os.environ.get("MCP_VERBOSE") == "1":
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser(description="Readiness-audit MCP server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--path", default="/mcp")
    args = ap.parse_args()
    force_utf8_stdout()
    Handler.mcp_path = args.path
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print("commerce-readiness MCP server on http://{}:{}{}  "
          "(deep={}, private-targets={})".format(
              args.host, args.port, args.path,
              "allowed" if os.environ.get("READINESS_ALLOW_DEEP") == "1" else "refused",
              "allowed" if os.environ.get("MCP_ALLOW_PRIVATE") == "1" else "refused"))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
