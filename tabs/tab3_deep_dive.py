# tabs/tab3_deep_dive.py
"""Tab 3: Bibliometric Deep Dive (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.constants import UNIVERSITY_SHORT_NAMES, UNIVERSITY_COLORS


# Metric display configs per SciVal export type
CITATIONS_METRICS = [
    ("Scholarly Output (QS)", "Scholarly Output"),
    ("Citations (QS)", "Citations"),
    ("Normalized Total Citation Count (QS)", "Normalized Citations"),
]

IRN_METRICS = [
    ("IRN Scholarly Output (QS)", "IRN Scholarly Output"),
    ("Locations (QS)", "Locations"),
    ("Partners (QS)", "Partners"),
    ("International Research Network (IRN) Index (QS)", "IRN Index"),
]


def render(scival_data, selected_universities, selected_faculty):
    if not scival_data:
        st.warning(
            "No SciVal data loaded. Drop SciVal CSV exports into `data/scival/` "
            "and restart the app."
        )
        return

    st.subheader(f"Bibliometric Deep Dive — {selected_faculty}")

    # Collect data for selected universities and faculty area
    uni_data = {}
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            uni_data[uni_short] = scival_data[uni_full]

    if not uni_data:
        st.warning("No SciVal data available for selected universities.")
        return

    # --- Citations per Faculty section ---
    st.markdown("### Citations per Faculty")
    _render_metric_comparison(
        uni_data, selected_faculty, "citations_per_faculty",
        CITATIONS_METRICS, "citation_per_faculty_score", "Citations per Faculty Score"
    )

    # --- IRN section ---
    st.markdown("### International Research Network")
    _render_metric_comparison(
        uni_data, selected_faculty, "irn",
        IRN_METRICS, "irn_score", "IRN Score"
    )


def _render_metric_comparison(
    uni_data, faculty_area, metric_type, metric_configs, score_key, score_label
):
    """Render a grouped bar chart comparing raw SciVal values across universities."""
    chart_data = []
    overall_scores = {}

    for uni_short, metrics in uni_data.items():
        if metric_type not in metrics:
            continue

        overall_scores[uni_short] = metrics[metric_type].get("overall_score")
        df = metrics[metric_type]["data"]
        area_row = df[df["faculty_area"] == faculty_area]

        if area_row.empty:
            continue

        row = area_row.iloc[0]
        for col_name, display_name in metric_configs:
            if col_name in row.index and pd.notna(row[col_name]):
                chart_data.append({
                    "University": uni_short,
                    "Metric": display_name,
                    "Value": float(row[col_name]),
                })

    if not chart_data:
        st.info(f"No {metric_type} data available for {faculty_area}.")
        return

    chart_df = pd.DataFrame(chart_data)
    metrics_list = [m[1] for m in metric_configs]

    # One chart per metric (different scales)
    cols = st.columns(min(len(metrics_list), 3))
    for i, metric_name in enumerate(metrics_list):
        metric_df = chart_df[chart_df["Metric"] == metric_name]
        if metric_df.empty:
            continue

        col = cols[i % len(cols)]
        with col:
            fig = go.Figure()
            for _, row in metric_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[row["University"]],
                    y=[row["Value"]],
                    name=row["University"],
                    marker_color=UNIVERSITY_COLORS.get(row["University"], "#999"),
                    showlegend=False,
                    hovertemplate=f"<b>{row['University']}</b><br>{metric_name}: %{{y:,.0f}}<extra></extra>",
                ))
            fig.update_layout(
                title=metric_name,
                height=300,
                margin=dict(l=10, r=10, t=40, b=30),
                yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Overall scores
    if any(v is not None for v in overall_scores.values()):
        scores_text = " | ".join(
            f"**{uni}**: {score}" for uni, score in overall_scores.items() if score is not None
        )
        st.caption(f"{score_label}: {scores_text}")
