# Service Templates

## Contents

- [Protocol](#protocol)
- [Stateless implementation](#stateless-implementation)
- [Thin wrapper over a core helper](#thin-wrapper-over-a-core-helper)
- [External-system implementation](#external-system-implementation)
- [Stateful singleton](#stateful-singleton)
- [DI factories](#di-factories)
- [Use-case wiring](#use-case-wiring)
- [Best-effort calls](#best-effort-calls)

## Protocol

`application/interfaces.py`, alongside the repository and cache Protocols.

```python
from typing import Protocol

from app.modules.{module}.domain.entities import {Entity}


class I{Name}Service(Protocol):
    async def generate(self, entity: {Entity}) -> {Entity}: ...

    async def send(self, entity: {Entity}) -> None: ...
```

Domain entities in, domain entities or `None` out. A Protocol that mentions a Pydantic schema or an
ORM model has leaked a layer.

## Stateless implementation

```python
from loguru import logger

from app.core.settings import settings
from app.modules.shared.application.exceptions import StandardException
from app.modules.{module}.application.exceptions import {Module}Exception
from app.modules.{module}.application.interfaces import I{Name}Service
from app.modules.{module}.domain.entities import {Entity}


class {Name}Service(I{Name}Service):
    async def send(self, entity: {Entity}) -> None:
        try:
            logger.debug(f"Sending {entity} '{entity.id}' through the {name} service.")

            ...

            logger.debug(f"{Entity} '{entity.id}' sent successfully.")
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the send {name} service."
            )
            raise {Module}Exception()
```

## Thin wrapper over a core helper

When the whole method is a delegation to a `core` helper that already handles its own errors, skip
the try/except. Reference: `KeyService`.

```python
from app.core.security import generate_api_key
from app.modules.key.application.interfaces import IKeyService
from app.modules.key.domain.entities import Key


class KeyService(IKeyService):
    async def generate(self, key: Key) -> Key:
        return generate_api_key(key)
```

The Protocol still earns its place: the use case depends on `IKeyService`, so the generation
strategy can be replaced or faked in tests without touching the use case.

Add the branches as soon as the method does more than delegate.

## External-system implementation

Configuration from `settings`, distinct exceptions per failure mode, and no upstream error text in
the response.

```python
class EmailSenderService(IEmailSenderService):
    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.timeout = settings.SMTP_TIMEOUT_SECONDS

    async def send(self, notification: Notification) -> None:
        try:
            logger.debug(f"Sending email for notification '{notification.id}'.")

            ...

            logger.debug(f"Email for notification '{notification.id}' sent successfully.")
        except StandardException:
            raise
        except TimeoutError as e:
            logger.opt(exception=e).error("The email service did not respond in time.")
            raise EmailSenderServiceTimeoutException()
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the send email service.")
            raise EmailSenderServiceUnavailableException()
```

A technology-specific middle branch is allowed here — it is how the service turns an upstream
failure mode into the right HTTP status. See `/create-exception` for the 502 and 504 shapes.

## Stateful singleton

State lives on the instance; the instance lives on `app.state`. Reference: `ConnectionManager`.

```python
class ConnectionManager(IConnectionManagerService):
    def __init__(self) -> None:
        self.active_connections: dict[WebSocket, WebSocketMessage] = {}
```

Created once in the lifespan, in `app/core/resources.py::startup`:

```python
    app.state.connection_manager = ConnectionManager()  # noqa
    logger.info("WebSocket connection manager initialized successfully.")
```

A singleton holding in-process state is single-worker only. Say so in a comment when the state
would need to be shared across workers.

## DI factories

**Stateless** — construct per request:

```python
def get_{name}_service() -> I{Name}Service:
    return {Name}Service()
```

**With configuration or a client** — take it as a dependency:

```python
def get_{name}_service(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> I{Name}Service:
    return {Name}Service(cache=cache)
```

**Singleton from `app.state`** — read it off the connection, never re-create it:

```python
from fastapi import Request


def get_connection_manager(request: Request) -> IConnectionManagerService:
    return request.app.state.connection_manager
```

Use `HTTPConnection` instead of `Request` when the same factory must serve WebSocket routes —
`Request` is not available during a WebSocket handshake.

The return annotation is always the Protocol.

## Use-case wiring

```python
def get_{module}_use_cases(
    cache: Annotated[I{Entity}Cache, Depends(get_{module}_cache)],
    repository: Annotated[I{Entity}Repository, Depends(get_{module}_repository)],
    service: Annotated[I{Name}Service, Depends(get_{name}_service)],
) -> {Module}UseCases:
    return {Module}UseCases(cache=cache, repository=repository, service=service)
```

```python
class {Module}UseCases:
    def __init__(
        self,
        cache: I{Entity}Cache,
        repository: I{Entity}Repository,
        service: I{Name}Service,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.service = service
```

Keep the collaborator order consistent across modules: `cache`, `repository`, `service`,
`shared_service`.

## Best-effort calls

When a service failure must not fail the request, the **caller** decides that — the service still
raises. Reference: `SharedUseCases._dispatch_user_notification_message`.

```python
    async def _dispatch_notification(self, notification: Notification) -> None:
        try:
            await self.service.send(notification)
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to dispatch notification '{notification.id}'; continuing best-effort."
            )
```

Persist first, dispatch second. A failed dispatch then leaves correct data behind, while a failed
persist leaves nothing to dispatch.
