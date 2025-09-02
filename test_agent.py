#!/usr/bin/env python3
"""
Basic test for the Solarmax agent functionality.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open


def mock_open_side_effect(*args, **kwargs):
    """Mock open function to avoid file system access during tests."""
    raise FileNotFoundError("Mocked file not found")


# Mock environment variables and config files before importing
os.environ["INVERTER_IP"] = "192.168.1.100"
os.environ["MQTT_BROKER_IP"] = "192.168.1.10"
os.environ["MQTT_INVERTER_TOPIC"] = "test/topic"

# Mock config file loading
with patch("builtins.open", side_effect=mock_open_side_effect):
    with patch("os.path.exists", return_value=False):
        # Add the src directory to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "python"))

        from agent import (
            build_request,
            calculate_checksum,
            map_data_value,
            convert_to_json,
            FIELD_MAP_INVERTER,
            STATUS_CODES,
            ALARM_CODES,
        )


class TestSolarmaxAgent(unittest.TestCase):

    def test_checksum_calculation(self):
        """Test checksum calculation."""
        test_data = "FB;01;31|64:PAC;PDC;SAL;SYS"
        checksum = calculate_checksum(test_data)
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 4)  # Should be 4-character hex

    def test_build_request(self):
        """Test request building."""
        test_map = {"PAC": "AC Power", "PDC": "DC Power"}
        request = build_request(test_map)

        self.assertIn("PAC", request)
        self.assertIn("PDC", request)
        self.assertTrue(request.startswith("{FB;01;"))
        self.assertTrue(request.endswith("}"))

    def test_map_data_value(self):
        """Test data value mapping."""
        # Test power value (should be divided by 2)
        self.assertEqual(map_data_value("PAC", 1000), 500.0)

        # Test voltage value (should be divided by 10)
        self.assertEqual(map_data_value("UL1", 2300), 230.0)

        # Test current value (should be divided by 100)
        self.assertEqual(map_data_value("IL1", 500), 5.0)

        # Test status code
        self.assertEqual(map_data_value("SYS", 20001), "In Betrieb")

        # Test alarm code
        self.assertEqual(map_data_value("SAL", 0), "kein Fehler")

        # Test unknown status
        self.assertEqual(map_data_value("SYS", 99999), "Unknown Status Code")

    def test_convert_to_json(self):
        """Test JSON conversion."""
        test_data = "some_prefix:PAC=1F40;PDC=1388;SAL=0;SYS=4E21,0|checksum"
        test_map = {
            "PAC": "AC Power (W)",
            "PDC": "DC Power (W)",
            "SAL": "Alarm Codes",
            "SYS": "Status Code",
        }

        result = convert_to_json(test_map, test_data)

        self.assertIn("PAC", result)
        self.assertIn("PDC", result)
        self.assertIn("SAL", result)
        self.assertIn("SYS", result)

        # Check structure
        self.assertIn("Value", result["PAC"])
        self.assertIn("Description", result["PAC"])
        self.assertIn("Raw Value", result["PAC"])

        # Check converted values
        self.assertEqual(result["PAC"]["Value"], 4000.0)  # 0x1F40 / 2
        self.assertEqual(result["SAL"]["Value"], "kein Fehler")  # 0 = no error

    def test_field_map_completeness(self):
        """Test that field map contains expected fields."""
        expected_fields = [
            "KDY",
            "KMT",
            "KYR",
            "KT0",  # Energy fields
            "PAC",
            "PDC",
            "PD01",
            "PD02",  # Power fields
            "UL1",
            "UL2",
            "UL3",  # AC voltage fields
            "IL1",
            "IL2",
            "IL3",  # AC current fields
            "SAL",
            "SYS",  # Status fields
        ]

        for field in expected_fields:
            self.assertIn(field, FIELD_MAP_INVERTER)

    def test_status_and_alarm_codes(self):
        """Test that status and alarm codes are properly defined."""
        self.assertIn(20000, STATUS_CODES)
        self.assertIn(20001, STATUS_CODES)
        self.assertIn(0, ALARM_CODES)
        self.assertIn(1, ALARM_CODES)


if __name__ == "__main__":
    unittest.main()
