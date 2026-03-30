---
name: python-django
description: >
  Write Python and Django code for Saleor — Django ORM patterns, signals,
  Celery tasks, type hints, migrations, management commands, and async views.
  Use when writing Python/Django in Saleor projects.
---

# Python & Django for Saleor

## Before writing code

**Fetch live docs**:
1. Web-search `site:docs.djangoproject.com topics models querysets` for current Django ORM documentation
2. Web-search `site:docs.djangoproject.com topics signals` for Django signals reference
3. Web-search `site:docs.celeryq.dev userguide tasks` for Celery task patterns and configuration
4. Web-search `site:docs.saleor.io developer` for Saleor-specific Django conventions
5. Fetch `https://docs.python.org/3/library/typing.html` for Python type hints reference

## Django ORM Patterns for Saleor

### QuerySet Operations

| Operation | Method | Example Use |
|-----------|--------|-------------|
| **Filter** | `.filter(**kwargs)` | Filter products by type |
| **Exclude** | `.exclude(**kwargs)` | Exclude draft orders |
| **Annotate** | `.annotate(expr)` | Add computed fields (totals, counts) |
| **Aggregate** | `.aggregate(expr)` | Compute sum, avg across queryset |
| **Select related** | `.select_related("fk")` | Join foreign keys (avoid N+1) |
| **Prefetch related** | `.prefetch_related("m2m")` | Batch-load many-to-many (avoid N+1) |
| **Values** | `.values("field")` | Return dictionaries instead of objects |
| **Order by** | `.order_by("field")` | Sort results |

### F and Q Objects

| Object | Purpose | Example Use |
|--------|---------|-------------|
| `F("field")` | Reference model field in expressions | Update stock: `F("quantity") - 1` |
| `Q(condition)` | Complex lookups with OR/AND/NOT | `Q(status="active") | Q(featured=True)` |

- Use `F()` for atomic field updates without race conditions
- Combine `Q()` objects with `|` (OR), `&` (AND), `~` (NOT) for complex filters

## Model Relationships in Saleor

| Relationship | Field Type | Example |
|-------------|-----------|---------|
| **One-to-Many** | `ForeignKey` | Order -> User, OrderLine -> Order |
| **Many-to-Many** | `ManyToManyField` | Product -> Category (via ProductCategory) |
| **One-to-One** | `OneToOneField` | User -> UserProfile |
| **Generic** | `GenericForeignKey` | Attribute values on multiple entity types |

- Always set `on_delete` explicitly (`CASCADE`, `PROTECT`, `SET_NULL`)
- Use `related_name` for reverse lookups
- Index foreign keys used in frequent queries

## Django Signals

| Signal | Fires When | Common Use |
|--------|-----------|------------|
| `pre_save` | Before `model.save()` | Validate or transform data |
| `post_save` | After `model.save()` | Trigger side effects, send notifications |
| `pre_delete` | Before `model.delete()` | Clean up related resources |
| `post_delete` | After `model.delete()` | Remove cached data |
| `m2m_changed` | Many-to-many field modified | Update denormalized counters |

- Saleor uses webhooks as the primary event mechanism, not Django signals
- Use signals sparingly for internal side effects only
- Never perform expensive I/O in signal handlers (use Celery tasks instead)
- Connect signals in `AppConfig.ready()` to avoid import issues

## Celery Task Patterns

### Defining Tasks

| Pattern | Decorator | Use Case |
|---------|-----------|----------|
| **Shared task** | `@shared_task` | Framework-agnostic, recommended |
| **App task** | `@app.task` | Tied to specific Celery app |
| **Bound task** | `@shared_task(bind=True)` | Access `self` for retries |

### Retry and Error Handling

| Parameter | Description | Example |
|-----------|-------------|---------|
| `max_retries` | Maximum retry attempts | `3` |
| `default_retry_delay` | Seconds between retries | `60` |
| `retry_backoff` | Enable exponential backoff | `True` |
| `autoretry_for` | Exception classes to auto-retry | `(ConnectionError,)` |
| `acks_late` | Acknowledge after execution | `True` (prevents task loss) |

