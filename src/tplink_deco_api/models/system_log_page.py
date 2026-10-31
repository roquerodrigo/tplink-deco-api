"""One page of the gateway's system log."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from .._json import JsonObject, get_int, get_str

# Some firmware leaves time/level/type empty and puts the whole syslog line in
# `content`, e.g. "Mon Oct 26 13:57:02 2026 daemon.notice pppd[18932]: len < 0".
_SYSLOG_LINE = re.compile(
    r"^(?P<time>\w{3} \w{3} +\d{1,2} \d{2}:\d{2}:\d{2} \d{4}) "
    r"(?P<facility>\w+)\.(?P<level>\w+) (?P<source>[^:]*): ?(?P<message>.*)$",
    re.DOTALL,
)


@dataclass(frozen=True)
class SystemLogEntry:
    """A single line of the system log."""

    time: str
    facility: str
    level: str
    source: str
    message: str

    @classmethod
    def from_api(cls, data: JsonObject) -> SystemLogEntry:
        """Build ``SystemLogEntry`` from a ``logList`` item, splitting a raw syslog line."""
        time = get_str(data, "time")
        content = get_str(data, "content")
        match = None if time else _SYSLOG_LINE.match(content)
        if match is None:
            return cls(
                time=time,
                facility="",
                level=get_str(data, "level"),
                source=get_str(data, "type"),
                message=content,
            )
        return cls(
            time=match["time"],
            facility=match["facility"],
            level=match["level"],
            source=match["source"],
            message=match["message"],
        )


@dataclass(frozen=True)
class SystemLogPage:
    """A page of system-log lines, ordered from oldest to newest."""

    page: int
    total_pages: int
    entries: tuple[SystemLogEntry, ...]

    @classmethod
    def from_api(cls, page: int, data: JsonObject) -> SystemLogPage:
        """Build ``SystemLogPage`` from a ``feedback_log`` read result for ``page``."""
        items = data.get("logList")
        return cls(
            page=page,
            total_pages=get_int(data, "totalNum"),
            entries=tuple(
                SystemLogEntry.from_api(item)
                for item in (items if isinstance(items, list) else [])
                if isinstance(item, Mapping)
            ),
        )
