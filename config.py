#!/usr/bin/env python3
"""
Centralized configuration management for Angel Cloud / LogiBot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Base paths
    BASE_DIR = Path(__file__).parent
    CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

    # Firebase
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')

    # Application
    APP_ID = os.getenv('APP_ID', 'logibot')
    USER_ID = os.getenv('USER_ID', 'shane_brazelton')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # Google Sheets
    SRM_DISPATCH_SHEET_ID = os.getenv('SRM_DISPATCH_SHEET_ID', '1V_So_9yzvLBAMjLu0dhtL_7mxCqudMUrkrH8iqRHuJU')
    LIFE_SHEET_ID = os.getenv('LIFE_SHEET_ID', '')

    # Webhook
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8080'))

    # Ollama
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/logibot.log')

    # Sync
    SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', '5'))
    ENABLE_AUTO_SYNC = os.getenv('ENABLE_AUTO_SYNC', 'true').lower() == 'true'

    # Haul Rate Constants
    HAUL_RATE_BASE = float(os.getenv('HAUL_RATE_BASE', '130.0'))
    HAUL_RATE_TIME_BASE = float(os.getenv('HAUL_RATE_TIME_BASE', '60.0'))
    HAUL_RATE_TON_BASE = float(os.getenv('HAUL_RATE_TON_BASE', '25.0'))
    HAUL_RATE_MINIMUM = float(os.getenv('HAUL_RATE_MINIMUM', '6.00'))
    HAUL_RATE_ROUND_INCREMENT = float(os.getenv('HAUL_RATE_ROUND_INCREMENT', '0.50'))

    # Firestore Collections
    @classmethod
    def get_public_collection(cls, collection_name: str) -> str:
        """Get public data collection path"""
        return f"artifacts/{cls.APP_ID}/public/data/{collection_name}"

    @classmethod
    def get_private_collection(cls, collection_name: str, user_id: str = None) -> str:
        """Get private user collection path"""
        uid = user_id or cls.USER_ID
        return f"artifacts/{cls.APP_ID}/users/{uid}/{collection_name}"

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        errors = []

        if not Path(cls.CREDENTIALS_PATH).exists():
            errors.append(f"Credentials file not found: {cls.CREDENTIALS_PATH}")

        if not cls.SRM_DISPATCH_SHEET_ID:
            errors.append("SRM_DISPATCH_SHEET_ID not set")

        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# Singleton instance
config = Config()
