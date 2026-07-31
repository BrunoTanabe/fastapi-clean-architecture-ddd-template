---
name: sync-architecture
description: Detects drift between the project code and the documentation under .claude/ — CLAUDE.md, architecture.md, the reference files, the plugin skills, and the command wrappers — then updates the docs surgically. Use after refactoring shared base types, adopting a new pattern, adding or renaming a module, bumping Python, or when the user says the docs are out of date.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git log *), Bash(ls *)
disable-model-invocation: true
---

# Sync Architecture Docs

<task>Reconcile the documentation under `.claude/` and `CLAUDE.md` with what the code actually does. The code is the source of truth; the docs follow.</task>

## Scope

- **In scope:** documentation only.
- **Out of scope:** changing code to match the docs. If the code violates an intentional
  convention, that is a `/check-standards` finding, not a doc update. Report it and leave the code
  alone.
- **Done when:** every drift item is either applied or explicitly deferred, and the report says
  which.

## Doc topology — where a fix lands

```
CLAUDE.md                                  facts + index; imports @.claude/architecture.md
.claude/architecture.md                    the map: layers, patterns, naming
.claude/reference/*.md                     deep detail: shared-module, persistence, caching, security
.claude/plugins/…/skills/*/SKILL.md        procedures
.claude/plugins/…/skills/*/TEMPLATES.md    code shapes
.claude/commands/*.md                      thin wrappers: frontmatter + @-include
.claude/README.md                          the guide to all of the above
```

Content drift is fixed in `architecture.md`, the reference files, the skills, and `CLAUDE.md`. A
**command wrapper changes only** when its frontmatter must change or a skill is added or removed —
its body is an `@`-include and can never drift.

## When to run

After a change to `BaseModel`, `BaseEntity`, `StandardException`, `ResponseMessages`, or the
`shared` surface; after adopting a new pattern; after adding, renaming, or removing a module;
after a Python or major dependency bump; after completing one of the documented in-progress areas;
or periodically to keep the docs honest.

## Step 1 — Sample the project

Read the canonical sources listed in [CANONICAL_SOURCES.md](CANONICAL_SOURCES.md). Use
`git log --oneline -20` to see what moved recently and focus there first.

## Step 2 — Read the current documentation

`CLAUDE.md`, `.claude/architecture.md`, `.claude/reference/*.md`, `.claude/README.md`, every
`SKILL.md` and companion, `.claude/commands/*.md`, the plugin `README.md`, and
`.claude-plugin/plugin.json`.

## Step 3 — Detect drift

<structural>
- Fields on `BaseModel` or `BaseEntity`; the `StandardException` signature; new `ResponseMessages`
  members or shared exceptions.
- The `shared` export surface — especially value objects moving between `shared` and a module.
- `SharedUseCases` constructor or method surface.
- Modules added, renamed, or removed under `app/modules/`.
- Cache-layer coverage: which modules implement `I{Entity}Cache`, whether their use cases call it,
  and which Redis settings are consumed.
- Service layer: new `I{Name}Service` Protocols and implementations.
- `app/core/security.py` — new `authenticate_*` dependencies, API-key surface, token entities.
- Allowlist tiers in `app/core/settings.py`; new settings groups.
- `migrations/env.py` registration list; whether `migrations/versions/` is still empty.
- Python version, Docker images, and Makefile targets.
</structural>

<patterns>
- The three error-handling shapes, and which layers use which.
- Use-case collaborators and `disable_exceptions()` usage.
- The `UNSET` partial-update protocol.
- automapper conventions, section ordering, and reserved-column bridges.
- ORM constraint patterns, enum column shape, cascades.
- Router double-route form and the injected authentication type.
- `ConfigDict` settings and pagination params.
- Repository pagination via window function.
- Cache namespace, key shapes, tombstones, and the never-raise policy.
</patterns>

<naming>
Table prefix, constraint and index names, class naming, router prefix, mapper function names,
test file names.
</naming>

Check every skill's `description` too: it is what makes the skill discoverable, and a description
naming a renamed type is drift that silently stops the skill from triggering.

## Step 4 — Report

```
## Architecture sync report

### Reference modules sampled
{modules}

### Aligned
{one line per area still correct}

### Drift

#### drift-{n}: {short description}
- **In the code:** `{file}:{line}` — {what it does now}
- **Docs say:** "{quote}" in `{doc file}`
- **Affects:** {list of doc files}
- **Proposed change:** {exact replacement wording}
```

## Step 5 — Confirm and apply

> Found {N} drift items. Proceed how?
> - **Update all**
> - **One by one** — confirm each
> - **Skip for now**

When approved, edit in dependency order so cross-references stay valid:

1. `.claude/architecture.md`
2. `.claude/reference/*.md`
3. The affected `SKILL.md` and companions
4. `CLAUDE.md`
5. `.claude/README.md`
6. Command wrappers — only for frontmatter changes, or to create/delete a wrapper alongside a
   skill
7. The plugin `README.md`, and bump `plugin.json` `version` for a structural change

Then re-read what you changed and confirm it matches the code.

## Rules

- The code is the source of truth for what *is*. The docs are the source of truth for what *should
  be*. When they disagree, decide which one is wrong before editing — and when it is the code,
  hand off to `/check-standards` instead of documenting the bug.
- `shared` is authoritative. A pattern in `shared` overrides a conflicting pattern in any single
  module.
- A pattern present in exactly one non-`shared` module is a candidate bug. Flag it; do not bake it
  into the docs.
- Documented in-progress areas describe a target state on purpose. Code matching an "unfinished"
  description is not drift — but code that *completes* one of them is, and the status note must
  then be removed.
- Keep the edits surgical. Rewrite a whole doc file only when its subject changed wholesale.
- Update the skill `description` fields whenever the terms a user would say have changed.
- When unsure whether a change was intentional, ask before documenting it.
