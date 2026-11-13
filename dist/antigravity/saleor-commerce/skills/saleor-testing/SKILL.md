---
name: saleor-testing
description: >
  Test Saleor applications — pytest setup, Django test client, GraphQL test
  patterns, App testing, factory_boy fixtures, and webhook testing. Use when
  writing tests for Saleor projects.
---

# Saleor Testing

## Before writing code

**Fetch live docs**:
1. Web-search `site:github.com/saleor/saleor pytest conftest fixtures` for Saleor's test setup and existing fixtures
2. Web-search `site:docs.saleor.io app testing webhooks` for App testing patterns and webhook verification
3. Web-search `site:docs.saleor.io graphql API testing` for GraphQL query and mutation testing approaches
4. Fetch `https://github.com/saleor/saleor/blob/main/conftest.py` and review root-level test configuration
5. Web-search `site:docs.pytest.org fixtures factory_boy django` for pytest fixtures and factory_boy integration

## Test Architecture

Saleor follows a layered testing approach:

| Layer | Tool | Purpose |
|-------|------|---------|
| Unit tests | pytest | Test individual functions, utilities, and model methods |
| Integration tests | Django test client | Test GraphQL API endpoints with database |
| App tests | pytest + httpx/requests-mock | Test App webhooks, signature verification |
| E2E tests | pytest + API client | Test full user flows through the API |

## Pytest Setup

### Core Configuration

| File | Purpose |
|------|---------|
| `pytest.ini` / `pyproject.toml` | Pytest settings, markers, default flags |
| `conftest.py` (root) | Shared fixtures, database setup, API clients |
| `conftest.py` (per-app) | App-specific fixtures and helpers |

### Essential pytest Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `DJANGO_SETTINGS_MODULE` | `saleor.tests.settings` | Test-specific Django settings |
| `--reuse-db` | Flag | Reuse test database across runs for speed |
| `--no-migrations` | Flag | Skip migrations; create tables directly |
| `-x` | Flag | Stop on first failure during development |
| `-n auto` | Flag | Parallel execution with pytest-xdist |

### Key pytest Plugins

| Plugin | Purpose |
|--------|---------|
| `pytest-django` | Django integration, database access, settings override |
| `pytest-xdist` | Parallel test execution |
| `pytest-mock` | Mock and patch utilities |
| `pytest-asyncio` | Async test support |
| `pytest-vcr` | Record and replay HTTP interactions |
| `pytest-factoryboy` | factory_boy integration with pytest fixtures |

## Django Test Client for GraphQL

Saleor's GraphQL API is tested using Django's test client:

### API Client Pattern

| Component | Description |
|-----------|-------------|
| Test client | Django `Client` or `RequestFactory` for HTTP requests |
| Endpoint | POST to `/graphql/` with query and variables |
| Authentication | Set `HTTP_AUTHORIZATION` header with JWT or App token |
| Content type | `application/json` for standard queries |

### Authenticated Request Patterns

| Actor | Header | Token Source |
|-------|--------|--------------|
| Anonymous | None | No authentication |
| Customer | `Authorization: Bearer <jwt>` | `tokenCreate` or test fixture |
| Staff user | `Authorization: Bearer <jwt>` | Staff user fixture with permissions |
| App | `Authorization: Bearer <app-token>` | App token fixture |

## GraphQL Test Helper Pattern

### Response Assertion Patterns

| Assertion | What to Check |
|-----------|---------------|
| Status code | `assert response.status_code == 200` |
| No errors | `assert "errors" not in content` or `content["data"]["mutation"]["errors"] == []` |
| Data present | `assert content["data"]["query"]["field"] == expected` |
| Permission denied | `assert content["errors"][0]["extensions"]["exception"]["code"] == "PermissionDenied"` |
| Validation error | Check `errors` array in mutation response for field-level errors |

## factory_boy Factories for Saleor Models

### Core Model Factories

