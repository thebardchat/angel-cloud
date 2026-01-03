#!/usr/bin/env python3
"""
Google Sheets to Firestore Sync
Syncs driver data and plant codes from SRM Dispatch Sheet to Firestore.
Haul Rate Formula: $130 / 60 mins * Round Trip Minutes / 25 tons
Round up to nearest $0.50, minimum $6.00
"""

import os
import math
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Constants
SHEET_ID = "1V_So_9yzvLBAMjLu0dhtL_7mxCqudMUrkrH8iqRHuJU"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
APP_ID = os.getenv('APP_ID', 'logibot')

# Firestore paths
DRIVERS_COLLECTION = f"artifacts/{APP_ID}/public/data/drivers"
PLANTS_COLLECTION = f"artifacts/{APP_ID}/public/data/plants"


def calculate_haul_rate(round_trip_minutes: float) -> float:
    """
    Calculate haul rate per formula:
    $130 / 60 mins * Round Trip Minutes / 25 tons
    Round up to nearest $0.50, minimum $6.00
    """
    if not round_trip_minutes or round_trip_minutes <= 0:
        return 6.00

    rate = (130.0 / 60.0) * round_trip_minutes / 25.0

    # Round up to nearest $0.50
    rate = math.ceil(rate * 2) / 2

    # Enforce minimum
    return max(rate, 6.00)


def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def get_sheets_service():
    """Initialize Google Sheets API service"""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)


def sync_drivers(sheets_service, db):
    """
    Pull driver data from Google Sheets and sync to Firestore.
    Expected columns: Driver Name, Round Trip Minutes, Status, etc.
    """
    # Adjust range based on actual sheet structure
    range_name = "Drivers!A2:Z"

    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=range_name
    ).execute()

    rows = result.get('values', [])

    if not rows:
        print("No driver data found.")
        return

    synced_count = 0
    for row in rows:
        if len(row) < 2:
            continue

        driver_name = row[0].strip() if row[0] else None
        if not driver_name:
            continue

        # Parse round trip minutes (adjust column index as needed)
        try:
            round_trip_minutes = float(row[1]) if len(row) > 1 and row[1] else 0
        except (ValueError, TypeError):
            round_trip_minutes = 0

        # Calculate haul rate
        haul_rate = calculate_haul_rate(round_trip_minutes)

        # Build driver document
        driver_data = {
            'name': driver_name,
            'round_trip_minutes': round_trip_minutes,
            'haul_rate': haul_rate,
            'status': row[2] if len(row) > 2 else 'active',
            'last_updated': datetime.utcnow().isoformat(),
            'raw_data': row  # Store full row for debugging
        }

        # Use driver name as document ID (sanitize for Firestore)
        doc_id = driver_name.replace(' ', '_').replace('/', '_')

        # Write to Firestore
        db.collection(DRIVERS_COLLECTION).document(doc_id).set(driver_data)
        synced_count += 1

    print(f"Synced {synced_count} drivers to Firestore.")


def sync_plants(sheets_service, db):
    """
    Pull plant codes from Google Sheets and sync to Firestore.
    Expected columns: Plant Code, Plant Name, Location, etc.
    """
    # Adjust range based on actual sheet structure
    range_name = "Plants!A2:Z"

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            print("No plant data found.")
            return

        synced_count = 0
        for row in rows:
            if len(row) < 1:
                continue

            plant_code = row[0].strip() if row[0] else None
            if not plant_code:
                continue

            plant_data = {
                'code': plant_code,
                'name': row[1] if len(row) > 1 else '',
                'location': row[2] if len(row) > 2 else '',
                'last_updated': datetime.utcnow().isoformat(),
                'raw_data': row
            }

            # Write to Firestore
            db.collection(PLANTS_COLLECTION).document(plant_code).set(plant_data)
            synced_count += 1

        print(f"Synced {synced_count} plants to Firestore.")

    except Exception as e:
        print(f"Plant sync skipped (sheet may not exist): {e}")


def main():
    """Main sync execution"""
    print(f"Starting sync at {datetime.utcnow().isoformat()}")

    db = init_firebase()
    sheets_service = get_sheets_service()

    sync_drivers(sheets_service, db)
    sync_plants(sheets_service, db)

    print("Sync complete.")


if __name__ == "__main__":
    main()
