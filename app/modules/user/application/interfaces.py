from typing import Protocol, Optional

from app.modules.user.domain.entities import User


class IUserRepository(Protocol):
    # CREATE
    async def create(self, user: User) -> None: ...

    # READ
    async def exists_by_email(self, user: User) -> bool: ...

    async def get_by_id(self, user: User) -> Optional[User]: ...
