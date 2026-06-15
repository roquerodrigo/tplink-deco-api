"""Payload encoding / decoding for the Deco auth protocol."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

from .._json import JsonObject, JsonValue, get_int, get_object
from ..crypto.aes import aes_decrypt, aes_encrypt
from ..crypto.rsa import rsa_encrypt
from ..exceptions.api import ApiError

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..models.rsa_key import RsaKey
    from ..models.session_keys import SessionKeys


def build_payload(
    keys: SessionKeys,
    sign_key: RsaKey,
    data: Mapping[str, JsonValue],
) -> str:
    """Encrypt + sign ``data`` and return the URL-encoded form body."""
    data_b64 = _encode_data(keys, data)
    sign = _encode_sign(keys, sign_key, len(data_b64))
    return f"sign={sign}&data={quote_plus(data_b64)}"


def parse_response(raw: JsonObject, keys: SessionKeys) -> JsonObject:
    """Decrypt the ``data`` field and return its ``result`` mapping."""
    data_b64 = raw.get("data")
    if not isinstance(data_b64, str) or not data_b64:
        raise ApiError(-1)
    decrypted_text = aes_decrypt(keys.aes_key, keys.aes_iv, data_b64)
    decoded = json.loads(decrypted_text)
    if not isinstance(decoded, dict):
        raise ApiError(-1)
    decrypted: JsonObject = decoded
    _check_error(decrypted)
    return get_object(decrypted, "result")


def parse_plain_response(raw: JsonObject) -> JsonObject:
    """Return the ``result`` mapping of an un-encrypted response."""
    _check_error(raw)
    return get_object(raw, "result")


def parse_list_response(raw: JsonObject, keys: SessionKeys) -> list[JsonObject]:
    """Decrypt the ``data`` field and return its ``result`` as a list of objects."""
    data_b64 = raw.get("data")
    if not isinstance(data_b64, str) or not data_b64:
        raise ApiError(-1)
    decrypted_text = aes_decrypt(keys.aes_key, keys.aes_iv, data_b64)
    decoded = json.loads(decrypted_text)
    if not isinstance(decoded, dict):
        raise ApiError(-1)
    decrypted: JsonObject = decoded
    _check_error(decrypted)
    result = decrypted.get("result")
    if not isinstance(result, list):
        return []
    return [item for item in result if isinstance(item, dict)]


def _encode_data(keys: SessionKeys, data: Mapping[str, JsonValue]) -> str:
    return aes_encrypt(
        keys.aes_key,
        keys.aes_iv,
        json.dumps(data, separators=(",", ":")),
    )


def _encode_sign(keys: SessionKeys, sign_key: RsaKey, data_len: int) -> str:
    seq_with_len = keys.seq + data_len
    sig_str = f"k={keys.aes_key}&i={keys.aes_iv}&h={keys.session_hash}&s={seq_with_len}"
    return rsa_encrypt(sign_key.n, sign_key.e, sig_str.encode())


def _check_error(response: JsonObject) -> None:
    code = get_int(response, "error_code") or get_int(response, "errorcode")
    if code:
        raise ApiError(code)
