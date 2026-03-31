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


def render(scival_data, selected_universities, selected_faculty, is_broad_field=False):
    if not scival_data:
        st.warning(
            "No SciVal data loaded. Drop SciVal CSV exports into `data/scival/` "
            "and restart the app."
        )
        return

    st.subheader(f"Bibliometric Deep Dive — {selected_faculty}")

    # Collect data for selected universities
    uni_data = {}
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            uni_data[uni_short] = scival_data[uni_full]

    if not uni_data:
        st.warning("No SciVal data available for selected universities.")
        return

    if is_broad_field:
        # Show all faculty areas side by side for cross-area comparison
        _render_broad_field_overview(uni_data)
    else:
        # Show specific faculty area detail
        st.markdown("### Citations per Faculty")
        _render_metric_comparison(
            uni_data, selected_faculty, "citations_per_faculty",
            CITATIONS_METRICS, "citation_per_faculty_score", "Citations per Faculty Score"
        )

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


def _render_broad_field_overview(uni_data):
    """Render cross-area comparison showing all faculty areas for each university."""
    from src.constants import FACULTY_AREAS

    # --- Citations per Faculty across all areas ---
    st.markdown("### Citations per Faculty — All Areas")
    _render_cross_area_chart(uni_data, "citations_per_faculty", CITATIONS_METRICS, FACULTY_AREAS)

    # --- IRN across all areas ---
    st.markdown("### International Research Network — All Areas")
    _render_cross_area_chart(uni_data, "irn", IRN_METRICS, FACULTY_AREAS)

    # --- Summary table with all raw values ---
    st.markdown("### Raw Values by Faculty Area")
    for metric_type, label, metric_configs in [
        ("citations_per_faculty", "Citations per Faculty", CITATIONS_METRICS),
        ("irn", "International Research Network", IRN_METRICS),
    ]:
        rows = []
        for uni_short, metrics in uni_data.items():
            if metric_type not in metrics:
                continue
            df = metrics[metric_type]["data"]
            for _, area_row in df.iterrows():
                row_data = {"University": uni_short, "Faculty Area": area_row.get("faculty_area", "")}
                for col_name, display_name in metric_configs:
                    if col_name in area_row.index and pd.notna(area_row[col_name]):
                        row_data[display_name] = area_row[col_name]
                rows.append(row_data)
        if rows:
            st.markdown(f"**{label}**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_cross_area_chart(uni_data, metric_type, metric_configs, faculty_areas):
    """Render grouped bar charts comparing universities across all faculty areas for a key metric."""
    # Use the most important metric (last one = index/normalized) for the cross-area view
    key_col, key_label = metric_configs[-1]

    chart_data = []
    for uni_short, metrics in uni_data.items():
        if metric_type not in metrics:
            continue
        df = metrics[metric_type]["data"]
        for area in faculty_areas:
            area_row = df[df["faculty_area"] == area]
            if area_row.empty:
                continue
            val = area_row.iloc[0].get(key_col)
            if pd.notna(val):
                chart_data.append({
                    "University": uni_short,
                    "Faculty Area": area,
                    "Value": float(val),
                })

    if not chart_data:
        st.info(f"No {metric_type} data available.")
        return

    chart_df = pd.DataFrame(chart_data)
    fig = go.Figure()
    for uni in sorted(chart_df["University"].unique()):
        uni_df = chart_df[chart_df["University"] == uni]
        fig.add_trace(go.Bar(
            x=uni_df["Faculty Area"],
            y=uni_df["Value"],
            name=uni,
            marker_color=UNIVERSITY_COLORS.get(uni, "#999"),
            hovertemplate=f"<b>{uni}</b><br>%{{x}}<br>{key_label}: %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        title=f"{key_label} by Faculty Area",
        height=400,
        margin=dict(l=10, r=10, t=50, b=80),
        xaxis_tickangle=-25,
        legend_title="University",
    )
    st.plotly_chart(fig, use_container_width=True)
