# Design Spec: Interpretive Reframing of the QS Subject Rankings Dashboard
**Date:** 2026-04-28
**Status:** Approved for implementation

---

## 1. Purpose and Framing Shift

The dashboard's primary purpose is reframed from **institutional improvement tool** to **instrument of informed interpretation**. The target audiences are:

- **University leaders and rectors** — who need to understand what the ranking actually measures (and doesn't) before making strategic decisions based on it
- **Researchers and faculty** — who want to understand why their institution scores the way it does, without being directed toward "improvement"

The redesign does **not** remove analytical depth. It reframes the narrative voice throughout: from prescriptive ("here is your gap, here is what to fix") to interpretive ("here is what this score reflects, and here is what it does not capture"). Inline annotation boxes surface methodological caveats where users encounter the data.

---

## 2. Structural Change: New "Como Interpretar" Tab

A new first tab — **"📖 Como Interpretar"** — is added before all existing tabs. It serves as the interpretive frame that users encounter before touching any data. It is structured as a readable, scrollable briefing in five blocks:

### Block 1 — O que o QS Subject Rankings mede
Plain-language summary:
- Ranks universities by subject area, not overall institutional performance
- Covers ~55 subjects across 5 grandes áreas
- Scores are weighted composites of 5 indicators; weights vary by subject
- Positions within banded ranges (e.g. 251–300) do not reflect meaningful score differences between institutions in that band

### Block 2 — Os cinco indicadores
One `st.expander` per indicator. Each contains:
- **O que mede:** one-sentence plain description
- **Como é coletado:** data source and method
- **Peso típico:** weight range across subjects
- **Notas de interpretação:** 2–3 bullets in a critically engaged, practically grounded voice (see Section 4)

Special emphasis across AR and ER:
> *"Os surveys de reputação avaliam a instituição como um todo — não a área específica. Um pesquisador que nomeia uma universidade em Ciências da Computação está avaliando sua impressão geral da instituição, não o departamento de computação especificamente. Isso favorece estruturalmente universidades maiores e mais antigas, independentemente da qualidade na área avaliada."*

Combined weight of AR + ER explicitly stated: ranges from **50% (Engenharia) a 70% (Artes & Humanidades)** — making reputation the dominant driver of score in most subjects.

### Block 3 — Princípios de interpretação responsável
Numbered list of 5 principles, each with a critical note:

1. **Rankings capturam reputação tanto quanto qualidade** — AR e ER respondem por 50–70% do escore. Reputação é acumulativa, lenta a mudar, e não reflete necessariamente desempenho atual.
2. **Posições em faixas não refletem diferenças reais** — Uma universidade na posição 251 e outra na posição 300 podem ter escores praticamente idênticos. Tratar faixas como posições ordinais precisas é metodologicamente incorreto.
3. **Comparações entre grandes áreas não são válidas** — Os pesos dos indicadores variam por área; escores não são comparáveis entre grandes áreas.
4. **Melhorias de escore nem sempre refletem mudanças reais** — Variações pequenas podem resultar de mudanças metodológicas, amostragem diferente nos surveys, ou flutuações estatísticas.
5. **O que o ranking não mede é tão importante quanto o que mede** — Impacto social, extensão, ensino de graduação, relevância regional, e pesquisa em língua portuguesa não aparecem no escore.

### Block 4 — O Manifesto de Leiden
A dedicated block summarising the [Leiden Manifesto for Research Metrics](https://doi.org/10.1038/520429a) (Hicks, Wouters, Waltman, De Rijcke & Rafols, *Nature*, 2015). Render all 10 principles from `leiden_principles()` as a numbered list. Principles with `highlighted=True` are rendered in a `st.info()` callout box to visually distinguish them as directly applicable to ranking interpretation. Non-highlighted principles render as plain list items in a `st.expander("Todos os 10 princípios")`.

The four highlighted principles and their framing:

- **Princípio 1:** Avaliação quantitativa deve apoiar — não substituir — o julgamento qualitativo de especialistas
- **Princípio 6:** Considere a variação por campo nas práticas de publicação e citação
- **Princípio 8:** Evite concretude deslocada e falsa precisão (ranks e escores transmitem uma precisão que os dados não sustentam)
- **Princípio 9:** Reconheça os efeitos sistêmicos dos indicadores no comportamento institucional

Link to full manifesto rendered as `st.link_button`: https://doi.org/10.1038/520429a

### Block 5 — Leituras recomendadas
`st.link_button` entries:

1. **Repensar a Universidade I: desempenho acadêmico e comparações internacionais**
   Marcovitch, J. et al. (2018). Universidade de São Paulo.
   DOI: 10.11606/9788571661868
   https://www.livrosabertos.abcd.usp.br/portaldelivrosUSP/catalog/book/224

2. **Repensar a Universidade II: impactos para a sociedade**
   Marcovitch, J. et al. (2019). Universidade de São Paulo.
   DOI: 10.11606/9788571661967
   https://www.livrosabertos.abcd.usp.br/portaldelivrosUSP/catalog/book/411

3. **Leiden Manifesto for Research Metrics**
   Hicks, D., Wouters, P., Waltman, L., De Rijcke, S. & Rafols, I. (2015). *Nature*, 520, 429–431.
   https://doi.org/10.1038/520429a

4. **Ranking universities: A magnified mirror of higher education**
   Marginson, S. (2014). *Perspectives: Policy and Practice in Higher Education*.

5. **Global Rankings and the Geopolitics of Higher Education**
   Hazelkorn, E. (2015). Routledge.

---

## 3. Inline Annotation Popovers (ℹ️)

Every indicator label across all tabs — chart legends, table column headers, slider labels in the simulator — gets a small ℹ️ icon rendered via `st.popover()`.

### Implementation approach
A shared helper function `indicator_popover(indicator_code)` in `src/interpretive.py` returns the popover content for each indicator. Called wherever indicator labels appear.

### Popover content

**Reputação Acadêmica (AR)**
- *O que mede:* Percepção de excelência acadêmica por pesquisadores de todo o mundo, via survey anual com ~170.000 respondentes.
- O survey pergunta sobre a instituição como um todo — não sobre a área específica sendo ranqueada. Isso favorece instituições com alta visibilidade global.
- Reputação é acumulativa e lenta a mudar; reflete trajetória histórica mais do que desempenho recente.
- Em muitos sujeitos, AR responde sozinha por 40–50% do escore total.

**Reputação com Empregadores (ER)**
- *O que mede:* Preferências de recrutamento de ~100.000 empregadores globais, via survey anual.
- Também avalia a instituição globalmente, não por área. Fortemente influenciado por presença geográfica e visibilidade de marca.
- Mais relevante para cursos profissionalizantes (Direito, Medicina, Administração) do que para pesquisa de ponta.

**Citações por Artigo (CpP)**
- *O que mede:* Impacto médio das publicações da instituição na área, normalizado por campo e ano.
- Padrões de citação variam enormemente entre disciplinas — humanidades e ciências sociais são estruturalmente desfavorecidas.
- Normalização por campo é parcial; sub-áreas dentro de uma grande área podem ter padrões muito distintos.

**Índice H (HI)**
- *O que mede:* O maior número H tal que H publicações tenham sido citadas ao menos H vezes — uma medida de impacto cumulativo. O QS utiliza uma janela temporal limitada (não o H-index acumulado completo), mas a métrica permanece estruturalmente favorável a volumes maiores de publicação.
- Cumulativo por natureza: favorece instituições maiores e mais antigas. Crescimento é necessariamente lento independentemente do desempenho atual.
- Não distingue entre publicações recentes e antigas dentro da janela avaliada.

**Rede Internacional de Pesquisa (IRN)**
- *O que mede:* Volume e diversidade das colaborações internacionais de pesquisa da instituição.
- Mede volume, não qualidade das colaborações. Favorece instituições grandes com mais docentes publicando.
- Instituições menores e mais especializadas são estruturalmente desfavorecidas mesmo com colaborações de alta qualidade.

---

## 4. Language Reframing Across Existing Tabs

### Tab 1 — Decomposição do Escore
- Subtitle: "Entenda como o escore é construído a partir dos cinco indicadores"
- Insight string (`decomposition_insight()` in `src/insights.py`): reframe from "é impulsionado principalmente por… O contribuinte ponderado mais fraco é…" → neutral description of composition, e.g. "X% do escore de [universidade] em [subject] é determinado por indicadores de reputação institucional (AR + ER)."
- Chart `update_layout` title: rename from "Decomposição do Escore — …" → "Composição do Escore — …" (not "Decomposição" which implies diagnosis)

### Tab 2 — Perfil dos Indicadores *(renamed from "Análise de Lacunas")*
- Tab name: "🎯 Perfil dos Indicadores"
- Subheader: "Compare o perfil de indicadores entre as universidades paulistas"
- Peer average label: "Média das pares SP" stays, but context caption changes to "Diferenças de perfil refletem escolhas institucionais, contextos e históricos distintos — não necessariamente lacunas a corrigir."
- Radar chart `update_layout` title: rename "Análise de Lacunas — …" → "Perfil dos Indicadores — …"
- Section header above the profile table: add `st.markdown("#### Diferenças de perfil")` (this replaces any existing "oportunidades de melhoria" heading)
- Dataframe column renames: "Lacuna" → "Diferença", "Impacto Ponderado" → "Peso no escore"

### Tab 3 — Análise Bibliométrica
- Minimal change — already descriptive. Add ℹ️ popovers to metric column headers.

### Tab 4 — Explorar os Pesos *(renamed from "Simulador")*
- Tab name: "🎛️ Explorar os Pesos"
- Subheader: rename "Simulador de Escore — {subject}" → "Explorar os Pesos — {subject}"
- Subheader below that: "Explore como os pesos de cada indicador determinam o escore final"
- Intro text: "Ajuste os valores dos indicadores para entender como o modelo de ponderação do QS funciona na prática. Este não é um plano de ação — é uma lente metodológica."
- Metric labels: `st.metric("Escore Atual", ...)` stays as-is; `st.metric("Escore Simulado", ...)` → `st.metric("Escore Hipotético", ...)`. Internal variable names (`simulated_total`, `simulate_score_change`) and `src/simulator.py` are **not** renamed.
- Delta table column "Impacto Ponderado" → rename to "Peso no escore" (same rename as Tab 2)
- Rank metric: `st.metric("Posição Estimada", estimated_rank_str)` → `st.metric("Posição equivalente", estimated_rank_str)` with a `st.caption("posição estimada assumindo que as demais instituições permanecem constantes")` rendered immediately below it (replacing the existing bottom-of-tab note about rank estimation)

### Tab 5 — Contexto Internacional *(renamed from "Benchmarking com Pares")*
- Tab name: "🏛️ Contexto Internacional"
- Caption: "Compare o perfil das universidades paulistas com grupos institucionais internacionais. Diferenças de escore refletem contextos históricos, de financiamento e de missão distintos."

---

## 5. New Source File: `src/interpretive.py`

New module containing:
- `indicator_popover(code)` — renders a `st.popover("ℹ️")` block for the given indicator. If `code` is not one of the five known indicators (`AR`, `ER`, `CpP`, `HI`, `IRN`), returns immediately without rendering (no exception).
- `indicator_help_text(code) -> str` — returns the same annotation content as a plain string (no Streamlit calls). Used for `help=` parameters on `st.slider()` and `column_config`. Returns `""` for unknown codes.
- `leiden_principles() -> list[dict]` — returns the 10 Leiden principles as a list of dicts with keys: `number` (int 1–10), `title` (str), `description` (str), `highlighted` (bool — True for principles 1, 6, 8, 9 which are called out in Block 4).
- `recommended_readings() -> list[dict]` — returns list of reading dicts with keys: `title` (str), `authors` (str), `year` (int), `url` (str | None), `doi` (str | None). Both `url` and `doi` are optional (None when absent). The renderer renders a `st.link_button` only when `url` is not None; skips the DOI display when `doi` is None. Entries with no URL receive plain text citation only.

This isolates all interpretive content from rendering logic, making it easy to update annotations without touching tab files.

### Rendering contract for `indicator_popover(code)`

The function **renders the popover widget itself** using `st.popover()` as a context manager — it does not return a string. Call sites simply call `indicator_popover(code)` wherever the ℹ️ icon should appear. If `code` is unknown the function returns immediately without rendering anything, so call sites never need to guard against empty output.

`st.popover()` is a block-level element in Streamlit; it renders as a standalone "ℹ️" button on its own line, not inline within a label string. This is acceptable and consistent with Streamlit's layout model.

**Exception — sliders:** `st.slider()` accepts a `help=` parameter that renders a native inline tooltip. For slider labels in Tab 4, use `help=` instead of `indicator_popover()`. The content to pass is returned by `indicator_help_text(code) -> str`, a second function in `src/interpretive.py` that returns the same annotation content as a plain string (no Streamlit calls). Call sites in Tab 4: `st.slider(..., help=indicator_help_text(ind))`.

**Exception — dataframe columns:** `st.dataframe()` column headers accept `help=` via `st.column_config`. Where indicator columns appear in a dataframe (Tab 2, Tab 5), use `column_config` with `help=indicator_help_text(code)`.

Example for running-text / section label contexts:
```python
st.markdown(f"**{label}**")
indicator_popover("AR")   # renders block-level popover button below label
```

### Dependency note
`st.popover()` requires Streamlit ≥ 1.31.0. `st.link_button()` requires Streamlit ≥ 1.26.0. The `requirements.txt` must pin `streamlit>=1.31.0` (currently `>=1.30.0` — needs updating).

---

## 6. Files Changed

| File | Change |
|---|---|
| `app.py` | Unpack 6 tabs (`tab0`–`tab5`); add "Como Interpretar" as first tab; update tab labels to reframed names |
| `requirements.txt` | Update `streamlit>=1.30.0` → `streamlit>=1.31.0` |
| `src/interpretive.py` | New file — `indicator_popover(code)`, `indicator_help_text(code)`, `leiden_principles()`, `recommended_readings()` |
| `src/insights.py` | Reframe all three insight functions: `decomposition_insight()` (replace "impulsionado" / "mais fraco" with neutral composition framing), `gap_analysis_insight()` (replace "oportunidade de melhoria" with "diferença de perfil"), `benchmarking_insight()` (replace "foco prioritário de melhoria" with neutral comparative language) |
| `tabs/tab0_interpretation.py` | New file — "Como Interpretar" tab renderer |
| `tabs/tab1_decomposition.py` | Language reframing + chart title "Composição do Escore" + ℹ️ popovers |
| `tabs/tab2_gap_analysis.py` | Rename + reframe + chart title "Perfil dos Indicadores" + column renames + column_config help= |
| `tabs/tab3_deep_dive.py` | column_config help= on metric headers |
| `tabs/tab4_simulator.py` | Rename + reframe intro text; rename "Escore Simulado" → "Escore Hipotético"; rename "Impacto Ponderado" → "Peso no escore"; help= on sliders |
| `tabs/tab5_benchmarking.py` | Rename + reframe caption; column_config help= on indicator columns |

### Out-of-scope clarification
Unit tests for `src/interpretive.py` (e.g., `tests/test_interpretive.py`) are **out of scope** for this implementation cycle. Content correctness is validated through manual review of the rendered tab.

---

## 7. Out of Scope

- Sidebar contextual panel (Option C) — deferred to future dashboard version
- Changes to underlying data, scoring logic, or peer group definitions
- New data sources
