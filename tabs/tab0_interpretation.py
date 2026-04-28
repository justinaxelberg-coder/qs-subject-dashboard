# tabs/tab0_interpretation.py
"""Tab 0: Como Interpretar — interpretive briefing for the QS Subject Rankings."""

import streamlit as st

from src.interpretive import leiden_principles, recommended_readings


# Indicator detail content used only in this tab (richer than the popover version)
_INDICATOR_DETAILS: dict[str, dict] = {
    "AR": {
        "title": "Reputação Acadêmica (AR)",
        "mede": (
            "Percepção de excelência acadêmica por pesquisadores de todo o mundo, "
            "via survey anual com ~170.000 respondentes."
        ),
        "coleta": (
            "Survey online enviado a pesquisadores ativos globalmente. "
            "Cada respondente avalia até 30 instituições em sua área de expertise."
        ),
        "peso": "40–50% na maioria dos sujeitos; até 50% em Artes & Humanidades.",
        "notas": [
            "O survey pergunta sobre a instituição como um todo — não sobre a área "
            "específica sendo ranqueada. Isso favorece instituições com alta "
            "visibilidade global independentemente do desempenho na área avaliada.",
            "Reputação é acumulativa e lenta a mudar; reflete trajetória histórica "
            "mais do que desempenho recente.",
            "Em muitos sujeitos, AR responde sozinha por 40–50% do escore total.",
        ],
    },
    "ER": {
        "title": "Reputação com Empregadores (ER)",
        "mede": (
            "Preferências de recrutamento de ~100.000 empregadores globais, "
            "via survey anual."
        ),
        "coleta": (
            "Survey online com empregadores globais. "
            "Avalia preferências de recrutamento por instituição de origem."
        ),
        "peso": "10–20% na maioria dos sujeitos.",
        "notas": [
            "Também avalia a instituição globalmente, não por área. "
            "Fortemente influenciado por presença geográfica e visibilidade de marca.",
            "Mais relevante para cursos profissionalizantes (Direito, Medicina, "
            "Administração) do que para pesquisa de ponta.",
        ],
    },
    "CpP": {
        "title": "Citações por Artigo (CpP)",
        "mede": (
            "Impacto médio das publicações da instituição na área, "
            "normalizado por campo e ano."
        ),
        "coleta": (
            "Dados bibliométricos da base Scopus. Calcula média de citações por "
            "artigo publicado no período de avaliação."
        ),
        "peso": "20–30% na maioria dos sujeitos.",
        "notas": [
            "Padrões de citação variam enormemente entre disciplinas — "
            "humanidades e ciências sociais são estruturalmente desfavorecidas.",
            "Normalização por campo é parcial; sub-áreas dentro de uma grande área "
            "podem ter padrões muito distintos.",
        ],
    },
    "HI": {
        "title": "Índice H (HI)",
        "mede": (
            "O maior número H tal que H publicações tenham sido citadas ao menos H vezes. "
            "O QS utiliza uma janela temporal limitada, não o H-index acumulado completo."
        ),
        "coleta": (
            "Calculado a partir dos dados Scopus para o período de avaliação do ranking."
        ),
        "peso": "10–20% na maioria dos sujeitos.",
        "notas": [
            "Mesmo com janela temporal, permanece estruturalmente favorável a volumes "
            "maiores de publicação: favorece instituições maiores e mais antigas.",
            "Crescimento é necessariamente lento independentemente do desempenho atual.",
            "Não distingue entre publicações recentes e antigas dentro da janela avaliada.",
        ],
    },
    "IRN": {
        "title": "Rede Internacional de Pesquisa (IRN)",
        "mede": (
            "Volume e diversidade das colaborações internacionais de pesquisa "
            "da instituição."
        ),
        "coleta": (
            "Calculado a partir de co-autorias internacionais em publicações Scopus."
        ),
        "peso": "10–25% dependendo da área.",
        "notas": [
            "Mede volume, não qualidade das colaborações. "
            "Favorece instituições grandes com mais docentes publicando.",
            "Instituições menores e mais especializadas são estruturalmente "
            "desfavorecidas mesmo com colaborações de alta qualidade.",
        ],
    },
}


