# `.claude/` — Claude Code Assets Guide

Everything Claude Code needs to work on the **FastAPI Clean Architecture and DDD Template** with
this project's conventions. This guide explains what each asset is and when it applies — for both
humans and the model.

## Contents

- [How the pieces fit](#how-the-pieces-fit)
- [Commands, skills, and how they relate](#commands-skills-and-how-they-relate)
- [The documentation layer](#the-documentation-layer)
- [Which tool for which job](#which-tool-for-which-job)
- [Command reference](#command-reference)
- [Typical workflows](#typical-workflows)
- [The hook and the agent](#the-hook-and-the-agent)
- [Maintenance rules](#maintenance-rules)

## How the pieces fit

```
CLAUDE.md (repo root)          Facts and index: stack, modules, critical rules, naming.
                               Loaded automatically at the start of every session.
        │
        └── imports @.claude/architecture.md
.claude/
├── README.md                  This guide.
├── architecture.md            The pattern map. Every scaffolding skill reads it first.
├── reference/
│   ├── shared-module.md       The shared surface, SharedUseCases, UNSET, PaginatedList.
│   ├── persistence.md         ORM columns, enums, constraints, Alembic.
│   ├── caching.md             Redis namespace, tombstones, the never-raise policy.
│   └── security.md            Nested JWT, auth dependencies, API keys, allowlist tiers.
├── commands/*.md              23 slash commands — thin wrappers: frontmatter + an @-include.
├── plugins/fastapi-ddd-scaffolder/
│   ├── skills/*/SKILL.md      The full procedures — the single source of truth per workflow.
│   ├── agents/ddd-reviewer.md Read-only module auditor.
│   ├── hooks/hooks.json       PostToolUse ruff hook.
│   ├── README.md              Plugin detail: skills, hook, agent, distribution.
│   └── .claude-plugin/plugin.json
└── settings.local.json        Local, gitignored permission allowlist. Not documentation.
```

## Commands, skills, and how they relate

Claude Code merged custom commands into skills: a `SKILL.md` alone now provides **both** `/name`
invocation and automatic discovery. This project keeps both surfaces anyway, wired so they cannot
diverge:

- `.claude/plugins/fastapi-ddd-scaffolder/skills/<name>/SKILL.md` holds the **entire** procedure.
- `.claude/commands/<name>.md` holds **only** frontmatter plus an `@`-include of that skill.

```markdown
---
description: Creates a SQLAlchemy ORM model extending BaseModel …
argument-hint: "<module> <EntityName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

<arguments module="$0" entity="$1">$ARGUMENTS</arguments>

@.claude/plugins/fastapi-ddd-scaffolder/skills/create-model/SKILL.md
```

Two entry points, one procedure:

- Typing `/create-model key Key` runs the **command** — an explicit, manual trigger.
- Saying "add a database model for API keys" lets Claude load the **skill** on its own, matched
  from its `description`.

Keeping the wrappers means the commands work whether or not the plugin is enabled, and the `/name`
surface stays unprefixed rather than `/fastapi-ddd-scaffolder:name`.

**Edit the `SKILL.md`.** Touch a command only to change frontmatter, or to add and remove one
alongside a skill. Because the wrappers are derived from the skills' frontmatter, regenerate the
set rather than hand-editing it.

Three skills set `disable-model-invocation: true` — `verify`, `check-standards`, and
`sync-architecture`. They are repo-wide or long-running, so they run when you ask rather than when
Claude decides. One skill sets `user-invocable: false` — `architecture-context` is background
knowledge, not an action.

## The documentation layer

`architecture.md` is what every scaffolding skill reads first. It carries the project layout, the
nine modules and their real status, the four layers, the three error-handling shapes, the `shared`
surface, inherited fields, canonical code for every pattern, registration, testing, and the naming
table.

The four files under `reference/` hold the detail that would otherwise make `architecture.md` too
expensive to load on every run. Each is linked directly from both `architecture.md` and the skills
that need it, so nothing is ever more than one hop away:

| Read | When |
|------|------|
| `reference/shared-module.md` | Touching base types, `SharedUseCases`, `UNSET`, or a value object |
| `reference/persistence.md` | Writing a model, a constraint, or a migration |
| `reference/caching.md` | Anything involving Redis |
| `reference/security.md` | Auth dependencies, allowlist tiers, API keys, WebSocket auth |

When a pattern is ambiguous, the tiebreaker is in `architecture.md`: read two recently modified
non-`shared` modules. Patterns repeated across modules are authoritative; a deviation in a single
module is likely a bug. `key` is the most complete module and the best model for anything new.

## Which tool for which job

| You want to… | Use |
|--------------|-----|
| Build a whole feature | `/create-feature` — discovery → confirmed plan → ordered generation |
| Start a new module | `/create-module`, or `scripts/create_module.py` for bare empty files |
| Add one endpoint end to end | `/create-endpoint` |
| Add a single component | `/create-entity`, `/create-value-object`, `/create-exception`, `/create-model`, `/create-schema`, `/create-mapper`, `/create-repository-method`, `/create-cache`, `/create-service`, `/create-use-case`, `/create-docs`, `/create-router` |
| Take a model change to the database | `/create-migration` |
| Insert reference data | `/create-seed-migration` |
| Add an env var | `/add-setting` |
| Wire a module's routes into the app | `/register-module` |
| Write tests | `/create-test` |
| Check nothing broke | `/verify` — read-only |
| Audit conventions | `/check-standards` |
| Update these docs after the code moved | `/sync-architecture` |

## Command reference

Scaffolding:

| Command | Arguments | What it does |
|---------|-----------|--------------|
| `/create-feature` | `[description]` | Orchestrates discovery, a confirmed plan, then generation across every layer |
| `/create-module` | `<module-name>` | The four-layer tree with canonical stubs, plus `test/modules/<name>/` |
| `/create-endpoint` | `<module> <operation>` | One endpoint through every layer, ending in allowlist registration |
| `/create-entity` | `<module> <EntityName>` | Entity dataclass, paginated companions, sort-field enum |
| `/create-value-object` | `<module> <ValueObjectName>` | Value object with normalization and validation |
| `/create-exception` | `<module> <ExceptionName>` | Generic and per-rule exception classes |
| `/create-model` | `<module> <EntityName>` | SQLAlchemy model + `migrations/env.py` registration |
| `/create-migration` | `[message]` | Autogenerate → review → `alembic upgrade head` |
| `/create-seed-migration` | `<what-to-seed>` | Hand-written data seed with a reversible downgrade |
| `/create-schema` | `<module> <action>` | Pydantic v2 request and response schemas |
| `/create-mapper` | `<module> <action>` | schema↔entity, model↔entity, and cache serializers |
| `/create-repository-method` | `<module> <method>` | Protocol signature + Postgres implementation |
| `/create-cache` | `<module> <EntityName> [op]` | Cache Protocol, Redis implementation, mappers, DI, policy |
| `/create-service` | `<module> <ServiceName>` | Service Protocol, implementation, factory |
| `/create-use-case` | `<module> <operation>` | `{Module}UseCases` methods with the 3-branch shape |
| `/create-docs` | `<module> [endpoint]` | `router_docs` plus per-endpoint dicts |
| `/create-router` | `<module> <operation>` | Double-route handler + allowlist registration |
| `/register-module` | `<module>` | Router and tag in `app.py`, paths in the allowlist tiers |
| `/add-setting` | `<SETTING_NAME>` | An env var across `.env.example`, `.env`, `settings.py`, compose |

Quality and maintenance:

| Command | Arguments | What it does |
|---------|-----------|--------------|
| `/check-standards` | `[module\|all]` | Audits against `CHECKLIST.md`, reports with `file:line`, fixes with permission |
| `/create-test` | `<module> [component]` | pytest via Protocol fakes; bootstraps pytest on first run |
| `/verify` | `[module]` | Read-only smoke check: ruff, imports, registration |
| `/sync-architecture` | — | Drift detection between the code and these docs |

`architecture-context` has no command by design — it is background knowledge Claude loads on its
own, and there is nothing for a human to "run".

## Typical workflows

1. **New feature** — `/create-feature` → `/create-migration` → `/register-module` → `/verify`
2. **Small addition** — `/create-endpoint` → `/verify`
3. **Schema change** — `/create-model` → `/create-migration`
4. **Reference data** — `/create-seed-migration`
5. **New configuration** — `/add-setting`
6. **Tests** — `/create-test` (bootstraps pytest the first time)
7. **Docs drifted** — `/sync-architecture`
8. **Pre-release** — `/check-standards` → `/verify`

## The hook and the agent

The plugin ships two things a command file cannot:

- **`hooks/hooks.json`** — a `PostToolUse` hook on `Write|Edit` running
  `scripts/ruff-on-write.sh`, which formats and lints any Python file Claude touches under `app/`,
  `test/`, `scripts/`, or `migrations/`. Deterministic, so formatting does not depend on the model
  remembering a lint step. It exits 0 always and no-ops without `uv`.
- **`agents/ddd-reviewer.md`** — a read-only subagent (`Read`, `Glob`, `Grep`) that audits one
  module and returns `file:line` findings with a severity. `/check-standards` delegates to it when
  auditing more than four modules.

Editing `hooks/` or `agents/` needs `/reload-plugins`; live change detection covers `SKILL.md` text
only.

## Maintenance rules

- **The code is the source of truth for reality; `architecture.md` and `reference/` are the source
  of truth for documented conventions.** When they disagree, decide which is wrong first —
  `/sync-architecture` fixes the docs, `/check-standards` fixes the code.
- Content changes go in a `SKILL.md`, its companions, `architecture.md`, or `reference/` — never
  duplicated into a command file.
- Regenerate the command wrappers from the skills' frontmatter rather than editing them by hand,
  so `description`, `argument-hint`, and `allowed-tools` stay identical across each pair.
- Keep a `SKILL.md` under roughly 120 lines and push code bulk into a companion, one level deep.
  Once a skill is invoked, its body stays in context for the rest of the session, so every line is
  a recurring cost.
- Keep every `description` in the third person, leading with the key use case. It is the only thing
  Claude matches against when deciding whether to load a skill.
- Bump `plugin.json` `version` for structural changes — skills added or removed, procedures
  overhauled.
- `settings.local.json` is personal, gitignored permission configuration. It is not part of the
  documentation system.
