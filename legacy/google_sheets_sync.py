#!/usr/bin/env python3
"""
Google Sheets to Firestore Sync
Syncs driver data and plant codes from SRM Dispatch Sheet to Firestore.
Haul Rate Formula: $130 / 60 mins * Round Trip Minutes / 25 tons
Round up to nearest $0.50, minimum $6.00
"""

import math
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config
from logger import LogiLogger, log_execution, log_sync_event, log_haul_rate_calculation

# Initialize logger
logger = LogiLogger.get_logger("sheets_sync")

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def calculate_haul_rate(round_trip_minutes: float) -> float:
    """
    Calculate haul rate per formula:
    $BASE / TIME_BASE mins * Round Trip Minutes / TON_BASE tons
    Round up to nearest INCREMENT, minimum MINIMUM
    """
    if not round_trip_minutes or round_trip_minutes <= 0:
        return config.HAUL_RATE_MINIMUM

    rate = (config.HAUL_RATE_BASE / config.HAUL_RATE_TIME_BASE) * round_trip_minutes / config.HAUL_RATE_TON_BASE

    # Round up to nearest INCREMENT
    increment_inverse = 1.0 / config.HAUL_RATE_ROUND_INCREMENT
    rate = math.ceil(rate * increment_inverse) / increment_inverse

    # Enforce minimum
    return max(rate, config.HAUL_RATE_MINIMUM)


@log_execution
def init_firebase() -> firestore.Client:
    """Initialize Firebase Admin SDK with error handling"""
    try:
        if not firebase_admin._apps:
            logger.info(f"Initializing Firebase with credentials: {config.CREDENTIALS_PATH}")
            cred = credentials.Certificate(config.CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


@log_execution
def get_sheets_service():
    """Initialize Google Sheets API service with error handling"""
    try:
        logger.info(f"Initializing Google Sheets API with credentials: {config.CREDENTIALS_PATH}")
        creds = service_account.Credentials.from_service_account_file(
            config.CREDENTIALS_PATH, scopes=SCOPES
        )
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets API: {e}")
        raise


@log_execution
def sync_drivers(sheets_service, db) -> Dict[str, Any]:
    """
    Pull driver data from Google Sheets and sync to Firestore.
    Expected columns: Driver Name, Round Trip Minutes, Status, etc.
    Returns sync statistics.
    """
    stats = {
        'synced': 0,
        'errors': 0,
        'skipped': 0
    }

    # Adjust range based on actual sheet structure
    range_name = "Drivers!A2:Z"
    collection_path = config.get_public_collection("drivers")

    try:
        logger.info(f"Fetching driver data from sheet: {config.SRM_DISPATCH_SHEET_ID}")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=config.SRM_DISPATCH_SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            logger.warning("No driver data found in sheet")
            return stats

        logger.info(f"Processing {len(rows)} driver rows")

        for idx, row in enumerate(rows, start=2):
            try:
                if len(row) < 2:
                    stats['skipped'] += 1
                    continue

                driver_name = row[0].strip() if row[0] else None
                if not driver_name:
                    stats['skipped'] += 1
                    continue

                # Parse round trip minutes (adjust column index as needed)
                try:
                    round_trip_minutes = float(row[1]) if len(row) > 1 and row[1] else 0
                except (ValueError, TypeError):
                    logger.warning(f"Invalid RTM for {driver_name} at row {idx}: {row[1]}")
                    round_trip_minutes = 0

                # Calculate haul rate
                haul_rate = calculate_haul_rate(round_trip_minutes)
                log_haul_rate_calculation(driver_name, round_trip_minutes, haul_rate)

                # Build driver document
                driver_data = {
                    'name': driver_name,
                    'round_trip_minutes': round_trip_minutes,
                    'haul_rate': haul_rate,
                    'status': row[2].strip() if len(row) > 2 and row[2] else 'active',
                    'last_updated': datetime.utcnow().isoformat(),
                    'sheet_row': idx,
                    'raw_data': row[:10]  # Store first 10 columns for debugging
                }

                # Use driver name as document ID (sanitize for Firestore)
                doc_id = driver_name.replace(' ', '_').replace('/', '_').replace('.', '_')

                # Write to Firestore
                db.collection(collection_path).document(doc_id).set(driver_data)
                stats['synced'] += 1
                logger.debug(f"Synced driver: {driver_name} -> ${haul_rate:.2f}")

            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error syncing driver at row {idx}: {e}")

        log_sync_event("drivers", stats)
        logger.info(f"Driver sync complete: {stats}")

    except HttpError as e:
        logger.error(f"Google Sheets API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in driver sync: {e}")
        raise

    return stats


@log_execution
def sync_plants(sheets_service, db) -> Dict[str, Any]:
    """
    Pull plant codes from Google Sheets and sync to Firestore.
    Expected columns: Plant Code, Plant Name, Location, etc.
    Returns sync statistics.
    """
    stats = {
        'synced': 0,
        'errors': 0,
        'skipped': 0
    }

    # Adjust range based on actual sheet structure
    range_name = "Plants!A2:Z"
    collection_path = config.get_public_collection("plants")

    try:
        logger.info(f"Fetching plant data from sheet: {config.SRM_DISPATCH_SHEET_ID}")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=config.SRM_DISPATCH_SHEET_ID,
            range=range_name
        ).execute()

        rows = result.get('values', [])

        if not rows:
            logger.warning("No plant data found in sheet")
            return stats

        logger.info(f"Processing {len(rows)} plant rows")

        for idx, row in enumerate(rows, start=2):
            try:
                if len(row) < 1:
                    stats['skipped'] += 1
                    continue

                plant_code = row[0].strip() if row[0] else None
                if not plant_code:
                    stats['skipped'] += 1
                    continue

                plant_data = {
                    'code': plant_code,
                    'name': row[1].strip() if len(row) > 1 and row[1] else '',
                    'location': row[2].strip() if len(row) > 2 and row[2] else '',
                    'last_updated': datetime.utcnow().isoformat(),
                    'sheet_row': idx,
                    'raw_data': row[:10]
                }

                # Write to Firestore
                db.collection(collection_path).document(plant_code).set(plant_data)
                stats['synced'] += 1
                logger.debug(f"Synced plant: {plant_code}")

            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error syncing plant at row {idx}: {e}")

        log_sync_event("plants", stats)
        logger.info(f"Plant sync complete: {stats}")

    except HttpError as e:
        if e.resp.status == 404:
            logger.warning("Plants sheet not found - skipping plant sync")
        else:
            logger.error(f"Google Sheets API error: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error in plant sync: {e}")
        raise

    return stats


@log_execution
def main():
    """Main sync execution"""
    logger.info("=" * 60)
    logger.info(f"Starting Google Sheets sync at {datetime.utcnow().isoformat()}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info("=" * 60)

    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)

    try:
        # Initialize services
        db = init_firebase()
        sheets_service = get_sheets_service()

        # Run sync operations
        driver_stats = sync_drivers(sheets_service, db)
        plant_stats = sync_plants(sheets_service, db)

        # Summary
        total_synced = driver_stats['synced'] + plant_stats['synced']
        total_errors = driver_stats['errors'] + plant_stats['errors']

        logger.info("=" * 60)
        logger.info(f"Sync complete - Synced: {total_synced}, Errors: {total_errors}")
        logger.info("=" * 60)

        # Exit with error code if there were errors
        if total_errors > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Sync interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error during sync: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