def render() -> None:
    """Render the 'Como Interpretar' tab."""
    st.subheader("Como Interpretar o QS Subject Rankings")
    st.caption(
        "Antes de explorar os dados, leia este briefing sobre o que o ranking mede, "
        "como os indicadores funcionam, e princípios para uma interpretação responsável."
    )

    # ── Block 1: O que o QS Subject Rankings mede ────────────────────────────
    st.markdown("### O que o QS Subject Rankings mede")
    st.markdown(
        "O QS Subject Rankings classifica universidades por **área do conhecimento** — "
        "não por desempenho institucional geral. Cada edição cobre aproximadamente "
        "55 disciplinas distribuídas em 5 grandes áreas.\n\n"
        "- Os **escores** são compostos ponderados de 5 indicadores; "
        "os **pesos variam por área e por disciplina**\n"
        "- Instituições com posições em **faixas** (e.g. 251–300) podem ter escores "
        "praticamente idênticos — a faixa não reflete diferenças reais de desempenho\n"
        "- O ranking **não avalia** ensino de graduação, impacto social, extensão, "
        "relevância regional, ou pesquisa em língua portuguesa"
    )

    # ── Block 2: Os cinco indicadores ────────────────────────────────────────
    st.markdown("### Os cinco indicadores")
    st.info(
        "⚠️ **Reputação domina o escore:** Reputação Acadêmica (AR) + Reputação com "
        "Empregadores (ER) respondem por **50% a 70% do escore total**, dependendo da área. "
        "Ambos os surveys avaliam a **instituição como um todo** — não a área específica "
        "sendo ranqueada. Um pesquisador que nomeia uma universidade em Ciências da "
        "Computação está avaliando sua impressão geral da instituição, não o departamento "
        "de computação especificamente. Isso favorece estruturalmente universidades "
        "maiores e mais antigas, independentemente da qualidade na área avaliada."
    )

    for code, detail in _INDICATOR_DETAILS.items():
        with st.expander(detail["title"]):
            st.markdown(f"**O que mede:** {detail['mede']}")
            st.markdown(f"**Como é coletado:** {detail['coleta']}")
            st.markdown(f"**Peso típico:** {detail['peso']}")
            st.markdown("**Notas de interpretação:**")
            for note in detail["notas"]:
                st.markdown(f"- {note}")

    # ── Block 3: Princípios de interpretação responsável ─────────────────────
    st.markdown("### Princípios de interpretação responsável")

    _PRINCIPLES = [
        (
            "Rankings capturam reputação tanto quanto qualidade",
            "AR e ER respondem por 50–70% do escore. Reputação é acumulativa, "
            "lenta a mudar, e não reflete necessariamente desempenho atual.",
        ),
        (
            "Posições em faixas não refletem diferenças reais",
            "Uma universidade na posição 251 e outra na posição 300 podem ter escores "
            "praticamente idênticos. Tratar faixas como posições ordinais precisas "
            "é metodologicamente incorreto.",
        ),
        (
            "Comparações entre grandes áreas não são válidas",
            "Os pesos dos indicadores variam por área; escores não são comparáveis "
            "entre grandes áreas.",
        ),
        (
            "Melhorias de escore nem sempre refletem mudanças reais",
            "Variações pequenas podem resultar de mudanças metodológicas, amostragem "
            "diferente nos surveys, ou flutuações estatísticas.",
        ),
        (
            "O que o ranking não mede é tão importante quanto o que mede",
            "Impacto social, extensão, ensino de graduação, relevância regional, "
            "e pesquisa em língua portuguesa não aparecem no escore.",
        ),
    ]

    for i, (title, note) in enumerate(_PRINCIPLES, 1):
        st.markdown(f"**{i}. {title}**")
        st.caption(note)

    # ── Block 4: O Manifesto de Leiden ───────────────────────────────────────
    st.markdown("### O Manifesto de Leiden")
    st.markdown(
        "O [Manifesto de Leiden para Métricas de Pesquisa](https://doi.org/10.1038/520429a) "
        "(Hicks, Wouters, Waltman, De Rijcke & Rafols, *Nature*, 2015) estabelece "
        "10 princípios para o uso responsável de indicadores quantitativos na avaliação "
        "da pesquisa. Os quatro princípios abaixo são diretamente aplicáveis à "
        "interpretação de rankings de universidades."
    )

    principles_data = leiden_principles()
    highlighted = [p for p in principles_data if p["highlighted"]]
    others = [p for p in principles_data if not p["highlighted"]]

    for p in highlighted:
        st.info(
            f"**Princípio {p['number']}: {p['title']}**\n\n{p['description']}"
        )

    with st.expander("Ver os demais princípios"):
        for p in others:
            st.markdown(
                f"**{p['number']}.** {p['title']} — {p['description']}"
            )

    st.link_button(
        "📄 Ler o Manifesto de Leiden completo",
        "https://doi.org/10.1038/520429a",
    )

    # ── Block 5: Leituras recomendadas ────────────────────────────────────────
    st.markdown("### Leituras recomendadas")

    readings = recommended_readings()
    for r in readings:
        citation = f"**{r['title']}**  \n{r['authors']} ({r['year']})"
        if r.get("doi"):
            citation += f". DOI: {r['doi']}"
        st.markdown(citation)
        if r.get("url"):
            st.link_button(
                "Acessar →",
                r["url"],
                key=f"reading_{r['year']}_{r['authors'][:8]}",
            )
        st.markdown("")  # visual spacing between entries
