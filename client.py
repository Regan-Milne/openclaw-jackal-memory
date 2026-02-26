#!/usr/bin/env python3
"""
Jackal Memory client for OpenClaw agents.

Usage:
  python client.py provision <jackal_address>
  python client.py save <key> <content>
  python client.py load <key>

Requires:
  JACKAL_MEMORY_API_KEY environment variable
  pip install requests
"""

import os
import sys

import requests

BASE_URL = "https://web-production-5cce7.up.railway.app"


def _headers() -> dict:
    key = os.environ.get("JACKAL_MEMORY_API_KEY", "")
    if not key:
        print("Error: JACKAL_MEMORY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


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
    resp = requests.post(
        f"{BASE_URL}/save",
        json={"key": key, "content": content},
        headers=_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"Saved — key: {data['key']}  cid: {data['cid']}")


def cmd_load(key: str) -> None:
    resp = requests.get(
        f"{BASE_URL}/load/{key}",
        headers=_headers(),
    )
    if resp.status_code == 404:
        print(f"No memory found for key '{key}'", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    print(resp.json()["content"])


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "provision" and len(args) == 2:
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
