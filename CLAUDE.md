# CLAUDE.md — Angel Cloud Project Context

> **Updated:** March 12, 2026
> **Version:** 1.0
> **Owner:** Shane Brazelton (SRM Dispatch, Alabama)
> **Repo:** github.com/thebardchat/angel-cloud
> **Constitution:** [thebardchat/constitution](https://github.com/thebardchat/constitution) — the single source of truth for all ShaneBrain ecosystem projects

## What Is This Project?

Angel Cloud — a mental wellness communication platform named after Angel Brazelton. Part of the ShaneBrain ecosystem. Node.js/Express backend (port 5000) with Flask auth bridge (port 3005), Mongoose/MongoDB models, AI sentiment analysis, angel progression system, and Google Sheets sync for SRM Dispatch operations. Local-first, privacy-first.

## Constitution

All thebardchat repositories follow the [ShaneBrain Constitution](https://github.com/thebardchat/constitution) — nine pillars governing faith, family, sobriety, local-first AI, pragmatic shipping, serving left-behind users, open-source defaults, ADHD-aware design, and gratitude as infrastructure. One link. One source. No drift.

## Hardware (All thebardchat Repos)

All thebardchat projects run on the same physical infrastructure:

| Component | Spec |
|-----------|------|
| Board | Raspberry Pi 5, 16GB RAM |
| Case | Pironman 5-MAX |
| Storage | NVMe RAID 1 — 2x WD Blue SN5000 2TB (mdadm) |
| RAID Path | `/mnt/shanebrain-raid/` |
| Core Path | `/mnt/shanebrain-raid/shanebrain-core/` |
| External | 8TB at `/media/shane/ANGEL_CLOUD` (NTFS via ntfs-3g) |
| Network | Wired ethernet, Tailscale VPN |
| Power | Always-on, 27W USB-C |
| Architecture | ARM64 (aarch64) |

## Project Structure

```
angel-cloud/
├── angel_cloud_server.js    # Express API (port 5000) — users, auth, messaging, AI sentiment
├── models/                  # Mongoose schemas (User, Angel, Message)
├── routes/                  # API routes (auth, users, messaging, angels, AI)
├── services/                # Sentiment analysis, angel matching, notifications
├── middleware/               # JWT auth middleware
├── automation/               # Memory auto-save system
├── auth-bridge/              # SSO + security bridge (port 3005)
│   ├── angel-auth-bridge.js  # JWT auth, Pulsar wallet verification, encrypted vaults
│   ├── angel_chat_v2.js      # ShaneBrain Legacy AI chatbot (Gemini)
│   ├── dispatch_calculator_service.js  # AI dispatch time windows
│   └── logistics_api/        # Flask haul rate quoting API (port 5001)
├── welcome/                  # 3D Welcome Center (Three.js, registration flow)
├── 3D Face/                  # CRT-style digital avatar interface
├── google_sheets_sync.py     # SRM Dispatch data sync to Firestore
└── life_command_center_sync.py  # Personal finance/family sync
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Angel Cloud API | 5000 | Express — users, auth, messaging, AI sentiment |
| Auth Bridge | 3005 | Flask SSO — JWT, Pulsar wallet, encrypted vaults |
| Logistics API | 5001 | Flask — haul rate quoting for SRM Dispatch |

## Angel Progression System

New Born → Young Angel → Growing Angel → Helping Angel → Guardian Angel → Angel

## Key Files

- `angel_cloud_server.js` — Main Express API server
- `auth-bridge/angel-auth-bridge.js` — SSO and security bridge
- `auth-bridge/angel_chat_v2.js` — Legacy AI chatbot (Gemini)
- `auth-bridge/dispatch_calculator_service.js` — Dispatch time window calculator
- `google_sheets_sync.py` — SRM Dispatch Google Sheets → Firestore sync
- `life_command_center_sync.py` — Personal finance/family data sync
- `ai-mission-statement.md` — Core mission, architecture, operational logic
- `SYNC_README.md` — Data synchronization documentation

## Ecosystem Projects

| Project | Repo | Status | Description |
|---------|------|--------|-------------|
| ShaneBrain Core | shanebrain-core | Active | Central AI orchestrator, Discord bot, social bot |
| Angel Cloud | angel-cloud | Active | Mental wellness platform (this repo) |
| Pulsar Sentinel | pulsar_sentinel | Active | Post-quantum security framework |
| AI-Trainer-MAX | AI-Trainer-MAX | Active | Modular AI training platform |
| Constitution | constitution | Active | Governance — nine pillars, single source of truth |

## Guidelines

- Optimize for ARM64 (aarch64) architecture
- Node.js backend, keep routes modular
- Never suggest cloud dependencies unless explicitly asked
- All data stays local on RAID when possible
- NEVER commit `.env` files — all secrets live in `.env`
- NEVER hardcode passwords or API keys in scripts
- Keep repos PRIVATE until production ready
- Use Tailscale for remote access, not port forwarding
- Follow the Constitution's nine pillars for all decisions

## Common Commands

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start Express API (port 5000)
npm start

# Start Auth Bridge (port 3005)
node auth-bridge/angel-auth-bridge.js

# Run Google Sheets sync
python google_sheets_sync.py

# Run Life Command Center sync
python life_command_center_sync.py
```

## Credits

This project would not exist without:

- **[Claude](https://claude.ai)** (Anthropic) — AI co-builder, code partner, and thinking companion
- **[Raspberry Pi Foundation](https://www.raspberrypi.org)** — affordable local compute that proves you don't need a data center
- **[Pironman 5-MAX](https://www.sunfounder.com/products/pironman-5-max)** (SunFounder) — NVMe RAID chassis that makes Pi 5 a real server
- **[WD Blue SN5000](https://www.westerndigital.com)** (Western Digital) — reliable NVMe storage, 2x 2TB in RAID 1
- **[mdadm](https://raid.wiki.kernel.org)** — Linux software RAID that keeps the data safe

## Project Owner

Shane Brazelton — dump truck dispatcher in Meridianville, Alabama building AI infrastructure for families. Direct communicator. Solutions over explanations.

## The Mission

800 million Windows users losing security updates. ShaneBrain proves affordable local AI works. Angel Cloud: mental wellness + security + digital legacy for every family.

## Contact

**Owner:** Shane Brazelton
**Company:** SRM Dispatch (Alabama)
**Ko-fi:** ko-fi.com/shanebrain
**Discord:** discord.gg/xbHQZkggU7
**Mission:** 800 million users. Digital legacy for generations.

## Claude Code Rules
- Commit and push directly to `main`. Do NOT create branches.
- Run build/test commands before committing.
- Update CLAUDE.md session log before final commit.


## Networking / Deployment
- When working with Tailscale Funnel, remember it strips URL path prefixes. Always use hardcoded base paths rather than server-side form action prefixing for routing.

## Creative Writing
- Never overwrite or rewrite the user's creative voice, prose style, or intentional structural choices (e.g., missing notes, dialogue rhythm). Ask before making stylistic changes to creative writing files.

## General Workflow Rules
- Before setting up repos, SSH keys, or services, check what's already configured on the current machine. Run `ls ~/.ssh/`, `git remote -v`, `tailscale status`, etc. before assuming fresh setup is needed.
- Let's focus on one thing at a time. Don't suggest other improvements until the current goal is fully verified working.
- Before applying changes to all files, show the result on one file first so Shane can verify the approach.

## Git
- For git conflicts, always verify --theirs vs --ours semantics before applying. State which version you're keeping and why before running the command.

## Raspberry Pi Environment
- This user runs services on Raspberry Pi. Be aware: Python 3.13 removed the `cgi` module, Piper TTS needs careful noise_scale tuning to avoid clipping, and aplay conflicts with PipeWire. Prefer `pw-play` or `paplay` for audio playback.
