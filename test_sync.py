#!/usr/bin/env python3
"""
Unit tests for LogiBot sync functionality
Run with: pytest test_sync.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from config import config
from google_sheets_sync import calculate_haul_rate


class TestHaulRateCalculation:
    """Test haul rate calculation logic"""

    def test_minimum_rate(self):
        """Test minimum rate enforcement"""
        rate = calculate_haul_rate(0)
        assert rate == 6.00

        rate = calculate_haul_rate(-10)
        assert rate == 6.00

        rate = calculate_haul_rate(None)
        assert rate == 6.00

    def test_formula_accuracy(self):
        """Test haul rate formula: ($130/60) * RTM / 25"""
        # For 60 minute round trip:
        # ($130 / 60) * 60 / 25 = 5.2
        # Rounded up to nearest $0.50 = 5.50
        # But minimum is $6.00, so result is $6.00
        rate = calculate_haul_rate(60)
        assert rate == 6.00

        # For 100 minute round trip:
        # ($130 / 60) * 100 / 25 = 8.67
        # Rounded up to nearest $0.50 = 9.00
        rate = calculate_haul_rate(100)
        assert rate == 9.00

    def test_rounding_behavior(self):
        """Test rounding to nearest $0.50"""
        # Test value that should round up
        # RTM = 80: ($130/60) * 80 / 25 = 6.93 → 7.00
        rate = calculate_haul_rate(80)
        assert rate == 7.00

        # RTM = 70: ($130/60) * 70 / 25 = 6.07 → 6.50
        rate = calculate_haul_rate(70)
        assert rate == 6.50

    def test_known_values(self):
        """Test with known real-world values"""
        test_cases = [
            (30, 6.00),   # Below minimum
            (50, 6.00),   # Below minimum
            (75, 6.50),   # Just above minimum
            (90, 8.00),   # Typical value
            (120, 10.50), # Higher value
            (150, 13.00), # High value
        ]

        for rtm, expected_rate in test_cases:
            actual_rate = calculate_haul_rate(rtm)
            assert actual_rate == expected_rate, f"RTM {rtm}: expected ${expected_rate}, got ${actual_rate}"


class TestConfig:
    """Test configuration management"""

    def test_config_values(self):
        """Test that config has required values"""
        assert config.APP_ID
        assert config.SRM_DISPATCH_SHEET_ID
        assert config.HAUL_RATE_BASE == 130.0
        assert config.HAUL_RATE_TIME_BASE == 60.0
        assert config.HAUL_RATE_TON_BASE == 25.0
        assert config.HAUL_RATE_MINIMUM == 6.00
        assert config.HAUL_RATE_ROUND_INCREMENT == 0.50

    def test_collection_paths(self):
        """Test Firestore collection path generation"""
        drivers_path = config.get_public_collection("drivers")
        assert "artifacts" in drivers_path
        assert "public" in drivers_path
        assert "drivers" in drivers_path

        finance_path = config.get_private_collection("finance")
        assert "artifacts" in finance_path
        assert "users" in finance_path
        assert "finance" in finance_path


class TestSyncFunctions:
    """Test sync functions with mocked dependencies"""

    @patch('google_sheets_sync.get_sheets_service')
    @patch('google_sheets_sync.init_firebase')
    def test_sync_drivers_empty_sheet(self, mock_firebase, mock_sheets):
        """Test driver sync with empty sheet"""
        from google_sheets_sync import sync_drivers

        # Mock empty response
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': []
        }
        mock_sheets.return_value = mock_service

        mock_db = Mock()
        mock_firebase.return_value = mock_db

        # Run sync
        stats = sync_drivers(mock_service, mock_db)

        # Verify results
        assert stats['synced'] == 0
        assert stats['errors'] == 0

    @patch('google_sheets_sync.get_sheets_service')
    @patch('google_sheets_sync.init_firebase')
    def test_sync_drivers_with_data(self, mock_firebase, mock_sheets):
        """Test driver sync with sample data"""
        from google_sheets_sync import sync_drivers

        # Mock sheet response with sample driver data
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': [
                ['John Doe', '90', 'active'],
                ['Jane Smith', '120', 'active'],
                ['Bob Wilson', '75', 'inactive']
            ]
        }
        mock_sheets.return_value = mock_service

        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_doc = Mock()
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc
        mock_firebase.return_value = mock_db

        # Run sync
        stats = sync_drivers(mock_service, mock_db)

        # Verify results
        assert stats['synced'] == 3
        assert stats['errors'] == 0
        assert mock_doc.set.call_count == 3


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response"""
    return {
        "response": "Test AI response",
        "model": "llama3.2"
    }


class TestOllamaIntegration:
    """Test Ollama AI integration"""

    @patch('requests.get')
    def test_ollama_availability_check(self, mock_get):
        """Test Ollama service availability check"""
        from logibot_core import OllamaClient

        # Mock successful response
        mock_get.return_value.status_code = 200
        client = OllamaClient()
        assert client.is_available() is True

        # Mock failed response
        mock_get.return_value.status_code = 404
        assert client.is_available() is False

    @patch('requests.post')
    @patch('requests.get')
    def test_ollama_generate(self, mock_get, mock_post):
        """Test Ollama text generation"""
        from logibot_core import OllamaClient

        # Mock availability check
        mock_get.return_value.status_code = 200

        # Mock generation response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "Test response"
        }

        client = OllamaClient()
        response = client.generate("Test prompt")
        assert response == "Test response"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
