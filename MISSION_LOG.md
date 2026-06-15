# MISSION LOG — Angel Cloud Repo Reconciliation

> Autonomous run by Claude Code while Shane was away. Source plan:
> `angel-cloud-repo-reconciliation.md` (ShaneBrain active-projects).
> Vision source of truth: `angel-cloud-spec.md` (locked v1.0).

---

## SUMMARY (read this first)

**Run date:** 2026-06-14 · **Box:** `Pulsar00100` · **Branch:** `main` · **Remote:** `https://github.com/thebardchat/angel-cloud`

### ✅ Phases completed + pushed to `main`
| Phase | What | Commit |
| --- | --- | --- |
| 0 | Untrack `.env` (keys already rotated; `.gitignore` already covered it) | `6aa2cda` |
| 2a | Reconcile **RAG.md** architecture → Weaviate+MCP+MiniLM; removed exposed SRM Sheet ID + Firebase project | `8d32ef4` |
| 2b | Rewrite **SCHEMA.md** → real current Weaviate schema (from `scripts/setup_weaviate_schema.py`) | `e8517be` |
| 3 | Place the 4 prototypes in `welcome_center/` (`welcome.html`, `home.html`, `newborn-namer.html`, `the-well.html`) — Shane supplied them after the first run | `a562f5d` |
| 4 | **Quarantine** the approved move-list to `/legacy/` via `git mv` (history preserved); add `legacy/README.md` | `4cf13ac` |

All pushed: `19a0307 → 6aa2cda → 8d32ef4 → e8517be → b6972f1 → a562f5d → b08e072 → 4cf13ac`.

