# Interpretive Reframing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe the QS Subject Rankings Dashboard from a prescriptive improvement tool to an instrument of informed interpretation, adding a new "Como Interpretar" tab, inline indicator annotations, and neutral language throughout.

**Architecture:** New `src/interpretive.py` module holds all annotation content (indicator popovers, Leiden principles, recommended readings) isolated from rendering logic. A new `tabs/tab0_interpretation.py` renders the five-block interpretive tab. Existing tabs receive language edits and `help=` / `st.popover()` calls that delegate content to `interpretive.py`. `src/insights.py` insight strings are reframed to neutral descriptive language.

**Tech Stack:** Streamlit ≥1.31.0 (required for `st.popover()` and `st.link_button()`), Plotly, pandas; no new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-28-interpretive-reframing-design.md`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Modify | Bump streamlit pin to ≥1.31.0 |
| `src/interpretive.py` | **Create** | All annotation content: indicator popovers, help text, Leiden principles, readings |
| `src/insights.py` | Modify | Reframe all three insight functions to neutral language |
| `tabs/tab0_interpretation.py` | **Create** | "Como Interpretar" tab renderer (5 blocks) |
| `app.py` | Modify | Unpack 6 tabs, update tab labels |
| `tabs/tab1_decomposition.py` | Modify | Chart title + popover after insight string |
| `tabs/tab2_gap_analysis.py` | Modify | Tab rename, chart title, section header, column renames, column_config help= |
| `tabs/tab3_deep_dive.py` | Modify | column_config help= on SciVal metric columns |
| `tabs/tab4_simulator.py` | Modify | Rename, reframe text, metric labels, slider help=, rank caption placement |
| `tabs/tab5_benchmarking.py` | Modify | Rename subheader, reframe caption, column_config help= on indicator columns |

---

## Task 1: Bump Streamlit version pin

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Edit requirements.txt**

Change line 1 from:
```
streamlit>=1.30.0
```
to:
```
streamlit>=1.31.0
```

- [ ] **Step 2: Verify Python can import streamlit at the required version**

```bash
python -c "import streamlit; print(streamlit.__version__)"
```

Expected: version string ≥ 1.31.0

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: bump streamlit requirement to >=1.31.0 for st.popover support"
```

---

## Task 2: Create `src/interpretive.py`

All interpretive content lives here. No Streamlit calls except in `indicator_popover()`. Everything else returns plain Python data structures or strings.

**Files:**
- Create: `src/interpretive.py`

- [ ] **Step 1: Create the file**

```python
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
```

- [ ] **Step 2: Verify module imports cleanly**

```bash
cd "/Users/administrador/Downloads/QS Subject 2026"
python -c "
from src.interpretive import (
    indicator_popover, indicator_help_text,
    leiden_principles, recommended_readings,
)
# Quick data checks
assert indicator_help_text('AR') != ''
assert indicator_help_text('UNKNOWN') == ''
principles = leiden_principles()
assert len(principles) == 10
highlighted = [p for p in principles if p['highlighted']]
assert [p['number'] for p in highlighted] == [1, 6, 8, 9]
readings = recommended_readings()
assert len(readings) == 5
assert readings[3]['url'] is None   # Marginson has no URL
print('src/interpretive.py OK')
"
```

Expected: `src/interpretive.py OK`

- [ ] **Step 3: Commit**

```bash
git add src/interpretive.py
git commit -m "feat: add src/interpretive.py — indicator annotations, Leiden principles, readings"
```

---

## Task 3: Reframe `src/insights.py`

Replace prescriptive language ("melhoria", "impulsionado", "mais fraco") with neutral descriptive language.

**Files:**
- Modify: `src/insights.py`

- [ ] **Step 1: Replace `decomposition_insight()`**

Replace the entire function body (lines 6–27) with:

