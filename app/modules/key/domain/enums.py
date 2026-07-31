from datetime import timedelta
from enum import Enum


class KeyExpiration(str, Enum):
    SEVEN_DAYS = "7_days"
    THIRTY_DAYS = "30_days"
    FORTY_FIVE_DAYS = "45_days"
    SIXTY_DAYS = "60_days"
    NINETY_DAYS = "90_days"
    SIX_MONTHS = "6_months"
    NEVER = "never"

    @property
    def duration(self) -> timedelta | None:
        """The validity period of this preset, or None when the key never expires."""
        return {
            KeyExpiration.SEVEN_DAYS: timedelta(days=7),
            KeyExpiration.THIRTY_DAYS: timedelta(days=30),
            KeyExpiration.FORTY_FIVE_DAYS: timedelta(days=45),
            KeyExpiration.SIXTY_DAYS: timedelta(days=60),
            KeyExpiration.NINETY_DAYS: timedelta(days=90),
            KeyExpiration.SIX_MONTHS: timedelta(days=180),
        }.get(self)


class KeySortField(str, Enum):
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
