"""Auto-generate plain-language headline insights from data."""

from src.constants import INDICATOR_NAMES


def decomposition_insight(contributions: dict, subject: str) -> str:
    """Generate a headline insight for the Score Decomposition tab.

    Args:
        contributions: dict mapping university short name to
            dict of indicator -> weighted points.
        subject: the subject name.

    Returns plain-language string.
    """
    if not contributions:
        return f"No data available for {subject}."

    # Find the top-scoring university
    totals = {uni: sum(c.values()) for uni, c in contributions.items()}
    top_uni = max(totals, key=totals.get)
    top_total = totals[top_uni]
    top_contribs = contributions[top_uni]

    # Find the strongest and weakest indicators
    strongest = max(top_contribs, key=top_contribs.get)
    weakest = min(top_contribs, key=top_contribs.get) if len(top_contribs) > 1 else strongest

    strongest_name = INDICATOR_NAMES.get(strongest, strongest)
    weakest_name = INDICATOR_NAMES.get(weakest, weakest)

    return (
        f"In {subject}, {top_uni}'s overall weighted score of {top_total:.1f} "
        f"is driven primarily by {strongest_name} ({top_contribs[strongest]:.1f} pts). "
        f"Its weakest weighted contributor is {weakest_name} "
        f"({top_contribs[weakest]:.1f} pts)."
    )


def gap_analysis_insight(
    focus_uni: str, subject: str, opportunities: list[dict]
) -> str:
    """Generate a headline insight for the Gap Analysis tab.

    Args:
        focus_uni: short name of focus university.
        subject: the subject name.
        opportunities: list of dicts with 'indicator' and 'gap_points',
            sorted descending by gap_points.

    Returns plain-language string.
    """
    if not opportunities:
        return (
            f"{focus_uni} leads or matches peers across all indicators "
            f"in {subject}. No improvement opportunities identified."
        )

    top = opportunities[0]
    indicator_name = INDICATOR_NAMES.get(top["indicator"], top["indicator"])
    return (
        f"{focus_uni}'s biggest opportunity in {subject} is "
        f"{indicator_name}, worth up to {top['gap_points']:.1f} "
        f"weighted points vs. Sao Paulo peers."
    )


def benchmarking_insight(
    focus_uni: str, faculty_area: str, peer_deltas: dict
) -> str:
    """Generate a headline insight for the Peer Benchmarking tab.

    Args:
        focus_uni: short name of focus university.
        faculty_area: the faculty area name.
        peer_deltas: dict mapping peer name to dict of indicator -> delta
            (positive = peer outperforms focus).

    Returns plain-language string.
    """
    if not peer_deltas:
        return f"No peer data available for {focus_uni} in {faculty_area}."

    # Count how many peers outperform on each indicator
    indicator_counts = {}
    for peer, deltas in peer_deltas.items():
        for indicator, delta in deltas.items():
            if delta > 0:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1

    if not indicator_counts:
        return (
            f"{focus_uni} leads all peers across every indicator "
            f"in {faculty_area}."
        )

    # Find most common outperformance area
    most_common = max(indicator_counts, key=indicator_counts.get)
    count = indicator_counts[most_common]
    total_peers = len(peer_deltas)
    indicator_name = INDICATOR_NAMES.get(most_common, most_common)

    return (
        f"{count} of {total_peers} peers outperform {focus_uni} on "
        f"{indicator_name} in {faculty_area}, suggesting this as a "
        f"key area for improvement."
    )
