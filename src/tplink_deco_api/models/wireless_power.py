"""Wireless transmit power settings for a Deco node."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_bool


@dataclass(frozen=True)
class WirelessPower:
    """Wireless transmit power configuration.

    ``support_dfs`` indicates whether the hardware supports Dynamic
    Frequency Selection on the 5 GHz band.
    """

    support_dfs: bool

    @classmethod
    def from_api(cls, data: JsonObject) -> WirelessPower:
        """Build ``WirelessPower`` from a router payload."""
        return cls(support_dfs=get_bool(data, "support_dfs"))
