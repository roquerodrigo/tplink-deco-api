from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceMode:
    mode: str
    raw:  dict