```python
def decomposition_insight(contributions: dict, subject: str) -> str:
    """Gera um insight de composição para a aba Decomposição do Escore."""
    if not contributions:
        return f"Sem dados disponíveis para {subject}."

    totals = {uni: sum(c.values()) for uni, c in contributions.items()}
    top_uni = max(totals, key=totals.get)
    top_total = totals[top_uni]
    top_contribs = contributions[top_uni]

    reputation_total = top_contribs.get("AR", 0) + top_contribs.get("ER", 0)
    reputation_pct = round(reputation_total / top_total * 100) if top_total > 0 else 0

    return (
        f"Em {subject}, {reputation_pct}% do escore ponderado de {top_uni} "
        f"({top_total:.1f} pts) é determinado por indicadores de reputação "
        f"institucional (AR + ER)."
    )
```

- [ ] **Step 2: Replace `gap_analysis_insight()`**

Replace the entire function body (lines 30–46) with:

```python
def gap_analysis_insight(
    focus_uni: str, subject: str, opportunities: list[dict]
) -> str:
    """Gera um insight de perfil para a aba Perfil dos Indicadores."""
    if not opportunities:
        return (
            f"{focus_uni} está acima ou igual à média das pares "
            f"em todos os indicadores em {subject}."
        )

    top = opportunities[0]
    indicator_name = INDICATOR_NAMES.get(top["indicator"], top["indicator"])
    return (
        f"Em {subject}, {focus_uni} apresenta a maior diferença de perfil "
        f"em {indicator_name}: {top['gap_points']:.1f} pts ponderados "
        f"abaixo da média das pares paulistas."
    )
```

- [ ] **Step 3: Replace `benchmarking_insight()`**

Replace lines 72–77 (the return statement) with:

```python
    return (
        f"{count} de {total_peers} grupos de pares apresentam diferença "
        f"positiva em relação a {focus_uni} em {indicator_name} "
        f"na área de {faculty_area}."
    )
```

And the no-peers-above branch (lines 62–66):

```python
    if not indicator_counts:
        return (
            f"{focus_uni} está acima ou igual a todas as pares "
            f"em todos os indicadores em {faculty_area}."
        )
```

- [ ] **Step 4: Verify with quick assertions**

```bash
cd "/Users/administrador/Downloads/QS Subject 2026"
python -c "
from src.insights import decomposition_insight, gap_analysis_insight, benchmarking_insight

# decomposition_insight
contribs = {'USP': {'AR': 30.0, 'ER': 10.0, 'CpP': 20.0, 'HI': 15.0, 'IRN': 5.0}}
result = decomposition_insight(contribs, 'Computer Science')
assert 'reputação' in result.lower(), f'Missing reputação: {result}'
assert 'USP' in result
print('decomposition_insight OK:', result)

# gap_analysis_insight — no gaps
result = gap_analysis_insight('USP', 'CS', [])
assert 'melhoria' not in result.lower(), f'Prescriptive language found: {result}'
print('gap_analysis_insight (no gaps) OK:', result)

# gap_analysis_insight — with gaps
opps = [{'indicator': 'CpP', 'gap_points': 5.2}]
result = gap_analysis_insight('USP', 'CS', opps)
assert 'diferença de perfil' in result, f'Wrong framing: {result}'
print('gap_analysis_insight (with gaps) OK:', result)

# benchmarking_insight
result = benchmarking_insight('USP', 'Engenharia', {'MIT': {'AR': 10}, 'Cambridge': {'AR': 5}})
assert 'melhoria' not in result.lower(), f'Prescriptive language found: {result}'
print('benchmarking_insight OK:', result)
"
```

Expected: four `OK:` lines with no assertion errors.

- [ ] **Step 5: Commit**

```bash
git add src/insights.py
git commit -m "refactor: reframe insights.py to neutral descriptive language"
```

---

## Task 4: Create `tabs/tab0_interpretation.py`

The new first tab. Five blocks. Imports `leiden_principles()` and `recommended_readings()` from `src.interpretive`. Does not import `indicator_popover` (the popovers belong to the data tabs, not this explanatory tab).

**Files:**
- Create: `tabs/tab0_interpretation.py`

- [ ] **Step 1: Create the file**

```python
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
```

- [ ] **Step 2: Verify the module imports cleanly (no Streamlit runtime needed)**

```bash
cd "/Users/administrador/Downloads/QS Subject 2026"
python -c "
import ast, sys
with open('tabs/tab0_interpretation.py') as f:
    ast.parse(f.read())
print('tabs/tab0_interpretation.py parses OK')
"
```

