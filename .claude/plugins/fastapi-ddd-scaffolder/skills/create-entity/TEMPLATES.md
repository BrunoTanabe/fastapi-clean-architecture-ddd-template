# Entity Templates

## Contents

- [Standard entity](#standard-entity)
- [Sort-field enum](#sort-field-enum)
- [Paginated companions](#paginated-companions)
- [Entity with value objects](#entity-with-value-objects)
- [Cross-field invariants](#cross-field-invariants)
- [Transient secret fields](#transient-secret-fields)
- [Censored sensitive fields](#censored-sensitive-fields)
- [Module enums](#module-enums)

## Standard entity

The `Key` / `Knowledge` shape: normalize, then validate, collecting every error.

```python
from dataclasses import dataclass, field

from app.modules.shared.domain.entities import BaseEntity, DomainErrors
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN, UNSET
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class {Entity}(BaseEntity):
    name: str = field(default=None, repr=True, compare=True)
    description: str | None = field(default=UNSET, repr=False, compare=False)

    # Actorship (both required; equal on creation)
    created_by: User = field(default=None, repr=False, compare=False)
    updated_by: User = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.name is not UNSET and self.name is not None:
            self.name = " ".join(self.name.strip().split())
            if self.name:
                self.name = self.name[0].upper() + self.name[1:]

            if len(self.name) < 3:
                errors.append("{Entity} name must be at least 3 characters long.")
            elif len(self.name) > 255:
                errors.append("{Entity} name must not exceed 255 characters.")
            elif not RESOURCE_NAME_PATTERN.match(self.name):
                errors.append(
                    "{Entity} name must contain only letters, numbers, spaces, hyphens, and underscores."
                )

        if self.description is not UNSET and self.description is not None:
            self.description = " ".join(self.description.strip().split())
            if self.description:
                self.description = self.description[0].upper() + self.description[1:]
            else:
                self.description = None

        if errors:
            raise DomainErrors(errors)

    def deactivate(self, updated_by: User) -> None:  # noqa
        super().deactivate()
        self.updated_by = updated_by
```

The `# noqa` on `deactivate` silences the signature-mismatch warning against `BaseEntity`; keep it
when the override takes arguments.

## Sort-field enum

In `domain/enums.py`. Members must be actual column names — the repository resolves them with
`getattr(Model, pagination.sort_by.value)`, so a value that is not a column raises at query time.

```python
from enum import Enum


class {Entity}SortField(str, Enum):
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
```

## Paginated companions

Same file as the entity. `PaginatedList` supplies and validates `total`; `Pagination` supplies
`page`, `per_page`, `sort_order`, and the computed `offset`.

```python
from app.modules.shared.domain.entities import PaginatedList, Pagination


@dataclass(kw_only=True, slots=True)
class {Entity}List(PaginatedList):
    items: list[{Entity}] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class {Entity}Pagination(Pagination):
    sort_by: {Entity}SortField = field(
        default={Entity}SortField.CREATED_AT, repr=False, compare=False
    )
```

## Entity with value objects

Fields accept `VO | str`; `__post_init__` converts strings and collects `DomainError`s.
Reference: `User`.

```python
from app.modules.shared.domain.entities import BaseEntity, DomainError, DomainErrors
from app.modules.shared.domain.value_objects import Email, Name, Phone


@dataclass(kw_only=True, slots=True)
class {Entity}(BaseEntity):
    name: Name = field(default=None, repr=True, compare=False)
    email: Email | str = field(default=None, repr=True, compare=True)
    phone: Phone | str = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if isinstance(self.email, str):
            try:
                self.email = Email(email=self.email)
            except DomainError as e:
                errors.append(e.message)

        if isinstance(self.phone, str):
            try:
                self.phone = Phone(phone=self.phone)
            except DomainError as e:
                errors.append(e.message)

        if errors:
            raise DomainErrors(errors)
```

For an entity that must accept addresses outside the internal-user policy, construct the email
with the flag rather than skipping the value object:

```python
self.email = Email(email=self.email, enforce_allowed_domains=False)
```

## Cross-field invariants

**Conditional requirement** — reference: `Notification` needs a target `user` unless
`originated_from_broadcast` is set.

```python
if self.user is None and self.originated_from_broadcast is None:
    errors.append(
        "A {entity} must have a target user unless it originates from a broadcast."
    )
```

**XOR ownership** — mirrors the database `CheckConstraint("num_nonnulls(a_id, b_id) = 1")`.

```python
owners_set = sum(value is not None for value in (self.owner_a_id, self.owner_b_id))
if owners_set != 1:
    errors.append("A {entity} must belong to exactly one owner.")
```

**Derived value** — expose computed state as a `@property`, never as a stored field.

```python
@property
def is_expired(self) -> bool:
    return self.expires_at is not None and self.expires_at < datetime.now(BRASILIA_TZ)
```

## Transient secret fields

The raw secret is generated once, returned once, and never persisted. The hash is what the model
stores. Reference: `Key.plain_key` / `Key.hashed_key`, mirroring `User.password` /
`User.hashed_password`.

```python
# Secret handling: the raw value is never persisted. 'plain_{thing}' is transient and only
# carries the freshly generated secret to the response once; 'hashed_{thing}' gets stored.
hashed_{thing}: str = field(default=None, repr=False, compare=True)
plain_{thing}: str | None = field(default=None, repr=False, compare=False)
```

Never `repr` a transient secret, never include it in `entity_cache_mapper`, and never log it.
Keep a non-secret identity fragment (`prefix`, `last_four`) for display and lookup.

## Censored sensitive fields

Cache the censored form once and log only that. Reference: `User`.

```python
_censored_email: str = field(init=False, default="", repr=False, compare=False)


def _calculate_censored_values(self) -> None:
    if self.email:
        local, _, domain = str(self.email).partition("@")
        self._censored_email = f"{local[:2]}***@{domain}"


@property
def censored_email(self) -> str:
    return self._censored_email
```

`init=False` fields are assigned inside `__post_init__`, not passed by the caller.

## Module enums

`domain/enums.py`. Always `(str, Enum)`. Enums may carry behaviour — reference:
`KeyExpiration.duration`.

```python
from datetime import timedelta
from enum import Enum


class {Entity}Expiration(str, Enum):
    SEVEN_DAYS = "7_days"
    THIRTY_DAYS = "30_days"
    NEVER = "never"

    @property
    def duration(self) -> timedelta | None:
        """The validity period of this preset, or None when it never expires."""
        return {
            {Entity}Expiration.SEVEN_DAYS: timedelta(days=7),
            {Entity}Expiration.THIRTY_DAYS: timedelta(days=30),
        }.get(self)
```

Reuse `Role` and `SortOrder` from `shared/domain/enums.py`; never redefine them.
