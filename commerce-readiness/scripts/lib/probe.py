#!/usr/bin/env python3
"""
Shared HTTP probe helpers for the agentic-commerce readiness scripts.

Design constraints (deliberate):
- Python 3.8+ standard library ONLY — no pip installs, works on a fresh
  Windows/macOS/Linux machine.
- Every network call is bounded (timeout, size cap) and never raises out of
  the helper — probes score evidence, they do not crash on a bad server.
- Evidence discipline: helpers return what the wire said (status, headers,
  first N bytes), never an interpretation. Interpretation happens in the
  probe scripts, and each conclusion must cite the raw evidence.
"""

import gzip
import io
import json
import re
import socket
import ssl
import sys
import zlib
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from urllib.request import (Request, urlopen, build_opener,
                            HTTPRedirectHandler, HTTPSHandler)
from urllib.error import HTTPError, URLError


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

DEFAULT_TIMEOUT = 12          # seconds per request
MAX_BODY = 2 * 1024 * 1024    # read at most 2 MB — commerce PDPs are heavy,
                              # and JSON-LD often sits at the end of the page

# User agents used by the agent-access pre-flight. These mirror the fetcher
# UAs real agent products send. Keep the browser baseline first.
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
AGENT_UAS = [
    "ChatGPT-User/1.0",
    "Claude-User/1.0",
    "PerplexityBot/1.0",
    "OAI-SearchBot/1.0",
]

CHALLENGE_MARKERS = re.compile(
    r"just a moment|cf-browser-verification|captcha|attention required"
    r"|enable javascript to continue|checking your browser",
    re.IGNORECASE,
)


def fetch(url, method="GET", headers=None, body=None, ua=BROWSER_UA,
          timeout=DEFAULT_TIMEOUT, follow_redirects=True):
    """One bounded HTTP request. Never raises.

    Returns a dict:
      status: int (0 on network failure)
      headers: dict[str, str] (lower-cased keys)
      body: str (decoded, truncated to MAX_BODY)
      url: str (final URL after redirects)
      error: str | None
    """
    req_headers = {"User-Agent": ua, "Accept": "*/*",
                   "Accept-Encoding": "gzip, deflate"}
    if headers:
        req_headers.update(headers)
    data = None
    if body is not None:
        data = body.encode("utf-8") if isinstance(body, str) else body
        req_headers.setdefault("Content-Type", "application/json")

    req = Request(url, data=data, headers=req_headers, method=method)
    ctx = ssl.create_default_context()
    try:
        if follow_redirects:
            opened = urlopen(req, timeout=timeout, context=ctx)
        else:
            opener = build_opener(_NoRedirect, HTTPSHandler(context=ctx))
            opened = opener.open(req, timeout=timeout)
        with opened as resp:
            raw = resp.read(MAX_BODY)
            return {
                "status": resp.status,
                "headers": {k.lower(): v for k, v in resp.headers.items()},
                "body": _decode(raw, resp.headers.get("Content-Encoding")),
                "url": resp.url,
                "error": None,
            }
    except HTTPError as e:
        try:
            raw = e.read(MAX_BODY)
        except Exception:
            raw = b""
        return {
            "status": e.code,
            "headers": {k.lower(): v for k, v in (e.headers or {}).items()},
            "body": _decode(raw, (e.headers or {}).get("Content-Encoding")),
            "url": url,
            "error": None,
        }
    except (URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError) as e:
        return {"status": 0, "headers": {}, "body": "", "url": url,
                "error": str(getattr(e, "reason", e))}
    except Exception as e:  # last-resort guard: a probe must never crash
        return {"status": 0, "headers": {}, "body": "", "url": url,
                "error": repr(e)}


def _decode(raw, encoding):
    if encoding:
        enc = encoding.lower()
        try:
            if "gzip" in enc:
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read(MAX_BODY)
            elif "deflate" in enc:
                raw = zlib.decompress(raw)
        except Exception:
            pass
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def origin_of(url):
    """Normalize user input to (origin, host). Accepts bare hosts."""
    if not re.match(r"^https?://", url):
        url = "https://" + url
    p = urlparse(url)
    return "{}://{}".format(p.scheme, p.netloc), p.netloc


def get_json(url, **kw):
    """Fetch + parse JSON. Adds parsed `json` key (None on parse failure)."""
    r = fetch(url, headers={"Accept": "application/json"}, **kw)
    r["json"] = None
    if r["body"]:
        try:
            r["json"] = json.loads(r["body"])
        except (ValueError, TypeError):
            pass
    return r


def looks_challenged(resp):
    """True when a response is a bot-challenge interstitial, not content."""
    if resp["status"] in (403, 429, 503):
        return True
    return bool(CHALLENGE_MARKERS.search(resp["body"][:20000]))


def surface_answers(resp):
    """Does an API surface genuinely answer here — as opposed to a SPA
    catch-all serving 200 text/html for every unknown path?

    Network-dead and 404 are clear No. A 200 whose content-type is HTML is
    treated as No for *API* surfaces: real checkout/tool endpoints answer
    with JSON, an error object, or at minimum a non-HTML 4xx. A 3xx is
    also No — urllib does not follow redirects for OPTIONS/POST, and a
    "307 Redirecting..." on an API path is a router fallback, not a
    surface answering (conservative reading, per the evidence rules).
    """
    if resp["status"] in (0, 404) or 300 <= resp["status"] < 400:
        return False
    ct = resp["headers"].get("content-type", "")
    if resp["status"] == 200 and "text/html" in ct:
        return False
    return True


CANARY_PATH = "/__readiness_canary_404__"


