from dataclasses import dataclass


@dataclass
class SessionKeys:
    aes_key: str
    aes_iv: str
    session_hash: str
    seq: int
