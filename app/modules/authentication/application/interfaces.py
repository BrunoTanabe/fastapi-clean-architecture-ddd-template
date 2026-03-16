from typing import Protocol, Optional

from app.modules.authentication.domain.entities import (
    Session,
    AccessToken,
    RefreshToken,
)


class IAuthenticationRepository(Protocol):
    # CREATE
    async def create(self, session: Session) -> None: ...

    # READ
    async def get_by_user_id_agent_and_device(
        self, session: Session
    ) -> Optional[Session]: ...

    async def get_access_token_by_hashed_jti(
        self, access_token: AccessToken
    ) -> Optional[AccessToken]: ...

    async def get_refresh_token_by_hashed_jti(
        self, refresh_token: RefreshToken
    ) -> Optional[RefreshToken]: ...

    # UPDATE
    async def update(self, session: Session) -> None: ...
