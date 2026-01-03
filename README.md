# Angel Cloud / LogiBot

**Shane's AI Memory System & Automation Hub - Angel Cloud Intelligence Platform**

[![CI/CD](https://github.com/thebardchat/angel-cloud/workflows/LogiBot%20CI%2FCD/badge.svg)](https://github.com/thebardchat/angel-cloud/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## Overview

LogiBot is a **fixed-cost local AI infrastructure** designed to replace $1,000/mo variable cloud costs with a self-hosted solution for SRM Trucking dispatch automation.

### Core Architecture

- **Compute:** Local Llama 3.2 via Ollama (Ubuntu WSL/USB)
- **Persistence:** Firestore (Layer 2)
- **Data Source:** Google Sheets (SRM Operations)
- **Security:** Domain-wide delegation via logibot-worker service account
- **Auth:** signInWithCustomToken using __initial_auth_token

### Key Features

✅ **Real-time Driver Data Sync** - 19 active drivers synced from Google Sheets
✅ **Automated Haul Rate Calculation** - `($130/60) * RTM / 25 tons`, rounded to $0.50, min $6.00
✅ **Local AI Integration** - Ollama + Llama 3.2 for intelligent dispatch
✅ **Webhook Support** - Instant sync on Google Sheets updates
✅ **Health Monitoring** - System health checks and alerts
✅ **Docker Support** - Containerized deployment
✅ **CI/CD Pipeline** - Automated testing with GitHub Actions

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/thebardchat/angel-cloud.git
cd angel-cloud
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment
```bash
# Edit .env with your settings
nano .env

# Add Google service account credentials
cp /path/to/your/credentials.json .
```

### 4. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 5. Run Health Check
```bash
python3 health_monitor.py
```

### 6. Start LogiBot
```bash
# One-time sync
python3 google_sheets_sync.py

# Continuous mode
python3 logibot_core.py

# Webhook receiver
python3 webhook_receiver.py
```

---

## Project Structure

```
angel-cloud/
├── google_sheets_sync.py      # Primary data sync (drivers, plants)
├── life_command_center_sync.py # Personal finance/family sync
├── logibot_core.py            # Main orchestrator with Ollama AI
├── webhook_receiver.py        # Google Sheets webhook handler
├── health_monitor.py          # System health monitoring
├── config.py                  # Centralized configuration
├── logger.py                  # Logging utilities
├── test_sync.py              # Unit tests
├── requirements.txt          # Python dependencies
├── setup.sh                  # Automated installation
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container setup
├── .env.example              # Environment variables template
├── SCHEMA.md                 # Firestore schema documentation
├── SYNC_README.md            # Sync setup guide
├── ai-mission-statement.md   # Shanebrain core memory
└── logs/                     # Application logs
```

---

## Components

### Google Sheets Sync
Syncs SRM Dispatch data to Firestore.

**Run:**
```bash
python3 google_sheets_sync.py
```

**Collections Updated:**
- `/artifacts/logibot/public/data/drivers`
- `/artifacts/logibot/public/data/plants`

**Haul Rate Formula:**
```
Rate = ($130 / 60 mins) * Round Trip Minutes / 25 tons
- Round up to nearest $0.50
- Minimum: $6.00
```

### LogiBot Core
Main orchestrator with continuous sync and AI integration.

**Run:**
```bash
python3 logibot_core.py
```

**Features:**
- Continuous sync (configurable interval)
- Ollama AI analysis
- Graceful shutdown handling
- Health monitoring integration

### Webhook Receiver
Flask server for Google Sheets change notifications.

**Run:**
```bash
python3 webhook_receiver.py
```

**Endpoints:**
- `POST /webhook/sheets` - Google Sheets updates
- `GET /health` - Health check
- `POST /webhook/test` - Testing endpoint

### Health Monitor
System health checks and diagnostics.

**Run:**
```bash
python3 health_monitor.py
```

**Checks:**
- Firebase/Firestore connectivity
- Google Sheets API access
- Ollama service availability
- Last sync time validation
- Data counts verification

---

## Docker Deployment

### Build Image
```bash
docker build -t logibot:latest .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

**Services:**
- `logibot` - Main sync orchestrator
- `webhook` - Webhook receiver (port 8080)
- `ollama` - Optional local AI service

### View Logs
```bash
docker-compose logs -f logibot
```

### Stop Services
```bash
docker-compose down
```

---

## Testing

### Run Unit Tests
```bash
pytest test_sync.py -v
```

### Run with Coverage
```bash
pytest test_sync.py -v --cov=. --cov-report=term-missing
```

### Test Haul Rate Calculation
```bash
python3 -c "
from google_sheets_sync import calculate_haul_rate
print(f'RTM 90 → \${calculate_haul_rate(90):.2f}')
print(f'RTM 120 → \${calculate_haul_rate(120):.2f}')
"
```

---

## Configuration

### Environment Variables

See [.env.example](.env.example) for all configuration options.

**Required:**
- `GOOGLE_CREDENTIALS_PATH` - Service account JSON file
- `SRM_DISPATCH_SHEET_ID` - Google Sheets ID

**Optional:**
- `OLLAMA_BASE_URL` - Ollama API endpoint (default: http://localhost:11434)
- `WEBHOOK_SECRET` - Webhook signature verification
- `SYNC_INTERVAL_MINUTES` - Auto-sync interval (default: 5)
- `LOG_LEVEL` - Logging verbosity (INFO, DEBUG, etc.)

### Firestore Paths

**Public Data:**
```
/artifacts/{appId}/public/data/{collectionName}
```

**Private Data:**
```
/artifacts/{appId}/users/{userId}/{collectionName}
```

See [SCHEMA.md](SCHEMA.md) for complete schema documentation.

---

## Automation

### Cron Job (Linux/WSL)
```bash
# Run sync every 5 minutes
*/5 * * * * cd /path/to/angel-cloud && /path/to/venv/bin/python3 google_sheets_sync.py >> logs/cron.log 2>&1
```

### Windows Task Scheduler
Create task pointing to:
```
python.exe C:\path\to\angel-cloud\google_sheets_sync.py
```

---

## Monitoring

### Health Check
```bash
python3 health_monitor.py
```

### View Logs
```bash
tail -f logs/logibot.log
```

### Check Last Sync
```bash
grep "Sync complete" logs/logibot.log | tail -1
```

---

## Troubleshooting

### Authentication Errors
- Verify `credentials.json` has both Firebase and Sheets API access
- Check domain-wide delegation for logibot-worker service account

### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (if needed)
ollama serve
```

### Firestore Write Failures
- Check Firebase project settings
- Verify Firestore security rules allow service account writes

### Google Sheets Access Denied
- Confirm sheet is shared with service account email
- Verify Sheet ID in .env is correct

---

## Development

### Install Development Dependencies
```bash
pip install -r requirements.txt
pip install black flake8 isort
```

### Run Linter
```bash
flake8 .
```

### Format Code
```bash
black .
isort .
```

### Run CI Pipeline Locally
```bash
pytest test_sync.py -v --cov=.
docker build -t logibot:test .
```

---

## Architecture

### Data Flow
```
Google Sheets (SRM Dispatch)
    ↓
Google Sheets API
    ↓
google_sheets_sync.py
    ↓
Firestore Collections
    ↓
logibot_core.py → Ollama AI
    ↓
Intelligent Dispatch Decisions
```

### Webhook Flow
```
Google Sheets Edit
    ↓
Apps Script Trigger
    ↓
POST /webhook/sheets
    ↓
webhook_receiver.py
    ↓
Async Sync Trigger
```

---

## Patent: Quantum Legacy AI Stick

**USPTO Status:** Abstract finalized
**Innovation:** Portable cache/co-processor on USB flash drive
**License:** Fixed $499 one-time cost
**Security:** Zero-knowledge session proof via Merkle trees
**Audit:** Pulsar Sentinel immutable audit logs

---

## Contributing

This is a proprietary project. External contributions are not accepted at this time.

---

## License

**Proprietary** - All rights reserved.
© 2026 Shane Brazelton / Angel Cloud Intelligence Platform

See [ai-mission-statement.md](ai-mission-statement.md) for IP protection details.

---

## Support

For issues and questions:
- Review [SYNC_README.md](SYNC_README.md) for setup guidance
- Check [SCHEMA.md](SCHEMA.md) for data structure
- Run health checks: `python3 health_monitor.py`
- Review logs: `tail -f logs/logibot.log`

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Maintainer:** Shane Brazelton

**Mission:** Build fixed-cost local AI infrastructure to replace $1,000/mo variable cloud costs.
