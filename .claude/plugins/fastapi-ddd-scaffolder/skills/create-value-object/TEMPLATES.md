# Value Object Templates

## Contents

- [Single-field value object](#single-field-value-object)
- [Regex-backed value object](#regex-backed-value-object)
- [Multi-field value object](#multi-field-value-object)
- [Policy flag](#policy-flag)
- [Numeric value object](#numeric-value-object)
- [Using it from an entity](#using-it-from-an-entity)

## Single-field value object

The base shape. Reference: `Phone`.

```python
from app.modules.shared.domain.entities import DomainError


class {ValueObject}:
    value: str

    def __init__(self, value: str) -> None:
        self.value = value
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.value = self.value.strip().lower()

    def _validate(self) -> None:
        if not self.value:
            raise DomainError("{ValueObject} is required.")

        if len(self.value) > 255:
            raise DomainError("{ValueObject} must not exceed 255 characters.")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
```

Name the attribute after the concept (`self.email`, `self.phone`, `self.slug`), not `self.value`,
when that reads better — both `Email` and `Phone` do this.

## Regex-backed value object

Compile the pattern once at class level, never inside `_validate`.

```python
import re

from app.modules.shared.domain.entities import DomainError


class Slug:
    slug: str

    _SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def __init__(self, slug: str) -> None:
        self.slug = slug
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.slug = re.sub(r"[\s_]+", "-", self.slug.strip().lower())

    def _validate(self) -> None:
        if not self.slug:
            raise DomainError("Slug is required.")

        if len(self.slug) > 100:
            raise DomainError("Slug must not exceed 100 characters.")

        if not self._SLUG_REGEX.match(self.slug):
            raise DomainError(
                f"Invalid slug format: '{self.slug}'. Use lowercase letters, numbers, and single hyphens."
            )

    def __str__(self) -> str:
        return self.slug

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
```

Include the offending value in format errors — `Email` and `Slug` both do — so the client can see
what was rejected. Never do this for a secret.

## Multi-field value object

Several primitives that are only meaningful together. Reference: `Name`.

```python
import re

from app.modules.shared.domain.entities import DomainError


class {ValueObject}:
    first_part: str
    second_part: str

    def __init__(self, first_part: str, second_part: str) -> None:
        self.first_part = first_part
        self.second_part = second_part
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.first_part = self.first_part.strip().capitalize()
        self.second_part = self.second_part.strip().capitalize()

    def _validate(self) -> None:
        if not self.first_part or not self.second_part:
            raise DomainError("Both parts are required.")

        if len(self.first_part.strip()) < 3:
            raise DomainError("First part must be at least 3 characters long.")

    def __str__(self) -> str:
        return f"{self.first_part} {self.second_part}"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
```

Expose the individual parts as attributes when a mapper needs them separately — `key`'s
`_actor_response` reads `user.name.preferred_name` directly.

## Policy flag

When one caller needs a looser rule, add a flag that defaults to the stricter behaviour so
existing callers keep failing closed. Reference: `Email.enforce_allowed_domains`.

```python
class Email:
    def __init__(self, email: str, enforce_allowed_domains: bool = True) -> None:
        self.email = email
        self.enforce_allowed_domains = enforce_allowed_domains
        self._normalize()
        self._validate()

    def _validate(self) -> None:
        # Format rules always run.
        ...

        # Policy rule is opt-out.
        if (
            self.enforce_allowed_domains
            and settings.SECURITY_EMAIL_ALLOWED_DOMAINS
            and domain not in settings.SECURITY_EMAIL_ALLOWED_DOMAINS
        ):
            raise DomainError(f"Email domain '{domain}' is not allowed.")
```

Reading `settings` inside a value object is acceptable only for policy of this kind — it is the
one place `domain/` touches configuration, and `shared/domain/value_objects.py` already does it.
Never read `settings` for a format rule.

## Numeric value object

```python
from decimal import Decimal, InvalidOperation

from app.modules.shared.domain.entities import DomainError


class Amount:
    amount: Decimal

    def __init__(self, amount: Decimal | str | int) -> None:
        self.amount = amount
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        try:
            self.amount = Decimal(str(self.amount)).quantize(Decimal("0.01"))
        except InvalidOperation, ValueError, TypeError:
            raise DomainError(f"Invalid amount: '{self.amount}'.")

    def _validate(self) -> None:
        if self.amount < 0:
            raise DomainError("Amount must be zero or greater.")

    def __str__(self) -> str:
        return f"{self.amount:.2f}"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
```

Use `Decimal` for money, never `float`. `_normalize` may raise when the input cannot be coerced at
all — that is normalization failure, not validation failure, and `DomainError` covers both.

## Using it from an entity

```python
@dataclass(kw_only=True, slots=True)
class {Entity}(BaseEntity):
    slug: Slug | str = field(default=None, repr=True, compare=True)

    def __post_init__(self):
        errors: list[str] = []

        if isinstance(self.slug, str):
            try:
                self.slug = Slug(slug=self.slug)
            except DomainError as e:
                errors.append(e.message)

        if errors:
            raise DomainErrors(errors)
```

At the mappers:

```python
"slug": str(entity.slug)                       # entity → model / response
"slug": model.slug                             # model → entity (the entity re-validates)
"slug": str(entity.slug) if entity.slug else None   # entity → cache JSON
```

The entity annotation stays `Slug | str` because every inbound boundary hands over a plain string
and `__post_init__` is what converts it.
