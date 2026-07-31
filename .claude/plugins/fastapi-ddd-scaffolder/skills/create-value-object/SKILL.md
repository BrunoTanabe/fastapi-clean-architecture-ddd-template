---
name: create-value-object
description: Creates a domain value object — a plain class with _normalize, _validate, __str__, and __eq__ that raises DomainError on invalid input — and places it in the owning module or in shared/ according to the reuse rule. Use when the user asks to add a value object, wrap a primitive with validation, or extract a validated concept such as an email, phone, name, slug, or currency amount out of an entity.
argument-hint: "<module> <ValueObjectName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Value Object

<task>Add a value object class to `app/modules/{module}/domain/value_objects.py`, or to `app/modules/shared/domain/value_objects.py` when more than one module constructs it.</task>

## Scope

- **In scope:** the value object class, and updating the entities that should now use it.
- **Out of scope:** schema-level validation. Pydantic `Field` constraints and the value object are
  complementary — the schema rejects malformed input at the HTTP edge, the value object guarantees
  the invariant everywhere else. Do not remove one in favour of the other.
- **Done when:** the class exists, its consumers construct it, and ruff is clean.

## Step 1 — Load the reference

Read `.claude/reference/shared-module.md` (value objects, value-object placement policy) and
`app/modules/shared/domain/value_objects.py`.

**Check first whether the concept already exists.** `Email`, `Name`, and `Phone` are already in
`shared`, and `RESOURCE_NAME_PATTERN` already covers resource-style names. Reuse beats creating.

## Step 2 — Decide where it lives

| Situation | Location |
|-----------|----------|
| One module constructs it | `{module}/domain/value_objects.py` |
| Two or more modules construct it | `shared/domain/value_objects.py` |
| It exists module-locally and a second module now needs it | Move it to `shared`, update imports |

Start module-local when in doubt. Promoting later is a mechanical move; demoting is not.

## Step 3 — Discovery

- The underlying primitive and its normalization rules (strip, lowercase, capitalize, collapse
  whitespace, strip separators).
- The validation rules, each with the exact message the API should return.
- Whether any rule is *policy* rather than *format* — policy that differs per caller becomes a
  constructor flag defaulting to the stricter behaviour.
- Whether equality is by normalized string (the default) or by something else.

## Step 4 — Generate

Templates for the single-field, multi-field, policy-flag, regex-backed, and numeric shapes are in
[TEMPLATES.md](TEMPLATES.md).

## Step 5 — Wire it into its entities

An entity field typed `VO | str` converts in `__post_init__`, catching `DomainError` into the
error list so the caller receives every problem at once:

```python
if isinstance(self.slug, str):
    try:
        self.slug = Slug(slug=self.slug)
    except DomainError as e:
        errors.append(e.message)
```

Mappers then stringify at the boundary: `"slug": str(entity.slug)` going out to a model or schema.

## Step 6 — Lint

Run `uv run ruff check` and `uv run ruff format` on the touched files. Fix and re-run until clean.

## Rules

- A plain class, never a dataclass — value objects control their own construction.
- `__init__` assigns, then calls `_normalize()`, then `_validate()`. Normalizing after validating
  means validating something the caller never sees.
- Raise `DomainError` (singular) with a complete, user-facing sentence. `DomainErrors` (plural) is
  for entities collecting multiple failures.
- Implement `__str__` — every consumer stringifies at the boundary. Implement `__eq__` comparing
  `str(self) == str(other)`.
- Value objects are conceptually immutable: construct a new one rather than mutating an existing
  one after validation.
- No `id`, no persistence concerns, no framework imports. A value object with an identity is an
  entity.
- Policy differences are constructor flags defaulting to the strict behaviour, so existing callers
  keep failing closed. Reference: `Email.enforce_allowed_domains`.
- Compile regexes once at module level as a `_UPPER_SNAKE` constant, not inside `_validate`.
- Do not implement `__hash__` unless a consumer puts the value object in a set or dict key —
  defining `__eq__` without `__hash__` already makes the class unhashable, which is the correct
  default here.
