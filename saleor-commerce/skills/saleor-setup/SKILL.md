---
name: saleor-setup
description: Set up a Saleor development environment — saleor-platform Docker Compose, CLI, PostgreSQL/Redis prerequisites, manage.py commands, environment variables, project structure. Use when starting a new Saleor project.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Development Setup

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/getting-started/architecture` for architecture overview
2. Web-search `site:docs.saleor.io saleor-platform docker compose setup` for Docker-based quickstart
3. Web-search `site:docs.saleor.io saleor CLI installation` for CLI tooling and commands
4. Web-search `site:docs.saleor.io environment variables configuration` for .env reference
5. Web-search `site:github.com saleor/saleor-platform docker-compose` for latest Compose file

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Python | 3.12+ | Saleor core runtime |
| PostgreSQL | 14+ | Primary database |
| Redis | 6+ | Celery broker, caching |
| Node.js | 18+ | Dashboard and storefront apps |
| Docker & Docker Compose | latest | Recommended local environment |
| Git | any | Version control |

### PostgreSQL Setup (Without Docker)

- Create a dedicated database: `CREATE DATABASE saleor;`
- Create a user with full privileges on that database
- Connection string format: `postgres://user:password@localhost:5432/saleor`

### Redis Setup

- Default connection: `redis://localhost:6379`
- Required for Celery task queue and caching layer
- Saleor does not fall back to an in-memory broker -- Redis is mandatory

## Docker Compose Quickstart (saleor-platform)

The `saleor-platform` repository bundles all Saleor services into a single Compose stack:

| Service | Container | Port |
|---------|-----------|------|
| Saleor Core (API) | `saleor-api` | 8000 |
| Saleor Dashboard | `saleor-dashboard` | 9000 |
| Saleor Storefront | `saleor-storefront` | 3000 |
| PostgreSQL | `saleor-db` | 5432 |
| Redis | `saleor-redis` | 6379 |
| Celery Worker | `saleor-worker` | -- |
| Jaeger (tracing) | `jaeger` | 16686 |
| Mailpit (email) | `mailpit` | 8025 |

Clone the platform repository and start all services with `docker compose up`.

## Saleor CLI

| Command | Purpose |
|---------|---------|
| `saleor login` | Authenticate with Saleor Cloud |
| `saleor env list` | List available environments |
| `saleor env create` | Create a new Cloud environment |
| `saleor tunnel` | Expose local app to Saleor for webhook delivery |
| `saleor app create` | Scaffold a new Saleor App |
| `saleor app tunnel` | Tunnel local app for development |
| `saleor storefront create` | Scaffold a storefront project |

Install via `npm i -g @saleor/cli` -- fetch live docs for current CLI version.

## Project Directory Structure (Saleor Core)

| Directory | Purpose |
|-----------|---------|
| `saleor/graphql/` | GraphQL schema, types, resolvers, mutations |
| `saleor/product/` | Product, category, collection models |
| `saleor/order/` | Order, fulfillment, draft order models |
| `saleor/checkout/` | Checkout models and calculations |
| `saleor/payment/` | Payment gateway interfaces |
| `saleor/warehouse/` | Stock, warehouse, allocation models |
| `saleor/plugins/` | Legacy plugin system (deprecated in favor of Apps) |
| `saleor/webhook/` | Webhook dispatch and event handling |
| `saleor/core/` | Shared utilities, permissions, base models |
| Root | `manage.py`, `requirements.txt`, `setup.cfg`, `.env` |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection for Celery and cache |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `DEFAULT_FROM_EMAIL` | Sender email address |
| `EMAIL_URL` | SMTP connection string |
| `DASHBOARD_URL` | Dashboard URL for CORS and redirects |
| `ALLOWED_CLIENT_HOSTS` | Storefront hosts for CORS |
| `ENABLE_DEBUG_TOOLBAR` | Enable Django Debug Toolbar |
| `JAEGER_AGENT_HOST` | OpenTelemetry tracing endpoint |

Never hardcode secrets -- always use `.env` files excluded from version control.

## manage.py Commands

| Command | Purpose |
|---------|---------|
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create admin staff account |
| `python manage.py populatedb` | Seed sample data |
| `python manage.py collectstatic` | Collect static files for production |
| `python manage.py create_thumbnails` | Generate product image thumbnails |

## Celery Worker

Saleor uses Celery for asynchronous tasks (email sending, webhook dispatch, thumbnail generation):

| Mode | Command |
|------|---------|
| Development | `celery -A saleor worker --loglevel=info` |
| Production | Use a process manager (systemd, supervisord) |
| Beat scheduler | `celery -A saleor beat` for periodic tasks |

## Common Issues

| Issue | Resolution |
|-------|-----------|
| Database connection refused | Verify PostgreSQL is running and `DATABASE_URL` is correct |
| Celery tasks not executing | Ensure Redis is running and `REDIS_URL` is correct |
| CORS errors from Dashboard | Check `DASHBOARD_URL` matches the actual Dashboard origin |
| CORS errors from Storefront | Check `ALLOWED_CLIENT_HOSTS` includes the storefront origin |
| Static files 404 | Run `collectstatic` or check `STATIC_URL` config |
| Docker Compose port conflict | Ensure ports 8000, 9000, 5432, 6379 are free |

## Best Practices

- Use `saleor-platform` Docker Compose for local development -- avoid manual dependency setup
- Always run `python manage.py migrate` after pulling changes with new migrations
- Keep `.env` in `.gitignore` and provide `.env.example` for team members
- Use `populatedb` to seed sample data for development and testing
- Run Celery worker alongside the API server -- async tasks will silently fail without it
- Pin dependency versions in `requirements.txt` to avoid unexpected breakage
- Use `saleor tunnel` or `saleor app tunnel` when developing Apps that receive webhooks

Fetch the Saleor setup documentation for exact Docker Compose configuration, CLI flags, and latest environment variable reference before implementing.
