from datetime import timezone, datetime
from zoneinfo import ZoneInfo
from typing import TypeVar

T = TypeVar("T")

BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")


def current_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.isoformat().replace("+00:00", "Z")
