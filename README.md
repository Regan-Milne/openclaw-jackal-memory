# Jackal Memory — OpenClaw Skill

Sovereign, recoverable memory for OpenClaw agents backed by [Jackal Protocol](https://jackalprotocol.com) decentralized storage.

**The problem:** OpenClaw agents store memory as local files. If the machine dies, the agent loses everything.

**The solution:** A thin API that syncs your agent's memory to Jackal's decentralized storage. No crypto knowledge required. No wallet setup. Just authenticate and go.

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

## First run — provision your storage

Your agent needs a Jackal address to store data against. Generate one (or use your existing `jkl1...` address) and run:

```bash
python ~/.openclaw/skills/jackal-memory/client.py provision jkl1youraddresshere
```

This provisions 5GB of decentralized storage linked to your agent. Free for 1 year.

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

**Or call the API directly:**
```bash
curl https://web-production-5cce7.up.railway.app/load/identity \
  -H "Authorization: Bearer $JACKAL_MEMORY_API_KEY"
```

---

## How it works

```
Agent starts  → GET /load/identity     → restore memory from Jackal
Agent works   → normal local operation
Agent ends    → POST /save             → sync memory to Jackal
```

Your memory is stored on Jackal Protocol's decentralized network — not on any single server. If the machine running your agent dies, your memory is safe and recoverable from any other machine.

---

## Environment variable

| Variable | Required | Description |
|---|---|---|
| `JACKAL_MEMORY_API_KEY` | Yes | Your API key from the onboarding page |

---

## API reference

Base URL: `https://web-production-5cce7.up.railway.app`

| Method | Endpoint | Body | Description |
|---|---|---|---|
| `POST` | `/provision` | `{"jackal_address": "jkl1..."}` | Activate storage for your agent |
| `POST` | `/save` | `{"key": "...", "content": "..."}` | Save a memory blob |
| `GET` | `/load/{key}` | — | Retrieve a memory blob |

All requests require: `Authorization: Bearer $JACKAL_MEMORY_API_KEY`

---

## Version

`v0.1.0` — early access. Report issues in this repo.
