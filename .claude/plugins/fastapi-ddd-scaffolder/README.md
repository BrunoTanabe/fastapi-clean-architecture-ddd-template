# fastapi-ddd-scaffolder

Scaffolding, auditing, migration, and testing skills for the **FastAPI Clean Architecture and DDD
Template**. Tailored to this codebase's conventions: Python 3.14, async SQLAlchemy 2, Pydantic v2,
py-automapper, loguru, Redis cache-aside with tombstones, nested JWT via jwcrypto, and pwdlib
(argon2).

Every skill follows Anthropic's skill-authoring guidance: a concise `SKILL.md` with a description
that triggers reliably, plus on-demand companions (`TEMPLATES.md`, `CHECKLIST.md`,
`PLAN_TEMPLATE.md`, `CANONICAL_SOURCES.md`) that cost nothing until they are read. Every
scaffolding skill starts by reading `.claude/architecture.md`, the project's canonical pattern
reference.

## Contents

- [Skills](#skills)
- [Hook](#hook)
- [Agent](#agent)
- [Recommended workflows](#recommended-workflows)
- [Skills and commands](#skills-and-commands)
- [Structure](#structure)
- [Setup and distribution](#setup-and-distribution)

## Skills

24 skills. 23 are user-invocable as `/name`; `architecture-context` is model-only background
knowledge.

### Reference

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `architecture-context` | auto-loaded by other skills | Points at `architecture.md` and the four reference files; `user-invocable: false` |

### Orchestration

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-feature` | "build a feature", "implement X", "add a capability" | Discovery → confirmed plan → ordered generation across every layer |
| `create-module` | "scaffold a module", "new bounded context" | The four-layer tree with canonical stubs, plus the test package |
| `create-endpoint` | "add an endpoint", "add a CRUD operation" | One endpoint through every layer, ending in allowlist registration |

### Domain

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-entity` | "add a domain entity", "model this" | Entity dataclass with `__post_init__` validation, paginated companions, sort-field enum |
| `create-value-object` | "add a value object", "wrap this primitive" | `_normalize` / `_validate` / `__str__` / `__eq__`, with the shared-vs-module placement rule |
| `create-exception` | "add an error case", "not-found exception" | Generic `{Module}Exception` plus one class per business rule, mapped to `ResponseMessages` |

### Application

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-use-case` | "add business logic", "orchestrate this" | `{Module}UseCases` methods, the 3-branch shape, the `UNSET` merge, cache-aside policy |
| `create-mapper` | "add a mapper", "wire the conversion" | schema↔entity, model↔entity, and cache serializers in the three-section layout |

### Infrastructure

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-model` | "add a database model", "add a table" | SQLAlchemy model + registration in `migrations/env.py` |
| `create-repository-method` | "add a query", "add a repository method" | Protocol signature + Postgres implementation, interface first |
| `create-cache` | "add a cache", "cache this lookup" | `I{Entity}Cache`, `Redis{Entity}Cache` with tombstones, cache mappers, DI, use-case policy |
| `create-service` | "integrate an external system" | `I{Name}Service` Protocol + implementation + factory |

### Presentation

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-schema` | "add a schema", "request/response models" | Pydantic v2 with full `Field` and `ConfigDict`, plus pagination params |
| `create-docs` | "add OpenAPI docs", "document the endpoint" | `router_docs` with the standard error block, plus per-endpoint dicts |
| `create-router` | "add a route", "add the handler" | Double-route handler, `Authentication` injection, 3-branch errors, allowlist |

### Data and configuration

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `create-migration` | "create a migration", "apply the schema change" | Registration check → autogenerate → review → upgrade |
| `create-seed-migration` | "seed data", "insert default rows" | Hand-written revision with bound parameters and a reversible downgrade |
| `add-setting` | "add an env var", "add a setting" | `.env.example` → `.env` → `settings.py` field → validator → computed field → compose |
| `register-module` | "register the module", "endpoint returns 403" | Router and tag in `app/app.py`, path rules in the allowlist tiers |

### Quality

| Skill | Trigger phrases | What it does |
|-------|-----------------|--------------|
| `check-standards` | "audit the architecture", "check standards" | Applies the full checklist, reports with `file:line` and severity, fixes with permission |
| `create-test` | "write tests", "test this module" | Protocol fakes, entity validation, use-case paths, mapper round-trips; bootstraps pytest |
| `verify` | "verify", "sanity check" | Read-only: ruff, imports, registration; reports without editing |
| `sync-architecture` | "the docs are stale", "sync the architecture" | Drift detection between code and `.claude/`, applied surgically |

`check-standards`, `verify`, and `sync-architecture` set `disable-model-invocation: true` — they
are longer-running or repo-wide, so they run when you ask, not when Claude decides.

## Hook

`hooks/hooks.json` registers a `PostToolUse` hook on `Write|Edit` that runs
`scripts/ruff-on-write.sh`. For a Python file under `app/`, `test/`, `scripts/`, or `migrations/`
it runs `uv run ruff format` then `uv run ruff check --fix` on that file.

This is deterministic where a skill instruction is not: formatting happens whether or not the
model remembers the lint step. The script exits 0 in every case, so it never blocks work, and it
no-ops when `uv` is unavailable.

`/reload-plugins` is required after editing `hooks/` — live change detection covers `SKILL.md`
text only.

## Agent

`agents/ddd-reviewer.md` is a read-only subagent (`Read`, `Glob`, `Grep` only) that audits one
module against `CHECKLIST.md` and returns `file:line` findings with a severity. `check-standards`
delegates to it when auditing more than four modules, so each module gets a clean context instead
of competing for one.

It appears as `fastapi-ddd-scaffolder:ddd-reviewer` in the `@`-mention list.

## Recommended workflows

**New feature from scratch**
`/create-feature` — plans, confirms, then delegates to the component skills.

**Adding to an existing module**
`/create-endpoint`, then `/verify`. Or target one layer: `/create-schema`, `/create-mapper`,
`/create-repository-method`, `/create-use-case`, `/create-router`, `/create-docs`.

**Schema change**
`/create-model` → `/create-migration`.

**Reference data**
`/create-seed-migration`.

**Module gains its first routes**
`/register-module`.

**New configuration**
`/add-setting`.

**Before a release**
`/check-standards` → `/verify`.

**After refactoring shared patterns**
`/sync-architecture`.

## Skills and commands

This project ships matching wrappers under `.claude/commands/` — each holds only frontmatter
(description, argument-hint, allowed-tools) and an `@`-include of the paired `SKILL.md`. The skill
file is the single source of truth, so the two surfaces cannot diverge.

Claude Code has since merged custom commands into skills: a `SKILL.md` alone already provides both
`/name` invocation and automatic discovery. The wrappers are kept deliberately — they let the
project expose the commands whether or not the plugin is enabled, and they keep the `/name` surface
unprefixed.

A wrapper changes only when its frontmatter changes or a skill is added or removed. Regenerate the
whole set from the skills' frontmatter rather than editing them by hand.

- **Skills** are model-invoked: Claude loads one when you describe the task naturally.
- **Commands** are manual: you type `/create-model` to run the same procedure explicitly.

## Structure

```
fastapi-ddd-scaffolder/
├── .claude-plugin/
│   └── plugin.json                        # manifest
├── README.md                              # this file
├── agents/
│   └── ddd-reviewer.md                    # read-only module auditor
├── hooks/
│   └── hooks.json                         # PostToolUse ruff hook
├── scripts/
│   └── ruff-on-write.sh                   # the hook implementation
└── skills/
    ├── add-setting/                       # SKILL.md + TEMPLATES.md
    ├── architecture-context/SKILL.md
    ├── check-standards/                   # SKILL.md + CHECKLIST.md
    ├── create-cache/                      # SKILL.md + TEMPLATES.md
    ├── create-docs/                       # SKILL.md + TEMPLATES.md
    ├── create-endpoint/                   # SKILL.md + TEMPLATES.md
    ├── create-entity/                     # SKILL.md + TEMPLATES.md
    ├── create-exception/                  # SKILL.md + TEMPLATES.md
    ├── create-feature/                    # SKILL.md + PLAN_TEMPLATE.md
    ├── create-mapper/                     # SKILL.md + TEMPLATES.md
    ├── create-migration/SKILL.md
    ├── create-model/                      # SKILL.md + TEMPLATES.md
    ├── create-module/                     # SKILL.md + TEMPLATES.md
    ├── create-repository-method/          # SKILL.md + TEMPLATES.md
    ├── create-router/                     # SKILL.md + TEMPLATES.md
    ├── create-schema/                     # SKILL.md + TEMPLATES.md
    ├── create-seed-migration/SKILL.md
    ├── create-service/                    # SKILL.md + TEMPLATES.md
    ├── create-test/                       # SKILL.md + TEMPLATES.md
    ├── create-use-case/                   # SKILL.md + TEMPLATES.md
    ├── create-value-object/                # SKILL.md + TEMPLATES.md
    ├── register-module/SKILL.md
    ├── sync-architecture/                 # SKILL.md + CANONICAL_SOURCES.md
    └── verify/SKILL.md
```

## Setup and distribution

No external services required. Skills use `Read`, `Write`, `Edit`, `Glob`, and `Grep`, plus scoped
`Bash` for ruff, imports, Alembic, and pytest. They inherit your permission settings.

Validate the manifest with:

```bash
claude plugin validate .claude/plugins/fastapi-ddd-scaffolder --strict
```

The plugin is consumed directly from this directory. To use it from another checkout, point Claude
Code at it with `claude --plugin-dir`, or copy the directory into that project's
`.claude/plugins/`.

Bump `version` in `plugin.json` for structural changes — skills added or removed, or a procedure
overhauled.
