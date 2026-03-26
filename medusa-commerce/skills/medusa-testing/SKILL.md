---
name: medusa-testing
description: Test Medusa v2 applications — Jest setup, module unit tests, workflow integration tests, API route tests, medusaIntegrationTestRunner, and mock patterns. Use when writing tests for Medusa projects.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Testing

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com testing` for official testing guide and setup
2. Web-search `site:docs.medusajs.com medusaIntegrationTestRunner` for integration test utilities
3. Web-search `site:docs.medusajs.com unit test module` for module unit testing patterns
4. Fetch `https://docs.medusajs.com/resources/medusa-testing` and review test runner configuration
5. Web-search `medusajs v2 jest test workflow 2026` for latest workflow testing patterns

## Test Architecture

### Test Pyramid

```
        ┌─────────┐
        │  E2E    │  API route tests (slow, high confidence)
        ├─────────┤
        │ Integr. │  Workflow + cross-module tests
        ├─────────┤
        │  Unit   │  Module service + utility tests (fast)
        └─────────┘
```

### Test Types

| Type | Scope | Runner | Speed |
|------|-------|--------|-------|
| Unit | Single module service | Jest | Fast |
| Integration | Workflows, cross-module | `medusaIntegrationTestRunner` | Medium |
| API Route | HTTP endpoints | `medusaIntegrationTestRunner` + supertest | Slow |
| E2E | Full user flows | Playwright/Cypress (optional) | Slowest |

## Jest Setup

```ts
// Skeleton: jest.config.ts for Medusa v2
// Fetch live docs for current recommended config
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  // Fetch live docs for moduleNameMapper and transform
}
```

### Package Dependencies

| Package | Purpose |
|---------|---------|
| `jest` | Test runner |
| `ts-jest` | TypeScript support |
| `@medusajs/test-utils` | Medusa test utilities |
| `supertest` | HTTP assertion library |

> **Fetch live docs** for the current `@medusajs/test-utils` package exports and version compatibility.

## Module Unit Tests

```ts
// Skeleton: module unit test
// Fetch live docs for module test setup
describe("ProductModuleService", () => {
  let service: IProductModuleService
  // Fetch live docs for beforeAll setup with test database
})
```

### Service Method Testing

| Test Target | What to Verify |
|-------------|----------------|
| `createProducts` | Returns product with correct fields |
| `listProducts` | Filters, pagination, sorting work |
| `retrieveProduct` | Relations loaded correctly |
| `updateProducts` | Partial updates applied |
| `deleteProducts` | Cascade behavior correct |

### Setup and Teardown

| Hook | Purpose |
|------|---------|
| `beforeAll` | Initialize module with test database |
| `beforeEach` | Seed test data |
| `afterEach` | Clean up created records |
| `afterAll` | Close database connection |

> **Fetch live docs** for test database initialization and module container setup.

## Integration Tests with medusaIntegrationTestRunner

`medusaIntegrationTestRunner` provides a full Medusa application container with all modules, test database setup/teardown, API client, and seeded admin user.

```ts
// Skeleton: integration test — Fetch live docs for config
import { medusaIntegrationTestRunner } from "@medusajs/test-utils"

medusaIntegrationTestRunner({
  testSuite: ({ api, getContainer }) => {
    // Fetch live docs for api and container usage
  },
})
```

### Runner Context

| Property | Description |
|----------|-------------|
| `api` | Pre-configured HTTP client (AxiosInstance) |
| `getContainer` | Returns the DI container for resolving services |
| `dbConnection` | Database connection reference |
| `modulesConfig` | Override module configurations (runner option) |

> **Fetch live docs** for the full context object shape and available helper methods.

## Workflow Tests

### What to Test

| Aspect | Verification |
|--------|-------------|
| Success path | Workflow completes, returns expected result |
| Side effects | Linked modules updated (pricing, inventory) |
| Compensation | Failed step triggers rollback of previous steps |
| Input validation | Invalid inputs produce expected errors |
| Idempotency | Repeated execution does not create duplicates |

### Compensation Testing

| Strategy | Description |
|----------|-------------|
| Force step failure | Mock a step to throw an error |
| Verify rollback | Check that previous steps are compensated |
| Check data state | Ensure database is clean after rollback |

> **Fetch live docs** for workflow step mocking and compensation test patterns.

## API Route Tests

### Route Test Checklist

| Check | Description |
|-------|-------------|
| Status code | Correct HTTP status for success and error |
| Response body | Expected fields present with correct types |
| Side effects | Database state updated correctly |
| Authentication | Unauthenticated requests rejected |
| Validation | Invalid inputs return 400 with errors |
| Pagination | List endpoints paginate correctly |

### Authentication in Tests

| Actor | Header | Source |
|-------|--------|--------|
| Admin | `Authorization: Bearer <jwt>` | Login via `/auth/user/emailpass` |
| Customer | `Authorization: Bearer <jwt>` | Login via `/auth/customer/emailpass` |
| Store API | `x-publishable-api-key` | Created in test setup |

## Mock Patterns

| Pattern | When to Use |
|---------|-------------|
| Full module mock | Unit testing code that depends on a module |
| Service method stub | Override specific method behavior |
| Test database | Integration tests with real data |

### Common Mocks

| Mock Target | Purpose |
|-------------|---------|
| Payment provider | Avoid real payment calls in tests |
| Fulfillment provider | Avoid real shipping API calls |
| Email service | Capture sent emails for assertion |
| Event bus | Capture emitted events for assertion |

> **Fetch live docs** for recommended mock patterns and test utility helpers.

## Best Practices

### Test Organization
- Co-locate tests with source: `src/modules/product/__tests__/`
- Name test files with `.spec.ts` suffix; group by feature, not test type
- Use factory functions to generate test data — avoid hardcoded fixtures

### Test Data and Integration
- Use `medusaIntegrationTestRunner` for all cross-module tests
- Always test compensation (rollback) paths for critical workflows
- Clean up in `afterEach` to prevent pollution; seed minimal data

### CI/CD and Coverage
- Run unit tests on every commit, integration tests on PR; target 80% coverage
- Use a dedicated test database — never test against production

Fetch the Medusa v2 testing documentation and `@medusajs/test-utils` reference for exact runner configuration, mock patterns, and test utility APIs before implementing.
