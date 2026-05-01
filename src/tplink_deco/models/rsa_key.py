from dataclasses import dataclass


@dataclass(frozen=True)
class RsaKey:
    n: int
    e: int

    @classmethod
    def from_hex(cls, modulus_hex: str, exponent_hex: str) -> "RsaKey":
        return cls(n=int(modulus_hex, 16), e=int(exponent_hex, 16))
