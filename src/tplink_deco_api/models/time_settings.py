"""Date, time and timezone settings for a Deco node."""

from __future__ import annotations

from dataclasses import dataclass

from .._json import JsonObject, get_str


@dataclass(frozen=True)
class TimeSettings:
    """Current date/time and timezone configuration as reported by a node."""

    time: str
    date: str
    timezone: str
    tz_region: str
    continent: str
    dst_status: str

    @classmethod
    def from_api(cls, data: JsonObject) -> TimeSettings:
        """Build ``TimeSettings`` from a router payload."""
        return cls(
            time=get_str(data, "time"),
            date=get_str(data, "date"),
            timezone=get_str(data, "timezone"),
            tz_region=get_str(data, "tz_region"),
            continent=get_str(data, "continent"),
            dst_status=get_str(data, "dst_status"),
        )
