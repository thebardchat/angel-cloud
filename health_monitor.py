#!/usr/bin/env python3
"""
Health Monitor for LogiBot System
Monitors system health, service availability, and data sync status.
"""

import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

import firebase_admin
from firebase_admin import credentials, firestore

from config import config
from logger import LogiLogger

# Initialize logger
logger = LogiLogger.get_logger("health_monitor")


class HealthMonitor:
    """System health monitoring"""

    def __init__(self):
        self.db = None
        self.checks = []
        logger.info("Health Monitor initialized")

    def add_check(self, name: str, check_func, critical: bool = True):
        """Add health check"""
        self.checks.append({
            'name': name,
            'function': check_func,
            'critical': critical
        })

    def check_ollama_service(self) -> Dict[str, Any]:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            available = response.status_code == 200

            models = []
            if available:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]

            return {
                'status': 'healthy' if available else 'unhealthy',
                'available': available,
                'models': models,
                'url': config.OLLAMA_BASE_URL
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'available': False,
                'error': str(e)
            }

    def check_firebase_connection(self) -> Dict[str, Any]:
        """Check Firebase/Firestore connectivity"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()

            # Try to read from a collection
            collection_path = config.get_public_collection("drivers")
            docs = self.db.collection(collection_path).limit(1).stream()
            list(docs)  # Force execution

            return {
                'status': 'healthy',
                'connected': True,
                'project_id': config.FIREBASE_PROJECT_ID
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e)
            }

    def check_google_sheets_api(self) -> Dict[str, Any]:
        """Check Google Sheets API access"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds = service_account.Credentials.from_service_account_file(
                config.CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=creds)

            # Try to get sheet metadata
            metadata = service.spreadsheets().get(
                spreadsheetId=config.SRM_DISPATCH_SHEET_ID
            ).execute()

            return {
                'status': 'healthy',
                'accessible': True,
                'sheet_title': metadata.get('properties', {}).get('title', ''),
                'sheet_id': config.SRM_DISPATCH_SHEET_ID
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'accessible': False,
                'error': str(e)
            }

    def check_last_sync_time(self) -> Dict[str, Any]:
        """Check when last sync occurred"""
        try:
            if not self.db:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(config.CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()

            collection_path = config.get_public_collection("drivers")
            docs = self.db.collection(collection_path).order_by(
                'last_updated',
                direction=firestore.Query.DESCENDING
            ).limit(1).stream()

            last_sync = None
            for doc in docs:
                data = doc.to_dict()
                last_sync = data.get('last_updated')
                break

            if last_sync:
                # Parse ISO timestamp
                last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                age_minutes = (datetime.utcnow().replace(tzinfo=last_sync_dt.tzinfo) - last_sync_dt).total_seconds() / 60

                status = 'healthy'
                if age_minutes > config.SYNC_INTERVAL_MINUTES * 2:
                    status = 'warning'
                if age_minutes > config.SYNC_INTERVAL_MINUTES * 5:
                    status = 'unhealthy'

                return {
                    'status': status,
                    'last_sync': last_sync,
                    'age_minutes': round(age_minutes, 2)
                }
            else:
                return {
                    'status': 'warning',
                    'last_sync': None,
                    'message': 'No sync data found'
                }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_data_counts(self) -> Dict[str, Any]:
        """Check document counts in Firestore"""
        try:
            if not self.db:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(config.CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()

            drivers_path = config.get_public_collection("drivers")
            plants_path = config.get_public_collection("plants")

            driver_docs = list(self.db.collection(drivers_path).stream())
            plant_docs = list(self.db.collection(plants_path).stream())

            driver_count = len(driver_docs)
            plant_count = len(plant_docs)

            status = 'healthy'
            if driver_count == 0:
                status = 'warning'

            return {
                'status': status,
                'driver_count': driver_count,
                'plant_count': plant_count
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("Running health checks...")

        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }

        # Run standard checks
        standard_checks = [
            ('firebase', self.check_firebase_connection, True),
            ('google_sheets', self.check_google_sheets_api, True),
            ('ollama', self.check_ollama_service, False),
            ('last_sync', self.check_last_sync_time, True),
            ('data_counts', self.check_data_counts, True)
        ]

        critical_failures = 0

        for check_name, check_func, critical in standard_checks:
            try:
                logger.info(f"Running check: {check_name}")
                result = check_func()
                results['checks'][check_name] = result

                if result['status'] == 'unhealthy' and critical:
                    critical_failures += 1
                    results['overall_status'] = 'unhealthy'

            except Exception as e:
                logger.error(f"Check {check_name} failed: {e}")
                results['checks'][check_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                if critical:
                    critical_failures += 1
                    results['overall_status'] = 'unhealthy'

        results['critical_failures'] = critical_failures
        logger.info(f"Health checks complete - Overall: {results['overall_status']}")

        return results

    def print_report(self, results: Dict[str, Any]):
        """Print formatted health report"""
        print("\n" + "=" * 60)
        print("LOGIBOT HEALTH REPORT")
        print("=" * 60)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print("=" * 60)

        for check_name, check_result in results['checks'].items():
            status = check_result.get('status', 'unknown').upper()
            status_symbol = "✓" if status == "HEALTHY" else ("⚠" if status == "WARNING" else "✗")

            print(f"\n{status_symbol} {check_name.replace('_', ' ').title()}: {status}")

            for key, value in check_result.items():
                if key != 'status':
                    print(f"  - {key}: {value}")

        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    logger.info("LogiBot Health Monitor")

    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)

    # Run health checks
    monitor = HealthMonitor()
    results = monitor.run_all_checks()

    # Print report
    monitor.print_report(results)

    # Exit with appropriate code
    if results['overall_status'] == 'unhealthy':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
