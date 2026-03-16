from typing import Protocol, Optional

from app.modules.health.domain.entities import Health


class IHealthRepository(Protocol):
    # READ
    async def get_alembic_version(self, health: Health) -> Optional[Health]: ...
