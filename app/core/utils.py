from datetime import timezone, datetime


def _current_timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.isoformat().replace("+00:00", "Z")