- Pass serializable arguments (IDs, not model instances)
- Keep tasks idempotent — safe to retry without side effects
- Set reasonable timeouts with `soft_time_limit` and `time_limit`

## Python Type Hints

| Type | Import | Use |
|------|--------|-----|
| `Optional[T]` | `typing` | Value may be None |
| `list[T]` | Built-in (3.9+) | Typed list |
| `dict[K, V]` | Built-in (3.9+) | Typed dictionary |
| `Union[A, B]` | `typing` | Either type A or B |
| `Protocol` | `typing` | Structural subtyping (duck typing) |
| `TypedDict` | `typing` | Typed dictionary with fixed keys |
| `Literal["a", "b"]` | `typing` | Restrict to specific values |

- Use `from __future__ import annotations` for postponed evaluation
- Type all function parameters, return values, and class attributes
- Use `mypy` or `pyright` for static type checking

## Database Migrations

| Command | Purpose |
|---------|---------|
| `python manage.py makemigrations` | Generate migration files from model changes |
| `python manage.py migrate` | Apply pending migrations to database |
| `python manage.py showmigrations` | List all migrations and their status |
| `python manage.py sqlmigrate app_name 0001` | Show SQL for a specific migration |
| `python manage.py squashmigrations app_name 0001 0010` | Combine multiple migrations |

- Review generated migrations before applying to production
- Use `RunPython` for data migrations (separate from schema migrations)
- Test migrations on a copy of production data before deploying

## Management Commands

| Aspect | Convention |
|--------|-----------|
| **Location** | `app_name/management/commands/command_name.py` |
| **Class** | Subclass `BaseCommand` |
| **Entry point** | `handle(self, *args, **options)` method |
| **Arguments** | Use `add_arguments(self, parser)` with `argparse` |
| **Output** | Use `self.stdout.write()` and `self.style` |

- Use management commands for one-off scripts, data fixes, and admin tasks
- Always add `help` text to commands for documentation

## Async Django Views (ASGI)

| Feature | Sync | Async |
|---------|------|-------|
| **View type** | `def view(request)` | `async def view(request)` |
| **Server** | WSGI (Gunicorn) | ASGI (Uvicorn, Daphne) |
| **ORM access** | Direct | Wrap in `sync_to_async` |
| **HTTP calls** | `requests` | `httpx` (async) |

- Saleor runs via ASGI with Uvicorn workers under Gunicorn
- Django ORM is synchronous — use `sync_to_async` or `QuerySet.aiterator()`
- Use `httpx.AsyncClient` for non-blocking HTTP requests

## Django Settings and Virtual Environments

| Pattern | Description |
|---------|-------------|
| **Environment variables** | Load with `os.environ` or `django-environ` |
| **Split settings** | `settings/base.py`, `settings/dev.py`, `settings/prod.py` |
| **Twelve-Factor** | All configuration via environment variables |

| Tool | Command | Notes |
|------|---------|-------|
| **venv** | `python -m venv .venv` | Built-in, standard |
| **poetry** | `poetry install` | Dependency resolution, lock file |
| **uv** | `uv venv && uv pip install -r requirements.txt` | Fast Rust-based installer |

## Best Practices

- Use `select_related` and `prefetch_related` to avoid N+1 query problems
- Keep Django signals lightweight — offload heavy work to Celery tasks
- Type all function signatures and use `mypy` for static analysis
- Make Celery tasks idempotent and pass only serializable arguments
- Review migration SQL before applying to production databases
- Use `F()` expressions for atomic field updates instead of read-modify-write
- Follow Saleor's existing code style when contributing to the core
- Use async views and `httpx` for I/O-heavy endpoints
- Store all configuration in environment variables following twelve-factor methodology

Fetch the Python and Django documentation for current ORM patterns, Celery task configuration, and async view setup before implementing.
