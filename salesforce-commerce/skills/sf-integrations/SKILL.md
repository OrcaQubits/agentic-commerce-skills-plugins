---
name: sf-integrations
description: Build Salesforce Commerce integrations — B2C (SCAPI hooks, webhooks, custom script callouts) and B2B (Platform Events, Change Data Capture, outbound messages). Both platforms use event-driven patterns, HMAC verification, idempotency, and retry handling for reliable integration.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Salesforce Commerce Integrations

## Before Writing Code

**CRITICAL**: Always fetch live documentation BEFORE implementing integrations.

1. Web-search: "Salesforce Platform Events developer guide 2026"
2. Web-search: "Salesforce Change Data Capture implementation guide 2026"
3. Web-search: "Salesforce Named Credentials callout authentication 2026"
4. Web-search: "Salesforce Commerce Cloud SCAPI hooks reference 2026"
5. Web-search: "Salesforce Commerce Cloud webhooks HMAC verification 2026"
6. Web-fetch: `https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/`
7. Web-fetch: `https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/`
8. Web-fetch: `https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_callouts_named_credentials.htm`

Integration APIs, security requirements, and event schemas change across Salesforce releases. Verify hook types, event schemas, authentication patterns, and signature algorithms against current docs.

## Conceptual Architecture

### Event-Driven Architecture Overview

Salesforce Commerce supports multiple event-driven integration patterns across B2C and B2B platforms.

| Pattern | Platform | Direction | Delivery | Use Case |
|---|---|---|---|---|
| Platform Events | B2B (Apex) | Pub/Sub | At-least-once | Order lifecycle, custom business events |
| Change Data Capture (CDC) | B2B (Apex) | Outbound | At-least-once | Record change sync to external systems |
| Streaming API | B2B (Apex) | Outbound | Push | Real-time record change notifications |
| SCAPI Hooks | B2C (SFCC) | Pre/Post | Synchronous | Intercept API calls (basket, order) |
| Webhooks | B2C (SFCC) | Outbound | At-least-once | Notify external systems of events |
| Outbound Messages | B2B (Workflow) | Outbound | SOAP | Legacy workflow-triggered notifications |
| Job-Based Import/Export | B2C (SFCC) | Bidirectional | Batch | Scheduled file-based data sync |

### B2C Integration Patterns

**SCAPI Hooks** provide pre/post processing on API calls. Hooks are **disabled by default** and must be explicitly enabled in Business Manager. Hook scripts live in cartridges and are configured via `hooks.json`.

| Hook Type | Timing | Can Modify | Example |
|---|---|---|---|
| `beforePOST` | Before API processes request | Request body | Validate inventory before add-to-cart |
| `afterPOST` | After API processes request | Response body | Send order to OMS after placement |
| `modifyGETResponse` | After GET response built | Response body | Add custom attributes to API response |
| `beforePATCH` | Before PATCH processes | Request body | Validate coupon code before applying |
| `afterPATCH` | After PATCH processes | Response body | Log basket modifications |

Hook scripts follow the `dw.ocapi.shop.[resource].[hookType]` naming convention and are registered in the cartridge's `hooks.json` file.

**Webhooks** deliver event notifications to external HTTP endpoints. Events include `order.created`, `order.updated`, inventory changes, and catalog updates. Webhook configuration is managed via the Data API.

**Job-Based Integration** uses scheduled scripts for bulk data sync via IMPEX directory (WebDAV or SFTP), parsing XML/CSV files and updating Commerce Cloud objects within `Transaction.wrap()`.

### B2B Integration Patterns

**Platform Events** are custom publish/subscribe events defined in Salesforce Setup. Publishers use `EventBus.publish()` from Apex; subscribers use Apex triggers on the event or external CometD/Pub/Sub API clients. Key characteristics:

- Defined as custom objects with `__e` suffix (e.g., `OrderShipped__e`)
- Support custom fields (Text, Number, DateTime, etc.)
- Published outside of transaction rollback scope (fire even if transaction fails when using `publish after commit`)
- Subscribers can set `ReplayId` to replay missed events

**Change Data Capture (CDC)** automatically publishes change events when standard or custom object records are created, updated, deleted, or undeleted.

| CDC Header Field | Purpose |
|---|---|
| `entityName` | Object name (e.g., `Order`, `Product2`) |
| `recordIds` | List of affected record IDs |
| `changeType` | `CREATE`, `UPDATE`, `DELETE`, `UNDELETE` |
| `changedFields` | List of field API names that changed |
| `commitTimestamp` | When the change was committed |
| `transactionKey` | Groups changes from the same transaction |

Enable CDC for specific objects in Setup > Change Data Capture. Not all objects support CDC -- verify in documentation.

**Outbound Messages** are SOAP-based notifications triggered by workflow rules. The receiver must expose a SOAP endpoint and return an `Ack: true` response. These are legacy; prefer Platform Events for new integrations.

