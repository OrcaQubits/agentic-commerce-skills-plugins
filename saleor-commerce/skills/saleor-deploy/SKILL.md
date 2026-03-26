---
name: saleor-deploy
description: Deploy Saleor to production — Docker setup, Saleor Cloud, environment variables, Celery workers, S3 media storage, database management, and scaling. Use when deploying Saleor applications.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Deployment

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.saleor.io deployment production setup` for production deployment guide
2. Fetch `https://github.com/saleor/saleor-platform` for Docker Compose reference configuration
3. Web-search `site:docs.saleor.io environment variables configuration` for required environment variables
4. Web-search `saleor Celery worker configuration production` for Celery setup details
5. Web-search `site:docs.saleor.io cloud` for Saleor Cloud managed hosting options

## Production Docker Setup

Saleor provides an official Dockerfile with a multi-stage build:

| Stage | Purpose | Base Image |
|-------|---------|------------|
| **build** | Install dependencies, compile assets | `python:3.12-slim` |
| **production** | Run the application | `python:3.12-slim` |

### Docker Compose Services

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| **api** | `saleor` (custom build) | GraphQL API server (Gunicorn) | 8000 |
| **worker** | `saleor` (same image) | Celery worker process | N/A |
| **db** | `postgres:15-alpine` | PostgreSQL database | 5432 |
| **redis** | `redis:7-alpine` | Cache and Celery broker | 6379 |
| **dashboard** | `saleor-dashboard` | React admin UI | 9002 |
| **storefront** | Custom Next.js | Customer-facing storefront | 3000 |

## Saleor Cloud (Managed Hosting)

| Feature | Description |
|---------|-------------|
| **Managed API** | Fully managed Saleor backend, no server maintenance |
| **Auto-scaling** | Scales based on traffic automatically |
| **Managed database** | PostgreSQL with backups and replication |
| **CDN** | Built-in CDN for media and static assets |
| **Environments** | Staging and production environments per project |
| **CLI integration** | Deploy and manage via `saleor` CLI |

Access via `https://cloud.saleor.io/` — create projects, manage environments, and deploy Apps.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/saleor` |
| `SECRET_KEY` | Django secret key (50+ chars) | Random string |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `api.example.com,localhost` |
| `DEFAULT_FROM_EMAIL` | Sender email address | `noreply@example.com` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://redis:6379/1` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `False` |
| `ALLOWED_CLIENT_HOSTS` | Storefront origins for CORS | `localhost` |
| `DEFAULT_CURRENCY` | Fallback currency code | `USD` |
| `DEFAULT_COUNTRY` | Fallback country code | `US` |
| `MAX_CHECKOUT_LINE_QUANTITY` | Max qty per checkout line | `50` |
| `JAEGER_AGENT_HOST` | OpenTelemetry/Jaeger host | None |
| `SENTRY_DSN` | Sentry error tracking DSN | None |

## Celery Worker Configuration

Celery runs as a separate process using the same Saleor codebase:

| Setting | Value | Description |
|---------|-------|-------------|
| **Broker** | Redis | `CELERY_BROKER_URL = redis://redis:6379/1` |
| **Result backend** | Redis | Optional, for task result storage |
| **Concurrency** | `--concurrency=4` | Number of worker threads |
| **Queues** | `celery` (default) | Default task queue name |
| **Beat** | Optional | Periodic task scheduler |

### Key Celery Tasks in Saleor

| Task | Purpose |
|------|---------|
| Webhook delivery | Send async webhook payloads to Apps |
| Email sending | Transactional emails (order confirmation, etc.) |
| Thumbnail generation | Generate product image thumbnails |
| Search indexing | Update search index entries |
| Export processing | Handle CSV/XLSX data exports |

## S3-Compatible Media Storage

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_MEDIA_BUCKET_NAME` | S3 bucket name | `saleor-media-prod` |
| `AWS_MEDIA_CUSTOM_DOMAIN` | CDN domain for media | `media.example.com` |
| `AWS_ACCESS_KEY_ID` | IAM access key | IAM credential |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key | IAM credential |
| `AWS_S3_REGION_NAME` | S3 region | `us-east-1` |
| `AWS_S3_ENDPOINT_URL` | Custom S3 endpoint (for MinIO, GCS) | `https://s3.example.com` |

