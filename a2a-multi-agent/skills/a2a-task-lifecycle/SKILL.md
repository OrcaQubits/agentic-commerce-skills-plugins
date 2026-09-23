---
name: a2a-task-lifecycle
description: "Implement A2A (Agent-to-Agent) task lifecycle management — task creation, state transitions, terminal states, history, and artifacts. Use when building task state machines, handling state transitions, managing task persistence, or implementing task status tracking in agent-to-agent workflows."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# A2A Task Lifecycle

## Before writing code

**Fetch live docs**:
1. Fetch `https://a2a-protocol.org/latest/specification/` for the Task object schema and state machine
2. Web-search `site:github.com a2aproject A2A task lifecycle states` for state transition rules
3. Web-search `site:github.com a2aproject a2a-samples task` for task handling examples

## The 9 States

| State | Terminal? | Description |
|-------|-----------|-------------|
| `submitted` | No | Task received, queued for processing |
| `working` | No | Agent actively processing |
| `input-required` | No | Agent needs more input (multi-turn) |
| `auth-required` | No | Authentication needed |
| `completed` | Yes | Task finished successfully |
| `failed` | Yes | Task encountered an unrecoverable error |
| `canceled` | Yes | Task was canceled |
| `rejected` | Yes | Server refused the task |
| `unknown` | — | Default/unknown state |

## Valid State Transitions

```
submitted → working → completed
                    → failed
                    → canceled
                    → input-required → working (client provides input)
                                     → canceled

submitted → rejected
submitted → canceled

auth-required → working (auth provided)
auth-required → canceled
```

**Rules:** Terminal states (`completed`, `failed`, `canceled`, `rejected`) are final — no transitions out. Only the server transitions state (except `canceled` which client can request).

## Task State Machine Implementation

```typescript
const TERMINAL_STATES = new Set(["completed", "failed", "canceled", "rejected"]);

const VALID_TRANSITIONS: Record<string, string[]> = {
  submitted: ["working", "rejected", "canceled"],
  working: ["completed", "failed", "canceled", "input-required"],
  "input-required": ["working", "canceled"],
  "auth-required": ["working", "canceled"],
};

interface Task {
  id: string;
  status: { state: string; message?: string; timestamp: string };
  messages: Message[];
  artifacts: Artifact[];
  metadata?: Record<string, unknown>;
}

function transitionTask(task: Task, newState: string, message?: string): Task {
  if (TERMINAL_STATES.has(task.status.state)) {
    throw new Error(`Cannot transition from terminal state: ${task.status.state}`);
  }
  const allowed = VALID_TRANSITIONS[task.status.state];
  if (!allowed?.includes(newState)) {
    throw new Error(`Invalid transition: ${task.status.state} → ${newState}`);
  }
  return {
    ...task,
    status: { state: newState, message, timestamp: new Date().toISOString() },
  };
}
```

## Task Creation (message/send handler)

```typescript
import { randomUUID } from "crypto";

async function handleMessageSend(request: {
  taskId?: string;
  message: Message;
}): Promise<Task> {
  let task: Task;

  if (request.taskId) {
    task = await taskStore.get(request.taskId);
    if (!task) throw new Error(`Task not found: ${request.taskId}`);
    task.messages.push(request.message);
    task = transitionTask(task, "working");
  } else {
    task = {
      id: randomUUID(),
      status: { state: "submitted", timestamp: new Date().toISOString() },
      messages: [request.message],
      artifacts: [],
    };
  }

  await taskStore.save(task);
  task = transitionTask(task, "working", "Processing request");
  await taskStore.save(task);

  const result = await processTask(task);
  task.artifacts.push(result.artifact);
  task = transitionTask(task, "completed", "Done");
  await taskStore.save(task);
  return task;
}
```

## Artifacts

Artifacts are the outputs of a task, produced during `working` state:
- Each artifact has `id`, `name`, optional `description`, and `parts`
- Parts can be TextPart, FilePart, or DataPart
- In streaming mode, artifacts are delivered incrementally via `TaskArtifactUpdateEvent`

## Verification Workflow

1. Create a task via `message/send` without `taskId` — verify task is created with `submitted` state
2. Verify automatic transition to `working` — check status updates
3. Attempt an invalid transition (e.g., `submitted` → `completed`) — verify error is thrown
4. Complete a task — verify state is `completed` and artifacts are present
5. Attempt to transition a completed task — verify error (terminal state)
6. Test `input-required` flow: send a task that needs more input, provide follow-up, verify it resumes

## Best Practices

- Always validate state transitions — reject invalid ones with appropriate errors
- Use UUIDs for task IDs
- Store task state durably for production (not just in-memory)
- Set timeouts for tasks stuck in non-terminal states
- Include meaningful messages in status updates (not just the state enum)
- Use artifacts for structured outputs, messages for conversational exchanges
- Implement idempotency — handle duplicate messages for the same task gracefully

Fetch the specification for the exact Task object schema, state enum values, and transition validation rules before implementing.