### ✅ Phase 1 — already done before this run
`README.md`, `CLAUDE.md` (v2.0), `LEGACY.md`, and `angel-cloud-spec.md` were **already in the repo** as the correct, reconciled versions (Weaviate+MCP+MiniLM; New Born → Born Again → Angel[Name]; retro AOL 2D front door; legacy map). Internal doc links verified valid. Nothing to redo. (The repo's `angel-cloud-spec.md` is the 20 KB locked v1.0; the 9 KB copy in `~/Downloads` is an older partial — **not** used.)

### ✅ Phase 3 — done (commit `a562f5d`)
Shane dropped the 4 prototypes into the repo root (`angel-cloud-*.html`) after the first run. Moved them into `welcome_center/` with the plan's names: `welcome.html` (front door), `home.html` (hub), `newborn-namer.html` (New Born naming), `the-well.html` (name gallery). The old tracked `angel-cloud-head.html` / `angelcloudwelcome2.0.html` at root are the superseded prototypes — left in place for the Phase-4 move-list.

### ✅ Phase 4 — DONE (commit `4cf13ac`, Shane-approved)
Moved the **MOVE → /legacy/** bucket via `git mv` (history preserved). The **NEEDS-SHANE** bucket was **left in place** (still pending decisions C/E). See "Phase 4 — what moved & what stayed" and "Phase 5 follow-ups" below.

### 🚩 CRITICAL FLAGS / decisions I need from you
- **A — Wrong box.** The plan says the one editable clone lives on **gulfshores**. This is **Pulsar00100**. There was *no* angel-cloud clone here (only `.claude/`), so I cloned via **HTTPS** (SSH to GitHub is denied here) and pushed through GitHub (the sanctioned hub flow — no rsync). Confirm: keep developing on Pulsar, or move the canonical clone to gulfshores and delete this one? (Fully reversible.)
- **B — RESOLVED.** Phase-3 prototypes supplied by Shane and committed (`a562f5d`).
- **C — Two "keeper" docs are legacy by content:** `ai-mission-statement.md` and `WELCOME_CENTER.md` are on the plan's KEEP list but their content is 100% the old LogiBot / 3D era. Rewrite to current vision (needs your voice) or quarantine? (I did **not** rewrite them — creative/vision content.)
- **D — RESOLVED.** Move-list approved; quarantine executed (`4cf13ac`).
- **E — Code-level legacy coupling** in two keepers (blogger uses Ollama; auth-bridge imports the dispatch calculator + a missing module) — see Observations. These are code migrations, not doc fixes.

---

## PRE-FLIGHT FINDINGS

- `git remote -v`: **no repo existed** at `C:\Users\Hubby\Desktop\angel-cloud` (only `.claude/`). `C:\Users\Hubby\shanebrain-core\angel-cloud` is a *subfolder of the shanebrain-core repo*, **not** angel-cloud.
- Hostname `Pulsar00100`; `~/.ssh/config` shows `gulf → gulfshores` is a **separate Tailscale node** (100.112.169.111).
- **SSH to GitHub denied** (`Permission denied (publickey)`) for both `id_ed25519` and `id_pulsar`. **HTTPS works** (read confirmed; push credential present in Windows Credential Manager → pushes succeeded).
- Git identity (system): `user.name=thebardchat`, `user.email=BRAZELTONSHANE@GMAIL.COM` → commits correctly attributed.
- Cloned `main` via `git init` + `git fetch origin main` + checkout (preserving the existing `.claude/`), then `git fetch --unshallow` for full history.
- `.env` **was tracked**; `.gitignore` already contained `.env` / `.env.*` / `!.env.example` (no gitignore edit needed).

## BUILD/TEST NOTE
`package.json` has no test script (only `start`/`dev = node server.js`, and `server.js` does not exist). No runnable test suite. All changes this run are docs/config-only, so there was nothing meaningful to build/test before committing.

---

## PROPOSED PHASE-4 MOVE LIST (proposal only — nothing moved)

### KEEP — current bones (do NOT move)
- `angel-cloud-spec.md`, `README.md`, `CLAUDE.md`, `LEGACY.md`, `RAG.md` (reconciled), `SCHEMA.md` (reconciled), `MISSION_LOG.md`
- `welcome_center/` — retro Welcome Center keeper (`index.html`, `styles.css`, `welcome.js`)
- `bots/` — the MEGA Crew *(but `bots/blogger/` uses Ollama — see Observations / Decision E)*
- `memory-exports/`
- `scripts/` — current Weaviate/RAG tooling (`setup_weaviate_schema.py`, `verify_weaviate.py`, `import_rag_to_weaviate.py`, `weaviate_utils.py`, `brain_search.py`, `consolidate_memory.py`, `log_conversation.py`, `log_crisis.py`, `query_legacy.py`)
- `routes/weaviate.js`, `utils/weaviate.js`, `utils/logger.js` — **current Weaviate code** (do NOT blanket-move `routes/`/`utils/`)
- `auth-bridge/angel-auth-bridge.js`, `auth-bridge/README.md`, `auth-bridge/package.json`, `auth-bridge/.gitignore`, `auth-bridge/.env.example` *(needs decoupling — see legacy bits below)*
- `.github/`, `assets/`, `docs/`, `.gitignore`, `.env.example`, `ai-mission-statement.md`* (*pending Decision C)

### MOVE → `/legacy/` (clearly superseded)
- **Sheets/Firestore sync:** `google_sheets_sync.py`, `life_command_center_sync.py`, `webhook_receiver.py`, `SYNC_README.md`
- **LogiBot core:** `logibot_core.py`, `legacy_ai.py`
- **Ollama/Llama training era:** `continuous_learner.py`, `model_manager.py`, `model_trainer.py`, `training_data_builder.py`, `training_config.yaml`, `TRAINING.md`
- **Google service account:** `credentials.json.template`
- **Era-2 Express/Mongoose app:** `angel_cloud_server.js`, `models/` (`User.js`, `angel.js`, `message.js`)
- **3D Welcome Center (rejected):** `welcome/` (`AngelCloud_WelcomeCenter_3D.ipynb`, `README.md` ["3d-welcome-home"], `index.html`, `shanebrain-avatar.glb`)
- **Legacy bits inside `auth-bridge/`** (pull out, don't move the whole folder): `dispatch_calculator_service.js`, `logistics_api/` (`pyproject.toml`, `quoter.py`, `requirements.txt`), `angel_chat_v2.js` (Gemini), `legacy_ai_integration_client.js`

### NEEDS-SHANE — review/decide (do NOT auto-move or rewrite)
- `3D Face/` — CRT 3D avatars + `angel-cloud-head.html` + `angel-quick-memory.js`. Legacy **unless** it becomes the 2D GABE doorman. Also contains stray empty file `3D Face/null` (cruft).
- `ai-mission-statement.md` — KEEP-by-plan but content is 100% LogiBot (Ollama/Firestore/Sheets). **Decision C.**
- `WELCOME_CENTER.md` — KEEP-by-plan but documents the rejected 3D welcome center. **Decision C.**
- `bots/blogger/` — keeper, but generates content via **Ollama/Llama 3.2**. Needs migration to Claude (code + README). **Decision E.**
- `routes/` (`angels.js`, `auth.js`, `users.js`, `messaging.js`, `ai.js`), `services/` (`aisentiment.js`, `matching.js`, `notifications.js`), `middleware/auth.js` — Era-2 Express app; likely legacy but may contain reusable logic. (Keep the weaviate.js/logger.js noted above.)
- `automation/memory-system.js` — local memory-export writer; keeper-ish, but a comment plans "add Google Drive" (against the no-Google rule). Confirm keep.
- Root welcome prototypes `angel-cloud-head.html`, `angelcloudwelcome2.0.html` — spec says these are superseded by the new prototypes; move to legacy once Phase 3 lands.
- **Infra (update, don't quarantine):** `docker-compose.yml`, `Dockerfile`, `package.json` (depends on `mongoose`, `main: server.js` missing — stale), `requirements.txt`, `config.py`, `logger.py`, `health_monitor.py`, `computer_profiles.yaml`, `mount_8tb.sh`, `setup.sh`, `sync.sh`, `sync_verify.py`, `test_sync.py`

---

## OBSERVATIONS / ISSUES FOUND
1. **Extensionless HTML files:** `build-our-worlds` and `welcome-page` are single HTML files (no `.html`), though README treats `build-our-worlds/` as a directory. Consider renaming to `.html` or foldering.
2. **Stray file:** `3D Face/null` is an empty file — safe to delete (staged, not done).
3. **Broken/legacy imports in keeper:** `auth-bridge/angel-auth-bridge.js` `require`s `./pulsar_security_core` (**not present in repo**) and `./dispatch_calculator_service` (legacy) → not runnable as-is.
4. **Stale `package.json`:** declares `main: server.js` (absent) and depends on `mongoose` (Era-2 Mongo).
5. **Secrets in history:** `.env` remains in git history (keys rotated per plan → no history rewrite, which would be destructive/out of scope). The SRM Google Sheet ID + Firebase project name removed from RAG.md/SCHEMA.md current versions still exist in history (a Sheet ID is not a credential; access needs sharing perms — flagged for awareness only).

---

## PHASE-BY-PHASE DETAIL

**Phase 0** — `git rm --cached .env` (file kept on disk; `.gitignore` already covers it). Commit `6aa2cda`, pushed (first push attempt hit a transient 443 timeout; retry succeeded).

**Phase 1** — Verified `README.md`/`CLAUDE.md`/`LEGACY.md`/`angel-cloud-spec.md` already correct and reconciled; internal links valid; `legacy/` is a forward reference (created in Phase 4). No commit needed.

**Phase 2** — `RAG.md` (`8d32ef4`): fixed "Architecture Decisions", ports, project identity; removed exposed Sheet ID + Firebase project; preserved all family/faith/personal/communication-style content and historical LogiBot notes. `SCHEMA.md` (`e8517be`): replaced the Firestore/LogiBot schema with the actual Weaviate schema (Conversation, LegacyKnowledge, CrisisLog, SessionMemory) mirrored from `scripts/setup_weaviate_schema.py`. Did **not** rewrite legacy-bound docs (`TRAINING.md`, `SYNC_README.md` → quarantine) or code-coupled/keeper-by-name docs (`bots/blogger/README.md`, `ai-mission-statement.md`, `WELCOME_CENTER.md` → Decisions C/E).

**Phase 3** — Shane supplied the 4 prototypes as `angel-cloud-*.html` in the repo root; moved them into `welcome_center/` (renamed to `welcome.html` / `home.html` / `newborn-namer.html` / `the-well.html`). Verified one first, then the rest. Commit `a562f5d`, pushed.

**Phase 4** — Executed the Shane-approved move-list with `git mv` (history preserved). 27 files moved into `/legacy/` (flat for the mutually-importing Python group so intra-group imports still resolve; `models/` → `legacy/models/`; `welcome/` → `legacy/welcome/`; auth-bridge bits → `legacy/auth-bridge/`). Added `legacy/README.md`. Commit `4cf13ac`, pushed. The **NEEDS-SHANE** bucket (3D Face/, ai-mission-statement.md, WELCOME_CENTER.md, bots/blogger, routes/services/middleware, automation, root old prototypes, infra) was **not** touched. `auth-bridge/` keepers retained: `angel-auth-bridge.js`, `launch_angel_cloud.js`, `mega-dashboard.html`, `package.json`, `README.md`, `Shanebrain_Strategist_Tool.ipynb`, `.env.example`, `.gitignore`, `.hintrc`.

### ⚠️ Phase 5 follow-ups — broken references introduced by the move (need cleanup)
Moving the legacy code left these references (in files that stayed) pointing at moved paths:
- **CI:** `.github/workflows/test.yml` → `from google_sheets_sync import calculate_haul_rate` — **CI will now fail.** It tests legacy LogiBot code; update the import to `legacy.google_sheets_sync`, or retire/relocate the legacy test.
- **`test_sync.py`** → imports `google_sheets_sync`, `logibot_core` (both moved). Legacy test; consider moving to `/legacy/` too.
- **`Dockerfile`** `CMD python3 logibot_core.py` and **`docker-compose.yml`** `command: python3 webhook_receiver.py` → moved. Update or retire (infra bucket).
- **`setup.sh`** chmod/run of `google_sheets_sync.py`/`logibot_core.py`/`webhook_receiver.py`/`life_command_center_sync.py` + `credentials.json.template` → moved.
- **`sync_verify.py`** expects `credentials.json.template`, `google_sheets_sync.py`, `logibot_core.py`, `legacy_ai.py`, `training_data_builder.py`, `model_trainer.py` at root → will report them missing.
- **`auth-bridge/launch_angel_cloud.js`** references `angel_chat_v2.js`; **`auth-bridge/angel-auth-bridge.js`** `require('./dispatch_calculator_service')` — both moved. (angel-auth-bridge.js was already non-runnable: it also `require`s a missing `./pulsar_security_core`.) → Decision E (decouple).
- **Stale doc refs (NEEDS-SHANE docs):** `ai-mission-statement.md` and `WELCOME_CENTER.md` reference moved files — resolves when Decision C is made.

None of these were auto-edited (outside the approved move-list). They are the Phase-5 / Decision-C/E work.

---

## STOP
Per mission: Phases 0–4 done + pushed. **Stopping here.** Remaining open items: Decisions **A** (Pulsar vs gulfshores), **C** (ai-mission-statement.md / WELCOME_CENTER.md: rewrite vs quarantine), **E** (blogger Ollama→Claude; decouple auth-bridge), and the **Phase-5 broken-reference cleanup** above (notably CI). B and D resolved.
