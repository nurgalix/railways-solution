"""
Unit tests for the Health Index calculation engine.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.health_index import (
    _score_parameter,
    calculate_health_index,
    load_config,
    reload_config,
)


class TestScoreParameter:
    """Test per-parameter scoring logic."""

    def test_normal_range_high_is_bad(self):
        """Value within normal range should score 100."""
        score, status = _score_parameter(
            value=80,
            normal_range=[0, 120],
            warning_range=[120, 140],
            critical_range=[140, 200],
        )
        assert score == 100.0
        assert status == "normal"

    def test_warning_range_high_is_bad(self):
        """Value in warning range should score between 50 and 100."""
        score, status = _score_parameter(
            value=130,
            normal_range=[0, 120],
            warning_range=[120, 140],
            critical_range=[140, 200],
        )
        assert 50 < score < 100
        assert status == "warning"

    def test_critical_range_high_is_bad(self):
        """Value in critical range should score between 0 and 50."""
        score, status = _score_parameter(
            value=170,
            normal_range=[0, 120],
            warning_range=[120, 140],
            critical_range=[140, 200],
        )
        assert 0 < score < 50
        assert status == "critical"

    def test_beyond_critical(self):
        """Value beyond critical max should score 0."""
        score, status = _score_parameter(
            value=250,
            normal_range=[0, 120],
            warning_range=[120, 140],
            critical_range=[140, 200],
        )
        assert score == 0.0
        assert status == "critical"

    def test_inverted_normal(self):
        """Inverted parameter (low is bad): value in normal range = 100."""
        score, status = _score_parameter(
            value=50,
            normal_range=[30, 100],
            warning_range=[15, 30],
            critical_range=[0, 15],
        )
        assert score == 100.0
        assert status == "normal"

    def test_inverted_warning(self):
        """Inverted parameter: value in warning range scores 50-100."""
        score, status = _score_parameter(
            value=22,
            normal_range=[30, 100],
            warning_range=[15, 30],
            critical_range=[0, 15],
        )
        assert 50 < score < 100
        assert status == "warning"

    def test_inverted_critical(self):
        """Inverted parameter: value in critical range scores 0-50."""
        score, status = _score_parameter(
            value=7,
            normal_range=[30, 100],
            warning_range=[15, 30],
            critical_range=[0, 15],
        )
        assert 0 < score < 50
        assert status == "critical"


class TestCalculateHealthIndex:
    """Test the full Health Index calculation."""

    def setup_method(self):
        """Load the YAML config before each test."""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "health_config.yaml"
        )
        reload_config()
        load_config(config_path)

    def test_all_nominal_values(self):
        """All parameters in normal range → high index."""
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
        result = calculate_health_index(telemetry)
        assert result.index >= 85  # Should be category A
        assert result.category == "A"
        assert result.label == "Normal"

    def test_one_critical_parameter(self):
        """One critical parameter should reduce the index."""
        telemetry = {
            "speed": 80,
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 115,  # Critical!
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        result = calculate_health_index(telemetry)
        assert result.index < 95  # Should be lower than all-normal

    def test_alert_penalty(self):
        """Active alerts should reduce the index."""
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
        no_alerts = calculate_health_index(telemetry, active_alerts=[])
        with_alerts = calculate_health_index(
            telemetry,
            active_alerts=[
                {"severity": "warning"},
                {"severity": "critical"},
            ],
        )
        assert with_alerts.index < no_alerts.index
        assert no_alerts.index - with_alerts.index >= 15  # At least critical penalty

    def test_top_factors_returned(self):
        """Top factors should be returned sorted by impact."""
        telemetry = {
            "speed": 150,  # Warning/critical
            "fuel_level": 70,
            "fuel_consumption": 12,
            "oil_pressure": 4.5,
            "brake_pressure": 5.5,
            "coolant_temp": 110,  # Critical
            "exhaust_temp": 350,
            "bearing_temp": 55,
            "voltage": 3100,
            "current": 800,
        }
        result = calculate_health_index(telemetry)
        assert len(result.top_factors) > 0
        # Top factor should be the worst one
        worst = result.top_factors[0]
        assert worst.impact < 0

    def test_all_critical_gives_low_index(self):
        """All parameters critical → very low index."""
        telemetry = {
            "speed": 180,
            "fuel_level": 5,
            "fuel_consumption": 45,
            "oil_pressure": 1.0,
            "brake_pressure": 2.5,
            "coolant_temp": 120,
            "exhaust_temp": 600,
            "bearing_temp": 100,
            "voltage": 2200,
            "current": 1400,
        }
        result = calculate_health_index(telemetry)
        assert result.index < 50
        assert result.category in ("D", "E")

    def test_index_clamped_to_zero(self):
        """Index should never go below 0."""
        telemetry = {
            "speed": 200,
            "fuel_level": 0,
            "fuel_consumption": 50,
            "oil_pressure": 0.5,
            "brake_pressure": 1.0,
            "coolant_temp": 130,
            "exhaust_temp": 650,
            "bearing_temp": 110,
            "voltage": 2000,
            "current": 1500,
        }
        result = calculate_health_index(
            telemetry,
            active_alerts=[{"severity": "critical"}] * 10,
        )
        assert result.index >= 0
