# Jackal Memory — OpenClaw Skill

Sovereign, recoverable memory for OpenClaw agents backed by [Jackal Protocol](https://jackalprotocol.com) decentralized storage.

**The problem:** OpenClaw agents store memory as local files. If the machine dies, the agent loses everything.

**The solution:** A thin API that syncs your agent's memory to Jackal's decentralized storage. No crypto knowledge required. No wallet setup. Just authenticate and go.

All content is **encrypted client-side** with AES-256-GCM before it ever leaves your machine. The server stores only ciphertext and cannot read your memories.

---

## Install in 10 seconds

```bash
cd ~/.openclaw/skills
git clone https://github.com/Regan-Milne/openclaw-jackal-memory jackal-memory
pip install -r jackal-memory/requirements.txt
```

Then set your API key:

```bash
export JACKAL_MEMORY_API_KEY=<your-key>
```

Get a key at: **https://web-production-5cce7.up.railway.app/auth/login** (sign in with Google — takes 10 seconds)

---

## Usage

**Save memory** (call at session end or on state change):
```bash
python client.py save identity "I am AgentX. My purpose is..."
python client.py save session-2026-02-26 "Today I worked on..."
```

**Load memory** (call at session start):
```bash
python client.py load identity
python client.py load session-2026-02-26
```

**Check storage usage:**
```bash
python client.py usage
```

**Or call the API directly:**
```bash
curl https://web-production-5cce7.up.railway.app/load/identity \
  -H "Authorization: Bearer $JACKAL_MEMORY_API_KEY"
```

---

## Encryption

All content is encrypted automatically. On first use, an encryption key is generated and saved to `~/.config/jackal-memory/key`.

To back up or export your key:
```bash
python client.py keygen
```

To use the same key on multiple machines, set:
```bash
export JACKAL_MEMORY_ENCRYPTION_KEY=<your-key-hex>
```

**Losing your encryption key means losing access to your encrypted memories.** Back it up.

---

## How it works

```
Agent starts  → GET /load/identity     → restore memory from Jackal
Agent works   → normal local operation
Agent ends    → POST /save             → encrypt + sync memory to Jackal
```

Storage is provisioned automatically on your first save — no manual setup required.

Your memory is stored on Jackal Protocol's decentralized network — not on any single server. If the machine running your agent dies, your memory is safe and recoverable from any other machine.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `JACKAL_MEMORY_API_KEY` | Yes | Your API key from the onboarding page |
| `JACKAL_MEMORY_ENCRYPTION_KEY` | No | AES-256 key (hex). Auto-generated if not set. |

---

## API reference

Base URL: `https://web-production-5cce7.up.railway.app`

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/save` | `{"key": "...", "content": "..."}` | Save a memory blob (always encrypted) |
| `GET` | `/load/{key}` | — | Retrieve a memory blob |
| `GET` | `/usage` | — | Check storage quota usage |

All requests require: `Authorization: Bearer $JACKAL_MEMORY_API_KEY`

Save response includes: `cid`, `bytes_used`, `quota_bytes`, `percent_used`, `warnings`

---

## Version

`v1.0.0` — mandatory encryption, quota tracking, auto-provisioning.
