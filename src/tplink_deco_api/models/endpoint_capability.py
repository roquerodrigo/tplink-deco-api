"""Outcome of probing one documented read endpoint on the connected router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type CapabilityStatus = Literal["ok", "empty", "absent", "error"]


@dataclass(frozen=True)
class EndpointCapability:
    """Whether the router answers one ``path`` + ``form`` read.

    ``status`` is ``"ok"`` for a non-empty result, ``"empty"`` when the
    router accepts the read but returns nothing, ``"absent"`` when the module
    is missing (HTTP 404) and ``"error"`` otherwise; ``detail`` then holds the
    HTTP status or the router's ``error_code``.
    """

    path: str
    form: str
    operation: str
    status: CapabilityStatus
    detail: str = ""
