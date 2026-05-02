from dataclasses import dataclass
from typing import Any

from ._utils import decode_b64, normalize_mac


@dataclass(frozen=True)
class ClientDevice:
    mac: str
    ip: str
    name: str
    up_speed: int
    down_speed: int
    wire_type: str
    connection_type: str
    space_id: str
    access_host: str
    interface: str
    client_type: str
    owner_id: str
    remain_time: int
    online: bool
    client_mesh: bool
    enable_priority: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ClientDevice":
        return cls(
            mac=normalize_mac(data["mac"]),
            ip=data.get("ip", ""),
            name=decode_b64(data.get("name", "")),
            up_speed=int(data.get("up_speed", 0)),
            down_speed=int(data.get("down_speed", 0)),
            wire_type=data.get("wire_type", ""),
            connection_type=data.get("connection_type", ""),
            space_id=data.get("space_id", ""),
            access_host=data.get("access_host", ""),
            interface=data.get("interface", ""),
            client_type=data.get("client_type", ""),
            owner_id=data.get("owner_id", ""),
            remain_time=int(data.get("remain_time", 0)),
            online=bool(data.get("online", False)),
            client_mesh=bool(data.get("client_mesh", False)),
            enable_priority=bool(data.get("enable_priority", False)),
        )
