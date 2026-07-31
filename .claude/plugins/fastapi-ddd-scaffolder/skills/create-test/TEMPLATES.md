# Test Templates

## Contents

- [Fake repository](#fake-repository)
- [Fake cache](#fake-cache)
- [Fake service](#fake-service)
- [Fixtures](#fixtures)
- [Entity validation tests](#entity-validation-tests)
- [Value object tests](#value-object-tests)
- [Use case tests](#use-case-tests)
- [The unexpected-failure path](#the-unexpected-failure-path)
- [Partial-update tests](#partial-update-tests)
- [Mapper round-trip tests](#mapper-round-trip-tests)

## Fake repository

One per Protocol, storing entities in a dict. Implement only the methods the tested use case
calls.

```python
from uuid import UUID, uuid4

from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination


class Fake{Entity}Repository:
    def __init__(self) -> None:
        self.items: dict[UUID, {Entity}] = {}
        self.fail = False   # flip to simulate an infrastructure failure

    def _guard(self) -> None:
        if self.fail:
            raise RuntimeError("simulated infrastructure failure")

    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        self._guard()
        entity.id = entity.id or uuid4()
        self.items[entity.id] = entity
        return entity

    # READ
    async def get_by_id(self, entity: {Entity}) -> {Entity} | None:
        self._guard()
        return self.items.get(entity.id)

    async def get_all(
        self, entity: {Entity}, pagination: {Entity}Pagination
    ) -> {Entity}List:
        self._guard()
        values = list(self.items.values())
        start = pagination.offset
        end = start + pagination.per_page
        return {Entity}List(items=values[start:end], total=len(values))

    async def exists_by_name(self, entity: {Entity}) -> bool:
        self._guard()
        return any(item.name == entity.name for item in self.items.values())

    # UPDATE
    async def update(self, entity: {Entity}) -> {Entity}:
        self._guard()
        self.items[entity.id] = entity
        return entity
```

The `fail` flag is what makes the unexpected-failure path testable without mocking.

## Fake cache

Mirror the real contract: return `None` on a miss, **never raise**. A cache fake that raises tests
a path production does not have, because real caches swallow their errors.

```python
class Fake{Entity}Cache:
    def __init__(self) -> None:
        self.items: dict[UUID, {Entity}] = {}
        self.deleted: list[UUID] = []

    async def insert(self, entity: {Entity}, ttl: int | None = None) -> None:
        self.items[entity.id] = entity

    async def get_by_id(self, id: UUID) -> {Entity} | None:
        return self.items.get(id)

    async def delete(self, entity: {Entity}) -> None:
        self.items.pop(entity.id, None)
        self.deleted.append(entity.id)
```

The `deleted` list makes invalidation assertable — that is the property worth testing:

```python
    assert existing.id in cache.deleted
```

## Fake service

```python
class Fake{Name}Service:
    def __init__(self) -> None:
        self.calls: list[{Entity}] = []
        self.fail = False

    async def generate(self, entity: {Entity}) -> {Entity}:
        if self.fail:
            raise RuntimeError("simulated service failure")
        self.calls.append(entity)
        entity.plain_key = "test-plain-value"
        entity.hashed_key = "test-hashed-value"
        return entity
```

## Fixtures

Fresh instances per test — shared state produces order-dependent failures.

```python
import pytest

from app.modules.shared.domain.value_objects import Email, Name
from app.modules.user.domain.entities import User


@pytest.fixture
def repository() -> Fake{Entity}Repository:
    return Fake{Entity}Repository()


@pytest.fixture
def cache() -> Fake{Entity}Cache:
    return Fake{Entity}Cache()


@pytest.fixture
def use_case(repository, cache) -> {Module}UseCases:
    return {Module}UseCases(cache=cache, repository=repository)


@pytest.fixture
def actor() -> User:
    return User(
        id=uuid4(),
        name=Name(first_name="Test", last_name="Actor"),
        email="test.actor@example.com",
    )
```

`Email` enforces `SECURITY_EMAIL_ALLOWED_DOMAINS`. When the test environment sets that list, either
use an allowed domain or construct with `Email(email=..., enforce_allowed_domains=False)`.

## Entity validation tests

Assert on the collected list, not on the first message.

```python
import pytest

from app.modules.shared.domain.entities import DomainErrors


def test_entity_accepts_valid_values(actor):
    entity = {Entity}(name="Valid name", created_by=actor, updated_by=actor)

    assert entity.name == "Valid name"
    assert entity.is_active is True


def test_entity_rejects_short_name(actor):
    with pytest.raises(DomainErrors) as exc_info:
        {Entity}(name="ab", created_by=actor, updated_by=actor)

    assert any("at least 3 characters" in error for error in exc_info.value.errors)


def test_entity_collects_every_error(actor):
    with pytest.raises(DomainErrors) as exc_info:
        {Entity}(name="ab", description="x" * 5000, created_by=actor, updated_by=actor)

    assert len(exc_info.value.errors) >= 2


def test_entity_normalizes_name(actor):
    entity = {Entity}(name="  multiple   spaces  ", created_by=actor, updated_by=actor)

    assert entity.name == "Multiple spaces"


def test_deactivate_records_the_actor(actor, other_actor):
    entity = {Entity}(name="Valid name", created_by=actor, updated_by=actor)

    entity.deactivate(updated_by=other_actor)

    assert entity.is_active is False
    assert entity.updated_by == other_actor
```

Normalization deserves its own test — it is behaviour, not incidental.

## Value object tests

```python
from app.modules.shared.domain.entities import DomainError


def test_value_object_normalizes():
    assert str(Slug(slug="  Hello World  ")) == "hello-world"


def test_value_object_rejects_empty():
    with pytest.raises(DomainError):
        Slug(slug="")


def test_value_object_equality_is_by_normalized_value():
    assert Slug(slug="Hello World") == Slug(slug="hello-world")
```

Value objects raise `DomainError`, singular. Entities raise `DomainErrors`, plural.

## Use case tests

```python
async def test_create_persists_the_entity(use_case, repository, actor):
    entity = {Entity}(name="New entity", created_by=actor, updated_by=actor)

    result = await use_case.create(entity)

    assert result.id is not None
    assert result.id in repository.items


async def test_create_raises_conflict_when_name_already_exists(use_case, repository, actor):
    existing = {Entity}(id=uuid4(), name="Taken", created_by=actor, updated_by=actor)
    repository.items[existing.id] = existing

    with pytest.raises({Entity}NameAlreadyExistsException) as exc_info:
        await use_case.create({Entity}(name="Taken", created_by=actor, updated_by=actor))

    assert exc_info.value.status_code == HTTPStatus.CONFLICT


async def test_get_by_id_raises_not_found(use_case, actor):
    with pytest.raises({Entity}NotFoundException) as exc_info:
        await use_case.get_by_id({Entity}(id=uuid4(), created_by=actor, updated_by=actor))

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


async def test_get_by_id_serves_from_cache(use_case, cache, repository, actor):
    cached = {Entity}(id=uuid4(), name="Cached", created_by=actor, updated_by=actor)
    cache.items[cached.id] = cached

    result = await use_case.get_by_id({Entity}(id=cached.id, created_by=actor, updated_by=actor))

    assert result is cached
    assert repository.items == {}   # the database was never touched


async def test_delete_invalidates_the_cache(use_case, cache, repository, actor):
    existing = {Entity}(id=uuid4(), name="Doomed", created_by=actor, updated_by=actor)
    repository.items[existing.id] = existing
    cache.items[existing.id] = existing

    await use_case.delete({Entity}(id=existing.id, updated_by=actor))

    assert existing.id in cache.deleted
```

Assert on the exception class and its `status_code`. Message wording changes; the contract does
not.

## The unexpected-failure path

The test that actually validates the 3-branch shape — an infrastructure error must surface as the
module's own exception, never leak the original.

```python
async def test_create_wraps_unexpected_failures(use_case, repository, actor):
    repository.fail = True

    with pytest.raises({Module}Exception) as exc_info:
        await use_case.create({Entity}(name="Anything", created_by=actor, updated_by=actor))

    assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
```

Write one of these per use-case method. It is the case most often skipped and the one that catches
a mis-ordered `except` block.

## Partial-update tests

```python
async def test_update_keeps_omitted_fields(use_case, repository, actor):
    existing = {Entity}(
        id=uuid4(),
        name="Original",
        description="Original description",
        created_by=actor,
        updated_by=actor,
    )
    repository.items[existing.id] = existing

    result = await use_case.update(
        {Entity}(id=existing.id, name="Renamed", updated_by=actor)
    )

    assert result.name == "Renamed"
    assert result.description == "Original description"  # UNSET preserved it


async def test_update_preserves_authorship(use_case, repository, actor, other_actor):
    existing = {Entity}(id=uuid4(), name="Original", created_by=actor, updated_by=actor)
    repository.items[existing.id] = existing

    result = await use_case.update(
        {Entity}(id=existing.id, name="Renamed", updated_by=other_actor)
    )

    assert result.created_by == actor
    assert result.updated_by == other_actor
```

The `description` field must be omitted from the update entity entirely, so it defaults to `UNSET`.
Passing `description=None` is the other case — it clears the field — and deserves its own test.

## Mapper round-trip tests

```python
from datetime import datetime


def test_entity_model_round_trip_preserves_every_field(actor):
    original = {Entity}(
        id=uuid4(),
        name="Round trip",
        description="Description",
        created_by=actor,
        updated_by=actor,
        created_at=datetime(2026, 1, 15, 10, 30),
        updated_at=datetime(2026, 1, 16, 8, 0),
    )

    model = entity_model_mapper(original)
    result = model_entity_mapper(model)

    assert result.id == original.id
    assert result.name == original.name
    assert result.description == original.description
    assert result.created_by.id == original.created_by.id
    # Inherited fields: automapper does not traverse parent slots, so these
    # are exactly what a missing fields_mapping entry silently drops.
    assert result.is_active == original.is_active
    assert result.created_at == original.created_at
    assert result.updated_at == original.updated_at


def test_cache_round_trip_preserves_every_field(actor):
    original = {Entity}(id=uuid4(), name="Cached", created_by=actor, updated_by=actor)

    result = cache_entity_mapper(entity_cache_mapper(original))

    assert result.id == original.id
    assert result.name == original.name
    assert result.is_active == original.is_active
```

These two tests are the highest-value ones in the suite: a dropped field in a mapper produces an
intermittent `None` that no other test catches.
