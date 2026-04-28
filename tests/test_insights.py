# tests/test_insights.py
"""Tests for auto-generated headline insights."""

import pytest
from src.insights import (
    decomposition_insight,
    gap_analysis_insight,
    benchmarking_insight,
)


def test_decomposition_insight():
    """decomposition_insight returns a plain-language headline about score drivers."""
    contributions = {
        "USP": {"AR": 32.0, "ER": 12.0, "CpP": 10.5, "HI": 7.5, "IRN": 4.0},
        "UNICAMP": {"AR": 28.0, "ER": 10.0, "CpP": 12.0, "HI": 9.0, "IRN": 6.0},
    }
    result = decomposition_insight(contributions, "Chemistry")
    assert isinstance(result, str)
    assert "Chemistry" in result
    assert len(result) > 20


def test_gap_analysis_insight():
    """gap_analysis_insight identifies the biggest opportunity."""
    opportunities = [
        {"indicator": "IRN", "gap_points": 3.2},
        {"indicator": "CpP", "gap_points": 1.8},
        {"indicator": "HI", "gap_points": 0.5},
    ]
    result = gap_analysis_insight("USP", "Chemistry", opportunities)
    assert "Rede Internacional de Pesquisa" in result
    assert "USP" in result
    assert "3.2" in result


def test_gap_analysis_insight_no_gaps():
    """gap_analysis_insight handles case where focus university leads all indicators."""
    result = gap_analysis_insight("USP", "Chemistry", [])
    assert isinstance(result, str)
    assert "USP" in result


def test_benchmarking_insight():
    """benchmarking_insight identifies most common area of outperformance."""
    peer_deltas = {
        "Peer A": {"CpP": 5.0, "HI": -2.0, "IRN": 8.0},
        "Peer B": {"CpP": 3.0, "HI": 1.0, "IRN": 6.0},
        "Peer C": {"CpP": -1.0, "HI": 4.0, "IRN": 10.0},
    }
    result = benchmarking_insight("USP", "Life Sciences & Medicine", peer_deltas)
    assert isinstance(result, str)
    assert "Rede Internacional de Pesquisa" in result  # All 3 peers outperform on IRN
