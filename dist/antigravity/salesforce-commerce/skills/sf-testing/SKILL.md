---
name: sf-testing
description: >
  Test Salesforce Commerce code — B2C (Node.js unit testing, sfcc-ci CI/CD,
  sandbox management, linting) and B2B (Apex test classes with 75% coverage
  minimum, Jest for LWC, sf CLI deployment and validation). Use when writing
  tests or setting up CI/CD.
---

# sf-testing

## Before Writing Code

**Fetch live docs before writing tests or setting up CI/CD.**

1. Web-search: "Salesforce B2C Commerce testing best practices 2026"
2. Web-search: "Salesforce Apex testing guide code coverage 2026"
3. Web-search: "Lightning Web Components Jest testing @salesforce/sfdx-lwc-jest 2026"
4. Web-search: "sfcc-ci CI/CD pipeline documentation 2026"
5. Web-fetch: `https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing.htm`
6. Web-fetch the LWC testing guide for current Jest patterns

## Conceptual Architecture

### Testing Strategy Overview

| Layer | B2C (SFCC) | B2B (Lightning) |
|---|---|---|
| Unit | Mocha/Jest for JS cartridge logic | Apex test classes (`@IsTest`) |
| Component | N/A | LWC Jest (`@salesforce/sfdx-lwc-jest`) |
| Integration | SCAPI/OCAPI against sandbox | sf CLI deploy validation |
| E2E | Full checkout flow on sandbox | Full storefront flow on scratch org |
| Linting | ESLint (SFCC config) | ESLint (LWC), Apex PMD |
| Coverage | nyc/istanbul (aim 80%+) | Salesforce enforced minimum 75% |

### B2C Commerce Testing

**Unit Testing:**
- Framework: Mocha or Jest for JavaScript cartridge logic
- Mocking: mock `dw.*` API stubs (dw.system, dw.catalog, dw.order) via proxyquire or jest.mock
- Test scope: controllers, models, helper scripts
- Coverage: nyc or istanbul; aim for 80%+ on business logic

**Integration Testing:**
- Test SCAPI endpoints against development/staging sandbox
- Validate full checkout flow, product search, account management
- Use sandbox-specific test data

**Linting and Code Quality:**
- ESLint with SFCC-specific configuration
- Enforce cartridge naming conventions and API usage patterns

**CI/CD Pipeline (sfcc-ci):**

```
1. sfcc-ci code:deploy -> upload cartridge
2. sfcc-ci code:activate -> activate version
3. npm test -> run unit tests
4. sfcc-ci job:run -> integration tests
```

**Sandbox Management:**

| Environment | Purpose |
|---|---|
| Development | Developer-specific feature work |
| Staging | Pre-production validation |
| Production | Controlled release deployment |

### B2B Commerce Testing

**Apex Test Classes:**
- Annotate with `@IsTest`; minimum 75% coverage enforced by Salesforce
- Aim for 85%+ on critical business logic
- Use `@TestSetup` for shared test data across methods
- Assertions: `System.assert()`, `System.assertEquals()`, `System.assertNotEquals()`

**Test Data Factory Pattern:**

```apex
@TestSetup
static void setupTestData() {
    // Fetch live docs for TestDataFactory patterns
    // Create accounts, products, orders for tests
}
```

**Mock Callouts:**
- `HttpCalloutMock` interface for external HTTP callouts
- `StaticResourceCalloutMock` for static response data
- Register mocks via `Test.setMock()`

**LWC Jest Testing:**
- Framework: `@salesforce/sfdx-lwc-jest`
- Wire adapter mocking for `@wire` decorated properties
- Imperative Apex method mocking via `jest.mock`
- DOM querying and assertion on rendered component output
- Custom event and standard event testing

**sf CLI Deployment Validation:**

```bash
# Dry-run validation with test execution
sf project deploy start --dry-run --test-level RunLocalTests
# Run specific test classes
sf apex run test --class-names MyTestClass --result-format human
```

**Code Coverage Requirements:**

| Threshold | Context |
|---|---|
| 75% minimum | Salesforce deployment requirement (org-wide) |
| 85%+ recommended | Critical business logic (payments, orders) |
| 100% target | Apex triggers (keep triggers thin, test all paths) |
| Per-class tracking | `sf apex run test --code-coverage` reports per class |

### CI/CD Pipelines

**B2C Pipeline (GitHub Actions pattern):**

| Step | Command |
|---|---|
| Deploy | `sfcc-ci code:deploy cartridge.zip -i $SANDBOX` |
| Activate | `sfcc-ci code:activate --version $VERSION` |
| Test | `npm test` |

**B2B Pipeline (Salesforce CLI pattern):**

| Step | Command |
|---|---|
| Deploy | `sf project deploy start --target-org staging` |
| Test | `sf apex run test --test-level RunLocalTests --code-coverage` |
| Report | `sf apex get test --test-run-id $ID` |

### Performance Testing

- Load testing: simulate concurrent users against sandbox (Artillery, JMeter)
- Stress testing: identify breaking points under extreme load
- Establish baseline metrics; run performance tests on schedule

## Code Examples

```javascript
// Pattern: B2C controller unit test
// Fetch live docs for proxyquire and dw.* mock patterns
// proxyquire('./Controller', {'dw/catalog/ProductMgr': mock})
// assert result matches expected
```

```apex
// Pattern: B2B Apex test with assertions
// Fetch live docs for @IsTest and System.assertEquals
// Test.startTest(); call method; Test.stopTest();
// System.assertEquals(expected, actual, 'message');
```

## Best Practices

### General Testing
- Write tests alongside feature development, not after
- Automate testing in every deployment pipeline
- Mock all external dependencies in unit tests
- Generate and archive test result reports

### B2C-Specific
- Mock `dw.*` APIs; never rely on live Salesforce APIs in unit tests
- Isolate controller logic from views for testability
- Use dedicated sandboxes for automated testing
- Store tests alongside cartridge code in version control

### B2B-Specific
- Bulkify test data (200+ records) to verify governor limit compliance
- Test error handling and edge cases (negative testing)
- Use `System.runAs()` for user context and permission testing
- Test LWC keyboard navigation and ARIA attributes for accessibility

### CI/CD
- Trigger tests on every commit; fail builds on test failure
- Maintain rollback plans for failed deployments
- Keep dev/staging/production configurations aligned
- Alert team immediately on test failures

Fetch the Apex testing guide, LWC Jest documentation, and sfcc-ci CI/CD reference for exact framework versions and configuration before implementing.
