from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Performance:
    cpu_usage: float
    mem_usage: float

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Performance":
        return cls(
            cpu_usage=float(data["cpu_usage"]),
            mem_usage=float(data["mem_usage"]),
        )
