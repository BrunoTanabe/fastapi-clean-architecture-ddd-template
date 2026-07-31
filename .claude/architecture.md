# Architectural Reference — FastAPI Clean Architecture and DDD Template

The canonical description of module structure, layer responsibilities, shared base types, and
conventions. Every scaffolding skill reads this file before generating code.

## Contents

- [Project layout](#project-layout)
- [Modules](#modules)
- [Layer responsibilities](#layer-responsibilities)
- [Error-handling shapes](#error-handling-shapes)
- [The shared module](#the-shared-module)
- [Inherited fields](#inherited-fields)
- [Domain entity pattern](#domain-entity-pattern)
- [Use case pattern](#use-case-pattern)
- [Repository pattern](#repository-pattern)
- [Mapper pattern](#mapper-pattern)
- [Schema pattern](#schema-pattern)
- [Router pattern](#router-pattern)
- [Dependencies pattern](#dependencies-pattern)
- [Docs pattern](#docs-pattern)
- [Service pattern](#service-pattern)
- [Middleware, lifespan, and WebSocket delivery](#middleware-lifespan-and-websocket-delivery)
- [Module registration](#module-registration)
- [Testing](#testing)
- [Naming reference](#naming-reference)
- [Deeper references](#deeper-references)

When a pattern here is ambiguous, read two recently modified non-`shared`, non-`example` modules
directly. Patterns repeated across modules are authoritative; a deviation in a single module is
likely a bug, not a new convention. `key` is the most complete module and the best model for
anything new.

## Project layout

```
app/
├── app.py                       # FastAPI instance, middleware, router registration, custom OpenAPI
├── core/                        # Cross-cutting infrastructure
│   ├── cache.py                 # Redis pool, get_cache_session(), init/flush/close lifecycle
│   ├── database.py              # Sync engine (Alembic) + async engine, get_async_session()
│   ├── exception_handler.py     # Global handlers (validation, HTTP, internal)
│   ├── logging.py               # loguru configuration
│   ├── middleware.py            # LogRequestMiddleware, ResponseFormattingMiddleware, DeviceIdMiddleware
│   ├── migrations.py            # Alembic auto-upgrade on startup
│   ├── resources.py             # FastAPI lifespan (db + cache + connection manager; DEV: ngrok + /devtools)
│   ├── security.py              # authenticate_* dependencies, nested JWT, password + API-key helpers
│   └── settings.py              # Pydantic settings + SECURITY_*_ALLOWED_PATHS tiers
└── modules/
    ├── shared/                  # Base types, shared value objects, SharedUseCases
    ├── authentication/          # Authentication sessions, nested JWT issuance, login/refresh/logout
    ├── example/                 # Minimal reference module (no persistence)
    ├── health/                  # Liveness, docs redirect, alembic-version (admin)
    ├── key/                     # API keys — the most complete module; canonical reference
    ├── knowledge/               # Knowledge bases (CRUD + broadcast notification reference)
    ├── notification/            # Per-user and broadcast notifications
    ├── user/                    # Internal user accounts and roles
    └── websocket/               # Real-time delivery over /connect (ConnectionManager)
```

Supporting directories: `migrations/` (Alembic; `versions/` ships empty), `test/` (mirrors
`app/modules/`), `scripts/` (module generator, key/secret generators, AsyncAPI docs, WS test
client — mounted at `/devtools` in DEV), `secrets/keys/` (JWT PEM key pairs), `docs/` (Postman
collection).

## Modules

| Module | Persistence | Cache | Service | Notes |
|--------|-------------|-------|---------|-------|
| `authentication` | yes | yes | `ITokenService` | `Authentication` → `RefreshToken` → `AccessToken` chain |
| `key` | yes | yes | `IKeyService` | Full CRUD + rotate; admin only; **canonical reference** |
| `user` | yes | — | — | Create + `/me`; roles admin/manager/user |
| `knowledge` | yes | partial | — | CRUD + broadcast notifications |
| `notification` | yes | — | — | Per-user + role-cascaded broadcast fan-out |
| `websocket` | — | — | `IConnectionManagerService` | In-memory, single-process |
| `health` | `AlembicModel` only | — | — | Liveness, docs redirect, alembic version |
| `example` | — | — | — | Minimal demo; no repository, no model |
| `shared` | base types | — | — | Not routed; imported by everything |

Documented in-progress areas — keep them, do not "fix" them:

1. **WebSocket fan-out is single-process.** `ConnectionManager` holds a
   `dict[WebSocket, WebSocketMessage]` on `app.state`. Cross-worker delivery (Redis pub/sub) is
   future work.
2. **`knowledge` caching is partial.** `IKnowledgeCache` declares only `insert`;
   `RedisKnowledgeCache` sets its prefix and key helper; `KnowledgeUseCases` receives a `cache`
   collaborator it does not call. Completing it means following `key`, not inventing a design.
3. **`SECURITY_API_KEY_ALLOWED_PATHS` is empty.** API-key authentication is fully implemented;
   no endpoint has opted in yet. Adding paths there enables it — a choice, not a fix.

## Layer responsibilities

### `domain/`
Pure Python. No FastAPI, SQLAlchemy, or Pydantic imports.

- `entities.py` — `@dataclass(kw_only=True, slots=True)` entities extending `BaseEntity`, plus
  `{Entity}List(PaginatedList)` and `{Entity}Pagination(Pagination)` for paginated modules.
- `value_objects.py` — module-local value objects. Empty when the module reuses `shared` ones.
- `enums.py` — module enums, always `(str, Enum)`. Enums may carry behaviour (see
  `KeyExpiration.duration`).

### `application/`
Orchestrates domain logic. Depends on `domain/` and `shared/` only — never on `infrastructure/`.

- `interfaces.py` — `typing.Protocol` contracts: `I{Entity}Repository`, `I{Entity}Cache`,
  `I{Name}Service`.
- `use_cases.py` — a single `{Module}UseCases` class taking its collaborators as Protocols.
- `mappers.py` — conversions in three sections: `# ENTITY / DTOS`, `# ENTITY / MODELS`,
  `# ENTITY / CACHE`.
- `exceptions.py` — one generic `{Module}Exception` (HTTP 500) plus one specific exception per
  business rule.
- `utils.py` — module-local helpers (e.g. `key/application/utils.py::resolve_expires_at`).

### `infrastructure/`
Framework-dependent implementations. Never imported by `domain/`.

- `models.py` — SQLAlchemy ORM models extending `BaseModel`.
- `repositories.py` — `Postgres{Entity}Repository` implementing `I{Entity}Repository`.
- `caches.py` — `Redis{Entity}Cache` implementing `I{Entity}Cache`.
- `services.py` — implementations behind `I{Name}Service`.

`core/cache.py` ↔ `caches.py` mirrors `core/database.py` ↔ `repositories.py`: `core/` owns the
connection, the module file owns the access logic.

### `presentation/`
FastAPI concerns only.

- `routers.py` — handlers on `router = APIRouter(**router_docs)`.
- `schemas.py` — Pydantic request/response models and `{Entity}PaginationParams`.
- `docs.py` — `router_docs` plus one `{action}_docs` dict per endpoint.
- `dependencies.py` — `Depends` factories for repositories, caches, services, and the use case.

Empty layer files are normal — a module keeps the full skeleton even when a file is unused.

## Error-handling shapes

Three shapes, chosen by layer kind. Getting this wrong is the most common review finding.

**3-branch** — use cases and router handlers:

```python
except StandardException:
    raise
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("An error occurred in the create key endpoint.")
    raise KeyException()
```

**2-branch** — repositories and services. No `DomainError` branch: these layers never evaluate
domain rules.

```python
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("An error occurred in the create key repository.")
    raise KeyException()
```

**Never-raise** — caches. Every method catches, logs, and returns `None` (or returns early). A
cache failure must degrade to the database, never fail the request.

```python
except Exception as e:
    logger.opt(exception=e).error(
        "An error occurred in the get key by hashed key cache. Falling back to the database."
    )
    return None
```

In `app/core/` the middle branch is technology-specific instead of `DomainError` — `RedisError`
in `cache.py`, `SQLAlchemyError` in `database.py` — because core code never touches domain rules.

Logging levels: `logger.debug` at use-case entry and exit, `logger.info` for notable business
decisions and every repository call, `logger.opt(exception=e).error(...)` for unexpected
failures, `logger.warning` for best-effort operations that failed harmlessly.

## The shared module

| File | Key exports |
|------|-------------|
| `shared/domain/entities.py` | `BaseEntity`, `DomainError`, `DomainErrors`, `Pagination`, `PaginatedList` |
| `shared/domain/value_objects.py` | `UNSET`, `RESOURCE_NAME_PATTERN`, `Email`, `Name`, `Phone` |
| `shared/domain/enums.py` | `ApplicationEnvironment`, `CookieSameSite`, `ResponseMessages`, `Role`, `SortOrder` |
| `shared/infrastructure/models.py` | `Base`, `BaseModel` |
| `shared/application/exceptions.py` | `StandardException`, `DomainException`, `CoreException`, `OriginNotAllowedException` |
| `shared/application/use_cases.py` | `SharedUseCases` |
| `shared/application/utils.py` | `BRASILIA_TZ`, `current_timestamp()`, `resolve_client_ip()` |
| `shared/presentation/schemas.py` | `StandardResponse`, `StandardDetailsResponse`, `PaginationParams`, `PaginationMeta`, `CreateResponse`, `UpdateResponse`, `DeleteResponse` |
| `shared/presentation/dependencies.py` | `get_authentication_repository`, `get_user_repository`, `get_notification_repository`, `get_key_repository`, `get_authentication_cache`, `get_key_cache`, `get_shared_use_cases` |

Full surface, `SharedUseCases` semantics, the `UNSET` protocol, and value-object placement
policy: [reference/shared-module.md](reference/shared-module.md).

## Inherited fields

### `BaseModel` (ORM) — never redeclare

- `id: UUID` — primary key, `server_default=func.gen_random_uuid()`.
- `is_active: bool` — soft-delete flag, default `True`.
- `created_at` / `updated_at: datetime` — Brasília timezone, `server_default=func.now()`;
  `updated_at` also carries `onupdate=func.now()` (DB-managed; never set manually).

`AlembicModel` and the authentication token models extend `Base` directly and declare their own
columns — they are lifecycle records, not soft-deletable business rows. Do not copy them.

### `BaseEntity` (domain) — never redeclare

- `id: UUID = field(default=None, repr=True, compare=True)`
- `is_active: bool = field(init=False, default=True, repr=False, compare=False)`
- `created_at` / `updated_at: datetime = field(default=None, repr=False, compare=False)`
- `deactivate() -> None` — sets `is_active = False`. Override only for extra domain logic, and
  call `super().deactivate()` (see `Key.deactivate(updated_by)`).

## Domain entity pattern

Entities validate in `__post_init__`, collecting every error and raising `DomainErrors` once.
Use `UNSET` as the default for fields that must distinguish "not provided" from "set to null".
Normalize before validating.

```python
from dataclasses import dataclass, field

from app.modules.shared.domain.entities import BaseEntity, DomainErrors
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN, UNSET
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class MyEntity(BaseEntity):
    name: str = field(default=None, repr=True, compare=True)
    description: str | None = field(default=UNSET, repr=False, compare=False)
    created_by: User = field(default=None, repr=False, compare=False)
    updated_by: User = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.name is not UNSET and self.name is not None:
            self.name = " ".join(self.name.strip().split())
            if self.name:
                self.name = self.name[0].upper() + self.name[1:]

            if len(self.name) < 3:
                errors.append("Name must be at least 3 characters long.")
            elif len(self.name) > 255:
                errors.append("Name must not exceed 255 characters.")
            elif not RESOURCE_NAME_PATTERN.match(self.name):
                errors.append(
                    "Name must contain only letters, numbers, spaces, hyphens, and underscores."
                )

        if errors:
            raise DomainErrors(errors)

    def deactivate(self, updated_by: User) -> None:  # noqa
        super().deactivate()
        self.updated_by = updated_by
```

Paginated companions live in the same file:

```python
@dataclass(kw_only=True, slots=True)
class MyEntityList(PaginatedList):
    items: list[MyEntity] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class MyEntityPagination(Pagination):
    sort_by: MyEntitySortField = field(
        default=MyEntitySortField.CREATED_AT, repr=False, compare=False
    )
```

`PaginatedList` already supplies and validates `total`; the subclass adds only `items`.

Cross-field rules belong in the same `__post_init__` block. Live reference: `Notification`
requires a target `user` unless `originated_from_broadcast` is set.

## Use case pattern

`{Module}UseCases` is one class. Collaborators are Protocols, injected via the constructor.

```python
class MyModuleUseCases:
    def __init__(
        self,
        cache: IMyEntityCache,
        repository: IMyEntityRepository,
        service: IMyEntityService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.service = service

    async def create(self, entity: MyEntity) -> MyEntity:
        try:
            logger.debug(
                f"Initializing create my_module use case for '{entity.name}'. "
                f"Requested by user {entity.created_by.id}."
            )

            if await self.repository.exists_by_name(entity):
                raise MyEntityNameAlreadyExistsException(name=entity.name)

            entity = await self.repository.create(entity)

            logger.debug(
                f"Create my_module use case completed successfully for {entity.id}."
            )
            return entity
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create my_module use case."
            )
            raise MyModuleException()
```

Add `shared_service: SharedUseCases` when the module notifies or looks up users, and call
`self.shared_service.disable_exceptions()` in `__init__` for `None`-on-miss lookups (see
`KnowledgeUseCases`).

Partial updates merge against the stored record, keeping the existing value wherever the incoming
field `is UNSET`:

```python
merged = MyEntity(
    id=entity.id,
    name=entity.name if entity.name is not UNSET else existing.name,
    description=entity.description
    if entity.description is not UNSET
    else existing.description,
    created_by=existing.created_by,
    updated_by=entity.updated_by,
)
```

The use case — not the cache class — owns cache policy: read-through on gets, invalidate on
mutations, TTL selection. See [reference/caching.md](reference/caching.md).

## Repository pattern

Use `await self.session.flush()` — never `commit()`. Return entities via mappers, never ORM
models. 2-branch try/except. `logger.info` on entry and exit of every method.

```python
class PostgresMyEntityRepository(IMyEntityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: MyEntity) -> MyEntity:
        try:
            logger.info(f"Creating '{entity.name}' in database.")

            db_model = entity_model_mapper(entity)
            self.session.add(db_model)
            await self.session.flush()

            logger.info(f"'{entity.name}' created successfully in database.")
            return model_entity_mapper(db_model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the create repository.")
            raise MyModuleException()
```

Paginated reads compute the total in the same statement with a window function, then order,
offset, and limit. Filter `is_active.is_(True)` unless the caller must distinguish "revoked" from
"absent" — see `PostgresKeyRepository.get_key_by_hashed_key`, which deliberately omits the filter
so the auth path can tell a revoked key from an invalid one.

```python
col = getattr(MyEntityModel, pagination.sort_by.value)
ordering = col.asc() if pagination.sort_order == SortOrder.ASC else col.desc()

statement = (
    select(MyEntityModel, func.count(MyEntityModel.id).over().label("total"))
    .where(MyEntityModel.is_active.is_(True))
    .order_by(ordering)
    .offset(pagination.offset)
    .limit(pagination.per_page)
)
rows = (await self.session.execute(statement)).all()
return models_my_entity_list_mapper(rows)
```

Use `joinedload(...)` when the response projects related actors, and pair it with
`model_entity_with_actors_mapper`.

## Mapper pattern

Use `automapper` for straightforward field copies and explicit construction for transformations
(value objects, joins, FK extraction, JSON). **Inherited fields must always be listed in
`fields_mapping`** — automapper does not traverse parent dataclass `slots`, so omitting them
silently drops values.

Three sections, in this order:

```python
# ENTITY / DTOS
def create_entity_mapper(
    payload: CreateRequest, authentication: Authentication
) -> MyEntity: ...
def entity_create_mapper(entity: MyEntity) -> CreateResponse: ...
def update_entity_mapper(
    id: UUID, payload: UpdateRequest, authentication: Authentication
) -> MyEntity: ...
def get_all_entity_mapper(
    authentication, query_params
) -> tuple[MyEntity, MyEntityPagination]: ...
def entities_get_all_mapper(
    entity_list: MyEntityList, pagination
) -> GetAllResponse: ...


# ENTITY / MODELS
def model_entity_mapper(model: MyEntityModel) -> MyEntity: ...
def model_entity_with_actors_mapper(model: MyEntityModel) -> MyEntity: ...
def models_my_entity_list_mapper(rows: list) -> MyEntityList: ...
def entity_model_mapper(entity: MyEntity) -> MyEntityModel: ...


# ENTITY / CACHE
def entity_cache_mapper(entity: MyEntity) -> str: ...
def cache_entity_mapper(raw: str) -> MyEntity: ...
```

Request mappers take `Authentication` and read the actor as `authentication.user`. Update mappers
set omitted fields to `UNSET` via `payload.model_fields_set`. Model→entity mappers rebuild minimal
related entities from FK columns (`User(id=model.created_by)`); the `_with_actors` variant builds
full ones from a joined row. Responses that show an actor use a small `ActorResponse` projection
rather than exposing the raw FK.

## Schema pattern

Pydantic v2 `BaseModel` subclasses. Every `Field` declares `title`, `description`, `examples`, and
`json_schema_extra` (`writeOnly` for requests, `readOnly` for responses). `model_config =
ConfigDict(...)` is the last member, carrying `title`, `str_strip_whitespace`, `extra="forbid"`,
`validate_default`, `validate_assignment`, `validate_return`, and `json_schema_extra`. Validators
are `@classmethod` under `@field_validator` / `@model_validator`. Import `CreateResponse`,
`UpdateResponse`, `DeleteResponse`, `PaginationMeta`, and `PaginationParams` from `shared` —
never redeclare them.

Module pagination is a callable class injected with `Depends()`:

```python
class MyEntityPaginationParams:
    def __init__(
        self,
        pagination: Annotated[PaginationParams, Depends()],
        sort_by: MyEntitySortField = Query(default=MyEntitySortField.CREATED_AT),
    ):
        self.sort_order = pagination.sort_order
        self.page = pagination.page
        self.limit = pagination.limit
        self.offset = pagination.offset
        self.sort_by = sort_by
```

## Router pattern

Every endpoint declares two decorators — one with the trailing `/` (visible in OpenAPI) and one
without (`include_in_schema=False`). This applies to parameterized routes too, mirroring how the
allowlists register both slash forms.

The handler body is strictly `payload → mapper → use case → mapper → return`. Business logic lives
in the use case. Handlers inject `Authentication`, never `User`.

```python
router = APIRouter(**router_docs)


@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[MyModuleUseCases, Depends(get_my_module_use_cases)],
) -> CreateResponse:
    try:
        request_domain = create_entity_mapper(payload, authentication)
        response_domain = await use_case.create(request_domain)
        output = entity_create_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the create my_module endpoint."
        )
        raise MyModuleException()
```

Handlers return plain response schemas — `ResponseFormattingMiddleware` wraps them in the
`StandardResponse` envelope. Never build the envelope by hand.

## Dependencies pattern

One factory per collaborator, then one that assembles the use case.

```python
def get_my_module_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> IMyEntityCache:
    return RedisMyEntityCache(cache=cache)


def get_my_module_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IMyEntityRepository:
    return PostgresMyEntityRepository(session=session)


def get_my_module_service() -> IMyEntityService:
    return MyEntityService()


def get_my_module_use_cases(
    cache: Annotated[IMyEntityCache, Depends(get_my_module_cache)],
    repository: Annotated[IMyEntityRepository, Depends(get_my_module_repository)],
    service: Annotated[IMyEntityService, Depends(get_my_module_service)],
) -> MyModuleUseCases:
    return MyModuleUseCases(cache=cache, repository=repository, service=service)
```

Omit collaborators the module does not use. Stateful singletons are created in the lifespan,
stored on `app.state`, and retrieved from `HTTPConnection.app.state` in the factory (see
`get_connection_manager`).

## Docs pattern

`docs.py` exports `router_docs` — carrying `prefix`, `tags`, and the standard error responses
(400, 401, 403, 405, 422, 500, 502, 504, plus 409 where a conflict is possible) — and one
`{action}_docs` dict per endpoint with `summary`, `description`, `response_description`,
`status_code`, `response_model`, `include_in_schema`, and a `responses` example. Copy the verbatim
shape from `key/presentation/docs.py`.

## Service pattern

Use a service when a module wraps an external system or a stateful in-process component. Live
references: `KeyService` / `IKeyService` (stateless, wraps `core.security.generate_api_key`),
`ConnectionManager` / `IConnectionManagerService` (stateful singleton), and `ITokenService`
(authentication).

- Declare `I{Name}Service` as a `typing.Protocol` in `application/interfaces.py`.
- Implement it in `infrastructure/services.py` with the 2-branch shape.
- Wire it through a `get_{name}_service` factory. Stateless services are constructed per request;
  stateful singletons come from `app.state`.
- `domain/` never imports a service; use cases depend on the Protocol only.

## Middleware, lifespan, and WebSocket delivery

`app/app.py` registers (outermost first) `CORSMiddleware`, `ResponseFormattingMiddleware`,
`LogRequestMiddleware` (request id + timing headers, structured loguru), and `DeviceIdMiddleware`
(issues a device-id cookie when absent). `ResponseFormattingMiddleware` wraps every JSON response
in the `StandardResponse` envelope — `code`, `method`, `path`, `timestamp`, and
`details{message, data}`.

The lifespan in `core/resources.py` initializes loguru, the database, and the cache client
(startup `PING`, optional namespace flush when `REDIS_FLUSH_ON_STARTUP`), runs Alembic
auto-upgrade to head, and stores a single `ConnectionManager` on `app.state.connection_manager`.
In DEV it also starts an ngrok tunnel and mounts `scripts/` at `/devtools`. In production,
`openapi_url` / `docs_url` / `redoc_url` are disabled.

The `websocket` module delivers messages over `/api/v1/websocket/connect`. A decoy
`@router.get("/connect/")` exists only to document the channel in OpenAPI. `broadcast_to` applies
the role cascade (`USER` → everyone, `MANAGER` → managers + admins, `ADMIN` → admins only) and
disconnects sockets whose send fails. Notification delivery always flows through `SharedUseCases`
— persist first, then dispatch best-effort.

## Module registration

**`app/app.py`:**
1. `from app.modules.{module}.presentation.routers import router as {module}_router`
2. Append `{module}_router` to the `routers` list (alphabetical).
3. Append `{"name": "{Module}", "description": "..."}` to the `tags` list in `custom_openapi()`.

**`app/core/settings.py`:** register every endpoint in the matching allowlist tier with both slash
forms. Tiers cascade — each spreads the previous one.

```python
(_path_rule("/api/v1/{module}/", "POST"),)
(_path_rule("/api/v1/{module}", "POST"),)
```

An endpoint missing from its tier returns 403 even with a valid token. Details:
[reference/security.md](reference/security.md).

## Testing

Tests live in `test/modules/{module}/`, mirroring `app/modules/`. `test/modules/notifications/`
is a plural-naming outlier that predates the convention — reuse it as is. pytest is not yet a
project dependency; the `create-test` skill bootstraps it on first use. The policy is unit-first:
drive use cases through in-memory fakes of the repository / cache / service Protocols, construct
entities directly as dataclasses, and avoid real database, Redis, or network access.

## Naming reference

| Component | Pattern | Example |
|-----------|---------|---------|
| Module directory | snake_case | `knowledge` |
| Domain entity | PascalCase | `Key` |
| Paginated companions | `{Entity}List` / `{Entity}Pagination` | `KeyList`, `KeyPagination` |
| Sort field enum | `{Entity}SortField` | `KeySortField` |
| ORM model | PascalCase + Model | `KeyModel` |
| Repository interface / impl | `I…Repository` / `Postgres…Repository` | `IKeyRepository`, `PostgresKeyRepository` |
| Cache interface / impl | `I…Cache` / `Redis…Cache` | `IKeyCache`, `RedisKeyCache` |
| Service interface / impl | `I…Service` / descriptive | `IKeyService`, `KeyService` |
| Use case class | PascalCase + UseCases | `KeyUseCases` |
| Generic exception | PascalCase + Exception | `KeyException` |
| Specific exception | describes the failure | `KeyNotFoundException` |
| Request / response schema | PascalCase + Request/Response | `CreateRequest`, `GetAllResponse` |
| Pagination params | `{Entity}PaginationParams` | `KeyPaginationParams` |
| Mapper functions | `{action}_entity_mapper`, `entity_{action}_mapper`, `model_entity_mapper`, `entity_model_mapper`, `entity_cache_mapper`, `cache_entity_mapper` | |
| Router prefix | `/api/v1/{kebab}` | `/api/v1/key` |
| Table name | `{APPLICATION_TABLE_PREFIX}_{plural_snake}` | `..._keys` |
| Enum type name | `{snake}_enum` | `role_enum` |
| Constraint / index | `uq_/ix_/ck_{plural}_{cols}` | `uq_keys_hashed_key` |
| Test file | `test_{layer}_{file}.py` | `test_application_use_cases.py` |

## Deeper references

Read the file that matches the work; each is self-contained and one level from here.

- [reference/shared-module.md](reference/shared-module.md) — `shared` exports, `SharedUseCases`, `UNSET`, `PaginatedList`, value-object placement.
- [reference/persistence.md](reference/persistence.md) — ORM columns, enums, the reserved `metadata` rename, constraints, cascades, Alembic.
- [reference/caching.md](reference/caching.md) — namespace and versioning, key shapes, tombstones, the never-raise policy, cache mappers.
- [reference/security.md](reference/security.md) — nested JWT, the `authenticate_*` dependencies, API keys, allowlist tiers.
