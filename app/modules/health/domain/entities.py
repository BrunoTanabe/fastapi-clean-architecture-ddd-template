from __future__ import annotations

from dataclasses import dataclass

from app.modules.health.application.enums import HealthType


@dataclass
class Health:
    # RESPONSE
    status: HealthType
