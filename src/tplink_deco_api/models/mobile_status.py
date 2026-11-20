"""Cellular (LTE / 5G) connection status for mobile Deco gateways."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_str
from ._utils import decode_b64


@dataclass(frozen=True)
class MobileStatus:
    """Cellular link state reported under ``mobile_cpe`` by LTE / 5G models.

    Numeric fields are passed through unscaled as the router reports them;
    ``rsrp`` and ``rssi`` are in dBm, ``rsrq`` and ``snr`` in dB.
    """

    inet_status: str
    dial_status: str
    sim_status: str
    network_type: str
    signal_strength: int
    rsrp: int
    rsrq: int
    snr: int
    rssi: int
    uplink_rate: int
    downlink_rate: int
    data_usage: int
    limit_mode: str
    profile_name: str
    sim_number: str

    @classmethod
    def from_api(cls, data: JsonObject) -> MobileStatus:
        """Build ``MobileStatus`` from a ``mobile_cpe`` payload, decoding ``profile_name``."""
        return cls(
            inet_status=get_str(data, "inet_status"),
            dial_status=get_str(data, "dial_status"),
            sim_status=get_str(data, "sim_status"),
            network_type=get_str(data, "network_type"),
            signal_strength=get_int(data, "signal_strength"),
            rsrp=get_int(data, "rsrp"),
            rsrq=get_int(data, "rsrq"),
            snr=get_int(data, "snr"),
            rssi=get_int(data, "rssi"),
            uplink_rate=get_int(data, "uplink_rate"),
            downlink_rate=get_int(data, "downlink_rate"),
            data_usage=get_int(data, "data_usage"),
            limit_mode=get_str(data, "limit_mode"),
            profile_name=decode_b64(get_str(data, "profile_name")),
            sim_number=get_str(data, "sim_number"),
        )
