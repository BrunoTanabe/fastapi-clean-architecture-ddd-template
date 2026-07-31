# Reference — The `shared` Module

Everything `app/modules/shared/` exposes, and the rules for using it.

## Contents

- [Export surface](#export-surface)
- [Base entities](#base-entities)
- [Pagination types](#pagination-types)
- [Value objects](#value-objects)
- [Value-object placement policy](#value-object-placement-policy)
- [The UNSET sentinel](#the-unset-sentinel)
- [Enums](#enums)
- [Exceptions](#exceptions)
- [SharedUseCases](#sharedusecases)
- [Presentation schemas](#presentation-schemas)
- [Shared dependencies](#shared-dependencies)
- [Utils](#utils)

## Export surface

| File | Exports |
|------|---------|
| `domain/entities.py` | `DomainError`, `DomainErrors`, `BaseEntity`, `Pagination`, `PaginatedList` |
| `domain/value_objects.py` | `RESOURCE_NAME_PATTERN`, `UNSET`, `Email`, `Name`, `Phone` |
| `domain/enums.py` | `ApplicationEnvironment`, `CookieSameSite`, `ResponseMessages`, `Role`, `SortOrder` |
| `application/exceptions.py` | `StandardException`, `DomainException`, `CoreException`, `OriginNotAllowedException` |
| `application/use_cases.py` | `SharedUseCases` |
| `application/utils.py` | `BRASILIA_TZ`, `current_timestamp()`, `resolve_client_ip()` |
| `infrastructure/models.py` | `Base`, `BaseModel` |
| `presentation/schemas.py` | `StandardResponse`, `StandardDetailsResponse`, `PaginationParams`, `PaginationMeta`, `CreateResponse`, `UpdateResponse`, `DeleteResponse` |
| `presentation/dependencies.py` | `get_authentication_repository`, `get_user_repository`, `get_notification_repository`, `get_key_repository`, `get_authentication_cache`, `get_key_cache`, `get_shared_use_cases` |

`shared/application/interfaces.py`, `shared/application/mappers.py`,
`shared/infrastructure/{caches,repositories,services}.py`, and
`shared/presentation/{docs,routers}.py` are intentionally empty — `shared` is not a routed module.

## Base entities

```python
class DomainError(Exception):
    def __init__(self, message: str) -> None: ...

    # .message


class DomainErrors(DomainError):
    def __init__(self, errors: list[str]) -> None: ...

    # .errors — the full list; .message is errors[0]


@dataclass(kw_only=True, slots=True)
class BaseEntity:
    id: UUID = field(default=None, repr=True, compare=True)
    is_active: bool = field(init=False, default=True, repr=False, compare=False)
    created_at: datetime = field(default=None, repr=False, compare=False)
    updated_at: datetime = field(default=None, repr=False, compare=False)

    def deactivate(self) -> None:
        self.is_active = False
```

Raise `DomainError` for a single failure (value objects) and `DomainErrors` for a collected list
(entities). `DomainException` in the application layer unwraps either into an HTTP 400 payload.

Override `deactivate()` only to add domain logic, and always call `super().deactivate()`:

```python
def deactivate(self, updated_by: User) -> None:  # noqa
    super().deactivate()
    self.updated_by = updated_by
```

## Pagination types

```python
@dataclass(kw_only=True, slots=True)
class Pagination:
    page: int = field(default=1, repr=True, compare=True)
    per_page: int = field(default=20, repr=True, compare=True)
    sort_order: SortOrder = field(default=SortOrder.DESC, repr=False, compare=False)
    offset: int = field(init=False, repr=False, compare=False)
    # __post_init__ validates page >= 1 and 1 <= per_page <= 100, then computes offset


@dataclass(kw_only=True, slots=True)
class PaginatedList:
    total: int = field(default=0, repr=True, compare=False)
    # __post_init__ rejects a negative total
```

A paginated module subclasses both in `domain/entities.py`:

```python
@dataclass(kw_only=True, slots=True)
class KeyList(PaginatedList):
    items: list[Key] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class KeyPagination(Pagination):
    sort_by: KeySortField = field(
        default=KeySortField.CREATED_AT, repr=False, compare=False
    )
```

Never redeclare `total`, `page`, `per_page`, `sort_order`, or `offset`.

The presentation counterpart is `PaginationMeta`, assembled by the response mapper:

```python
total_pages = math.ceil(total / pagination.per_page) if pagination.per_page else 0

PaginationMeta(
    total=total,
    page=pagination.page,
    limit=pagination.per_page,
    total_pages=total_pages,
    has_next=pagination.page < total_pages,
    has_prev=pagination.page > 1,
)
```

Note the vocabulary shift at the boundary: the domain says `per_page`, the HTTP surface says
`limit`.

## Value objects

`shared/domain/value_objects.py` owns the reusable ones.

**`Email(email: str, enforce_allowed_domains: bool = True)`** — lowercases and strips, enforces a
254-character cap, a strict regex, no leading/trailing dot in the local part, no consecutive dots,
and membership in `settings.SECURITY_EMAIL_ALLOWED_DOMAINS` when that list is non-empty. Pass
`enforce_allowed_domains=False` for emails outside the internal-user policy (external contacts,
imported data).

**`Name(first_name: str, last_name: str, preferred_name: str = None)`** — capitalizes and strips;
`preferred_name` defaults to `first_name`. Requires 3–100 characters and letters, spaces,
apostrophes, or hyphens only. `str(name)` renders `"First Last (Preferred)"`.

**`Phone(phone: str)`** — strips separators, forces a leading `+`, requires 7–15 digits.

**`RESOURCE_NAME_PATTERN`** — the shared regex for resource-style names (letters including
accented, digits, spaces, hyphens, underscores). Used by `Key` and `Knowledge`.

Entities convert `str → VO` inside `__post_init__`, catching `DomainError` into the error list:

```python
if isinstance(self.email, str):
    try:
        self.email = Email(email=self.email)
    except DomainError as e:
        errors.append(e.message)
```

## Value-object placement policy

A value object lives in the module that owns the concept and moves to
`shared/domain/value_objects.py` when a second module starts constructing it. `Email`, `Name`, and
`Phone` are in `shared` because `user`, `key`, and `authentication` all build them.
`example/domain/value_objects.py::FullName` is module-local because only `example` uses it.

When promoting a VO whose policy differs between consumers, express the difference as a
constructor flag that defaults to the stricter behaviour — `Email.enforce_allowed_domains` is the
reference implementation of that pattern.

## The UNSET sentinel

`UNSET` is a singleton distinguishing "field omitted" from "field explicitly set to null".

```python
class _Unset:
    _instance = None

    def __new__(cls): ...
    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()
```

Always compare with `is` / `is not`, never `==`.

**The three-step protocol:**

1. The entity defaults optional-on-update fields to `UNSET`:
   `description: str | None = field(default=UNSET, ...)`
2. The update mapper sets each field from `model_fields_set`:
   ```python
   description = (
       payload.description if "description" in payload.model_fields_set else UNSET
   )
   ```
3. The use case merges against the stored record:
   ```python
   description = (
       entity.description if entity.description is not UNSET else existing.description
   )
   ```

Guard validation with `is not UNSET` so an omitted field is never validated, and normalize `UNSET`
back to `None` in response mappers:
`"description": key.description if key.description is not UNSET else None`.

## Enums

| Enum | Members |
|------|---------|
| `ApplicationEnvironment` | `DEV="development"`, `HOMOLOG="homolog"`, `PRODUCTION="production"` |
| `CookieSameSite` | `LAX`, `STRICT`, `NONE` |
| `Role` | `ADMIN="admin"`, `MANAGER="manager"`, `USER="user"` |
| `SortOrder` | `ASC="asc"`, `DESC="desc"` |
| `ResponseMessages` | success, client-error, and server-error message constants |

`ResponseMessages` is a plain `Enum` (not `(str, Enum)`) — always read `.value`. Every module
exception and every `docs.py` example pulls its message from it; never hardcode a message string.

## Exceptions

```python
class StandardException(HTTPException):
    def __init__(
        self, status_code: int, message: str, data: dict | None = None
    ) -> None: ...

    # .message, .data
```

- `DomainException(domain_error)` — HTTP 400, unwraps `DomainError` / `DomainErrors` into
  `data={"errors": [...]}`.
- `CoreException()` — HTTP 500, for `app/core/` failures.
- `OriginNotAllowedException()` — HTTP 403, raised by `authenticate_websocket`.

Module exceptions subclass `StandardException` directly. Because `StandardException` is an
`HTTPException`, the `except StandardException: raise` branch must always come first — it
re-raises deliberate failures untouched.

## SharedUseCases

Constructed with `user_repository`, `notification_repository`, and `connection_manager`. Inject it
with `get_shared_use_cases`.

| Method | Behaviour |
|--------|-----------|
| `create_notification(notification) -> Notification` | Persists a per-user notification, then dispatches it over WebSocket best-effort (a WS failure logs a warning and never breaks the write) |
| `create_broadcast_notification(notification) -> list[Notification]` | Fans out to the role in `notification.originated_from_broadcast`; returns one persisted `Notification` per matched user |
| `get_user_by_id(user) -> User \| None` | User lookup by id |
| `get_user_by_email(user) -> User \| None` | User lookup by email |
| `enable_exceptions()` / `disable_exceptions()` | Toggles whether the lookups raise or return `None` on miss |
| `raise_exceptions` | Read-only property reflecting the current mode |

Default is raise-on-miss. A use case that wants `None` calls `disable_exceptions()` in its own
`__init__`:

```python
def __init__(self, cache, repository, shared_service: SharedUseCases) -> None:
    self.cache = cache
    self.repository = repository
    self.shared_service = shared_service
    self.shared_service.disable_exceptions()
```

Broadcast example:

```python
await self.shared_service.create_broadcast_notification(
    Notification(
        originated_from_broadcast=Role.MANAGER,
        notification_type=NotificationType.KNOWLEDGE_CREATED,
        title="Knowledge base created",
        body=f"Knowledge base '{entity.name}' was created by {creator.name}.",
    )
)
```

The role cascade on fan-out: `ADMIN` → admins, `MANAGER` → managers + admins, `USER` → everyone.
Module use cases never call `ConnectionManager` directly — always go through `SharedUseCases`.

## Presentation schemas

- **`StandardResponse[T]`** / **`StandardDetailsResponse[T]`** — the response envelope
  (`code`, `method`, `path`, `timestamp`, `details{message, data}`). Built by
  `ResponseFormattingMiddleware`; handlers never construct it, but `docs.py` references it as the
  `model` for error responses.
- **`PaginationParams`** — callable class with `sort_order`, `page`, `limit`, `offset`. Compose it
  into `{Entity}PaginationParams` with `Annotated[PaginationParams, Depends()]`.
- **`PaginationMeta`** — the pagination block of a list response.
- **`CreateResponse` / `UpdateResponse` / `DeleteResponse`** — single-field message responses.
  Import them; never redeclare.

## Shared dependencies

`shared/presentation/dependencies.py` exists so cross-module collaborators can be injected without
importing another module's `presentation` package (which would create a cycle). Use these when a
module needs another module's repository or cache; keep module-owned factories in the module's own
`dependencies.py`.

## Utils

```python
BRASILIA_TZ = ZoneInfo(
    "America/Sao_Paulo"
)  # the project timezone; BaseModel timestamps use it


def current_timestamp() -> str: ...  # UTC ISO 8601 with a trailing "Z"
def resolve_client_ip(x_forwarded_for, x_real_ip, peer_host) -> str: ...
```

`resolve_client_ip` prefers the first hop of `X-Forwarded-For`, then `X-Real-IP`, then the peer
host, and returns `"unknown"` when all are absent.
