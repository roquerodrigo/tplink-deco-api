import secrets
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..exceptions.crypto import CryptoError

_KEY_DIGITS = 16
_KEY_MIN = 10 ** (_KEY_DIGITS - 1)
_KEY_MAX = (10**_KEY_DIGITS) - 1


def generate_aes_pair() -> tuple[str, str]:
    key = str(secrets.randbelow(_KEY_MAX - _KEY_MIN) + _KEY_MIN)
    iv = str(secrets.randbelow(_KEY_MAX - _KEY_MIN) + _KEY_MIN)
    return key, iv


def aes_encrypt(key: str, iv: str, plaintext: str) -> str:
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()))
    enc = cipher.encryptor()
    return b64encode(enc.update(padded) + enc.finalize()).decode()


def aes_decrypt(key: str, iv: str, ciphertext_b64: str) -> str:
    try:
        ct = b64decode(ciphertext_b64)
        cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()))
        dec = cipher.decryptor()
        raw = dec.update(ct) + dec.finalize()
        n_pad = raw[-1]
        return raw[:-n_pad].decode()
    except Exception as exc:
        raise CryptoError(f"Falha ao decifrar AES: {exc}") from exc
