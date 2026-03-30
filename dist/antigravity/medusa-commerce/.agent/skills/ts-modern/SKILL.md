---
name: ts-modern
description: >
  Write modern TypeScript for Medusa v2 — DML type inference, service generics,
  container typing, strict mode constraints, utility types, and module interface
  patterns. Use when writing TypeScript in Medusa projects.
---

# Modern TypeScript for Medusa v2

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com typescript types modules` for Medusa type patterns
2. Web-search `site:www.typescriptlang.org docs handbook` for latest TypeScript features
3. Web-search `site:docs.medusajs.com DML infer type model` for DML type inference
4. Fetch `https://docs.medusajs.com/learn/fundamentals/modules/service-factory` for service generics
5. Web-search `site:docs.medusajs.com container dependency injection resolve` for container typing

## TypeScript Configuration in Medusa

Medusa v2 projects use strict TypeScript with specific compiler options:

| Option | Value | Purpose |
|--------|-------|---------|
| `strict` | `true` | Enable all strict type checks |
| `target` | `ES2021` | Modern JS output |
| `module` | `CommonJS` | Module system |
| `moduleResolution` | `node` | Node.js module resolution |
| `esModuleInterop` | `true` | CJS/ESM interop |
| `skipLibCheck` | `true` | Skip declaration file checks |
| `declaration` | `true` | Generate `.d.ts` files |
| `outDir` | `.medusa/server` | Build output directory |

## DML Type Inference

### InferTypeOf Pattern

Medusa generates TypeScript types from DML model definitions. Use `InferTypeOf` to derive entity types without manual interface duplication:

```ts
// Fetch live docs for InferTypeOf import path
// and exact DML-to-type mapping behavior
import { InferTypeOf } from "@medusajs/framework/types"
```

| DML Field | Inferred TypeScript Type |
|-----------|--------------------------|
| `.text()` | `string` |
| `.number()` | `number` |
| `.boolean()` | `boolean` |
| `.dateTime()` | `Date` |
| `.json()` | `Record<string, unknown>` |
| `.enum(values)` | Union literal type |
| `.id()` | `string` |
| `.hasOne(Model)` | Inferred model type |
| `.hasMany(Model)` | Array of inferred model type |
| `.belongsTo(Model)` | Inferred model type |
| `.nullable()` | `T | null` |

## Service Generics

### MedusaService Factory

The `MedusaService` factory generates a typed service class from DML models:

```ts
// Fetch live docs for MedusaService generic
// signature and generated method types
class MyService extends MedusaService({ MyModel }) {}
```

### Generated Method Signatures

| Generated Method | Return Type | Purpose |
|-----------------|-------------|---------|
| `list(filters, config)` | `Promise<T[]>` | List with filters and pagination |
| `retrieve(id, config)` | `Promise<T>` | Get single entity by ID |
| `create(data)` | `Promise<T>` | Create one entity |
| `update(data)` | `Promise<T>` | Update entity by ID |
| `delete(id)` | `Promise<void>` | Delete entity by ID |
| `listAndCount(filters, config)` | `Promise<[T[], number]>` | List with total count |
| `softDelete(id)` | `Promise<T>` | Soft delete entity |
| `restore(id)` | `Promise<T>` | Restore soft-deleted entity |

Custom methods added to the service class are fully typed alongside generated ones.

## Container Typing

### Dependency Injection Container

Medusa resolves dependencies from a typed container. Module services are registered and resolved by key:

| Registration Pattern | Resolution Key | Type |
|---------------------|---------------|------|
| Module service | `ModuleRegistrationName.MODULE` | Module service interface |
| Custom module service | Defined in module export | Custom service class |
| Remote query | `ContainerRegistrationKeys.QUERY` | `RemoteQueryFunction` |
| Logger | `ContainerRegistrationKeys.LOGGER` | `Logger` |

### Typing the Container in Routes and Workflows

Access the container in API routes via `req.scope.resolve("key")`. In workflow steps, resolve via the `StepFunction` context. Use typed registration keys for compile-time safety.

