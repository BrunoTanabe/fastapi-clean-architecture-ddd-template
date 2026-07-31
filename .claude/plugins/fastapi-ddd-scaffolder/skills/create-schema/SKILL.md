---
name: create-schema
description: Creates Pydantic v2 request and response schemas in presentation/schemas.py with full Field and ConfigDict declarations, plus the {Entity}PaginationParams class for list endpoints. Use when the user asks to add a schema, create request or response models, add a Pydantic model, or define the HTTP contract of an endpoint.
argument-hint: "<module> <action>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Pydantic v2 Schema

<task>Add request and/or response schemas to `app/modules/{module}/presentation/schemas.py` following the project's full `Field` + `ConfigDict` convention.</task>

## Scope

- **In scope:** the schemas, their validators, and the pagination params class for a list endpoint.
- **Out of scope:** the mappers that consume them and the OpenAPI dicts that reference them. Name
  `/create-mapper` and `/create-docs` as follow-ups.
- **Done when:** the schemas exist, field names line up with the entity and the planned mappers,
  and ruff is clean.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Schema pattern) and
`app/modules/shared/presentation/schemas.py` for `CreateResponse`, `UpdateResponse`,
`DeleteResponse`, `StandardResponse`, `PaginationMeta`, `PaginationParams`.

## Step 2 — Load live patterns

Read `app/modules/key/presentation/schemas.py` — the most complete example: create/update
requests, a create response carrying a one-time secret, a detail response with actor projections,
a paginated list response, and `KeyPaginationParams`.

## Step 3 — Discovery

Derive the field set from the entity in `domain/entities.py`; ask only about the HTTP contract:

- Which entity fields are exposed, and which are internal. A hashed secret is never exposed; a
  transient plain secret is exposed exactly once, in the create and rotate responses.
- Response shape: a shared CRUD response, a custom detail response, or a paginated list.
- Whether related actors appear in the response — those get a compact `ActorResponse` projection,
  not a raw UUID.
- Validation at the edge: `min_length`, `max_length`, `ge`, `le`, `pattern`, enum choices.
- For a `PATCH` request: which fields are optional, and whether "at least one field present" needs
  a `@model_validator`.
- For a list endpoint: the sortable fields (these come from the `{Entity}SortField` enum).

## Step 4 — Generate

Templates for the request, partial-update request, custom response, one-time-secret response,
actor projection, paginated list response, and pagination params are in
[TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint

Run `uv run ruff check app/modules/{module}/presentation/schemas.py` and `uv run ruff format` on
it. Fix and re-run until clean.

Cross-check every field name against the entity and the mapper that will consume it — a mismatch
here surfaces as a silently dropped field at runtime, not as an error.

## Rules

- Every `Field(...)` declares `title`, `description`, `examples`, and `json_schema_extra`.
  Requests carry `"writeOnly": True`; responses carry `"readOnly": True`.
- `model_config = ConfigDict(...)` is the last member of the class, after fields and validators.
- `ConfigDict` always carries `title`, `str_strip_whitespace=True`, `extra="forbid"`,
  `validate_default=True`, `validate_assignment=True`, `validate_return=True`, and a
  `json_schema_extra` with `description` and `example`.
- `extra="forbid"` is deliberate — an unknown field is a client bug and must 422, not be ignored.
- Optional types are `X | None` with `default=None`. Never `Optional[X]`.
- Partial-update requests give every field `default=None`; the mapper reads `model_fields_set` to
  tell "omitted" from "explicitly null", so the schema must not distinguish them itself.
- Enum fields list the allowed values in the description:
  `f"Allowed values: {', '.join([e.value for e in MyEnum])}"`.
- `@field_validator` and `@model_validator` methods are `@classmethod`, named
  `validate_{field}`. Schema validation is the fast gate at the HTTP edge; the entity's domain
  validation still runs and is the real guarantee. Keep both.
- Structured names cross the API as separate `first_name` / `last_name` / `preferred_name` fields —
  the mapper assembles the `Name` value object. Free-form names are a single `name` field.
- Never redeclare `CreateResponse`, `UpdateResponse`, `DeleteResponse`, `PaginationMeta`, or
  `PaginationParams` — import them from `shared.presentation.schemas`.
- Never build the `StandardResponse` envelope in a schema; `ResponseFormattingMiddleware` adds it.
- Never expose a hashed secret, an internal FK to a private table, or a stack trace.
