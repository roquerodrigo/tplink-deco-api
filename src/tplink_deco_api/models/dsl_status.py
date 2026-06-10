"""DSL link status for a Deco node.

On non-DSL hardware all fields are empty strings or zero.
"""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_int, get_str


@dataclass(frozen=True)
class DslStatus:
    """DSL physical-layer link status.

    Fields are populated only on DSL-capable hardware. On other hardware
    the router returns an empty result and all fields default to their
    zero values.
    """

    status: str
    upstream_rate: int
    downstream_rate: int
    upstream_max_rate: int
    downstream_max_rate: int
    upstream_noise_margin: int
    downstream_noise_margin: int
    upstream_attenuation: int
    downstream_attenuation: int

    @classmethod
    def from_api(cls, data: JsonObject) -> DslStatus:
        """Build ``DslStatus`` from a router payload."""
        return cls(
            status=get_str(data, "status"),
            upstream_rate=get_int(data, "upstream_rate"),
            downstream_rate=get_int(data, "downstream_rate"),
            upstream_max_rate=get_int(data, "upstream_max_rate"),
            downstream_max_rate=get_int(data, "downstream_max_rate"),
            upstream_noise_margin=get_int(data, "upstream_noise_margin"),
            downstream_noise_margin=get_int(data, "downstream_noise_margin"),
            upstream_attenuation=get_int(data, "upstream_attenuation"),
            downstream_attenuation=get_int(data, "downstream_attenuation"),
        )