Expected: `tabs/tab0_interpretation.py parses OK`

- [ ] **Step 3: Commit**

```bash
git add tabs/tab0_interpretation.py
git commit -m "feat: add tabs/tab0_interpretation.py — Como Interpretar tab with 5 blocks"
```

---

## Task 5: Update `app.py` — 6-tab unpack + reframed labels

**Files:**
- Modify: `app.py:98–124`

- [ ] **Step 1: Replace the tabs block**

Find this block (lines 98–124):

```python
# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Decomposição do Escore",
    "🎯 Análise de Lacunas",
    "🔬 Análise Bibliométrica",
    "🎛️ Simulador",
    "🏛️ Benchmarking com Pares",
])

with tab1:
    from tabs.tab1_decomposition import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab2:
    from tabs.tab2_gap_analysis import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab3:
    from tabs.tab3_deep_dive import render
    render(scival_data, selected_universities, selected_faculty, is_broad_field)

with tab4:
    from tabs.tab4_simulator import render
    render(qs_data, scival_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab5:
    from tabs.tab5_benchmarking import render
    render(qs_data, scival_data, selected_universities, selected_faculty, selected_subject, selected_year)
```

Replace with:

```python
# --- Tabs ---
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 Como Interpretar",
    "📊 Decomposição do Escore",
    "🎯 Perfil dos Indicadores",
    "🔬 Análise Bibliométrica",
    "🎛️ Explorar os Pesos",
    "🏛️ Contexto Internacional",
])

with tab0:
    from tabs.tab0_interpretation import render
    render()

with tab1:
    from tabs.tab1_decomposition import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab2:
    from tabs.tab2_gap_analysis import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab3:
    from tabs.tab3_deep_dive import render
    render(scival_data, selected_universities, selected_faculty, is_broad_field)

with tab4:
    from tabs.tab4_simulator import render
    render(qs_data, scival_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab5:
    from tabs.tab5_benchmarking import render
    render(qs_data, scival_data, selected_universities, selected_faculty, selected_subject, selected_year)
```

- [ ] **Step 2: Verify the app parses**

```bash
cd "/Users/administrador/Downloads/QS Subject 2026"
python -c "import ast; ast.parse(open('app.py').read()); print('app.py parses OK')"
```

Expected: `app.py parses OK`

- [ ] **Step 3: Launch the app and verify the new tab appears**

```bash
streamlit run app.py
```

Open http://localhost:8501. Confirm: 6 tabs appear, first tab is "📖 Como Interpretar", and all 5 blocks render without errors. Then Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add Como Interpretar as first tab, reframe tab labels"
```

---

## Task 6: Update `tabs/tab1_decomposition.py`

Changes: add subtitle; chart title rename; add `indicator_popover()` calls for each indicator after the chart.

**Files:**
- Modify: `tabs/tab1_decomposition.py`

- [ ] **Step 1: Add import for `indicator_popover`**

At the top of the file, after the existing imports, add:

```python
from src.interpretive import indicator_popover
```

- [ ] **Step 2: Add subtitle at top of render()**

Find (first line inside `render()`, line ~35):
```python
    if selected_subject == "(nenhuma disciplina disponível)":
```

Insert before it:
```python
    st.caption("Entenda como o escore é construído a partir dos cinco indicadores")
```

- [ ] **Step 3: Rename the chart title**

Find (line ~103):
```python
        title=f"Decomposição do Escore — {selected_subject} ({selected_year})",
```

Replace with:
```python
        title=f"Composição do Escore — {selected_subject} ({selected_year})",
```

- [ ] **Step 4: Add popovers for each indicator in use after the chart**

Find this exact line (line ~110):
```python
    st.plotly_chart(fig, use_container_width=True)

    # Fórmula de pesos
```

Insert between `st.plotly_chart` and the `# Fórmula de pesos` comment:

```python
    # Anotações dos indicadores
    if indicators_in_use:
        st.markdown("**Indicadores nesta disciplina:**")
        ind_cols = st.columns(len(indicators_in_use))
        for i, ind in enumerate(indicators_in_use):
            with ind_cols[i]:
                st.markdown(f"**{INDICATOR_NAMES.get(ind, ind)}**")
                indicator_popover(ind)
```

