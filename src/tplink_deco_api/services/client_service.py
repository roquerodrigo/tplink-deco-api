"""Editing, removal and blocking of the clients known to the mesh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import BlockedClient
from ..models._utils import encode_b64
from ._request import require_mac

if TYPE_CHECKING:
    from .._json import JsonValue
    from ._request import RequestSender

_PATH = "admin/client"


class ClientService:
    """Changes the clients listed by :meth:`DecoClient.get_client_list`."""

    def __init__(self, send: RequestSender) -> None:
        self._send = send

    def update(self, mac: str, name: str, client_type: str | None = None) -> None:
        """Rename ``mac`` and optionally change its device category.

        The firmware ignores an entry unless it carries a user-set name, so the
        name is always sent; pass the current one to change only ``client_type``.
        """
        if not name.strip():
            message = "Failed to update client: name must not be blank"
            raise ValueError(message)
        entry: dict[str, JsonValue] = {
            "mac": require_mac(mac),
            "name": encode_b64(name),
            "user_set_name_type": True,
        }
        if client_type is not None:
            entry["client_type"] = client_type
        self._send(_PATH, "client_list", {"operation": "write", "params": {"client_list": [entry]}})

    def remove(self, mac: str) -> None:
        """Forget ``mac``; the router lists it again if the device reconnects."""
        entry: dict[str, JsonValue] = {"mac": require_mac(mac)}
        self._send(
            _PATH, "client_list", {"operation": "remove", "params": {"client_list": [entry]}}
        )

    def get_blocked(self) -> list[BlockedClient]:
        """Return every client on the mesh-wide internet blocklist."""
        result = self._send(_PATH, "black_list", {"operation": "list"})
        items = result.get("client_list")
        if not isinstance(items, list):
            return []
        return [BlockedClient.from_api(item) for item in items if isinstance(item, dict)]

    def block(self, mac: str, name: str, client_type: str) -> None:
        """Cut ``mac`` off from the internet; ``name`` and ``client_type`` label the entry."""
        entry: dict[str, JsonValue] = {
            "mac": require_mac(mac),
            "name": encode_b64(name),
            "client_type": client_type,
        }
        self._send(_PATH, "black_list", {"operation": "block", "params": {"client_list": [entry]}})

    def unblock(self, mac: str) -> None:
        """Restore internet access for ``mac``."""
        macs: list[JsonValue] = [require_mac(mac)]
        self._send(_PATH, "black_list", {"operation": "unblock", "params": {"client_list": macs}})
