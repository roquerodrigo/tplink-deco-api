import hashlib


def md5_session_hash(username: str, password: str) -> str:
    return hashlib.md5((username + password).encode()).hexdigest()
