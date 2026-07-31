from typing import Protocol

from app.modules.user.domain.entities import User


class IUserRepository(Protocol):
    # CREATE
    async def create(self, user: User) -> User: ...

    # READ
    async def exists_by_email(self, user: User) -> bool: ...

    async def get_by_id(self, user: User) -> User | None: ...

    async def get_by_email(self, user: User) -> User | None: ...
