# Exception Templates

Every class subclasses `StandardException`, which is an `HTTPException` carrying `message` and
`data` alongside `status_code`.

## Contents

- [File skeleton](#file-skeleton)
- [Generic exception](#generic-exception)
- [Not found](#not-found)
- [Conflict](#conflict)
- [Not modified](#not-modified)
- [Credential failures](#credential-failures)
- [Forbidden](#forbidden)
- [Upstream dependency](#upstream-dependency)
- [Multiple errors in one payload](#multiple-errors-in-one-payload)

## File skeleton

```python
from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.application.exceptions import StandardException


# GENERIC EXCEPTIONS
class {Module}Exception(StandardException):
    ...


# SPECIFIC EXCEPTIONS
class {Entity}NotFoundException(StandardException):
    ...
```

## Generic exception

Exactly one per module, no constructor arguments. Raised by the final `except Exception` branch
in every layer of the module.

```python
class {Module}Exception(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the {module} module."
            },
        )
```

Keep the wording verbatim apart from the module name — it is what makes a 500 traceable to a
module from the response alone.

## Not found

```python
class {Entity}NotFoundException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"{Entity} with id '{id}' not found."},
        )
```

One class per lookup dimension when the messages differ — `user` has both
`UserIdNotFoundException` and `UserEmailNotFoundException`.

## Conflict

```python
class {Entity}NameAlreadyExistsException(StandardException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={"errors": f"{Entity} with name '{name}' already exists."},
        )
```

Raise it from the use case after an explicit `exists_by_*` check, rather than catching the
database's unique-constraint error — the check produces a clear message and keeps the constraint
as a backstop.

## Not modified

A `PATCH` whose merged result equals the stored record. Reference: `KeyNotModifiedException`.

```python
class {Entity}NotModifiedException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.BAD_REQUEST.value,
            data={
                "errors": f"No changes were provided; the {entity} with id '{id}' already has the submitted values."
            },
        )
```

## Credential failures

Distinguish the cases — the client needs to know whether to retry, re-authenticate, or issue a new
credential. Reference: the four API-key exceptions in `key`.

```python
class ApiKeyNotProvidedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "API key was not provided. Please provide a valid API key in the request header."
            },
        )


class ApiKeyInvalidException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={"errors": "Invalid API key. The provided key is not valid or does not exist."},
        )


class ApiKeyRevokedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={"errors": "The provided API key has been revoked and can no longer be used."},
        )


class ApiKeyExpiredException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={"errors": "The provided API key has expired. Please generate a new API key."},
        )
```

Credential exceptions take no arguments and never echo the submitted credential.

## Forbidden

Authenticated, but not allowed. Distinct from 401 — the client should not retry with new
credentials of the same kind.

```python
class {Entity}AccessDeniedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=ResponseMessages.AUTHORIZATION_ERROR.value,
            data={"errors": "You do not have permission to access this resource."},
        )
```

## Upstream dependency

For a service wrapping an external system.

```python
class {Name}ServiceUnavailableException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_GATEWAY,
            message=ResponseMessages.BAD_GATEWAY.value,
            data={"errors": "The {name} service is currently unavailable. Please try again later."},
        )


class {Name}ServiceTimeoutException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.GATEWAY_TIMEOUT,
            message=ResponseMessages.GATEWAY_TIMEOUT.value,
            data={"errors": "The {name} service did not respond in time. Please try again later."},
        )
```

Never surface the upstream's own error text — it can leak internal hosts, credentials, or payloads.
Log the original with `logger.opt(exception=e).error(...)` and return this instead.

## Multiple errors in one payload

`data["errors"]` is a string for a single failure. Use a list only when reporting several at once,
matching what `DomainException` produces:

```python
data={"errors": ["First problem.", "Second problem."]}
```

Do not hand-roll this for validation — raising `DomainErrors(errors)` from the entity produces it
automatically through `DomainException`.