## Strict Mode Constraints

### Key Strict Checks

| Check | Flag | Effect on Medusa Code |
|-------|------|-----------------------|
| `strictNullChecks` | Part of `strict` | Must handle `null`/`undefined` explicitly |
| `noImplicitAny` | Part of `strict` | All parameters and variables must be typed |
| `strictPropertyInitialization` | Part of `strict` | All class properties must be initialized |
| `noImplicitReturns` | Recommended | All code paths must return a value |
| `noUnusedLocals` | Recommended | Catch dead code early |
| `exactOptionalPropertyTypes` | Optional | Distinguish `undefined` from missing |

### Handling Nullable Types in Medusa

- DML `.nullable()` fields produce `T | null` — always check before using
- `retrieve()` may throw if entity not found — wrap in try/catch or use `list()` with filters
- Optional config parameters use `?:` — provide defaults where needed

## Utility Types for Medusa

### Commonly Used TypeScript Utilities

| Utility Type | Use Case in Medusa |
|-------------|-------------------|
| `Partial<T>` | Update DTOs (only changed fields required) |
| `Required<T>` | Ensure all fields present in creation |
| `Pick<T, Keys>` | Select specific fields for API responses |
| `Omit<T, Keys>` | Exclude internal fields from public DTOs |
| `Record<string, T>` | Metadata and JSON fields |
| `NonNullable<T>` | Assert non-null after null check |
| `Awaited<T>` | Unwrap Promise return types |
| `ReturnType<T>` | Extract return type from functions |

### Medusa-Specific Types

| Type | Import From | Purpose |
|------|-------------|---------|
| `InferTypeOf` | `@medusajs/framework/types` | Infer entity type from DML model |
| `MedusaRequest` | `@medusajs/framework/http` | Typed HTTP request in API routes |
| `MedusaResponse` | `@medusajs/framework/http` | Typed HTTP response in API routes |
| `StepResponse` | `@medusajs/framework/workflows-sdk` | Typed workflow step return |
| `MedusaContainer` | `@medusajs/framework/types` | DI container type |

## Module Interface Patterns

### Defining Module Types

Each custom module should export typed interfaces for its service:

```ts
// Fetch live docs for module type export
// conventions and service interface patterns
```

| File | Purpose |
|------|---------|
| `src/modules/<name>/models/` | DML model definitions |
| `src/modules/<name>/service.ts` | Service extending `MedusaService` |
| `src/modules/<name>/index.ts` | Module definition with `Module()` factory |
| `src/modules/<name>/types.ts` | Custom types and interfaces (optional) |

### Generic Constraints on Module Boundaries

- Module services should accept and return typed DTOs, not raw entities
- Use `Pick`/`Omit` to shape public API types from internal entity types
- Define explicit input types for `create` and `update` operations

## Zod Validators and Type Inference

API routes use Zod schemas for runtime validation. Infer TypeScript types from Zod schemas to avoid duplication:

```ts
// Fetch live docs for Zod schema usage in
// Medusa API route validators
import { z } from "zod"
```

| Pattern | Purpose |
|---------|---------|
| `z.infer<typeof schema>` | Derive TS type from Zod schema |
| `defineMiddlewares` | Register Zod validators on routes |
| `additionalDataValidator` | Extend existing route validation |

## Best Practices

- **DML-first typing** — define models in DML and use `InferTypeOf` to derive types; never manually duplicate entity types as interfaces; keep the DML model as the single source of truth
- **Strict mode always** — enable `strict: true` in `tsconfig.json`; handle all nullable cases explicitly; use `NonNullable` and type guards instead of non-null assertions (`!`)
- **Container type safety** — use typed registration keys when resolving from the container; avoid `any` casts on resolved services; define explicit return types on custom service methods
- **API type flow** — define Zod schemas for request validation; infer TypeScript types from Zod with `z.infer`; type API route handlers with `MedusaRequest<T>` and `MedusaResponse`

Fetch the Medusa TypeScript documentation for exact type imports, generic signatures, and DML inference patterns before implementing.
