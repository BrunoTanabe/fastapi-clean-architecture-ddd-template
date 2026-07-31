from typing import Protocol

from app.modules.key.domain.entities import Key, KeyList, KeyPagination


class IKeyRepository(Protocol):
    # CREATE
    async def create(self, key: Key) -> Key: ...

    # READ
    async def get_by_id(self, key: Key) -> Key | None: ...

    async def get_all(self, key: Key, pagination: KeyPagination) -> KeyList: ...

    async def get_key_by_hashed_key(self, hashed_key: str) -> Key | None: ...

    # UPDATE
    async def update(self, key: Key) -> Key: ...

    async def rotate(self, key: Key) -> Key: ...


class IKeyCache(Protocol):
    # CREATE
    async def insert(self, key: Key, ttl: int | None = None) -> None: ...

    # READ
    async def get_by_hashed_key(self, hashed_key: str) -> Key | None: ...

    # DELETE
    async def delete(self, key: Key) -> None: ...


class IKeyService(Protocol):
    async def generate(self, key: Key) -> Key: ...
