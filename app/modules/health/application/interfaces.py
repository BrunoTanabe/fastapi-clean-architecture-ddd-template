from typing import Protocol

from app.modules.health.domain.entities import Health


class IHealthRepository(Protocol):
    # READ
    async def get_alembic_version(self, health: Health) -> Health | None: ...
