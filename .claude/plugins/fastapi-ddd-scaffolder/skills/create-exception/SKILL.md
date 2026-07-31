---
name: create-exception
description: Creates module exception classes in application/exceptions.py — the generic {Module}Exception returning HTTP 500 plus one specific StandardException subclass per business rule, each mapped to a ResponseMessages constant and the right HTTP status. Use when the user asks to add an exception, an error case, a not-found or conflict error, or when a new business rule needs its own failure response.
argument-hint: "<module> <ExceptionName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Module Exception

<task>Add exception classes to `app/modules/{module}/application/exceptions.py`, each subclassing `StandardException` with a status code, a `ResponseMessages` message, and a `data={"errors": ...}` payload.</task>

## Scope

- **In scope:** the exception classes, and the `raise` sites in the use case or repository that
  need them.
- **Out of scope:** the endpoint documentation for the new status code. Point at `/create-docs`
  when the exception introduces a status the module's `router_docs` does not already list.
- **Done when:** the classes exist, they are raised where the rule is enforced, and ruff is clean.

## Step 1 — Load the reference

Read `.claude/reference/shared-module.md` (exceptions) and
`app/modules/shared/application/exceptions.py` for `StandardException`, `DomainException`,
`CoreException`.

Then read `app/modules/key/application/exceptions.py` — the most complete example, with a generic
exception plus six specific ones.

## Step 2 — Check what already exists

Read the module's current `application/exceptions.py`. Every module must have exactly one generic
`{Module}Exception`; create it if missing, never a second one.

Do not add an exception for a condition that `DomainException` already covers. Domain validation
failures are raised as `DomainError` / `DomainErrors` from the entity and converted centrally —
they never need a module exception.

## Step 3 — Choose the status code and message

| Condition | Status | `ResponseMessages` |
|-----------|--------|--------------------|
| Unexpected failure (the generic one) | 500 `INTERNAL_SERVER_ERROR` | `INTERNAL_ERROR` |
| Record not found | 404 `NOT_FOUND` | `RESOURCE_NOT_FOUND` |
| Name or natural key already taken | 409 `CONFLICT` | `CONFLICT` |
| Update submitted with no effective change | 400 `BAD_REQUEST` | `BAD_REQUEST` |
| Missing, invalid, revoked, or expired credential | 401 `UNAUTHORIZED` | `UNAUTHORIZED_ERROR` |
| Authenticated but not permitted | 403 `FORBIDDEN` | `AUTHORIZATION_ERROR` |
| Upstream dependency failed | 502 `BAD_GATEWAY` | `BAD_GATEWAY` |
| Upstream dependency timed out | 504 `GATEWAY_TIMEOUT` | `GATEWAY_TIMEOUT` |

Never hardcode a message string — always a `ResponseMessages` member. If none fits, add a member
to `shared/domain/enums.py` rather than inlining a literal.

## Step 4 — Generate

Templates for the generic exception, the not-found / conflict / not-modified / credential shapes,
and the multi-error payload are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Raise it where the rule is enforced

The rule lives in the use case; the exception is raised there, after a `logger.info` explaining
the decision:

```python
existing = await self.repository.get_by_id(entity)
if existing is None:
    logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
    raise {Entity}NotFoundException(id=str(entity.id))
```

Because these subclass `StandardException`, the outer `except StandardException: raise` branch
re-raises them untouched through every layer. Never catch and re-wrap one.

## Step 6 — Lint

Run `uv run ruff check` and `uv run ruff format` on the touched files. Fix and re-run until clean.

If the module's `router_docs` does not already document the new status code, say so and point at
`/create-docs`.

## Rules

- One file per module: `application/exceptions.py`, with a `# GENERIC EXCEPTIONS` section followed
  by `# SPECIFIC EXCEPTIONS`.
- Exactly one generic `{Module}Exception`, HTTP 500, no constructor arguments. It is the fallback
  raised by the final `except Exception` branch in every layer of the module.
- Specific exceptions take the identifying value as a constructor argument and interpolate it into
  the message, so the client learns which record failed.
- `data` is always `{"errors": ...}` — a string for a single failure, a list only when reporting
  several at once (`DomainException` is the one that uses a list).
- Error text is a complete, user-facing sentence ending in a period. It must never leak a stack
  trace, a SQL fragment, an internal path, or a secret.
- Name specific exceptions after the failure, not the operation: `KeyNotFoundException`, not
  `GetKeyException`.
- Exceptions live in `application/`, never in `presentation/` or `domain/`. The domain layer raises
  `DomainError` / `DomainErrors` and knows nothing about HTTP.
- Cross-module raising is allowed and normal — `SharedUseCases` raises `UserIdNotFoundException`
  and `NotificationException` from the modules that own those rules.
