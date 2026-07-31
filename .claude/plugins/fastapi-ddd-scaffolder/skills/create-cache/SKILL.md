---
name: create-cache
description: Adds Redis cache-aside caching to a module — the I{Entity}Cache Protocol, the Redis{Entity}Cache implementation with namespaced keys and tombstone invalidation, the entity_cache_mapper and cache_entity_mapper serializers, the DI factory, and the read-through and invalidate calls in the use case. Use when the user asks to add a cache, cache an entity, speed up a lookup, or wire Redis into a module.
argument-hint: "<module> <EntityName> [operation]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Cache

<task>Wire cache-aside caching into a module: `I{Entity}Cache` in `application/interfaces.py`, `Redis{Entity}Cache` in `infrastructure/caches.py`, the cache mappers in `application/mappers.py`, the `get_{module}_cache` factory, and the policy calls in the use case.</task>

## Scope

- **In scope:** all five pieces above. A cache class without a caller is dead code, so the use-case
  wiring is part of the job.
- **Out of scope:** changing what the repository returns. The cache stores exactly what the
  repository already produces.
- **Done when:** every cached dimension is invalidated on every mutation, ruff is clean, and the
  checklist below passes.

## Step 1 — Load the reference

Read `.claude/reference/caching.md` in full. It carries the namespace rules, key shapes, the
tombstone protocol, the never-raise policy, and the cache-aside patterns this skill implements.

## Step 2 — Load live patterns

Read `app/modules/key/infrastructure/caches.py` — the canonical implementation — together with
`app/modules/key/application/interfaces.py` (the `IKeyCache` Protocol), the `# ENTITY / CACHE`
section of `app/modules/key/application/mappers.py`, and
`app/modules/key/presentation/dependencies.py`.

Read `app/modules/authentication/infrastructure/caches.py` for the multi-dimension variant (one
entity cached under both an access-token key and a refresh-token key).

`app/modules/knowledge/infrastructure/caches.py` is a partial stub — `IKnowledgeCache` declares
only `insert` and nothing calls it. Do not copy it; completing it means following `key`.

## Step 3 — Discovery

- Which lookups are hot enough to cache. Cache reads that happen on most requests (credential
  resolution, session lookup), not reads that happen once per user action.
- The lookup dimensions — each becomes a key suffix, and **each must be invalidated on every
  mutation**.
- Whether staleness has a security consequence. If yes, the entity needs the tombstone protocol.
- Which TTL applies: `REDIS_DEFAULT_TTL_SECONDS`, or a dedicated setting like
  `REDIS_SESSION_TTL_SECONDS`.

## Step 4 — Generate

Templates for the Protocol, the implementation, the mappers, the factory, and the use-case policy
blocks are in [TEMPLATES.md](TEMPLATES.md). Generate in this order, so nothing references a
missing symbol:

1. `entity_cache_mapper` / `cache_entity_mapper` in `application/mappers.py`.
2. `I{Entity}Cache` in `application/interfaces.py`.
3. `Redis{Entity}Cache` in `infrastructure/caches.py`.
4. `get_{module}_cache` in `presentation/dependencies.py`, and `cache` on
   `get_{module}_use_cases` and the `{Module}UseCases` constructor.
5. The read-through and invalidate calls in the use case.

Use `Edit` for the files that already exist.

## Step 5 — Check, then lint

Copy this checklist and tick it off:

```
Cache wiring:
- [ ] Every cached dimension has a matching invalidation on every mutating path
- [ ] delete() writes the tombstone BEFORE removing the key
- [ ] insert() checks the tombstone BEFORE writing
- [ ] No method raises — each catches, logs, and returns None
- [ ] Keys hang off settings.REDIS_NAMESPACE, never REDIS_KEY_PREFIX directly
- [ ] entity_cache_mapper round-trips every field the consumer reads
- [ ] No secret and no ORM model is serialized
- [ ] The use case owns TTL and invalidation; the cache class owns neither
```

Then run `uv run ruff check` on every touched file and `uv run ruff format` on them. Fix and re-run
until clean.

## Rules

- Postgres is the source of truth. A full cache flush must be harmless — never serve data from
  Redis that cannot be recovered from Postgres.
- **Cache methods never raise.** Every method catches `Exception`, logs with
  `logger.opt(exception=e).error(...)` stating the consequence, and returns `None`. There is no
  `except StandardException: raise` branch — that is what separates a cache from a repository.
- Keys are built from `settings.REDIS_NAMESPACE` (which already folds in `REDIS_CACHE_VERSION`),
  through the `_key()` and `_tombstone()` helpers. Never concatenate a key inline.
- Invalidation writes the tombstone first, then deletes; `insert` skips the write when a tombstone
  is present. This closes the race where a slow reader repopulates a just-revoked entry.
- The **use case** owns policy — when to read through, when to invalidate, which TTL. The cache
  class only executes commands. A cache call inside a repository or a router is a layering
  violation.
- Invalidate with the entity whose fields produce the *stored* key. After a rotation the key
  material has changed, so the delete must use the pre-rotation entity.
- Serialization lives in `application/mappers.py`, never inside the cache class. Changing the
  payload means bumping `REDIS_CACHE_VERSION`.
- Never cache a transient secret, and never log one.
- `domain/` never imports a cache.
