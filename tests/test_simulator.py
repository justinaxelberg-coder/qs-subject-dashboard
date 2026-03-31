# tests/test_simulator.py
"""Tests for score simulation logic."""

import pytest
from src.simulator import simulate_score_change, build_score_mapping


def test_build_score_mapping():
    """build_score_mapping creates a linear interpolation from data points."""
    data_points = [
        {"raw_value": 100, "qs_score": 50.0},
        {"raw_value": 200, "qs_score": 75.0},
        {"raw_value": 300, "qs_score": 90.0},
    ]
    mapping = build_score_mapping(data_points)
    assert mapping(150) == pytest.approx(62.5, abs=1.0)
    assert mapping(200) == pytest.approx(75.0, abs=0.1)


def test_build_score_mapping_single_point():
    """build_score_mapping with one data point returns that score for any input."""
    data_points = [{"raw_value": 100, "qs_score": 50.0}]
    mapping = build_score_mapping(data_points)
    assert mapping(100) == pytest.approx(50.0)
    assert mapping(200) == pytest.approx(50.0)


def test_simulate_score_change():
    """simulate_score_change returns current score, simulated score, and delta."""
    current_scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}
    adjusted_scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 55.0}

    result = simulate_score_change(current_scores, adjusted_scores, weights)
    assert "current_total" in result
    assert "simulated_total" in result
    assert "delta" in result
    assert result["delta"] == pytest.approx(1.5)


def test_simulate_score_change_no_change():
    """simulate_score_change returns 0 delta when scores unchanged."""
    scores = {"AR": 80.0, "ER": 60.0}
    weights = {"AR": 50, "ER": 50}
    result = simulate_score_change(scores, scores, weights)
    assert result["delta"] == pytest.approx(0.0)
