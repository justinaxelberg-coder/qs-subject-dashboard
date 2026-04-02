# tabs/tab5_benchmarking.py
"""Tab 5: Peer Benchmarking — QS indicator scores + SciVal bibliometrics."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.constants import (
    INDICATOR_NAMES,
    PEER_GROUPS,
    TARGET_UNIVERSITIES,
    UNIVERSITY_SHORT_NAMES,
)

# Short labels for peer institutions (display only)
_PEER_SHORT = {
    "Tsinghua University": "Tsinghua",
    "Peking University": "Peking",
    "Fudan University": "Fudan",
    "Shanghai Jiao Tong University": "SJTU",
    "Zhejiang University": "Zhejiang",
    "Nanjing University": "Nanjing",
    "University of Science and Technology of China": "USTC",
    "Xi\u2019an Jiaotong University": "XJTU",
    "Harbin Institute of Technology": "HIT",
    "Universidad de Buenos Aires (UBA)": "UBA",
    "Universidad Nacional Aut\u00f3noma de M\u00e9xico  (UNAM)": "UNAM",
    "Pontificia Universidad Cat\u00f3lica de Chile (UC)": "PUC Chile",
    "Universidad de Chile": "U Chile",
    "Universidad de los Andes": "Uniandes",
    "Universidad Nacional de Colombia": "UNAL",
    "Tecnol\u00f3gico de Monterrey": "Tec Monterrey",
    "Universidade Federal do Rio de Janeiro": "UFRJ",
    "Federal University of Minas Gerais (UFMG)": "UFMG",
    "Universidade Federal do Rio Grande Do Sul": "UFRGS",
    "Pontif\u00edcia Universidade Cat\u00f3lica do Rio de Janeiro": "PUC-Rio",
    "Universidade Federal de Santa Catarina": "UFSC",
    "Universidade Federal da Bahia": "UFBA",
    "Universidade de Bras\u00edlia": "UnB",
    "Universidade Federal Fluminense": "UFF",
    # Russell Group
    "University of Oxford": "Oxford",
    "University of Cambridge": "Cambridge",
    "Imperial College London": "Imperial",
    "UCL": "UCL",
    "The University of Edinburgh": "Edinburgh",
    "The University of Manchester": "Manchester",
    "King's College London": "KCL",
    "The University of Warwick": "Warwick",
    "University of Bristol": "Bristol",
    "University of Leeds": "Leeds",
    "The University of Sheffield": "Sheffield",
    "University of Nottingham": "Nottingham",
    "University of Birmingham": "Birmingham",
    "Durham University": "Durham",
    "University of Southampton": "Southampton",
    "University of Glasgow": "Glasgow",
    "Queen Mary University of London": "QMUL",
    "University of Liverpool": "Liverpool",
    "Newcastle University": "Newcastle",
    "Cardiff University": "Cardiff",
    "Queen's University Belfast": "QUB",
    "University of Exeter": "Exeter",
    # Ibero-American
    "Complutense University of Madrid": "UCM",
    "Universidad Aut\u00f3noma de Madrid": "UAM",
    "Universitat de Barcelona": "UB",
    "Universitat Pompeu Fabra (Barcelona)": "UPF",
    "Universidad Polit\u00e9cnica de Madrid (UPM)": "UPM",
    "Universitat de Valencia": "UV",
    "Universidad de Sevilla": "US",
    "University of Porto": "UPorto",
    "Universidade Nova de Lisboa": "UNL",
    # BRICS
    "Indian Institute of Science (IISc) Bangalore": "IISc",
    "Lomonosov Moscow State University": "MSU",
    "HSE University": "HSE",
    "University of Cape Town": "UCT",
    "Stellenbosch University": "SU",
    "University of Witwatersrand": "Wits",
    "University of Pretoria": "UP",
    # Rising East Asian
    "National University of Singapore (NUS)": "NUS",
    "Nanyang Technological University, Singapore (NTU Singapore)": "NTU",
    "Seoul National University": "SNU",
    "Sungkyunkwan University (SKKU)": "SKKU",
    "Pohang University of Science And Technology (POSTECH)": "POSTECH",
    "Korea University": "KU",
    "Yonsei University": "Yonsei",
    "The Hong Kong University of Science and Technology": "HKUST",
    "The Chinese University of Hong Kong (CUHK)": "CUHK",
    "City University of Hong Kong (CityUHK)": "CityU HK",
}


def _short(name: str) -> str:
    if name in UNIVERSITY_SHORT_NAMES:
        return UNIVERSITY_SHORT_NAMES[name]
    return _PEER_SHORT.get(name, name)


def _fmt_score(val) -> str:
    if pd.isna(val):
        return "—"
    return f"{float(val):.1f}"


def _fmt_rank(val) -> str:
    if pd.isna(val):
        return "—"
    s = str(val).strip()
    if s in ("nan", "None", ""):
        return "—"
    return s


def _build_group_table(
    qs_data: pd.DataFrame,
    subject: str,
    group_institutions: list[str],
    sp_universities: list[str],
    year: int,
) -> pd.DataFrame:
    """Return a table of indicator scores for the peer group + SP universities."""
    subject_df = qs_data[
        (qs_data["subject"] == subject) & (qs_data["year"] == year)
    ].copy()

    all_institutions = list(dict.fromkeys(group_institutions + sp_universities))
    rows = []
    for inst in all_institutions:
        row_df = subject_df[subject_df["institution"] == inst]
        is_sp = inst in sp_universities
        is_target = inst in TARGET_UNIVERSITIES
        if row_df.empty:
            rows.append(
                {
                    "Institution": _short(inst),
                    "Full Name": inst,
                    "Rank": "—",
                    "Score": "—",
                    "AR": "—",
                    "ER": "—",
                    "CpP": "—",
                    "HI": "—",
                    "IRN": "—",
                    "_is_sp": is_sp,
                    "_in_ranking": False,
                }
            )
        else:
            r = row_df.iloc[0]
            rows.append(
                {
                    "Institution": _short(inst),
                    "Full Name": inst,
                    "Rank": _fmt_rank(r.get("rank_display", "—")),
                    "Score": _fmt_score(r.get("overall_score")),
                    "AR": _fmt_score(r.get("AR")),
                    "ER": _fmt_score(r.get("ER")),
                    "CpP": _fmt_score(r.get("CpP")),
                    "HI": _fmt_score(r.get("HI")),
                    "IRN": _fmt_score(r.get("IRN")),
                    "_is_sp": is_sp,
                    "_in_ranking": True,
                }
            )

    df = pd.DataFrame(rows)
    # Sort: ranked first (by numeric rank asc), then unranked; use rank midpoint so bands sort correctly
    from src.data_loader import _parse_rank_numeric
    def _rank_sort_key(rank_str):
        if rank_str == "—":
            return float("inf")
        return _parse_rank_numeric(rank_str)

    df["_sort_rank"] = df["Rank"].apply(_rank_sort_key)
    df = df.sort_values("_sort_rank", ascending=True)
    df = df.drop(columns=["_sort_rank", "_in_ranking"])
    return df


def _render_group_table(df: pd.DataFrame, sp_names: set[str]) -> None:
    """Render a styled comparison table highlighting SP universities."""
    display_cols = ["Institution", "Rank", "Score", "AR", "ER", "CpP", "HI", "IRN"]
    disp_df = df[display_cols].copy()

    def highlight_sp(row):
        if row["Institution"] in sp_names:
            return ["background-color: #e8f4fd; font-weight: bold"] * len(row)
        return [""] * len(row)

    sp_short = {_short(u) for u in TARGET_UNIVERSITIES}
    styled = disp_df.style.apply(highlight_sp, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)


def _radar_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Radar chart comparing institutions on 5 indicators."""
    indicators = ["AR", "ER", "CpP", "HI", "IRN"]
    fig = go.Figure()
    for _, row in df.iterrows():
        vals = []
        for ind in indicators:
            try:
                vals.append(float(row[ind]) if row[ind] != "—" else None)
            except (ValueError, TypeError):
                vals.append(None)
        if all(v is None for v in vals):
            continue
        vals_clean = [v if v is not None else 0 for v in vals]
        fig.add_trace(
            go.Scatterpolar(
                r=vals_clean + [vals_clean[0]],
                theta=indicators + [indicators[0]],
                name=row["Institution"],
                mode="lines",
                line=dict(width=2),
            )
        )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=title,
        height=420,
        margin=dict(l=40, r=40, t=60, b=20),
    )
    return fig


