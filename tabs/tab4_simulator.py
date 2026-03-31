# tabs/tab4_simulator.py
"""Tab 4: Simulator — what-if analysis with ranking position and bibliometric impact."""

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
    """Estimate ranking band for a simulated score."""
    if "rank_display" not in subject_df.columns:
        return "—"
    ranked = subject_df[["rank_display", "overall_score"]].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)

    if ranked.empty or pd.isna(simulated_score):
        return "—"

    for idx, row in ranked.iterrows():
        if row["overall_score"] <= simulated_score:
            if idx == 0:
                return _format_rank(row["rank_display"])
            prev_row = ranked.iloc[idx - 1]
            if abs(row["overall_score"] - simulated_score) < 0.05:
                return _format_rank(row["rank_display"])
            return _format_rank(prev_row["rank_display"])

    return _format_rank(ranked.iloc[-1]["rank_display"])


def _get_scival_context(scival_data, focus_full, selected_faculty):
    """Extract current raw bibliometric values for the focus university."""
    if not scival_data or focus_full not in scival_data:
        return {}

    uni_metrics = scival_data[focus_full]
    result = {}

    # Citations per Faculty raw values
    if "citations_per_faculty" in uni_metrics:
        df = uni_metrics["citations_per_faculty"]["data"]
        area_row = df[df["faculty_area"] == selected_faculty]
        if not area_row.empty:
            r = area_row.iloc[0]
            result["CpP"] = {
                "Scholarly Output": r.get("Scholarly Output (QS)"),
                "Citations": r.get("Citations (QS)"),
                "Normalized Citations": r.get("Normalized Total Citation Count (QS)"),
                "Weighting Factor": r.get("Weighting Factor (QS)"),
            }

    # IRN raw values
    if "irn" in uni_metrics:
        df = uni_metrics["irn"]["data"]
        area_row = df[df["faculty_area"] == selected_faculty]
        if not area_row.empty:
            r = area_row.iloc[0]
            result["IRN"] = {
                "IRN Scholarly Output": r.get("IRN Scholarly Output (QS)"),
                "Locations": r.get("Locations (QS)"),
                "Partners": r.get("Partners (QS)"),
                "IRN Index": r.get("International Research Network (IRN) Index (QS)"),
            }

    return result


