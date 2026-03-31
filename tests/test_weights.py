"""Tests for weights lookup and weighted score calculations."""

import pytest
from src.weights import load_weights, get_subject_weights, calculate_weighted_contributions


def test_load_weights_returns_dict(tmp_path):
    """load_weights reads weights.json and returns dict with 'broad' and 'subjects' keys."""
    import json
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(json.dumps({
        "broad": {"Natural Sciences": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}},
        "subjects": {"Chemistry": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}},
    }))
    result = load_weights(str(weights_file))
    assert "broad" in result
    assert "subjects" in result
    assert "Chemistry" in result["subjects"]


def test_get_subject_weights_known_subject(sample_weights):
    """get_subject_weights returns subject-specific weights when subject exists."""
    result = get_subject_weights(sample_weights, "Chemistry")
    assert result == {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}


def test_get_subject_weights_falls_back_to_broad(sample_weights):
    """get_subject_weights falls back to broad faculty area weights for unknown subjects."""
    result = get_subject_weights(sample_weights, "Unknown Subject", faculty_area="Natural Sciences")
    assert result == {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}


def test_get_subject_weights_missing_raises():
    """get_subject_weights raises KeyError when neither subject nor faculty area found."""
    weights = {"broad": {}, "subjects": {}}
    with pytest.raises(KeyError):
        get_subject_weights(weights, "Unknown", faculty_area="Unknown")


def test_calculate_weighted_contributions():
    """calculate_weighted_contributions returns indicator_code -> weighted_points dict."""
    scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}
    result = calculate_weighted_contributions(scores, weights)
    assert result["AR"] == pytest.approx(32.0)
    assert result["ER"] == pytest.approx(12.0)
    assert result["CpP"] == pytest.approx(10.5)
    assert result["HI"] == pytest.approx(7.5)
    assert result["IRN"] == pytest.approx(4.0)


def test_calculate_weighted_contributions_missing_indicator():
    """Indicators missing from weights are treated as 0 contribution."""
    scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 70, "ER": 30}
    result = calculate_weighted_contributions(scores, weights)
    assert result["AR"] == pytest.approx(56.0)
    assert result["ER"] == pytest.approx(18.0)
    assert result.get("CpP", 0) == 0
    assert result.get("HI", 0) == 0
    assert result.get("IRN", 0) == 0
