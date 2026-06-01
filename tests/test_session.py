"""Unit tests for ``SessionContext`` state transitions."""

from __future__ import annotations

from tplink_deco_api.auth.session import SessionContext
from tplink_deco_api.models.rsa_key import RsaKey
from tplink_deco_api.models.session_keys import SessionKeys


def _make_session(stok: str = "") -> SessionContext:
    keys = SessionKeys(
        aes_key="1234567890123456",
        aes_iv="6543210987654321",
        session_hash="a" * 32,
        seq=10,
    )
    key = RsaKey(n=123, e=0x10001)
    return SessionContext(sign_key=key, pwd_key=key, keys=keys, stok=stok)


def test_not_authenticated_without_stok() -> None:
    assert not _make_session().is_authenticated()


def test_authenticated_with_stok() -> None:
    assert _make_session(stok="tok").is_authenticated()


def test_increment_seq_bumps_counter() -> None:
    session = _make_session()
    session.increment_seq()
    session.increment_seq()
    assert session.keys.seq == 12


def test_invalidate_clears_stok_and_resets_seq() -> None:
    session = _make_session(stok="tok")
    session.keys.seq = 99
    session.invalidate()
    assert session.stok == ""
    assert session.keys.seq == 0
    assert not session.is_authenticated()


def test_default_stok_is_empty() -> None:
    keys = SessionKeys(aes_key="k", aes_iv="i", session_hash="h", seq=0)
    key = RsaKey(n=1, e=1)
    session = SessionContext(sign_key=key, pwd_key=key, keys=keys)
    assert session.stok == ""
