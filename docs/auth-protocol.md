# TP-Link Deco — Authentication Protocol

Documentation of the proprietary HTTP protocol used by the TP-Link Deco web
UI, as implemented by this SDK and validated against real Deco hardware.

> This page is the crypto/handshake deep-dive. For the request/response
> contract around the envelope see
> [`protocol/transport-and-dispatch.md`](./protocol/transport-and-dispatch.md),
> and for the **complete** endpoint catalogue (every controller, form and
> operation) see the [endpoint index](./endpoints/README.md). Start at
> [`README.md`](./README.md).

---

## Overview

All communication uses `POST` with `Content-Type: application/json` against:

```
https://<router-ip>/cgi-bin/luci/;stok=<TOKEN>/<endpoint>?form=<form>
```

Modern firmware serves HTTPS with a self-signed certificate, so the SDK
disables certificate verification. `stok` is empty before login (`/;stok=/`)
and populated afterwards.

Authenticated requests carry an **AES-128-CBC** encrypted payload signed with
**RSA PKCS#1 v1.5** — except for the endpoints listed under
[Plaintext endpoints](#plaintext-endpoints). Despite the JSON content type,
the encrypted envelope is sent as a form-style body:

```
sign=<hex RSA signature>&data=<URL-encoded base64 ciphertext>
```

---

## Login flow

### Step 1 — Fetch RSA keys

Two calls in parallel, both unencrypted:

#### `POST /login?form=auth`

```json
{ "operation": "read" }
```

Response:
```json
{
  "result": {
    "key": ["<modulus_hex>", "010001"],
    "seq": 766218342
  },
  "error_code": 0
}
```

- **512-bit RSA key** used to sign the `sign` field on every request.
- **`seq`** is a session nonce folded into every signature as
  `seq + len(data_b64)`. The official web client increments it after each
  request, but the firmware keeps accepting the handshake value — the SDK
  reuses it unchanged for the whole session.

#### `POST /login?form=keys`

```json
{ "operation": "read" }
```

Response:
```json
{
  "result": {
    "username": "",
    "password": ["<modulus_hex>", "010001"]
  },
  "error_code": 0
}
```

- **1024-bit RSA key** used to encrypt the password inside the login payload.

---

### Step 2 — Prepare the encryptor

```python
import secrets, hashlib

# AES key: two 16-digit numeric strings
aes_key = "".join(secrets.choice("0123456789") for _ in range(16))
aes_iv  = "".join(secrets.choice("0123456789") for _ in range(16))

# AES key identifier (used inside the signature)
aes_key_str = f"k={aes_key}&i={aes_iv}"
# e.g. "k=1415950173028918&i=5652578606663031"

# Session hash: MD5 of the username concatenated with the password
session_hash = hashlib.md5((username + password).encode()).hexdigest()
```

---

### Step 3 — Send the login request

#### Build the payload

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from base64 import b64encode
import json, secrets

def aes_encrypt(key: str, iv: str, plaintext: str) -> str:
    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key.encode()), modes.CBC(iv.encode()))
    enc = cipher.encryptor()
    return b64encode(enc.update(padded) + enc.finalize()).decode()

def rsa_pkcs1v15_encrypt(n: int, e: int, message: bytes) -> str:
    """RSA PKCS#1 v1.5 — one block, returned as fixed-width lowercase hex."""
    k = (n.bit_length() + 7) // 8
    pad_len = k - len(message) - 3
    pad = b""
    while len(pad) < pad_len:
        b = secrets.token_bytes(1)
        if b != b"\x00":
            pad += b
    em = b"\x00\x02" + pad + b"\x00" + message
    ct = pow(int.from_bytes(em, "big"), e, n)
    return format(ct, f"0{k * 2}x")

def rsa_encrypt(n: int, e: int, plaintext: bytes) -> str:
    """Split into (k - 11)-byte blocks — 53 bytes for the 512-bit sign key."""
    k = (n.bit_length() + 7) // 8
    step = k - 11
    return "".join(
        rsa_pkcs1v15_encrypt(n, e, plaintext[i : i + step])
        for i in range(0, len(plaintext), step)
    )

# Login data (AES-encrypted). The password travels RSA-encrypted with the
# 1024-bit key from /login?form=keys; no username field is sent.
login_data = json.dumps({
    "operation": "login",
    "params": {"password": rsa_encrypt(pwd_rsa_n, pwd_rsa_e, password.encode())},
})
data_b64 = aes_encrypt(aes_key, aes_iv, login_data)

# String to sign: AES key pair + session hash + seq bound to the payload length
sig_str = f"{aes_key_str}&h={session_hash}&s={seq + len(data_b64)}"

body = f"sign={rsa_encrypt(sign_rsa_n, sign_rsa_e, sig_str.encode())}&data={quote_plus(data_b64)}"
```

#### `POST /login?form=login`

```
sign=<hex RSA-512 blocks of sig_str>&data=<URL-encoded base64 AES-CBC-PKCS7(login_data_json)>
```

Response (on success):
```json
{
  "result": {
    "stok":    "abc123...",
    "usrLvl":  1
  },
  "error_code": 0
}
```

---

## Authenticated requests

After login, every call reuses the same envelope — the signature keeps
carrying the AES key pair, and `seq` stays at the handshake value:

```python
data_b64 = aes_encrypt(aes_key, aes_iv, json.dumps(request_data))
sig_str = f"{aes_key_str}&h={session_hash}&s={seq + len(data_b64)}"

body = f"sign={rsa_encrypt(sign_rsa_n, sign_rsa_e, sig_str.encode())}&data={quote_plus(data_b64)}"
```

URL:
```
POST https://<ip>/cgi-bin/luci/;stok=<TOKEN>/admin/<endpoint>?form=<form>
```

---

## Crypto parameters

| Parameter | Value |
|-----------|-------|
| AES mode | CBC |
| AES padding | PKCS7 |
| AES key size | 128-bit (16 numeric chars) |
| RSA (sign) | 512-bit, PKCS#1 v1.5 |
| RSA (pwd) | 1024-bit, PKCS#1 v1.5 |
| RSA split | modulus length − 11 bytes per block (53 bytes for the sign key) |
| Session hash | MD5(username + password) |
| `seq` | handshake value, reused unchanged on every request |

---

## Plaintext endpoints

These endpoints accept plain JSON (no `sign` / `data`):

| Endpoint | Description |
|----------|-------------|
| `/login?form=auth` | RSA sign key + initial seq |
| `/login?form=keys` | RSA password key |
| `/login?form=check_factory_default` | Check whether the router is in factory state |
| `/login?form=default_info` | Factory default SSID and password |
| `/admin/system?form=envar` | Environment variables |
| `/admin/system?form=sysmode` | System mode |
| `/admin/cloud?form=firmware` | Cloud firmware info |
| `/admin/isp?form=isp_upgrade` | ISP-driven upgrade |
| `/admin/firmware?form=config_multipart` | Firmware config (multipart) |
| `/admin/log_export?form=save_log` | Log export |

---

## Authenticated endpoints (sample)

> A small sample. The full catalogue — every controller, form and operation —
> is in [`endpoints/README.md`](./endpoints/README.md).

| Endpoint | Description |
|----------|-------------|
| `/admin/device?form=mode` | Device operating mode |
| `/admin/wireless?form=wlan` | Wi-Fi configuration |
| `/admin/web?form=extra_component_info` | Extra component info |
| `/admin/component_control?form=switch_list` | Switch list |
