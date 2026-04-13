# tabs/tab2_gap_analysis.py
"""Aba 2: Análise de Lacunas (Nível 1 — Disciplina)."""

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


def _format_rank(rank_val):
    """Formata posição para exibição — trata números e faixas."""
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


def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    if selected_subject == "(nenhuma disciplina disponível)":
        st.warning("Nenhuma disciplina disponível para esta grande área.")
        return

    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
        & (qs_data["institution"].isin(selected_universities))
    )
    df = qs_data[mask].copy()

    if df.empty:
        st.warning(f"Sem dados para {selected_subject} ({selected_year}).")
        return

    df["short_name"] = df["institution"].map(UNIVERSITY_SHORT_NAMES)

    available_unis = sorted(df["short_name"].dropna().unique().tolist())
    if not available_unis:
        st.warning("Nenhuma universidade disponível.")
        return

    focus_uni = st.selectbox("Universidade de foco", available_unis, key="gap_focus")

    # Posições no ranking para todas as universidades
    rank_cols = st.columns(min(len(available_unis), 6))
    for i, uni in enumerate(available_unis):
        uni_row = df[df["short_name"] == uni].iloc[0]
        rank_val = uni_row.get("rank_display", uni_row.get("rank"))
        score_val = uni_row.get("overall_score")
        with rank_cols[i % len(rank_cols)]:
            rank_display = _format_rank(rank_val)
            score_display = f"{score_val:.1f}" if pd.notna(score_val) else "—"
            st.metric(uni, rank_display, help=f"Escore geral: {score_display}")

    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"Pesos não definidos para {selected_subject}.")
        return

    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    focus_row = df[df["short_name"] == focus_uni].iloc[0]
    focus_scores = {ind: (focus_row.get(ind, 0) if pd.notna(focus_row.get(ind)) else 0) for ind in indicators_in_use}

    peers_df = df[df["short_name"] != focus_uni]
    if peers_df.empty:
        st.info("Selecione ao menos 2 universidades para comparar.")
        return

    peer_avg = {}
    for ind in indicators_in_use:
        vals = pd.to_numeric(peers_df[ind], errors="coerce").dropna()
        peer_avg[ind] = vals.mean() if len(vals) > 0 else 0

    # Gráfico radar
    fig = go.Figure()
    labels = [INDICATOR_NAMES.get(ind, ind) for ind in indicators_in_use]
    focus_values = [focus_scores[ind] for ind in indicators_in_use]
    peer_values = [peer_avg[ind] for ind in indicators_in_use]

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
        name="Média das Pares SP",
        fillcolor="rgba(255, 127, 14, 0.2)",
        line_color="rgba(255, 127, 14, 1)",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=f"Análise de Lacunas — {focus_uni} vs. Pares Paulistas em {selected_subject}",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de oportunidades
    opportunities = []
    for ind in indicators_in_use:
        gap = peer_avg[ind] - focus_scores[ind]
        weight = subject_weights.get(ind, 0)
        if gap > 0:
            opportunities.append({
                "indicator": ind,
                "Indicador": INDICATOR_NAMES.get(ind, ind),
                "Seu Escore": f"{focus_scores[ind]:.1f}",
                "Média das Pares": f"{peer_avg[ind]:.1f}",
                "Lacuna": f"{gap:.1f}",
                "Peso": f"{weight}%",
                "gap_points": gap * weight / 100,
                "Impacto Ponderado": f"{gap * weight / 100:.1f} pts",
            })

    opportunities.sort(key=lambda x: x["gap_points"], reverse=True)

    st.markdown(f"**{gap_analysis_insight(focus_uni, selected_subject, opportunities)}**")

    if opportunities:
        opp_df = pd.DataFrame(opportunities)[
            ["Indicador", "Seu Escore", "Média das Pares", "Lacuna", "Peso", "Impacto Ponderado"]
        ]
        st.dataframe(opp_df, use_container_width=True, hide_index=True)
    else:
        st.success(f"{focus_uni} lidera ou empata com as pares em todos os indicadores!")
