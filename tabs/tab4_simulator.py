# tabs/tab4_simulator.py
"""Tab 4: Simulator — what-if analysis with ranking position impact."""

import streamlit as st
import pandas as pd
import numpy as np

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES, INDICATOR_COLORS
from src.weights import get_subject_weights
from src.simulator import simulate_score_change


def _format_rank(rank_val):
    """Format rank for display — handles both numeric and band strings."""
    if rank_val is None or (isinstance(rank_val, float) and pd.isna(rank_val)):
        return "—"
    s = str(rank_val).strip()
    if s in ("nan", "None", ""):
        return "—"
    if "-" in s:
        return s
    try:
        return f"#{int(float(s))}"
    except (ValueError, TypeError):
        return s


def _estimate_rank_band(simulated_score, subject_df):
    """Estimate ranking band for a simulated score.

    Returns a display string like '#88' or '251-300'.
    """
    ranked = subject_df[["rank_display", "overall_score"]].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)

    if ranked.empty or pd.isna(simulated_score):
        return "—"

    # Find where the simulated score would slot in
    # Look for the first row where score is <= simulated score
    for idx, row in ranked.iterrows():
        if row["overall_score"] <= simulated_score:
            # This university has a lower or equal score — we'd be at this position or above
            if idx == 0:
                return _format_rank(row["rank_display"])
            # Return the rank of the university just above us in score
            prev_row = ranked.iloc[idx - 1]
            # If we match the prev score, same rank; otherwise use the current position's rank
            if abs(row["overall_score"] - simulated_score) < 0.05:
                return _format_rank(row["rank_display"])
            return _format_rank(prev_row["rank_display"])

    # Score is below everyone — return last rank
    return _format_rank(ranked.iloc[-1]["rank_display"])


def render(qs_data, scival_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    st.subheader(f"Score Simulator — {selected_subject}")

    if selected_subject == "(no subjects available)":
        st.warning("No subjects available for this faculty area.")
        return

    # Filter QS data for this subject/year
    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
    )
    subject_df = qs_data[mask].copy()

    # Get our universities in this subject
    our_df = subject_df[subject_df["institution"].isin(selected_universities)].copy()
    our_df["short_name"] = our_df["institution"].map(UNIVERSITY_SHORT_NAMES)

    available_unis = sorted(our_df["short_name"].dropna().unique().tolist())
    if not available_unis:
        st.warning(f"No target universities found in {selected_subject} ({selected_year}).")
        return

    focus_uni = st.selectbox("Focus university", available_unis, key="sim_focus")
    focus_row = our_df[our_df["short_name"] == focus_uni].iloc[0]

    # Get weights for this subject
    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights defined for {selected_subject}.")
        return

    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    # Current scores and rank
    current_scores = {}
    for ind in indicators_in_use:
        val = focus_row.get(ind)
        current_scores[ind] = float(val) if pd.notna(val) else 0.0

    current_rank_display = focus_row.get("rank_display", focus_row.get("rank"))
    current_rank_numeric = focus_row.get("rank")
    current_overall = focus_row.get("overall_score")

    # Show current position
    rank_str = _format_rank(current_rank_display)
    score_display = f"{current_overall:.1f}" if pd.notna(current_overall) else "—"
    st.markdown(f"**Current position:** {rank_str} (score: {score_display})")

    st.markdown("---")
    st.markdown("**Adjust indicator scores to simulate changes:**")

    # Create sliders for each indicator
    adjusted_scores = {}
    cols = st.columns(len(indicators_in_use))
    for i, ind in enumerate(indicators_in_use):
        with cols[i]:
            weight = subject_weights.get(ind, 0)
            adjusted_scores[ind] = st.slider(
                f"{INDICATOR_NAMES.get(ind, ind)} ({weight}%)",
                min_value=0.0,
                max_value=100.0,
                value=current_scores[ind],
                step=0.5,
                key=f"sim_{ind}",
            )

    # Calculate simulation
    result = simulate_score_change(current_scores, adjusted_scores, subject_weights)

    # Estimate new ranking position from score distribution
    simulated_overall = result["simulated_total"]
    estimated_rank_str = _estimate_rank_band(simulated_overall, subject_df)

    # Display results
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Score", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Simulated Score", f"{result['simulated_total']:.1f}",
                   delta=f"{result['delta']:+.1f}")
    with col3:
        st.metric("Current Rank", rank_str)
    with col4:
        st.metric("Estimated Rank", estimated_rank_str)

    # Per-indicator impact table
    if result["indicator_deltas"]:
        st.markdown("**Per-indicator impact:**")
        delta_data = []
        for ind in indicators_in_use:
            delta = result["indicator_deltas"].get(ind, 0)
            weight = subject_weights.get(ind, 0)
            delta_data.append({
                "Indicator": INDICATOR_NAMES.get(ind, ind),
                "Weight": f"{weight}%",
                "Current": f"{current_scores.get(ind, 0):.1f}",
                "Adjusted": f"{adjusted_scores.get(ind, 0):.1f}",
                "Δ Score": f"{adjusted_scores.get(ind, 0) - current_scores.get(ind, 0):+.1f}",
                "Weighted Impact": f"{delta:+.1f} pts",
            })
        st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)

    # Show context: nearby universities in the ranking
    if not score_rank_df.empty:
        with st.expander("Ranking context — nearby universities"):
            _show_ranking_context(subject_df, focus_row, simulated_overall, selected_subject)

    st.caption(
        "Note: Rank estimation is approximate — it assumes other universities' scores remain constant. "
        "Academic Reputation and Employer Reputation are survey-based and harder to influence directly."
    )


def _show_ranking_context(subject_df, focus_row, simulated_score, subject_name):
    """Show universities near the current and simulated positions."""
    cols_needed = ["institution", "rank_display", "overall_score"]
    available_cols = [c for c in cols_needed if c in subject_df.columns]
    if "rank_display" not in available_cols:
        available_cols.append("rank") if "rank" in subject_df.columns else None
    ranked = subject_df[available_cols].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)

    focus_inst = focus_row["institution"]

    # Find current position
    current_idx = ranked.index[ranked["institution"] == focus_inst]
    if len(current_idx) == 0:
        return
    current_idx = current_idx[0]

    # Show 5 above and 5 below current position
    start = max(0, current_idx - 5)
    end = min(len(ranked), current_idx + 6)
    context = ranked.iloc[start:end].copy()

    # Mark the focus university
    context[""] = context["institution"].apply(
        lambda x: "→" if x == focus_inst else ""
    )
    context["institution"] = context["institution"].apply(
        lambda x: UNIVERSITY_SHORT_NAMES.get(x, x)
    )

    rank_col = "rank_display" if "rank_display" in context.columns else "rank"
    context["QS Rank"] = context[rank_col].apply(_format_rank)
    context["Score"] = context["overall_score"].apply(lambda x: f"{x:.1f}")

    st.dataframe(
        context[["", "institution", "QS Rank", "Score"]].rename(columns={"institution": "University"}),
        use_container_width=True,
        hide_index=True,
    )

    if pd.notna(simulated_score):
        est_rank = _estimate_rank_band(simulated_score, subject_df)
        st.info(f"With a simulated score of **{simulated_score:.1f}**, "
                f"{UNIVERSITY_SHORT_NAMES.get(focus_inst, focus_inst)} would be at approximately "
                f"**{est_rank}** in {subject_name}.")
