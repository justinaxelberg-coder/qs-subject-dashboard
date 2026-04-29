# tabs/tab4_simulator.py
"""Aba 4: Simulador — análise hipotética com posição no ranking e impacto bibliométrico."""

import streamlit as st
import pandas as pd
import numpy as np

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES, INDICATOR_COLORS
from src.weights import get_subject_weights
from src.simulator import simulate_score_change
from src.interpretive import indicator_help_text


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


def _estimate_rank_band(simulated_score, subject_df):
    """Estima a faixa de posição para um escore simulado."""
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
    """Extrai valores bibliométricos brutos atuais da universidade de foco."""
    if not scival_data or focus_full not in scival_data:
        return {}

    uni_metrics = scival_data[focus_full]
    result = {}

    if "citations_per_faculty" in uni_metrics:
        df = uni_metrics["citations_per_faculty"]["data"]
        area_row = df[df["faculty_area"] == selected_faculty]
        if not area_row.empty:
            r = area_row.iloc[0]
            result["CpP"] = {
                "Produção Científica": r.get("Scholarly Output (QS)"),
                "Citações": r.get("Citations (QS)"),
                "Citações Normalizadas": r.get("Normalized Total Citation Count (QS)"),
                "Fator de Ponderação": r.get("Weighting Factor (QS)"),
            }

    if "irn" in uni_metrics:
        df = uni_metrics["irn"]["data"]
        area_row = df[df["faculty_area"] == selected_faculty]
        if not area_row.empty:
            r = area_row.iloc[0]
            result["IRN"] = {
                "Produção Científica (IRN)": r.get("IRN Scholarly Output (QS)"),
                "Localidades": r.get("Locations (QS)"),
                "Parceiros": r.get("Partners (QS)"),
                "Índice IRN": r.get("International Research Network (IRN) Index (QS)"),
            }

    return result


def _estimate_bibliometric_changes(indicator, score_change, raw_context):
    """Estima as mudanças bibliométricas reais que uma variação de escore implica."""
    if not raw_context or indicator not in raw_context:
        return None

    metrics = raw_context[indicator]
    changes = []

    if indicator == "CpP":
        norm_cit = metrics.get("Citações Normalizadas")
        scholarly_out = metrics.get("Produção Científica")
        citations = metrics.get("Citações")

        if norm_cit and pd.notna(norm_cit) and scholarly_out and pd.notna(scholarly_out):
            pct_change = score_change / 100.0
            cit_change = norm_cit * pct_change
            direcao = "a mais" if cit_change > 0 else "a menos"
            changes.append(f"~{abs(cit_change):,.0f} citações normalizadas {direcao}")

        if citations and pd.notna(citations):
            pct_change = score_change / 100.0
            raw_cit_change = citations * pct_change
            direcao = "a mais" if raw_cit_change > 0 else "a menos"
            changes.append(f"~{abs(raw_cit_change):,.0f} citações brutas {direcao}")

    elif indicator == "IRN":
        partners = metrics.get("Parceiros")
        locations = metrics.get("Localidades")

        if partners and pd.notna(partners):
            pct_change = score_change / 100.0
            partner_change = partners * pct_change
            direcao = "a mais" if partner_change > 0 else "a menos"
            changes.append(f"~{abs(partner_change):,.0f} parceiros internacionais {direcao}")

        if locations and pd.notna(locations):
            pct_change = score_change / 100.0
            loc_change = locations * pct_change
            direcao = "a mais" if loc_change > 0 else "a menos"
            changes.append(f"~{abs(loc_change):,.0f} localidades parceiras {direcao}")

    return changes if changes else None


