# tabs/tab1_decomposition.py
"""Tab 1: Score Decomposition (Tier 1 — Subject level)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.constants import (
    UNIVERSITY_SHORT_NAMES,
    UNIVERSITY_COLORS,
    INDICATOR_NAMES,
    INDICATOR_COLORS,
)
from src.weights import get_subject_weights, calculate_weighted_contributions
from src.insights import decomposition_insight
from src.data_loader import filter_target_universities


def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    if selected_subject == "(no subjects available)":
        st.warning("No subjects available for this faculty area.")
        return

    # Filter data for selected subject, year, and universities
    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
        & (qs_data["institution"].isin(selected_universities))
    )
    df = qs_data[mask].copy()

    if df.empty:
        st.warning(f"No data for {selected_subject} ({selected_year}) for selected universities.")
        return

    # Get weights for this subject
    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights defined for {selected_subject}. Check weights.json.")
        return

    # Calculate weighted contributions per university and collect ranks
    contributions = {}
    uni_ranks = {}
    uni_scores = {}
    for _, row in df.iterrows():
        uni_full = row["institution"]
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        scores = {ind: row.get(ind, 0) for ind in ["AR", "ER", "CpP", "HI", "IRN"]}
        # Replace NaN with 0
        scores = {k: (v if pd.notna(v) else 0) for k, v in scores.items()}
        contributions[uni_short] = calculate_weighted_contributions(scores, subject_weights)
        uni_ranks[uni_short] = row.get("rank")
        uni_scores[uni_short] = row.get("overall_score")

    # Ranking position summary
    rank_cols = st.columns(len(contributions))
    for i, uni in enumerate(sorted(contributions.keys())):
        with rank_cols[i]:
            rank_val = uni_ranks.get(uni)
            score_val = uni_scores.get(uni)
            rank_display = f"#{int(rank_val)}" if pd.notna(rank_val) else "Unranked"
            score_display = f"{score_val:.1f}" if pd.notna(score_val) else "—"
            st.metric(uni, rank_display, help=f"Overall score: {score_display}")

    # Headline insight
    st.markdown(f"**{decomposition_insight(contributions, selected_subject)}**")

    # Stacked horizontal bar chart
    fig = go.Figure()
    universities = sorted(contributions.keys())
    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    for indicator in indicators_in_use:
        values = [contributions[uni].get(indicator, 0) for uni in universities]
        fig.add_trace(go.Bar(
            y=universities,
            x=values,
            name=INDICATOR_NAMES.get(indicator, indicator),
            orientation="h",
            marker_color=INDICATOR_COLORS.get(indicator, "#999"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{INDICATOR_NAMES.get(indicator, indicator)}: "
                "%{x:.1f} weighted pts<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        title=f"Score Decomposition — {selected_subject} ({selected_year})",
        xaxis_title="Weighted Score Contribution",
        yaxis_title="",
        legend_title="Indicator",
        height=max(300, len(universities) * 60 + 100),
        margin=dict(l=10, r=10, t=50, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Weight formula display
    weight_parts = [
        f"{INDICATOR_NAMES.get(k, k)} {v}%"
        for k, v in subject_weights.items()
    ]
    st.caption(f"**{selected_subject} weights:** {' | '.join(weight_parts)}")

    # Collapsible data table
    with st.expander("View raw data"):
        table_data = []
        for uni in universities:
            rank_val = uni_ranks.get(uni)
            row = {
                "University": uni,
                "Rank": f"#{int(rank_val)}" if pd.notna(rank_val) else "—",
                "Score": f"{uni_scores.get(uni, 0):.1f}" if pd.notna(uni_scores.get(uni)) else "—",
            }
            for ind in indicators_in_use:
                row[INDICATOR_NAMES.get(ind, ind)] = f"{contributions[uni].get(ind, 0):.1f}"
            row["Total (weighted)"] = f"{sum(contributions[uni].values()):.1f}"
            table_data.append(row)
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
