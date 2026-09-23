---
name: mpp-session-flow
description: "Implement MPP session-based streaming payment flows — authorize-once pay-as-you-go patterns for continuous data feeds, per-token billing, and micropayment aggregation. Use when building streaming APIs or services that charge incrementally, implementing pay-per-use or metered billing, or adding usage-based pricing to an API."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# MPP Session Flow (Streaming Payments)

## Before writing code

**Fetch live docs**:
1. Fetch `https://www.npmjs.com/package/mppx` for the session middleware API and payment channel configuration
2. Fetch `https://paymentauth.org/` for the canonical session intent specification
3. Web-search `mpp session streaming micropayments payment channel` for session implementation patterns

## Session Lifecycle

```
Open → Authorize → Active → Refill (optional) → Close → Settled
```

1. **Open** — Client sends initial request; server returns 402 with session challenge
2. **Authorize** — Client authorizes spending cap (e.g., 10,000 units)
3. **Active** — Client makes requests; each deducts from the cap
4. **Refill** — Client can extend the cap before it runs out
5. **Close** — Either party closes; final settlement happens on-chain
6. **Settled** — Single on-chain transaction for the total consumed amount

## Server-Side Implementation

```typescript
import { mppx } from "mppx";

// Protect a streaming endpoint with session-based payment
app.get("/api/stream", mppx.session({ maxAmount: "10000" }), async (c) => {
  return c.json({ data: "streaming content" });
});

// Metered endpoint — charge per unit consumed
app.post("/api/inference", mppx.session({ maxAmount: "50000" }), async (c) => {
  const result = await runInference(c.req.body);
  const tokensUsed = result.usage.totalTokens;
  await c.mpp.charge(tokensUsed);
  return c.json({ result: result.output, charged: tokensUsed });
});
```

## Client-Side Implementation

```typescript
import { MppClient } from "mppx/client";

const client = new MppClient({ wallet: agentWallet });

// Open a session with a spending cap
const session = await client.openSession("https://api.example.com/api/stream", {
  spendingCap: 10000,
});

// Make metered requests — each deducts from the cap
const response = await session.fetch("/api/inference", {
  method: "POST",
  body: JSON.stringify({ prompt: "Hello" }),
});

// Monitor remaining balance
console.log(`Remaining: ${session.remainingBalance}`);

// Extend the cap before it runs out
if (session.remainingBalance < 1000) {
  await session.refill(5000);
}

// Close the session — triggers final settlement
await session.close();
```

## Handling Cap Exhaustion

```typescript
// Server: return 402 when cap is exhausted
app.use("/api/*", async (c, next) => {
  try {
    await next();
  } catch (err) {
    if (err.code === "CAP_EXHAUSTED") {
      return c.json({ error: "spending_cap_exhausted", remaining: 0 }, 402);
    }
    throw err;
  }
});

// Client: handle 402 by opening a new session
async function fetchWithRetry(session, url, opts) {
  const res = await session.fetch(url, opts);
  if (res.status === 402) {
    const newSession = await client.openSession(url, { spendingCap: 10000 });
    return newSession.fetch(url, opts);
  }
  return res;
}
```

## Verification Workflow

1. Start server with session middleware enabled
2. Open a session from the client — verify 402 challenge is returned, then authorization succeeds
3. Make a metered request — verify balance decreases by the correct amount
4. Exhaust the cap — verify server returns 402
5. Refill or open a new session — verify requests resume
6. Close the session — verify settlement transaction is recorded

## Best Practices

- Set reasonable default spending caps (not too high for safety, not too low for UX)
- Implement cap exhaustion warnings before the cap runs out
- Log metering data for billing reconciliation
- Handle session interruptions gracefully (network drops, server restarts)
- Implement session resumption where possible

Fetch the latest mppx SDK documentation and MPP specification for exact session API, payment channel mechanics, and configuration options before implementing.
