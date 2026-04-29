# tabs/tab5_benchmarking.py
"""Tab 5: Peer Benchmarking — QS indicator scores + SciVal bibliometrics."""

import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.constants import (
    PEER_GROUPS,
    TARGET_UNIVERSITIES,
    UNIVERSITY_SHORT_NAMES,
)
from src.interpretive import indicator_help_text

# Layout: which groups appear in the top regional section vs. international expander
_REGIONAL_GROUPS = ["Líderes Brasileiras (excl. SP)", "Líderes Latino-Americanas", "Ibero-Americanas"]
_INTERNATIONAL_GROUPS = ["C9 Chinesas", "Russell Group", "Pares BRICS", "Leste Asiático em Ascensão"]


def _display_name(name: str) -> str:
    """Clean, readable display name.

    SP universities keep their well-known short brand (USP, UNICAMP …).
    All other institutions show their full name with trailing all-caps
    parenthetical abbreviations stripped (e.g. "(NUS)", "(UFMG)") and
    double-spaces normalised.
    """
    if name in UNIVERSITY_SHORT_NAMES:
        return UNIVERSITY_SHORT_NAMES[name]
    # Strip trailing all-caps abbreviation in parentheses, e.g. "(NUS)", "(UFMG)", "(UC)"
    cleaned = re.sub(r"\s*\([A-Z][A-Z0-9\-]{1,9}\)\s*$", "", name).strip()
    # Normalise double spaces (QS data for UNAM has "México  (UNAM)")
    cleaned = re.sub(r"  +", " ", cleaned)
    return cleaned


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
    """Return a sorted table of QS indicator scores for the peer group + SP universities."""
    from src.data_loader import _parse_rank_numeric

    subject_df = qs_data[
        (qs_data["subject"] == subject) & (qs_data["year"] == year)
    ].copy()

    all_institutions = list(dict.fromkeys(group_institutions + sp_universities))
    rows = []
    for inst in all_institutions:
        row_df = subject_df[subject_df["institution"] == inst]
        is_sp = inst in sp_universities
        display = _display_name(inst)
        if row_df.empty:
            rows.append({
                "Institution": display,
                "_full_name": inst,
                "Rank": "—",
                "Score": "—",
                "AR": "—",
                "ER": "—",
                "CpP": "—",
                "HI": "—",
                "IRN": "—",
                "_is_sp": is_sp,
                "_in_ranking": False,
            })
        else:
            r = row_df.iloc[0]
            rows.append({
                "Institution": display,
                "_full_name": inst,
                "Rank": _fmt_rank(r.get("rank_display", "—")),
                "Score": _fmt_score(r.get("overall_score")),
                "AR": _fmt_score(r.get("AR")),
                "ER": _fmt_score(r.get("ER")),
                "CpP": _fmt_score(r.get("CpP")),
                "HI": _fmt_score(r.get("HI")),
                "IRN": _fmt_score(r.get("IRN")),
                "_is_sp": is_sp,
                "_in_ranking": True,
            })

    df = pd.DataFrame(rows)

    def _rank_sort_key(rank_str):
        if rank_str == "—":
            return float("inf")
        return _parse_rank_numeric(rank_str)

    df["_sort_rank"] = df["Rank"].apply(_rank_sort_key)
    df = df.sort_values("_sort_rank").drop(columns=["_sort_rank", "_in_ranking"])
    return df


def _render_group_table(df: pd.DataFrame) -> None:
    """Render comparison table with SP universities highlighted in blue."""
    display_cols = ["Institution", "Rank", "Score", "AR", "ER", "CpP", "HI", "IRN"]
    disp_df = df[display_cols].copy()

    sp_display_names = {_display_name(u) for u in TARGET_UNIVERSITIES}

    def highlight_sp(row):
        if row["Institution"] in sp_display_names:
            return ["background-color: #e8f4fd; font-weight: bold"] * len(row)
        return [""] * len(row)

    styled = disp_df.style.apply(highlight_sp, axis=1)

    col_cfg = {
        ind: st.column_config.TextColumn(ind, help=indicator_help_text(ind))
        for ind in ["AR", "ER", "CpP", "HI", "IRN"]
    }
    st.dataframe(styled, use_container_width=True, hide_index=True, column_config=col_cfg)


