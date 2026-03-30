---
name: medusa-setup
description: >
  Set up a Medusa v2 development environment — CLI, PostgreSQL/Redis
  prerequisites, project creation, medusa-config.ts, directory structure,
  environment variables. Use when starting a new Medusa project.
---

# Medusa v2 Development Setup

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/installation` for installation guide
2. Web-search `site:docs.medusajs.com create medusa starter` for project scaffolding
3. Web-search `site:docs.medusajs.com medusa-config reference` for configuration options
4. Web-search `site:docs.medusajs.com project directory structure` for v2 layout

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Node.js | v20+ | Runtime |
| PostgreSQL | — (see docs) | Primary database |
| Redis | v6+ | Event bus, caching (optional for dev) |
| Git | any | Version control |
| npm / yarn / pnpm | latest | Package manager |

### PostgreSQL Setup

- Create a dedicated database: `CREATE DATABASE medusa_db;`
- Create a user with full privileges on that database
- Connection string format: `postgres://user:password@localhost:5432/medusa_db`

### Redis Setup (Optional for Development)

- Default connection: `redis://localhost:6379`
- Required in production for the event bus module and caching
- In development, Medusa falls back to an in-memory event bus

## Project Creation

### CLI Scaffolding

```bash
npx create-medusa-app@latest my-store
# Prompts: project name, PostgreSQL credentials
# Creates: backend + Next.js storefront starter
```

### Backend Only

```bash
npx create-medusa-app@latest my-store --skip-client
# Fetch live docs for current CLI flags
```

## Project Directory Structure

| Directory | Purpose |
|-----------|---------|
| `src/modules/` | Custom modules (DML data models, services) |
| `src/workflows/` | Custom workflows and steps |
| `src/api/store/`, `src/api/admin/` | Custom API routes + `middlewares.ts` |
| `src/subscribers/`, `src/jobs/` | Event subscribers, scheduled jobs |
| `src/admin/widgets/`, `src/admin/routes/` | Admin UI extensions |
| `src/links/` | Module link definitions |
| Root | `medusa-config.ts`, `package.json`, `tsconfig.json`, `.env` |

## medusa-config.ts Key Fields

| Field | Purpose |
|-------|---------|
| `projectConfig.databaseUrl` | PostgreSQL connection string |
| `projectConfig.redisUrl` | Redis connection (optional) |
| `projectConfig.http.adminCors` | Allowed origins for admin API |
| `projectConfig.http.storeCors` | Allowed origins for store API |
| `projectConfig.http.authCors` | Allowed origins for auth routes |
| `projectConfig.workerMode` | `shared`, `worker`, or `server` |
| `modules` | Array of module configurations |
| `plugins` | Array of plugin configurations |

### Minimal Configuration Skeleton

```typescript
// medusa-config.ts — Fetch live docs for current defineConfig shape
import { defineConfig } from "@medusajs/framework/utils"

export default defineConfig({
  projectConfig: { databaseUrl: process.env.DATABASE_URL },
  // Fetch live docs for modules, plugins, http config
})
```

## Environment Variables

```
DATABASE_URL=postgres://user:password@localhost:5432/medusa_db
REDIS_URL=redis://localhost:6379
COOKIE_SECRET=your-cookie-secret
JWT_SECRET=your-jwt-secret
STORE_CORS=http://localhost:8000
ADMIN_CORS=http://localhost:5173
AUTH_CORS=http://localhost:5173
```

Never hardcode secrets -- always use `.env` files excluded from version control.

## CLI Commands

| Command | Purpose |
|---------|---------|
| `npx medusa develop` | Start dev server with hot reload |
| `npx medusa build` | Build for production |
| `npx medusa start` | Start production server |
| `npx medusa worker` | Start background worker process |
| `npx medusa db:migrate` | Run database migrations |
| `npx medusa db:generate` | Generate migration files |
| `npx medusa db:rollback` | Rollback last migration |
| `npx medusa user --email admin@example.com` | Create admin user |
| `npx medusa exec ./src/scripts/seed.ts` | Run seed script |

## Worker Mode

Medusa supports three worker modes for handling background jobs:

| Mode | Description |
|------|-------------|
| `shared` | Single process handles HTTP and background jobs (default) |
| `worker` | Dedicated process for background jobs only |
| `server` | HTTP-only, no background job processing |

In production, run one `server` instance and one or more `worker` instances.

## Database Migrations

- Medusa v2 auto-generates migrations from DML model changes
- Run `npx medusa db:generate` after modifying data models
- Run `npx medusa db:migrate` to apply pending migrations
- Always commit migration files to version control

## Best Practices

- Use `npx create-medusa-app@latest` to scaffold -- do not set up manually
- Always run `npx medusa db:migrate` after pulling changes that include new migrations
- Keep `.env` in `.gitignore` and provide `.env.template` for team members
- Use `shared` worker mode in development, separate `server` + `worker` in production
- Pin your Medusa version in `package.json` to avoid unexpected breaking changes
- Run `npx medusa user` to create the first admin user after initial setup

## Common Issues

| Issue | Resolution |
|-------|-----------|
| Database connection refused | Verify PostgreSQL is running and `DATABASE_URL` is correct |
| Migrations fail | Ensure database exists and user has DDL privileges |
| Admin dashboard blank | Check `ADMIN_CORS` matches the admin URL |
| Store API 403 | Check `STORE_CORS` matches the storefront URL |
| Redis connection error | Either start Redis or remove `redisUrl` from config |

Fetch the Medusa installation guide and CLI reference for exact commands, flags, and latest configuration options before setting up.
