from datetime import timezone, datetime
from zoneinfo import ZoneInfo

BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")


def _current_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.isoformat().replace("+00:00", "Z")
