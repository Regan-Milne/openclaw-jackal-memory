#!/usr/bin/env python3
"""
Jackal Memory client for OpenClaw agents.

Usage:
  python client.py keygen       — show your current encryption key (or generate one)
  python client.py save <key> <content>
  python client.py load <key>
  python client.py usage        — show storage quota usage

Required env vars:
  JACKAL_MEMORY_API_KEY         — from https://web-production-5cce7.up.railway.app/auth/login

Optional env vars:
  JACKAL_MEMORY_ENCRYPTION_KEY  — AES-256 key (hex). If not set, a key is auto-generated
                                   and saved to ~/.config/jackal-memory/key on first use.
                                   All content is always encrypted — there is no opt-out.

Install:
  pip install requests cryptography
"""

import base64
import os
import pathlib
import sys

import requests

BASE_URL = "https://web-production-5cce7.up.railway.app"

_KEY_FILE = pathlib.Path.home() / ".config" / "jackal-memory" / "key"


# ── Encryption (mandatory) ────────────────────────────────────────────────────

def _encryption_key() -> bytes:
    """
    Return the AES-256 encryption key. Resolution order:
      1. JACKAL_MEMORY_ENCRYPTION_KEY env var
      2. ~/.config/jackal-memory/key file
      3. Auto-generate, save to key file, print one-time notice
    Encryption is always on — there is no opt-out.
    """
    # 1. Env var
    key_hex = os.environ.get("JACKAL_MEMORY_ENCRYPTION_KEY", "").strip()
    if key_hex:
        return bytes.fromhex(key_hex)

    # 2. Key file
    if _KEY_FILE.exists():
        return bytes.fromhex(_KEY_FILE.read_text().strip())

    # 3. Auto-generate and persist
    key_hex = os.urandom(32).hex()
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_text(key_hex)
    print(
        "\n[jackal-memory] Generated a new encryption key and saved it to:\n"
        f"  {_KEY_FILE}\n\n"
        "Your memories are encrypted with this key. Back it up:\n"
        f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n",
        file=sys.stderr,
    )
    return bytes.fromhex(key_hex)


def _encrypt(plaintext: str) -> str:
    """AES-256-GCM encrypt. Returns base64(nonce + ciphertext)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key   = _encryption_key()
    nonce = os.urandom(12)
    ct    = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def _decrypt(ciphertext_b64: str) -> str:
    """AES-256-GCM decrypt. Expects base64(nonce + ciphertext)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key  = _encryption_key()
    data = base64.b64decode(ciphertext_b64)
    nonce, ct = data[:12], data[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()


# ── API ───────────────────────────────────────────────────────────────────────

def _headers() -> dict:
    key = os.environ.get("JACKAL_MEMORY_API_KEY", "")
    if not key:
        print("Error: JACKAL_MEMORY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def cmd_keygen() -> None:
    """Show the active encryption key (generating one if needed)."""
    key = _encryption_key()
    key_hex = key.hex()
    print(f"\nActive encryption key:\n\n  {key_hex}\n")
    print("Set this in your environment to use the same key on other machines:")
    print(f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n")
    print("Keep this key safe — lose it and your encrypted memories are unrecoverable.")


def cmd_save(key: str, content: str) -> None:
    payload = _encrypt(content)
    resp = requests.post(
        f"{BASE_URL}/save",
        json={"key": key, "content": payload},
        headers=_headers(),
    )
    if not resp.ok:
        print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    data = resp.json()
    used_mb  = data.get("bytes_used", 0) / 1024 ** 2
    quota_mb = data.get("quota_bytes", 0) / 1024 ** 2
    print(f"Saved — key: {data['key']}  cid: {data['cid']}  "
          f"used: {used_mb:.1f} MB / {quota_mb:.0f} MB")
    for w in data.get("warnings", []):
        print(f"WARNING: {w['message']}", file=sys.stderr)


def cmd_load(key: str) -> None:
    resp = requests.get(
        f"{BASE_URL}/load/{key}",
        headers=_headers(),
    )
    if resp.status_code == 404:
        print(f"No memory found for key '{key}'", file=sys.stderr)
        sys.exit(1)
    if not resp.ok:
        print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    print(_decrypt(resp.json()["content"]))


def cmd_usage() -> None:
    resp = requests.get(f"{BASE_URL}/usage", headers=_headers())
    resp.raise_for_status()
    data     = resp.json()
    used_mb  = data["bytes_used"] / 1024 ** 2
    quota_mb = data["quota_bytes"] / 1024 ** 2
    pct      = data["percent_used"] * 100
    print(f"Storage: {used_mb:.1f} MB / {quota_mb:.0f} MB ({pct:.1f}% used)")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "keygen" and len(args) == 1:
        cmd_keygen()
    elif cmd == "save" and len(args) == 3:
        cmd_save(args[1], args[2])
    elif cmd == "load" and len(args) == 2:
        cmd_load(args[1])
    elif cmd == "usage" and len(args) == 1:
        cmd_usage()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