- [ ] **Step 5: Verify the file parses**

```bash
python -c "import ast; ast.parse(open('tabs/tab1_decomposition.py').read()); print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add tabs/tab1_decomposition.py
git commit -m "refactor: tab1 — add subtitle, rename chart title, add indicator popovers"
```

---

## Task 7: Update `tabs/tab2_gap_analysis.py`

Changes: add subheader; chart title rename; add context caption; add section header "Diferenças de perfil"; rename columns "Lacuna"→"Diferença" and "Impacto Ponderado"→"Peso no escore"; add `column_config` help=.

**Files:**
- Modify: `tabs/tab2_gap_analysis.py`

- [ ] **Step 1: Add import for `indicator_help_text`**

```python
from src.interpretive import indicator_help_text
```

- [ ] **Step 2: Add subheader at top of render()**

Find (first line inside `render()`, line ~33):
```python
    if selected_subject == "(nenhuma disciplina disponível)":
```

Insert before it:
```python
    st.subheader("Perfil dos Indicadores")
    st.caption("Compare o perfil de indicadores entre as universidades paulistas")
```

- [ ] **Step 4: Rename the chart title**

Find (line ~114):
```python
        title=f"Análise de Lacunas — {focus_uni} vs. Pares Paulistas em {selected_subject}",
```

Replace with:
```python
        title=f"Perfil dos Indicadores — {focus_uni} vs. Pares Paulistas em {selected_subject}",
```

- [ ] **Step 5: Add context caption after the chart**

After `st.plotly_chart(fig, use_container_width=True)`:

```python
    st.caption(
        "Diferenças de perfil refletem escolhas institucionais, contextos e históricos "
        "distintos — não necessariamente lacunas a corrigir."
    )
```

- [ ] **Step 6: Replace the opportunities table block**

Find this block (lines ~138–146):

```python
    st.markdown(f"**{gap_analysis_insight(focus_uni, selected_subject, opportunities)}**")

    if opportunities:
        opp_df = pd.DataFrame(opportunities)[
            ["Indicador", "Seu Escore", "Média das Pares", "Lacuna", "Peso", "Impacto Ponderado"]
        ]
        st.dataframe(opp_df, use_container_width=True, hide_index=True)
    else:
        st.success(f"{focus_uni} lidera ou empata com as pares em todos os indicadores!")
```

Replace with:

```python
    st.markdown(f"**{gap_analysis_insight(focus_uni, selected_subject, opportunities)}**")

    if opportunities:
        st.markdown("#### Diferenças de perfil")
        opp_df = pd.DataFrame(opportunities).rename(columns={
            "Lacuna": "Diferença",
            "Impacto Ponderado": "Peso no escore",
        })[["Indicador", "Seu Escore", "Média das Pares", "Diferença", "Peso", "Peso no escore"]]

        # Build column_config with help text for each indicator row
        # (column_config applies to column headers; indicator names are row values here,
        #  so we add help to the "Diferença" and "Peso no escore" column headers instead)
        col_cfg = {
            "Diferença": st.column_config.TextColumn(
                "Diferença",
                help="Diferença entre o escore médio das pares e o escore desta universidade neste indicador.",
            ),
            "Peso no escore": st.column_config.TextColumn(
                "Peso no escore",
                help="Diferença ponderada pelo peso do indicador no escore total desta disciplina (em pontos).",
            ),
        }
        st.dataframe(opp_df, use_container_width=True, hide_index=True, column_config=col_cfg)
    else:
        st.success(f"{focus_uni} está acima ou igual à média das pares em todos os indicadores!")
```

- [ ] **Step 7: Verify the file parses**

```bash
python -c "import ast; ast.parse(open('tabs/tab2_gap_analysis.py').read()); print('OK')"
```

- [ ] **Step 8: Commit**

```bash
git add tabs/tab2_gap_analysis.py
git commit -m "refactor: tab2 — add subheader, rename to Perfil dos Indicadores, reframe columns"
```

---

## Task 8: Update `tabs/tab3_deep_dive.py`