def render(qs_data, scival_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    st.subheader(f"Explorar os Pesos — {selected_subject}")
    st.markdown("Explore como os pesos de cada indicador determinam o escore final")

    if selected_subject == "(nenhuma disciplina disponível)":
        st.warning("Nenhuma disciplina disponível para esta grande área.")
        return

    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
    )
    subject_df = qs_data[mask].copy()

    our_df = subject_df[subject_df["institution"].isin(selected_universities)].copy()
    our_df["short_name"] = our_df["institution"].map(UNIVERSITY_SHORT_NAMES)

    available_unis = sorted(our_df["short_name"].dropna().unique().tolist())
    if not available_unis:
        st.warning(f"Nenhuma universidade encontrada em {selected_subject} ({selected_year}).")
        return

    focus_uni = st.selectbox("Universidade de foco", available_unis, key="sim_focus")
    focus_row = our_df[our_df["short_name"] == focus_uni].iloc[0]
    focus_full = focus_row["institution"]

    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"Pesos não definidos para {selected_subject}.")
        return

    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    current_scores = {}
    for ind in indicators_in_use:
        val = focus_row.get(ind)
        current_scores[ind] = float(val) if pd.notna(val) else 0.0

    current_rank_display = focus_row.get("rank_display", focus_row.get("rank"))
    current_overall = focus_row.get("overall_score")

    rank_str = _format_rank(current_rank_display)
    score_display = f"{current_overall:.1f}" if pd.notna(current_overall) else "—"
    st.markdown(f"**Posição atual:** {rank_str} (escore: {score_display})")

    raw_context = _get_scival_context(scival_data, focus_full, selected_faculty)

    st.markdown("---")
    st.markdown(
        "Ajuste os valores dos indicadores para entender como o modelo de ponderação "
        "do QS funciona na prática. Este não é um plano de ação — é uma lente metodológica."
    )

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
                help=indicator_help_text(ind),
            )

    result = simulate_score_change(current_scores, adjusted_scores, subject_weights)

    simulated_overall = result["simulated_total"]
    estimated_rank_str = _estimate_rank_band(simulated_overall, subject_df)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Escore Atual", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Escore Hipotético", f"{result['simulated_total']:.1f}",
                   delta=f"{result['delta']:+.1f}")
    with col3:
        st.metric("Posição Atual", rank_str)
    with col4:
        st.metric("Posição equivalente", estimated_rank_str)
        st.caption("posição estimada assumindo que as demais instituições permanecem constantes")

    st.markdown("**Impacto por indicador:**")
    delta_data = []
    bibliometric_notes = []
    for ind in indicators_in_use:
        delta = result["indicator_deltas"].get(ind, 0)
        weight = subject_weights.get(ind, 0)
        score_change = adjusted_scores.get(ind, 0) - current_scores.get(ind, 0)
        row_data = {
            "Indicador": INDICATOR_NAMES.get(ind, ind),
            "Peso": f"{weight}%",
            "Atual": f"{current_scores.get(ind, 0):.1f}",
            "Ajustado": f"{adjusted_scores.get(ind, 0):.1f}",
            "Δ Escore": f"{score_change:+.1f}",
            "Peso no escore": f"{delta:+.1f} pts",
        }
        delta_data.append(row_data)

        if abs(score_change) > 0.1:
            bib_changes = _estimate_bibliometric_changes(ind, score_change, raw_context)
            if bib_changes:
                for change in bib_changes:
                    bibliometric_notes.append(f"**{INDICATOR_NAMES.get(ind, ind)}** ({score_change:+.1f} pts): {change}")

    st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)

    if bibliometric_notes:
        st.markdown("---")
        st.markdown("#### 📐 O que isso significa na prática")
        st.caption(f"Com base nos dados SciVal atuais de {focus_uni} em {selected_faculty}:")
        for note in bibliometric_notes:
            st.markdown(f"- {note}")
    elif any(abs(adjusted_scores[ind] - current_scores[ind]) > 0.1 for ind in indicators_in_use):
        if not raw_context:
            st.info(
                f"💡 Adicione os CSVs do SciVal de {focus_uni} em `data/scival/` para ver "
                f"quais mudanças bibliométricas reais esses ajustes de escore exigiriam."
            )

    if raw_context:
        with st.expander(f"📊 Valores SciVal atuais — {focus_uni} em {selected_faculty}"):
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

    with st.expander("Contexto do ranking — universidades próximas"):
        _show_ranking_context(subject_df, focus_row, simulated_overall, selected_subject)

    st.caption(
        "Estimativas bibliométricas são aproximações lineares com base nos dados SciVal atuais. "
        "Reputação Acadêmica e com Empregadores são baseadas em surveys e refletem percepções "
        "acumuladas — mais difíceis de influenciar diretamente."
    )


def _show_ranking_context(subject_df, focus_row, simulated_score, subject_name):
    """Exibe universidades próximas à posição atual e simulada."""
    cols_needed = ["institution", "rank_display", "overall_score"]
    available_cols = [c for c in cols_needed if c in subject_df.columns]
    ranked = subject_df[available_cols].dropna(subset=["overall_score"]).copy()
    ranked = ranked.sort_values("overall_score", ascending=False).reset_index(drop=True)

    focus_inst = focus_row["institution"]

    current_idx = ranked.index[ranked["institution"] == focus_inst]
    if len(current_idx) == 0:
        st.info("Esta universidade não possui escore ranqueado nesta disciplina.")
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
    context["Posição QS"] = context[rank_col].apply(_format_rank)
    context["Escore"] = context["overall_score"].apply(lambda x: f"{x:.1f}")

    st.dataframe(
        context[["", "institution", "Posição QS", "Escore"]].rename(columns={"institution": "Universidade"}),
        use_container_width=True,
        hide_index=True,
    )

    if pd.notna(simulated_score):
        est_rank = _estimate_rank_band(simulated_score, subject_df)
        focus_short = UNIVERSITY_SHORT_NAMES.get(focus_inst, focus_inst)
        st.info(f"Com um escore simulado de **{simulated_score:.1f}**, "
                f"{focus_short} estaria em aproximadamente "
                f"**{est_rank}** em {subject_name}.")
