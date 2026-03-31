# tabs/tab5_benchmarking.py
"""Tab 5: Peer Benchmarking (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES
from src.peers import load_manual_peers, find_structural_peers
from src.insights import benchmarking_insight


def render(qs_data, scival_data, selected_universities, selected_faculty):
    st.subheader(f"Peer Benchmarking — {selected_faculty}")

    if not scival_data:
        st.warning("No SciVal data loaded.")
        return

    # Focus university selector
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
        key="bench_focus",
    )
    focus_full = next(f for s, f in available if s == focus_short)

    # Load manual peers
    manual_peers = load_manual_peers()
    manual_peer_names = manual_peers.get(focus_full, [])

    # Build comparison table
    # Focus university row
    focus_metrics = _extract_faculty_metrics(scival_data.get(focus_full, {}), selected_faculty)
    if not focus_metrics:
        st.warning(f"No SciVal data for {focus_short} in {selected_faculty}.")
        return

    comparison_rows = [{"University": f"**{focus_short}** (focus)", **focus_metrics}]

    # --- Structural peers (auto-matched by scholarly output) ---
    structural_peer_df = _build_structural_peer_pool(scival_data, selected_faculty)
    if not structural_peer_df.empty:
        matched = find_structural_peers(
            focus_university=focus_full,
            faculty_area=selected_faculty,
            all_data=structural_peer_df,
            output_band=0.3,
            max_rank_improvement=20,
            top_n=5,
        )
        for _, peer_row in matched.iterrows():
            peer_name = peer_row["institution"]
            peer_metrics = _extract_faculty_metrics(scival_data.get(peer_name, {}), selected_faculty)
            if peer_metrics:
                display_name = UNIVERSITY_SHORT_NAMES.get(peer_name, peer_name)
                comparison_rows.append({"University": f"{display_name} (structural peer)", **peer_metrics})

    # --- SP peer rows ---
    peer_deltas = {}
    for uni_full_peer in selected_universities:
        if uni_full_peer == focus_full:
            continue
        uni_short_peer = UNIVERSITY_SHORT_NAMES.get(uni_full_peer, uni_full_peer)
        peer_metrics = _extract_faculty_metrics(scival_data.get(uni_full_peer, {}), selected_faculty)
        if peer_metrics:
            comparison_rows.append({"University": uni_short_peer, **peer_metrics})
            # Calculate deltas for insight
            deltas = {}
            for key in peer_metrics:
                if key in focus_metrics and isinstance(peer_metrics[key], (int, float)) and isinstance(focus_metrics[key], (int, float)):
                    deltas[key] = peer_metrics[key] - focus_metrics[key]
            peer_deltas[uni_short_peer] = deltas

    # --- Manual peer rows ---
    for peer_name in manual_peer_names:
        peer_metrics = _extract_faculty_metrics(scival_data.get(peer_name, {}), selected_faculty)
        if peer_metrics:
            comparison_rows.append({"University": f"{peer_name} (manual peer)", **peer_metrics})
            deltas = {}
            for key in peer_metrics:
                if key in focus_metrics and isinstance(peer_metrics[key], (int, float)) and isinstance(focus_metrics[key], (int, float)):
                    deltas[key] = peer_metrics[key] - focus_metrics[key]
            peer_deltas[peer_name] = deltas

    # Insight
    if peer_deltas:
        st.markdown(f"**{benchmarking_insight(focus_short, selected_faculty, peer_deltas)}**")

    # Comparison table
    comp_df = pd.DataFrame(comparison_rows)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Delta table
    if peer_deltas:
        st.markdown("### Gaps vs. Focus University")
        delta_rows = []
        for peer, deltas in peer_deltas.items():
            row = {"Peer": peer}
            for key, val in deltas.items():
                if isinstance(val, (int, float)):
                    row[key] = f"{val:+,.0f}" if abs(val) >= 10 else f"{val:+.1f}"
            delta_rows.append(row)
        if delta_rows:
            delta_df = pd.DataFrame(delta_rows)
            st.dataframe(delta_df, use_container_width=True, hide_index=True)

    st.caption(
        "To add more institutions to the benchmarking pool, "
        "export their SciVal data and drop into `data/scival/`. "
        "To add manual peers, edit `data/peers.csv`."
    )


def _build_structural_peer_pool(scival_data: dict, faculty_area: str) -> pd.DataFrame:
    """Build a DataFrame of all universities with scholarly output for structural peer matching."""
    rows = []
    for uni_name, metrics in scival_data.items():
        if "citations_per_faculty" not in metrics:
            continue
        df = metrics["citations_per_faculty"]["data"]
        area_row = df[df["faculty_area"] == faculty_area]
        if area_row.empty:
            continue
        output_col = "Scholarly Output (QS)"
        if output_col not in area_row.columns:
            continue
        rows.append({
            "institution": uni_name,
            "faculty_area": faculty_area,
            "scholarly_output": float(area_row[output_col].iloc[0]),
            "overall_rank": 0,  # Placeholder — requires QS rank data
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def _extract_faculty_metrics(uni_scival: dict, faculty_area: str) -> dict:
    """Extract key metrics for a given faculty area from a university's SciVal data."""
    if not uni_scival:
        return {}

    result = {}

    # Citations data
    if "citations_per_faculty" in uni_scival:
        df = uni_scival["citations_per_faculty"]["data"]
        row = df[df["faculty_area"] == faculty_area]
        if not row.empty:
            r = row.iloc[0]
            for col in ["Scholarly Output (QS)", "Citations (QS)", "Normalized Total Citation Count (QS)"]:
                if col in r.index and pd.notna(r[col]):
                    result[col] = r[col]

    # IRN data
    if "irn" in uni_scival:
        df = uni_scival["irn"]["data"]
        row = df[df["faculty_area"] == faculty_area]
        if not row.empty:
            r = row.iloc[0]
            for col in ["Locations (QS)", "Partners (QS)", "International Research Network (IRN) Index (QS)"]:
                if col in r.index and pd.notna(r[col]):
                    result[col] = r[col]

    return result
