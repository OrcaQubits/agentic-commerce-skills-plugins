---
name: sf-security
description: Implement Salesforce Commerce security — SLAS OAuth 2.1, session management, CSRF tokens, XSS prevention (isprint encoding in ISML), PCI compliance, RBAC in Business Manager, OWASP Top 10 protections, and Salesforce Shield for B2B. Use when implementing authentication or security controls.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# sf-security

Implement Salesforce Commerce security across B2C and B2B platforms.

## Before Writing Code

Always fetch the latest official documentation BEFORE implementing security controls:

- **SLAS Security**: WebSearch "Salesforce SLAS OAuth 2.1 security guide 2026" and WebFetch official Commerce API docs
- **B2C Commerce Security**: WebSearch "Salesforce B2C Commerce security best practices 2026" and WebFetch the security reference
- **Salesforce Security Guide**: WebSearch "Salesforce security guide OWASP 2026" and WebFetch official documentation
- **PCI DSS Requirements**: WebSearch "PCI DSS v4 requirements ecommerce 2026" for current compliance standards

**Why:** OAuth flows, CSRF protection patterns, encoding modes, and PCI requirements evolve. Live docs ensure correct implementation of current security standards.

## Conceptual Architecture

### Authentication

**SLAS (B2C Commerce) -- OAuth 2.1 with PKCE:**

| Client Type | Flow | Use Case |
|-------------|------|----------|
| Public (browser/PWA Kit) | `authorization_code_pkce` | Guest and registered users |
| Private (server-side) | `client_credentials` | Guest sessions |
| Private (server-side) | `authorization_code` | Registered users |
| Any | Refresh token | Session extension |

PKCE (Proof Key for Code Exchange) is required for all public client flows. Guest tokens enable anonymous shopping before login.

**Salesforce OAuth (B2B Commerce):**

| Flow | Use Case |
|------|----------|
| Connected Apps | OAuth application registration |
| JWT Bearer | Server-to-server authentication |
| Web Server Flow | User authorization with redirect |

**Session Management:**
- Secure, random, unpredictable session IDs
- Token expiration with renewal handling
- Secure cookies: HttpOnly, Secure, SameSite attributes
- Session invalidation on logout, timeout, or security events

**Token Lifecycle:**

| Token | Typical TTL | Storage |
|-------|-------------|---------|
| Access Token | 30 minutes | Memory or httpOnly cookie |
| Refresh Token | 30 days | httpOnly cookie (never localStorage) |
| CSRF Token | Per request | Hidden form field or custom header |

### XSS Prevention

**B2C Commerce (ISML):**

| Encoding Mode | Context |
|---------------|---------|
| `htmlcontent` | HTML body text |
| `htmlsinglequote` / `htmldoublequote` | HTML attributes |
| `jshtml` | JavaScript strings in HTML |
| `jsonvalue` | JSON data |
| `uricomponent` | URL parameters |

Always use `<isprint>` with explicit encoding. Never use raw `${variable}` for user-controlled data. Set Content Security Policy headers to restrict script sources.

**B2B Commerce (LWC):**
- Automatic encoding in Lightning template expressions
- Lightning Web Security (LWS) replaces Locker Service (Spring '23+)
- Use `textContent` instead of `innerHTML` in JavaScript
- Use `lightning-formatted-*` components for safe rendering

### Content Security Policy

| Directive | Purpose |
|-----------|---------|
| `default-src` | Fallback for all resource types |
| `script-src` | Allowed script sources (restrict to self and trusted CDNs) |
| `style-src` | Allowed stylesheet sources |
| `img-src` | Allowed image sources |
| `connect-src` | Allowed API/fetch targets |
| `frame-ancestors` | Clickjacking protection |

Configure CSP headers in Business Manager or via server configuration. Use `nonce` or `hash` for inline scripts rather than `unsafe-inline`.

### CSRF Protection

**B2C Commerce:** Validate tokens with `CSRFProtection.validateRequest()` in controllers. Generate tokens with `CSRFProtection.generateToken()`. Include hidden token fields in all state-changing forms. Use double-submit cookie pattern for AJAX.

**B2B Commerce:** Built-in Salesforce CSRF protection. `<lightning-input>` includes tokens automatically. `@AuraEnabled` Apex methods have CSRF protection.

### Input Validation

| Layer | Technique |
|-------|-----------|
| Client-side | HTML5 validation, JavaScript checks (UX only, not security) |
| Server-side | Whitelist validation, type checking, length limits |
| Form definitions | SFCC XML form definitions with validation rules |
| Query API | Parameterized queries -- never string concatenation |

Always validate on the server. Client-side validation is a convenience, not a security measure.

### PCI Compliance

| Requirement | Implementation |
|-------------|---------------|
| Tokenization | Never store raw card numbers; use tokenized payment methods |
| SAQ-A Scope | Use hosted payment fields to minimize PCI scope |
| TLS 1.2+ | Enforce for all API communication and payment processing |
| Log Masking | No card data in application logs |
| Gateway | Use Salesforce Commerce Payments or validated third-party processors |

### RBAC (Role-Based Access Control)

**B2C Commerce:** Business Manager roles (Admin, Merchant, Content) with granular, site-specific permissions. Custom roles for organization-specific needs.

**B2B Commerce:** Salesforce profiles and permission sets. Buyer permissions control ordering (browse, cart, checkout, approve). Account hierarchy restricts visibility based on relationships.

**B2B Sharing Rules:**
- Organization-wide defaults set baseline visibility
- Sharing rules grant additional access to specific groups
- Account hierarchies provide implicit sharing up the chain
- Manual sharing for ad-hoc access grants

### OWASP Top 10 Protections

| Threat | Mitigation |
|--------|------------|
| Injection | Parameterized queries via Query API; input whitelisting |
| Broken Auth | SLAS/OAuth best practices; MFA where available; strong password policies |
| Sensitive Data Exposure | Salesforce Shield encryption at rest (B2B); TLS in transit; log masking |
| Security Misconfiguration | Disable dev features in production; change default credentials; suppress stack traces |
| Access Control | Authorization checks on every request; least privilege principle |
| Monitoring | Log authentication events, failed logins, suspicious activity |

## Best Practices

### Implementation
- Always encode output using the correct mode for context (HTML, JS, URL, JSON).
- Validate input at the boundary -- whitelist acceptable values, reject everything else.
- Implement CSRF protection on all state-changing operations.
- Enforce TLS 1.2+ for all communications.

### Credentials and Access
- Rotate API keys, client secrets, and certificates on a regular schedule.
- Grant minimum necessary permissions (least privilege).
- Restrict customer data access to authorized users and systems only.
- Store credentials in Business Manager services or Salesforce Named Credentials, never in code.

### Operations
- Log authentication events, failed login attempts, and suspicious activity.
- Audit code for security issues regularly; conduct penetration testing.
- Keep dependencies updated; scan for known vulnerabilities.
- Maintain an incident response plan for security breaches.

---

Fetch the SLAS OAuth 2.1 guide, B2C Commerce security reference, and Salesforce OWASP documentation for exact token flows, encoding specifications, and compliance requirements before implementing.
