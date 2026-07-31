from typing import Protocol

from app.modules.authentication.domain.entities import Authentication


class IAuthenticationRepository(Protocol):
    # CREATE
    async def create(self, authentication: Authentication) -> Authentication: ...

    # READ
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_access_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_refresh_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # UPDATE
    async def update(self, authentication: Authentication) -> Authentication: ...

    # DELETE
    async def delete(self, authentication: Authentication) -> Authentication: ...


class IAuthenticationCache(Protocol):
    # CREATE
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    # READ
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # DELETE
    async def delete_by_access_token(self, authentication: Authentication) -> None: ...

    async def delete_by_refresh_token(self, authentication: Authentication) -> None: ...


class ITokenService(Protocol):
    async def generate(self, authentication: Authentication) -> Authentication: ...

    async def hash_tokens(self, authentication: Authentication) -> Authentication: ...

    async def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool: ...
