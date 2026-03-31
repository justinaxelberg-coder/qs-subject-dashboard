# tabs/tab4_simulator.py
"""Tab 4: Simulator — what-if analysis with ranking position impact."""

import streamlit as st
import pandas as pd
import numpy as np

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES, INDICATOR_COLORS
from src.weights import get_subject_weights
from src.simulator import simulate_score_change


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

    current_rank = focus_row.get("rank")
    current_overall = focus_row.get("overall_score")

    # Show current position
    rank_display = f"#{int(current_rank)}" if pd.notna(current_rank) else "Unranked"
    score_display = f"{current_overall:.1f}" if pd.notna(current_overall) else "—"
    st.markdown(f"**Current position:** {rank_display} (score: {score_display})")

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
    # Build score-to-rank mapping from all universities in this subject
    score_rank_df = subject_df[["overall_score", "rank"]].dropna().sort_values("overall_score", ascending=False)

    simulated_overall = result["simulated_total"]
    estimated_rank = _estimate_rank(simulated_overall, score_rank_df)
    rank_delta = None
    if pd.notna(current_rank) and estimated_rank is not None:
        rank_delta = int(current_rank) - estimated_rank  # positive = improvement (lower rank number)

    # Display results
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Score", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Simulated Score", f"{result['simulated_total']:.1f}",
                   delta=f"{result['delta']:+.1f}")
    with col3:
        st.metric("Current Rank", rank_display)
    with col4:
        if estimated_rank is not None:
            new_rank_display = f"#{estimated_rank}"
            if rank_delta is not None and rank_delta != 0:
                # Positive rank_delta means improvement (moved up)
                delta_str = f"{'↑' if rank_delta > 0 else '↓'} {abs(rank_delta)} places"
                st.metric("Estimated Rank", new_rank_display, delta=delta_str,
                          delta_color="normal" if rank_delta > 0 else "inverse")
            else:
                st.metric("Estimated Rank", new_rank_display)
        else:
            st.metric("Estimated Rank", "—")

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


def _estimate_rank(simulated_score, score_rank_df):
    """Estimate ranking position for a given score based on the score distribution."""
    if score_rank_df.empty or pd.isna(simulated_score):
        return None

    # Count how many universities have a higher score
    higher = score_rank_df[score_rank_df["overall_score"] > simulated_score]
    if higher.empty:
        return 1
    # Rank = number of universities with higher score + 1
    return len(higher) + 1


def _show_ranking_context(subject_df, focus_row, simulated_score, subject_name):
    """Show universities near the current and simulated positions."""
    ranked = subject_df[["institution", "rank", "overall_score"]].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)
    ranked["position"] = range(1, len(ranked) + 1)

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
    short_names = {v: k for k, v in UNIVERSITY_SHORT_NAMES.items()}
    context["institution"] = context["institution"].apply(
        lambda x: UNIVERSITY_SHORT_NAMES.get(x, x)
    )
    context = context.rename(columns={
        "position": "Pos",
        "institution": "University",
        "overall_score": "Score",
        "rank": "QS Rank",
    })
    context["QS Rank"] = context["QS Rank"].apply(lambda x: f"#{int(x)}" if pd.notna(x) else "—")
    context["Score"] = context["Score"].apply(lambda x: f"{x:.1f}")

    st.dataframe(
        context[["", "Pos", "University", "QS Rank", "Score"]],
        use_container_width=True,
        hide_index=True,
    )

    if pd.notna(simulated_score):
        # Show where simulated score would land
        higher_count = len(ranked[ranked["overall_score"] > simulated_score])
        st.info(f"With a simulated score of **{simulated_score:.1f}**, "
                f"{UNIVERSITY_SHORT_NAMES.get(focus_inst, focus_inst)} would be at approximately "
                f"**position #{higher_count + 1}** out of {len(ranked)} universities in {subject_name}.")