**External Services** provide declarative integration via OpenAPI specs imported into Salesforce, generating Apex classes automatically. Useful for no-code/low-code integration via Flow Builder.

### Common Integration Targets

| System | B2C Pattern | B2B Pattern |
|---|---|---|
| ERP (SAP, Oracle, NetSuite) | SCAPI hook afterPOST, job-based export | Platform Event, CDC |
| OMS (Order Management) | Webhook order.created, SCAPI hook | Platform Event on Order |
| PIM (Product Information) | Job-based import (XML/CSV) | CDC on Product2 |
| Tax Engine (Avalara, Vertex) | SCAPI hook beforePOST on basket | CartExtension TaxCalculator callout |
| Shipping Carrier (FedEx, UPS) | SCAPI hook for rate shopping | CartExtension ShippingCalculator callout |
| Payment Gateway | SCAPI hook on checkout | Apex callout with Named Credentials |

### HMAC Verification

Incoming webhooks must be verified using HMAC signatures before processing. The sender computes an HMAC-SHA256 digest of the payload using a shared secret and includes it in a header (e.g., `X-DW-Signature` for Commerce Cloud). The receiver recomputes the digest and compares using constant-time comparison to prevent timing attacks. Key points:

- Always use SHA-256 (or the algorithm specified in current docs)
- Use constant-time string comparison (not `===`) to prevent timing side-channels
- Reject requests with missing or invalid signatures immediately (return 401)
- Rotate webhook secrets periodically and support dual-secret rotation windows

### Idempotency

Webhooks and Platform Events deliver at-least-once, meaning duplicates are possible. Every event handler must be idempotent:

- Use the unique event ID (e.g., `event_id`, `ReplayId`) as a deduplication key
- Check a persistent store (database table or cache like Redis) before processing
- Skip duplicates with a 200 OK response (not an error)
- Set a reasonable TTL (24-48 hours) for the deduplication window
- For database-backed deduplication, use a unique constraint on the event ID column

### Named Credentials

Named Credentials manage external service authentication declaratively in Salesforce Setup. They handle OAuth 2.0 token refresh, basic auth, and custom headers automatically. Always use `callout:CredentialName/path` in Apex HTTP requests -- never hardcode API keys or secrets.

| Credential Type | Auth Method | Use Case |
|---|---|---|
| Named Credential | Basic, OAuth 2.0, JWT | Apex callouts to external APIs |
| External Credential | OAuth 2.0 Client Credentials | Server-to-server integration |
| Per-User | OAuth 2.0 Auth Code | User-specific external access |

### Error Handling and Retry Strategy

- Distinguish retryable (5xx, timeout, network error) from non-retryable (4xx) errors
- Implement exponential backoff: delay = 2^attempt * base_delay, max 3-5 attempts
- Add jitter (random component) to prevent thundering herd on retries
- Use a dead letter queue (DLQ) for messages that exceed max retries
- Log all integration activity with correlation IDs for end-to-end tracing
- Platform Events support replay: subscribers can replay missed events using `ReplayId`
- For B2C webhooks: respond with 200 OK quickly, then process asynchronously

## Code Examples

**Pattern: Platform Event publisher skeleton**

```apex
OrderShipped__e event = new OrderShipped__e(
    OrderId__c = orderId
);
Database.SaveResult sr = EventBus.publish(event);
// Fetch live docs for EventBus.publish error handling
```

**Pattern: SCAPI hook module skeleton**

```javascript
exports.beforePOST = function(basket, requestBody) {
    // Fetch live docs for SCAPI hook signatures
};
module.exports.afterPOST = afterPOST;
```

**Pattern: CDC subscriber concept**

```javascript
// Subscribe to /data/OrderChangeEvent via CometD
// Fetch live docs for CDC event schema and replay
```

## Best Practices

### Event-Driven Design
- Decouple systems with async messaging (Platform Events, webhooks)
- Design for eventual consistency -- avoid synchronous cross-system calls
- Add new consumers without changing publishers
- Use CDC for record-change sync; Platform Events for custom business events

### Security
- Always validate HMAC signatures before processing webhooks
- Use constant-time comparison to prevent timing attacks
- Use Named Credentials for all outbound callouts -- never hardcode secrets
- Rotate webhook secrets and API credentials on a regular schedule

### Reliability
- Implement idempotency on every event handler using unique event IDs
- Use exponential backoff with jitter for retries
- Route failed messages to a dead letter queue for manual inspection
- Monitor integration health: success rate, latency, error rate, DLQ depth

### Observability
- Structured JSON logging with correlation IDs across all integration points
- Track metrics: requests total, error count, duration histogram
- Set alerts for sustained failure rates or latency spikes
- Document all integration points, API contracts, and runbooks

---

Fetch the latest Salesforce Platform Events guide, CDC guide, SCAPI hooks reference, and Named Credentials documentation for exact event schemas, hook signatures, and authentication configuration before implementing.
