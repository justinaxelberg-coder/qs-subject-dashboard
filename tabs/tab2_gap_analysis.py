# tabs/tab2_gap_analysis.py
"""Tab 2: Gap Analysis (Tier 1 — Subject level)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.constants import (
    UNIVERSITY_SHORT_NAMES,
    INDICATOR_NAMES,
    INDICATOR_COLORS,
)
from src.weights import get_subject_weights
from src.insights import gap_analysis_insight


def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    if selected_subject == "(no subjects available)":
        st.warning("No subjects available for this faculty area.")
        return

    # Filter data
    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
        & (qs_data["institution"].isin(selected_universities))
    )
    df = qs_data[mask].copy()

    if df.empty:
        st.warning(f"No data for {selected_subject} ({selected_year}).")
        return

    # Map to short names
    df["short_name"] = df["institution"].map(UNIVERSITY_SHORT_NAMES)

    # Focus university selector
    available_unis = sorted(df["short_name"].dropna().unique().tolist())
    if not available_unis:
        st.warning("No universities available.")
        return

    focus_uni = st.selectbox("Focus university", available_unis, key="gap_focus")

    # Get weights
    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights defined for {selected_subject}.")
        return

    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    # Get focus university scores
    focus_row = df[df["short_name"] == focus_uni].iloc[0]
    focus_scores = {ind: (focus_row.get(ind, 0) if pd.notna(focus_row.get(ind)) else 0) for ind in indicators_in_use}

    # Calculate peer average (all other selected universities)
    peers_df = df[df["short_name"] != focus_uni]
    if peers_df.empty:
        st.info("Select at least 2 universities to compare.")
        return

    peer_avg = {}
    for ind in indicators_in_use:
        vals = pd.to_numeric(peers_df[ind], errors="coerce").dropna()
        peer_avg[ind] = vals.mean() if len(vals) > 0 else 0

    # Radar chart
    fig = go.Figure()
    labels = [INDICATOR_NAMES.get(ind, ind) for ind in indicators_in_use]
    focus_values = [focus_scores[ind] for ind in indicators_in_use]
    peer_values = [peer_avg[ind] for ind in indicators_in_use]

    # Close the radar polygon
    fig.add_trace(go.Scatterpolar(
        r=focus_values + [focus_values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name=focus_uni,
        fillcolor="rgba(31, 119, 180, 0.2)",
        line_color="rgba(31, 119, 180, 1)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=peer_values + [peer_values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name="SP Peer Average",
        fillcolor="rgba(255, 127, 14, 0.2)",
        line_color="rgba(255, 127, 14, 1)",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=f"Gap Analysis — {focus_uni} vs. São Paulo Peers in {selected_subject}",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Opportunity table
    opportunities = []
    for ind in indicators_in_use:
        gap = peer_avg[ind] - focus_scores[ind]
        weight = subject_weights.get(ind, 0)
        if gap > 0:
            opportunities.append({
                "indicator": ind,
                "Indicator": INDICATOR_NAMES.get(ind, ind),
                "Your Score": f"{focus_scores[ind]:.1f}",
                "Peer Avg": f"{peer_avg[ind]:.1f}",
                "Gap": f"{gap:.1f}",
                "Weight": f"{weight}%",
                "gap_points": gap * weight / 100,
                "Weighted Impact": f"{gap * weight / 100:.1f} pts",
            })

    opportunities.sort(key=lambda x: x["gap_points"], reverse=True)

    # Headline
    st.markdown(f"**{gap_analysis_insight(focus_uni, selected_subject, opportunities)}**")

    if opportunities:
        opp_df = pd.DataFrame(opportunities)[
            ["Indicator", "Your Score", "Peer Avg", "Gap", "Weight", "Weighted Impact"]
        ]
        st.dataframe(opp_df, use_container_width=True, hide_index=True)
    else:
        st.success(f"{focus_uni} leads or matches peers across all indicators!")
