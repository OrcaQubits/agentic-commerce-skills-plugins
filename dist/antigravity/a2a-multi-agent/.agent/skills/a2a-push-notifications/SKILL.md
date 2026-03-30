---
name: a2a-push-notifications
description: >
  Implement A2A push notifications — callback URL registration, notification
  delivery, and management methods. Use when building async notification
  delivery for long-running A2A tasks.
---

# A2A Push Notifications

## Before writing code

**Fetch live docs**:
1. Fetch `https://a2a-protocol.org/latest/specification/` for the push notification section
2. Web-search `site:github.com a2aproject A2A push notifications` for notification protocol details
3. Web-search `site:github.com a2aproject a2a-samples push notification` for implementation examples
4. Fetch SDK docs for push notification classes and configuration

## Conceptual Architecture

### What Push Notifications Are

Push notifications allow A2A servers to **proactively notify clients** about task state changes without requiring the client to hold open a streaming connection or poll. The client registers a callback URL, and the server POSTs updates to it.

### When to Use Push Notifications

- **Very long-running tasks** — Minutes to hours, where holding an SSE connection is impractical
- **Asynchronous workflows** — Client doesn't need real-time updates, just eventual notification
- **Serverless clients** — Clients that can't maintain long-lived connections
- **Batch processing** — Multiple tasks submitted, notifications received as each completes

### How It Works

1. **Client registers** — Calls `tasks/pushNotificationConfig/set` with a callback URL for a task
2. **Server stores config** — Associates the callback URL with the task
3. **Task progresses** — Server processes the task normally
4. **Server notifies** — When the task state changes, server POSTs an update to the callback URL
5. **Client processes** — Client's webhook endpoint receives and processes the notification

### Push Notification Methods

| Method | Purpose |
|--------|---------|
| `tasks/pushNotificationConfig/set` | Register a callback URL for a task |
| `tasks/pushNotificationConfig/get` | Retrieve the notification config for a task |
| `tasks/pushNotificationConfig/list` | List all notification configs |
| `tasks/pushNotificationConfig/delete` | Remove a notification config |

### Notification Payload

When the server sends a push notification, it POSTs a JSON payload to the callback URL containing:
- Task ID
- Current task status (state + optional message)
- Optional artifacts or data

### Server-Side Implementation

The server must:
1. Declare `pushNotifications: true` in the Agent Card capabilities
2. Store notification configurations (callback URL per task)
3. On task state change, POST to the registered callback URL
4. Handle failed deliveries (retry with backoff, or mark as failed)
5. Support CRUD operations for notification configs

### Client-Side Implementation

The client must:
1. Check Agent Card for `pushNotifications` capability
2. Expose an HTTP endpoint to receive notifications (webhook)
3. Register the webhook URL via `tasks/pushNotificationConfig/set`
4. Validate incoming notifications (verify they're from the expected server)
5. Process notification payloads

### Security Considerations

- **Validate origin** — Verify notifications come from the expected A2A server
- **Use HTTPS** — Callback URLs should always be HTTPS in production
- **Authenticate callbacks** — Use shared secrets or signature verification
- **Rate limiting** — Protect the callback endpoint from excessive notifications
- **Timeout handling** — Server should not block indefinitely on notification delivery

### Best Practices

- Implement retry logic with exponential backoff for failed notification deliveries
- Set a maximum retry count to avoid infinite loops
- Log all notification attempts (success and failure) for debugging
- Support notification config deletion for task cleanup
- Use idempotent callback handlers — notifications may be delivered more than once
- Consider notification batching for high-volume scenarios
- Test with unreachable callback URLs to verify retry behavior

Fetch the specification for exact push notification schemas, callback payload format, and delivery guarantees before implementing.
