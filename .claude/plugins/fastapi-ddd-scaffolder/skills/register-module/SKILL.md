---
name: register-module
description: Wires a completed module into the application — the router import and entry in app/app.py, the OpenAPI tag in custom_openapi, and both slash forms of every endpoint in the matching SECURITY_*_ALLOWED_PATHS tier. Use when the user asks to register a module, wire up a router, or when a new endpoint returns 403 with a valid token.
argument-hint: "<module>"
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
---

# Register a Module

<task>Wire a module that has routes into `app/app.py` and `app/core/settings.py`, then confirm the app imports.</task>

Current modules:

!`ls app/modules`

## Scope

- **In scope:** the router import and list entry, the OpenAPI tag, and the allowlist rules for
  every endpoint the module exposes.
- **Out of scope:** creating endpoints. A module with an empty router stays unregistered.
- **Done when:** the app imports, every endpoint has both slash forms in the right tier, and the
  tag matches `router_docs`.

## Step 1 — Read the current wiring

1. `app/app.py` — the router import group, the `routers` list, and the `tags` list inside
   `custom_openapi()`.
2. `app/core/settings.py` — the `_path_rule` helper and the five allowlist properties.
3. The module's `presentation/routers.py` and `presentation/docs.py` — enumerate every endpoint
   with its method, path, and `authenticate_*` dependency.

Build that enumeration before editing anything. The allowlist step is mechanical only once you
have the complete list, and a missed endpoint is invisible until someone calls it.

## Step 2 — Register in `app/app.py`

Three edits:

```python
from app.modules.{module}.presentation.routers import router as {module}_router
```

```python
routers = [
    authentication_router,
    {module}_router,        # alphabetical
    ...
]
```

```python
        tags=[
            {
                "name": "{Module}",
                "description": "Endpoints for managing {module} resources.",
            },
            ...
        ],
```

The tag name must match `router_docs["tags"]` in the module's `docs.py`, or its endpoints land in
an undocumented group in the OpenAPI schema.

## Step 3 — Register the allowlist paths

For each endpoint, add **both** slash forms to the tier matching its dependency:

| Dependency | Tier |
|------------|------|
| `no_authentication` | `SECURITY_NO_AUTH_PATHS` |
| `authenticate_user` | `SECURITY_USER_ALLOWED_PATHS` |
| `authenticate_manager` | `SECURITY_MANAGER_ALLOWED_PATHS` |
| `authenticate_admin` | `SECURITY_ADMIN_ALLOWED_PATHS` |

```python
    # {MODULE}
    _path_rule("/api/v1/{module}/", "POST"),
    _path_rule("/api/v1/{module}", "POST"),
    _path_rule("/api/v1/{module}/{id}/", "PATCH"),
    _path_rule("/api/v1/{module}/{id}", "PATCH"),
```

Tiers cascade — each spreads the previous one — so declare each path once, in the lowest tier that
should reach it. Registering an admin path in the user tier silently grants it to every user.

Path parameters keep the `{id}` placeholder; `_match_path_rules` converts it to `(?P<id>[^/]+)`,
so a parameter can never span a `/`.

`SECURITY_API_KEY_ALLOWED_PATHS` is a separate, currently empty tier for machine-to-machine
access. Add to it only when the endpoint is explicitly meant to be callable with an API key.

## Step 4 — Verify

1. `uv run ruff check app/app.py app/core/settings.py` and `uv run ruff format` on both. Fix and
   re-run until clean.
2. `uv run python -c "import app.app"` — the whole app graph must import.
3. Grep the settings file for the module's prefix and confirm the rule count is exactly twice the
   number of endpoints.

Report the endpoint-to-tier mapping you registered, so the permissions are reviewable at a glance.

## Rules

- Register only after the module has real routes.
- Keep the import group and the `routers` list alphabetical; keep allowlist rules grouped under an
  uppercase `# {MODULE}` comment.
- Both slash forms for every rule. This is the single most common omission and it presents as an
  authentication bug, not a routing one.
- An endpoint missing from its tier returns 403 even with a valid token — the dependency and the
  allowlist both have to allow it.
- Public endpoints still need an entry: `no_authentication` checks `SECURITY_NO_AUTH_PATHS`.
- WebSocket routes are not registered in any HTTP tier; `authenticate_websocket` is the whole
  check. The `GET` decoy route that documents the channel does need a `SECURITY_NO_AUTH_PATHS`
  entry.
