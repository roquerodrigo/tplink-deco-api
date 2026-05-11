from collections.abc import Iterable
from dataclasses import dataclass

from .client_device import ClientDevice


@dataclass(frozen=True)
class NetworkTotals:
    up_speed: int
    down_speed: int

    @classmethod
    def from_clients(cls, clients: Iterable[ClientDevice]) -> "NetworkTotals":
        up_total = 0
        down_total = 0
        for client in clients:
            up_total += client.up_speed
            down_total += client.down_speed
        return cls(up_speed=up_total, down_speed=down_total)
