# Endpoint Templates

A worked example of one endpoint through every layer, so the pieces can be checked against each
other. Per-layer detail lives in each layer's own skill.

## Contents

- [The layer chain](#the-layer-chain)
- [1. Schemas](#1-schemas)
- [2. Mappers](#2-mappers)
- [3. Protocol signature](#3-protocol-signature)
- [4. Repository method](#4-repository-method)
- [5. Use case method](#5-use-case-method)
- [6. Dependencies](#6-dependencies)
- [7. Docs dict](#7-docs-dict)
- [8. Router handler](#8-router-handler)
- [9. Allowlist rules](#9-allowlist-rules)
- [Name alignment](#name-alignment)

## The layer chain

For `POST /api/v1/{module}/`:

```
CreateRequest                       presentation/schemas.py
   → create_entity_mapper           application/mappers.py
      → {Entity}                    domain/entities.py
         → use_case.create          application/use_cases.py
            → repository.create     infrastructure/repositories.py
               → entity_model_mapper / model_entity_mapper
                  → {Entity}Model   infrastructure/models.py
   ← entity_create_mapper           application/mappers.py
Create{Entity}Response              presentation/schemas.py
```

Every arrow is a place a field name can silently disappear. Walk the chain once before linting.

## 1. Schemas

```python
class CreateRequest(BaseModel):
    name: str = Field(
        title="{Entity} Name (Required)",
        description="A human-readable name to identify the {entity}.",
        min_length=3,
        max_length=255,
        examples=["My {entity}"],
        json_schema_extra={"example": "My {entity}", "writeOnly": True},
    )

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Payload for creating a new {entity}.",
            "example": {"name": "My {entity}"},
        },
    )
```

## 2. Mappers

```python
# ENTITY / DTOS
def create_entity_mapper(payload: CreateRequest, authentication: Authentication) -> {Entity}:
    return mapper.to({Entity}).map(
        payload,
        fields_mapping={
            "name": payload.name,
            "description": payload.description,
            "created_by": authentication.user,
            "updated_by": authentication.user,
        },
    )


def entity_create_mapper(entity: {Entity}) -> CreateResponse:
    return CreateResponse()
```

## 3. Protocol signature

```python
class I{Entity}Repository(Protocol):
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}: ...

    # READ
    async def exists_by_name(self, entity: {Entity}) -> bool: ...
```

Add the `exists_by_*` signature at the same time as `create` when the use case enforces uniqueness
— otherwise the use case will call a method that does not exist.

## 4. Repository method

```python
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.info(
                f"Creating {entity} '{entity.name}' in database. "
                f"Requested by user {entity.created_by.id}."
            )

            db_model: {Entity}Model = entity_model_mapper(entity)

            self.session.add(db_model)
            await self.session.flush()

            logger.info(f"{Entity} '{entity.name}' created successfully in database.")
            return model_entity_mapper(db_model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create {entity} repository."
            )
            raise {Module}Exception()
```

2-branch: no `DomainError` branch in a repository.

## 5. Use case method

```python
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing create {module} use case for '{entity.name}'. "
                f"Requested by user {entity.created_by.id}."
            )

            if await self.repository.exists_by_name(entity):
                logger.info(
                    f"{Entity} with name '{entity.name}' already exists. Raising exception."
                )
                raise {Entity}NameAlreadyExistsException(name=entity.name)

            entity = await self.repository.create(entity)

            logger.debug(f"Create {module} use case completed successfully for {entity.id}.")
            return entity
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create {module} use case."
            )
            raise {Module}Exception()
```

3-branch, `StandardException` first — it is an `HTTPException`, so a later branch would turn every
deliberate 404 and 409 into a 500.

## 6. Dependencies

```python
def get_{module}_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> I{Entity}Repository:
    return Postgres{Entity}Repository(session=session)


def get_{module}_use_cases(
    repository: Annotated[I{Entity}Repository, Depends(get_{module}_repository)],
) -> {Module}UseCases:
    return {Module}UseCases(repository=repository)
```

Add `cache` and `service` parameters here at the same time you add them to the constructor —
forgetting the factory is a runtime `TypeError` on the first request, not an import error.

## 7. Docs dict

```python
create_docs = {
    "summary": "Create a new {entity}",
    "description": "Creates a new {entity} owned by the authenticated user.",
    "response_description": "The {entity} was created successfully.",
    "status_code": HTTPStatus.CREATED,
    "response_model": CreateResponse,
    "include_in_schema": True,
    "responses": {
        201: { ... },
        409: { ... },
    },
}
```

## 8. Router handler

```python
# CREATE
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
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
        logger.opt(exception=e).error("An error occurred in the create {module} endpoint.")
        raise {Module}Exception()
```

## 9. Allowlist rules

In the tier matching the handler's dependency, in `app/core/settings.py`:

```python
    # {MODULE}
    _path_rule("/api/v1/{module}/", "POST"),
    _path_rule("/api/v1/{module}", "POST"),
```

Both forms, every time. This is the single most common omission.

## Name alignment

Before linting, check these pairs line up:

| Left | Right |
|------|-------|
| Request schema field | `fields_mapping` key in the request mapper |
| Entity field | `fields_mapping` key in both model mappers |
| Model column attribute | `fields_mapping` value in both model mappers |
| Response schema field | `fields_mapping` key in the response mapper |
| Handler return annotation | `response_model` in the docs dict |
| Router path | both `_path_rule` entries |
| Protocol method signature | repository implementation signature |
| Use-case constructor parameters | `get_{module}_use_cases` parameters |

None of these are caught by ruff. All of them fail at runtime.
