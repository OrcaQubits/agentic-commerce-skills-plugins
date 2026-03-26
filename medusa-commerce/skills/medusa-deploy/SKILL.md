---
name: medusa-deploy
description: Deploy Medusa v2 to production — build process, server vs worker mode, environment variables, hosting options, Redis caching, database configuration, and production checklist. Use when deploying Medusa applications.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Medusa v2 Deployment

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.medusajs.com deployment production` for production deployment guides
2. Web-search `site:docs.medusajs.com medusa build` for build process details
3. Fetch `https://docs.medusajs.com/learn/fundamentals/cli` for CLI command reference
4. Web-search `site:docs.medusajs.com environment variables configuration` for env var reference
5. Web-search `site:docs.medusajs.com redis cache events` for Redis caching and event bus setup

## Build Process

### Build Commands

| Command | Purpose |
|---------|---------|
| `npx medusa build` | Compile server + admin dashboard for production |
| `npx medusa db:migrate` | Run pending database migrations |
| `npx medusa start` | Start the production server |
| `npx medusa worker` | Start the background worker process |

The build step compiles TypeScript, bundles admin extensions (Vite), and prepares the `.medusa/` output directory.

### Build Output Structure

```
.medusa/
├── server/           — Compiled server code
│   ├── src/          — Custom modules, routes, workflows
│   └── medusa-config.js
└── admin/            — Bundled admin dashboard (static)
```

## Server vs Worker Mode

Medusa v2 supports running the server and background workers as separate processes:

| Mode | Command | Handles |
|------|---------|---------|
| **Server** | `npx medusa start` | HTTP requests, API routes, admin dashboard |
| **Worker** | `npx medusa worker` | Workflows, scheduled jobs, event subscribers |
| **Combined** | Default `start` behavior | Both server and worker (single process) |

### When to Separate

- **Development** — combined mode is fine
- **Production** — separate for reliability and independent scaling
- **High traffic** — scale server instances independently from workers
- Worker mode requires Redis for job queue communication between processes

## Environment Variables

### Required Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/medusa` |
| `COOKIE_SECRET` | Session cookie signing | Random 32+ character string |
| `JWT_SECRET` | JWT token signing | Random 32+ character string |
| `NODE_ENV` | Runtime environment | `production` |

### Optional but Recommended

| Variable | Purpose | Default |
|----------|---------|---------|
| `REDIS_URL` | Redis connection for cache/events/workers | None (in-memory) |
| `STORE_CORS` | Store API CORS origins | `http://localhost:8000` |
| `ADMIN_CORS` | Admin API CORS origins | `http://localhost:9000` |
| `AUTH_CORS` | Auth route CORS origins | Combination of store + admin |
| `PORT` | Server listen port | `9000` |
| `MEDUSA_ADMIN_ONBOARDING_TYPE` | Admin onboarding flow | `default` |
| `MEDUSA_WORKER_MODE` | `server`, `worker`, or `shared` | `shared` |

## Database Configuration

### PostgreSQL Requirements

- PostgreSQL required (see official docs for version compatibility)
- Enable SSL in production: append `?sslmode=require` to `DATABASE_URL`
- Connection pooling recommended for high-traffic deployments

### Migration Workflow

```bash
# Generate migration after DML model changes
npx medusa db:generate <module_name>
# Apply migrations
npx medusa db:migrate
```

- Always run migrations before starting the new server version
- Back up the database before running migrations in production
- Test migrations against a staging database first

## Redis Configuration

Redis serves three roles in production Medusa:

| Role | Purpose | Required? |
|------|---------|-----------|
| **Event Bus** | Pub/sub for event-driven subscribers | Recommended |
| **Cache** | Module data caching layer | Recommended |
| **Worker Queue** | Job queue for background workflows | Required for worker mode |

Configure in `medusa-config.ts` by registering the Redis modules:

```ts
// Fetch live docs for Redis module registration
// in medusa-config.ts modules array
```

- Use separate Redis databases (db index) for cache vs events vs queues
- Set appropriate `maxmemory` and eviction policies for cache
- Monitor Redis memory usage and connection count in production

## Hosting Options

| Platform | Type | Notes |
|----------|------|-------|
| **Railway** | PaaS | One-click deploy, managed PostgreSQL and Redis |
| **DigitalOcean App Platform** | PaaS | Managed infrastructure, auto-scaling |
| **AWS (EC2/ECS/Fargate)** | IaaS/CaaS | Full control, use with RDS and ElastiCache |
| **Google Cloud Run** | Serverless containers | Auto-scaling, pay-per-use |
| **Render** | PaaS | Simple deploy, managed databases |
| **Self-hosted (Docker)** | Container | Full control, use Docker Compose or Kubernetes |
| **Vercel** | Serverless | Admin/storefront hosting only (not the Medusa server) |

### Docker Deployment

```dockerfile
# Fetch live docs for official Medusa Dockerfile
# and docker-compose.yml patterns
```

A typical Docker Compose setup includes three services: Medusa server, PostgreSQL, and Redis.

## Production Checklist

### Pre-Deploy

- [ ] Set `NODE_ENV=production`
- [ ] Configure unique `COOKIE_SECRET` and `JWT_SECRET`
- [ ] Set `DATABASE_URL` with SSL mode enabled
- [ ] Configure `REDIS_URL` for events, cache, and worker queue
- [ ] Set CORS variables (`STORE_CORS`, `ADMIN_CORS`, `AUTH_CORS`)
- [ ] Run `npx medusa build` successfully
- [ ] Run `npx medusa db:migrate` against production database

### Infrastructure

- [ ] PostgreSQL with automated backups and point-in-time recovery
- [ ] Redis with persistence enabled (RDB or AOF)
- [ ] HTTPS termination (TLS certificate) via reverse proxy or load balancer
- [ ] Health check endpoint configured for load balancer
- [ ] Log aggregation (stdout/stderr to centralized logging)

### Post-Deploy

- [ ] Verify admin dashboard loads and login works
- [ ] Verify store API responds with publishable key
- [ ] Confirm background workers are processing jobs
- [ ] Test payment provider webhooks reach the server
- [ ] Monitor error rates and response times

## Scaling Strategies

### Horizontal Scaling

- Run multiple server instances behind a load balancer
- Use Redis-backed sessions for sticky-session-free scaling
- Run multiple worker instances for parallel job processing

### Vertical Scaling

- Increase PostgreSQL connection pool size for heavier workloads
- Allocate more memory to Redis for larger cache datasets
- Use `--max-old-space-size` for Node.js memory limits

## Best Practices

- **Separate server and worker** — run as independent processes in production; scale each based on demand; use Redis as the communication backbone
- **Environment variable hygiene** — never commit secrets to source control; use platform-native secret management (AWS Secrets Manager, Railway variables, etc.); rotate secrets periodically
- **Database management** — always test migrations on staging first; automate backups; use connection pooling (PgBouncer) for high concurrency
- **Monitoring** — track API response times, worker queue depth, database connection count, and Redis memory; set alerts for anomalies

Fetch the Medusa deployment documentation for exact build flags, Docker configuration, and platform-specific deployment guides before deploying.
