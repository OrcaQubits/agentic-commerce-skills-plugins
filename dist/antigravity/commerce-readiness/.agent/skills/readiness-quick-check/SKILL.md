---
name: readiness-quick-check
description: >
  Sixty-second agentic commerce triage — probe just agent access (r1) and
  protocol discovery (r2) to answer "can agents reach us, and can they tell we
  do commerce?". Use for a first look, a sales call, or checking a competitor
  before committing to the full readiness-audit.
---

# Readiness Quick Check

The two questions that decide everything else, in under a minute:

1. **Can an agent get in?** (r1 — WAF/robots posture toward agent fetchers)
2. **Can it tell you do commerce?** (r2 — UCP/ACP/A2A discovery docs,
   llms.txt, feed)

Everything downstream — catalog, checkout, payment — is moot until both
answer yes. This check sends only GET requests; it is safe against any
site, including ones you don't own.

## Run

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/readiness_audit.py" <URL> --modules r1,r2 --json-only
```

## Present

Three lines, no more:

- **Access**: open / blocked — name which fetcher UAs were challenged.
- **Discovery**: which protocols are advertised (UCP, ACP, A2A, llms.txt,
  feed) — verbatim from the evidence, e.g. "UCP profile live, version
  2026-08-25; no ACP doc; no agent card".
- **Verdict + next step**: "agents can't see you — start with
  `/commerce-readiness:readiness-audit` for the full picture", or the
  single discovery doc that would move them most
  (`/ucp-agentic-commerce:ucp-setup` or `/acp-agentic-commerce:acp-setup`).

Evidence rules apply even at this size: report what the probes observed,
never what the platform "should" provide. If both modules pass, say so and
offer the full audit for the transactability and payment layers — a
passing quick check is a door, not a score.
