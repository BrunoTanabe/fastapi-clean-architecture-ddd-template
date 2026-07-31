---
name: create-router
description: Creates a FastAPI endpoint handler in presentation/routers.py with the project's double-route decorators, Authentication dependency injection, mapper flow, and 3-branch error handling, then registers the path in the matching SECURITY_*_ALLOWED_PATHS tier. Use when the user asks to add an endpoint handler, create a route, or extend presentation/routers.py.
argument-hint: "<module> <operation>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Router Endpoint Handler

<task>Add one endpoint function to `app/modules/{module}/presentation/routers.py` and register both of its path forms in the security allowlist.</task>

## Scope

- **In scope:** the handler and its allowlist registration. Registration is included because the
  endpoint returns 403 without it — a handler alone is not a working endpoint.
- **Out of scope:** the schemas, mappers, use case, and docs dicts it references. They must already
  exist; if one is missing, say so and name the skill that creates it.
- **Done when:** the handler exists, both path forms are in the right tier, and ruff is clean.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Router pattern) and `.claude/reference/security.md` (router
dependencies, the allowlist tiers, registering an endpoint).

## Step 2 — Load live patterns

Read `app/modules/key/presentation/routers.py` — six handlers covering create, list, get by id,
update, a sub-path action, and delete, all in the double-route form.

Read the target module's `presentation/dependencies.py` for the available factories and
`presentation/docs.py` for the `{action}_docs` names.

## Step 3 — Discovery

- The operation, HTTP method, and path.
- The authentication dependency — this also determines the allowlist tier.
- The request and response schemas, the use-case method, and the mappers.

## Step 4 — Generate the handler

Templates for every handler shape are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Register both path forms

Add the rules to the tier matching the handler's dependency, in `app/core/settings.py`:

```python
(_path_rule("/api/v1/{module}/", "POST"),)
(_path_rule("/api/v1/{module}", "POST"),)
```

| Dependency | Tier |
|------------|------|
| `no_authentication` | `SECURITY_NO_AUTH_PATHS` |
| `authenticate_user` | `SECURITY_USER_ALLOWED_PATHS` |
| `authenticate_manager` | `SECURITY_MANAGER_ALLOWED_PATHS` |
| `authenticate_admin` | `SECURITY_ADMIN_ALLOWED_PATHS` |

Tiers cascade, so declare a path once at its lowest permitted role. Group the rules under an
uppercase module comment. `SECURITY_API_KEY_ALLOWED_PATHS` is a separate, currently empty tier —
add to it only when the endpoint is explicitly meant for machine-to-machine access.

WebSocket routes are not listed in any HTTP tier; `authenticate_websocket` is the whole check.

## Step 6 — Lint

Run `uv run ruff check` on both touched files and `uv run ruff format` on them. Fix and re-run
until clean.

If the module's router is not yet in `app/app.py`, say so and point at `/register-module`.

## Rules

- **Two decorators per route** — one with the trailing `/` carrying `**{action}_docs`, one without
  carrying `include_in_schema=False`. This applies to parameterized routes too (`/{id}/` plus
  `/{id}`), because the allowlists register both slash forms. Missing the second decorator is the
  most common cause of "works in Swagger, 403 from the client".
- `router = APIRouter(**router_docs)` once at module level.
- Handlers inject `Annotated[Authentication, Depends(authenticate_*)]`, never `User` and never
  `Session`. Read the actor as `authentication.user`. Public endpoints inject
  `Annotated[None, Depends(no_authentication)]` — there is no unguarded route.
- The body is exactly `payload → mapper → use case → mapper → return`, assigning to
  `request_domain`, `response_domain`, and `output`. No branching, no loops, no database access,
  no business rules.
- The 3-branch try/except, `StandardException` first:
  ```python
  except StandardException:
      raise
  except DomainError as e:
      raise DomainException(e)
  except Exception as e:
      logger.opt(exception=e).error("An error occurred in the create {module} endpoint.")
      raise {Module}Exception()
  ```
- The error message names the endpoint that failed — it is what makes a 500 traceable.
- Return the plain response schema. `ResponseFormattingMiddleware` adds the `StandardResponse`
  envelope; never build it by hand.
- The return annotation is the response schema, and it must match the `response_model` in the
  matching `{action}_docs`.
- Group handlers under `# CREATE`, `# READ`, `# UPDATE`, `# DELETE` headers. Function names match
  the operation: `create`, `get_by_id`, `get_all`, `update`, `rotate`, `delete`, `me`.
- Path parameters are typed (`id: UUID`), so FastAPI rejects a malformed value before the handler
  runs.
- Pagination arrives as `query_params: Annotated[{Entity}PaginationParams, Depends()]`.
