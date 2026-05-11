from ..models.rsa_key import RsaKey
from ..models.session_keys import SessionKeys


class SessionContext:
    def __init__(
        self,
        sign_key: RsaKey,
        pwd_key: RsaKey,
        keys: SessionKeys,
        stok: str = "",
    ):
        self.sign_key = sign_key
        self.pwd_key = pwd_key
        self.keys = keys
        self.stok = stok

    def is_authenticated(self) -> bool:
        return bool(self.stok)

    def increment_seq(self) -> None:
        self.keys.seq += 1

    def invalidate(self) -> None:
        self.stok = ""
        self.keys.seq = 0
