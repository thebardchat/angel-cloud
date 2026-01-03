# SHANEBRAIN AI MISSION STATEMENT

## IDENTITY & PURPOSE

**Primary Operator**: Shane Brazelton
**Role**: Systems Architect / Dispatch Manager, SRM Trucking
**Mission**: Build fixed-cost local AI infrastructure to replace $1,000/mo variable cloud costs

## CORE ARCHITECTURE

### PROJECT LOGIBOT
- **Compute**: Local Llama 3.2 via Ollama (Ubuntu WSL/USB)
- **Persistence**: Firestore (Layer 2)
- **Data Source**: Google Sheets (SRM Operations)
- **Security**: Domain-wide delegation via logibot-worker service account
- **Auth**: signInWithCustomToken using __initial_auth_token

### ANGEL CLOUD NETWORK
Unified intelligence platform combining:
- **LogiBot**: Operational dispatch automation
- **Shanebrain**: Personal AI memory and decision support
- **Pulsar Sentinel**: Zero-knowledge audit system (Merkle tree immutable logs)

## DATA STORAGE RULES (STRICT)

### Public Data Path
```
/artifacts/{appId}/public/data/{collectionName}
```

### Private Data Path
```
/artifacts/{appId}/users/{userId}/{collectionName}
```

### Constraint
No complex queries. Fetch all documents and filter in memory.

## OPERATIONAL LOGIC

### Haul Rate Calculation (SRM Trucking)
```
Rate = ($130 / 60 mins) * Round Trip Minutes / 25 tons
- Round up to nearest $0.50
- Minimum: $6.00
```

### Active Drivers
19 active drivers tracked in real-time via Google Sheets sync.

### Plant Codes
Synchronized from SRM Dispatch Sheet to Firestore for route optimization.

## QUANTUM LEGACY AI STICK (PATENT)

**USPTO Status**: Abstract finalized
**Innovation**: Portable cache/co-processor on USB flash drive
**License**: Fixed $499 one-time cost
**Security**: Zero-knowledge session proof via Merkle trees
**Audit**: Pulsar Sentinel immutable audit logs

### Key Features
- Offline AI inference cache
- Personal data sovereignty
- Cryptographic session verification
- Tamper-evident audit trail

## COMMUNICATION PROTOCOL

### Mandatory Directness
- No apologies
- No conversational filler
- No summaries
- No rants
- No repetition
- No "Is there anything else I can do for you?"

### Context Management
If the conversation becomes repetitive or looping ("funky"), STOP and wait for Shane to reset context.

### Priority
Code execution over explanation.

## SYSTEM GOALS

1. **Cost Reduction**: Eliminate $1,000/mo cloud AI costs
2. **Data Sovereignty**: Keep operational data under local control
3. **Performance**: Real-time sync between Google Sheets and Firestore
4. **Scalability**: Modular architecture for future expansion
5. **Innovation**: Patent-protected IP for commercial licensing

## DATA SOURCES

### SRM Dispatch Sheet
- **Sheet ID**: 1V_So_9yzvLBAMjLu0dhtL_7mxCqudMUrkrH8iqRHuJU
- **Webhook**: https://script.google.com/macros/s/AKfycbxqhVZiYQ74mt9y7yDy0Wpp8rwrEjSisCO63yWS_q_wEJCuaMMYZd_MlkBlIjzhGKdD9A/exec
- **Integration**: iPhone Shortcuts → Apps Script → Shanebrain API

### Life Command Center Sheet
- Finance tracking
- Family schedules
- Personal goals

## EXECUTION FILES

### Required Scripts
- `google_sheets_sync.py`: Primary data bridge (drivers, plant codes)
- `life_command_center_sync.py`: Personal finance/family logic
- `logibot_core.py`: Main execution loop with Llama AI integration

### System Health Monitoring
- Automatic health checks
- Work schedule initialization
- Error logging and recovery

## TECHNICAL CONSTRAINTS

- **WSL Environment**: Ubuntu on Windows Subsystem for Linux
- **USB Boot**: System runs from external USB drive
- **Local Inference**: Ollama serves Llama 3.2 models
- **Cloud Sync**: Firestore for data persistence only
- **No MongoDB**: Previous architecture deprecated

## IP PROTECTION

All core logic, patent abstracts, and proprietary algorithms are:
- Version controlled in private repositories
- Protected under USPTO provisional patent application
- Subject to commercial licensing terms ($499 fixed license)

---

**Last Updated**: 2026-01-03
**Version**: 1.0
**Status**: Active Development
