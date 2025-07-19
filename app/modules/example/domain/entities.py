from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Example:
    # Request
    name: str

    # Response
    message: str | None = field(default=None)
