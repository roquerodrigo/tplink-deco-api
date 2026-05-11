import json
from typing import Any
from urllib.parse import quote_plus

from ..crypto.aes import aes_decrypt, aes_encrypt
from ..crypto.rsa import rsa_encrypt
from ..exceptions.api import ApiError
from ..models.rsa_key import RsaKey
from ..models.session_keys import SessionKeys


def build_payload(keys: SessionKeys, sign_key: RsaKey, data: dict[str, Any]) -> str:
    data_b64 = _encode_data(keys, data)
    sign = _encode_sign(keys, sign_key, len(data_b64))
    return f"sign={sign}&data={quote_plus(data_b64)}"


def parse_response(raw: dict[str, Any], keys: SessionKeys) -> dict[str, Any]:
    data_b64 = raw.get("data", "")
    if not data_b64:
        raise ApiError(-1)
    decrypted = json.loads(aes_decrypt(keys.aes_key, keys.aes_iv, data_b64))
    _check_error(decrypted)
    return decrypted.get("result", {})


def parse_plain_response(raw: dict[str, Any]) -> dict[str, Any]:
    _check_error(raw)
    return raw.get("result", {})


def _encode_data(keys: SessionKeys, data: dict[str, Any]) -> str:
    return aes_encrypt(
        keys.aes_key, keys.aes_iv, json.dumps(data, separators=(",", ":"))
    )


def _encode_sign(keys: SessionKeys, sign_key: RsaKey, data_len: int) -> str:
    seq_with_len = keys.seq + data_len
    sig_str = f"k={keys.aes_key}&i={keys.aes_iv}&h={keys.session_hash}&s={seq_with_len}"
    return rsa_encrypt(sign_key.n, sign_key.e, sig_str.encode())


def _check_error(response: dict[str, Any]) -> None:
    code = response.get("error_code") or response.get("errorcode")
    if code and code != 0:
        raise ApiError(int(code))