def _render_scival_section(
    scival_data: dict,
    sp_universities: list[str],
    selected_faculty: str,
) -> None:
    """Show SciVal bibliometric data for SP universities."""
    if not scival_data:
        return

    rows = []
    for uni_full in sp_universities:
        uni_metrics = scival_data.get(uni_full, {})
        if not uni_metrics:
            continue
        row = {"University": _short(uni_full)}
        cpf = uni_metrics.get("citations_per_faculty", {})
        irn = uni_metrics.get("irn", {})
        if "data" in cpf:
            area_row = cpf["data"][cpf["data"]["faculty_area"] == selected_faculty]
            if not area_row.empty:
                r = area_row.iloc[0]
                for col in ["Scholarly Output (QS)", "Citations (QS)", "Normalized Total Citation Count (QS)"]:
                    if col in r.index and pd.notna(r[col]):
                        row[col.replace(" (QS)", "")] = round(float(r[col]), 1)
        if "data" in irn:
            area_row = irn["data"][irn["data"]["faculty_area"] == selected_faculty]
            if not area_row.empty:
                r = area_row.iloc[0]
                for col in ["Partners (QS)", "International Research Network (IRN) Index (QS)"]:
                    if col in r.index and pd.notna(r[col]):
                        row[col.replace(" (QS)", "")] = round(float(r[col]), 1)
        if len(row) > 1:
            rows.append(row)

    if rows:
        st.markdown("#### SciVal Bibliometrics — SP Universities")
        st.caption(f"Faculty area: {selected_faculty} | Source: QS SciVal exports")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(
            "SciVal data for peer groups requires institutional SciVal exports or a "
            "SciVal Analytics API subscription. Add CSVs to `data/scival/` to extend coverage."
        )


