# tests/test_peers.py
"""Tests for peer matching logic."""

import pandas as pd
import pytest
from src.peers import load_manual_peers, find_structural_peers


def test_load_manual_peers(tmp_path):
    """load_manual_peers reads peers.csv and returns dict mapping university to peer list."""
    peers_csv = tmp_path / "peers.csv"
    peers_csv.write_text(
        "university,peer\n"
        "Universidade de São Paulo,University of Barcelona\n"
        "Universidade de São Paulo,National Autonomous University of Mexico\n"
        "UNICAMP,Technical University of Munich\n"
    )
    result = load_manual_peers(str(peers_csv))
    assert "Universidade de São Paulo" in result
    assert len(result["Universidade de São Paulo"]) == 2
    assert "University of Barcelona" in result["Universidade de São Paulo"]
    assert "UNICAMP" in result
    assert len(result["UNICAMP"]) == 1


def test_load_manual_peers_missing_file(tmp_path):
    """load_manual_peers returns empty dict when file doesn't exist."""
    result = load_manual_peers(str(tmp_path / "nonexistent.csv"))
    assert result == {}


def test_find_structural_peers():
    """find_structural_peers finds universities with similar output volume scoring slightly better."""
    all_universities = pd.DataFrame({
        "institution": ["USP", "Peer A", "Peer B", "Peer C", "Far Away", "Much Worse"],
        "faculty_area": ["Natural Sciences"] * 6,
        "scholarly_output": [20000, 18000, 22000, 19000, 50000, 21000],
        "overall_rank": [85, 70, 65, 80, 10, 120],
    })
    result = find_structural_peers(
        focus_university="USP",
        faculty_area="Natural Sciences",
        all_data=all_universities,
        output_band=0.3,
        max_rank_improvement=20,
        top_n=5,
    )
    assert "Peer A" in result["institution"].values
    assert "Peer B" in result["institution"].values
    assert "Peer C" in result["institution"].values
    assert "Far Away" not in result["institution"].values
    assert "Much Worse" not in result["institution"].values
