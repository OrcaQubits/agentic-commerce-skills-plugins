---
name: sf-b2c-jobs
description: Build and manage B2C Commerce jobs — job framework, job steps (script modules, pipelines, custom), scheduling with cron expressions, job context and parameters, import/export jobs, reindex jobs, and Business Manager monitoring. Use when implementing background processing in B2C Commerce.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Salesforce B2C Commerce Jobs

## Before Writing Code

**ALWAYS fetch live documentation BEFORE writing any job code:**

1. Web-search: "Salesforce B2C Commerce job framework documentation 2026"
2. Web-search: "SFCC custom job step implementation guide 2026"
3. WebFetch official Salesforce docs for:
   - Job framework reference and execution context
   - System job types and parameters
   - Cron expression syntax for B2C Commerce
   - sfcc-ci job command reference

**Why:** Job APIs, execution contexts, and best practices evolve with each B2C Commerce release. Always verify current patterns.

## Conceptual Architecture

### Job Framework Overview

The job framework provides scheduled background processing in B2C Commerce:
- **Job execution engine**: Server-side background task runner
- **Job steps**: Individual units of work within a job (one job can have multiple steps)
- **Job scheduling**: Cron-based recurring or manual/API triggering
- **Job monitoring**: Business Manager dashboard (Administration > Operations > Jobs)

### Job Types

| Type | Description | Approach |
|------|-------------|----------|
| **System jobs** | Built-in import/export/reindex/cleanup | Configured in Business Manager |
| **Script module steps** | Custom JavaScript (modern approach) | `exports.execute = function(jobStepExecution) {}` |
| **Pipeline steps** | Legacy pipeline-based steps | Maintenance mode; avoid for new work |
| **Chunk steps** | Large dataset processing | Read-process-write pattern with commit intervals |

### Step Types

| Step Type | Use Case | Key Characteristic |
|-----------|----------|--------------------|
| **Script** | General custom logic | Single `execute()` entry point; return `Status` |
| **Pipeline** | Legacy flows | Deprecated for new development |
| **Chunk** | Large dataset processing | Framework manages read/process/write lifecycle with batching |

### Cron Expression Examples

```
0 0 2 * * ?        Every day at 2:00 AM
0 */15 * * * ?     Every 15 minutes
0 0 0 1 * ?        First day of month at midnight
0 0 18 ? * MON-FRI Weekdays at 6:00 PM
```

Format: `seconds minutes hours day-of-month month day-of-week`

### Status Return Concept

Every job step must return a `dw.system.Status` object:

| Status | Constant | Meaning |
|--------|----------|---------|
| Success | `Status.OK` | Step completed successfully |
| Error | `Status.ERROR` | Step failed; may halt job depending on configuration |

There is **no `Status.WARN`**. For partial success, return `Status.OK` with a descriptive message (e.g., `'PARTIAL'` status code with error count in the message).

```javascript
// Pattern: Status return
var Status = require('dw/system/Status');
return new Status(Status.OK, 'COMPLETED', 'message');
// Fetch live docs for Status constructor
```

### Chunk Processing Lifecycle

For large datasets, chunk-oriented processing follows this lifecycle:

1. **Read**: Iterator provides next item (or batch of items)
2. **Process**: Transform/validate each item
3. **Write**: Persist results (wrapped in transaction)
4. **Commit**: Framework commits at configured intervals

The framework manages batching, transaction boundaries, and error recovery. Fetch live docs for the exact chunk step interface (`read`, `process`, `write`, `afterStep` methods).

### Job Context and Parameters

Job step parameters are configured in Business Manager per job and accessed at runtime:
- `jobStepExecution.getParameterValue('ParamName')` -- retrieve config values
- `jobStepExecution.isDisabled()` -- check if step is disabled
- Parameter types: String, Number, Boolean, File

### System Jobs

| Category | Examples |
|----------|---------|
| **Import** | Catalog, inventory, pricing, customer data (XML/CSV) |
| **Export** | Orders, products, customers |
| **Reindex** | Search index rebuild, product availability updates |
| **Cleanup** | Session cleanup, log rotation, temp file removal |

### Monitoring

- **Business Manager**: Administration > Operations > Jobs -- execution history, error logs, manual triggering
- **sfcc-ci CLI**: `sfcc-ci job:run --job-id <id>` and `sfcc-ci job:status --job-execution-id <id>`
- Use `dw/system/Logger` for structured logging within job steps

## Best Practices

### Design Principles
- Make job steps **idempotent** -- running twice produces the same result (use absolute values, not increments)
- Use **chunked processing** with `Transaction.wrap()` per batch, not per item
- Externalize configuration via **job parameters** rather than hardcoding values
- Return meaningful `Status` messages with item counts and error summaries

### Error Handling
- Wrap job logic in try/catch; return `Status.ERROR` on failure
- For partial failures, catch per-item errors, accumulate counts, return `Status.OK` with descriptive message
- Log errors with `dw/system/Logger` including item identifiers for debugging

### Transaction Management
- Wrap batch operations in `Transaction.wrap()` (per batch, not per item)
- Keep transaction scope minimal to reduce lock contention
- Close iterators (e.g., `products.close()`) in finally blocks to prevent resource leaks

### Scheduling and Monitoring
- Schedule resource-intensive jobs during off-peak hours
- Monitor execution times and error rates in Business Manager
- Set up alerts for failed job executions
- Test jobs with small batch sizes before production deployment

Fetch the B2C Commerce job framework reference, cron syntax guide, and sfcc-ci documentation for exact step interfaces, parameter configuration, and chunk processing patterns before implementing.
