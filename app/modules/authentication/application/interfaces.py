from typing import Protocol, Optional

from app.modules.authentication.domain.entities import (
    Session,
)


class IAuthenticationRepository(Protocol):
    # CREATE
    async def create(self, session: Session) -> None: ...

    # READ
    async def get_by_user_id_agent_and_device(
        self, session: Session
    ) -> Optional[Session]: ...

    async def get_access_token_by_session(
        self, session: Session
    ) -> Optional[Session]: ...

    async def get_refresh_token_by_session(
        self, session: Session
    ) -> Optional[Session]: ...

    # UPDATE
    async def update(self, session: Session) -> None: ...

    # DELETE
    async def delete(self, session: Session) -> None: ...
