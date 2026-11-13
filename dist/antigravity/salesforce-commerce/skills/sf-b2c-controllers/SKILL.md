---
name: sf-b2c-controllers
description: >
  Build SFRA controllers — server.get/post/use route handlers, middleware chain
  with server.append/prepend/replace, CSRF protection, form validation, response
  rendering, and route-level caching. Use when implementing request handling in
  B2C Commerce.
---

# sf-b2c-controllers

Build SFRA controllers for request handling in Salesforce B2C Commerce Cloud.

## Before Writing Code

**Fetch live documentation FIRST:**

1. **Web-search** for:
   - "Salesforce B2C Commerce SFRA controllers documentation 2026"
   - "SFCC server module middleware patterns"
   - "B2C Commerce controller CSRF protection best practices"

2. **Web-fetch** official sources:
   - `github.com/SalesforceCommerceCloud/storefront-reference-architecture` (SFRA controllers)
   - Salesforce B2C Commerce server module API reference

3. **Verify** before coding: current server module syntax, middleware chain methods, CSRF validation requirements, form validation patterns in latest SFRA.

## Conceptual Architecture

### Controller Basics

Controllers are **route handlers** defined using the `server` module. Routes follow the naming convention `ControllerName-ActionName` (e.g., `Product-Show`, `Cart-AddProduct`).

- Controller file: `controllers/Product.js`
- Route: `Product-Show`
- URL: `https://site.com/Product-Show?pid=12345`

Every controller file ends with `module.exports = server.exports();`

### Server Module Methods

| Method | HTTP | Purpose | Example |
|--------|------|---------|---------|
| `server.get(name, ...mw, handler)` | GET | Display pages | `Product-Show`, `Cart-Show` |
| `server.post(name, ...mw, handler)` | POST | Form submissions | `Cart-AddProduct`, `Account-Register` |
| `server.use(name, ...mw, handler)` | Any | Shared logic, API endpoints | Method-agnostic handlers |

### Middleware Chain

Middleware functions execute **left to right** before the final handler. Each must call `next()` to continue the chain.

```
server.post('Action',
  server.middleware.https,        -> 1. Force HTTPS
  csrfProtection.validateRequest, -> 2. Validate CSRF
  userLoggedIn.validateLoggedIn,  -> 3. Require login
  function (req, res, next) {}    -> 4. Handler
);
```

Common built-in middleware:
- `server.middleware.https` -- force HTTPS
- `csrfProtection.validateRequest` -- CSRF token validation
- `csrfProtection.generateToken` -- generate CSRF token for forms
- `userLoggedIn.validateLoggedIn` -- require authenticated user
- `consentTracking.consent` -- consent tracking check

### Extend vs Replace

| Method | What Happens | When to Use |
|--------|-------------|-------------|
| `server.extend(base)` | Inherit all base routes | Always start with this |
| `server.append('Route', fn)` | Run AFTER base handler | Add data to response, logging, analytics |
| `server.prepend('Route', fn)` | Run BEFORE base handler | Validation, guards, tracking |
| `server.replace('Route', fn)` | Completely override base | Fundamentally different logic (rare) |
| `server.get/post('Route', fn)` | Define new route | New functionality not in base |

```javascript
// Pattern: Extend a base controller
var base = module.superModule;
server.extend(base);
// Fetch live docs for append/prepend behavior
```

### Route Handling Lifecycle

```
HTTP Request
  -> Route resolution (cartridge path, left-to-right)
  -> server.use middleware (guards, validation)
  -> server.prepend extensions
  -> Base route handler (if extended)
  -> server.append extensions
  -> Response (render / json / redirect)
```

### Response Types

| Method | Use Case |
|--------|----------|
| `res.render(template, data)` | Render ISML template (HTML page) |
| `res.json(object)` | Return JSON (AJAX responses) |
| `res.redirect(url)` | HTTP redirect |
| `res.setStatusCode(code)` | Set HTTP status (404, 500, etc.) |
| `res.setViewData(data)` | Set data for middleware chain sharing |
| `res.getViewData()` | Get data set by previous middleware |

### Route-Level Caching

Cache GET responses via property assignment on `res`:

| Property | Type | Values |
|----------|------|--------|
| `res.cachePeriod` | Number | Duration value (e.g., `24`) |
| `res.cachePeriodUnit` | String | `'minutes'`, `'hours'`, `'days'` |

Never cache: cart, checkout, account pages. Always cache: product pages, category pages.

### CSRF Protection

All **state-changing requests** (POST, DELETE) must validate CSRF tokens. The token is generated in the controller, passed to the ISML template as a hidden form field, and validated on submission via `csrfProtection.validateRequest` middleware.

### Form Validation

Server-side form validation uses `server.forms.getForm('formName')`. Form definitions live in `forms/default/*.xml`. Always validate server-side -- never trust client-side validation alone.

## Best Practices

### Route Design
- RESTful naming: `Product-Show` (view), `Cart-AddProduct` (action)
- Separate GET and POST -- never use `server.use` for method-specific routes
- Keep controllers thin -- move business logic to models and `scripts/` helpers

### Middleware
- Chain security checks before business logic (HTTPS, CSRF, auth)
- Always call `next()` -- forgetting breaks the chain silently
- Create reusable middleware in `scripts/middleware/`
- Use `server.middleware.https` for all sensitive operations

### Response Patterns
- Consistent JSON: `{ success: boolean, data?: object, errors?: array }`
- Set appropriate status codes (404, 400, 500)
- Use `res.setViewData` / `res.getViewData` to share data across middleware chain

### Security
- CSRF protection on all state-changing operations
- Sanitize all user inputs (`req.querystring`, `req.form`)
- Wrap data mutations in `Transaction.wrap()`
- Log security events with `dw/system/Logger`

Fetch the SFRA GitHub repository and server module API reference for exact method signatures, middleware patterns, and req/res property details before implementing.
