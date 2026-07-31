---
name: add-setting
description: Adds a configuration value across every place it must appear — .env.example, .env, the typed field in app/core/settings.py, any validator or computed_field, and docker-compose when a container needs it. Use when the user asks to add an env var, a setting, a feature flag, a timeout, or configuration for a new integration.
argument-hint: "<SETTING_NAME>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Add a Setting

<task>Add a configuration value to every file it must appear in, so the app starts with it and a fresh clone knows it exists.</task>

## Scope

- **In scope:** `.env.example`, `.env`, the `Settings` field, any validator or `computed_field`,
  and `docker-compose.yaml` when a container needs the value.
- **Out of scope:** the code that consumes the setting. Add the setting, then let the caller be
  written by whichever skill owns that layer.
- **Done when:** every file below is updated and `Settings()` loads without error.

Half-finished settings are the failure mode here: a field added to `settings.py` but not to
`.env.example` breaks every fresh clone at startup, because `BaseSettings` raises on a missing
required field.

Copy this checklist and tick it off:

```
Setting: {NAME}
- [ ] .env.example — key, empty or safe placeholder value
- [ ] .env — real local value
- [ ] settings.py — typed field in the right group
- [ ] settings.py — validator, if the raw value needs coercion
- [ ] settings.py — computed_field, if something is derived from it
- [ ] docker-compose.yaml — only if a container consumes it
- [ ] Settings() loads
```

## Step 1 — Read the current configuration

Read `app/core/settings.py` — the field groups, the `model_config`, the `field_validator`s, and
the `computed_field` properties. Read `.env.example` for the group ordering and comment style.

Settings are grouped by uppercase comment (`# APPLICATION`, `# API KEY`, `# AUTH`, `# COOKIES`,
`# JWT`, `# LOGS`, `# NGROK`, `# POSTGRESQL`, `# REDIS`, `# SECURITY SETTINGS`). Add to the
matching group in both files, keeping the same order.

## Step 2 — Discovery

- Name, in `SCREAMING_SNAKE_CASE`, prefixed with its group (`REDIS_`, `JWT_`, `SECURITY_`).
- Type: `str`, `int`, `bool`, `list[str]`, or an enum from `shared/domain/enums.py`.
- Required, or optional with a default. Prefer required — a silent default that differs between
  environments is harder to debug than a startup error.
- Whether it is a secret. Secrets get an empty value in `.env.example` and a real one only in
  `.env`.
- Whether anything is derived from it — a URL, a duration in seconds, a namespace.
- Whether a Docker container needs it.

## Step 3 — Generate

Templates for the field, list and enum types, validators, computed fields, and the compose entry
are in [TEMPLATES.md](TEMPLATES.md).

Order matters: add the key to `.env` **before** the field to `settings.py`, so the app never sits
in a state where it cannot start.

## Step 4 — Confirm it loads

```bash
uv run python -c "from app.core.settings import settings; print(settings.{NAME})"
```

A `ValidationError` here names the missing or malformed key exactly. For a `computed_field`, print
that too — `cached_property` errors only surface on first access, not at construction.

Then `uv run ruff check app/core/settings.py` and `uv run ruff format` on it.

## Rules

- Every key exists in **both** `.env.example` and `.env`. `.env.example` is the contract for a
  fresh clone; a key missing there is a startup failure for the next person.
- Never put a real secret, token, password, or private URL in `.env.example`. Leave the value
  empty, or use an obviously fake placeholder.
- Settings are read through `settings`, never `os.environ` or `os.getenv`, and never at import time
  in a module. `Settings` is the single typed entry point for configuration.
- Give the field a real type. `bool`, `int`, and `list[str]` are parsed by pydantic-settings —
  declaring one as `str` and parsing it by hand defeats the point.
- Group the field under the matching uppercase comment, in the same order in both files.
- Derived values are `@computed_field` + `@cached_property` with `# noqa` on the uppercase method
  name, following `REDIS_URL`, `REDIS_NAMESPACE`, and `COOKIES_ACCESS_TOKEN_MAX_AGE`. Compute them
  once in `settings.py` rather than recomputing at call sites.
- A `cached_property` is computed once per process. Do not use one for a value that must be
  re-read while the app runs.
- Enum-typed settings need a `field_validator(mode="before")` that accepts the raw string and
  raises a clear `ValueError` listing the allowed values — see `COOKIES_SAME_SITE`.
- The global `strip_quotes` validator already removes surrounding quotes from every string value,
  so `.env` values may be quoted or bare.
- Adding a required field without a default is a breaking change for every existing deployment.
  Say so when you do it.
