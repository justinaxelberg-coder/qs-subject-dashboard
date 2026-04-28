# src/interpretive.py
"""Interpretive content for the QS Subject Rankings Dashboard.

Provides:
  - indicator_popover(code)      — renders a st.popover() block (no return value)
  - indicator_help_text(code)    — returns annotation as plain string for help= params
  - leiden_principles()          — returns list[dict] of the 10 Leiden principles
  - recommended_readings()       — returns list[dict] of recommended readings
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Indicator annotation content
# ---------------------------------------------------------------------------

_INDICATOR_CONTENT: dict[str, dict] = {
    "AR": {
        "title": "Reputação Acadêmica (AR)",
        "what": (
            "Percepção de excelência acadêmica por pesquisadores de todo o mundo, "
            "via survey anual com ~170.000 respondentes."
        ),
        "notes": [
            "O survey pergunta sobre a instituição como um todo — não sobre a área "
            "específica sendo ranqueada. Isso favorece instituições com alta visibilidade global.",
            "Reputação é acumulativa e lenta a mudar; reflete trajetória histórica "
            "mais do que desempenho recente.",
            "Em muitos sujeitos, AR responde sozinha por 40–50% do escore total.",
        ],
    },
    "ER": {
        "title": "Reputação com Empregadores (ER)",
        "what": (
            "Preferências de recrutamento de ~100.000 empregadores globais, "
            "via survey anual."
        ),
        "notes": [
            "Também avalia a instituição globalmente, não por área. Fortemente "
            "influenciado por presença geográfica e visibilidade de marca.",
            "Mais relevante para cursos profissionalizantes (Direito, Medicina, "
            "Administração) do que para pesquisa de ponta.",
        ],
    },
    "CpP": {
        "title": "Citações por Artigo (CpP)",
        "what": (
            "Impacto médio das publicações da instituição na área, "
            "normalizado por campo e ano."
        ),
        "notes": [
            "Padrões de citação variam enormemente entre disciplinas — humanidades "
            "e ciências sociais são estruturalmente desfavorecidas.",
            "Normalização por campo é parcial; sub-áreas dentro de uma grande área "
            "podem ter padrões muito distintos.",
        ],
    },
    "HI": {
        "title": "Índice H (HI)",
        "what": (
            "O maior número H tal que H publicações tenham sido citadas ao menos H vezes. "
            "O QS utiliza uma janela temporal limitada (não o H-index acumulado completo), "
            "mas a métrica permanece estruturalmente favorável a volumes maiores de publicação."
        ),
        "notes": [
            "Favorece instituições maiores e mais antigas. Crescimento é necessariamente "
            "lento independentemente do desempenho atual.",
            "Não distingue entre publicações recentes e antigas dentro da janela avaliada.",
        ],
    },
    "IRN": {
        "title": "Rede Internacional de Pesquisa (IRN)",
        "what": (
            "Volume e diversidade das colaborações internacionais de pesquisa da instituição."
        ),
        "notes": [
            "Mede volume, não qualidade das colaborações. Favorece instituições grandes "
            "com mais docentes publicando.",
            "Instituições menores e mais especializadas são estruturalmente desfavorecidas "
            "mesmo com colaborações de alta qualidade.",
        ],
    },
}


def indicator_popover(code: str) -> None:
    """Render a st.popover('ℹ️') block for the given indicator code.

    For unknown codes, returns immediately without rendering anything.
    The popover is a block-level element — it renders as a standalone button,
    not inline within text.
    """
    content = _INDICATOR_CONTENT.get(code)
    if not content:
        return
    with st.popover("ℹ️"):
        st.markdown(f"**{content['title']}**")
        st.markdown(f"*O que mede:* {content['what']}")
        for note in content["notes"]:
            st.markdown(f"- {note}")


def indicator_help_text(code: str) -> str:
    """Return annotation content as a plain string for use in help= parameters.

    Used for st.slider(help=...) and column_config(help=...).
    Returns '' for unknown codes.
    """
    content = _INDICATOR_CONTENT.get(code)
    if not content:
        return ""
    notes = "\n".join(f"• {n}" for n in content["notes"])
    return f"{content['what']}\n\n{notes}"


# ---------------------------------------------------------------------------
# Leiden Manifesto principles
# ---------------------------------------------------------------------------

def leiden_principles() -> list[dict]:
    """Return the 10 Leiden Manifesto principles as structured data.

    Each dict has keys: number (int), title (str), description (str),
    highlighted (bool). highlighted=True for principles 1, 6, 8, 9.
    """
    return [
        {
            "number": 1,
            "title": (
                "Avaliação quantitativa deve apoiar — não substituir — "
                "o julgamento qualitativo de especialistas"
            ),
            "description": (
                "Indicadores quantitativos são ferramentas de apoio, não substitutos "
                "para a avaliação por pares. O contexto e o julgamento especializado "
                "são insubstituíveis."
            ),
            "highlighted": True,
        },
        {
            "number": 2,
            "title": (
                "Meça o desempenho em relação às missões de pesquisa "
                "da instituição, grupo ou pesquisador"
            ),
            "description": (
                "Indicadores devem refletir os objetivos declarados de quem está sendo "
                "avaliado. Missões diversas exigem medidas diversas."
            ),
            "highlighted": False,
        },
        {
            "number": 3,
            "title": "Proteja a excelência em pesquisa localmente relevante",
            "description": (
                "Rankings globais tendem a valorizar pesquisa de alcance internacional, "
                "potencialmente subvalorizando contribuições regionais e locais de "
                "grande relevância."
            ),
            "highlighted": False,
        },
        {
            "number": 4,
            "title": (
                "Mantenha a coleta e os processos analíticos de dados "
                "abertos, transparentes e simples"
            ),
            "description": (
                "Os dados e métodos usados para avaliar a pesquisa devem ser "
                "transparentes e verificáveis por todos."
            ),
            "highlighted": False,
        },
        {
            "number": 5,
            "title": "Permita que os avaliados verifiquem dados e análises",
            "description": (
                "As instituições e pesquisadores avaliados devem ter acesso aos dados "
                "sobre si mesmos e a possibilidade de contestar imprecisões."
            ),
            "highlighted": False,
        },
        {
            "number": 6,
            "title": (
                "Considere a variação por campo nas práticas "
                "de publicação e citação"
            ),
            "description": (
                "Padrões de publicação e citação variam enormemente entre disciplinas. "
                "Comparações entre campos sem normalização adequada são "
                "metodologicamente problemáticas."
            ),
            "highlighted": True,
        },
        {
            "number": 7,
            "title": (
                "Base a avaliação de pesquisadores individuais "
                "em portfólios qualitativos"
            ),
            "description": (
                "Avaliações individuais de pesquisadores devem ir além de métricas "
                "de publicação e incluir análise qualitativa do impacto e relevância "
                "da pesquisa."
            ),
            "highlighted": False,
        },
        {
            "number": 8,
            "title": "Evite concretude deslocada e falsa precisão",
            "description": (
                "Ranks e escores transmitem uma precisão que os dados subjacentes "
                "não sustentam. Diferenças de poucos pontos ou posições raramente "
                "são estatisticamente significativas."
            ),
            "highlighted": True,
        },
        {
            "number": 9,
            "title": (
                "Reconheça os efeitos sistêmicos dos indicadores "
                "no comportamento institucional"
            ),
            "description": (
                "Indicadores mudam o que se mede. Quando rankings se tornam objetivos, "
                "as instituições adaptam comportamentos para maximizar escores, "
                "não necessariamente qualidade."
            ),
            "highlighted": True,
        },
        {
            "number": 10,
            "title": "Examine e atualize indicadores regularmente",
            "description": (
                "Indicadores devem ser revistos periodicamente para garantir que "
                "continuam servindo ao propósito original e não criaram incentivos "
                "perversos."
            ),
            "highlighted": False,
        },
    ]


# ---------------------------------------------------------------------------
# Recommended readings
# ---------------------------------------------------------------------------

def recommended_readings() -> list[dict]:
    """Return recommended readings as a list of dicts.

    Each dict has keys: title (str), authors (str), year (int),
    url (str | None), doi (str | None).
    """
    return [
        {
            "title": (
                "Repensar a Universidade I: desempenho acadêmico "
                "e comparações internacionais"
            ),
            "authors": "Marcovitch, J. et al.",
            "year": 2018,
            "doi": "10.11606/9788571661868",
            "url": "https://www.livrosabertos.abcd.usp.br/portaldelivrosUSP/catalog/book/224",
        },
        {
            "title": "Repensar a Universidade II: impactos para a sociedade",
            "authors": "Marcovitch, J. et al.",
            "year": 2019,
            "doi": "10.11606/9788571661967",
            "url": "https://www.livrosabertos.abcd.usp.br/portaldelivrosUSP/catalog/book/411",
        },
        {
            "title": "Leiden Manifesto for Research Metrics",
            "authors": (
                "Hicks, D., Wouters, P., Waltman, L., De Rijcke, S. & Rafols, I."
            ),
            "year": 2015,
            "doi": "10.1038/520429a",
            "url": "https://doi.org/10.1038/520429a",
        },
        {
            "title": (
                "Ranking universities: A magnified mirror of higher education"
            ),
            "authors": "Marginson, S.",
            "year": 2014,
            "doi": None,
            "url": None,
        },
        {
            "title": "Global Rankings and the Geopolitics of Higher Education",
            "authors": "Hazelkorn, E.",
            "year": 2015,
            "doi": None,
            "url": None,
        },
    ]
