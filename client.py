#!/usr/bin/env python3
"""
Jackal Memory client for OpenClaw agents.

Usage:
  python client.py keygen                  — generate an encryption key
  python client.py provision <jackal_address>
  python client.py save <key> <content>
  python client.py load <key>

Required env vars:
  JACKAL_MEMORY_API_KEY       — from https://web-production-5cce7.up.railway.app/auth/login

Optional env vars:
  JACKAL_MEMORY_ENCRYPTION_KEY — AES-256 key (hex). If set, all content is encrypted
                                  client-side before leaving your machine. The server
                                  and Jackal storage never see plaintext.
                                  Generate with: python client.py keygen

Install:
  pip install requests cryptography
"""

import base64
import os
import sys

import requests

BASE_URL = "https://web-production-5cce7.up.railway.app"


# ── Encryption ────────────────────────────────────────────────────────────────

def _encryption_key() -> bytes | None:
    key_hex = os.environ.get("JACKAL_MEMORY_ENCRYPTION_KEY", "")
    if not key_hex:
        return None
    return bytes.fromhex(key_hex)


def _encrypt(plaintext: str) -> str:
    """AES-256-GCM encrypt. Returns base64(nonce + ciphertext)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = _encryption_key()
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def _decrypt(ciphertext_b64: str) -> str:
    """AES-256-GCM decrypt. Expects base64(nonce + ciphertext)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = _encryption_key()
    data = base64.b64decode(ciphertext_b64)
    nonce, ct = data[:12], data[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()


def _maybe_encrypt(content: str) -> str:
    return _encrypt(content) if _encryption_key() else content


def _maybe_decrypt(content: str) -> str:
    if not _encryption_key():
        return content
    try:
        return _decrypt(content)
    except Exception:
        # Content was stored unencrypted — return as-is
        return content


# ── API ───────────────────────────────────────────────────────────────────────

def _headers() -> dict:
    key = os.environ.get("JACKAL_MEMORY_API_KEY", "")
    if not key:
        print("Error: JACKAL_MEMORY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def cmd_keygen() -> None:
    """Generate a new AES-256 encryption key."""
    key_hex = os.urandom(32).hex()
    print(f"\nGenerated encryption key:\n\n  {key_hex}\n")
    print("Add to your environment:")
    print(f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n")
    print("Keep this key safe — lose it and your encrypted memories are unrecoverable.")


def cmd_provision(jackal_address: str) -> None:
    resp = requests.post(
        f"{BASE_URL}/provision",
        json={"jackal_address": jackal_address},
        headers=_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"Provisioned — address: {data['jackal_address']}  tx: {data['tx_hash']}")


def cmd_save(key: str, content: str) -> None:
    payload = _maybe_encrypt(content)
    resp = requests.post(
        f"{BASE_URL}/save",
        json={"key": key, "content": payload},
        headers=_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    encrypted = _encryption_key() is not None
    print(f"Saved — key: {data['key']}  cid: {data['cid']}  encrypted: {encrypted}")


def cmd_load(key: str) -> None:
    resp = requests.get(
        f"{BASE_URL}/load/{key}",
        headers=_headers(),
    )
    if resp.status_code == 404:
        print(f"No memory found for key '{key}'", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    print(_maybe_decrypt(resp.json()["content"]))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "keygen" and len(args) == 1:
        cmd_keygen()
    elif cmd == "provision" and len(args) == 2:
        cmd_provision(args[1])
    elif cmd == "save" and len(args) == 3:
        cmd_save(args[1], args[2])
    elif cmd == "load" and len(args) == 2:
        cmd_load(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
