# Security Policy — Jackal Memory

This document describes the security model for the `jackal-memory` OpenClaw skill for ClawHub review purposes.

---

## What this skill can do

- **Read memory blobs** stored under the authenticated agent's namespace via `GET /load/{key}`
- **Write memory blobs** to the authenticated agent's namespace via `POST /save`
- **Provision decentralized storage** on Jackal Protocol for a given Jackal address via `POST /provision`
- **Make outbound HTTPS requests** to `https://web-production-5cce7.up.railway.app` only

All actions are scoped to the API key provided — one key cannot access another agent's data.

---

## What this skill cannot do

- **Access other agents' memory** — all storage is namespaced per API key; keys are not shared
- **Execute arbitrary code** — the skill is a thin HTTP client; it calls a fixed API, nothing else
- **Read or write local files** — `client.py` makes no filesystem calls beyond what Python requires to run
- **Access environment variables beyond `JACKAL_MEMORY_API_KEY`** — no other env vars are read
- **Phone home to any domain other than `web-production-5cce7.up.railway.app`** — no analytics, no telemetry, no third-party calls
- **Store or transmit private keys** — the agent's Jackal private key never leaves the agent's machine; only the public Jackal address (`jkl1...`) is sent to the API

---

## Key handling

### JACKAL_MEMORY_API_KEY

- Issued via Google OAuth at `https://web-production-5cce7.up.railway.app/auth/login`
- One key per Google account — re-authenticating returns the same key
- The key is a 32-byte URL-safe random token (`secrets.token_urlsafe(32)`)
- Stored server-side in a SQLite database (Railway-hosted), hashed lookup
- **Never logged, never echoed in API responses, never committed to this repo**
- If compromised: re-authenticate to retrieve the same key, or contact the operator to rotate

### Jackal wallet private key

- Generated locally by the agent — **the server never sees it**
- Only the public Jackal address (`jkl1...`) is transmitted to `/provision`
- The operator has no ability to recover or access agent wallet keys
- Agents are responsible for their own key custody

### Backend operator wallet

- A separate wallet (`jkl1ya7h0k3xf9t2rmyla33puqzp7xkzp7l02zncl3`) is used by the API to sign `MsgBuyStorage` transactions on behalf of users
- This wallet pays for storage provisioning and receives the Jackal Protocol referral fee
- User funds are not held or controlled by this wallet

---

## Network surface

This skill makes outbound requests to exactly one endpoint:

```
https://web-production-5cce7.up.railway.app
```

Endpoints used:

| Endpoint | Method | Purpose |
|---|---|---|
| `/provision` | POST | Provisions Jackal storage for a Jackal address |
| `/save` | POST | Writes a memory blob |
| `/load/{key}` | GET | Reads a memory blob |

No other domains are contacted. No DNS lookups beyond the above. No CDN, analytics, or tracking.

---

## Data storage

- Memory blobs are stored on **Jackal Protocol** decentralized storage, not on a central server
- The hosted API stores only: Google account ID, email address, API key, and optionally the agent's Jackal address
- No memory content passes through or is retained by the hosted API — content goes directly to Jackal
- Users may delete their account by contacting the operator

---

## Responsible disclosure

To report a security issue, open a private GitHub advisory on this repository or contact the maintainer directly via the repository profile.

---

## Operator

Maintained by [@Regan-Milne](https://github.com/Regan-Milne). Jackal storage is provided via [Jackal Protocol](https://jackalprotocol.com).