| Factory | Model | Key Fields |
|---------|-------|------------|
| `UserFactory` | `User` | email, first_name, last_name, is_staff |
| `ProductTypeFactory` | `ProductType` | name, has_variants, is_shipping_required |
| `ProductFactory` | `Product` | name, product_type, category, slug |
| `ProductVariantFactory` | `ProductVariant` | product, sku, track_inventory |
| `CategoryFactory` | `Category` | name, slug, parent |
| `CollectionFactory` | `Collection` | name, slug |
| `ChannelFactory` | `Channel` | name, slug, currency_code |
| `WarehouseFactory` | `Warehouse` | name, slug, address |
| `OrderFactory` | `Order` | user, channel, billing_address |
| `OrderLineFactory` | `OrderLine` | order, variant, quantity |
| `CheckoutFactory` | `Checkout` | channel, email, shipping_address |
| `VoucherFactory` | `Voucher` | code, type, discount_value |
| `ShippingZoneFactory` | `ShippingZone` | name, countries |
| `ShippingMethodFactory` | `ShippingMethod` | name, type, shipping_zone |

## Testing Apps

### Webhook Payload Validation

| Test Aspect | What to Verify |
|-------------|----------------|
| Payload structure | JSON schema matches expected format |
| Required fields | All mandatory fields are present |
| Data accuracy | Payload values match the triggering event |
| Serialization | Dates, decimals, and enums serialize correctly |

### Signature Verification Testing

| Step | Description |
|------|-------------|
| 1. Get key material | For JWS (default): use test JWKS; for legacy HMAC: use App secret key |
| 2. Sign payload | Create valid JWS/HMAC signature for the test payload |
| 3. Set header | Include signature in the `Saleor-Signature` header |
| 4. Verify in App | App verifies signature and processes payload |
| 5. Test mismatch | Verify App rejects requests with invalid signatures |

## Testing GraphQL Queries and Mutations

### Query Test Pattern

| Step | Description |
|------|-------------|
| 1. Create test data | Use factories to set up products, channels, etc. |
| 2. Execute query | Send GraphQL query via test client |
| 3. Assert results | Verify returned data matches created test data |
| 4. Test filtering | Verify filters, search, and pagination work |
| 5. Test permissions | Verify unauthorized users cannot access data |

### Mutation Test Pattern

| Step | Description |
|------|-------------|
| 1. Set up prerequisites | Create required related objects |
| 2. Execute mutation | Send mutation with valid input |
| 3. Assert success | Check response for data and no errors |
| 4. Verify database | Query the database to confirm changes persisted |
| 5. Test validation | Send invalid input and verify error messages |
| 6. Test permissions | Verify only authorized users can execute |

## Fixture Patterns

### Commonly Needed Test Fixtures

| Fixture | Provides |
|---------|----------|
| `staff_user` | Authenticated staff user with configurable permissions |
| `customer_user` | Authenticated customer with address |
| `channel_USD` | Default USD channel |
| `product` | Product with type, category, variant, and channel listing |
| `order` | Order with lines, addresses, and payment |
| `checkout` | Checkout with lines and shipping address |
| `warehouse` | Warehouse with stock for test variants |
| `shipping_zone` | Shipping zone with methods and channel listing |

## CI/CD Pipeline Integration

| Stage | Tests | Configuration |
|-------|-------|---------------|
| Pre-commit | Linting, type checks | `pre-commit` hooks with `ruff`, `mypy` |
| Unit tests | Fast, isolated tests | `pytest -x --no-migrations -q` |
| Integration tests | API and database tests | `pytest --reuse-db -n auto` |
| Coverage | Code coverage report | `pytest --cov=saleor --cov-report=xml` |
| App tests | Webhook and App tests | `pytest tests/apps/ -v` |

## Best Practices

- Use factory_boy factories instead of manual object creation for consistency
- Test both success and error paths for every mutation
- Verify permissions by testing with unauthenticated, customer, and staff users
- Use `@pytest.mark.django_db` on all tests that access the database
- Mock external services (payment gateways, shipping carriers) in unit tests
- Test webhook signature verification (JWS/HMAC) with both valid and invalid signatures
- Keep test fixtures composable and avoid deeply nested dependencies
- Run tests in parallel with `pytest-xdist` for faster CI pipelines
- Use `assertNumQueries` to catch N+1 query problems in resolvers

Fetch the Saleor testing and pytest documentation for exact fixture patterns, test client setup, and CI configuration before implementing.
