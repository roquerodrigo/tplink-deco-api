"""AES-128-CBC primitives used to encrypt request payloads."""

from __future__ import annotations

import secrets
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..exceptions.crypto import CryptoError

_KEY_DIGITS = 16
_KEY_MIN = 10 ** (_KEY_DIGITS - 1)
_KEY_MAX = (10**_KEY_DIGITS) - 1


def generate_aes_pair() -> tuple[str, str]:
    """Return a fresh ``(key, iv)`` pair of 16 numeric digits each."""
    key = str(secrets.randbelow(_KEY_MAX - _KEY_MIN) + _KEY_MIN)
    iv = str(secrets.randbelow(_KEY_MAX - _KEY_MIN) + _KEY_MIN)
    return key, iv


def aes_encrypt(key: str, iv: str, plaintext: str) -> str:
    """Encrypt ``plaintext`` with AES-128-CBC + PKCS7, returning base64."""
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()))
    enc = cipher.encryptor()
    return b64encode(enc.update(padded) + enc.finalize()).decode()


def aes_decrypt(key: str, iv: str, ciphertext_b64: str) -> str:
    """Decrypt base64 AES-128-CBC ciphertext, returning the plaintext string."""
    try:
        ct = b64decode(ciphertext_b64)
        cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()))
        dec = cipher.decryptor()
        padded = dec.update(ct) + dec.finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        raw = unpadder.update(padded) + unpadder.finalize()
        return raw.decode()
    except Exception as exc:
        raise CryptoError(f"Failed to decrypt AES payload: {exc}") from exc
