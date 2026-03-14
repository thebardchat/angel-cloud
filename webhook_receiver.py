#!/usr/bin/env python3
"""
Webhook Receiver for Google Sheets Updates
Receives webhook notifications from Google Apps Script when sheets are updated.
Triggers immediate sync instead of waiting for scheduled interval.
"""

import hmac
import hashlib
from flask import Flask, request, jsonify
from datetime import datetime
import threading

from config import config
from logger import LogiLogger
from google_sheets_sync import sync_drivers, sync_plants, init_firebase, get_sheets_service

# Initialize logger
logger = LogiLogger.get_logger("webhook")

# Initialize Flask app
app = Flask(__name__)

# Global services
db = None
sheets_service = None


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature using HMAC"""
    if not config.WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not configured - skipping verification")
        return True

    expected_signature = hmac.new(
        config.WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def trigger_sync_async():
    """Trigger sync in background thread"""
    def run_sync():
        try:
            logger.info("Starting async sync from webhook")
            driver_stats = sync_drivers(sheets_service, db)
            plant_stats = sync_plants(sheets_service, db)

            total_synced = driver_stats['synced'] + plant_stats['synced']
            logger.info(f"Webhook-triggered sync complete - Synced: {total_synced}")

        except Exception as e:
            logger.error(f"Error in webhook-triggered sync: {e}", exc_info=True)

    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()


@app.route('/webhook/sheets', methods=['POST'])
def sheets_webhook():
    """Handle Google Sheets webhook"""
    try:
        # Get signature from header
        signature = request.headers.get('X-Webhook-Signature', '')

        # Verify signature
        if not verify_webhook_signature(request.data, signature):
            logger.warning(f"Invalid webhook signature from {request.remote_addr}")
            return jsonify({'error': 'Invalid signature'}), 401

        # Parse payload
        data = request.json
        logger.info(f"Received webhook: {data}")

        # Validate payload
        if not data or 'event' not in data:
            return jsonify({'error': 'Invalid payload'}), 400

        event_type = data.get('event')
        sheet_id = data.get('sheetId')
        timestamp = data.get('timestamp')

        logger.info(f"Webhook event: {event_type} - Sheet: {sheet_id} - Time: {timestamp}")

        # Trigger sync
        trigger_sync_async()

        return jsonify({
            'status': 'success',
            'message': 'Sync triggered',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'LogiBot Webhook Receiver',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test endpoint for webhook debugging"""
    logger.info(f"Test webhook received from {request.remote_addr}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {request.data}")

    return jsonify({
        'status': 'test_success',
        'received': request.json,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


def initialize_services():
    """Initialize global services"""
    global db, sheets_service
    logger.info("Initializing webhook receiver services...")

    db = init_firebase()
    sheets_service = get_sheets_service()

    logger.info("Webhook receiver services initialized")


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("LogiBot Webhook Receiver starting")
    logger.info(f"Port: {config.WEBHOOK_PORT}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info("=" * 60)

    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        return

    # Initialize services
    initialize_services()

    # Start Flask server
    logger.info(f"Starting webhook server on port {config.WEBHOOK_PORT}")
    app.run(
        host='0.0.0.0',
        port=config.WEBHOOK_PORT,
        debug=(config.ENVIRONMENT == 'development')
    )


if __name__ == "__main__":
    main()
