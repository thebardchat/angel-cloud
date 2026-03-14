# Firestore Schema Documentation

## Overview
LogiBot uses Firestore for data persistence following a strict path structure that separates public and private data.

## Collection Path Structure

### Public Data
```
/artifacts/{appId}/public/data/{collectionName}
```

### Private Data
```
/artifacts/{appId}/users/{userId}/{collectionName}
```

## Collections

### Drivers Collection
**Path:** `/artifacts/logibot/public/data/drivers`

**Document Structure:**
```json
{
  "name": "John Doe",
  "round_trip_minutes": 90.0,
  "haul_rate": 8.00,
  "status": "active",
  "last_updated": "2026-01-03T12:00:00.000000",
  "sheet_row": 2,
  "raw_data": ["John Doe", "90", "active", ...]
}
```

**Fields:**
- `name` (string): Driver full name
- `round_trip_minutes` (float): Round trip time in minutes
- `haul_rate` (float): Calculated haul rate in USD
- `status` (string): Driver status (`active`, `inactive`, etc.)
- `last_updated` (ISO datetime): Last sync timestamp
- `sheet_row` (int): Source row number in Google Sheet
- `raw_data` (array): Raw row data from sheet (first 10 columns)

**Document ID:** Sanitized driver name (spaces and special chars replaced with `_`)

**Haul Rate Calculation:**
```
Rate = ($130 / 60 mins) * Round Trip Minutes / 25 tons
- Round up to nearest $0.50
- Minimum: $6.00
```

**Example Document IDs:**
- `John_Doe`
- `Jane_Smith`
- `Bob_Wilson_Jr_`

---

### Plants Collection
**Path:** `/artifacts/logibot/public/data/plants`

**Document Structure:**
```json
{
  "code": "PLANT001",
  "name": "Main Distribution Center",
  "location": "Dallas, TX",
  "last_updated": "2026-01-03T12:00:00.000000",
  "sheet_row": 2,
  "raw_data": ["PLANT001", "Main Distribution Center", "Dallas, TX", ...]
}
```

**Fields:**
- `code` (string): Unique plant code
- `name` (string): Plant name
- `location` (string): Plant location
- `last_updated` (ISO datetime): Last sync timestamp
- `sheet_row` (int): Source row number in Google Sheet
- `raw_data` (array): Raw row data from sheet (first 10 columns)

**Document ID:** Plant code as-is

---

### Finance Collection (Private)
**Path:** `/artifacts/logibot/users/{userId}/finance`

**Document Structure:**
```json
{
  "category": "Income",
  "amount": 5000.00,
  "date": "2026-01-01",
  "notes": "Monthly salary",
  "last_updated": "2026-01-03T12:00:00.000000",
  "raw_data": ["Income", "5000.00", "2026-01-01", "Monthly salary", ...]
}
```

**Fields:**
- `category` (string): Finance category
- `amount` (float): Transaction amount in USD
- `date` (string): Transaction date
- `notes` (string): Additional notes
- `last_updated` (ISO datetime): Last sync timestamp
- `raw_data` (array): Raw row data from sheet

**Document ID:** `entry_{index}` (sequential)

---

### Family Collection (Private)
**Path:** `/artifacts/logibot/users/{userId}/family`

**Document Structure:**
```json
{
  "event_name": "Soccer Practice",
  "date": "2026-01-05",
  "participants": "Kids",
  "notes": "4:00 PM at school field",
  "last_updated": "2026-01-03T12:00:00.000000",
  "raw_data": ["Soccer Practice", "2026-01-05", "Kids", "4:00 PM at school field", ...]
}
```

**Fields:**
- `event_name` (string): Event or activity name
- `date` (string): Event date
- `participants` (string): Family members involved
- `notes` (string): Additional details
- `last_updated` (ISO datetime): Last sync timestamp
- `raw_data` (array): Raw row data from sheet

**Document ID:** `event_{index}` (sequential)

---

### Goals Collection (Private)
**Path:** `/artifacts/logibot/users/{userId}/goals`

**Document Structure:**
```json
{
  "goal": "Save $10,000 for emergency fund",
  "target_date": "2026-12-31",
  "status": "in_progress",
  "progress": "60%",
  "last_updated": "2026-01-03T12:00:00.000000",
  "raw_data": ["Save $10,000 for emergency fund", "2026-12-31", "in_progress", "60%", ...]
}
```

**Fields:**
- `goal` (string): Goal description
- `target_date` (string): Target completion date
- `status` (string): Status (`pending`, `in_progress`, `completed`)
- `progress` (string): Progress indicator
- `last_updated` (ISO datetime): Last sync timestamp
- `raw_data` (array): Raw row data from sheet

**Document ID:** `goal_{index}` (sequential)

---

## Query Constraints

**CRITICAL:** Firestore collections use **simple document fetches only**.

- ❌ **NO** complex queries
- ❌ **NO** `where()` clauses
- ❌ **NO** compound indexes

**Querying Pattern:**
1. Fetch all documents from collection
2. Filter in memory (Python/JavaScript)

**Example:**
```python
# Correct approach
docs = db.collection('artifacts/logibot/public/data/drivers').stream()
active_drivers = [d.to_dict() for d in docs if d.to_dict()['status'] == 'active']

# Incorrect approach (will fail)
docs = db.collection('artifacts/logibot/public/data/drivers').where('status', '==', 'active').stream()
```

---

## Data Sync Behavior

### Sync Strategy
- Full collection replacement on each sync
- No incremental updates
- No conflict resolution (last write wins)

### Timestamps
- All timestamps in ISO 8601 format (UTC)
- `last_updated` field updated on every sync

### Error Handling
- Individual document failures are logged but don't stop sync
- Sync continues even if some rows are invalid
- Statistics tracked: `synced`, `errors`, `skipped`

---

## Security Rules (Reference)

Public data is readable by authenticated users:
```
/artifacts/{appId}/public/data/** - read: authenticated, write: service_account
```

Private data is user-scoped:
```
/artifacts/{appId}/users/{userId}/** - read/write: user_id match OR service_account
```

---

## Data Source

All data synced from Google Sheets:
- **SRM Dispatch Sheet:** `1V_So_9yzvLBAMjLu0dhtL_7mxCqudMUrkrH8iqRHuJU`
- **Life Command Center Sheet:** (User-configurable)

---

## Retention Policy

- No automatic deletion
- Manual cleanup required for old records
- Consider implementing TTL for event/transaction data

---

## Index Requirements

None. All filtering done in application memory.

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Maintainer:** Shane Brazelton / LogiBot System
