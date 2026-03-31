"""Score simulation logic for what-if analysis."""

from typing import Callable
import numpy as np


def build_score_mapping(data_points: list[dict]) -> Callable[[float], float]:
    """Build a linear interpolation function from raw values to QS scores.

    Args:
        data_points: list of dicts with 'raw_value' and 'qs_score' keys.

    Returns:
        callable that takes a raw value and returns estimated QS score.
    """
    if not data_points:
        return lambda x: 0.0

    if len(data_points) == 1:
        score = data_points[0]["qs_score"]
        return lambda x: score

    # Sort by raw value
    sorted_points = sorted(data_points, key=lambda p: p["raw_value"])
    raw_values = [p["raw_value"] for p in sorted_points]
    qs_scores = [p["qs_score"] for p in sorted_points]

    def interpolate(x: float) -> float:
        return float(np.interp(x, raw_values, qs_scores))

    return interpolate


def simulate_score_change(
    current_scores: dict,
    adjusted_scores: dict,
    weights: dict,
) -> dict:
    """Calculate the impact of changing indicator scores.

    Args:
        current_scores: dict mapping indicator codes to current QS scores.
        adjusted_scores: dict mapping indicator codes to adjusted QS scores.
        weights: dict mapping indicator codes to weight percentages.

    Returns dict with:
        current_total: current weighted total
        simulated_total: simulated weighted total
        delta: difference (simulated - current)
        indicator_deltas: dict of per-indicator weighted point changes
    """
    current_total = 0.0
    simulated_total = 0.0
    indicator_deltas = {}

    for indicator, weight in weights.items():
        w = weight / 100.0
        current = current_scores.get(indicator, 0.0)
        adjusted = adjusted_scores.get(indicator, 0.0)
        current_total += current * w
        simulated_total += adjusted * w
        indicator_deltas[indicator] = (adjusted - current) * w

    return {
        "current_total": current_total,
        "simulated_total": simulated_total,
        "delta": simulated_total - current_total,
        "indicator_deltas": indicator_deltas,
    }
