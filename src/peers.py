"""Peer matching logic — manual and structural."""

from pathlib import Path

import pandas as pd


def load_manual_peers(peers_path: str = "data/peers.csv") -> dict:
    """Load manual peer definitions from CSV.

    Returns dict mapping university name to list of peer institution names.
    Returns empty dict if file doesn't exist.
    """
    if not Path(peers_path).exists():
        return {}

    try:
        df = pd.read_csv(peers_path)
    except Exception:
        return {}

    if df.empty or "university" not in df.columns or "peer" not in df.columns:
        return {}

    result = {}
    for _, row in df.iterrows():
        uni = str(row["university"]).strip()
        peer = str(row["peer"]).strip()
        if uni and peer and uni != "nan" and peer != "nan":
            if uni not in result:
                result[uni] = []
            result[uni].append(peer)
    return result


def find_structural_peers(
    focus_university: str,
    faculty_area: str,
    all_data: pd.DataFrame,
    output_band: float = 0.3,
    max_rank_improvement: int = 20,
    top_n: int = 5,
) -> pd.DataFrame:
    """Find structurally similar universities that score slightly better.

    Args:
        focus_university: name of the university to find peers for.
        faculty_area: faculty area to compare within.
        all_data: DataFrame with columns: institution, faculty_area,
            scholarly_output, overall_rank.
        output_band: fraction tolerance for scholarly output similarity
            (0.3 = within +/-30%).
        max_rank_improvement: max positions higher in rank to consider.
        top_n: max number of peers to return.

    Returns DataFrame of matching peers, sorted by rank (best first).
    """
    area_data = all_data[all_data["faculty_area"] == faculty_area].copy()

    focus_row = area_data[area_data["institution"] == focus_university]
    if focus_row.empty:
        return pd.DataFrame()

    focus_output = focus_row["scholarly_output"].iloc[0]
    focus_rank = focus_row["overall_rank"].iloc[0]

    # Filter: similar output, better rank (but not too much better)
    min_output = focus_output * (1 - output_band)
    max_output = focus_output * (1 + output_band)
    min_rank = focus_rank - max_rank_improvement  # lower rank number = better

    peers = area_data[
        (area_data["institution"] != focus_university)
        & (area_data["scholarly_output"] >= min_output)
        & (area_data["scholarly_output"] <= max_output)
        & (area_data["overall_rank"] < focus_rank)
        & (area_data["overall_rank"] >= max(1, min_rank))
    ].copy()

    peers = peers.sort_values("overall_rank").head(top_n)
    return peers.reset_index(drop=True)
