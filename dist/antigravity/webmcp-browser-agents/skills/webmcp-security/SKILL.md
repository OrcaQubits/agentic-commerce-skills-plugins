---
name: webmcp-security
description: >
  Implement WebMCP security best practices — permission model, data
  minimization, honest descriptions, input validation, fingerprinting
  prevention, and fraud mitigation. Use when auditing or hardening WebMCP tool
  implementations.
---

# WebMCP Security

## Before writing code

**Fetch live docs**:
1. Fetch `https://webmachinelearning.github.io/webmcp/` for security-related sections of the specification
2. Web-search `webmcp security privacy permission model` for security architecture details
3. Web-search `site:github.com mcp-b security` for polyfill security guidelines
4. Web-search `webmcp fingerprinting data minimization` for privacy best practices

## Conceptual Architecture

### Permission-First Design

WebMCP's security model is **permission-first**:
1. The site defines what tools exist (tool registration)
2. The browser mediates — prompts the user before allowing agent invocation
3. The user grants or denies permission per tool or per session
4. Annotations (`destructiveHint`, `readOnlyHint`) inform browser permission decisions
5. Tools execute within the page's secure context (same-origin, HTTPS required)

### Threat Model

| Threat | Description | Mitigation |
|--------|-------------|------------|
| **Deceptive tool descriptions** | Tool named "addToCart" actually charges the user | Honest descriptions; browser/audit verification |
| **Agent hallucination** | Agent calls wrong tool or passes bad parameters | Schema validation; user confirmation for high-risk tools |
| **Over-parameterization** | Tool requests excessive personal data from agent | Data minimization; server-side session lookups |
| **Fingerprinting** | Tool parameters reveal user attributes | Minimal input schemas; avoid asking for identity data |
| **Rapid automation abuse** | Agent makes rapid repeated transactions | Server-side rate limiting; CAPTCHA for bulk operations |
| **Cross-origin data leak** | Tool exposes data from another origin | Same-origin enforcement; browser sandboxing |
| **Session hijacking** | Tool's session exploited by malicious agent | Standard CSRF protection; secure cookie flags |
| **Prompt injection** | Malicious content in tool results manipulates agent | Output sanitization; structured JSON responses |

### Honest Descriptions

Tool descriptions are a critical security surface:
- Agents rely on descriptions to decide which tools to use
- A malicious site could expose `addToCart` that actually calls `placeOrder`
- Descriptions MUST accurately reflect what the tool does
- Include side effects: "Adds item to cart AND applies default shipping"
- Include limitations: "Only works for in-stock items"

### Data Minimization

Minimize the data tools request from agents:

**Bad — over-parameterized:**
```js
// DON'T: asking agent to supply user's personal data
inputSchema: {
  properties: {
    userId: { type: "string" },
    email: { type: "string" },
    shippingAddress: { type: "object" },
    creditCardLast4: { type: "string" }
  }
}
```

**Good — minimal, server-side lookup:**
```js
// DO: only take what's needed, look up user data server-side
inputSchema: {
  properties: {
    productId: { type: "string" },
    quantity: { type: "integer" }
  }
}
// execute callback uses session cookies to identify the user server-side
```

### Input Validation

Always validate tool input:
- JSON Schema validation happens at the browser level before `execute` is called
- Add server-side validation in your API endpoints — don't trust client-side schema alone
- Sanitize string inputs to prevent XSS or injection attacks
- Validate IDs against actual database records
- Reject unexpected fields or overly long values

### Rate Limiting

Protect against agent abuse:
- Implement server-side rate limits on APIs called by tools
- Limit transactions per session (e.g., max 5 orders per hour)
- Use CAPTCHA or user interaction for bulk operations
- Monitor for anomalous patterns (rapid-fire tool calls)

### Audit Logging

Log all agent interactions:
- Tool name, input parameters (sanitized), timestamp
- User session identity
- Whether user interaction was requested and the user's response
- Tool result status (success, failure, canceled)
- Agent identifier if available

### Liability Considerations

- If an agent mistakenly places an order, who is responsible?
- WebMCP's human-in-the-loop design and confirmation prompts help
- Always require `requestUserInteraction` for financial actions
- Log user approvals as evidence of consent
- Consider displaying pending agent actions as reversible/draft before committing

### Best Practices Checklist

- [ ] All tool descriptions accurately match behavior
- [ ] No sensitive data in input schemas (no passwords, SSNs, full card numbers)
- [ ] `destructiveHint` set on all financial/irreversible tools
- [ ] `requestUserInteraction` used for purchases, deletions, and account changes
- [ ] Server-side input validation on all API endpoints
- [ ] Rate limiting on APIs called by tools
- [ ] Audit logging for all tool invocations
- [ ] CSRF tokens included in POST requests
- [ ] Sensitive tools only registered for authenticated users
- [ ] `clearContext()` called on logout

Fetch the specification for the latest security requirements, permission model details, and browser enforcement behavior before auditing.
