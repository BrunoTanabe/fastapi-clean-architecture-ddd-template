from datetime import datetime

from app.modules.key.domain.enums import KeyExpiration
from app.modules.shared.application.utils import BRASILIA_TZ


def resolve_expires_at(expires_in: KeyExpiration) -> datetime | None:
    delta = expires_in.duration
    if delta is None:
        return None
    return datetime.now(BRASILIA_TZ) + delta
