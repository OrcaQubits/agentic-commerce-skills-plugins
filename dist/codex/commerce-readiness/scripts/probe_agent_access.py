#!/usr/bin/env python3
"""
R1 — Agent access pre-flight.

Can an AI agent's fetcher even reach this site? If the WAF challenges or
blocks agent user-agents, every downstream readiness check is moot — the
agent bounces before reading a byte. This probe compares a browser-UA
baseline against the fetcher UAs real agent products send.

Blocking *training* crawlers (GPTBot/CCBot) in robots.txt is a legitimate
policy choice and is NOT penalized. Blocking *fetchers* (ChatGPT-User,
Claude-User) at the WAF level is what closes the door on agentic commerce.

Usage:
    python probe_agent_access.py https://shop.example.com
    python probe_agent_access.py shop.example.com --json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from lib.probe import (fetch, check, evidence, looks_challenged, run_cli,
                       AGENT_UAS, BROWSER_UA)


def probe(origin, host, deep=False):
    checks = []

    base = fetch(origin + "/", ua=BROWSER_UA)
    base_ok = base["status"] == 200 and not looks_challenged(base)
    base_size = len(base["body"])
    checks.append(check(
        "browser baseline reachable", base_ok, 1,
        evidence(base),
    ))

    # Each agent fetcher UA must get substantially the same page.
    open_uas, blocked_uas = [], []
    for ua in AGENT_UAS:
        r = fetch(origin + "/", ua=ua)
        challenged = looks_challenged(r)
        # "wildly below baseline" = interstitial masquerading as 200
        thin = base_size > 5000 and len(r["body"]) < base_size * 0.2
        ok = r["status"] == 200 and not challenged and not thin
        (open_uas if ok else blocked_uas).append(
            "{} → {}{}".format(ua.split("/")[0], r["status"],
                               " CHALLENGE" if challenged else (" THIN" if thin else "")))
    checks.append(check(
        "agent fetcher UAs served like a browser",
        not blocked_uas, 3,
        "; ".join(open_uas + blocked_uas),
        fix_skill="webmcp-browser-agents:webmcp-setup",
    ))

    robots = fetch(origin + "/robots.txt")
    has_robots = robots["status"] == 200 and len(robots["body"]) > 0
    checks.append(check(
        "robots.txt present", has_robots, 1, evidence(robots),
    ))

    # Fetcher UAs must not be Disallow'd site-wide in robots.txt.
    fetcher_blocked = []
    if has_robots:
        # normalize CRLF and guarantee a trailing newline so a
        # "Disallow: /" on the file's last line still matches
        body = robots["body"].lower().replace("\r", "") + "\n"
        for ua in ("chatgpt-user", "claude-user", "perplexitybot", "oai-searchbot"):
            idx = body.find("user-agent: " + ua)
            if idx != -1 and "disallow: /\n" in body[idx:idx + 400]:
                fetcher_blocked.append(ua)
    # No robots.txt means nothing is disallowed — agents are allowed by
    # default, so absence passes this check (presence is scored above).
    checks.append(check(
        "robots.txt does not disallow agent fetchers",
        not fetcher_blocked, 2,
        ("blocked: " + ", ".join(fetcher_blocked)) if fetcher_blocked
        else ("no site-wide Disallow for fetcher UAs" if has_robots
              else "no robots.txt — nothing disallowed"),
    ))

    return {
        "probe": "agent-access", "id": "r1", "module": "Reachable",
        "origin": origin, "impact": 5, "complexity": 2,
        "na_condition": None,
        "blocker": bool(blocked_uas),
        "checks": checks,
    }


if __name__ == "__main__":
    run_cli(probe, __doc__.strip().splitlines()[0])
