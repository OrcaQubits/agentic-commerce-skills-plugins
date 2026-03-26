---
name: saleor-customers
description: Manage Saleor customers and staff — customer accounts, registration, addresses, staff users, permission groups, and authentication. Use when working with user management.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Customer and Staff Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io customers accounts registration` for customer account model and registration flow
2. Web-search `site:docs.saleor.io staff users permissions groups` for staff management and permission system
3. Web-search `site:docs.saleor.io authentication JWT tokens` for authentication flow and token handling
4. Fetch `https://docs.saleor.io/docs/developer/users` and review User model, addresses, and account operations
5. Web-search `site:docs.saleor.io permission groups MANAGE_PRODUCTS MANAGE_ORDERS` for the full list of available permissions

## Customer Model

Saleor uses a single `User` entity for both customers and staff. The `isStaff` flag distinguishes between them.

| Field | Description |
|-------|-------------|
| `id` | Unique user identifier |
| `email` | Email address (unique, used for login) |
| `firstName` | Customer first name |
| `lastName` | Customer last name |
| `isActive` | Whether the account is enabled |
| `isStaff` | Whether the user has dashboard access |
| `dateJoined` | Account creation timestamp |
| `lastLogin` | Most recent login timestamp |
| `metadata` | Public key-value metadata |
| `privateMetadata` | Staff-only key-value metadata |
| `languageCode` | Preferred language |
| `defaultShippingAddress` | Default shipping address |
| `defaultBillingAddress` | Default billing address |

## Customer Registration and Login

### Registration Flow

| Step | Mutation | Description |
|------|----------|-------------|
| 1. Register | `accountRegister` | Create account with email and password |
| 2. Confirm email | `confirmAccount` | Verify email with token from confirmation email |
| 3. Active account | -- | Account is active after confirmation |

### Registration Input

| Field | Required | Description |
|-------|----------|-------------|
| `email` | Yes | Customer email address |
| `password` | Yes | Account password |
| `firstName` | No | First name |
| `lastName` | No | Last name |
| `redirectUrl` | Yes | URL for email confirmation link |
| `channel` | Yes | Channel slug for channel-specific registration |
| `languageCode` | No | Preferred language for communications |
| `metadata` | No | Initial metadata key-value pairs |

### Login Flow

| Step | Mutation | Description |
|------|----------|-------------|
| 1. Obtain tokens | `tokenCreate` | Provide email + password; returns JWT access and refresh tokens |
| 2. Use access token | -- | Include in `Authorization: Bearer <token>` header |
| 3. Refresh token | `tokenRefresh` | Exchange refresh token for new access token |
| 4. Verify token | `tokenVerify` | Check if a token is still valid |

## JWT Authentication Flow

| Token Type | Lifetime | Purpose |
|------------|----------|---------|
| Access token | Short-lived (configurable, default ~5 min) | Authenticate API requests |
| Refresh token | Long-lived (configurable) | Obtain new access tokens |
| CSRF token | Per-session | Protect against cross-site request forgery |

### Token Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Login | `tokenCreate` | Returns `token`, `refreshToken`, `csrfToken` |
| Refresh | `tokenRefresh` | Requires `refreshToken`; returns new `token` |
| Verify | `tokenVerify` | Returns `isValid` and decoded payload |
| Deactivate all | `tokensDeactivateAll` | Invalidate all tokens for the user |

> **Fetch live docs** for token expiration configuration and any changes to the JWT authentication model.

## Customer Addresses

Each customer can store multiple addresses with defaults for shipping and billing:

| Field | Description |
|-------|-------------|
| `firstName` | Address first name |
| `lastName` | Address last name |
| `companyName` | Optional company name |
| `streetAddress1` | Primary street address |
| `streetAddress2` | Additional address line |
| `city` | City name |
| `postalCode` | Postal or ZIP code |
| `country` | ISO 3166-1 alpha-2 country code |
| `countryArea` | State or province |
| `phone` | Phone number |
| `isDefaultShippingAddress` | Default for shipping |
| `isDefaultBillingAddress` | Default for billing |