def render(
    qs_data: pd.DataFrame,
    scival_data: dict,
    selected_universities: list[str],
    selected_faculty: str,
    selected_subject: str,
    selected_year: int,
) -> None:
    st.subheader("Peer Benchmarking")

    if qs_data.empty:
        st.warning("No QS data loaded.")
        return

    subject_label = selected_subject
    st.caption(
        f"Subject: **{subject_label}** | Year: **{selected_year}** | "
        "SP universities highlighted in blue."
    )

    sp_short_names = {_short(u) for u in TARGET_UNIVERSITIES}

    group_tabs = st.tabs(list(PEER_GROUPS.keys()))

    for tab_widget, (group_name, group_insts) in zip(group_tabs, PEER_GROUPS.items()):
        with tab_widget:
            df = _build_group_table(
                qs_data=qs_data,
                subject=selected_subject,
                group_institutions=group_insts,
                sp_universities=selected_universities,
                year=selected_year,
            )

            ranked = df[df["Rank"] != "—"]
            unranked = df[df["Rank"] == "—"]

            n_ranked = len(ranked)
            n_group_ranked = len(ranked[ranked["Full Name"].isin(group_insts)])
            n_sp_ranked = len(ranked[ranked["Full Name"].isin(selected_universities)])

            col1, col2, col3 = st.columns(3)
            col1.metric("Group institutions ranked", f"{n_group_ranked} / {len(group_insts)}")
            col2.metric("SP universities ranked", f"{n_sp_ranked} / {len(selected_universities)}")
            if n_ranked > 0:
                top_inst = ranked.iloc[0]
                col3.metric("Top scorer", f"{top_inst['Institution']} ({top_inst['Score']})")

            st.markdown("##### Indicator Scores")
            _render_group_table(df, sp_short_names)

            # Radar chart with selectable institutions
            if not ranked.empty and len(ranked) >= 2:
                indicators = ["AR", "ER", "CpP", "HI", "IRN"]
                # Include banded institutions — they have indicator scores even without overall score
                has_data = ranked[indicators].apply(
                    lambda col: col.apply(lambda x: x != "—")
                ).any(axis=1)
                radar_df = ranked[has_data]
                if len(radar_df) >= 2:
                    st.markdown("##### Radar Comparison")
                    all_names = radar_df["Institution"].tolist()
                    # Default: select all
                    selected_radar = st.multiselect(
                        "Institutions to compare",
                        options=all_names,
                        default=all_names,
                        key=f"radar_{group_name}_{selected_subject}_{selected_year}",
                    )
                    if len(selected_radar) >= 2:
                        filtered_radar = radar_df[radar_df["Institution"].isin(selected_radar)]
                        fig = _radar_chart(filtered_radar, f"{group_name} — {subject_label}")
                        st.plotly_chart(fig, use_container_width=True)
                    elif len(selected_radar) == 1:
                        st.caption("Select at least 2 institutions to display the radar chart.")
                    else:
                        st.caption("No institutions selected.")

            if not unranked.empty:
                with st.expander(f"{len(unranked)} institutions not ranked in this subject"):
                    st.dataframe(
                        unranked[["Institution", "Full Name"]],
                        use_container_width=True,
                        hide_index=True,
                    )

    st.divider()
    _render_scival_section(scival_data, selected_universities, selected_faculty)
