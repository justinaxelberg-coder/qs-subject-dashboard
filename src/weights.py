"""Weight lookups and weighted score calculations."""

import json
from pathlib import Path
from typing import Optional


def load_weights(weights_path: str = "data/weights.json") -> dict:
    """Load weights from JSON file.

    Returns dict with 'broad' and 'subjects' keys.
    """
    with open(weights_path, "r") as f:
        return json.load(f)


def get_subject_weights(
    weights: dict, subject: str, faculty_area: Optional[str] = None
) -> dict:
    """Get indicator weights for a subject.

    Looks up subject-specific weights first. Falls back to broad faculty area
    weights if subject not found and faculty_area is provided.

    Returns dict mapping indicator codes (AR, ER, CpP, HI, IRN) to weight
    percentages (e.g., {"AR": 40, "ER": 20, ...}).

    Raises KeyError if neither subject nor faculty area found.
    """
    if subject in weights["subjects"]:
        return weights["subjects"][subject]
    if faculty_area and faculty_area in weights["broad"]:
        return weights["broad"][faculty_area]
    raise KeyError(
        f"No weights found for subject '{subject}'"
        + (f" or faculty area '{faculty_area}'" if faculty_area else "")
    )


def calculate_weighted_contributions(
    scores: dict, weights: dict
) -> dict:
    """Calculate each indicator's weighted contribution to the overall score.

    Args:
        scores: dict mapping indicator codes to QS scores (0-100).
        weights: dict mapping indicator codes to weight percentages.

    Returns:
        dict mapping indicator codes to weighted points
        (score * weight / 100).
    """
    result = {}
    for indicator in ["AR", "ER", "CpP", "HI", "IRN"]:
        weight = weights.get(indicator, 0)
        score = scores.get(indicator, 0)
        if weight > 0:
            result[indicator] = score * weight / 100
    return result
