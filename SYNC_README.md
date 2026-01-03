# Angel Cloud Data Synchronization

## Overview
Python scripts for synchronizing data between Google Sheets and Firestore.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Service Account
Place your `credentials.json` file in the project root. This file should contain:
- Firebase Admin SDK credentials
- Google Sheets API access via domain-wide delegation

### 3. Set Environment Variables
```bash
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"
export APP_ID="logibot"
export USER_ID="shane_brazelton"
export LIFE_SHEET_ID="your-life-command-center-sheet-id"
```

Or create a `.env` file:
```env
GOOGLE_CREDENTIALS_PATH=credentials.json
APP_ID=logibot
USER_ID=shane_brazelton
LIFE_SHEET_ID=
```

## Scripts

### google_sheets_sync.py
Syncs SRM Dispatch data to Firestore.

**Data Sources:**
- Sheet ID: `1V_So_9yzvLBAMjLu0dhtL_7mxCqudMUrkrH8iqRHuJU`
- Drivers (19 active)
- Plant codes

**Haul Rate Calculation:**
```
Rate = ($130 / 60 mins) * Round Trip Minutes / 25 tons
- Round up to nearest $0.50
- Minimum: $6.00
```

**Run:**
```bash
python google_sheets_sync.py
```

**Firestore Collections:**
- `/artifacts/logibot/public/data/drivers`
- `/artifacts/logibot/public/data/plants`

### life_command_center_sync.py
Syncs personal finance and family data.

**Run:**
```bash
python life_command_center_sync.py
```

**Firestore Collections:**
- `/artifacts/logibot/users/shane_brazelton/finance`
- `/artifacts/logibot/users/shane_brazelton/family`
- `/artifacts/logibot/users/shane_brazelton/goals`

## Firestore Storage Rules

### Public Data
```
/artifacts/{appId}/public/data/{collectionName}
```

### Private Data
```
/artifacts/{appId}/users/{userId}/{collectionName}
```

**Constraint:** No complex queries. Fetch all documents and filter in memory.

## Automation

### Cron Job (Linux/WSL)
```bash
# Run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/google_sheets_sync.py >> /var/log/angel-cloud-sync.log 2>&1

# Run daily at 6 AM
0 6 * * * /usr/bin/python3 /path/to/life_command_center_sync.py >> /var/log/life-sync.log 2>&1
```

### Windows Task Scheduler
Create tasks pointing to:
- `python.exe C:\path\to\google_sheets_sync.py`
- `python.exe C:\path\to\life_command_center_sync.py`

## Troubleshooting

### Authentication Errors
- Verify `credentials.json` has both Firebase and Sheets API access
- Check domain-wide delegation for logibot-worker service account

### Sheet Not Found
- Verify Sheet ID in constants
- Check service account has read access to the sheet

### Firestore Write Failures
- Verify Firebase project settings
- Check Firestore security rules allow service account writes

## Architecture

**Compute:** Local Llama 3.2 via Ollama (Ubuntu WSL/USB)
**Persistence:** Firestore (Layer 2)
**Data Source:** Google Sheets (SRM Operations)
**Security:** Domain-wide delegation to logibot-worker service account
**Auth:** signInWithCustomToken using __initial_auth_token
