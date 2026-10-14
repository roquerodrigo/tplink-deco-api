"""Client on the mesh-wide internet blocklist."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_str
from ._utils import decode_b64, normalize_mac


@dataclass(frozen=True)
class BlockedClient:
    """A client whose internet access is blocked across the whole mesh."""

    mac: str
    name: str
    client_type: str

    @classmethod
    def from_api(cls, data: JsonObject) -> BlockedClient:
        """Build ``BlockedClient`` from a router payload."""
        return cls(
            mac=normalize_mac(get_str(data, "mac")),
            name=decode_b64(get_str(data, "name")),
            client_type=get_str(data, "client_type"),
        )