def _radar_chart(df: pd.DataFrame, title: str) -> go.Figure:
    """Radar chart comparing institutions on 5 QS indicators."""
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
        fig.add_trace(go.Scatterpolar(
            r=vals_clean + [vals_clean[0]],
            theta=indicators + [indicators[0]],
            name=row["Institution"],
            mode="lines",
            line=dict(width=2),
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=title,
        height=450,
        margin=dict(l=40, r=40, t=60, b=20),
    )
    return fig


def _render_group(
    group_name: str,
    group_insts: list[str],
    qs_data: pd.DataFrame,
    selected_subject: str,
    selected_universities: list[str],
    selected_year: int,
) -> None:
    """Render the full comparison block for one peer group."""
    df = _build_group_table(
        qs_data=qs_data,
        subject=selected_subject,
        group_institutions=group_insts,
        sp_universities=selected_universities,
        year=selected_year,
    )

    ranked = df[df["Rank"] != "—"]
    unranked = df[df["Rank"] == "—"]

    n_group_ranked = len(ranked[ranked["_full_name"].isin(group_insts)])
    n_sp_ranked = len(ranked[ranked["_full_name"].isin(selected_universities)])

    col1, col2, col3 = st.columns(3)
    col1.metric("Instituições do grupo ranqueadas", f"{n_group_ranked} / {len(group_insts)}")
    col2.metric("Universidades SP ranqueadas", f"{n_sp_ranked} / {len(selected_universities)}")
    if not ranked.empty:
        top = ranked.iloc[0]
        col3.metric("Maior escore", f"{top['Institution']} ({top['Score']})")

    _render_group_table(df)

    # Radar chart
    indicators = ["AR", "ER", "CpP", "HI", "IRN"]
    has_data = ranked[indicators].apply(lambda c: c != "—").any(axis=1)
    radar_df = ranked[has_data]
    if len(radar_df) >= 2:
        st.markdown("##### Comparação em Radar")
        all_names = radar_df["Institution"].tolist()
        selected_radar = st.multiselect(
            "Instituições a comparar",
            options=all_names,
            default=all_names,
            key=f"radar_{group_name}_{selected_subject}_{selected_year}",
        )
        if len(selected_radar) >= 2:
            fig = _radar_chart(
                radar_df[radar_df["Institution"].isin(selected_radar)],
                f"{group_name} — {selected_subject}",
            )
            st.plotly_chart(fig, use_container_width=True)
        elif len(selected_radar) == 1:
            st.caption("Selecione ao menos 2 instituições para exibir o gráfico radar.")

    if not unranked.empty:
        with st.expander(f"{len(unranked)} instituições não ranqueadas nesta disciplina"):
            st.dataframe(
                unranked[["Institution"]].rename(columns={"Institution": "Instituição (não ranqueada)"}),
                use_container_width=True,
                hide_index=True,
            )


def _render_scival_section(
    scival_data: dict,
    sp_universities: list[str],
    selected_faculty: str,
) -> None:
    """SciVal bibliometric data for SP universities (faculty area level)."""
    if not scival_data:
        return

    rows = []
    for uni_full in sp_universities:
        uni_metrics = scival_data.get(uni_full, {})
        if not uni_metrics:
            continue
        row = {"University": _display_name(uni_full)}
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
        st.markdown("#### Bibliometria SciVal — Universidades SP")
        st.caption(f"Grande área: {selected_faculty} | Fonte: exportações SciVal QS")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(
            "Dados SciVal para os grupos de pares requerem exportações institucionais ou "
            "assinatura da API SciVal Analytics. Adicione CSVs em `data/scival/` para ampliar a cobertura."
        )


def render(
    qs_data: pd.DataFrame,
    scival_data: dict,
    selected_universities: list[str],
    selected_faculty: str,
    selected_subject: str,
    selected_year: int,
) -> None:
    st.subheader("Contexto Internacional")

    if qs_data.empty:
        st.warning("Nenhum dado QS carregado.")
        return

    st.caption(
        f"Disciplina: **{selected_subject}** | Ano: **{selected_year}** | "
        "Universidades SP destacadas em azul. "
        "Compare o perfil das universidades paulistas com grupos institucionais "
        "internacionais. Diferenças de escore refletem contextos históricos, "
        "de financiamento e de missão distintos."
    )

    # ── Regional peers (top section) ─────────────────────────────────────────
    regional_tabs = st.tabs(_REGIONAL_GROUPS)
    for tab_widget, group_name in zip(regional_tabs, _REGIONAL_GROUPS):
        with tab_widget:
            _render_group(
                group_name=group_name,
                group_insts=PEER_GROUPS[group_name],
                qs_data=qs_data,
                selected_subject=selected_subject,
                selected_universities=selected_universities,
                selected_year=selected_year,
            )

    # ── International benchmarks (collapsible) ───────────────────────────────
    st.divider()
    with st.expander("🌍 Benchmarks Internacionais", expanded=False):
        intl_tabs = st.tabs(_INTERNATIONAL_GROUPS)
        for tab_widget, group_name in zip(intl_tabs, _INTERNATIONAL_GROUPS):
            with tab_widget:
                _render_group(
                    group_name=group_name,
                    group_insts=PEER_GROUPS[group_name],
                    qs_data=qs_data,
                    selected_subject=selected_subject,
                    selected_universities=selected_universities,
                    selected_year=selected_year,
                )

    # ── SciVal bibliometrics ─────────────────────────────────────────────────
    st.divider()
    _render_scival_section(scival_data, selected_universities, selected_faculty)