def _estimate_bibliometric_changes(indicator, score_change, raw_context):
    """Estimate what real bibliometric changes a score change implies."""
    if not raw_context or indicator not in raw_context:
        return None

    metrics = raw_context[indicator]
    changes = []

    if indicator == "CpP":
        # CpP score is driven by normalized citations relative to scholarly output
        norm_cit = metrics.get("Normalized Citations")
        scholarly_out = metrics.get("Scholarly Output")
        citations = metrics.get("Citations")

        if norm_cit and pd.notna(norm_cit) and scholarly_out and pd.notna(scholarly_out):
            # Rough linear estimate: score change of X points ≈ X% change in normalized citations
            # (QS normalises to 0-100 scale)
            pct_change = score_change / 100.0
            cit_change = norm_cit * pct_change
            changes.append(f"~{abs(cit_change):,.0f} {'more' if cit_change > 0 else 'fewer'} normalized citations")

        if citations and pd.notna(citations):
            pct_change = score_change / 100.0
            raw_cit_change = citations * pct_change
            changes.append(f"~{abs(raw_cit_change):,.0f} {'more' if raw_cit_change > 0 else 'fewer'} raw citations")

    elif indicator == "IRN":
        irn_index = metrics.get("IRN Index")
        partners = metrics.get("Partners")
        locations = metrics.get("Locations")

        if partners and pd.notna(partners):
            pct_change = score_change / 100.0
            partner_change = partners * pct_change
            changes.append(f"~{abs(partner_change):,.0f} {'more' if partner_change > 0 else 'fewer'} international partners")

        if locations and pd.notna(locations):
            pct_change = score_change / 100.0
            loc_change = locations * pct_change
            changes.append(f"~{abs(loc_change):,.0f} {'more' if loc_change > 0 else 'fewer'} partner locations")

    return changes if changes else None


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
    focus_full = focus_row["institution"]

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
    current_overall = focus_row.get("overall_score")

    # Show current position
    rank_str = _format_rank(current_rank_display)
    score_display = f"{current_overall:.1f}" if pd.notna(current_overall) else "—"
    st.markdown(f"**Current position:** {rank_str} (score: {score_display})")

    # Get SciVal raw context for this university + faculty area
    raw_context = _get_scival_context(scival_data, focus_full, selected_faculty)

    st.markdown("---")
    st.markdown("**Adjust indicator scores to simulate changes:**")

    # Create sliders — key includes university name so they reset on switch
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
                key=f"sim_{focus_uni}_{selected_subject}_{ind}",
            )

    # Calculate simulation
    result = simulate_score_change(current_scores, adjusted_scores, subject_weights)

    # Estimate new ranking position
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

    # Per-indicator impact table with bibliometric translation
    st.markdown("**Per-indicator impact:**")
    delta_data = []
    bibliometric_notes = []
    for ind in indicators_in_use:
        delta = result["indicator_deltas"].get(ind, 0)
        weight = subject_weights.get(ind, 0)
        score_change = adjusted_scores.get(ind, 0) - current_scores.get(ind, 0)
        row_data = {
            "Indicator": INDICATOR_NAMES.get(ind, ind),
            "Weight": f"{weight}%",
            "Current": f"{current_scores.get(ind, 0):.1f}",
            "Adjusted": f"{adjusted_scores.get(ind, 0):.1f}",
            "Δ Score": f"{score_change:+.1f}",
            "Weighted Impact": f"{delta:+.1f} pts",
        }
        delta_data.append(row_data)

        # Translate to bibliometric changes
        if abs(score_change) > 0.1:
            bib_changes = _estimate_bibliometric_changes(ind, score_change, raw_context)
            if bib_changes:
                for change in bib_changes:
                    bibliometric_notes.append(f"**{INDICATOR_NAMES.get(ind, ind)}** ({score_change:+.1f} pts): {change}")

    st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)

    # Bibliometric translation section
    if bibliometric_notes:
        st.markdown("---")
        st.markdown("#### 📐 What this means in real terms")
        st.caption(f"Based on {focus_uni}'s current SciVal data for {selected_faculty}:")
        for note in bibliometric_notes:
            st.markdown(f"- {note}")
    elif any(abs(adjusted_scores[ind] - current_scores[ind]) > 0.1 for ind in indicators_in_use):
        if not raw_context:
            st.info(
                f"💡 Add SciVal CSV exports for {focus_uni} to `data/scival/` to see "
                f"what real bibliometric changes these score adjustments would require."
            )

    # Show current raw bibliometric values
    if raw_context:
        with st.expander(f"📊 Current SciVal values — {focus_uni} in {selected_faculty}"):
            for ind, metrics in raw_context.items():
                st.markdown(f"**{INDICATOR_NAMES.get(ind, ind)}:**")
                metric_items = []
                for label, val in metrics.items():
                    if val is not None and pd.notna(val):
                        if isinstance(val, float) and val == int(val):
                            metric_items.append(f"{label}: **{int(val):,}**")
                        elif isinstance(val, float):
                            metric_items.append(f"{label}: **{val:,.2f}**")
                        else:
                            metric_items.append(f"{label}: **{val}**")
                st.markdown(" · ".join(metric_items))

    # Ranking context
    with st.expander("Ranking context — nearby universities"):
        _show_ranking_context(subject_df, focus_row, simulated_overall, selected_subject)

    st.caption(
        "Note: Rank estimation is approximate — it assumes other universities' scores remain constant. "
        "Bibliometric estimates are linear approximations based on current SciVal data. "
        "Academic Reputation and Employer Reputation are survey-based and harder to influence directly."
    )


def _show_ranking_context(subject_df, focus_row, simulated_score, subject_name):
    """Show universities near the current and simulated positions."""
    cols_needed = ["institution", "rank_display", "overall_score"]
    available_cols = [c for c in cols_needed if c in subject_df.columns]
    ranked = subject_df[available_cols].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)

    focus_inst = focus_row["institution"]

    current_idx = ranked.index[ranked["institution"] == focus_inst]
    if len(current_idx) == 0:
        st.info("This university does not have a ranked score in this subject.")
        return
    current_idx = current_idx[0]

    start = max(0, current_idx - 5)
    end = min(len(ranked), current_idx + 6)
    context = ranked.iloc[start:end].copy()

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
        focus_short = UNIVERSITY_SHORT_NAMES.get(focus_inst, focus_inst)
        st.info(f"With a simulated score of **{simulated_score:.1f}**, "
                f"{focus_short} would be at approximately "
                f"**{est_rank}** in {subject_name}.")
