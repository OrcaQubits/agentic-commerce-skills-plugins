---
name: medusa-customers
description: Manage Medusa v2 customers — customer profiles, email and social authentication, customer groups, addresses, and account management. Use when working with customer data and auth.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Customer Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com customer module` for customer data model and service methods
2. Web-search `site:docs.medusajs.com auth module` for authentication providers and flows
3. Web-search `site:docs.medusajs.com customer group` for group management and pricing rules
4. Fetch `https://docs.medusajs.com/resources/references/customer` and review the `ICustomerModuleService` interface
5. Web-search `medusajs v2 auth provider social login 2026` for latest authentication patterns

## Customer Data Model

### Entity Relationships

| Entity | Relationship | Key Fields |
|--------|-------------|------------|
| **Customer** | Root | email, first_name, last_name, phone, has_account, metadata |
| **Addresses[]** | Customer → many | address fields, country_code, is_default_shipping/billing |
| **CustomerGroups[]** | Customer ↔ many | Many-to-many group membership |
| **Orders[]** | Customer → many (link) | Via Order Module link |

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | Unique identifier for the customer |
| `has_account` | boolean | `true` for registered, `false` for guest |
| `first_name` / `last_name` | string | Customer name |
| `phone` | string | Phone number |
| `metadata` | JSONB | Custom key-value data |

## Authentication Architecture

Medusa v2 separates **customer identity** from **authentication** via the Auth Module:

```
Auth Module
├── AuthIdentity
│   ├── provider_identities[] (emailpass, google, github...)
│   └── app_metadata (linked customer_id)
└── Auth Providers (built-in + custom)
```

### Authentication Flow

```
Register/Login ──> Auth Module validates ──> JWT token
  ──> Token includes auth_identity_id ──> Linked to customer_id
```

### Auth Provider Comparison

| Provider | Type | Configuration |
|----------|------|---------------|
| `emailpass` | Built-in | No external config needed |
| `google` | OAuth2 | Client ID + secret |
| `github` | OAuth2 | Client ID + secret |
| Custom | Extensible | Implement `AbstractAuthModuleProvider` |

### Email + Password Flow

| Step | Endpoint | Purpose |
|------|----------|---------|
| Register | `/auth/customer/emailpass/register` | Create auth identity |
| Login | `/auth/customer/emailpass` | Authenticate, get token |
| Create customer | `/store/customers` | Create customer profile (with token) |

### Social Login Flow (OAuth2)

| Step | Endpoint | Purpose |
|------|----------|---------|
| Initiate | `/auth/customer/{provider}` | Get redirect URL |
| Callback | `/auth/customer/{provider}/callback` | Exchange code for token |
| Create/Link | `/store/customers` | Create or link customer profile |

> **Fetch live docs** for OAuth2 callback handling, redirect URIs, and token exchange flow.

## Customer Groups

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Group name (e.g., "VIP", "Wholesale") |
| `metadata` | JSONB | Custom group data |
| `customers` | relation | Many-to-many with customers |

### Use Cases

| Use Case | Mechanism |
|----------|-----------|
| Group-specific pricing | Price List rules linked to customer groups |
| Conditional promotions | Promotion rules targeting customer groups |
| Access control | Custom middleware checking group membership |

### Key Service Methods

| Operation | Method |
|-----------|--------|
| Create group | `customerModuleService.createCustomerGroups()` |
| Add to group | `customerModuleService.addCustomerToGroup()` |
| Remove from group | `customerModuleService.removeCustomerFromGroup()` |
| List groups | `customerModuleService.listCustomerGroups()` |

## Address Management

| Field | Required | Notes |
|-------|----------|-------|
| `first_name` / `last_name` | Yes | |
| `address_1` | Yes | Street address |
| `city` | Yes | |
| `country_code` | Yes | ISO 2-letter code |
| `postal_code` | Conditional | Required by country |
| `is_default_shipping` / `is_default_billing` | No | Default flags |

| Workflow | Purpose |
|----------|---------|
| `createCustomerAddressesWorkflow` | Add new address |
| `updateCustomerAddressesWorkflow` | Update existing address |
| `deleteCustomerAddressesWorkflow` | Remove address |

## Store API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/store/customers` | POST | Create customer profile |
| `/store/customers/me` | GET | Retrieve authenticated customer |
| `/store/customers/me` | POST | Update customer profile |
| `/store/customers/me/addresses` | GET/POST | List/add addresses |
| `/store/customers/me/addresses/:id` | POST/DELETE | Update/remove address |

All `/store/customers/me` routes require a valid JWT in the `Authorization` header.

## Admin API Routes

| Route Pattern | Method | Purpose |
|---------------|--------|---------|
| `/admin/customers` | GET/POST | List/create customers |
| `/admin/customers/:id` | GET/POST | Retrieve/update customer |
| `/admin/customer-groups` | GET/POST | Manage groups |
| `/admin/customer-groups/:id/customers` | POST | Add customers to group |

> **Fetch live docs** for request body shapes and query parameters on each route.

## Best Practices

### Authentication
- Use the **Auth Module** for all authentication -- never implement custom auth logic outside it
- Support both `emailpass` and at least one OAuth2 provider for user convenience
- Store provider-specific data in `provider_identities`, not in customer metadata
- Always link auth identities to customer profiles via `app_metadata.customer_id`

### Customer Data
- Use `has_account` to distinguish registered customers from guest checkouts
- Store loyalty points, preferences, and custom attributes in `metadata`
- Use customer groups for segmentation -- avoid duplicating group logic in app code

### Address Management
- Validate addresses against country-specific requirements (postal code formats)
- Set `is_default_shipping` and `is_default_billing` to streamline checkout

### Security
- Validate JWT tokens on every authenticated request
- Scope Store API customer data to the authenticated customer only
- Never expose customer lists or group memberships via the Store API

Fetch the Medusa v2 customer module and auth module documentation for exact service method signatures, auth provider configuration, and JWT handling before implementing.
