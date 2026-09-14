---
name: readiness-fix-plan
description: >
  Turn an existing readiness audit (report/score.json) into a sequenced,
  stack-aware fix plan — each gap mapped to the marketplace skill that closes
  it, ordered by dependency and priority, with effort estimates. Use after
  readiness-audit when the user says "make me a plan", "what do we fix first",
  or wants issues for their tracker.
---

# Readiness Fix Plan

You turn a `score.json` from `readiness-audit` into a plan a team can
execute. The audit says *what* is broken; you decide *order*, *owner-sized
chunks*, and *which skill does the work*.

## Inputs

- **`report/score.json`** — required. If absent, run `readiness-audit`
  first (or ask the user where their score.json lives).
- **Repo path** — optional but changes the quality of the plan: with it you
  can name the actual framework and files; without it, hints stay generic.
- **Format** — plan in chat (default), and/or one issue block per gap
  ready to paste into a tracker.

## Building the plan

1. **Read every module** in score.json — statuses, failing sub-checks,
   evidence strings, `fix_skill` fields. The evidence strings are verbatim
   probe output; quote them, don't paraphrase.
2. **Order by dependency first, priority second:**
   - An r1 blocker is always step 1 — nothing else is testable until agents
     can fetch.
   - Discovery (r2) before transactability (r4): an endpoint nobody can
     find might as well not exist. Payment (r5) after checkout (r4).
   - Within a tier, sort by `priority` (already computed:
     `impact × (6 − complexity)`).
3. **Detect the stack** if a repo path was given (package.json / Gemfile /
   composer.json / requirements.txt), and route platform-shaped gaps to the
   platform plugin: Product JSON-LD on a WooCommerce site is
   `woocommerce-commerce:woo-catalog`, on Magento
   `magento2-commerce:magento-catalog` — the generic `fix_skill` in
   score.json is the fallback, not the final answer.
4. **Size each step** — small (config/file drop: discovery docs, robots,
   llms.txt), medium (structured data, OAuth wiring), large (checkout
   endpoint, delegated payment). Flag the larges as projects, not tasks.
5. **State the projected score** after the small+medium steps, computed
   from the actual weights in score.json — never estimated.

## Plan format

| # | Fix | Module | Skill to invoke | Size | +pts |
|---|-----|--------|-----------------|------|-----:|

Follow the table with one short paragraph per **large** item explaining
what it involves and what to read first (e.g. delegated payment → read
`ap2-agentic-payments:ap2-agent-authorization` before designing).

**Issue blocks** (on request): title
`agentic-readiness: <sub-check> (<module id>)`, body = evidence verbatim +
fix steps + skill to invoke + re-probe command.

## Rules

- Never add gaps the audit didn't find, and never drop one silently — if
  you exclude a gap (e.g. MPP on a store that will never sell API access),
  say so and mark it deliberate.
- Don't promise score → revenue. The plan closes capability gaps; adoption
  is the merchant's traffic, catalog, and price doing their job.
- Verification is part of every step: each fix ends with its module's
  re-probe command, and the plan ends with one full re-audit.
