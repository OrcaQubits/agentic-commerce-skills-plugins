---
name: shopify-customers
description: >
  Manage Shopify customers — Customer Account API, new vs classic accounts,
  Multipass SSO, customer segmentation, B2B company accounts, metafields, and
  marketing consent. Use when working with Shopify customer data.
---

# Shopify Customer Management

## Before writing code

**Fetch live docs**:
1. Web-search `site:shopify.dev customer account api` for Customer Account API
2. Web-search `site:shopify.dev customer graphql admin api` for customer mutations
3. Web-search `site:shopify.dev multipass` for SSO integration
4. Web-search `site:shopify.dev customer segmentation api` for segmentation queries
5. Web-search `site:shopify.dev b2b company accounts` for B2B features

## Customer Account Types

### New Customer Accounts

Modern, Shopify-hosted accounts:
- Passwordless login (email verification code or Shop app)
- OAuth-based API access (Customer Account API)
- Customizable with account extensions
- Supports order history, addresses, profile management
- Recommended for all new stores

### Classic Customer Accounts

Legacy accounts:
- Password-based login
- Liquid-based pages (`customers/login.liquid`, `customers/account.liquid`)
- Being replaced by new customer accounts
- Still supported but no longer receiving new features

## Customer Account API

For headless/custom account experiences (used in Hydrogen):
- OAuth 2.0 authentication flow
- Access customer data: orders, addresses, profile
- Customer-initiated actions: update profile, manage addresses
- Separate from Admin API — scoped to the authenticated customer

> **Fetch live docs**: Web-search `site:shopify.dev customer account api reference` for current OAuth flow endpoints, available queries, and token handling.

## Admin API Customer Operations

### Key Mutations

| Operation | Mutation | Notes |
|-----------|----------|-------|
| Create customer | `customerCreate` | Email, name, addresses |
| Update customer | `customerUpdate` | Partial updates |
| Delete customer | `customerDelete` | Removes customer record |
| Add tags | `tagsAdd` | Tagging for segmentation |
| Set metafield | `metafieldsSet` | Custom customer data |
| Send invite | `customerSendAccountInviteEmail` | Account activation email |
| Merge customers | `customerMerge` | Combine duplicate records |

> **Fetch live docs** for each mutation's input fields — `CustomerInput` and related types change across API versions.

### Minimal Query Pattern

```graphql
# Pattern: query customer with orders and metafields
# Fetch live docs for current available fields
query Customer($id: ID!) {
  customer(id: $id) {
    id
    firstName
    lastName
    email
    phone
    tags
    addresses { address1 city province country zip }
    orders(first: 10) {
      edges {
        node { id name totalPrice { amount currencyCode } }
      }
    }
    metafields(first: 5) {
      edges {
        node { namespace key value type }
      }
    }
  }
}
```

### Customer Search

```graphql
# Search customers by email, name, or other fields
query Customers($query: String!) {
  customers(first: 10, query: $query) {
    edges { node { id email firstName lastName } }
  }
}
# query: "email:customer@example.com" or "first_name:John"
```

> **Fetch live docs** for query filter syntax and searchable fields.

## Multipass SSO

Single sign-on for Shopify stores (Shopify Plus only):
- Encrypt customer data with Multipass secret → generate token
- Redirect to `{store}.myshopify.com/account/login/multipass/{token}`
- Customer is logged in without entering credentials
- Used for: external identity providers, membership sites, B2B portals

### Multipass Flow

```
Your site → Encrypt customer JSON with Multipass secret → Base64 token
→ Redirect to Shopify /account/login/multipass/{token}
→ Customer auto-logged in
```

Required customer data in the token: `email` (required), plus optional `first_name`, `last_name`, `tag_string`, `return_to`, `remote_ip`.

> **Fetch live docs**: Web-search `site:shopify.dev multipass` for current encryption algorithm, token format, and required fields. The encryption method (AES-128-CBC + HMAC-SHA256) is stable but verify key derivation steps.

## Customer Segmentation

Filter customers based on criteria:
- ShopifyQL-style filters: `orders_count > 5 AND total_spent > 100`
- Used for marketing campaigns and analytics
- Accessible via Admin API and Shopify admin
- Supports: order history, spending, location, tags, dates, custom attributes

> **Fetch live docs**: Web-search `site:shopify.dev customer segmentation filters` for current filter syntax and available attributes.

## B2B (Company Accounts)

Shopify Plus feature:
- **Companies** with multiple **locations**
- Company-specific catalogs and price lists
- Payment terms (Net 30, Net 60)
- Draft order workflows for B2B purchasing
- Company contacts linked to customer records

### B2B Data Model

```
Company
├── Locations (billing/shipping)
├── Contacts (linked to customers)
├── Catalogs (company-specific pricing)
│   └── Price Lists
└── Payment Terms
```

> **Fetch live docs**: Web-search `site:shopify.dev b2b api company` for company mutations, catalog assignment, and payment terms configuration.

## Marketing Consent

GDPR/privacy compliance:
- Email marketing consent: `SUBSCRIBED`, `NOT_SUBSCRIBED`, `PENDING`, `UNSUBSCRIBED`
- SMS marketing consent (separate from email)
- Must honor consent status in all communications
- Consent recorded with timestamp and source
- Manage via `customerEmailMarketingConsentUpdate` and `customerSmsMarketingConsentUpdate`

> **Fetch live docs** for consent mutation input fields and consent state transition rules.

## Best Practices

- Use new customer accounts (not classic) for new stores
- Implement Multipass SSO for stores with external auth systems
- Always check and respect marketing consent before sending communications
- Store custom customer data in metafields (not tags for structured data)
- Use customer segmentation for targeted marketing
- Handle GDPR data requests via mandatory webhooks (`customers/data_request`, `customers/redact`)
- Use `customerMerge` for duplicate records instead of manual data transfer
- For B2B: set up companies and catalogs before onboarding wholesale customers

Fetch the Shopify Customer Account API, Multipass, and B2B documentation for exact OAuth flows, encryption details, mutation inputs, and segmentation syntax before implementing.
