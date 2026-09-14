# Readiness rubrics

Machine-testable companions to the probe scripts. One file per module
(`r1.md` … `r6.md`). The `readiness-audit` skill loads these to interpret
probe output and explain scores; the scripts in `../scripts/` are the
executable source of truth for probes and weights.

## Consistency contract

Three layers must agree on module ids, sub-check names, and weights:

```
scripts/probe_<module>.py   ←  executable source of truth (probes + weights)
audit/r{N}.md               ←  documents the same sub-checks, same weights
report READINESS.md         ←  renders them (generated, never hand-edited)
```

When a probe script gains, drops, or re-weights a sub-check, update the
matching rubric file in the same commit. The rubric may explain *why* a
check exists and how to fix a failure; it may never disagree with the
script about *what* is checked or its weight.

## File format

```markdown
---
id: r{N}
title: <short module name>
impact: <1-5>          # how much agent-commerce outcome hinges on this
complexity: <1-5>      # how hard the typical fix is
script: probe_<module>.py
weight_total: <shallow total> [deep: <deep total>]
---

# r{N} — <title>

## What this measures        (2-4 sentences, why an agent cares)
## Sub-checks                (table: name | pass when | weight | fix skill)
## N/A condition             (when the module genuinely doesn't apply)
## Fix guidance              (which plugin skills close each gap, in order)
```

## Scoring (all modules)

- **Pass** — points ≥ 85% of weight_total
- **Partial** — ≥ 30%
- **Fail** — < 30%
- **Blocked** — r1 found agent fetchers blocked; r2–r5 are gated. Their probe evidence (gathered with a browser UA) is reported but **excluded from the weighted score** — it shows what becomes reachable once the wall comes down
- **priority = impact × (6 − complexity)** — higher = fix first

## Evidence rules (binding)

- A conclusion comes from **HTTP response bytes only** — never from a repo,
  a marketing page, or an assumption about the platform.
- A probe that cannot complete (timeout, auth wall, JS-only render)
  **fails** its sub-check, with the reason in the evidence string.
- Ambiguous responses get the conservative reading: a 400 naming a
  protocol's field proves the endpoint validates a schema, not that the
  protocol is implemented.
- Weight-0 rows are skipped deep probes — they never lower a shallow score.