- Works with any S3-compatible service (AWS S3, Google Cloud Storage, MinIO, DigitalOcean Spaces)
- Set a CDN in front of the bucket for performance
- Configure CORS on the bucket to allow Dashboard uploads

## PostgreSQL Configuration

| Setting | Recommendation |
|---------|---------------|
| **Version** | PostgreSQL 14 or 15 |
| **Connection pooling** | Use PgBouncer in transaction mode |
| **SSL** | Require SSL connections (`sslmode=require` in DATABASE_URL) |
| **Backups** | Automated daily backups with point-in-time recovery |
| **Extensions** | `pg_trgm` (required for search), `btree_gin` |
| **Max connections** | Size for Gunicorn workers + Celery workers + buffer |

## Redis Configuration

| Purpose | Database | Variable |
|---------|----------|----------|
| **Cache** | `redis://redis:6379/0` | `CACHE_URL` |
| **Celery broker** | `redis://redis:6379/1` | `CELERY_BROKER_URL` |

- Use separate Redis databases (or instances) for cache and Celery
- Enable Redis persistence (RDB snapshots or AOF) for the Celery broker

## Database Migrations

Run migrations during deployment before starting the new application version:
- Always run `python manage.py migrate --noinput` before starting Gunicorn/Celery with new code
- Back up the database before applying migrations
- Review migration SQL with `python manage.py sqlmigrate <app> <migration>`
- For zero-downtime: ensure migrations are backward-compatible with the running code

## Scaling Strategies

### Horizontal Scaling

| Component | Strategy | Notes |
|-----------|----------|-------|
| **API (Gunicorn)** | Add replicas behind load balancer | Stateless, scale freely |
| **Celery workers** | Add worker processes/containers | Scale based on queue depth |
| **Database** | Read replicas for queries | Write goes to primary |
| **Redis** | Redis Cluster or managed Redis | Separate cache from broker |

### Vertical Scaling

| Component | Tune |
|-----------|------|
| **Gunicorn** | `--workers` (2 * CPU + 1), `--threads` per worker |
| **Celery** | `--concurrency` based on task type (I/O vs CPU) |
| **PostgreSQL** | `shared_buffers`, `work_mem`, `effective_cache_size` |

## Monitoring and Logging

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Sentry** | Error tracking | `SENTRY_DSN` environment variable |
| **OpenTelemetry** | Distributed tracing | `OTEL_EXPORTER_OTLP_ENDPOINT` |
| **Prometheus** | Metrics collection | `django-prometheus` middleware |
| **Health check** | Liveness and readiness probes | `/health/` endpoint |

## Production Checklist

| Item | Action |
|------|--------|
| `DEBUG` | Set to `False` |
| `SECRET_KEY` | Strong random value, stored in env var |
| `ALLOWED_HOSTS` | Restrict to actual domain names |
| Database | SSL enabled, connection pooling, backups configured |
| Media storage | S3-compatible with CDN |
| Celery | Running as separate process with monitoring |
| HTTPS | SSL termination at load balancer or reverse proxy |
| Migrations | Applied before deploying new code |
| Monitoring | Sentry, metrics, and health checks enabled |

## Best Practices

- Run Celery workers as a separate container or process, never in the API process
- Use connection pooling (PgBouncer) between Gunicorn/Celery and PostgreSQL
- Store all secrets in environment variables, never in source code or Docker images
- Use multi-stage Docker builds to minimize production image size
- Run database migrations in a separate init container or deployment step
- Configure health check endpoints for load balancer and orchestrator probes
- Use S3-compatible storage with a CDN for media files
- Monitor Celery queue depth to detect processing backlogs
- Set up automated database backups with tested restore procedures

Fetch the deployment documentation for current Docker setup, environment variables, and scaling recommendations before implementing.
