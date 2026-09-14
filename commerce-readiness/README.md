# Commerce Readiness — Agentic Commerce Gap Audit

**Is your store ready for AI agents to buy from it?** This plugin answers
that with executable evidence, not opinion: six stdlib-only Python probes
score a live site on the full agentic commerce stack, and every gap maps to
the skill in this marketplace that closes it.

```
python commerce-readiness/scripts/readiness_audit.py https://shop.example.com --out report/
```

```
Score 18/40 (45%) · 1 Pass · 3 Partial · 2 Fail
r1 Reachable       PASS     7/7   agents can fetch the site
r2 Discoverable    PARTIAL  4/8   UCP profile live · no ACP doc · no agent card
r3 Comprehensible  PASS     7/7   ProductGroup JSON-LD with price+availability
r4 Transactable    PARTIAL  2/5   MCP tools/list answers · no REST checkout
r5 Payable         PARTIAL  2/6   payment handlers declared · no delegate_payment
r6 Trustworthy     PARTIAL  4/7   OAuth discovery live · no signing keys
```

## The six modules

| ID | Module | Question it answers | Weight |
|----|--------|--------------------|-------:|
| r1 | **Reachable** | Can an agent's fetcher get past your WAF at all? | 7 |
| r2 | **Discoverable** | Can it find your UCP/ACP/A2A discovery docs, llms.txt, feed? | 8 |
| r3 | **Comprehensible** | Does your product page carry JSON-LD an agent can price from? | 7 |
| r4 | **Transactable** | Do your checkout surfaces (ACP, UCP, MCP, NLWeb) answer? | 5 (12 deep) |
| r5 | **Payable** | Payment handlers, delegated payment, AP2, HTTP 402? | 6 |
| r6 | **Trustworthy** | OAuth discovery, signing keys, TLS, structured errors? | 7 |

Scoring: **Pass** ≥ 85% · **Partial** ≥ 30% · **Fail** below · **Blocked**
when r1 finds agent fetchers walled out (then r2–r5 are gated on the WAF
fix). Priority = `impact × (6 − complexity)`.

## Structure

```
commerce-readiness/
├── agents/readiness-expert.md        # Orchestrating subagent
├── skills/
│   ├── readiness-audit/              # Full audit: probe → score → report → map
│   ├── readiness-quick-check/        # 60-second triage (r1 + r2 only)
│   └── readiness-fix-plan/           # score.json → sequenced, stack-aware plan
├── audit/                            # Rubrics: what each sub-check means + fix path
│   ├── README.md                     #   format + consistency contract + evidence rules
│   └── r1.md … r6.md
├── scripts/                          # Executable probes — Python 3.8+, stdlib only
│   ├── lib/probe.py                  #   bounded HTTP, JSON-LD extractor, UCP profile parser
│   ├── probe_agent_access.py         #   r1 — agent-UA reachability vs browser baseline
│   ├── probe_discovery.py            #   r2 — /.well-known/{ucp,acp.json,agent-card.json}, llms.txt, feed
│   ├── probe_catalog.py              #   r3 — Product/ProductGroup JSON-LD, Offer/price/availability
│   ├── probe_transact.py             #   r4 — ACP + UCP checkout, MCP tools/list, NLWeb /ask
│   ├── probe_payments.py             #   r5 — handlers, delegate_payment, AP2 signal, HTTP 402
│   ├── probe_trust.py                #   r6 — OAuth discovery, signing keys, TLS, error shape
│   ├── readiness_audit.py            #   runner: parallel probes → READINESS.md + score.json
│   ├── mcp_server.py                 #   MCP endpoint exposing the audit as callable tools
│   ├── test_scoring.py               #   offline unit tests (scoring, surfaces, parsers) — no network
│   └── test_mcp_server.py            #   offline MCP integration tests (fixture storefront, SSRF, deep refusal)
└── evals/readiness.json              # Behavior evals incl. refusal cases
```

## Design principles

