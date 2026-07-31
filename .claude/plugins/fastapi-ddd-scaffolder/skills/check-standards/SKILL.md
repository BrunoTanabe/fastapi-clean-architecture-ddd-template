---
name: check-standards
description: Audits modules against the project's architectural conventions — layer boundaries, the three error-handling shapes, naming, mapper completeness, cache rules, and registration — reporting every violation with a file and line citation, then fixing with permission. Use when the user asks to check standards, audit the architecture, run a compliance pass, or sanity-check before a release.
argument-hint: "[module|all]"
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
disable-model-invocation: true
---

# Check Project Standards

<task>Audit one module, or every non-`shared` module, against the project's conventions. Report violations with citations, then fix with permission.</task>

Current modules:

!`ls app/modules`

## Scope

- **In scope:** convention compliance in `app/modules/`, plus the registration files those modules
  depend on.
- **Out of scope:** whether the design is right. A module that follows every convention and solves
  the wrong problem passes this audit. Say so if you notice, but do not restructure.
- **Done when:** every rule has been applied to every target and the report is delivered. Fixing
  happens only after the user chooses.

Copy this checklist and tick it off:

```
Audit progress:
- [ ] Reference read
- [ ] Targets enumerated
- [ ] Every layer file read
- [ ] Checklist applied
- [ ] Report delivered
- [ ] Fixes applied (with permission) and re-verified
```

## Step 1 — Load the reference

Read `.claude/architecture.md`, plus `reference/caching.md` and `reference/security.md` when the
targets cache or expose routes.

## Step 2 — Enumerate targets

Glob `app/modules/*/`. Exclude `shared` — it defines the base types the rules are written against,
so it is authoritative by construction. Honour the user's scope: a module name, `all`, or empty
(defaults to all).

**Documented status, not violations.** Do not report these:

- Single-process `ConnectionManager` fan-out in `websocket`.
- The partial `knowledge` cache — `IKnowledgeCache` declaring only `insert`, and
  `KnowledgeUseCases` holding a `cache` collaborator it does not call.
- `SECURITY_API_KEY_ALLOWED_PATHS` returning an empty tuple.
- Empty `caches.py`, `services.py`, `utils.py`, `value_objects.py`, `enums.py`, `models.py`,
  `repositories.py`, or `interfaces.py`. The full skeleton is the convention.
- `test/modules/notifications/` being plural.
- `example` having no repository, model, or interfaces.

## Step 3 — Read before reporting

Read every layer file of each target before checking anything, so each finding is grounded in the
code rather than in a guess:

`domain/{entities,value_objects,enums}.py`,
`application/{interfaces,use_cases,mappers,exceptions,utils}.py`,
`infrastructure/{models,repositories,caches,services}.py`,
`presentation/{schemas,routers,docs,dependencies}.py`.

For modules with routes, also read `app/app.py` and `app/core/settings.py`. For modules with
models, also read `migrations/env.py`.

Delegating a wide audit is reasonable: with `all` and more than four modules, run the plugin's
`ddd-reviewer` agent once per module so each gets a clean context, then merge the findings. For a
single module, do it inline.

## Step 4 — Apply the checklist

The rule-by-rule checklist is in [CHECKLIST.md](CHECKLIST.md). Load it and apply every rule.

## Step 5 — Report

```
## Standards audit — {target}

### Violations

#### [{module}] {layer}/{file}
| # | Severity | Rule | Location | Issue | Fix |
|---|----------|------|----------|-------|-----|
| 1 | high | Error shape | `app/modules/x/application/use_cases.py:42` | `except Exception` precedes `except StandardException`, so every 404 becomes a 500 | Reorder the branches |

### Passing
{one line per module}

### Summary
{N} violations across {Y} files — {A} high, {B} medium, {C} low. {Z} mechanically fixable.
```

Severity: **high** changes behaviour (wrong error-branch order, missing allowlist entry, missing
inherited field in a mapper, missing cache invalidation, `commit()` in a repository); **medium**
risks behaviour (missing `is_active` filter, unindexed foreign key, missing `joinedload` where
actors are projected); **low** is style (naming, section headers, log level).

Report everything you find. The user filters in the next step — an audit that pre-filters is not
an audit.

## Step 6 — Fix with permission

Ask:

> Found {N} violations. How should I proceed?
> - **Fix all** — apply every mechanical fix
> - **High only** — behaviour-changing findings
> - **By module** — confirm each module
> - **Show diffs first** — preview before applying

Use `Edit` for surgical fixes. Never rewrite a whole file to fix a rule. After fixing, run
`uv run ruff check` on the touched files and re-check the affected rules; repeat until clean.

Report what was fixed and what was left, and why.

## Rules

- `shared` is authoritative — never report a violation against it.
- A pattern present in one non-`shared` module and nowhere else is a candidate bug, not a new
  convention. A pattern repeated across modules is the convention, even when it contradicts an
  older note.
- Cite `file:line` for every finding. A finding without a location is not actionable.
- Do not report the documented in-progress areas listed in Step 2.
- Do not change behaviour while fixing a style violation. If a fix is not mechanical, describe it
  and leave it to the user.
