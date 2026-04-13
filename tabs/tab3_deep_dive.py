# tabs/tab3_deep_dive.py
"""Aba 3: Análise Bibliométrica Detalhada (Nível 2 — Grande Área)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.constants import UNIVERSITY_SHORT_NAMES, UNIVERSITY_COLORS


# Configurações de métricas por tipo de exportação SciVal
CITATIONS_METRICS = [
    ("Scholarly Output (QS)", "Produção Científica"),
    ("Citations (QS)", "Citações"),
    ("Normalized Total Citation Count (QS)", "Citações Normalizadas"),
]

IRN_METRICS = [
    ("IRN Scholarly Output (QS)", "Produção Científica (IRN)"),
    ("Locations (QS)", "Localidades"),
    ("Partners (QS)", "Parceiros"),
    ("International Research Network (IRN) Index (QS)", "Índice IRN"),
]


def render(scival_data, selected_universities, selected_faculty, is_broad_field=False):
    if not scival_data:
        st.warning(
            "Nenhum dado SciVal carregado. Adicione os CSVs exportados do SciVal "
            "na pasta `data/scival/` e reinicie o aplicativo."
        )
        return

    st.subheader(f"Análise Bibliométrica — {selected_faculty}")

    uni_data = {}
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            uni_data[uni_short] = scival_data[uni_full]

    if not uni_data:
        st.warning("Nenhum dado SciVal disponível para as universidades selecionadas.")
        return

    if is_broad_field:
        _render_broad_field_overview(uni_data)
    else:
        st.markdown("### Citações por Corpo Docente")
        _render_metric_comparison(
            uni_data, selected_faculty, "citations_per_faculty",
            CITATIONS_METRICS, "citation_per_faculty_score", "Escore de Citações por Corpo Docente"
        )

        st.markdown("### Rede Internacional de Pesquisa")
        _render_metric_comparison(
            uni_data, selected_faculty, "irn",
            IRN_METRICS, "irn_score", "Escore IRN"
        )


def _render_metric_comparison(
    uni_data, faculty_area, metric_type, metric_configs, score_key, score_label
):
    """Gráfico de barras agrupadas comparando valores SciVal entre universidades."""
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
                    "Universidade": uni_short,
                    "Métrica": display_name,
                    "Valor": float(row[col_name]),
                })

    if not chart_data:
        st.info(f"Sem dados de {metric_type} para {faculty_area}.")
        return

    chart_df = pd.DataFrame(chart_data)
    metrics_list = [m[1] for m in metric_configs]

    cols = st.columns(min(len(metrics_list), 3))
    for i, metric_name in enumerate(metrics_list):
        metric_df = chart_df[chart_df["Métrica"] == metric_name]
        if metric_df.empty:
            continue

        col = cols[i % len(cols)]
        with col:
            fig = go.Figure()
            for _, row in metric_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[row["Universidade"]],
                    y=[row["Valor"]],
                    name=row["Universidade"],
                    marker_color=UNIVERSITY_COLORS.get(row["Universidade"], "#999"),
                    showlegend=False,
                    hovertemplate=f"<b>{row['Universidade']}</b><br>{metric_name}: %{{y:,.0f}}<extra></extra>",
                ))
            fig.update_layout(
                title=metric_name,
                height=300,
                margin=dict(l=10, r=10, t=40, b=30),
                yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

    if any(v is not None for v in overall_scores.values()):
        scores_text = " | ".join(
            f"**{uni}**: {score}" for uni, score in overall_scores.items() if score is not None
        )
        st.caption(f"{score_label}: {scores_text}")


def _render_broad_field_overview(uni_data):
    """Comparação entre grandes áreas para cada universidade."""
    from src.constants import FACULTY_AREAS

    st.markdown("### Citações por Corpo Docente — Todas as Áreas")
    _render_cross_area_chart(uni_data, "citations_per_faculty", CITATIONS_METRICS, FACULTY_AREAS)

    st.markdown("### Rede Internacional de Pesquisa — Todas as Áreas")
    _render_cross_area_chart(uni_data, "irn", IRN_METRICS, FACULTY_AREAS)

    st.markdown("### Valores Brutos por Grande Área")
    for metric_type, label, metric_configs in [
        ("citations_per_faculty", "Citações por Corpo Docente", CITATIONS_METRICS),
        ("irn", "Rede Internacional de Pesquisa", IRN_METRICS),
    ]:
        rows = []
        for uni_short, metrics in uni_data.items():
            if metric_type not in metrics:
                continue
            df = metrics[metric_type]["data"]
            for _, area_row in df.iterrows():
                row_data = {"Universidade": uni_short, "Grande Área": area_row.get("faculty_area", "")}
                for col_name, display_name in metric_configs:
                    if col_name in area_row.index and pd.notna(area_row[col_name]):
                        row_data[display_name] = area_row[col_name]
                rows.append(row_data)
        if rows:
            st.markdown(f"**{label}**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _render_cross_area_chart(uni_data, metric_type, metric_configs, faculty_areas):
    """Gráfico de barras comparando universidades em todas as grandes áreas."""
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
                    "Universidade": uni_short,
                    "Grande Área": area,
                    "Valor": float(val),
                })

    if not chart_data:
        st.info(f"Sem dados de {metric_type}.")
        return

    chart_df = pd.DataFrame(chart_data)
    fig = go.Figure()
    for uni in sorted(chart_df["Universidade"].unique()):
        uni_df = chart_df[chart_df["Universidade"] == uni]
        fig.add_trace(go.Bar(
            x=uni_df["Grande Área"],
            y=uni_df["Valor"],
            name=uni,
            marker_color=UNIVERSITY_COLORS.get(uni, "#999"),
            hovertemplate=f"<b>{uni}</b><br>%{{x}}<br>{key_label}: %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        title=f"{key_label} por Grande Área",
        height=400,
        margin=dict(l=10, r=10, t=50, b=80),
        xaxis_tickangle=-25,
        legend_title="Universidade",
    )
    st.plotly_chart(fig, use_container_width=True)