- **Evidence over impressions.** Every score derives from HTTP response
  bytes. A repo file, platform default, or vendor assurance is a fix hint,
  never a Pass. A probe that can't complete *fails* with the reason
  recorded — there is no Unknown.
- **Shape over status.** A checkout stub answering 200 with a non-canonical
  body is not ready — agents parse fields. Deep mode validates ACP's
  canonical CheckoutSession (`object`, status enum, top-level
  `line_items[]`, `totals`) and UCP's status enum.
- **Safe by default.** Shallow mode sends GET/OPTIONS plus MCP `tools/list`
  (a pure read). `--deep` — which POSTs demo-SKU checkout creates — is
  opt-in, idempotency-keyed, and should target staging. Never run deep
  against a site you don't operate.
- **Zero dependencies.** Pure Python stdlib. No pip install, works on a
  fresh Windows/macOS/Linux machine.
- **The marketplace is the fix.** Every failing sub-check carries a
  `fix_skill` — the audit is the front door; the other 15 plugins are the
  toolbox. Each fixing skill fetches the live protocol spec before writing
  code.

## Usage with Claude Code

```bash
claude --plugin-dir "commerce-readiness"
```

| Skill | Invoke | Purpose |
|-------|--------|---------|
| **readiness-audit** | auto, or `/commerce-readiness:readiness-audit` | Full six-module audit with report + gap map |
| **readiness-quick-check** | auto | 60-second r1+r2 triage, safe on any public site |
| **readiness-fix-plan** | auto | Turn score.json into a sequenced, stack-aware plan |

Example prompts:

```
Is https://mystore.com ready for agentic commerce?
Quick-check https://competitor.com — can agents even see them?
Turn report/score.json into a fix plan; our stack is Next.js + Medusa.
Fix the ACP discovery gap from the audit, then re-probe.
```

## Serve the audit as an MCP endpoint

Any MCP client — Claude, ChatGPT, Gemini, another agent — can call the
audit as a tool. The server is the same stdlib-only Python as the probes:

```bash
python scripts/mcp_server.py --host 0.0.0.0 --port 8765 --path /mcp
```

```bash
curl -sS -X POST localhost:8765/mcp -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"readiness_quick_check","arguments":{"url":"https://shop.example.com"}}}'
```

Tools: **`readiness_audit`** (url, modules?, deep?) and
**`readiness_quick_check`** (url) — results arrive as `structuredContent`
(the score.json payload) plus a one-line text summary. Written against the
`2026-07-28` stateless MCP revision; also answers handshake-era
`initialize` so older clients work.

**Safe by default, because it fetches caller-supplied URLs from wherever
it runs:**

- **SSRF guard** — targets resolving to loopback/private/link-local/
  metadata ranges are refused (`MCP_ALLOW_PRIVATE=1` overrides, for local
  testing only)
- **Deep mode refused** unless the operator sets `READINESS_ALLOW_DEEP=1`
  — a public endpoint must not let anonymous callers aim checkout-creating
  probes at third parties
- **Bounded concurrency** (`MAX_CONCURRENT_AUDITS`, default 4); put rate
  limiting and TLS on the fronting proxy

Behind nginx, this is the location block (adjust the upstream):

```nginx
location = /mcp {
    limit_req zone=web_limit burst=20 nodelay;
    proxy_pass http://readiness-mcp:8765/mcp;
    proxy_set_header Host $host;
    proxy_read_timeout 120s;   # a full shallow audit can take ~60s
}
```

The endpoint passes this plugin's own r4 sub-check ("MCP endpoint answers
tools/list") — the audit and the server dogfood each other.

## Standalone CLI (no Claude required)

```bash
# full audit → report/READINESS.md + report/score.json
python scripts/readiness_audit.py https://shop.example.com --out report/

# deep mode (POST probes; see safety note) against staging
python scripts/readiness_audit.py https://staging.shop.example.com --deep

# one module, machine-readable
python scripts/probe_discovery.py shop.example.com --json

# scoped run
python scripts/readiness_audit.py shop.example.com --modules r1,r2 --json-only
```

## License

MIT
