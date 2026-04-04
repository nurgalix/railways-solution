"""
Unit tests for the telemetry simulator.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.health_index import load_config, reload_config
from services.alert_engine import AlertEngine


class TestAlertEngine:
    """Test alert detection and debouncing."""

    def setup_method(self):
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "health_config.yaml"
        )
        reload_config()
        load_config(config_path)

    def test_no_alerts_for_normal_values(self):
        """Normal telemetry should produce no alerts."""
        engine = AlertEngine(debounce_seconds=0)
        telemetry = {
            "speed": 80,
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 80,
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts = engine.check(telemetry)
        assert len(alerts) == 0

    def test_warning_alert_generated(self):
        """Value in warning range should generate a warning."""
        engine = AlertEngine(debounce_seconds=0)
        telemetry = {
            "speed": 130,  # Warning range [120, 140]
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 80,
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts = engine.check(telemetry)
        speed_alerts = [a for a in alerts if a["parameter"] == "speed"]
        assert len(speed_alerts) == 1
        assert speed_alerts[0]["severity"] == "warning"

    def test_critical_alert_generated(self):
        """Value in critical range should generate a critical alert."""
        engine = AlertEngine(debounce_seconds=0)
        telemetry = {
            "speed": 80,
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 115,  # Critical range [105, 130]
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts = engine.check(telemetry)
        temp_alerts = [a for a in alerts if a["parameter"] == "coolant_temp"]
        assert len(temp_alerts) == 1
        assert temp_alerts[0]["severity"] == "critical"

    def test_alert_has_recommendation(self):
        """Alert should include a recommendation."""
        engine = AlertEngine(debounce_seconds=0)
        telemetry = {
            "speed": 80,
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 100,  # Warning range
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts = engine.check(telemetry)
        temp_alerts = [a for a in alerts if a["parameter"] == "coolant_temp"]
        if temp_alerts:
            assert temp_alerts[0]["recommendation"] is not None
            assert len(temp_alerts[0]["recommendation"]) > 0

    def test_debouncing(self):
        """Same alert should not fire twice within debounce window."""
        engine = AlertEngine(debounce_seconds=60)
        telemetry = {
            "speed": 130,
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 80,
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts1 = engine.check(telemetry)
        alerts2 = engine.check(telemetry)

        # First call should fire, second should be debounced
        speed_alerts_1 = [a for a in alerts1 if a["parameter"] == "speed"]
        speed_alerts_2 = [a for a in alerts2 if a["parameter"] == "speed"]
        assert len(speed_alerts_1) >= 1
        assert len(speed_alerts_2) == 0

    def test_inverted_parameter_alert(self):
        """Low fuel_level should generate an alert."""
        engine = AlertEngine(debounce_seconds=0)
        telemetry = {
            "speed": 80,
            "fuel_level": 10,  # Below critical range [0, 15]
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 80,
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        alerts = engine.check(telemetry)
        fuel_alerts = [a for a in alerts if a["parameter"] == "fuel_level"]
        assert len(fuel_alerts) >= 1
