from dataclasses import dataclass


@dataclass(frozen=True)
class LoginResult:
    stok:    str
    usr_lvl: int = 1
