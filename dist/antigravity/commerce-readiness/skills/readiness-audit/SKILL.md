---
name: readiness-audit
description: >
  Run the full agentic commerce readiness audit against a live site — six probe
  modules (Reachable, Discoverable, Comprehensible, Transactable, Payable,
  Trustworthy), weighted scoring, and a report that maps every gap to the
  marketplace skill that closes it. Use when a user asks "is my store
  agent-ready", "audit my site for agentic commerce", or "what do I need for
  ACP/UCP/agents to buy from us".
---

# Agentic Commerce Readiness Audit

You score a live site's readiness for AI-agent commerce using the executable
probes in this plugin, then turn every gap into a concrete fix wired to the
skills in this marketplace.

## Prerequisites

Python 3.8+ on PATH (`python3` or `python`). The probes are **stdlib-only**
— no pip installs. If Python is missing, tell the user how to install it for
their platform and stop; don't degrade to guessing.

## Inputs

Ask for these if not provided:

- **URL** — required. `https://shop.example.com` or a bare host.
- **Deep mode** — opt-in. Default probes send GET/OPTIONS (plus MCP
  `tools/list`, a pure read). `--deep` adds POST probes: a demo-SKU checkout
  create against ACP and UCP, NLWeb `/ask`, and a delegate_payment
  validation call. These are discovery-shaped, but on a live merchant a
  created session can trigger inventory holds or abandoned-cart emails —
  **ask before enabling deep mode**, and prefer a staging host.
- **Scope** — optional: `all` (default) or module ids `r1,r2,r4`.

## Process

### 1. Run the audit

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/readiness_audit.py" <URL> --out report/
# deep, with user consent:
python "${CLAUDE_PLUGIN_ROOT}/scripts/readiness_audit.py" <URL> --deep --out report/
```

Outside Claude Code — or on a converted platform bundle where
`${CLAUDE_PLUGIN_ROOT}` is not set — substitute the path to the
`commerce-readiness` plugin directory; the scripts have no other
dependency on the harness.

Emit one progress line before running ("Probing <host> — 6 modules…") and
one after ("Scored N/W — writing report/READINESS.md"). The runner executes
all modules in parallel; a full shallow run takes under a minute.

For a single module, run its probe directly:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/probe_transact.py" <URL> --json
```

### 2. Interpret — with the rubrics, not your impressions

Read `report/score.json`. For any module you need to explain, read its
rubric in `audit/r{N}.md` — the rubric documents what each sub-check means,
its N/A condition, and the fix path. The scripts are the source of truth
for weights; the rubrics for meaning.

**Evidence rules (binding):**

- Scores come from HTTP responses only. Never upgrade a Fail because the
  user says the feature exists, the platform "should" provide it, or a repo
  file suggests it — a file in a repo is not a URL that serves.
- A probe that couldn't complete has already Failed its sub-check with the
  reason recorded. Surface the reason; offer a re-run, don't hand-wave.
- If r1 found agent fetchers blocked, r2–r5 report **Blocked** — lead with
  the WAF fix and do not present the other modules as independent problems.
- Never fabricate or round up a score, and never claim a Pass means agents
  *will* buy — the audit measures capability, not adoption.

### 3. Present

Show the user, in this order:

1. **Headline** — score, stage, and the single most valuable next action.
   Two sentences; no endpoints or file paths here.
2. **Action plan** — from the report, ordered: r1 blocker first if present,
   then by `priority = impact × (6 − complexity)`.
3. **Gap → skill map** — the report's table. For each gap the user wants to
   close, name the exact skill (e.g. `/acp-agentic-commerce:acp-setup`) and
   offer to invoke it. Every fixing skill fetches the live spec before
   writing code, so the fix is always against the current protocol version.

The full findings table stays in `report/READINESS.md`; don't paste it into
chat unless asked.

### 4. Fix (only when asked)

When the user picks a gap, invoke the mapped skill and implement the fix in
their codebase. After each fix, re-run **only that module's probe** to
confirm the sub-check flipped:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/probe_discovery.py" <URL> --json
```

One fix, one re-probe, one confirmation. Don't re-run the whole audit per
fix; run it once at the end to show the before/after score.

## Scoring model (for reference)

Pass ≥ 85% of module weight · Partial ≥ 30% · Fail < 30% · Blocked when r1
gates it · N/A per the rubric's condition. Details: `audit/README.md`.
