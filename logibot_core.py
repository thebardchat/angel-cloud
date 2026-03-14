#!/usr/bin/env python3
"""
LogiBot Core Orchestrator
Main execution loop with Ollama AI integration for SRM Dispatch automation.
"""

import sys
import time
import signal
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from config import config
from logger import LogiLogger, log_execution
from google_sheets_sync import sync_drivers, sync_plants, init_firebase, get_sheets_service

# Initialize logger
logger = LogiLogger.get_logger("logibot_core")

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {sig}. Initiating graceful shutdown...")
    shutdown_requested = True


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class OllamaClient:
    """Client for interacting with Ollama local LLM"""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL
        logger.info(f"Initialized Ollama client: {self.base_url} - Model: {self.model}")

    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.warning(f"Ollama service not available: {e}")
            return False

    def generate(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            if context:
                payload["context"] = context

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Failed to generate response: {e}")
            return None

    def analyze_driver_data(self, driver_stats: Dict[str, Any]) -> Optional[str]:
        """Use AI to analyze driver sync results"""
        prompt = f"""Analyze the following driver sync statistics and provide brief insights:

Synced: {driver_stats.get('synced', 0)}
Errors: {driver_stats.get('errors', 0)}
Skipped: {driver_stats.get('skipped', 0)}

Provide a 1-2 sentence analysis."""

        return self.generate(prompt)


class LogiBotOrchestrator:
    """Main orchestrator for LogiBot system"""

    def __init__(self):
        self.db = None
        self.sheets_service = None
        self.ollama_client = None
        self.last_sync_time = None
        logger.info("LogiBot Orchestrator initialized")

    @log_execution
    def initialize_services(self):
        """Initialize all required services"""
        logger.info("Initializing LogiBot services...")

        # Firebase
        self.db = init_firebase()
        logger.info("✓ Firebase initialized")

        # Google Sheets API
        self.sheets_service = get_sheets_service()
        logger.info("✓ Google Sheets API initialized")

        # Ollama (optional - system works without it)
        self.ollama_client = OllamaClient()
        if self.ollama_client.is_available():
            logger.info("✓ Ollama AI available")
        else:
            logger.warning("⚠ Ollama AI not available - continuing without AI features")

        logger.info("All services initialized successfully")

    @log_execution
    def run_sync_cycle(self) -> Dict[str, Any]:
        """Execute one sync cycle"""
        logger.info("Starting sync cycle")

        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'drivers': {'synced': 0, 'errors': 0, 'skipped': 0},
            'plants': {'synced': 0, 'errors': 0, 'skipped': 0}
        }

        try:
            # Sync drivers
            driver_stats = sync_drivers(self.sheets_service, self.db)
            results['drivers'] = driver_stats

            # Sync plants
            plant_stats = sync_plants(self.sheets_service, self.db)
            results['plants'] = plant_stats

            # AI analysis (if available)
            if self.ollama_client and self.ollama_client.is_available():
                analysis = self.ollama_client.analyze_driver_data(driver_stats)
                if analysis:
                    logger.info(f"AI Analysis: {analysis}")
                    results['ai_analysis'] = analysis

            self.last_sync_time = datetime.utcnow()
            results['success'] = True

        except Exception as e:
            logger.error(f"Sync cycle failed: {e}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)

        return results

    @log_execution
    def run_continuous(self):
        """Run continuous sync loop"""
        global shutdown_requested

        logger.info("Starting continuous sync mode")
        logger.info(f"Sync interval: {config.SYNC_INTERVAL_MINUTES} minutes")

        while not shutdown_requested:
            try:
                # Run sync cycle
                results = self.run_sync_cycle()

                if results['success']:
                    total_synced = results['drivers']['synced'] + results['plants']['synced']
                    logger.info(f"Sync cycle complete - Total synced: {total_synced}")
                else:
                    logger.error("Sync cycle failed")

                # Wait for next cycle
                logger.info(f"Next sync in {config.SYNC_INTERVAL_MINUTES} minutes")
                for _ in range(config.SYNC_INTERVAL_MINUTES * 60):
                    if shutdown_requested:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error in continuous loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying

        logger.info("Continuous sync mode stopped")

    @log_execution
    def run_once(self):
        """Run sync once and exit"""
        logger.info("Running one-time sync")
        results = self.run_sync_cycle()

        if results['success']:
            logger.info("One-time sync completed successfully")
            return 0
        else:
            logger.error("One-time sync failed")
            return 1


def print_banner():
    """Print LogiBot startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                      LOGIBOT v1.0                         ║
║          Angel Cloud Intelligence Platform                ║
║                                                           ║
║  SRM Dispatch Automation • Ollama AI • Firestore         ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


@log_execution
def main():
    """Main entry point"""
    print_banner()

    logger.info("=" * 60)
    logger.info(f"LogiBot starting at {datetime.utcnow().isoformat()}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"App ID: {config.APP_ID}")
    logger.info(f"Auto-sync: {config.ENABLE_AUTO_SYNC}")
    logger.info("=" * 60)

    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)

    try:
        # Initialize orchestrator
        orchestrator = LogiBotOrchestrator()
        orchestrator.initialize_services()

        # Run mode
        if config.ENABLE_AUTO_SYNC:
            orchestrator.run_continuous()
        else:
            exit_code = orchestrator.run_once()
            sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("LogiBot interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
