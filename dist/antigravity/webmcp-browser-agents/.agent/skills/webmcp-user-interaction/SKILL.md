---
name: webmcp-user-interaction
description: >
  Implement human-in-the-loop flows with requestUserInteraction() —
  confirmation dialogs, approval workflows, and user prompts during tool
  execution. Use when building tools that require user consent before performing
  actions.
---

# WebMCP User Interaction (Human-in-the-Loop)

## Before writing code

**Fetch live docs**:
1. Fetch `https://webmachinelearning.github.io/webmcp/` for the `ModelContextClient` and `requestUserInteraction` specification
2. Web-search `webmcp requestUserInteraction ModelContextClient specification` for the callback API
3. Web-search `site:developer.chrome.com webmcp user interaction confirmation` for Chrome implementation guidance
4. Web-search `webmcp human-in-the-loop agent confirmation` for community patterns

## Conceptual Architecture

### What requestUserInteraction Does

`client.requestUserInteraction(callback)` is a method on the `ModelContextClient` object passed to every tool's `execute` callback. It pauses tool execution, hands control to the user (via a site-provided UI), and resumes when the user responds.

This is the primary mechanism for **human-in-the-loop** approval in WebMCP.

### Why It Matters

AI agents can make mistakes — hallucinate, misinterpret instructions, or select the wrong option. For irreversible actions (purchases, account changes, data deletion), requiring user confirmation prevents costly errors. WebMCP's design explicitly accommodates shared-context interactions where the user and agent collaborate.

### Flow

```
Agent calls tool → execute(input, client) starts
  → Tool calls client.requestUserInteraction(callback)
    → Browser pauses tool execution
    → Site shows UI to the user (modal, banner, etc.)
    → User approves or rejects
    → callback resolves with user's response
  → Tool resumes with user's answer
  → Tool returns result to agent
```

### When to Use requestUserInteraction

| Action | User Interaction? | Rationale |
|--------|:--:|-----------|
| Search products | No | Read-only, no side effects |
| View product details | No | Read-only |
| Add to cart | Maybe | Low risk, but could confirm for expensive items |
| Apply coupon | No | Easily reversible |
| Place order / checkout | **Yes** | Irreversible, involves payment |
| Delete account | **Yes** | Destructive, irreversible |
| Change subscription plan | **Yes** | Financial commitment |
| Initiate return | **Yes** | Starts a process that may be hard to undo |
| Update shipping address | Maybe | Depends on timing relative to order |

### Implementation Pattern

```js
navigator.modelContext.registerTool({
  name: "placeOrder",
  description: "Complete the purchase with the items in the cart",
  inputSchema: { type: "object", properties: {} },
  annotations: { destructiveHint: true },
  async execute(input, client) {
    // 1. Gather order summary
    const summary = await fetch("/api/cart/summary").then(r => r.json());

    // 2. Ask user to confirm
    const approved = await client.requestUserInteraction((resolve) => {
      // Show a confirmation UI — this is your site's custom modal/dialog
      showOrderConfirmation(summary, (userApproved) => {
        resolve(userApproved);
      });
    });

    // 3. Proceed or cancel based on user response
    if (!approved) {
      return { status: "canceled", message: "User declined the order" };
    }

    // 4. Execute the order
    const result = await fetch("/api/orders", { method: "POST" });
    return await result.json();
  }
});
```

### UI Design for Confirmation

The site controls how the confirmation UI looks. Common patterns:
- **Modal dialog** — "AI wants to place an order for $127.50. Allow?"
- **Inline banner** — Highlighted section showing pending agent action
- **Slide-over panel** — Side panel with order details and approve/reject buttons
- **Toast with action** — Brief notification with "Approve" / "Cancel" buttons

### Multi-Step Interactions

A tool can call `requestUserInteraction` multiple times:
1. First interaction: "Select a shipping option" → user picks Express
2. Second interaction: "Confirm order total of $142.30?" → user approves
3. Tool proceeds with both choices

### Best Practices

- Always show the user what the agent is about to do, not just "Allow action?"
- Include relevant details (amounts, item names, addresses) in the confirmation UI
- Provide a clear "Cancel" option that returns a structured cancellation response to the agent
- Keep the interaction UI accessible (keyboard navigable, screen reader compatible)
- Time out long-running interactions — if the user doesn't respond within a reasonable period, cancel gracefully
- Log user approvals and rejections for audit trails

Fetch the specification for exact `requestUserInteraction` callback signature, return types, and browser behavior before implementing.
