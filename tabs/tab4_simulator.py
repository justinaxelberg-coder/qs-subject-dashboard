# tabs/tab4_simulator.py
"""Tab 4: Simulator (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES
from src.weights import get_subject_weights
from src.simulator import simulate_score_change


def render(scival_data, weights, selected_universities, selected_faculty):
    st.subheader(f"Score Simulator — {selected_faculty}")

    if not scival_data:
        st.warning("No SciVal data loaded. Drop SciVal CSV exports into `data/scival/`.")
        return

    # Select focus university
    available = []
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            available.append((uni_short, uni_full))

    if not available:
        st.warning("No SciVal data available for selected universities.")
        return

    focus_short = st.selectbox(
        "Focus university",
        [s for s, _ in available],
        key="sim_focus",
    )
    focus_full = next(f for s, f in available if s == focus_short)

    # Get broad-area weights
    try:
        area_weights = get_subject_weights(weights, selected_faculty, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights for {selected_faculty}.")
        return

    # Extract current QS scores from SciVal data (overall scores per metric type)
    uni_metrics = scival_data[focus_full]
    current_scores = {}
    score_mapping = {
        "citations_per_faculty": "CpP",
        "irn": "IRN",
        "h_index": "HI",
    }

    for metric_type, indicator in score_mapping.items():
        if metric_type in uni_metrics and uni_metrics[metric_type]["overall_score"] is not None:
            current_scores[indicator] = uni_metrics[metric_type]["overall_score"]

    if not current_scores:
        st.warning("No score data available from SciVal exports for simulation.")
        return

    st.markdown("Adjust the sliders to simulate score changes at the faculty area level:")

    # Create sliders for available indicators
    adjusted_scores = {}
    cols = st.columns(len(current_scores))
    for i, (indicator, score) in enumerate(current_scores.items()):
        with cols[i]:
            adjusted_scores[indicator] = st.slider(
                INDICATOR_NAMES.get(indicator, indicator),
                min_value=0.0,
                max_value=100.0,
                value=float(score),
                step=0.5,
                key=f"sim_{indicator}",
            )

    # Add unchanged indicators (AR, ER) — we don't have these from SciVal
    # but they contribute to the total. We note this limitation.
    for indicator in area_weights:
        if indicator not in current_scores and indicator not in adjusted_scores:
            current_scores[indicator] = 0
            adjusted_scores[indicator] = 0

    # Calculate simulation
    result = simulate_score_change(current_scores, adjusted_scores, area_weights)

    # Display results
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Bibliometric Score", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Simulated Score", f"{result['simulated_total']:.1f}")
    with col3:
        st.metric("Delta", f"{result['delta']:+.1f}", delta=f"{result['delta']:+.1f}")

    # Per-indicator breakdown
    if result["indicator_deltas"]:
        st.markdown("**Per-indicator impact:**")
        delta_data = []
        for ind, delta in result["indicator_deltas"].items():
            if ind in current_scores:
                delta_data.append({
                    "Indicator": INDICATOR_NAMES.get(ind, ind),
                    "Weight": f"{area_weights.get(ind, 0)}%",
                    "Current Score": f"{current_scores.get(ind, 0):.1f}",
                    "Adjusted Score": f"{adjusted_scores.get(ind, 0):.1f}",
                    "Weighted Impact": f"{delta:+.1f} pts",
                })
        if delta_data:
            st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)

    st.caption(
        "Note: This simulator operates on QS indicator scores at the faculty area level. "
        "Academic Reputation and Employer Reputation (survey-based) are not included "
        "as they cannot be directly influenced through bibliometric improvements."
    )
