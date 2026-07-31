---
name: verify
description: Smoke-checks freshly scaffolded or edited code — runs ruff, confirms the app graph imports, checks module and allowlist registration, and optionally boots the app. Read-only; reports findings with real command output and offers fixes without applying them. Use right after scaffolding a module or endpoint, or when the user asks to verify or sanity-check a change.
argument-hint: "[module]"
allowed-tools: Read, Glob, Grep, Bash(uv run *), Bash(ls *), Bash(git status *)
disable-model-invocation: true
---

# Verify Scaffolded Code

<task>Run fast read-only checks confirming the code lints, imports, and is registered. Report pass or fail with the real command output.</task>

Current modules:

!`ls app/modules`

Pending changes:

!`git status --porcelain`

## Scope

- **In scope:** lint, import resolution, registration checks, and — only when asked — an app boot.
- **Out of scope:** fixing anything. This skill reports; it does not edit, migrate, or install.
  Convention violations go to `/check-standards`; a broken pattern goes to the skill that owns it.
- **Done when:** every applicable check has run and been reported with its output.

## Step 1 — Scope the run

If the user named a module, check that module. Otherwise use the files in the git status above,
falling back to the whole `app/` tree when the status is empty.

## Step 2 — Run the checks

Copy this checklist and fill it in:

```
Verify:
- [ ] Lint (ruff)
- [ ] Format (ruff format --check)
- [ ] Imports
- [ ] Module registration (new modules only)
- [ ] Allowlist registration (new endpoints only)
- [ ] Model registration (new models only)
- [ ] Tests (only if pytest is installed)
- [ ] App boot (only if asked)
```

**Lint** — `uv run ruff check .`, or scoped to `app/modules/{module}`. Report errors verbatim.

**Format** — `uv run ruff format --check .` on the same scope. A file that would be reformatted is
a finding, not a failure.

**Imports** — `uv run python -c "import app.app"` exercises the whole graph, including
`app/app.py`'s router imports and every module they pull in. For a single module, also
`uv run python -c "import app.modules.{module}.presentation.routers"`.

**Module registration** — only when a module was just created. Grep `app/app.py` for the router
import, the entry in the `routers` list, and the tag in `custom_openapi()`.

**Allowlist registration** — only when endpoints were just added. For each new endpoint, grep
`app/core/settings.py` for a `_path_rule` entry in the tier matching its `authenticate_*`
dependency, in **both** slash forms. A missing entry means a 403 with a valid token.

**Model registration** — only when a model was just added. Grep `migrations/env.py` for the import
and the entry in the `_ = [...]` list. A missing entry makes autogenerate emit a `drop_table` for
the live table.

**Tests** — only when pytest is a dependency (grep `pyproject.toml`). Then
`uv run pytest test/modules/{module} -q`. Skip silently otherwise; bootstrapping pytest belongs to
`/create-test`.

**App boot** — only when the user asks. `uv run uvicorn app.app:app --port 8000` in the background,
confirm a healthy startup in the log, then stop it. Never leave a server running. Note that a boot
needs Postgres and Redis reachable and will run Alembic upgrade-to-head.

## Step 3 — Report

One line per check with its verdict, followed by the exact output of anything that failed. Name the
file and line. If everything passed, say so in a sentence.

Where a fix is obvious, describe it and name the skill that owns it — do not apply it here.

## Rules

- Read-only. No edits, no migrations, no installs, no `alembic upgrade`.
- Surface real command output. Never paraphrase a failure as a pass, and never report a check as
  run when it was skipped — say it was skipped and why.
- Keep it fast. No full test suite, no long-lived processes, unless asked.
- Forward slashes in every path.
