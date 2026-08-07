"""RSA PKCS#1 v1.5 encryption used for the request signature and password."""

from __future__ import annotations

import math
import secrets

from ..exceptions.crypto import CryptoError


def rsa_encrypt(n: int, e: int, plaintext: bytes) -> str:
    """Encrypt ``plaintext`` with RSA PKCS#1 v1.5, splitting into blocks as needed."""
    block_size = (int(math.log2(n)) + 8) >> 3
    bytes_per_block = block_size - 11
    result = ""
    for i in range(0, len(plaintext), bytes_per_block):
        result += _encrypt_block(n, e, block_size, plaintext[i : i + bytes_per_block])
    return result


def _encrypt_block(n: int, e: int, k: int, block: bytes) -> str:
    if len(block) > k - 11:
        message = f"Failed to encrypt RSA block: length {len(block)} > {k - 11}"
        raise CryptoError(message)
    pad_len = k - len(block) - 3
    pad = b""
    while len(pad) < pad_len:
        byte = secrets.token_bytes(1)
        if byte != b"\x00":
            pad += byte
    em = b"\x00\x02" + pad + b"\x00" + block
    ct = pow(int.from_bytes(em, "big"), e, n)
    return format(ct, f"0{k * 2}x")
