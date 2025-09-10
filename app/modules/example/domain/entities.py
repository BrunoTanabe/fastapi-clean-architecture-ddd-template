from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Example:
    # REQUEST
    name: str

    # RESPONSE
    message: str | None = field(default=None)
