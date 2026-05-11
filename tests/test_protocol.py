import json
import re
from urllib.parse import unquote_plus

import pytest

from tplink_deco_api import ApiError
from tplink_deco_api.crypto import aes_encrypt, aes_decrypt
from tplink_deco_api.models.rsa_key import RsaKey
from tplink_deco_api.models.session_keys import SessionKeys
from tplink_deco_api.auth.protocol import (
    build_payload,
    parse_plain_response,
    parse_response,
)

_SIGN_N = int(
    "DE1E5BD8347A6BED75ED9E96190B47FDCE5696B49A542F908003D01DD3CBF59B"
    "9A76F42A68048D85B1E3AFC78CD23191AA26CD69E5932D4CA02F35687071F65F",
    16,
)
_KEY = RsaKey(n=_SIGN_N, e=0x10001)
_SESS = SessionKeys(
    aes_key="1234567890123456",
    aes_iv="6543210987654321",
    session_hash="a" * 32,
    seq=1000,
)


# ── build_payload ─────────────────────────────────────────────────────────────


def test_payload_is_form_encoded_string():
    result = build_payload(_SESS, _KEY, {"operation": "read"})
    assert isinstance(result, str)
    assert result.startswith("sign=")
    assert "&data=" in result


def test_payload_data_is_url_encoded_base64():
    result = build_payload(_SESS, _KEY, {"operation": "read"})
    data_b64 = unquote_plus(re.search(r"&data=(.+)$", result).group(1))
    # deve ser base64 válido e decifrar sem erro
    decrypted = aes_decrypt(_SESS.aes_key, _SESS.aes_iv, data_b64)
    assert json.loads(decrypted) == {"operation": "read"}


def test_payload_sign_always_includes_aes_key():
    # sign é RSA-cifrado, tamanho indica split em 2 blocos (sig_str tem k= e i=)
    result = build_payload(_SESS, _KEY, {"operation": "read"})
    sign = re.search(r"^sign=([^&]+)", result).group(1)
    assert len(sign) == 256  # 2 × 128 hex chars


def test_payload_uses_compact_json():
    # Sem espaços no JSON → comprimento mínimo
    result = build_payload(_SESS, _KEY, {"operation": "read"})
    data_b64 = unquote_plus(re.search(r"&data=(.+)$", result).group(1))
    raw_json = aes_decrypt(_SESS.aes_key, _SESS.aes_iv, data_b64)
    assert " " not in raw_json


# ── parse_response ────────────────────────────────────────────────────────────


def test_parse_response_ok():
    inner = {"result": {"stok": "abc"}, "error_code": 0}
    data_b64 = aes_encrypt(_SESS.aes_key, _SESS.aes_iv, json.dumps(inner))
    assert parse_response({"data": data_b64}, _SESS) == {"stok": "abc"}


def test_parse_response_empty_data():
    with pytest.raises(ApiError):
        parse_response({"data": ""}, _SESS)


def test_parse_response_missing_data():
    with pytest.raises(ApiError):
        parse_response({}, _SESS)


def test_parse_response_error_code():
    inner = {"result": {}, "error_code": -5002}
    data_b64 = aes_encrypt(_SESS.aes_key, _SESS.aes_iv, json.dumps(inner))
    with pytest.raises(ApiError) as exc:
        parse_response({"data": data_b64}, _SESS)
    assert exc.value.error_code == -5002


# ── parse_plain_response ──────────────────────────────────────────────────────


def test_parse_plain_ok():
    assert parse_plain_response({"result": {"seq": 1}, "error_code": 0}) == {"seq": 1}


def test_parse_plain_error():
    with pytest.raises(ApiError):
        parse_plain_response({"error_code": -1})
