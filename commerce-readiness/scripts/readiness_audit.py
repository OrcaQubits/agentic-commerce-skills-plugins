#!/usr/bin/env python3
"""
Agentic Commerce Readiness Audit — runner.

Runs all six probes against a site, scores each module Pass/Partial/Fail,
prioritizes gaps, and writes:

  <out>/READINESS.md   human report: headline, action plan, findings table
  <out>/score.json     machine-readable breakdown (schema mirrors the report)

Every gap row carries `fix_skill` — the plugin skill in THIS marketplace
that closes it. The audit is the front door; the 16 plugins are the toolbox.

Scoring model (borrowed deliberately from the weighted-rubric pattern):
  Pass    ≥ 85% of module weight      Partial ≥ 30%      Fail < 30%
  priority = impact × (6 − complexity)   — higher = fix first

Evidence rules (binding):
  - A conclusion comes from HTTP responses only. No repo inspection, no
    inference from marketing pages.
  - A probe that cannot complete FAILS its sub-check; the evidence string
    says why so a human can re-run.
  - Ambiguous responses get the conservative reading.

Usage:
    python readiness_audit.py https://shop.example.com
    python readiness_audit.py shop.example.com --deep --out report/
    python readiness_audit.py shop.example.com --modules r1,r2,r4 --json-only
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.probe import origin_of, force_utf8_stdout  # noqa: E402
import probe_agent_access  # noqa: E402
import probe_discovery     # noqa: E402
import probe_catalog       # noqa: E402
import probe_transact      # noqa: E402
import probe_payments      # noqa: E402
import probe_trust         # noqa: E402

MODULES = {
    "r1": probe_agent_access.probe,
    "r2": probe_discovery.probe,
    "r3": probe_catalog.probe,
    "r4": probe_transact.probe,
    "r5": probe_payments.probe,
    "r6": probe_trust.probe,
}

STATUS_ICON = {"pass": "PASS", "partial": "PARTIAL", "fail": "FAIL",
               "blocked": "BLOCKED", "na": "N/A"}


def score_module(result, blocked=False):
    scored = [c for c in result["checks"] if c["weight"] > 0]
    total = sum(c["weight"] for c in scored)
    got = sum(c["weight"] for c in scored if c["pass"])
    pct = (got / total) if total else 0.0
    if blocked:
        status = "blocked"
    elif pct >= 0.85:
        status = "pass"
    elif pct >= 0.30:
        status = "partial"
    else:
        status = "fail"
    priority = result["impact"] * (6 - result["complexity"])
    return {"id": result["id"], "module": result["module"],
            "status": status, "points": got, "weight_total": total,
            "impact": result["impact"], "complexity": result["complexity"],
            "priority": priority, "checks": result["checks"],
            "skipped_deep": any(c["weight"] == 0 for c in result["checks"])}


def gaps_of(mod):
    return [c for c in mod["checks"] if not c["pass"] and c["weight"] > 0]


def counted(mods):
    """Weighted (points, total) excluding blocked modules.

    A blocked module's probes ran with a browser UA — their points describe
    what a browser sees, not what an agent can reach. Counting them would
    let file-presence checks mask the WAF wall, which is the exact failure
    the r1 pre-flight exists to catch.
    """
    live = [m for m in mods if m["status"] != "blocked"]
    return (sum(m["points"] for m in live),
            sum(m["weight_total"] for m in live))


def render_report(origin, mods, deep, blocker):
    got, total = counted(mods)
    pct = int(round(100 * got / total)) if total else 0
    counts = {s: sum(1 for m in mods if m["status"] == s)
              for s in ("pass", "partial", "fail", "blocked")}
    today = datetime.date.today().isoformat()

    lines = []
    lines.append("# Agentic Commerce Readiness — {}".format(origin))
    lines.append("")
    lines.append("**Score {} / {} ({}%)** · {} Pass · {} Partial · {} Fail{} · {}{}".format(
        got, total, pct, counts["pass"], counts["partial"], counts["fail"],
        " · {} Blocked".format(counts["blocked"]) if counts["blocked"] else "",
        today, "" if deep else " · shallow mode (rerun with --deep for POST probes)"))
    lines.append("")

    # Headline — story, not findings.
    stage = ("agent-ready foundations" if pct >= 70
             else "partially agent-ready" if pct >= 35
             else "not yet visible to commerce agents")
    lines.append("> **Headline.** This site is {} ({}%). ".format(stage, pct)
                 + ("Agent fetchers are being blocked at the door — fixing access "
                    "unlocks every other module. " if blocker else "")
                 + "Each gap below maps to a skill in this marketplace that closes it.")
    lines.append("")

    # Action plan: failing/partial modules by priority, deps first (r1 gates all).
    plan = sorted([m for m in mods if m["status"] in ("fail", "partial", "blocked")],
                  key=lambda m: (m["id"] != "r1", -m["priority"]))
    if plan:
        lines.append("## Action plan — do in order")
        lines.append("")
        lines.append("| # | Module | Status | Top gap | Fix with |")
        lines.append("|---|--------|--------|---------|----------|")
        for i, m in enumerate(plan, 1):
            gs = gaps_of(m)
            top = gs[0] if gs else None
            lines.append("| {} | {} {} | {} {}/{} | {} | `{}` |".format(
                i, m["id"], m["module"], STATUS_ICON[m["status"]],
                m["points"], m["weight_total"],
                top["name"] if top else "—",
                (top.get("fix_skill") or "—") if top else "—"))
        lines.append("")

    if blocker:
        lines.append("## Cross-cutting blocker — agent fetchers blocked")
        lines.append("")
        lines.append("Agent user-agents are challenged or blocked at the WAF/CDN. "
                     "Every module that needs an agent to fetch a real response is "
                     "gated on this. Allow the agent/fetcher bot category in your "
                     "WAF before acting on anything else. Blocked modules' probe "
                     "evidence below was gathered with a browser UA and is "
                     "**excluded from the score** — it shows what would be "
                     "reachable once the wall comes down, not what agents can "
                     "reach today.")
        lines.append("")

    lines.append("## Findings")
    lines.append("")
    lines.append("| ID | Module | Score | Sub-check evidence |")
    lines.append("|----|--------|------:|--------------------|")
    for m in mods:
        ev = "; ".join(
            "{}[{}] {}".format("" if c["pass"] else "✗ ", c["weight"], c["name"])
            for c in m["checks"] if c["weight"] > 0)
        score_cell = ("{} {}/{} (not counted)".format(
                          STATUS_ICON[m["status"]], m["points"], m["weight_total"])
                      if m["status"] == "blocked"
                      else "{} {}/{}".format(STATUS_ICON[m["status"]],
                                             m["points"], m["weight_total"]))
        lines.append("| {} | {} | {} | {} |".format(
            m["id"], m["module"], score_cell, ev))
    lines.append("")

    # Gap → skill map: the marketplace tie-in.
    rows = []
    for m in mods:
        for c in gaps_of(m):
            if c.get("fix_skill"):
                rows.append((m["id"], c["name"], c["fix_skill"]))
    if rows:
        lines.append("## Your gaps → the skills that close them")
        lines.append("")
        lines.append("Install the plugin, invoke the skill, and it fetches the live "
                     "spec before writing any code.")
        lines.append("")
        lines.append("| Gap | Skill |")
        lines.append("|-----|-------|")
        for mid, name, skill in rows:
            lines.append("| {} — {} | `/{}` |".format(mid, name, skill))
        lines.append("")

    lines.append("## Methodology")
    lines.append("")
    lines.append("Six probe scripts (`scripts/probe_*.py`, stdlib-only Python) gather "
                 "HTTP evidence; rubrics in `audit/` define the weighted sub-checks. "
                 "Conclusions come from response bytes only — a probe that cannot "
                 "complete fails its sub-check with the reason recorded. "
                 "Pass ≥ 85% · Partial ≥ 30% · priority = impact × (6 − complexity). "
                 "Machine-readable breakdown: `score.json`.")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Agentic commerce readiness audit — probe, score, report")
    ap.add_argument("url", help="site URL or bare host")
    ap.add_argument("--deep", action="store_true",
                    help="enable POST probes (demo checkout/ask calls; opt-in "
                         "because created sessions can trigger side effects "
                         "on live merchants)")
    ap.add_argument("--out", default="report", help="output directory (default: report/)")
    ap.add_argument("--modules", default="all",
                    help="comma-separated module ids (r1..r6) or 'all'")
    ap.add_argument("--json-only", action="store_true",
                    help="print score.json to stdout, write no files")
    args = ap.parse_args()
    force_utf8_stdout()  # Windows consoles default to cp1252

    origin, host = origin_of(args.url)
    wanted = list(MODULES) if args.modules == "all" else [
        m.strip() for m in args.modules.split(",") if m.strip() in MODULES]
    if not wanted:
        print("no valid modules in --modules", file=sys.stderr)
        return 2

    sys.stderr.write("Probing {} — modules: {}{}\n".format(
        origin, ",".join(wanted), " (deep)" if args.deep else ""))

    results = {}
    with cf.ThreadPoolExecutor(max_workers=len(wanted)) as ex:
        futs = {ex.submit(MODULES[m], origin, host, args.deep): m for m in wanted}
        for fut in cf.as_completed(futs):
            m = futs[fut]
            try:
                results[m] = fut.result()
            except Exception as e:  # a probe must never sink the audit
                results[m] = {"probe": m, "id": m, "module": m, "origin": origin,
                              "impact": 3, "complexity": 3, "checks": [
                                  {"name": "probe crashed", "pass": False,
                                   "weight": 1, "evidence": repr(e)}]}
            sys.stderr.write("  {} done\n".format(m))

    blocker = bool(results.get("r1", {}).get("blocker"))
    mods = []
    for m in wanted:
        blocked = blocker and m in ("r2", "r3", "r4", "r5")
        mods.append(score_module(results[m], blocked=blocked))

    got, total = counted(mods)
    payload = {
        "host": host,
        "tested_at": datetime.datetime.now(datetime.timezone.utc)
                     .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "deep": args.deep,
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

    if args.json_only:
        print(json.dumps(payload, indent=2))
        return 0

    os.makedirs(args.out, exist_ok=True)
    score_path = os.path.join(args.out, "score.json")
    report_path = os.path.join(args.out, "READINESS.md")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(render_report(origin, mods, args.deep, blocker))

    print("Score {}/{} ({}%) — report: {}  data: {}".format(
        got, total, payload["scoreboard"]["weighted"]["pct"],
        report_path, score_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
