"""Mutable session state held between requests after a successful login."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.rsa_key import RsaKey
    from ..models.session_keys import SessionKeys


class SessionContext:
    """Holds the RSA keys, AES bundle and stok token after login."""

    def __init__(
        self,
        sign_key: RsaKey,
        pwd_key: RsaKey,
        keys: SessionKeys,
        stok: str = "",
    ) -> None:
        self.sign_key = sign_key
        self.pwd_key = pwd_key
        self.keys = keys
        self.stok = stok

    def is_authenticated(self) -> bool:
        """Return ``True`` once a ``stok`` has been issued."""
        return bool(self.stok)

    def invalidate(self) -> None:
        """Drop the token and reset the sequence counter."""
        self.stok = ""
        self.keys.seq = 0
