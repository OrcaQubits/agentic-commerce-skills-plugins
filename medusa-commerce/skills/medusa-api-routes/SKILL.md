---
name: medusa-api-routes
description: Create custom Medusa v2 API routes — file-based routing, HTTP method exports, middleware configuration, Zod validators, authentication middleware, and additional-data pattern. Use when adding REST endpoints.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Custom API Routes

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/fundamentals/api-routes` for API route overview
2. Web-search `site:docs.medusajs.com custom API route file convention` for file-based routing
3. Web-search `site:docs.medusajs.com API route middleware` for middleware configuration
4. Web-search `site:docs.medusajs.com API route validation zod` for request validation
5. Web-search `site:docs.medusajs.com additional data API routes` for the additional-data pattern

## File-Based Routing

Medusa v2 uses a file-system router under `src/api/`:

| File Path | Resulting Endpoint |
|-----------|-------------------|
| `src/api/store/custom/route.ts` | `GET/POST /store/custom` |
| `src/api/admin/custom/route.ts` | `GET/POST /admin/custom` |
| `src/api/store/custom/[id]/route.ts` | `GET/POST /store/custom/:id` |
| `src/api/custom/route.ts` | `GET/POST /custom` (no auth prefix) |

### Conventions

- File must be named `route.ts` (not `index.ts`)
- Dynamic parameters use `[param]` folder syntax
- The `store/` prefix applies storefront authentication scope
- The `admin/` prefix applies admin authentication scope
- Routes outside these prefixes have no default authentication

## HTTP Method Exports

Each `route.ts` exports named functions matching HTTP methods:

| Export Name | HTTP Method |
|-------------|-------------|
| `GET` | GET |
| `POST` | POST |
| `PUT` | PUT |
| `PATCH` | PATCH |
| `DELETE` | DELETE |

### Route Handler Skeleton

```typescript
// src/api/store/custom/route.ts
// Fetch live docs for MedusaRequest/MedusaResponse types
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework/http"

export const GET = async (req: MedusaRequest, res: MedusaResponse) => {
  const service = req.scope.resolve("my-module")
  res.json({ items: await service.listMyEntities() })
}
```

### Route with Dynamic Parameter

```typescript
// src/api/store/custom/[id]/route.ts
// Fetch live docs for path parameter access
export const GET = async (req: MedusaRequest, res: MedusaResponse) => {
  const item = await req.scope.resolve("my-module").retrieveMyEntity(req.params.id)
  res.json({ item })
}
```

## Request Validation with Zod

Medusa v2 uses Zod schemas for request body and query parameter validation:

### Validation File Convention

| Validation Target | File |
|------------------|------|
| POST/PUT/PATCH body | `validators.ts` in same directory as `route.ts` |
| Query parameters | Same `validators.ts` file |

### Validator Skeleton

```typescript
// src/api/store/custom/validators.ts
// Fetch live docs for Zod schema integration
import { z } from "zod"

export const PostStoreCustom = z.object({
  name: z.string(),
  description: z.string().optional(),
})
```

Validators are linked to routes via middleware configuration.

## Middleware Configuration

All middleware is configured in `src/api/middlewares.ts`:

```typescript
// src/api/middlewares.ts — Fetch live docs for defineMiddlewares API
import { defineMiddlewares, validateAndTransformBody } from "@medusajs/framework/http"
import { PostStoreCustom } from "./store/custom/validators"

export default defineMiddlewares({
  routes: [{ matcher: "/store/custom", method: "POST",
    middlewares: [validateAndTransformBody(PostStoreCustom)] }],
})
```

### Built-in Middleware Utilities

| Utility | Purpose |
|---------|---------|
| `validateAndTransformBody(schema)` | Validate request body with Zod |
| `validateAndTransformQuery(schema)` | Validate query parameters |
| `authenticate("customer", ["session", "bearer"])` | Require customer auth |
| `authenticate("user", ["session", "bearer"])` | Require admin auth |

## Authentication Middleware

| Route Prefix | Default Auth | Custom Auth Override |
|-------------|-------------|---------------------|
| `/admin/*` | Admin user required | Can be loosened per route |
| `/store/*` | Optional customer auth | Can require auth per route |
| `/custom/*` | None | Must add explicitly |

### Requiring Customer Authentication

```typescript
// In middlewares.ts routes array
// Fetch live docs for authenticate() options
{
  matcher: "/store/custom/me",
  middlewares: [authenticate("customer", ["session", "bearer"])],
}
```

## Additional Data Pattern

Medusa v2 supports passing extra data through built-in API routes to workflow hooks:

- Client sends extra fields in the request body under `additional_data`
- Validated by defining an `additionalDataValidator` in middleware
- Received in workflow hooks as `additional_data`

This allows extending core commerce flows (e.g., adding custom fields to product creation) without overriding API routes.

## Error Handling

| Error Type | Recommended Approach |
|-----------|---------------------|
| Validation error | Handled automatically by Zod middleware (400) |
| Not found | Throw `MedusaError` with `NOT_FOUND` type |
| Unauthorized | Handled by auth middleware (401) |
| Business logic | Throw `MedusaError` with appropriate type |
| Unexpected | Let Medusa error handler return 500 |

## Best Practices

- Use file-based routing conventions -- do not register routes programmatically
- Always validate request bodies with Zod schemas via `validateAndTransformBody`
- Resolve services from `req.scope` -- never import services directly
- Use the `additional_data` pattern to extend core routes instead of overriding them
- Apply `authenticate()` middleware explicitly for routes requiring auth outside default scopes
- Return consistent response shapes: `{ item }` for single, `{ items, count, offset, limit }` for lists
- Keep route handlers thin -- delegate business logic to workflows or services

Fetch the Medusa API route documentation for exact file conventions, middleware utilities, and Zod integration patterns before implementing.