Changes: add `column_config` help= to the broad-field overview dataframe columns for CpP and IRN metric names.

**Files:**
- Modify: `tabs/tab3_deep_dive.py`

- [ ] **Step 1: Add import for `indicator_help_text`**

```python
from src.interpretive import indicator_help_text
```

- [ ] **Step 2: Add column_config to the broad-field dataframes**

Find the `_render_broad_field_overview` function. The `st.dataframe(pd.DataFrame(rows), ...)` calls at the end of the function (inside the loop, line ~156–157) should be updated to add column_config for CpP and IRN related columns:

Replace:
```python
        if rows:
            st.markdown(f"**{label}**")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
```

With:
```python
        if rows:
            st.markdown(f"**{label}**")
            # Add help text to the score-index columns
            _col_cfg = {}
            if metric_type == "citations_per_faculty":
                _col_cfg["Citações Normalizadas"] = st.column_config.NumberColumn(
                    "Citações Normalizadas",
                    help=indicator_help_text("CpP"),
                )
            elif metric_type == "irn":
                _col_cfg["Índice IRN"] = st.column_config.NumberColumn(
                    "Índice IRN",
                    help=indicator_help_text("IRN"),
                )
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
                column_config=_col_cfg if _col_cfg else None,
            )
```

- [ ] **Step 3: Verify the file parses**

```bash
python -c "import ast; ast.parse(open('tabs/tab3_deep_dive.py').read()); print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add tabs/tab3_deep_dive.py
git commit -m "refactor: tab3 — add column_config help= for CpP/IRN metric columns"
```

---

## Task 9: Update `tabs/tab4_simulator.py`

Changes: rename subheader; add intro text; rename "Escore Simulado"→"Escore Hipotético"; rename "Impacto Ponderado"→"Peso no escore"; add `help=` to sliders; move rank caption inside col4; trim bottom caption.

**Files:**
- Modify: `tabs/tab4_simulator.py`

- [ ] **Step 1: Add import for `indicator_help_text`**

After the existing imports, add:
```python
from src.interpretive import indicator_help_text
```

- [ ] **Step 2: Rename the subheader and add intro text**

Find (line ~130):
```python
    st.subheader(f"Simulador de Escore — {selected_subject}")
```

Replace with:
```python
    st.subheader(f"Explorar os Pesos — {selected_subject}")
    st.markdown("Explore como os pesos de cada indicador determinam o escore final")
```

- [ ] **Step 3: Replace the slider intro text and add `help=` to sliders**

Find (line ~177):
```python
    st.markdown("---")
    st.markdown("**Ajuste os escores dos indicadores para simular mudanças:**")

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
```

Replace with:
```python
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
```

- [ ] **Step 4: Rename metrics and move rank caption inside col4**

Find (lines ~199–208):
```python
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Escore Atual", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Escore Simulado", f"{result['simulated_total']:.1f}",
                   delta=f"{result['delta']:+.1f}")
    with col3:
        st.metric("Posição Atual", rank_str)
    with col4:
        st.metric("Posição Estimada", estimated_rank_str)
```

Replace with:
```python
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
```

- [ ] **Step 5: Rename "Impacto Ponderado" column in the delta table**

Find (line ~224):
```python
            "Impacto Ponderado": f"{delta:+.1f} pts",
```

Replace with:
```python
            "Peso no escore": f"{delta:+.1f} pts",
```

And find the dataframe display (line ~233):
```python
    st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)
```

This should now work automatically since the column was renamed in the dict above.

- [ ] **Step 6: Update the bottom-of-tab caption (trim sentence (a))**

Find (lines ~266–271):
```python
    st.caption(
        "Nota: A estimativa de posição é aproximada — assume que os escores das demais "
        "universidades permanecem constantes. As estimativas bibliométricas são aproximações "
        "lineares com base nos dados SciVal atuais. Reputação Acadêmica e com Empregadores "
        "são baseadas em pesquisas e mais difíceis de influenciar diretamente."
    )
```

