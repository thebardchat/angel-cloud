#!/usr/bin/env python3
"""
Life Command Center Sync
Personal finance and family data synchronization.
Pulls data from Google Sheets and syncs to Firestore private user collection.
"""

import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
APP_ID = os.getenv('APP_ID', 'logibot')
USER_ID = os.getenv('USER_ID', 'shane_brazelton')

# Life Command Center Sheet ID (update with actual sheet)
LIFE_SHEET_ID = os.getenv('LIFE_SHEET_ID', '')

# Firestore private paths
FINANCE_COLLECTION = f"artifacts/{APP_ID}/users/{USER_ID}/finance"
FAMILY_COLLECTION = f"artifacts/{APP_ID}/users/{USER_ID}/family"
GOALS_COLLECTION = f"artifacts/{APP_ID}/users/{USER_ID}/goals"


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


def sync_finance(sheets_service, db):
    """
    Sync personal finance data from Life Command Center sheet.
    Expected: Income, Expenses, Budgets, Savings Goals
    """
    if not LIFE_SHEET_ID:
        print("LIFE_SHEET_ID not set. Skipping finance sync.")
        return

    range_name = "Finance!A2:Z"

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=LIFE_SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            print("No finance data found.")
            return

        synced_count = 0
        for idx, row in enumerate(rows):
            if len(row) < 2:
                continue

            # Example structure: Category, Amount, Date, Notes
            finance_data = {
                'category': row[0] if len(row) > 0 else '',
                'amount': float(row[1]) if len(row) > 1 and row[1] else 0.0,
                'date': row[2] if len(row) > 2 else '',
                'notes': row[3] if len(row) > 3 else '',
                'last_updated': datetime.utcnow().isoformat(),
                'raw_data': row
            }

            doc_id = f"entry_{idx}"
            db.collection(FINANCE_COLLECTION).document(doc_id).set(finance_data)
            synced_count += 1

        print(f"Synced {synced_count} finance entries to Firestore.")

    except Exception as e:
        print(f"Finance sync error: {e}")


def sync_family(sheets_service, db):
    """
    Sync family-related data (schedules, events, contacts).
    """
    if not LIFE_SHEET_ID:
        print("LIFE_SHEET_ID not set. Skipping family sync.")
        return

    range_name = "Family!A2:Z"

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=LIFE_SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            print("No family data found.")
            return

        synced_count = 0
        for idx, row in enumerate(rows):
            if len(row) < 1:
                continue

            family_data = {
                'event_name': row[0] if len(row) > 0 else '',
                'date': row[1] if len(row) > 1 else '',
                'participants': row[2] if len(row) > 2 else '',
                'notes': row[3] if len(row) > 3 else '',
                'last_updated': datetime.utcnow().isoformat(),
                'raw_data': row
            }

            doc_id = f"event_{idx}"
            db.collection(FAMILY_COLLECTION).document(doc_id).set(family_data)
            synced_count += 1

        print(f"Synced {synced_count} family events to Firestore.")

    except Exception as e:
        print(f"Family sync error: {e}")


def sync_goals(sheets_service, db):
    """
    Sync personal and professional goals.
    """
    if not LIFE_SHEET_ID:
        print("LIFE_SHEET_ID not set. Skipping goals sync.")
        return

    range_name = "Goals!A2:Z"

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=LIFE_SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            print("No goals data found.")
            return

        synced_count = 0
        for idx, row in enumerate(rows):
            if len(row) < 1:
                continue

            goals_data = {
                'goal': row[0] if len(row) > 0 else '',
                'target_date': row[1] if len(row) > 1 else '',
                'status': row[2] if len(row) > 2 else 'pending',
                'progress': row[3] if len(row) > 3 else '',
                'last_updated': datetime.utcnow().isoformat(),
                'raw_data': row
            }

            doc_id = f"goal_{idx}"
            db.collection(GOALS_COLLECTION).document(doc_id).set(goals_data)
            synced_count += 1

        print(f"Synced {synced_count} goals to Firestore.")

    except Exception as e:
        print(f"Goals sync error: {e}")


def main():
    """Main sync execution for Life Command Center"""
    print(f"Starting Life Command Center sync at {datetime.utcnow().isoformat()}")

    db = init_firebase()
    sheets_service = get_sheets_service()

    sync_finance(sheets_service, db)
    sync_family(sheets_service, db)
    sync_goals(sheets_service, db)

    print("Life Command Center sync complete.")


if __name__ == "__main__":
    main()
