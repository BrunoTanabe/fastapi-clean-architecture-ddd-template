from dataclasses import dataclass, field

from app.modules.health.domain.enums import HealthType
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Health:
    # Alembic fields
    alembic_version: str = field(default=None, repr=True, compare=True)
    user: User = field(default=None, compare=True, repr=True)

    @property
    def status(self) -> HealthType:
        return HealthType.OK