Replace with (sentences (b) and (c) only — sentence (a) moved to col4 above):
```python
    st.caption(
        "Estimativas bibliométricas são aproximações lineares com base nos dados SciVal atuais. "
        "Reputação Acadêmica e com Empregadores são baseadas em surveys e refletem percepções "
        "acumuladas — mais difíceis de influenciar diretamente."
    )
```

- [ ] **Step 7: Verify the file parses**

```bash
python -c "import ast; ast.parse(open('tabs/tab4_simulator.py').read()); print('OK')"
```

- [ ] **Step 8: Commit**

```bash
git add tabs/tab4_simulator.py
git commit -m "refactor: tab4 — rename to Explorar os Pesos, reframe text, Escore Hipotético, help= on sliders"
```

---

## Task 10: Update `tabs/tab5_benchmarking.py`

Changes: rename subheader; update caption; add `column_config` help= to AR/ER/CpP/HI/IRN columns in the group table.

**Files:**
- Modify: `tabs/tab5_benchmarking.py`

- [ ] **Step 1: Add import for `indicator_help_text`**

```python
from src.interpretive import indicator_help_text
```

- [ ] **Step 2: Rename the subheader and update caption**

Find (lines ~277–284):
```python
    st.subheader("Benchmarking com Pares")

    if qs_data.empty:
        st.warning("Nenhum dado QS carregado.")
        return

    st.caption(
        f"Disciplina: **{selected_subject}** | Ano: **{selected_year}** | "
        "Universidades SP destacadas em azul."
    )
```

Replace with:
```python
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
```

- [ ] **Step 3: Add column_config to `_render_group_table()`**

Find the `_render_group_table` function (lines ~115–128):

```python
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
    st.dataframe(styled, use_container_width=True, hide_index=True)
```

Replace with:

```python
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
```

- [ ] **Step 4: Verify the file parses**

```bash
python -c "import ast; ast.parse(open('tabs/tab5_benchmarking.py').read()); print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add tabs/tab5_benchmarking.py
git commit -m "refactor: tab5 — rename to Contexto Internacional, reframe caption, indicator help="
```

---

## Task 11: End-to-end smoke test and push

- [ ] **Step 1: Run full app and verify all 6 tabs**

```bash
streamlit run app.py
```

Walk through each tab and confirm:
- **📖 Como Interpretar**: All 5 blocks render. Four `st.info()` callouts visible before the expander. `st.link_button` entries render for readings with URLs.
- **📊 Decomposição do Escore**: Chart title says "Composição do Escore". Indicator popovers render below the indicator labels. Insight string mentions "reputação institucional".
- **🎯 Perfil dos Indicadores**: Tab label updated. Radar chart title says "Perfil dos Indicadores". Profile table shows columns "Diferença" and "Peso no escore". Caption about "lacunas a corrigir" is present.
- **🔬 Análise Bibliométrica**: Hover on "Citações Normalizadas" column header shows CpP help text. Hover on "Índice IRN" column header shows IRN help text.
- **🎛️ Explorar os Pesos**: Subheader says "Explorar os Pesos". Sliders have tooltip icons. Metric reads "Escore Hipotético". col4 shows "Posição equivalente" with caption below it.
- **🏛️ Contexto Internacional**: Subheader says "Contexto Internacional". Hovering AR/ER/CpP/HI/IRN column headers shows help text.

Ctrl+C when done.

- [ ] **Step 2: Push to GitHub**

```bash
git push origin master
```

Expected: all 10 commits pushed successfully.

---

## Reference: Key file line numbers (at plan-writing time)

| File | Relevant lines |
|---|---|
| `app.py` | 98–124: tabs block |
| `tabs/tab1_decomposition.py` | 103: chart title; 110: plotly_chart call |
| `tabs/tab2_gap_analysis.py` | 114: chart title; 138–146: insight + table |
| `tabs/tab3_deep_dive.py` | 155–157: broad-field dataframe |
| `tabs/tab4_simulator.py` | 130: subheader; 177: slider intro; 199–208: metrics; 224: Impacto Ponderado; 233: dataframe; 266–271: bottom caption |
| `tabs/tab5_benchmarking.py` | 277: subheader; 283: caption; 115–128: _render_group_table |
| `src/insights.py` | 6–27: decomposition; 30–46: gap; 49–77: benchmarking |
