# CLAUDE.md — Angel Cloud Project Context

> **Updated:** 2026-06-13 · **Version:** 2.0 · **Owner:** Shane Brazelton (Hazel Green, Alabama)
> **Repo:** github.com/thebardchat/angel-cloud
> **Vision source of truth:** [`angel-cloud-spec.md`](./angel-cloud-spec.md) (locked v1.0)
> **Governance:** [thebardchat/constitution](https://github.com/thebardchat/constitution) — nine pillars, the single source of truth for all ShaneBrain projects.

## What Is This Project?

Angel Cloud — a **faith-rooted, local-first mental-wellness and creative safe haven**, the public face of ShaneBrain. Named after Angel Brazelton. You don't log in; you prove an uplifting state of being and earn your way in (the security filter and the human filter are the same gate). Read [`angel-cloud-spec.md`](./angel-cloud-spec.md) before making architectural or vision decisions — it governs.

## ⚠️ Read Before You Build — this repo has legacy layers

Earlier iterations were a **different thing**: a Node/Express + MongoDB/Firestore + Google Sheets dispatch tool with Ollama/Gemini and a 3D welcome center. **All of that is superseded.** See [`LEGACY.md`](./LEGACY.md) and the `legacy/` folder. Do NOT build on, extend, or copy patterns from:
- Ollama / Llama (removed 2026-04-30) — embeddings are **text2vec-transformers / all-MiniLM-L6-v2** only
- Firestore or MongoDB as a primary store — persistence is **Weaviate**
- Google Sheets / Drive dependency or service-account delegation
- The "LogiBot / SRM dispatch" identity — that's a **separate project** now
- The 3D welcome center — the front door is locked **1998 / AOL retro, 2D** (3D / Roblox rejected)

## Architecture (current)

**The ShaneBrain Engine = Claude (intelligence) + Weaviate (memory) + MCP (nervous system) + text2vec-transformers / MiniLM (local embeddings).** Local-first, zero-knowledge, owned hardware over Tailscale. A hosted lane serves people who can't self-host.

## Identity Arc (current — per spec §15)

**New Born → Born Again → Angel[Name].**
- **New Born** — enters under a *given* handle drawn from the Gospels + a hope-verse number (e.g. `DoveofJordan4031`). Grounded, cared for, no wings.
- **Born Again** — earned over time (peer-confirmed Uplifts + verified Missions + Halo threshold + mentor vouch + a Ceremony). Cannot be faked or clicked.
- **Angel[Name]** — claims their own name and their wings (trust + power).
- **The rule:** *Care is never gated. Power always is.*

> The old 6-tier ladder (Young / Growing / Helping / Guardian Angel) is **superseded as the identity model**. Those names are candidates for **Halo trust levels** inside Angel-hood — but the spec's three-stage arc governs.

## Where It Runs

- **gulfshores** — primary dev box. The one editable working clone lives here; Claude Code runs here.
- **shanebrain (Pi 5, Pironman 5-MAX, NVMe RAID 1)** — orchestrator + MCP server + the deployed/running copy (pulled from GitHub, separate from the dev clone). Core path: `/mnt/shanebrain-raid/shanebrain-core/`. ARM64 (aarch64).
- **GitHub** — single source of truth / hub. Push & pull through GitHub; never rsync the working dir between nodes.
- Remote access via **Tailscale**, not port forwarding.

## Ecosystem Projects

| Project | Repo | Description |
| --- | --- | --- |
| ShaneBrain Core | shanebrain-core | Central AI orchestrator, Discord bot, social bot |
| Angel Cloud | angel-cloud | Mental-wellness safe haven (this repo) |
| Pulsar Sentinel | pulsar_sentinel | Post-quantum security framework |
| AI-Trainer-MAX | AI-Trainer-MAX | Modular AI training platform |
| Constitution | constitution | Governance — nine pillars, single source of truth |

## Claude Code Rules

- Commit and push directly to `main`. Do NOT create branches.
- Run build/test commands before committing.
- **Confirm with Shane before moving or deleting ANY file** during the repo reconciliation. When unsure whether a file is legacy or a keeper, leave it and ask.
- Update the CLAUDE.md session log before the final commit.

## General Workflow Rules

- Before setting up repos, SSH keys, or services, check what's already configured: `ls ~/.ssh/`, `git remote -v`, `tailscale status`. Never assume fresh setup.
- One thing at a time. Don't suggest other improvements until the current goal is fully verified working.
- Before applying a change across all files, show the result on one file first so Shane can verify the approach.

## Git

- For conflicts, verify `--theirs` vs `--ours` semantics before applying. State which version you're keeping and why before running the command.

## Creative Writing

- Never overwrite or rewrite Shane's creative voice, prose style, or intentional structural choices. Ask before any stylistic change to creative files.

## Raspberry Pi Environment

- Python 3.13 removed the `cgi` module. Piper TTS needs careful `noise_scale` tuning to avoid clipping. `aplay` conflicts with PipeWire — prefer `pw-play` or `paplay`.

## Security

- NEVER commit `.env` (it must be in `.gitignore`). NEVER hardcode passwords or API keys.
- This repo is **public** — keep secrets and internal IPs out of committed files.

## Owner / Mission

Shane Brazelton — concrete dispatch operator in Hazel Green, Alabama, building AI infrastructure for families. Direct communicator, solutions over explanations. **Mission:** 800 million users losing security updates; prove affordable local AI works; mental wellness + security + digital legacy for every family.

**Ko-fi:** ko-fi.com/shanebrain · **Discord:** discord.gg/xbHQZkggU7

## Credits

- **[Claude](https://claude.ai)** (Anthropic) — AI co-builder and thinking companion
- **[Raspberry Pi Foundation](https://www.raspberrypi.org)** — affordable local compute
- **[Pironman 5-MAX](https://www.sunfounder.com)** (SunFounder) — NVMe RAID chassis

## Session Log

- 2026-06-13 — CLAUDE.md v2.0: reconciled to the locked spec (Weaviate + MCP + MiniLM; New Born → Born Again → Angel[Name]; retro AOL front door). Flagged legacy Node/Mongo/Firestore/Ollama/3D layers for quarantine. Durable workflow/git/Claude-Code rules retained.
