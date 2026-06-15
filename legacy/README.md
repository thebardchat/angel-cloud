# /legacy — Pre-pivot code (quarantined)

This is the **pre-pivot LogiBot / dispatch + Ollama/Firestore/Google era**. It is **superseded** by [`../angel-cloud-spec.md`](../angel-cloud-spec.md) and the current architecture in [`../CLAUDE.md`](../CLAUDE.md). See [`../LEGACY.md`](../LEGACY.md) for the full era map.

**Kept for reference and history only. Do NOT build on, extend, or copy patterns from anything in here.** In particular: no **Ollama/Llama**, no **Firestore/MongoDB** as a primary store, no **Google Sheets/Drive** dependency, no **Gemini**. Embeddings are text2vec-transformers / all-MiniLM-L6-v2; persistence is Weaviate; intelligence is Claude.

## What's here

| Path | Why it's here |
| --- | --- |
| `google_sheets_sync.py`, `life_command_center_sync.py`, `webhook_receiver.py`, `SYNC_README.md` | Google Sheets → Firestore sync (LogiBot/SRM dispatch) |
| `logibot_core.py`, `legacy_ai.py` | LogiBot orchestrator + legacy AI |
| `continuous_learner.py`, `model_manager.py`, `model_trainer.py`, `training_data_builder.py`, `training_config.yaml`, `TRAINING.md` | Ollama/Llama 3.2 training era |
| `credentials.json.template` | Google service-account template |
| `angel_cloud_server.js`, `models/` | Era-2 Express/Mongoose app |
| `welcome/` | 3D Welcome Center (Three.js) — front door is now 1998/AOL retro 2D |
| `auth-bridge/dispatch_calculator_service.js`, `auth-bridge/logistics_api/`, `auth-bridge/angel_chat_v2.js`, `auth-bridge/legacy_ai_integration_client.js` | Legacy bits pulled out of the kept `auth-bridge/` (dispatch calculator, logistics API, Gemini chat, legacy-AI client) |

## Note on broken imports / references
These files were quarantined as a group. Intra-group Python imports (e.g. `logibot_core.py` → `google_sheets_sync.py`) still resolve because the modules remain siblings here. References from files that stayed in the repo (CI, Dockerfile, docker-compose, setup.sh, sync_verify.py, test_sync.py, auth-bridge launcher/bridge) now point at moved files — these are tracked in `../MISSION_LOG.md` for the Phase-5 cleanup. Quarantined code is **not** expected to run as-is.

*Superseded by [`../angel-cloud-spec.md`](../angel-cloud-spec.md).*
