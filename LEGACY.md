# LEGACY.md — What's Superseded (and why it's still here)

This repo grew through a few eras before the vision crystallized. The **locked vision** is [`angel-cloud-spec.md`](./angel-cloud-spec.md); the **current architecture** is in [`CLAUDE.md`](./CLAUDE.md). This file is the honest map of what came *before* — kept for reference and history, **not as a base to build on**.

> Earlier code got Angel Cloud here. It's a foundation to learn from, not a thing to extend. The bones that carried forward (auth, the Welcome Center idea, build-our-worlds, the bot crew) live on; the rest is parked.

---

## The eras (so the layers make sense)

**Era 1 — LogiBot / SRM dispatch automation.** A fixed-cost local AI to replace cloud spend for trucking dispatch. Google Sheets → Firestore sync, haul-rate calculation, webhook receiver, health monitor. Compute via **Ollama + Llama 3.2**.

**Era 2 — Angel Cloud v1 (mental-wellness comms).** **Node/Express** API (:5000) + **Flask** auth bridge (:3005) + **MongoDB/Mongoose**, a **Gemini** chatbot, AI sentiment analysis, a **6-tier** angel ladder, a **3D Welcome Center** (Three.js) + CRT avatar, and a Logistics API (:5001).

**Era 3 — the current vision (the spec).** AOL-retro safe haven; **Weaviate + MCP + text2vec-transformers/MiniLM**; **New Born → Born Again → Angel[Name]**; the Crisis Covenant; Angels Build Worlds.

---

## Do NOT build on these (superseded)

| Old | Current | 
| --- | --- |
| Ollama / Llama 3.2 | **text2vec-transformers / all-MiniLM-L6-v2** only |
| Firestore **and** MongoDB/Mongoose | **Weaviate** |
| Google Sheets / Drive sync + service-account delegation | **No Google dependency** (sovereign, zero-knowledge) |
| Gemini as the chat brain | **Claude** |
| LogiBot / SRM-dispatch identity | A **separate project** — not Angel Cloud |
| 3D Welcome Center (Three.js) + CRT 3D avatar | Front door is **1998 / AOL retro, 2D** (3D / Roblox rejected) |
| 6-tier ladder (Young / Growing / Helping / Guardian) | **New Born → Born Again → Angel[Name]** *(the 4 old names may return as Halo trust levels — TBD)* |
| Ports 5000 / 3005 / 5001 | Gateway **:4200**, MCP **:8100**, Weaviate **:8080**, t2v **:8090** |

---

## File map — three buckets

**Quarantine to `/legacy/` (clearly superseded):**
- `google_sheets_sync.py`, `life_command_center_sync.py`, `webhook_receiver.py` — Google Sheets / Firestore sync
- `logibot_core.py`, `legacy_ai.py` — LogiBot orchestrator + legacy AI
- `continuous_learner.py`, `model_manager.py`, `model_trainer.py`, `training_data_builder.py`, `training_config.yaml`, `TRAINING.md` — Ollama/Llama training era
- `credentials.json.template` — Google service-account template
- `angel_cloud_server.js` + `models/` — Era-2 Express/Mongoose app
- `welcome/` — the 3D Welcome Center (Three.js)
- `3D Face/` — CRT 3D avatar *(confirm: keep only if it becomes the 2D GABE doorman; otherwise legacy)*

**Keep (current bones — do NOT move):**
- `auth-bridge/` — the trust + security gate *(keeps `angel-auth-bridge.js`; but `dispatch_calculator_service.js`, `logistics_api/`, and the Gemini `angel_chat_v2.js` inside it are legacy — pull those out)*
- `welcome_center/` — the retro Welcome Center + New Born naming
- `build-our-worlds/` — Angels Build Worlds
- `bots/` — the MEGA Crew
- `memory-exports/`, `ai-mission-statement.md`, `CLAUDE.md`, `angel-cloud-spec.md`

**Review before moving (mixed / unclear — confirm with Shane, don't auto-move):**
- `routes/`, `services/`, `middleware/` — Era-2 Express app pieces; likely legacy, but check for anything reusable
- `automation/`, `utils/`, `scripts/` — some may still be live cluster utilities
- `docker-compose.yml`, `Dockerfile`, `package.json`, `requirements.txt` — infra; update rather than quarantine

---

## Why we keep it

This isn't failure — it's iteration. Three honest attempts stacked up, and each one taught the next. The auth bridge, the Welcome Center, build-our-worlds, and the bot crew all came out of this work and carried forward into the real thing. We park the rest for reference; git history holds whatever isn't in `/legacy/`.

*Superseded by [`angel-cloud-spec.md`](./angel-cloud-spec.md). Do not build on anything in this file without checking the spec first.*
