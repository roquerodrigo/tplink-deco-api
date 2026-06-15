"""Log category descriptor returned by the log-export endpoint."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_str


@dataclass(frozen=True)
class LogType:
    """A single log category available for export."""

    name: str
    value: int

    @classmethod
    def from_api(cls, data: JsonObject) -> LogType:
        """Build ``LogType`` from a router payload."""
        return cls(
            name=get_str(data, "name"),
            value=get_int(data, "value"),
        )
