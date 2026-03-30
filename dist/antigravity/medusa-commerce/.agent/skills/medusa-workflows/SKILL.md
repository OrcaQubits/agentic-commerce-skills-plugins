---
name: medusa-workflows
description: >
  Build Medusa v2 workflows — steps with createStep, compensation/rollback,
  parallel execution, hooks for extending built-in workflows, and when
  conditions. Use when orchestrating multi-step operations.
---

# Medusa v2 Workflows

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/fundamentals/workflows` for workflow overview
2. Web-search `site:docs.medusajs.com createStep createWorkflow` for step and workflow API
3. Web-search `site:docs.medusajs.com workflow compensation rollback` for compensation patterns
4. Web-search `site:docs.medusajs.com workflow hooks` for extending built-in workflows
5. Web-search `site:docs.medusajs.com built-in workflows list` for available core workflows

## Workflow Concept

Workflows orchestrate multi-step, transactional operations in Medusa v2:
- Each step is an isolated, retryable unit of work
- Steps can define compensation (rollback) logic for failure recovery
- Workflows execute steps sequentially, in parallel, or conditionally
- Built-in workflows handle core commerce operations (cart, order, fulfillment)
- Custom workflows are invoked from API routes, subscribers, or scheduled jobs

## Step Lifecycle

| Phase | On Success | On Failure |
|-------|-----------|-----------|
| Step invoked | Execute function | — |
| Execute function | Proceed to next step | Trigger compensation |
| All steps done | Workflow complete | — |
| Compensation | Rollback completed steps in reverse order | Manual resolution |

## Creating Steps

### Step Definition Skeleton

```typescript
// Fetch live docs for createStep signature
import { createStep, StepResponse } from "@medusajs/framework/workflows-sdk"

const myStep = createStep("my-step", async (input, { container }) => {
  const service = container.resolve("my-module")
  const result = await service.createMyEntity(input)
  return new StepResponse(result, result.id) // data, compensationInput
})
```

### Compensation (Rollback)

```typescript
// Fetch live docs for compensation function signature
const myStep = createStep("my-step",
  async (input, { container }) => {
    return new StepResponse(result, result.id) // forward logic
  },
  async (compensationInput, { container }) => {
    // Rollback logic: undo what forward did
  })
```

## Creating Workflows

### Workflow Definition Skeleton

```typescript
// Fetch live docs for createWorkflow API
import { createWorkflow, WorkflowResponse }
  from "@medusajs/framework/workflows-sdk"

const myWorkflow = createWorkflow("my-workflow", (input) => {
  const stepResult = myStep(input)
  return new WorkflowResponse(stepResult)
})
```

## Execution Patterns

| Pattern | API | Purpose |
|---------|-----|---------|
| Sequential | Default step ordering | Steps run one after another |
| Parallel | `parallelize(stepA, stepB)` | Steps run concurrently |
| Conditional | `when(condition, () => step())` | Skip steps based on data |
| Transform | `transform(data, fn)` | Transform data between steps |

### Parallel Execution

```typescript
// Fetch live docs for parallelize import
import { parallelize } from "@medusajs/framework/workflows-sdk"

const [resultA, resultB] = parallelize(stepA(input), stepB(input))
```

### Conditional Execution

```typescript
// Fetch live docs for when() API
import { when } from "@medusajs/framework/workflows-sdk"

when(input, (data) => data.sendEmail === true, () => {
  return sendEmailStep(input)
})
```

## Invoking Workflows

| Context | Invocation Pattern |
|---------|-------------------|
| API Route | `await myWorkflow(req.scope).run({ input })` |
| Subscriber | `await myWorkflow(container).run({ input })` |
| Scheduled Job | `await myWorkflow(container).run({ input })` |
| Another Workflow | Use as a step with `createStep` wrapping |

## Workflow Hooks

Hooks allow extending built-in workflows without modifying core code:

| Hook Type | Purpose |
|-----------|---------|
| `before` | Run custom logic before a built-in step |
| `after` | Run custom logic after a built-in step |

### Hook Registration Skeleton

```typescript
// src/workflows/hooks/my-hook.ts
// Fetch live docs for hook registration API
import { createProductsWorkflow } from "@medusajs/medusa/core-flows"

createProductsWorkflow.hooks.productsCreated(
  async ({ products, additional_data }, { container }) => {})
// Fetch live docs for available hook names per workflow
```

## Built-in Workflows (Key Examples)

| Workflow | Domain | Key Hooks |
|----------|--------|-----------|
| `createProductsWorkflow` | Catalog | `productsCreated` |
| `updateProductsWorkflow` | Catalog | `productsUpdated` |
| `createCartWorkflow` | Cart | `cartCreated` |
| `completeCartWorkflow` | Checkout | `cartCompleted` |
| `createOrderWorkflow` | Orders | `orderCreated` |
| `createFulfillmentWorkflow` | Fulfillment | `fulfillmentCreated` |
| `createPaymentCollectionWorkflow` | Payments | hook available |
| `createCustomerAccountWorkflow` | Customers | hook available |

> **Fetch live docs** for the complete list -- new workflows and hooks are added in each Medusa release.

## Compensation Strategy

| Scenario | Compensation Action |
|----------|-------------------|
| Record created | Delete the created record |
| Payment captured | Refund the payment |
| Inventory reserved | Release the reservation |
| Email sent | Log warning (cannot unsend) |
| External API called | Call reverse/cancel endpoint |

Key rules:
- Every step that creates a side effect should define compensation
- Compensation runs in reverse order of step completion
- Compensation input is the second argument to `StepResponse`
- If compensation itself fails, the workflow enters a "failed" state requiring manual resolution

## Best Practices

- Keep steps small and focused -- one side effect per step
- Always define compensation for steps with side effects
- Use `parallelize` for independent steps to improve performance
- Use `when` for conditional logic -- do not put branching inside steps
- Resolve services from the container, never import them directly
- Name workflows and steps descriptively (e.g., `reserve-inventory-step`)
- Use `transform` for data reshaping -- do not create steps that only transform data

Fetch the Medusa workflow documentation for exact createStep/createWorkflow signatures, hook names, and built-in workflow list before implementing.
