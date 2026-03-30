# QS Subject Rankings Dashboard — Design Spec

## Purpose

A Streamlit dashboard that compares the performance of 6 public universities in the state of Sao Paulo across QS Subject Rankings areas of knowledge, enriched with SciVal bibliometric data, to make the determinants of ranking performance clear and actionable for university leadership and institutional research analysts.

## Target Universities

- USP (Universidade de Sao Paulo)
- UNICAMP (Universidade Estadual de Campinas)
- UNESP (Universidade Estadual Paulista)
- UNIFESP (Universidade Federal de Sao Paulo)
- UFSCar (Universidade Federal de Sao Carlos)
- UFABC (Universidade Federal do ABC)

## Primary Audience

University leadership and faculty directors (clear takeaways, plain-language insights) with drill-down capability for institutional research / bibliometrics analysts.

## Data Sources & Two-Tier Architecture

The dashboard operates at two tiers due to data availability constraints:

- **Tier 1 (Subject level)**: QS Subject Rankings scores — rank, overall score, and per-indicator scores (Academic Reputation, Employer Reputation, Citations per Paper, H-Index, IRN). Available per university, per subject, per year.
- **Tier 2 (Faculty area level)**: SciVal WUR exports — raw bibliometric values (scholarly output, citations, normalized citations, h-index, IRN locations/partners) plus QS-calculated scores. Available per university, per faculty area (5 broad areas), not per individual subject.

SciVal does not provide subject-level data aligned to QS subjects. Mapping via ASJC codes was considered and rejected as too much effort for insufficient accuracy.

## QS Subject Rankings Methodology

Weights vary by subject. Five indicators are used:

| Indicator | Type | Weight Range |
|---|---|---|
| Academic Reputation (AR) | Survey | 30–90% |
| Employer Reputation (ER) | Survey | 5–50% |
| Citations per Paper (CpP) | Bibliometric | 0–30% |
| H-Index (HI) | Bibliometric | 0–30% |
| International Research Network (IRN) | Bibliometric | 0–10% |

Bibliometric weight ranges by faculty area:

| Faculty Area | AR | ER | CpP | HI | IRN | Bibliometric Total |
|---|---|---|---|---|---|---|
| Arts & Humanities | 60% | 20% | 7.5% | 7.5% | 5% | 20% |
| Engineering & Technology | 40% | 30% | 10% | 10% | 10% | 30% |
| Life Sciences & Medicine | 40% | 10% | 20% | 20% | 10% | 50% |
| Natural Sciences | 40% | 20% | 15% | 15% | 10% | 40% |
| Social Sciences & Management | 50% | 30% | 7.5% | 7.5% | 5% | 20% |

Individual subject weights are hardcoded in `weights.json` (extracted from QS methodology SVGs). Some subjects omit CpP, HI, or IRN entirely.

## Data Architecture

### Input files in `data/`

| Directory | Source | Format | Level | Contents |
|---|---|---|---|---|
| `data/qs/` | QS website (xlsx) | Excel | Per subject | Rank, overall score, per-indicator scores, per university, per year |
| `data/scival/` | Manual SciVal export (CSV) | CSV | Per faculty area | Raw bibliometric values + QS scores per university |
| `data/peers.csv` | User-defined | CSV | Per university | Manual peer institutions for benchmarking |
| `data/weights.json` | Hardcoded from QS SVGs | JSON | Per subject + per faculty area | Indicator weights |

### SciVal CSV structure (example: Citations per Faculty)

Header metadata rows followed by a table with columns: QS metrics, Scholarly Output (QS), Excluded Scholarly Output, Total Scholarly Output, Citations (QS), Excluded self-citations, Total Citations, Normalized Total Citation Count (QS), Weighting Factor (QS), Weighting Adjustment Ratio (QS). One row per faculty area. Overall score in a standalone row.

### SciVal CSV structure (example: IRN)

Header metadata rows followed by a table with columns: QS metrics, IRN Scholarly Output (QS), Locations (QS), Partners (QS), Non-Scaled IRN Index (QS), IRN Index (QS). One row per faculty area. Overall score in a standalone row.

### Weights.json structure

```json
{
  "broad": {
    "Arts and Humanities": {"AR": 60, "ER": 20, "CpP": 7.5, "HI": 7.5, "IRN": 5}
  },
  "subjects": {
    "Chemistry": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "History": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15}
  }
}
```

Subjects without a given indicator omit the key (weight is implicitly 0).

### peers.csv format

```
university,peer
Universidade de Sao Paulo,University of Barcelona
Universidade de Sao Paulo,National Autonomous University of Mexico
UNICAMP,Technical University of Munich
```

### Multi-year handling

If multiple years of QS data are present in `data/qs/`, the app auto-detects them from filenames. 2026 is the default; a year selector appears if older data exists.

### University filtering

Only subjects where at least 1 of the 6 target universities appears in the ranking are shown.

## UI Layout

### Sidebar (persistent)

- University selector (multi-select, defaults to all 6)
- Faculty area dropdown (Arts & Humanities, Engineering & Technology, Life Sciences & Medicine, Natural Sciences, Social Sciences & Management)
- Subject dropdown (filtered by selected faculty area, only subjects where >= 1 of the 6 universities appears)
- Year selector (defaults to 2026, shows other years if data present)

### Main Area — 5 Tabs

#### Tab 1: Score Decomposition (Tier 1 — Subject level)

- Stacked horizontal bar chart: one bar per selected university, segments = indicator QS score x subject-specific weight
- Weight formula displayed below chart (e.g., "Chemistry: AR 40% | ER 20% | CpP 15% | HI 15% | IRN 10%")
- Data table beneath (collapsible, defaults collapsed)
- Auto-generated headline insight at top in plain language

