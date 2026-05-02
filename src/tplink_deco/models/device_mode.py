from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DeviceMode:
    workmode: str
    sysmode: str
    region: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "DeviceMode":
        return cls(
            workmode=data.get("workmode", ""),
            sysmode=data.get("sysmode", ""),
            region=data.get("region", {}).get("device", ""),
        )
