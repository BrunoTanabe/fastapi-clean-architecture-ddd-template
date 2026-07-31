---
name: create-docs
description: Adds OpenAPI documentation to a module — the router_docs dict carrying the prefix, tag, and standard error responses, plus one {action}_docs dict per endpoint with summary, description, status code, response model, and examples. Use when the user asks to add OpenAPI docs, document an endpoint, or populate presentation/docs.py.
argument-hint: "<module> [endpoint]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create OpenAPI Documentation

<task>Add `router_docs` and the per-endpoint `{action}_docs` dicts to `app/modules/{module}/presentation/docs.py`.</task>

## Scope

- **In scope:** `router_docs` and the `{action}_docs` dicts for the endpoints named.
- **Out of scope:** the handlers that consume them, the OpenAPI tag entry in `app/app.py`, and the
  allowlist rules. Name `/create-router` and `/register-module` as follow-ups.
- **Done when:** every documented endpoint has a dict, the response models match the handlers'
  return annotations, and ruff is clean.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Docs pattern).

## Step 2 — Load live patterns

Read `app/modules/key/presentation/docs.py` — the canonical reference, with the full error block
and six endpoint dicts. Read `app/app.py` to confirm the tag name registered in
`custom_openapi()`.

This is the most copy-heavy file in a module. Take the verbatim shape and change only the module
name, prefix, paths, schemas, and examples.

## Step 3 — Discovery

Derive most of it from `presentation/routers.py` and `presentation/schemas.py`; ask only about:

- The router prefix and OpenAPI tag.
- A one-line summary and a fuller description per endpoint.
- The success status code per endpoint.
- Endpoint-specific error responses beyond the router-level set — 404 for a lookup, 409 for a
  uniqueness conflict.

## Step 4 — Generate

Templates for `router_docs` and every endpoint shape are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint

Run `uv run ruff check app/modules/{module}/presentation/docs.py` and `uv run ruff format` on it.
Fix and re-run until clean.

Confirm each `response_model` matches the return annotation of the handler that uses the dict — a
mismatch produces an OpenAPI schema that lies about the response.

If the module's tag is new, say so and point at `/register-module`.

## Rules

- `router_docs` carries `prefix`, `tags`, and `responses`. The `tags` value must match the name
  registered in `custom_openapi()` in `app/app.py`, or the endpoints land in an undocumented group.
- The router-level `responses` block declares the standard error codes — 400, 401, 403, 405, 422,
  500, 502, 504 — so every endpoint inherits a complete error contract. Add 409 at the router level
  when any endpoint in the module can conflict.
- Every error entry is `{"model": StandardResponse, "description": ..., "content": {...}}`, and
  every example carries `code`, `method`, `path`, `timestamp`, and
  `details: {message, data}` — the shape `ResponseFormattingMiddleware` actually produces. An
  example that omits the envelope teaches clients the wrong shape.
- Messages in examples come from `ResponseMessages`, never hardcoded strings.
- Endpoint dicts are named `{action}_docs`, matching the handler function: `create_docs`,
  `get_all_docs`, `get_docs`, `update_docs`, `rotate_docs`, `delete_docs`.
- Each endpoint dict declares `summary`, `description`, `response_description`, `status_code`,
  `response_model`, `include_in_schema=True`, and `responses` with at least the success example.
- Use `HTTPStatus` constants, not integer literals, for `status_code`.
- `include_in_schema=False` belongs only on the second route decorator in `routers.py` — never in
  an endpoint docs dict.
- Never put a real credential, token, or personal email in an example. Use obviously fake values.
- Document a one-time secret as such in the `description` — that the value is returned once and
  cannot be retrieved again is part of the contract.
