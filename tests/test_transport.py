"""Network-free unit tests for ``HttpTransport``.

``urllib.request.urlopen`` is patched so no socket is ever opened. The tests
exercise the request building, cookie capture and the HTTPError / URLError →
``TransportError`` wrapping at the transport boundary.
"""

from __future__ import annotations

import io
import json
import ssl
import urllib.error
from email.message import Message
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from tplink_deco_api.auth.transport import HttpTransport
from tplink_deco_api.exceptions import TransportError

if TYPE_CHECKING:
    from collections.abc import Iterable


class _FakeResponse:
    """Minimal stand-in for the ``HTTPResponse`` returned by ``urlopen``."""

    def __init__(self, body: bytes, set_cookies: Iterable[str] = ()) -> None:
        self._body = body
        self.headers = Message()
        for cookie in set_cookies:
            self.headers["Set-Cookie"] = cookie

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _patch_urlopen(response_or_exc: object) -> mock._patch[mock.MagicMock]:
    def side_effect(req: object, timeout: float | None = None) -> object:
        if isinstance(response_or_exc, Exception):
            raise response_or_exc
        side_effect.captured_req = req  # type: ignore[attr-defined]
        side_effect.captured_timeout = timeout  # type: ignore[attr-defined]
        return response_or_exc

    return mock.patch("urllib.request.urlopen", side_effect=side_effect)


def test_post_json_serializes_and_parses() -> None:
    resp = _FakeResponse(json.dumps({"result": {"ok": True}}).encode())
    with mock.patch("urllib.request.urlopen", return_value=resp) as patched:
        transport = HttpTransport(timeout=3.0)
        out = transport.post_json("http://192.0.2.1/x", {"operation": "read"})
    assert out == {"result": {"ok": True}}
    req = patched.call_args.args[0]
    assert req.data == json.dumps({"operation": "read"}).encode()
    assert req.headers["Content-type"] == "application/json"
    assert patched.call_args.kwargs["timeout"] == 3.0


def test_post_form_encodes_body() -> None:
    resp = _FakeResponse(b'{"data": "abc"}')
    with mock.patch("urllib.request.urlopen", return_value=resp) as patched:
        transport = HttpTransport()
        out = transport.post_form("http://192.0.2.1/x", "sign=a&data=b")
    assert out == {"data": "abc"}
    assert patched.call_args.args[0].data == b"sign=a&data=b"


def test_cookie_is_captured_and_sent_on_next_request() -> None:
    first = _FakeResponse(b"{}", set_cookies=["sysauth=deadbeef0123; Path=/; HttpOnly"])
    second = _FakeResponse(b"{}")
    with mock.patch("urllib.request.urlopen", side_effect=[first, second]) as patched:
        transport = HttpTransport()
        transport.post_json("http://192.0.2.1/login", {"operation": "read"})
        assert transport._cookie == "sysauth=deadbeef0123"
        transport.post_form("http://192.0.2.1/admin", "sign=a&data=b")
    second_req = patched.call_args_list[1].args[0]
    assert second_req.headers["Cookie"] == "sysauth=deadbeef0123"


def test_cookie_not_captured_when_pattern_absent() -> None:
    resp = _FakeResponse(b"{}", set_cookies=["session=xyz; Path=/"])
    with mock.patch("urllib.request.urlopen", return_value=resp):
        transport = HttpTransport()
        transport.post_json("http://192.0.2.1/login", {"operation": "read"})
    assert transport._cookie is None


def test_no_cookie_header_when_none_captured() -> None:
    resp = _FakeResponse(b"{}")
    with mock.patch("urllib.request.urlopen", return_value=resp) as patched:
        transport = HttpTransport()
        transport.post_json("http://192.0.2.1/login", {"operation": "read"})
    assert "Cookie" not in patched.call_args.args[0].headers


def test_http_error_wrapped_with_status_code() -> None:
    err = urllib.error.HTTPError(
        url="http://192.0.2.1/x",
        code=403,
        msg="Forbidden",
        hdrs=Message(),
        fp=io.BytesIO(b""),
    )
    with mock.patch("urllib.request.urlopen", side_effect=err):
        transport = HttpTransport()
        with pytest.raises(TransportError) as exc:
            transport.post_json("http://192.0.2.1/x", {"operation": "read"})
    assert exc.value.status_code == 403
    assert "HTTP 403" in str(exc.value)


def test_url_error_wrapped_without_status_code() -> None:
    err = urllib.error.URLError("Connection refused")
    with mock.patch("urllib.request.urlopen", side_effect=err):
        transport = HttpTransport()
        with pytest.raises(TransportError) as exc:
            transport.post_form("http://192.0.2.1/x", "sign=a&data=b")
    assert exc.value.status_code is None
    assert "Connection refused" in str(exc.value)


def test_ssl_context_is_unverified() -> None:
    resp = _FakeResponse(b"{}")
    with mock.patch("urllib.request.urlopen", return_value=resp) as patched:
        HttpTransport().post_json("https://192.0.2.1/x", {"operation": "read"})
    ctx = patched.call_args.kwargs.get("context")
    assert ctx is not None
    assert ctx.verify_mode == ssl.CERT_NONE