def catchall_baseline(origin, method="OPTIONS"):
    """The site's response to a path that certainly does not exist.

    SPA servers and nginx catch-alls answer *every* unknown path the same
    way (200 index.html, 405 on OPTIONS, a 307 to a router...). A status
    that matches this baseline is the wallpaper, not an API surface.
    """
    return fetch(origin + CANARY_PATH, method=method)


def distinct_surface(resp, baseline):
    """surface_answers + must be distinguishable from the catch-all.

    A response proves a *distinct* surface when it differs from the
    baseline in status, or carries API-shaped signals the baseline lacks
    (an Allow header, a non-HTML content-type).
    """
    if not surface_answers(resp):
        return False
    if resp["status"] != baseline["status"]:
        return True
    if resp["headers"].get("allow") and not baseline["headers"].get("allow"):
        return True
    ct = resp["headers"].get("content-type", "")
    bct = baseline["headers"].get("content-type", "")
    if "json" in ct and "json" not in bct:
        return True
    return False


def evidence(resp, max_len=160):
    """One-line verbatim evidence string for a response."""
    if resp["error"]:
        return "network error: {}".format(resp["error"][:max_len])
    ct = resp["headers"].get("content-type", "-")
    frag = re.sub(r"\s+", " ", resp["body"][:max_len]).strip()
    return "HTTP {} ct={} body[:{}]={!r}".format(
        resp["status"], ct.split(";")[0], max_len, frag)


class _JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._in_ldjson = False
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            a = dict(attrs)
            if (a.get("type") or "").strip().lower() == "application/ld+json":
                self._in_ldjson = True
                self._buf = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ldjson:
            self._in_ldjson = False
            self.blocks.append("".join(self._buf))

    def handle_data(self, data):
        if self._in_ldjson:
            self._buf.append(data)


def extract_jsonld(html):
    """All parsed application/ld+json objects from an HTML document.

    Flattens @graph arrays and top-level lists so callers see a flat list of
    dict objects.
    """
    p = _JsonLdParser()
    try:
        p.feed(html)
    except Exception:
        pass
    out = []
    for block in p.blocks:
        try:
            data = json.loads(block)
        except (ValueError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                out.append(item)
                graph = item.get("@graph")
                if isinstance(graph, list):
                    out.extend(x for x in graph if isinstance(x, dict))
    return out


def ucp_endpoints(profile):
    """Transport → endpoint map from a UCP profile's `services`.

    Handles both shapes seen in the wild:
      canonical:  services: {"dev.ucp.shopping": [{transport, endpoint, ...}]}
      simplified: services: {"rest": {"endpoint": ...}, "mcp": {...}}
    """
    out = {}
    services = (profile or {}).get("services") or {}
    if not isinstance(services, dict):
        return out
    for key, val in services.items():
        if isinstance(val, dict) and "endpoint" in val:
            out.setdefault(key.lower(), val["endpoint"])
        elif isinstance(val, list):
            for binding in val:
                if isinstance(binding, dict) and binding.get("endpoint"):
                    t = str(binding.get("transport", "")).lower()
                    if t:
                        out.setdefault(t, binding["endpoint"])
    return out


def find_product_url(origin):
    """Best-effort product-page URL from the sitemap. Returns None quietly.

    Only a heuristic: looks for /product/, /products/, /p/, /item/ leaf URLs
    in sitemap.xml (following one level of sitemap-index indirection).
    """
    pat = re.compile(r"<loc>([^<]+/(?:products?|p|item)/[^<]+)</loc>", re.I)
    idx = re.compile(r"<loc>([^<]+\.xml[^<]*)</loc>", re.I)

    def unescape(u):  # sitemap <loc> values are XML-escaped
        return u.replace("&amp;", "&").replace("&#38;", "&").strip()

    sm = fetch(urljoin(origin, "/sitemap.xml"))
    if sm["status"] != 200:
        return None
    m = pat.search(sm["body"])
    if m:
        return unescape(m.group(1))
    # one level of sitemap index
    for child in idx.findall(sm["body"])[:5]:
        c = fetch(unescape(child))
        m = pat.search(c["body"])
        if m:
            return unescape(m.group(1))
    return None


def force_utf8_stdout():
    """Windows consoles default to cp1252; probe evidence is UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def emit(result, as_json):
    """Standard probe output: pretty text or machine JSON."""
    force_utf8_stdout()
    if as_json:
        print(json.dumps(result, indent=2))
        return
    print("# {} — {}".format(result["probe"], result["origin"]))
    for c in result["checks"]:
        mark = "skip" if c["weight"] == 0 else ("PASS" if c["pass"] else "fail")
        print("  [{}] w={} {} — {}".format(mark, c["weight"], c["name"], c["evidence"]))
    total = sum(c["weight"] for c in result["checks"])
    got = sum(c["weight"] for c in result["checks"] if c["pass"])
    print("  score {}/{}".format(got, total))


def run_cli(probe_fn, description):
    """Shared argparse main for every probe script."""
    import argparse
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("url", help="Site URL or bare host, e.g. https://shop.example.com")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--deep", action="store_true",
                    help="enable POST probes (creates real checkout/ask calls; "
                         "safe-by-design but opt-in)")
    args = ap.parse_args()
    origin, host = origin_of(args.url)
    result = probe_fn(origin, host, deep=args.deep)
    emit(result, args.json)
    return result


def check(name, passed, weight, ev, fix_skill=None):
    """One scored sub-check row."""
    row = {"name": name, "pass": bool(passed), "weight": weight, "evidence": ev}
    if fix_skill:
        row["fix_skill"] = fix_skill
    return row
