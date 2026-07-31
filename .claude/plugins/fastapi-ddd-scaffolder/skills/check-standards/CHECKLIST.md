# Standards Audit Checklist

The rules `check-standards` enforces, grouped by layer. Severity in brackets: **[H]** changes
behaviour, **[M]** risks behaviour, **[L]** is style.

## Contents

- [Structure and registration](#structure-and-registration)
- [Domain — entities](#domain--entities)
- [Domain — value objects and enums](#domain--value-objects-and-enums)
- [Application — interfaces](#application--interfaces)
- [Application — use cases](#application--use-cases)
- [Application — mappers](#application--mappers)
- [Application — exceptions](#application--exceptions)
- [Infrastructure — models](#infrastructure--models)
- [Infrastructure — repositories](#infrastructure--repositories)
- [Infrastructure — caches](#infrastructure--caches)
- [Infrastructure — services](#infrastructure--services)
- [Presentation — schemas](#presentation--schemas)
- [Presentation — routers](#presentation--routers)
- [Presentation — docs](#presentation--docs)
- [Presentation — dependencies](#presentation--dependencies)
- [Cross-cutting](#cross-cutting)

## Structure and registration

- **[L]** All four layer directories exist, each with `__init__.py`, and every canonical file is
  present — empty files included.
- **[H]** A module with routes is registered in `app/app.py`: the router import, the entry in the
  `routers` list, and the tag in `custom_openapi()`.
- **[H]** Every endpoint appears in the `SECURITY_*_ALLOWED_PATHS` tier matching its
  `authenticate_*` dependency, in **both** slash forms.
- **[H]** No endpoint is registered in a *lower* tier than its dependency requires — that silently
  widens access.
- **[H]** Every ORM model is imported in `migrations/env.py` and present in the `_ = [...]` list.
- **[L]** The `routers` list, the import group, and the `_ = [...]` list are alphabetical.

## Domain — entities

- **[L]** `@dataclass(kw_only=True, slots=True)`.
- **[H]** Extends `BaseEntity`; never redeclares `id`, `is_active`, `created_at`, `updated_at`.
- **[M]** An overridden `deactivate()` calls `super().deactivate()`.
- **[L]** Every business field declares `field(default=..., repr=..., compare=...)` explicitly.
- **[H]** Fields that take part in partial updates default to `UNSET`, and every check on them is
  guarded with `is not UNSET`.
- **[M]** `__post_init__` collects errors into a `list[str]` and raises `DomainErrors(errors)`
  once, rather than raising `DomainError` on the first failure.
- **[M]** Normalization happens before validation.
- **[H]** No FastAPI, SQLAlchemy, or Pydantic import anywhere under `domain/`.
- **[M]** Actor fields are typed as `User`, not `UUID`.
- **[H]** A transient secret is excluded from `repr` and `compare` and is never persisted.
- **[M]** Paginated modules declare `{Entity}List(PaginatedList)` and
  `{Entity}Pagination(Pagination)` in the same file, redeclaring neither `total` nor `page` /
  `per_page` / `sort_order` / `offset`.

## Domain — value objects and enums

- **[L]** Value objects are plain classes, not dataclasses.
- **[M]** `__init__` assigns, then `_normalize()`, then `_validate()`.
- **[M]** They raise `DomainError` (singular) and implement `__str__` and `__eq__`.
- **[L]** Regexes are compiled once at module level.
- **[M]** A value object used by two or more modules lives in `shared/domain/value_objects.py`; a
  duplicate of `Email`, `Name`, `Phone`, or `RESOURCE_NAME_PATTERN` is a violation.
- **[L]** Enums live in `domain/enums.py` and extend `(str, Enum)`.
- **[H]** Every `{Entity}SortField` member is a real column name — the repository resolves it with
  `getattr`.
- **[M]** `Role` and `SortOrder` are imported from `shared`, never redefined.

## Application — interfaces

- **[M]** Every contract is a `typing.Protocol` with `...` bodies, grouped under `# CREATE`,
  `# READ`, `# UPDATE`, `# DELETE`.
- **[L]** Naming: `I{Entity}Repository`, `I{Entity}Cache`, `I{Name}Service`.
- **[H]** Every Protocol method has a matching implementation with an identical signature —
  `Protocol` conformance is structural and unchecked at runtime.
- **[M]** Signatures take and return domain entities, never ORM models, schemas, or dicts.

## Application — use cases

- **[L]** One `{Module}UseCases` class per module, methods grouped by CRUD comment.
- **[H]** Collaborators are Protocols injected through the constructor. No concrete repository,
  cache, or service is instantiated inside the class.
- **[H]** **The 3-branch shape in the correct order**: `except StandardException: raise` first,
  then `except DomainError`, then `except Exception`. `StandardException` is an `HTTPException`,
  so any other order turns every deliberate 404 and 409 into a 500. This is the highest-value
  check in the audit.
- **[M]** `logger.debug` at entry and exit; `logger.info` before each business-rule raise.
- **[H]** Partial updates merge against the stored record, keeping the existing value wherever the
  incoming field `is UNSET`.
- **[H]** `created_by` is restored from the stored record on update — an update must never rewrite
  authorship.
- **[H]** Every mutating path invalidates every cached dimension, using the entity whose fields
  produce the *stored* key.
- **[M]** Notifications go through `SharedUseCases`, never directly to `ConnectionManager`, and are
  dispatched after the write.
- **[H]** No FastAPI, SQLAlchemy, or Redis import, and nothing from `infrastructure/`.
- **[H]** No secret is logged.

## Application — mappers

- **[H]** `id`, `is_active`, `created_at`, `updated_at` appear in `fields_mapping` in **both**
  directions of every model↔entity mapper. This is the most common silent data-loss bug.
- **[L]** Three sections, in order: `# ENTITY / DTOS`, `# ENTITY / MODELS`, `# ENTITY / CACHE`.
- **[L]** Naming follows `{action}_entity_mapper`, `entity_{action}_mapper`, `model_entity_mapper`,
  `entity_model_mapper`, `entity_cache_mapper`, `cache_entity_mapper`.
- **[H]** Request mappers take `Authentication` and read `authentication.user` — never a `User`
  parameter, never a `Session`.
- **[H]** Update mappers set omitted fields to `UNSET` via `model_fields_set`.
- **[M]** Response mappers normalize `UNSET` to `None`.
- **[M]** A reserved renamed column is bridged in both directions.
- **[H]** No secret appears in `entity_cache_mapper` or `entity_model_mapper`.
- **[M]** Mappers contain no database access, no branching on business rules, no logging, and raise
  nothing.
- **[M]** `models_{entity}_list_mapper` guards the empty case (`rows[0][1] if rows else 0`).

## Application — exceptions

- **[M]** Exactly one generic `{Module}Exception`, HTTP 500, no constructor arguments.
- **[L]** Sections: `# GENERIC EXCEPTIONS` then `# SPECIFIC EXCEPTIONS`.
- **[M]** Every class subclasses `StandardException` and takes its message from `ResponseMessages`
  — no hardcoded message strings.
- **[M]** `data` is `{"errors": ...}`.
- **[H]** No error text leaks a stack trace, a SQL fragment, an internal path, or a secret.
- **[H]** Exceptions live in `application/exceptions.py`, never in `presentation/` or `domain/`.

## Infrastructure — models

- **[H]** Extends `BaseModel`; never redeclares the inherited four. (`AlembicModel` and the
  authentication token models extending `Base` are the documented exception.)
- **[H]** `__tablename__` uses the f-string with `settings.APPLICATION_TABLE_PREFIX` — no
  hardcoded prefix anywhere, including in `ForeignKey` targets and index names.
- **[L]** Every `mapped_column` declares the type, `name=`, `comment=`, `nullable=`.
- **[H]** Enum columns use `SQLEnum(Enum, name="{snake}_enum")` and never pass `create_type`.
- **[H]** A field named `metadata` is renamed to `{module}_metadata` with `name="metadata"`.
- **[H]** Every `relationship` declares `lazy="noload"`; two FKs to the same table each declare
  `foreign_keys=[...]`.
- **[M]** `ondelete="RESTRICT"` on actor references, `ondelete="CASCADE"` on owned children.
- **[M]** Cross-module model imports are under `if TYPE_CHECKING:` with the string target form.
- **[L]** `__table_args__` is a tuple, and constraint names follow
  `uq_/ix_/ck_{plural}_{cols}`.
- **[M]** Every foreign key that is filtered or sorted on has an index.

## Infrastructure — repositories

- **[H]** `await self.session.flush()` — a `commit()` anywhere in a repository is a violation.
- **[H]** Returns domain entities via mappers, never ORM models.
- **[H]** 2-branch try/except with `StandardException` first, and **no** `DomainError` branch.
- **[M]** `logger.info` at entry and exit of every method.
- **[M]** Reads filter `is_active.is_(True)`, unless a comment explains why not.
- **[M]** Paginated reads use `func.count(Model.id).over()` in the same statement — a separate
  `COUNT(*)` is a violation.
- **[M]** `joinedload` is present wherever the response projects a related row.
- **[M]** A not-found read returns `None`; raising the not-found exception here is a violation.
- **[H]** The repository never inspects `UNSET` — merging is the use case's job.

## Infrastructure — caches

- **[H]** **No cache method raises.** Every method catches `Exception`, logs, and returns `None`.
  A cache with an `except StandardException: raise` branch is a violation.
- **[H]** Keys are built from `settings.REDIS_NAMESPACE` through `_key()` / `_tombstone()` —
  never from `REDIS_KEY_PREFIX` directly and never concatenated inline.
- **[H]** `delete` writes the tombstone before removing the key; `insert` checks it before writing.
- **[H]** TTL defaults to `settings.REDIS_DEFAULT_TTL_SECONDS` or a dedicated setting.
- **[H]** Serialization goes through the mappers, not inline in the cache class.
- **[H]** No secret and no ORM model is serialized.
- **[M]** The log message on failure states the consequence.

## Infrastructure — services

- **[M]** Implements an `I{Name}Service` Protocol.
- **[M]** 2-branch try/except (a trivially thin delegation to a `core` helper may omit it).
- **[H]** Configuration from `settings`, never `os.environ` and never hardcoded.
- **[H]** No upstream error text is surfaced to the client.
- **[M]** Stateful singletons live on `app.state` via the lifespan, never as module globals.

## Presentation — schemas

- **[L]** Every `Field` declares `title`, `description`, `examples`, `json_schema_extra` with
  `writeOnly` or `readOnly`.
- **[L]** `model_config = ConfigDict(...)` is the last member and carries `title`,
  `str_strip_whitespace`, `extra="forbid"`, the three `validate_*` flags, and
  `json_schema_extra`.
- **[M]** Optional types are `X | None` with `default=None` — never `Optional[X]`.
- **[H]** `CreateResponse`, `UpdateResponse`, `DeleteResponse`, `PaginationMeta`, and
  `PaginationParams` are imported from `shared`, never redeclared.
- **[H]** No hashed secret, internal FK, or raw credential is exposed.
- **[M]** Enum fields list their allowed values in the description, built from the enum.
- **[H]** No schema builds the `StandardResponse` envelope.

## Presentation — routers

- **[H]** **Two decorators per route**, including parameterized ones — the second with
  `include_in_schema=False`.
- **[H]** Handlers inject `Annotated[Authentication, Depends(authenticate_*)]`. Injecting `User`,
  or referring to a `Session` type, is a violation.
- **[H]** Public endpoints inject `Annotated[None, Depends(no_authentication)]` — no route is
  unguarded.
- **[H]** The body is exactly `payload → mapper → use case → mapper → return`. Any branching,
  loop, query, or business rule in a handler is a violation.
- **[H]** The 3-branch try/except with `StandardException` first.
- **[M]** The error log names the endpoint.
- **[M]** The return annotation matches the `response_model` in the matching docs dict.
- **[L]** `router = APIRouter(**router_docs)` once at module level; handlers grouped by CRUD
  comment.
- **[M]** Path parameters are typed (`id: UUID`).

## Presentation — docs

- **[M]** `router_docs` carries `prefix`, `tags`, and the standard error responses.
- **[H]** The `tags` value matches the tag registered in `custom_openapi()`.
- **[M]** Every endpoint has a `{action}_docs` dict declaring `summary`, `description`,
  `response_description`, `status_code`, `response_model`, `include_in_schema=True`, `responses`.
- **[M]** Examples carry the full envelope: `code`, `method`, `path`, `timestamp`,
  `details{message, data}`.
- **[L]** Messages come from `ResponseMessages`.
- **[L]** `status_code` uses `HTTPStatus` constants.
- **[H]** No real credential or personal data in an example.
- **[M]** `include_in_schema=False` never appears in an endpoint docs dict.

## Presentation — dependencies

- **[M]** One factory per collaborator, plus one assembling the use case.
- **[H]** Factory return annotations are the Protocol, never the concrete class.
- **[H]** The use-case factory's parameters match the constructor exactly — a mismatch is a
  `TypeError` on the first request.
- **[M]** Stateful singletons are read from `app.state`, not constructed.

## Cross-cutting

- **[H]** No layer imports "upward": `domain/` imports nothing from the project except `shared`;
  `application/` never imports `infrastructure/` or `presentation/`; `infrastructure/` never
  imports `presentation/`.
- **[M]** Cross-module collaborators come from `shared/presentation/dependencies.py`, not from
  another module's `presentation` package.
- **[L]** Naming matches the reference table in `architecture.md`.
- **[M]** `uv run ruff check` and `uv run ruff format --check` are clean.
- **[H]** No `print()`, no commented-out code block, no `TODO` left where a rule was skipped.
