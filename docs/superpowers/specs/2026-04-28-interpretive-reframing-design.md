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

A new first tab — **"📖 Como Interpretar"** — is added before all existing tabs. It serves as the interpretive frame that users encounter before touching any data. It is structured as a readable, scrollable briefing in four blocks:

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
A dedicated block summarising the [Leiden Manifesto for Research Metrics](https://doi.org/10.1038/520429a) (Hicks, Wouters, Waltman, De Rijcke & Rafols, *Nature*, 2015). Brief summary of all 10 principles, with the following called out as directly applicable to ranking interpretation:

- **Princípio 1:** Avaliação quantitativa deve apoiar — não substituir — o julgamento qualitativo de especialistas
- **Princípio 6:** Considere a variação por campo nas práticas de publicação e citação
- **Princípio 8:** Evite concretude deslocada e falsa precisão (ranks e escores transmitem uma precisão que os dados não sustentam)
- **Princípio 9:** Reconheça os efeitos sistêmicos dos indicadores no comportamento institucional

Link to full manifesto: https://doi.org/10.1038/520429a

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
- *O que mede:* O maior número H tal que H publicações tenham sido citadas ao menos H vezes — uma medida de impacto cumulativo.
- Cumulativo por natureza: favorece instituições maiores e mais antigas. Crescimento é necessariamente lento independentemente do desempenho atual.
- Não distingue entre publicações recentes e antigas.

**Rede Internacional de Pesquisa (IRN)**
- *O que mede:* Volume e diversidade das colaborações internacionais de pesquisa da instituição.
- Mede volume, não qualidade das colaborações. Favorece instituições grandes com mais docentes publicando.
- Instituições menores e mais especializadas são estruturalmente desfavorecidas mesmo com colaborações de alta qualidade.

---

## 4. Language Reframing Across Existing Tabs

### Tab 1 — Decomposição do Escore
- Subtitle: "Entenda como o escore é construído a partir dos cinco indicadores"
- Insight string changes from "X's score is driven by Y" → "X% do escore de [universidade] depende de indicadores de reputação institucional"
- Chart title: "Composição do Escore" (not "Decomposição" which implies diagnosis)

### Tab 2 — Perfil dos Indicadores *(renamed from "Análise de Lacunas")*
- Tab name: "🎯 Perfil dos Indicadores"
- Subheader: "Compare o perfil de indicadores entre as universidades paulistas"
- Peer average label: "Média das pares SP" stays, but context caption changes to "Diferenças de perfil refletem escolhas institucionais, contextos e históricos distintos — não necessariamente lacunas a corrigir."
- Opportunity table renamed: "Diferenças de perfil" (not "oportunidades de melhoria")
- Column headers: "Diferença" (not "Lacuna"), remove "Impacto Ponderado" or rename to "Peso no escore"

### Tab 3 — Análise Bibliométrica
- Minimal change — already descriptive. Add ℹ️ popovers to metric column headers.

### Tab 4 — Explorar os Pesos *(renamed from "Simulador")*
- Tab name: "🎛️ Explorar os Pesos"
- Subheader: "Explore como os pesos de cada indicador determinam o escore final"
- Intro text: "Ajuste os valores dos indicadores para entender como o modelo de ponderação do QS funciona na prática. Este não é um plano de ação — é uma lente metodológica."
- Result metrics: "Escore Atual" / "Escore Hipotético" (not "Simulado")
- Rank output: "Posição equivalente" with caption "posição estimada assumindo que as demais instituições permanecem constantes"

### Tab 5 — Contexto Internacional *(renamed from "Benchmarking com Pares")*
- Tab name: "🏛️ Contexto Internacional"
- Caption: "Compare o perfil das universidades paulistas com grupos institucionais internacionais. Diferenças de escore refletem contextos históricos, de financiamento e de missão distintos."

---

## 5. New Source File: `src/interpretive.py`

New module containing:
- `indicator_popover(code)` — returns popover annotation content for each indicator code
- `leiden_principles()` — returns the 10 Leiden principles as structured data for rendering
- `recommended_readings()` — returns list of reading dicts (title, authors, year, doi, url)

This isolates all interpretive content from rendering logic, making it easy to update annotations without touching tab files.

---

## 6. Files Changed

| File | Change |
|---|---|
| `app.py` | Add "Como Interpretar" as first tab |
| `src/interpretive.py` | New file — all annotation and reading content |
| `tabs/tab0_interpretation.py` | New file — "Como Interpretar" tab renderer |
| `tabs/tab1_decomposition.py` | Language reframing + ℹ️ popovers |
| `tabs/tab2_gap_analysis.py` | Rename + reframe + ℹ️ popovers |
| `tabs/tab3_deep_dive.py` | ℹ️ popovers on metric headers |
| `tabs/tab4_simulator.py` | Rename + reframe intro text |
| `tabs/tab5_benchmarking.py` | Rename + reframe caption |

---

## 7. Out of Scope

- Sidebar contextual panel (Option C) — deferred to future dashboard version
- Changes to underlying data, scoring logic, or peer group definitions
- New data sources
