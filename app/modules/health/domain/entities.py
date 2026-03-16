from dataclasses import dataclass, field

from app.modules.health.application.enums import HealthType
from app.modules.user.domain.entities import User


@dataclass
class Health:
    # Alembic fields
    alembic_version: str = field(default=None, repr=True, compare=True)
    user: User = field(default=None, compare=True, repr=True)

    @property
    def status(self) -> HealthType:
        return HealthType.OK
