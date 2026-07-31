---
name: create-test
description: Creates pytest tests for a module — entity and value-object validation, use cases driven by in-memory fakes of the repository, cache, and service Protocols, and mapper round-trips. Bootstraps pytest on first run. Use when the user asks to write tests, add tests for a module, or cover a use case.
argument-hint: "<module> [component]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Create Module Tests

<task>Write unit tests under `test/modules/{module}/`, driving use cases through in-memory fakes of their Protocols. Bootstrap pytest first if it is not installed.</task>

Toolchain status:

!`grep -n pytest pyproject.toml || echo "pytest not installed"`

Existing test packages:

!`ls test/modules`

## Scope

- **In scope:** unit tests for the domain, application, and mapper layers of one module.
- **Out of scope:** integration tests against a real database, Redis, or HTTP client. The Protocol
  boundary exists so use cases can be tested without infrastructure.
- **Done when:** the tests pass, the run output is reported verbatim, and any uncovered risk is
  named.

## Step 1 — Bootstrap, first run only

pytest is not yet a project dependency. If the status above shows it missing, confirm with the
user, then:

```bash
uv add --dev pytest pytest-asyncio
```

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["test"]
```

Check with `uv run pytest --collect-only -q`. Skip this step entirely when pytest is present.

`asyncio_mode = "auto"` is what lets `async def test_...` run without a decorator on every test.

## Step 2 — Load the target

Read `.claude/architecture.md` (Testing) and the module's `domain/entities.py`,
`application/interfaces.py`, `application/use_cases.py`, `application/exceptions.py`, and
`application/mappers.py`.

Read any existing tests in `test/modules/{module}/` and extend them rather than starting over.

## Step 3 — Discovery

- Which layers to cover: domain validation, use cases, mappers, or all three.
- The edge cases that matter — invalid input, not found, conflict, no-op update, cache miss.
- Anything the user considers a current regression risk.

## Step 4 — Generate

Write `test/modules/{module}/test_{layer}_{file}.py` — `test_domain_entities.py`,
`test_application_use_cases.py`, `test_application_mappers.py`.

Templates for the fakes and each test shape are in [TEMPLATES.md](TEMPLATES.md).

Cover, per use-case method:

- the happy path;
- each specific exception it can raise;
- the unexpected-failure path — the fake raises `RuntimeError`, the use case must raise
  `{Module}Exception`, not leak the original.

That last one is what actually validates the 3-branch error shape, and it is the case most often
left untested.

Reuse an existing directory even when its name predates the convention —
`test/modules/notifications/` is plural. Note it; do not rename it.

## Step 5 — Run

```bash
uv run pytest test/modules/{module} -q
```

Fix failures and re-run until green. Report the final output verbatim, and say plainly what is not
covered.

## Rules

- Unit-first: fakes over Protocols. No real database, Redis, network, or `TestClient`.
- One fake per Protocol, storing entities in a dict, implementing only the methods the tested use
  case calls. A fake that implements the whole Protocol is mostly dead code.
- A cache fake must behave like the real thing: return `None` on a miss and never raise. A fake
  that raises tests a path production does not have.
- Entities are plain dataclasses — construct them directly. No factory library.
- Test names read `test_{method}_{scenario}`:
  `test_create_raises_conflict_when_name_already_exists`.
- Assert on the raised exception class and its `status_code`, not on message text. Messages are
  wording; classes and status codes are contract.
- Assert on `DomainErrors.errors` as a list when checking that an entity collects every failure —
  asserting on `.message` only sees the first one.
- Mapper round-trip tests must assert the inherited fields (`id`, `is_active`, `created_at`,
  `updated_at`) survive. Dropping them is the exact bug the explicit `fields_mapping` convention
  exists to prevent.
- Plain `async def test_...` functions; `asyncio_mode = "auto"` handles the rest.
- Fresh fakes per test, through a fixture or direct construction. Shared mutable state between
  tests produces order-dependent failures.
- Never assert on log output.