#### Tab 2: Gap Analysis (Tier 1 — Subject level)

- User selects one focus university
- Radar/spider chart: focus university indicator scores vs. average of other Sao Paulo peers
- Opportunity table: (peer avg - focus score) x weight, sorted descending
- Headline callout: "Your biggest opportunity in [Subject] is [Indicator], worth up to [X] weighted points"

#### Tab 3: Bibliometric Deep Dive (Tier 2 — Faculty area level)

- Grouped bar chart of raw SciVal values across the 6 universities for selected faculty area
- Metrics shown: scholarly output, citations, normalized citations, h-index, IRN locations, IRN partners
- Contextualises QS scores from Tier 1: "behind USP's CpP score of 72 is 50,811 publications with 496,020 citations"

#### Tab 4: Simulator (Tier 2 — Faculty area level)

- Select one university, operates at faculty area level
- Sliders for raw bibliometric values, pre-filled with current SciVal data
- Shows current QS score -> simulated score -> delta
- Mapping from raw to score built from available data points across universities
- "What-if" framing

#### Tab 5: Peer Benchmarking (Tier 2 — Faculty area level)

- Select one focus university
- Two peer sources:
  - **Structural peers (auto)**: institutions with similar scholarly output volume (within +/-30% band) in the same faculty area, ranked by QS overall score (the university's overall ranking score, not a single indicator), filtered to those scoring slightly better (up to 20 positions higher in overall rank), top 5 shown
  - **Manual peers**: from `peers.csv`, always shown
- Table: focus university at top, peers below, columns = raw SciVal values + QS scores per indicator
- Conditional formatting: green = focus leads, red = focus trails
- Delta column per indicator
- Insight callout identifying most common area of outperformance across peers
- Note in UI: "To add more institutions to the benchmarking pool, export their SciVal data and drop into data/scival/"

## Visual Design

### Color scheme

- University colors (consistent across all tabs): USP = blue, Unicamp = green, Unesp = red, Unifesp = orange, UFSCar = purple, UFABC = teal
- Indicator colors (secondary palette, matching QS SVGs): AR = red (#DE472C), ER = yellow (#FECC01), CpP = blue (#739ED9), HI = orange (#F7A70D), IRN = dark orange (#F76000)
- Leadership view uses university colors; analyst view uses indicator colors

### Interactions

- Hover: tooltip with exact values on any bar segment
- Click: selecting a university in any chart sets it as focus for Gap Analysis and Simulator
- All charts Plotly-based (zoom, pan, export)

### Layout principles

- Each tab opens with a headline insight in plain language, auto-generated from data
- Chart below the headline
- Collapsible data table below chart (collapsed by default — leadership users stay at chart level, analyst users expand for raw numbers; no explicit mode switcher, just a toggle on each table)
- Streamlit native column layout, sidebar fixed, main area scrolls

## Technical Stack

- Python 3.11+
- Streamlit
- Pandas
- Plotly
- openpyxl (Excel reading)
- No database — flat files only

## Project Structure

```
qs-subject-dashboard/
├── app.py                    # Streamlit entry point, sidebar, tab routing
├── data/
│   ├── qs/                   # QS Subject Rankings xlsx files (by year)
│   ├── scival/               # SciVal CSV exports (by university)
│   ├── peers.csv             # Manual peer group definitions
│   └── weights.json          # Hardcoded indicator weights per subject
├── src/
│   ├── data_loader.py        # Read & validate QS + SciVal files, cache
│   ├── weights.py            # Weights lookup, weight x score calculations
│   ├── peers.py              # Peer matching (structural + manual)
│   ├── simulator.py          # Score simulation logic
│   └── insights.py           # Auto-generate headline text from data
├── tabs/
│   ├── tab1_decomposition.py # Score Decomposition
│   ├── tab2_gap_analysis.py  # Gap Analysis
│   ├── tab3_deep_dive.py     # Bibliometric Deep Dive
│   ├── tab4_simulator.py     # Simulator
│   └── tab5_benchmarking.py  # Peer Benchmarking
├── requirements.txt          # streamlit, pandas, plotly, openpyxl
└── README.md
```

## Key Module Responsibilities

- **data_loader.py**: Scans `data/qs/` and `data/scival/` on startup. Auto-detects years from QS filenames and universities from SciVal filenames. Validates that target universities exist. Caches with `@st.cache_data`. Logs warnings for missing data.
- **weights.py**: Looks up subject-specific or faculty-area-level weights from `weights.json`. Provides weighted score calculation.
- **peers.py**: Loads `peers.csv` for manual peers. Implements structural peer matching by scholarly output volume band (+/-30%) from SciVal data.
- **simulator.py**: Builds approximate raw-to-score mapping from available data points. Applies weight formula to produce simulated scores.
- **insights.py**: Generates plain-language headline strings from data (e.g., "USP's biggest gap vs. peers in Chemistry is IRN, worth up to 3.2 weighted points").

## Constraints & Limitations

- SciVal data is only available at the 5 broad faculty area level, not per individual QS subject. Subject-level analysis uses QS scores only.
- The QS normalization formula (raw value to 0-100 score) is opaque. The simulator builds an approximate mapping from available data points.
- Structural peer matching requires SciVal exports for peer institutions. Initially limited to the 6 target universities unless user provides additional exports.
- SciVal has no API; all data is manually exported and dropped into `data/scival/`.
- QS Subject Rankings data for 2026 is the primary dataset. Older years supported if xlsx files are provided.
