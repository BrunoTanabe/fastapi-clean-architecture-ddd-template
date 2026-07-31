from datetime import UTC, datetime
from typing import TypeVar
from zoneinfo import ZoneInfo

T = TypeVar("T")

BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")


def current_timestamp() -> str:
    now = datetime.now(UTC)
    return now.isoformat().replace("+00:00", "Z")


def resolve_client_ip(
    x_forwarded_for: str | None,
    x_real_ip: str | None,
    peer_host: str | None,
) -> str:
    if x_forwarded_for:
        first_hop = x_forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop
    if x_real_ip and x_real_ip.strip():
        return x_real_ip.strip()
    return peer_host or "unknown"