### Address Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create address | `accountAddressCreate` | Customer self-service |
| Update address | `accountAddressUpdate` | Customer self-service |
| Delete address | `accountAddressDelete` | Customer self-service |
| Set default | `accountSetDefaultAddress` | Set shipping or billing default |
| Admin create | `addressCreate` | Staff creating address for a customer |
| Admin update | `addressUpdate` | Staff updating customer address |
| Admin delete | `addressDelete` | Staff deleting customer address |

## Staff Users vs Customers

| Aspect | Customer | Staff |
|--------|----------|-------|
| `isStaff` | `false` | `true` |
| Dashboard access | No | Yes |
| API scope | Storefront queries, own account | Admin queries, assigned permissions |
| Creation | `accountRegister` or `customerCreate` | `staffCreate` |
| Permissions | None (implicit storefront access) | Assigned via permission groups |

### Staff Management Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create staff | `staffCreate` | Set email, permissions, groups |
| Update staff | `staffUpdate` | Modify details and permissions |
| Delete staff | `staffDelete` | Remove staff user |

## Permission Groups

Permission groups bundle permissions and assign them to staff users:

| Operation | Mutation |
|-----------|----------|
| Create group | `permissionGroupCreate` |
| Update group | `permissionGroupUpdate` |
| Delete group | `permissionGroupDelete` |

### Key Permissions

| Permission | Grants Access To |
|------------|-----------------|
| `MANAGE_PRODUCTS` | Products, categories, collections, product types |
| `MANAGE_ORDERS` | Orders, fulfillments, draft orders |
| `MANAGE_USERS` | Customer accounts and staff users |
| `MANAGE_STAFF` | Staff accounts and permission groups |
| `MANAGE_DISCOUNTS` | Vouchers and promotions |
| `MANAGE_SHIPPING` | Shipping zones and methods |
| `MANAGE_CHANNELS` | Channel configuration |
| `MANAGE_CHECKOUTS` | Checkout operations |
| `MANAGE_APPS` | App installation and configuration |
| `MANAGE_SETTINGS` | Site-wide settings |
| `MANAGE_TRANSLATIONS` | Content translations |
| `HANDLE_PAYMENTS` | Payment processing and transactions |
| `MANAGE_GIFT_CARD` | Gift card creation and management |
| `MANAGE_PAGE_TYPES_AND_ATTRIBUTES` | Page types and attributes |

> **Fetch live docs** for the complete `PermissionEnum` -- additional permissions may exist for plugins and newer features.

## Account Management Mutations

| Operation | Mutation | Actor |
|-----------|----------|-------|
| Request password reset | `requestPasswordReset` | Customer |
| Set new password | `setPassword` | Customer (with token) |
| Change password | `passwordChange` | Customer (authenticated) |
| Request email change | `requestEmailChange` | Customer |
| Confirm email change | `confirmEmailChange` | Customer (with token) |
| Update account | `accountUpdate` | Customer (own profile) |
| Delete account | `accountDelete` | Customer (with token) |
| Admin create customer | `customerCreate` | Staff |
| Admin update customer | `customerUpdate` | Staff |
| Admin delete customer | `customerDelete` | Staff |
| Admin bulk delete | `customerBulkDelete` | Staff |

## Best Practices

- Use `accountRegister` for self-service registration and `customerCreate` for staff-created accounts
- Always configure `redirectUrl` for email confirmation and password reset to point to your storefront
- Store custom customer data in `metadata` (public) or `privateMetadata` (staff-only)
- Use permission groups to organize staff access -- avoid assigning permissions directly to users
- Implement token refresh logic in your storefront to maintain sessions without re-authentication
- Validate email confirmation before allowing customers to place orders
- Use `channel` parameter in registration to send channel-specific confirmation emails
- Handle `tokensDeactivateAll` for security-sensitive operations like password changes
- Prefer `accountAddressCreate` for customer-facing flows and `addressCreate` for admin flows

Fetch the Saleor authentication and user management documentation for exact mutation inputs, permission enums, and token handling patterns before implementing.
