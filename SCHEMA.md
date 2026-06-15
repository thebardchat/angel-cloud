# Weaviate Schema Documentation

> **Updated:** 2026-06-14 · **Source of truth for vision:** [`angel-cloud-spec.md`](./angel-cloud-spec.md) · **Architecture:** [`CLAUDE.md`](./CLAUDE.md)

Angel Cloud persists everything in **Weaviate** (local-first, zero-knowledge, owned hardware). Embeddings are produced locally by **text2vec-transformers / all-MiniLM-L6-v2**. There is **no Firestore, MongoDB, or Google dependency** — the pre-pivot Firestore/LogiBot schema is superseded (see [`LEGACY.md`](./LEGACY.md); the old version lives in git history).

The authoritative, runnable definition is [`scripts/setup_weaviate_schema.py`](./scripts/setup_weaviate_schema.py). This document mirrors it.

## Stack

| Service | Port | Role |
| --- | --- | --- |
| Weaviate | `:8080` | vector store / persistence |
| text2vec-transformers (all-MiniLM-L6-v2) | `:8090` | local embeddings |
| MCP | `:8100` | nervous system / tool layer |
| Angel Cloud Gateway | `:4200` | API surface |

All classes use `vectorizer: "none"` — vectors are computed externally by the MiniLM transformer service and supplied at write time, keeping embedding fully local and the schema model-agnostic.

## Classes

### `Conversation`
Chat history for ShaneBrain and Angel Cloud.

| Property | Type | Notes |
| --- | --- | --- |
| `message` | `text` | message body |
| `role` | `string` | e.g. `user`, `assistant` |
| `mode` | `string` | conversation mode/context |
| `timestamp` | `date` | when the message occurred |
| `session_id` | `string` | groups messages into a session |

### `LegacyKnowledge`
Shane's RAG data and family-legacy wisdom (imported from [`RAG.md`](./RAG.md) via [`scripts/import_rag_to_weaviate.py`](./scripts/import_rag_to_weaviate.py)).

| Property | Type | Notes |
| --- | --- | --- |
| `content` | `text` | knowledge chunk |
| `category` | `string` | topical grouping |
| `source` | `string` | originating document/section |

### `CrisisLog`
Logs for high-severity wellness detections. Part of the **Crisis Covenant**: AI flags, a human decides — the machine never acts alone on a life.

| Property | Type | Notes |
| --- | --- | --- |
| `input_text` | `text` | text that triggered the detection |
| `severity` | `string` | severity classification |
| `timestamp` | `date` | when the detection occurred |

### `SessionMemory`
Consolidated session memories from Angel Cloud (built from `/memory-exports`).

| Property | Type | Notes |
| --- | --- | --- |
| `content` | `text` | consolidated memory |
| `session_date` | `date` | date of the session |
| `session_file` | `string` | source file in `/memory-exports` |
| `section` | `string` | section within the session |
| `imported_at` | `date` | when it was imported into Weaviate |

## Operations

- **Create / migrate the schema:** `python scripts/setup_weaviate_schema.py` (idempotent — skips classes that already exist).
- **Verify:** `python scripts/verify_weaviate.py`.
- **Import RAG knowledge:** `python scripts/import_rag_to_weaviate.py`.

## Conventions

- Timestamps are ISO 8601 (UTC), stored in `date` properties.
- Because `vectorizer` is `none`, the caller is responsible for passing a vector (from the MiniLM service) on every object write that should be semantically searchable.
- Crisis data is sensitive: handle under the zero-knowledge, human-in-the-loop rules in the spec.

---

*Superseded predecessor: the Firestore/LogiBot dispatch schema (drivers/plants/finance/family/goals synced from Google Sheets). See [`LEGACY.md`](./LEGACY.md); retained only in git history.*
