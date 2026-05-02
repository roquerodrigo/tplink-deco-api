from base64 import b64decode


def decode_b64(value: str) -> str:
    if not value:
        return value
    return b64decode(value).decode()


def normalize_mac(value: str) -> str:
    return value.replace("-", ":").upper()
