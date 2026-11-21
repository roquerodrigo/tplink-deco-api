"""Unit tests for ``CapabilityService.probe``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tplink_deco_api import (
    ApiError,
    AuthenticationError,
    CapabilityService,
    CryptoError,
    EndpointCapability,
    TransportError,
)
from tplink_deco_api.services._read_endpoints import READ_ENDPOINTS, READ_OPERATIONS

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tplink_deco_api._json import JsonValue


class _ScriptedSender:
    def __init__(self, answer: Callable[[str, str], JsonValue]) -> None:
        self.calls: list[tuple[str, str, Mapping[str, JsonValue]]] = []
        self._answer = answer

    def __call__(self, path: str, form: str, data: Mapping[str, JsonValue]) -> JsonValue:
        self.calls.append((path, form, data))
        return self._answer(path, form)


def _raise(exc: Exception) -> Callable[[str, str], JsonValue]:
    def answer(_path: str, _form: str) -> JsonValue:
        raise exc

    return answer


def test_endpoint_list_only_uses_read_operations() -> None:
    assert {operation for _, _, operation in READ_ENDPOINTS} <= READ_OPERATIONS
    assert len(set(READ_ENDPOINTS)) == len(READ_ENDPOINTS)


def test_probe_sends_every_endpoint_as_a_read() -> None:
    sender = _ScriptedSender(lambda _path, _form: {"x": 1})
    capabilities = CapabilityService(sender).probe(interval=0)
    assert len(capabilities) == len(READ_ENDPOINTS)
    assert all(c.status == "ok" for c in capabilities)
    sent = [(path, form, data["operation"]) for path, form, data in sender.calls]
    assert sent == list(READ_ENDPOINTS)


def test_probe_waits_between_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr("tplink_deco_api.services.capability_service.time.sleep", sleeps.append)
    CapabilityService(_ScriptedSender(lambda _path, _form: {})).probe(interval=0.5)
    assert sleeps == [0.5] * (len(READ_ENDPOINTS) - 1)


@pytest.mark.parametrize(
    ("answer", "status", "detail"),
    [
        (lambda _p, _f: {}, "empty", ""),
        (lambda _p, _f: [], "empty", ""),
        (lambda _p, _f: None, "empty", ""),
        (lambda _p, _f: [{"value": 7}], "ok", ""),
        (_raise(TransportError("x", status_code=404)), "absent", "HTTP 404"),
        (_raise(TransportError("x", status_code=500)), "error", "HTTP 500"),
        (_raise(TransportError("timed out")), "error", "timed out"),
        (_raise(ApiError(-1)), "error", "error_code=-1"),
        (_raise(CryptoError("bad envelope")), "error", "bad envelope"),
        (_raise(ValueError("not an object")), "error", "not an object"),
    ],
)
def test_probe_classifies_outcomes(
    answer: Callable[[str, str], JsonValue], status: str, detail: str
) -> None:
    first = CapabilityService(_ScriptedSender(answer)).probe(interval=0)[0]
    path, form, operation = READ_ENDPOINTS[0]
    assert first == EndpointCapability(path, form, operation, status, detail)  # type: ignore[arg-type]


def test_probe_lets_authentication_errors_through() -> None:
    service = CapabilityService(_ScriptedSender(_raise(AuthenticationError("not authenticated"))))
    with pytest.raises(AuthenticationError):
        service.probe(interval=0)
