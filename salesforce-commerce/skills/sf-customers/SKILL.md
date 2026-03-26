---
name: sf-customers
description: Manage Salesforce Commerce customers — B2C (customer objects, customer groups, segmentation, SLAS authentication, wishlists) and B2B (Account/Contact, buyer groups, buyer permissions, self-registration). Both platforms share Data Cloud for unified customer profiles and consent management.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-customers

## Before Writing Code

**CRITICAL**: Always fetch live documentation BEFORE implementing customer management features.

1. **B2C Commerce Customer APIs**
   - Web-search: "Salesforce B2C Commerce Cloud SCAPI Shopper Customers API 2026"
   - Web-fetch official Salesforce B2C customer management guides

2. **SLAS Authentication**
   - Web-search: "Salesforce Commerce Cloud SLAS authentication documentation 2026"
   - Web-fetch SLAS authentication flow documentation

3. **B2B Commerce Buyer Management**
   - Web-search: "Salesforce B2B Commerce buyer groups permissions 2026"
   - Web-fetch B2B buyer management and self-registration guides

4. **Data Cloud Integration**
   - Web-search: "Salesforce Data Cloud unified customer profile Commerce integration 2026"
   - Web-fetch Data Cloud customer data sync and consent management documentation

**Why:** Customer API versions, SLAS token flows, B2B permission models, and Data Cloud connector capabilities evolve frequently. Live docs ensure correct schemas and compliance with GDPR/CCPA.

## Conceptual Architecture

### B2C Customer Model

| Object | Description |
|--------|-------------|
| Customer Profile | Registration data, preferences, custom attributes for personalization |
| Addresses | Billing and shipping addresses with validation and default selection |
| Payment Instruments | Tokenized payment methods (cards, wallets) -- never raw card data |
| Order History | Past orders, returns, order status tracking |
| Wishlists | Multiple product lists per customer; public, private, or shared visibility |
| Custom Attributes | Extended profile fields for segmentation and personalization |

### B2C Customer Groups and Segmentation

| Concept | Description |
|---------|-------------|
| Dynamic Groups | Auto-assigned based on attributes (VIP status, location, lifetime value) |
| Static Groups | Manually assigned membership for targeted campaigns |
| Group-based Pricing | Price books assigned to specific customer groups |
| Group-based Promotions | Exclusive offers for specific segments |
| Customer Segments | Rule-based segments for dynamic targeting and promotion qualification |
| Customer Lists | Curated lists for marketing campaigns and email targeting |

### SLAS Authentication

| Flow | Purpose |
|------|---------|
| Guest Login | Anonymous shopper sessions for browsing and checkout |
| Registered Login | Authenticated sessions with username/password |
| Social Login | OAuth integration (Google, Facebook, Apple) |
| Token Refresh | Session extension via refresh tokens |
| Session Merge | Basket merge when guest converts to registered customer |

**Token lifecycle:** Access tokens have short TTL; refresh tokens extend the session. The Commerce SDK handles token refresh transparently. Store tokens securely (httpOnly cookies preferred over localStorage).

### Shopper Customers API (SCAPI)

| Operation | Description |
|-----------|-------------|
| Profile CRUD | Create, read, update customer profiles |
| Address Management | Add, update, delete, set default addresses |
| Payment Instruments | Tokenize and store payment methods |
| Password Management | Reset and update passwords |
| Authentication | Login, logout, token refresh |

Fetch live docs for current SCAPI endpoint versions and request/response schemas before implementing.

### B2C Wishlists

| Feature | Description |
|---------|-------------|
| Multiple Lists | Customers can create and name multiple wishlists |
| Item Operations | Add, remove, move items between lists |
| Sharing | Share via email or link with configurable privacy |
| Visibility | Public, private, or shared list settings |

### B2B Customer Model

| Object | Description |
|--------|-------------|
| Business Accounts | Company entities with tax IDs, credit terms, parent/child hierarchies |
| Contacts | Individual users associated with accounts, with roles (purchaser, approver) |
| Buyer Groups | Control product entitlements, catalog visibility, and price book access |
| Buyer Permissions | Browse, add-to-cart, checkout, approval workflow, and budget controls |
| Self-Registration | Portal user registration with account request workflow and verification |
| Account Teams | Sales reps and support teams assigned to accounts |

### B2B Permission Levels

| Permission | Controls |
|------------|----------|
| Browse | Product and price visibility |
| Add to Cart | Ability to build orders |
| Checkout | Ability to complete purchases |
| Approval | Order approval for certain users/amounts |
| Budget | Spending limits per user or group |
| Quote Request | Ability to request quotes from sales |

### B2B Account Hierarchy

Parent/child account relationships model enterprise structures. Child accounts inherit default settings from parents but can override pricing, catalog visibility, and shipping preferences. Contact roles (decision maker, influencer, purchaser) provide sales intelligence.

### Data Cloud Integration

| Capability | Description |
|------------|-------------|
| Profile Unification | Merge B2C and B2B data into a single customer view via identity resolution |
| Consent Management | GDPR/CCPA compliance -- capture, respect, and audit consent across categories |
| Bi-directional Sync | Real-time for critical updates; batch for historical data loads |
| Data Mapping | Field mapping between Commerce Cloud and Data Cloud schemas |
| Conflict Resolution | Handle concurrent updates from multiple systems |
| Profile Enrichment | Append third-party data to customer profiles |

### Consent Categories

| Category | Purpose |
|----------|---------|
| Marketing | Email, SMS, push notification consent |
| Analytics | Browsing behavior and usage tracking |
| Personalization | Product recommendations and content targeting |
| Data Processing | General GDPR data processing consent |

All consent changes must be logged with timestamps for audit trail compliance. Honor right-to-be-forgotten requests with complete data deletion workflows.

## Best Practices

### B2C Customer Management
- Use SCAPI Shopper Customers API for headless storefronts.
- Implement SLAS with correct grant types (guest, credentials, refresh).
- Store tokens securely; refresh before expiration.
- Merge guest baskets on login to preserve shopping context.

### B2B Customer Management
- Model enterprise structures with parent/child account hierarchies.
- Show/hide UI features based on buyer permissions.
- Implement multi-level approval workflows for large orders.
- Validate business email domains and tax IDs during self-registration.

### Data Cloud and Compliance
- Capture consent before syncing any customer data to Data Cloud.
- Configure identity resolution rules carefully to avoid false matches.
- Use real-time sync for profile updates and consent changes; batch for order history.
- Honor data deletion requests immediately; maintain audit trail for compliance.

### Performance
- Cache customer group lookups; lazy-load addresses on demand.
- Paginate order history; index frequently queried custom attributes.
- Update consent asynchronously to avoid checkout delays.

---

Fetch the SCAPI Shopper Customers reference, SLAS authentication guide, B2B buyer management docs, and Data Cloud connector documentation for exact API schemas, token flows, and configuration before implementing.
