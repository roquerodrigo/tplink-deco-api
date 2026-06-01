"""Unit tests for the AES / RSA / MD5 primitives."""

from __future__ import annotations

import hashlib
from base64 import b64decode

import pytest

from tplink_deco_api.crypto import (
    aes_decrypt,
    aes_encrypt,
    generate_aes_pair,
    md5_session_hash,
    rsa_encrypt,
)
from tplink_deco_api.exceptions import CryptoError


def test_generate_aes_pair_lengths() -> None:
    key, iv = generate_aes_pair()
    assert len(key) == 16
    assert len(iv) == 16


def test_generate_aes_pair_numeric() -> None:
    key, iv = generate_aes_pair()
    assert key.isdigit()
    assert iv.isdigit()


def test_generate_aes_pair_random() -> None:
    pairs = {generate_aes_pair() for _ in range(20)}
    assert len(pairs) > 1


def test_md5_session_hash() -> None:
    expected = hashlib.md5(b"adminpassword").hexdigest()
    assert md5_session_hash("admin", "password") == expected


def test_md5_session_hash_empty() -> None:
    expected = hashlib.md5(b"admin").hexdigest()
    assert md5_session_hash("admin", "") == expected


def test_aes_roundtrip() -> None:
    key, iv = "1234567890123456", "6543210987654321"
    plain = '{"operation":"login","username":"admin","password":"secret"}'
    assert aes_decrypt(key, iv, aes_encrypt(key, iv, plain)) == plain


def test_aes_encrypt_returns_base64() -> None:
    key, iv = "1234567890123456", "6543210987654321"
    result = aes_encrypt(key, iv, "hello")
    b64decode(result)


def test_aes_decrypt_bad_input() -> None:
    with pytest.raises(CryptoError):
        aes_decrypt("1234567890123456", "6543210987654321", "not-valid-base64!!!")


_SIGN_N = int(
    "DE1E5BD8347A6BED75ED9E96190B47FDCE5696B49A542F908003D01DD3CBF59B"
    "9A76F42A68048D85B1E3AFC78CD23191AA26CD69E5932D4CA02F35687071F65F",
    16,
)
_SIGN_E = 0x10001


def test_rsa_encrypt_short_message() -> None:
    msg = b"h=abc123&s=12345"
    result = rsa_encrypt(_SIGN_N, _SIGN_E, msg)
    assert isinstance(result, str)
    assert len(result) == 128


def test_rsa_encrypt_long_message_splits() -> None:
    msg = ("k=1234567890123456&i=6543210987654321&h=" + "a" * 32 + "&s=999999999").encode()
    result = rsa_encrypt(_SIGN_N, _SIGN_E, msg)
    assert len(result) == 256


def test_rsa_encrypt_deterministic_length() -> None:
    msg = b"h=abc&s=123"
    results = {rsa_encrypt(_SIGN_N, _SIGN_E, msg) for _ in range(5)}
    lengths = {len(r) for r in results}
    assert lengths == {128}


def test_rsa_encrypt_block_rejects_oversized_block() -> None:
    from tplink_deco_api.crypto.rsa import _encrypt_block

    with pytest.raises(CryptoError, match=r"length .* >"):
        _encrypt_block(_SIGN_N, _SIGN_E, k=16, block=b"x" * 16)
