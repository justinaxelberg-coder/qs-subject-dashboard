# QS Subject Rankings Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit dashboard comparing 6 Sao Paulo public universities across QS Subject Rankings, enriched with SciVal data, to reveal the bibliometric determinants of ranking performance.

**Architecture:** Two-tier data model — Tier 1 (subject level) uses QS indicator scores for decomposition and gap analysis; Tier 2 (faculty area level) uses SciVal raw bibliometric data for deep dives, simulation, and peer benchmarking. All data from flat files, no database.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly, openpyxl

---

## File Structure

```
qs-subject-dashboard/
├── app.py                     # Streamlit entry point, sidebar, tab routing
├── requirements.txt           # Dependencies
├── data/
│   ├── qs/                    # QS Subject Rankings xlsx files
│   ├── scival/                # SciVal CSV exports
│   ├── peers.csv              # Manual peer definitions
│   └── weights.json           # Indicator weights per subject
├── src/
│   ├── __init__.py
│   ├── constants.py           # University names, colors, indicator codes
│   ├── data_loader.py         # Load and validate QS + SciVal data
│   ├── weights.py             # Weight lookups and weighted score math
│   ├── insights.py            # Auto-generated headline text
│   ├── peers.py               # Peer matching logic
│   └── simulator.py           # Score simulation
├── tabs/
│   ├── __init__.py
│   ├── tab1_decomposition.py  # Score Decomposition
│   ├── tab2_gap_analysis.py   # Gap Analysis
│   ├── tab3_deep_dive.py      # Bibliometric Deep Dive
│   ├── tab4_simulator.py      # Simulator
│   └── tab5_benchmarking.py   # Peer Benchmarking
└── tests/
    ├── __init__.py
    ├── conftest.py            # Shared fixtures (sample DataFrames)
    ├── test_data_loader.py
    ├── test_weights.py
    ├── test_insights.py
    ├── test_peers.py
    └── test_simulator.py
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/constants.py`
- Create: `tabs/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `data/qs/.gitkeep`
- Create: `data/scival/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
numpy>=1.24.0
pytest>=7.4.0
```

- [ ] **Step 2: Create src/constants.py**

```python
"""Shared constants for the QS Subject Rankings dashboard."""

# Target universities — canonical names as they appear in QS data
TARGET_UNIVERSITIES = [
    "Universidade de São Paulo",
    "Universidade Estadual de Campinas",
    "Universidade Estadual Paulista 'Júlio de Mesquita Filho'",
    "Universidade Federal de São Paulo",
    "Universidade Federal de São Carlos",
    "Universidade Federal do ABC",
]

# Short display names
UNIVERSITY_SHORT_NAMES = {
    "Universidade de São Paulo": "USP",
    "Universidade Estadual de Campinas": "UNICAMP",
    "Universidade Estadual Paulista 'Júlio de Mesquita Filho'": "UNESP",
    "Universidade Federal de São Paulo": "UNIFESP",
    "Universidade Federal de São Carlos": "UFSCar",
    "Universidade Federal do ABC": "UFABC",
}

# University colors (consistent across all tabs)
UNIVERSITY_COLORS = {
    "USP": "#1f77b4",       # blue
    "UNICAMP": "#2ca02c",   # green
    "UNESP": "#d62728",     # red
    "UNIFESP": "#ff7f0e",   # orange
    "UFSCar": "#9467bd",    # purple
    "UFABC": "#17becf",     # teal
}

# Indicator codes and display names
INDICATOR_NAMES = {
    "AR": "Academic Reputation",
    "ER": "Employer Reputation",
    "CpP": "Citations per Paper",
    "HI": "H-Index",
    "IRN": "International Research Network",
}

# Indicator colors (matching QS SVG palette)
INDICATOR_COLORS = {
    "AR": "#DE472C",   # red
    "ER": "#FECC01",   # yellow
    "CpP": "#739ED9",  # blue
    "HI": "#F7A70D",   # orange
    "IRN": "#F76000",  # dark orange
}

# Mapping from QS xlsx column headers to indicator codes
QS_COLUMN_TO_INDICATOR = {
    "Academic": "AR",
    "Employer": "ER",
    "Citations": "CpP",
    "H": "HI",
    "International": "IRN",
}

# Faculty areas
FACULTY_AREAS = [
    "Arts & Humanities",
    "Engineering & Technology",
    "Life Sciences & Medicine",
    "Natural Sciences",
    "Social Sciences & Management",
]
```

- [ ] **Step 3: Create empty init files and data directories**

```bash
mkdir -p src tabs tests data/qs data/scival
touch src/__init__.py tabs/__init__.py tests/__init__.py
touch data/qs/.gitkeep data/scival/.gitkeep
```

- [ ] **Step 4: Create tests/conftest.py with shared fixtures**

```python
"""Shared test fixtures for QS Subject Rankings dashboard."""

import pandas as pd
import pytest


@pytest.fixture
def sample_qs_subject_data():
    """Sample QS Subject Rankings data for testing."""
    return pd.DataFrame({
        "year": [2026, 2026, 2026],
        "subject": ["Chemistry", "Chemistry", "Chemistry"],
        "faculty_area": ["Natural Sciences", "Natural Sciences", "Natural Sciences"],
        "institution": [
            "Universidade de São Paulo",
            "Universidade Estadual de Campinas",
            "Universidade Federal de São Carlos",
        ],
        "country": ["Brazil", "Brazil", "Brazil"],
        "rank": [85, 201, 401],
        "overall_score": [72.3, 55.1, 38.7],
        "AR": [78.5, 60.2, 35.1],
        "ER": [65.3, 45.8, 28.4],
        "CpP": [70.1, 58.9, 45.2],
        "HI": [68.4, 52.3, 40.8],
        "IRN": [55.2, 48.7, 35.6],
    })


@pytest.fixture
def sample_scival_citations_data():
    """Sample SciVal Citations per Faculty data for testing."""
    return pd.DataFrame({
        "university": [
            "Universidade de São Paulo",
            "Universidade de São Paulo",
        ],
        "faculty_area": ["Life Sciences & Medicine", "Natural Sciences"],
        "scholarly_output_qs": [50811, 20489],
        "excluded_scholarly_output": [5518, 1344],
        "total_scholarly_output": [56329, 21833],
        "citations_qs": [496020, 171702],
        "excluded_self_citations": [276565, 102492],
        "total_citations": [772585, 274194],
        "normalized_citation_count_qs": [433494, 215661],
        "weighting_factor_qs": [0.61, 0.88],
        "weighting_adjustment_ratio_qs": [1.43, 1.43],
        "citation_per_faculty_score": [40.3, 40.3],
    })


@pytest.fixture
def sample_scival_irn_data():
    """Sample SciVal IRN data for testing."""
    return pd.DataFrame({
        "university": [
            "Universidade de São Paulo",
            "Universidade de São Paulo",
        ],
        "faculty_area": ["Life Sciences & Medicine", "Natural Sciences"],
        "irn_scholarly_output_qs": [19053, 8977],
        "locations_qs": [118.0, 81.0],
        "partners_qs": [1529.0, 1209.0],
        "non_scaled_irn_index_qs": [16.09, 11.41],
        "irn_index_qs": [85.51, 73.03],
        "irn_score": [95.3, 95.3],
    })


@pytest.fixture
def sample_weights():
    """Sample weights dictionary for testing."""
    return {
        "broad": {
            "Arts & Humanities": {"AR": 60, "ER": 20, "CpP": 7.5, "HI": 7.5, "IRN": 5},
            "Natural Sciences": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
        },
        "subjects": {
            "Chemistry": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
            "History": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15},
        },
    }
```

- [ ] **Step 5: Install dependencies and verify**

```bash
pip install -r requirements.txt
python -c "import streamlit, pandas, plotly, openpyxl; print('All dependencies OK')"
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt src/ tabs/ tests/ data/
git commit -m "feat: project scaffold with constants, fixtures, and dependencies"
```

---

### Task 2: Weights Data and Lookup Module

**Files:**
- Create: `data/weights.json`
- Create: `src/weights.py`
- Create: `tests/test_weights.py`

- [ ] **Step 1: Write the failing tests for weights module**

```python
# tests/test_weights.py
"""Tests for weights lookup and weighted score calculations."""

import pytest
from src.weights import load_weights, get_subject_weights, calculate_weighted_contributions


def test_load_weights_returns_dict(tmp_path):
    """load_weights reads weights.json and returns dict with 'broad' and 'subjects' keys."""
    import json
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(json.dumps({
        "broad": {"Natural Sciences": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}},
        "subjects": {"Chemistry": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}},
    }))
    result = load_weights(str(weights_file))
    assert "broad" in result
    assert "subjects" in result
    assert "Chemistry" in result["subjects"]


def test_get_subject_weights_known_subject(sample_weights):
    """get_subject_weights returns subject-specific weights when subject exists."""
    result = get_subject_weights(sample_weights, "Chemistry")
    assert result == {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}


def test_get_subject_weights_falls_back_to_broad(sample_weights):
    """get_subject_weights falls back to broad faculty area weights for unknown subjects."""
    result = get_subject_weights(sample_weights, "Unknown Subject", faculty_area="Natural Sciences")
    assert result == {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}


def test_get_subject_weights_missing_raises():
    """get_subject_weights raises KeyError when neither subject nor faculty area found."""
    weights = {"broad": {}, "subjects": {}}
    with pytest.raises(KeyError):
        get_subject_weights(weights, "Unknown", faculty_area="Unknown")


def test_calculate_weighted_contributions():
    """calculate_weighted_contributions returns indicator_code -> weighted_points dict."""
    scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}
    result = calculate_weighted_contributions(scores, weights)
    assert result["AR"] == pytest.approx(32.0)   # 80 * 0.40
    assert result["ER"] == pytest.approx(12.0)   # 60 * 0.20
    assert result["CpP"] == pytest.approx(10.5)  # 70 * 0.15
    assert result["HI"] == pytest.approx(7.5)    # 50 * 0.15
    assert result["IRN"] == pytest.approx(4.0)   # 40 * 0.10


def test_calculate_weighted_contributions_missing_indicator():
    """Indicators missing from weights are treated as 0 contribution."""
    scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 70, "ER": 30}  # No bibliometrics (e.g., Art & Design)
    result = calculate_weighted_contributions(scores, weights)
    assert result["AR"] == pytest.approx(56.0)
    assert result["ER"] == pytest.approx(18.0)
    assert result.get("CpP", 0) == 0
    assert result.get("HI", 0) == 0
    assert result.get("IRN", 0) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_weights.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.weights'`

- [ ] **Step 3: Create data/weights.json with all subject weights**

Write `data/weights.json` with the complete weights extracted from the QS methodology SVGs. Structure:

```json
{
  "broad": {
    "Arts & Humanities": {"AR": 60, "ER": 20, "CpP": 7.5, "HI": 7.5, "IRN": 5},
    "Engineering & Technology": {"AR": 40, "ER": 30, "CpP": 10, "HI": 10, "IRN": 10},
    "Life Sciences & Medicine": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Natural Sciences": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "Social Sciences & Management": {"AR": 50, "ER": 30, "CpP": 7.5, "HI": 7.5, "IRN": 5}
  },
  "subjects": {
    "Archaeology": {"AR": 70, "ER": 10, "CpP": 10, "HI": 10},
    "Architecture / Built Environment": {"AR": 70, "ER": 10, "CpP": 10, "HI": 10},
    "Art and Design": {"AR": 90, "ER": 10},
    "Classics and Ancient History": {"AR": 90, "ER": 10},
    "English Language and Literature": {"AR": 80, "ER": 10, "CpP": 10},
    "History": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15},
    "History of Art": {"AR": 90, "ER": 10},
    "Linguistics": {"AR": 80, "ER": 10, "CpP": 5, "HI": 5},
    "Modern Languages": {"AR": 70, "ER": 30},
    "Music": {"AR": 80, "ER": 20},
    "Performing Arts": {"AR": 80, "ER": 20},
    "Philosophy": {"AR": 75, "ER": 5, "CpP": 10, "HI": 10},
    "Theology, Divinity and Religious Studies": {"AR": 70, "ER": 10, "CpP": 10, "HI": 10},
    "Computer Science and Information Systems": {"AR": 40, "ER": 30, "CpP": 12.5, "HI": 12.5, "IRN": 5},
    "Data Science and Artificial Intelligence": {"AR": 40, "ER": 30, "CpP": 15, "HI": 15},
    "Engineering - Chemical": {"AR": 40, "ER": 30, "CpP": 12.5, "HI": 12.5, "IRN": 5},
    "Engineering - Civil and Structural": {"AR": 40, "ER": 30, "CpP": 15, "HI": 15},
    "Engineering - Electrical and Electronic": {"AR": 40, "ER": 30, "CpP": 12.5, "HI": 12.5, "IRN": 5},
    "Engineering - Mechanical, Aeronautical and Manufacturing": {"AR": 40, "ER": 30, "CpP": 12.5, "HI": 12.5, "IRN": 5},
    "Engineering - Mineral and Mining": {"AR": 40, "ER": 30, "CpP": 15, "HI": 15},
    "Engineering - Petroleum": {"AR": 40, "ER": 30, "CpP": 15, "HI": 15},
    "Agriculture and Forestry": {"AR": 50, "ER": 10, "CpP": 15, "HI": 15, "IRN": 10},
    "Anatomy and Physiology": {"AR": 40, "ER": 10, "CpP": 25, "HI": 25},
    "Biological Sciences": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Dentistry": {"AR": 30, "ER": 10, "CpP": 30, "HI": 30},
    "Medicine": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Nursing": {"AR": 30, "ER": 10, "CpP": 30, "HI": 30},
    "Pharmacy and Pharmacology": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Psychology": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "Veterinary Science": {"AR": 30, "ER": 10, "CpP": 30, "HI": 30},
    "Chemistry": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "Earth and Marine Sciences": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Environmental Sciences": {"AR": 40, "ER": 10, "CpP": 22.5, "HI": 22.5, "IRN": 5},
    "Geography": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15},
    "Geology": {"AR": 30, "ER": 10, "CpP": 25, "HI": 25, "IRN": 10},
    "Geophysics": {"AR": 30, "ER": 10, "CpP": 25, "HI": 25, "IRN": 10},
    "Materials Science": {"AR": 40, "ER": 10, "CpP": 20, "HI": 20, "IRN": 10},
    "Mathematics": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "Physics and Astronomy": {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10},
    "Accounting and Finance": {"AR": 50, "ER": 30, "CpP": 10, "HI": 10},
    "Anthropology": {"AR": 70, "ER": 10, "CpP": 10, "HI": 10},
    "Business and Management Studies": {"AR": 50, "ER": 30, "CpP": 10, "HI": 10},
    "Communication and Media Studies": {"AR": 50, "ER": 10, "CpP": 20, "HI": 20},
    "Development Studies": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15},
    "Economics and Econometrics": {"AR": 40, "ER": 20, "CpP": 20, "HI": 20},
    "Education": {"AR": 50, "ER": 10, "CpP": 20, "HI": 20},
    "Hospitality and Leisure Management": {"AR": 45, "ER": 50, "CpP": 5},
    "Law": {"AR": 50, "ER": 30, "CpP": 5, "HI": 15},
    "Library and Information Management": {"AR": 70, "ER": 10, "CpP": 15, "HI": 5},
    "Marketing": {"AR": 50, "ER": 30, "CpP": 10, "HI": 10},
    "Politics and International Studies": {"AR": 50, "ER": 30, "CpP": 10, "HI": 10},
    "Social Policy and Administration": {"AR": 70, "ER": 20, "CpP": 10},
    "Sociology": {"AR": 70, "ER": 10, "CpP": 5, "HI": 15},
    "Sports-related Subjects": {"AR": 60, "ER": 10, "CpP": 15, "HI": 15},
    "Statistics and Operational Research": {"AR": 50, "ER": 10, "CpP": 20, "HI": 20}
  }
}
```

- [ ] **Step 4: Implement src/weights.py**

```python
"""Weight lookups and weighted score calculations."""

import json
from pathlib import Path
from typing import Optional


def load_weights(weights_path: str = "data/weights.json") -> dict:
    """Load weights from JSON file.

    Returns dict with 'broad' and 'subjects' keys.
    """
    with open(weights_path, "r") as f:
        return json.load(f)


def get_subject_weights(
    weights: dict, subject: str, faculty_area: Optional[str] = None
) -> dict:
    """Get indicator weights for a subject.

    Looks up subject-specific weights first. Falls back to broad faculty area
    weights if subject not found and faculty_area is provided.

    Returns dict mapping indicator codes (AR, ER, CpP, HI, IRN) to weight
    percentages (e.g., {"AR": 40, "ER": 20, ...}).

    Raises KeyError if neither subject nor faculty area found.
    """
    if subject in weights["subjects"]:
        return weights["subjects"][subject]
    if faculty_area and faculty_area in weights["broad"]:
        return weights["broad"][faculty_area]
    raise KeyError(
        f"No weights found for subject '{subject}'"
        + (f" or faculty area '{faculty_area}'" if faculty_area else "")
    )


def calculate_weighted_contributions(
    scores: dict, weights: dict
) -> dict:
    """Calculate each indicator's weighted contribution to the overall score.

    Args:
        scores: dict mapping indicator codes to QS scores (0-100).
        weights: dict mapping indicator codes to weight percentages.

    Returns:
        dict mapping indicator codes to weighted points
        (score * weight / 100).
    """
    result = {}
    for indicator in ["AR", "ER", "CpP", "HI", "IRN"]:
        weight = weights.get(indicator, 0)
        score = scores.get(indicator, 0)
        if weight > 0:
            result[indicator] = score * weight / 100
    return result
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_weights.py -v
```

Expected: All 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add data/weights.json src/weights.py tests/test_weights.py
git commit -m "feat: weights lookup module with subject-specific and fallback weights"
```

---

### Task 3: QS Data Loader

**Files:**
- Create: `src/data_loader.py`
- Create: `tests/test_data_loader.py`

- [ ] **Step 1: Write failing tests for QS data loading**

```python
# tests/test_data_loader.py
"""Tests for data loading and validation."""

import pandas as pd
import pytest
from unittest.mock import patch
from src.data_loader import (
    parse_qs_subject_sheet,
    load_qs_data,
    detect_qs_years,
    filter_target_universities,
    get_available_subjects,
)


def test_parse_qs_subject_sheet_extracts_columns():
    """parse_qs_subject_sheet returns DataFrame with standard columns."""
    # We test with the actual file if available, otherwise skip
    import os
    test_file = "data/qs/2022 Subject Rankings Results (for qs.com).xlsx"
    if not os.path.exists(test_file):
        pytest.skip("QS test data not available")
    df = parse_qs_subject_sheet(test_file, "Chemistry", 2022)
    assert "institution" in df.columns
    assert "rank" in df.columns
    assert "overall_score" in df.columns
    assert "AR" in df.columns
    assert "subject" in df.columns
    assert df["subject"].iloc[0] == "Chemistry"
    assert df["year"].iloc[0] == 2022


def test_filter_target_universities(sample_qs_subject_data):
    """filter_target_universities returns only rows for the 6 SP universities."""
    result = filter_target_universities(sample_qs_subject_data)
    assert len(result) == 3
    assert all(
        inst in result["institution"].values
        for inst in [
            "Universidade de São Paulo",
            "Universidade Estadual de Campinas",
            "Universidade Federal de São Carlos",
        ]
    )


def test_filter_target_universities_empty():
    """filter_target_universities returns empty df when no matches."""
    df = pd.DataFrame({
        "institution": ["MIT", "Stanford"],
        "rank": [1, 2],
    })
    result = filter_target_universities(df)
    assert len(result) == 0


def test_get_available_subjects(sample_qs_subject_data):
    """get_available_subjects returns subjects where >= 1 target university appears."""
    result = get_available_subjects(sample_qs_subject_data)
    assert "Chemistry" in result


def test_get_available_subjects_by_faculty_area(sample_qs_subject_data):
    """get_available_subjects filters by faculty area when provided."""
    result = get_available_subjects(sample_qs_subject_data, faculty_area="Natural Sciences")
    assert "Chemistry" in result
    result_empty = get_available_subjects(sample_qs_subject_data, faculty_area="Arts & Humanities")
    assert len(result_empty) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_data_loader.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'src.data_loader'`

- [ ] **Step 3: Implement src/data_loader.py (QS loading portion)**

```python
"""Load and validate QS Subject Rankings and SciVal data."""

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.constants import TARGET_UNIVERSITIES, QS_COLUMN_TO_INDICATOR


def detect_qs_years(qs_dir: str = "data/qs") -> list[int]:
    """Scan qs_dir for xlsx files and extract years from filenames.

    Expected filename patterns:
    - '2022 Subject Rankings Results (for qs.com).xlsx'
    - 'QS_Subject_Rankings_2026.xlsx'

    Returns sorted list of years found (descending, newest first).
    """
    years = set()
    for f in Path(qs_dir).glob("*.xlsx"):
        matches = re.findall(r"20\d{2}", f.stem)
        for m in matches:
            year = int(m)
            if 2015 <= year <= 2030:
                years.add(year)
    return sorted(years, reverse=True)


def parse_qs_subject_sheet(
    filepath: str, sheet_name: str, year: int
) -> pd.DataFrame:
    """Parse a single subject sheet from a QS Subject Rankings xlsx file.

    The xlsx format has metadata rows at top, then a header row with columns
    like: '2022', '2021', 'Institution', 'Country', 'Academic', 'Employer',
    'Citations', 'H', 'Score'. Some sheets also have 'International' (IRN).

    Also extracts the faculty area from row 2.

    Returns DataFrame with standardized columns:
    year, subject, faculty_area, institution, country, rank, overall_score,
    AR, ER, CpP, HI, IRN (IRN may be NaN if not present).
    """
    # Read raw — no header, we find it ourselves
    raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    # Extract faculty area from row 2 (format: 'Faculty Area', '<name>', ...)
    faculty_area = None
    if len(raw) > 2:
        row2 = raw.iloc[2].dropna().tolist()
        if len(row2) >= 2 and row2[0] == "Faculty Area":
            faculty_area = str(row2[1])

    # Find the header row — it contains 'Institution' and 'Score'
    header_row_idx = None
    for idx, row in raw.iterrows():
        vals = [str(v).strip() for v in row.dropna().values]
        if "Institution" in vals and "Score" in vals:
            header_row_idx = idx
            break

    if header_row_idx is None:
        return pd.DataFrame()

    # Re-read with proper header
    df = pd.read_excel(
        filepath, sheet_name=sheet_name, header=header_row_idx
    )

    # Drop rows where Institution is NaN
    df = df.dropna(subset=["Institution"])

    # Build standardized output
    result = pd.DataFrame()
    result["year"] = year
    result["subject"] = sheet_name
    result["faculty_area"] = faculty_area
    result["institution"] = df["Institution"].str.strip().values
    result["country"] = df["Country"].str.strip().values if "Country" in df.columns else None

    # Rank — first column, may have trailing spaces
    rank_col = df.columns[0]
    result["rank"] = pd.to_numeric(
        df[rank_col].astype(str).str.strip().str.replace(r"[^\d]", "", regex=True),
        errors="coerce",
    )

    result["overall_score"] = pd.to_numeric(df["Score"], errors="coerce")

    # Map indicator columns
    for col_name, indicator_code in QS_COLUMN_TO_INDICATOR.items():
        if col_name in df.columns:
            result[indicator_code] = pd.to_numeric(df[col_name], errors="coerce")
        else:
            result[indicator_code] = float("nan")

    return result


def load_qs_data(qs_dir: str = "data/qs") -> pd.DataFrame:
    """Load all QS Subject Rankings data from xlsx files in qs_dir.

    Auto-detects years and subjects. Returns combined DataFrame.
    Skips sheets that are metadata-only (e.g., 'Main', broad faculty area sheets).
    """
    all_frames = []
    skip_sheets = {"Main"}

    for filepath in Path(qs_dir).glob("*.xlsx"):
        years = re.findall(r"20\d{2}", filepath.stem)
        if not years:
            continue
        year = int(years[0])

        import openpyxl
        wb = openpyxl.load_workbook(str(filepath), read_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        for sheet_name in sheet_names:
            if sheet_name in skip_sheets:
                continue
            try:
                df = parse_qs_subject_sheet(str(filepath), sheet_name, year)
                if len(df) > 0:
                    all_frames.append(df)
            except Exception as e:
                print(f"Warning: could not parse sheet '{sheet_name}' from {filepath.name}: {e}")

    if not all_frames:
        return pd.DataFrame()

    return pd.concat(all_frames, ignore_index=True)


def filter_target_universities(df: pd.DataFrame) -> pd.DataFrame:
    """Filter DataFrame to only include the 6 target SP universities.

    Uses fuzzy matching — checks if any target university name is contained
    in the institution column (handles minor naming variations).
    """
    if df.empty or "institution" not in df.columns:
        return df

    mask = pd.Series(False, index=df.index)
    for target in TARGET_UNIVERSITIES:
        # Check both directions for substring matching
        mask |= df["institution"].str.contains(target[:20], case=False, na=False)

    return df[mask].copy()


def get_available_subjects(
    df: pd.DataFrame, faculty_area: Optional[str] = None
) -> list[str]:
    """Get subjects where at least 1 target university appears.

    Optionally filter by faculty area first.
    Returns sorted list of subject names.
    """
    filtered = filter_target_universities(df)
    if faculty_area:
        filtered = filtered[filtered["faculty_area"] == faculty_area]
    return sorted(filtered["subject"].dropna().unique().tolist())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_data_loader.py -v
```

Expected: All tests PASS (the file-dependent test skips if no data)

- [ ] **Step 5: Commit**

```bash
git add src/data_loader.py tests/test_data_loader.py
git commit -m "feat: QS Subject Rankings data loader with auto-detection and filtering"
```

---

### Task 4: SciVal Data Loader

**Files:**
- Modify: `src/data_loader.py`
- Modify: `tests/test_data_loader.py`

- [ ] **Step 1: Write failing tests for SciVal loading**

Add to `tests/test_data_loader.py`:

```python
from src.data_loader import parse_scival_csv, load_scival_data


def test_parse_scival_citations_csv(tmp_path):
    """parse_scival_csv correctly reads a Citations per Faculty CSV."""
    csv_content = '''Data set,"QS World University Rankings 2026 - Citations per Faculty"
Entity,"Universidade de São Paulo"

"Year range","2019 to 2023"
Subject classification,"QS"
Filtered by,"All subject areas"

Types of publications included
Gross,"All types"
QS,"Article, review, conference paper, book, book chapter, article in press"

Self-citations
Gross,Included
QS,Author-level excluded

Data source,Scopus
Date last updated,9 February 2023
Date exported,30 March 2026

Citation per Faculty Score,40.3

"QS metrics","Scholarly Output (QS)","Excluded Scholarly Output","Total Scholarly Output","Citations (QS)","Excluded self-citations","Total Citations","Normalized Total Citation Count (QS)","Weighting Factor (QS)","Weighting Adjustment Ratio (QS)"
Arts & Humanities,2546,147,2693,4441,2005,6446,16547,14.59,0.26
Engineering & Technology,21052,767,21819,173376,66326,239702,155062,0.63,1.43
Life Sciences & Medicine,50811,5518,56329,496020,276565,772585,433494,0.61,1.43
Natural Sciences,20489,1344,21833,171702,102492,274194,215661,0.88,1.43
Social Sciences & Management,11686,532,12218,77641,26563,104204,63256,1.8,0.45
Total,106584,8308,114892,923180,473951,1397131,606239,N/A,N/A
Deduplicated Count,80382,7186,87568,696972,378019,1074991,N/A,N/A,N/A
'''
    csv_file = tmp_path / "citations.csv"
    csv_file.write_text(csv_content)
    result = parse_scival_csv(str(csv_file))
    assert result["university"] == "Universidade de São Paulo"
    assert result["metric_type"] == "citations_per_faculty"
    assert result["overall_score"] == 40.3
    assert len(result["data"]) == 5  # 5 faculty areas (excludes Total, Deduplicated)
    assert result["data"]["faculty_area"].iloc[0] == "Arts & Humanities"


def test_parse_scival_irn_csv(tmp_path):
    """parse_scival_csv correctly reads an IRN CSV."""
    csv_content = '''Data set,"QS World University Rankings 2026 - International Research Network Index"
Entity,"Universidade de São Paulo"

"Year range","2019 to 2023"
Subject classification,"QS"
Filtered by,"All subject areas"

Types of publications included
Gross,"All types"
QS,"Article, review, conference paper, book, book chapter, article in press"

Self-citations
Gross,Included
QS,Author-level excluded

Data source,Scopus
Date last updated,9 February 2023
Date exported,30 March 2026

International Research Network (IRN) Score,95.3

"QS metrics","IRN Scholarly Output (QS)","Locations (QS)","Partners (QS)","Non-Scaled International Research Network (IRN) Index (QS)","International Research Network (IRN) Index (QS)"
Arts & Humanities,297,21.0,90.0,4.67,45.73
Engineering & Technology,7617,81.0,1034.0,11.67,77.28
Life Sciences & Medicine,19053,118.0,1529.0,16.09,85.51
Natural Sciences,8977,81.0,1209.0,11.41,73.03
Social Sciences & Management,3239,64.0,633.0,9.92,65.46
Total,29727,73.0,899.0,N/A,69.4
'''
    csv_file = tmp_path / "irn.csv"
    csv_file.write_text(csv_content)
    result = parse_scival_csv(str(csv_file))
    assert result["university"] == "Universidade de São Paulo"
    assert result["metric_type"] == "irn"
    assert result["overall_score"] == 95.3
    assert len(result["data"]) == 5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_data_loader.py::test_parse_scival_citations_csv -v
pytest tests/test_data_loader.py::test_parse_scival_irn_csv -v
```

Expected: FAIL with `ImportError: cannot import name 'parse_scival_csv'`

- [ ] **Step 3: Implement SciVal parsing in src/data_loader.py**

Add the following functions to `src/data_loader.py`:

```python
def parse_scival_csv(filepath: str) -> dict:
    """Parse a SciVal QS WUR export CSV.

    SciVal CSVs have a metadata header section, then a data table.
    The metadata contains the Entity (university name), dataset name
    (which tells us the metric type), and an overall score.

    Returns dict with:
    - university: str
    - metric_type: str ('citations_per_faculty', 'irn', etc.)
    - overall_score: float
    - data: DataFrame with faculty_area column + metric-specific columns
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    university = None
    metric_type = None
    overall_score = None
    data_start_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip().strip('"')

        # Extract entity (university)
        if line.startswith("Entity,"):
            university = line.split(",", 1)[1].strip().strip('"')

        # Extract dataset name to determine metric type
        if line.startswith("Data set,"):
            dataset = line.split(",", 1)[1].strip().strip('"')
            if "Citations per Faculty" in dataset:
                metric_type = "citations_per_faculty"
            elif "International Research Network" in dataset:
                metric_type = "irn"
            elif "H-Index" in dataset or "H-index" in dataset:
                metric_type = "h_index"
            else:
                metric_type = dataset.lower().replace(" ", "_")

        # Extract overall score
        if "Score," in line and any(
            keyword in line
            for keyword in ["Citation per Faculty Score", "IRN) Score", "H-Index Score", "H-index Score"]
        ):
            try:
                score_str = line.strip().rsplit(",", 1)[1].strip()
                overall_score = float(score_str)
            except (ValueError, IndexError):
                pass

        # Find data table header (starts with "QS metrics" or similar)
        if '"QS metrics"' in line or "QS metrics" in line:
            data_start_idx = i
            break

    if data_start_idx is None:
        return {
            "university": university,
            "metric_type": metric_type,
            "overall_score": overall_score,
            "data": pd.DataFrame(),
        }

    # Read the data table
    import io
    data_text = "".join(lines[data_start_idx:])
    df = pd.read_csv(io.StringIO(data_text))

    # Rename first column to faculty_area
    df = df.rename(columns={df.columns[0]: "faculty_area"})

    # Remove Total and Deduplicated rows
    df = df[~df["faculty_area"].str.contains("Total|Deduplicated", case=False, na=False)].copy()

    # Clean column names — remove quotes, normalize
    df.columns = [c.strip().strip('"') for c in df.columns]

    # Convert numeric columns
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.reset_index(drop=True)

    return {
        "university": university,
        "metric_type": metric_type,
        "overall_score": overall_score,
        "data": df,
    }


def load_scival_data(scival_dir: str = "data/scival") -> dict:
    """Load all SciVal CSV exports from scival_dir.

    Returns dict keyed by university name, containing sub-dicts keyed by
    metric_type, each holding the parsed data.

    Structure:
    {
        "Universidade de São Paulo": {
            "citations_per_faculty": {"overall_score": 40.3, "data": DataFrame},
            "irn": {"overall_score": 95.3, "data": DataFrame},
        },
        ...
    }
    """
    result = {}
    for filepath in Path(scival_dir).glob("*.csv"):
        try:
            parsed = parse_scival_csv(str(filepath))
            uni = parsed["university"]
            metric = parsed["metric_type"]
            if uni and metric:
                if uni not in result:
                    result[uni] = {}
                result[uni][metric] = {
                    "overall_score": parsed["overall_score"],
                    "data": parsed["data"],
                }
        except Exception as e:
            print(f"Warning: could not parse SciVal file {filepath.name}: {e}")
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_data_loader.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/data_loader.py tests/test_data_loader.py
git commit -m "feat: SciVal CSV parser with auto-detection of metric type and university"
```

---

### Task 5: Insights Module

**Files:**
- Create: `src/insights.py`
- Create: `tests/test_insights.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_insights.py
"""Tests for auto-generated headline insights."""

import pytest
from src.insights import (
    decomposition_insight,
    gap_analysis_insight,
    benchmarking_insight,
)


def test_decomposition_insight():
    """decomposition_insight returns a plain-language headline about score drivers."""
    contributions = {
        "USP": {"AR": 32.0, "ER": 12.0, "CpP": 10.5, "HI": 7.5, "IRN": 4.0},
        "UNICAMP": {"AR": 28.0, "ER": 10.0, "CpP": 12.0, "HI": 9.0, "IRN": 6.0},
    }
    result = decomposition_insight(contributions, "Chemistry")
    assert isinstance(result, str)
    assert "Chemistry" in result
    assert len(result) > 20


def test_gap_analysis_insight():
    """gap_analysis_insight identifies the biggest opportunity."""
    opportunities = [
        {"indicator": "IRN", "gap_points": 3.2},
        {"indicator": "CpP", "gap_points": 1.8},
        {"indicator": "HI", "gap_points": 0.5},
    ]
    result = gap_analysis_insight("USP", "Chemistry", opportunities)
    assert "IRN" in result
    assert "USP" in result
    assert "3.2" in result


def test_gap_analysis_insight_no_gaps():
    """gap_analysis_insight handles case where focus university leads all indicators."""
    result = gap_analysis_insight("USP", "Chemistry", [])
    assert isinstance(result, str)
    assert "USP" in result


def test_benchmarking_insight():
    """benchmarking_insight identifies most common area of outperformance."""
    peer_deltas = {
        "Peer A": {"CpP": 5.0, "HI": -2.0, "IRN": 8.0},
        "Peer B": {"CpP": 3.0, "HI": 1.0, "IRN": 6.0},
        "Peer C": {"CpP": -1.0, "HI": 4.0, "IRN": 10.0},
    }
    result = benchmarking_insight("USP", "Life Sciences & Medicine", peer_deltas)
    assert isinstance(result, str)
    assert "IRN" in result  # All 3 peers outperform on IRN
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_insights.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement src/insights.py**

```python
"""Auto-generate plain-language headline insights from data."""

from src.constants import INDICATOR_NAMES


def decomposition_insight(contributions: dict, subject: str) -> str:
    """Generate a headline insight for the Score Decomposition tab.

    Args:
        contributions: dict mapping university short name to
            dict of indicator -> weighted points.
        subject: the subject name.

    Returns plain-language string.
    """
    if not contributions:
        return f"No data available for {subject}."

    # Find the top-scoring university
    totals = {uni: sum(c.values()) for uni, c in contributions.items()}
    top_uni = max(totals, key=totals.get)
    top_total = totals[top_uni]
    top_contribs = contributions[top_uni]

    # Find the strongest and weakest indicators
    strongest = max(top_contribs, key=top_contribs.get)
    weakest = min(top_contribs, key=top_contribs.get) if len(top_contribs) > 1 else strongest

    strongest_name = INDICATOR_NAMES.get(strongest, strongest)
    weakest_name = INDICATOR_NAMES.get(weakest, weakest)

    return (
        f"In {subject}, {top_uni}'s overall weighted score of {top_total:.1f} "
        f"is driven primarily by {strongest_name} ({top_contribs[strongest]:.1f} pts). "
        f"Its weakest weighted contributor is {weakest_name} "
        f"({top_contribs[weakest]:.1f} pts)."
    )


def gap_analysis_insight(
    focus_uni: str, subject: str, opportunities: list[dict]
) -> str:
    """Generate a headline insight for the Gap Analysis tab.

    Args:
        focus_uni: short name of focus university.
        subject: the subject name.
        opportunities: list of dicts with 'indicator' and 'gap_points',
            sorted descending by gap_points.

    Returns plain-language string.
    """
    if not opportunities:
        return (
            f"{focus_uni} leads or matches peers across all indicators "
            f"in {subject}. No improvement opportunities identified."
        )

    top = opportunities[0]
    indicator_name = INDICATOR_NAMES.get(top["indicator"], top["indicator"])
    return (
        f"{focus_uni}'s biggest opportunity in {subject} is "
        f"{indicator_name}, worth up to {top['gap_points']:.1f} "
        f"weighted points vs. Sao Paulo peers."
    )


def benchmarking_insight(
    focus_uni: str, faculty_area: str, peer_deltas: dict
) -> str:
    """Generate a headline insight for the Peer Benchmarking tab.

    Args:
        focus_uni: short name of focus university.
        faculty_area: the faculty area name.
        peer_deltas: dict mapping peer name to dict of indicator -> delta
            (positive = peer outperforms focus).

    Returns plain-language string.
    """
    if not peer_deltas:
        return f"No peer data available for {focus_uni} in {faculty_area}."

    # Count how many peers outperform on each indicator
    indicator_counts = {}
    for peer, deltas in peer_deltas.items():
        for indicator, delta in deltas.items():
            if delta > 0:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1

    if not indicator_counts:
        return (
            f"{focus_uni} leads all peers across every indicator "
            f"in {faculty_area}."
        )

    # Find most common outperformance area
    most_common = max(indicator_counts, key=indicator_counts.get)
    count = indicator_counts[most_common]
    total_peers = len(peer_deltas)
    indicator_name = INDICATOR_NAMES.get(most_common, most_common)

    return (
        f"{count} of {total_peers} peers outperform {focus_uni} on "
        f"{indicator_name} in {faculty_area}, suggesting this as a "
        f"key area for improvement."
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_insights.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/insights.py tests/test_insights.py
git commit -m "feat: auto-generated plain-language headline insights"
```

---

### Task 6: Peers Module

**Files:**
- Create: `src/peers.py`
- Create: `tests/test_peers.py`
- Create: `data/peers.csv`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_peers.py
"""Tests for peer matching logic."""

import pandas as pd
import pytest
from src.peers import load_manual_peers, find_structural_peers


def test_load_manual_peers(tmp_path):
    """load_manual_peers reads peers.csv and returns dict mapping university to peer list."""
    peers_csv = tmp_path / "peers.csv"
    peers_csv.write_text(
        "university,peer\n"
        "Universidade de São Paulo,University of Barcelona\n"
        "Universidade de São Paulo,National Autonomous University of Mexico\n"
        "UNICAMP,Technical University of Munich\n"
    )
    result = load_manual_peers(str(peers_csv))
    assert "Universidade de São Paulo" in result
    assert len(result["Universidade de São Paulo"]) == 2
    assert "University of Barcelona" in result["Universidade de São Paulo"]
    assert "UNICAMP" in result
    assert len(result["UNICAMP"]) == 1


def test_load_manual_peers_missing_file(tmp_path):
    """load_manual_peers returns empty dict when file doesn't exist."""
    result = load_manual_peers(str(tmp_path / "nonexistent.csv"))
    assert result == {}


def test_find_structural_peers():
    """find_structural_peers finds universities with similar output volume scoring slightly better."""
    all_universities = pd.DataFrame({
        "institution": ["USP", "Peer A", "Peer B", "Peer C", "Far Away", "Much Worse"],
        "faculty_area": ["Natural Sciences"] * 6,
        "scholarly_output": [20000, 18000, 22000, 19000, 50000, 21000],
        "overall_rank": [85, 70, 65, 80, 10, 120],
    })
    result = find_structural_peers(
        focus_university="USP",
        faculty_area="Natural Sciences",
        all_data=all_universities,
        output_band=0.3,
        max_rank_improvement=20,
        top_n=5,
    )
    # Peer A (rank 70, output 18000 within 30%) should be included
    # Peer B (rank 65, output 22000 within 30%) should be included
    # Peer C (rank 80, output 19000 within 30%) should be included
    # Far Away (output 50000) should be excluded — outside 30% band
    # Much Worse (rank 120) should be excluded — worse rank
    assert "Peer A" in result["institution"].values
    assert "Peer B" in result["institution"].values
    assert "Peer C" in result["institution"].values
    assert "Far Away" not in result["institution"].values
    assert "Much Worse" not in result["institution"].values
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_peers.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create data/peers.csv starter file**

```csv
university,peer
```

(Empty header-only file — user populates as needed.)

- [ ] **Step 4: Implement src/peers.py**

```python
"""Peer matching logic — manual and structural."""

from pathlib import Path

import pandas as pd


def load_manual_peers(peers_path: str = "data/peers.csv") -> dict:
    """Load manual peer definitions from CSV.

    Returns dict mapping university name to list of peer institution names.
    Returns empty dict if file doesn't exist.
    """
    if not Path(peers_path).exists():
        return {}

    try:
        df = pd.read_csv(peers_path)
    except Exception:
        return {}

    if df.empty or "university" not in df.columns or "peer" not in df.columns:
        return {}

    result = {}
    for _, row in df.iterrows():
        uni = str(row["university"]).strip()
        peer = str(row["peer"]).strip()
        if uni and peer and uni != "nan" and peer != "nan":
            if uni not in result:
                result[uni] = []
            result[uni].append(peer)
    return result


def find_structural_peers(
    focus_university: str,
    faculty_area: str,
    all_data: pd.DataFrame,
    output_band: float = 0.3,
    max_rank_improvement: int = 20,
    top_n: int = 5,
) -> pd.DataFrame:
    """Find structurally similar universities that score slightly better.

    Args:
        focus_university: name of the university to find peers for.
        faculty_area: faculty area to compare within.
        all_data: DataFrame with columns: institution, faculty_area,
            scholarly_output, overall_rank.
        output_band: fraction tolerance for scholarly output similarity
            (0.3 = within +/-30%).
        max_rank_improvement: max positions higher in rank to consider.
        top_n: max number of peers to return.

    Returns DataFrame of matching peers, sorted by rank (best first).
    """
    area_data = all_data[all_data["faculty_area"] == faculty_area].copy()

    focus_row = area_data[area_data["institution"] == focus_university]
    if focus_row.empty:
        return pd.DataFrame()

    focus_output = focus_row["scholarly_output"].iloc[0]
    focus_rank = focus_row["overall_rank"].iloc[0]

    # Filter: similar output, better rank (but not too much better)
    min_output = focus_output * (1 - output_band)
    max_output = focus_output * (1 + output_band)
    min_rank = focus_rank - max_rank_improvement  # lower rank number = better

    peers = area_data[
        (area_data["institution"] != focus_university)
        & (area_data["scholarly_output"] >= min_output)
        & (area_data["scholarly_output"] <= max_output)
        & (area_data["overall_rank"] < focus_rank)
        & (area_data["overall_rank"] >= max(1, min_rank))
    ].copy()

    peers = peers.sort_values("overall_rank").head(top_n)
    return peers.reset_index(drop=True)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_peers.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/peers.py tests/test_peers.py data/peers.csv
git commit -m "feat: peer matching module with manual and structural peer finding"
```

---

### Task 7: Simulator Module

**Files:**
- Create: `src/simulator.py`
- Create: `tests/test_simulator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_simulator.py
"""Tests for score simulation logic."""

import pytest
from src.simulator import simulate_score_change, build_score_mapping


def test_build_score_mapping():
    """build_score_mapping creates a linear interpolation from data points."""
    data_points = [
        {"raw_value": 100, "qs_score": 50.0},
        {"raw_value": 200, "qs_score": 75.0},
        {"raw_value": 300, "qs_score": 90.0},
    ]
    mapping = build_score_mapping(data_points)
    # Interpolated value at 150 should be ~62.5
    assert mapping(150) == pytest.approx(62.5, abs=1.0)
    # Value at exact point should match
    assert mapping(200) == pytest.approx(75.0, abs=0.1)


def test_build_score_mapping_single_point():
    """build_score_mapping with one data point returns that score for any input."""
    data_points = [{"raw_value": 100, "qs_score": 50.0}]
    mapping = build_score_mapping(data_points)
    assert mapping(100) == pytest.approx(50.0)
    assert mapping(200) == pytest.approx(50.0)


def test_simulate_score_change():
    """simulate_score_change returns current score, simulated score, and delta."""
    current_scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 40.0}
    weights = {"AR": 40, "ER": 20, "CpP": 15, "HI": 15, "IRN": 10}
    adjusted_scores = {"AR": 80.0, "ER": 60.0, "CpP": 70.0, "HI": 50.0, "IRN": 55.0}

    result = simulate_score_change(current_scores, adjusted_scores, weights)
    assert "current_total" in result
    assert "simulated_total" in result
    assert "delta" in result
    assert result["delta"] == pytest.approx(1.5)  # (55-40) * 0.10 = 1.5


def test_simulate_score_change_no_change():
    """simulate_score_change returns 0 delta when scores unchanged."""
    scores = {"AR": 80.0, "ER": 60.0}
    weights = {"AR": 50, "ER": 50}
    result = simulate_score_change(scores, scores, weights)
    assert result["delta"] == pytest.approx(0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_simulator.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement src/simulator.py**

```python
"""Score simulation logic for what-if analysis."""

from typing import Callable
import numpy as np


def build_score_mapping(data_points: list[dict]) -> Callable[[float], float]:
    """Build a linear interpolation function from raw values to QS scores.

    Args:
        data_points: list of dicts with 'raw_value' and 'qs_score' keys.

    Returns:
        callable that takes a raw value and returns estimated QS score.
    """
    if not data_points:
        return lambda x: 0.0

    if len(data_points) == 1:
        score = data_points[0]["qs_score"]
        return lambda x: score

    # Sort by raw value
    sorted_points = sorted(data_points, key=lambda p: p["raw_value"])
    raw_values = [p["raw_value"] for p in sorted_points]
    qs_scores = [p["qs_score"] for p in sorted_points]

    def interpolate(x: float) -> float:
        return float(np.interp(x, raw_values, qs_scores))

    return interpolate


def simulate_score_change(
    current_scores: dict,
    adjusted_scores: dict,
    weights: dict,
) -> dict:
    """Calculate the impact of changing indicator scores.

    Args:
        current_scores: dict mapping indicator codes to current QS scores.
        adjusted_scores: dict mapping indicator codes to adjusted QS scores.
        weights: dict mapping indicator codes to weight percentages.

    Returns dict with:
        current_total: current weighted total
        simulated_total: simulated weighted total
        delta: difference (simulated - current)
        indicator_deltas: dict of per-indicator weighted point changes
    """
    current_total = 0.0
    simulated_total = 0.0
    indicator_deltas = {}

    for indicator, weight in weights.items():
        w = weight / 100.0
        current = current_scores.get(indicator, 0.0)
        adjusted = adjusted_scores.get(indicator, 0.0)
        current_total += current * w
        simulated_total += adjusted * w
        indicator_deltas[indicator] = (adjusted - current) * w

    return {
        "current_total": current_total,
        "simulated_total": simulated_total,
        "delta": simulated_total - current_total,
        "indicator_deltas": indicator_deltas,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_simulator.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/simulator.py tests/test_simulator.py
git commit -m "feat: score simulator with linear interpolation and what-if calculation"
```

---

### Task 8: App Shell — Sidebar and Tab Routing

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create app.py with sidebar and tab structure**

```python
"""QS Subject Rankings Dashboard — Streamlit entry point."""

import streamlit as st
from src.constants import (
    TARGET_UNIVERSITIES,
    UNIVERSITY_SHORT_NAMES,
    FACULTY_AREAS,
)
from src.data_loader import load_qs_data, load_scival_data, get_available_subjects, filter_target_universities
from src.weights import load_weights

st.set_page_config(
    page_title="QS Subject Rankings Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("QS Subject Rankings Dashboard")
st.caption("Comparing São Paulo public universities across areas of knowledge")


# --- Data Loading (cached) ---
@st.cache_data
def cached_load_qs():
    return load_qs_data()


@st.cache_data
def cached_load_scival():
    return load_scival_data()


@st.cache_data
def cached_load_weights():
    return load_weights()


qs_data = cached_load_qs()
scival_data = cached_load_scival()
weights = cached_load_weights()

if qs_data.empty:
    st.error(
        "No QS data found. Place QS Subject Rankings xlsx files in `data/qs/` "
        "and restart the app."
    )
    st.stop()

# Filter to target universities for subject/year discovery
target_data = filter_target_universities(qs_data)

# --- Sidebar ---
st.sidebar.header("Filters")

# University selector
short_to_full = {v: k for k, v in UNIVERSITY_SHORT_NAMES.items()}
available_short = [
    UNIVERSITY_SHORT_NAMES.get(uni, uni)
    for uni in target_data["institution"].unique()
    if uni in UNIVERSITY_SHORT_NAMES
]
selected_short = st.sidebar.multiselect(
    "Universities",
    options=sorted(available_short),
    default=sorted(available_short),
)
selected_universities = [short_to_full.get(s, s) for s in selected_short]

# Faculty area selector
selected_faculty = st.sidebar.selectbox("Faculty Area", FACULTY_AREAS)

# Subject selector (filtered by faculty area and target universities)
available_subjects = get_available_subjects(target_data, faculty_area=selected_faculty)
selected_subject = st.sidebar.selectbox(
    "Subject",
    options=available_subjects if available_subjects else ["(no subjects available)"],
)

# Year selector
available_years = sorted(target_data["year"].unique(), reverse=True)
default_year = 2026 if 2026 in available_years else available_years[0] if available_years else 2026
selected_year = st.sidebar.selectbox("Year", options=available_years, index=0)

# Store selections in session state for tab access
st.session_state["selected_universities"] = selected_universities
st.session_state["selected_subject"] = selected_subject
st.session_state["selected_faculty"] = selected_faculty
st.session_state["selected_year"] = selected_year

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Score Decomposition",
    "🎯 Gap Analysis",
    "🔬 Bibliometric Deep Dive",
    "🎛️ Simulator",
    "🏛️ Peer Benchmarking",
])

with tab1:
    from tabs.tab1_decomposition import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab2:
    from tabs.tab2_gap_analysis import render
    render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year)

with tab3:
    from tabs.tab3_deep_dive import render
    render(scival_data, selected_universities, selected_faculty)

with tab4:
    from tabs.tab4_simulator import render
    render(scival_data, weights, selected_universities, selected_faculty)

with tab5:
    from tabs.tab5_benchmarking import render
    render(qs_data, scival_data, selected_universities, selected_faculty)
```

- [ ] **Step 2: Create placeholder render functions for all tabs**

Create each tab file with a minimal placeholder so the app can load:

```python
# tabs/tab1_decomposition.py
"""Tab 1: Score Decomposition."""
import streamlit as st

def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    st.info("Score Decomposition — coming soon")
```

```python
# tabs/tab2_gap_analysis.py
"""Tab 2: Gap Analysis."""
import streamlit as st

def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    st.info("Gap Analysis — coming soon")
```

```python
# tabs/tab3_deep_dive.py
"""Tab 3: Bibliometric Deep Dive."""
import streamlit as st

def render(scival_data, selected_universities, selected_faculty):
    st.info("Bibliometric Deep Dive — coming soon")
```

```python
# tabs/tab4_simulator.py
"""Tab 4: Simulator."""
import streamlit as st

def render(scival_data, weights, selected_universities, selected_faculty):
    st.info("Simulator — coming soon")
```

```python
# tabs/tab5_benchmarking.py
"""Tab 5: Peer Benchmarking."""
import streamlit as st

def render(qs_data, scival_data, selected_universities, selected_faculty):
    st.info("Peer Benchmarking — coming soon")
```

- [ ] **Step 3: Verify app launches**

```bash
streamlit run app.py --server.headless true
```

Expected: App starts without errors, sidebar renders with filters, all 5 tabs show placeholder messages. (Stop with Ctrl+C after confirming.)

- [ ] **Step 4: Commit**

```bash
git add app.py tabs/
git commit -m "feat: app shell with sidebar filters and 5-tab navigation"
```

---

### Task 9: Tab 1 — Score Decomposition

**Files:**
- Modify: `tabs/tab1_decomposition.py`

- [ ] **Step 1: Implement Score Decomposition tab**

```python
# tabs/tab1_decomposition.py
"""Tab 1: Score Decomposition (Tier 1 — Subject level)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.constants import (
    UNIVERSITY_SHORT_NAMES,
    UNIVERSITY_COLORS,
    INDICATOR_NAMES,
    INDICATOR_COLORS,
)
from src.weights import get_subject_weights, calculate_weighted_contributions
from src.insights import decomposition_insight
from src.data_loader import filter_target_universities


def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    if selected_subject == "(no subjects available)":
        st.warning("No subjects available for this faculty area.")
        return

    # Filter data for selected subject, year, and universities
    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
        & (qs_data["institution"].isin(selected_universities))
    )
    df = qs_data[mask].copy()

    if df.empty:
        st.warning(f"No data for {selected_subject} ({selected_year}) for selected universities.")
        return

    # Get weights for this subject
    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights defined for {selected_subject}. Check weights.json.")
        return

    # Calculate weighted contributions per university
    contributions = {}
    for _, row in df.iterrows():
        uni_full = row["institution"]
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        scores = {ind: row.get(ind, 0) for ind in ["AR", "ER", "CpP", "HI", "IRN"]}
        # Replace NaN with 0
        scores = {k: (v if pd.notna(v) else 0) for k, v in scores.items()}
        contributions[uni_short] = calculate_weighted_contributions(scores, subject_weights)

    # Headline insight
    st.markdown(f"**{decomposition_insight(contributions, selected_subject)}**")

    # Stacked horizontal bar chart
    fig = go.Figure()
    universities = sorted(contributions.keys())
    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    for indicator in indicators_in_use:
        values = [contributions[uni].get(indicator, 0) for uni in universities]
        fig.add_trace(go.Bar(
            y=universities,
            x=values,
            name=INDICATOR_NAMES.get(indicator, indicator),
            orientation="h",
            marker_color=INDICATOR_COLORS.get(indicator, "#999"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"{INDICATOR_NAMES.get(indicator, indicator)}: "
                "%{x:.1f} weighted pts<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        title=f"Score Decomposition — {selected_subject} ({selected_year})",
        xaxis_title="Weighted Score Contribution",
        yaxis_title="",
        legend_title="Indicator",
        height=max(300, len(universities) * 60 + 100),
        margin=dict(l=10, r=10, t=50, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Weight formula display
    weight_parts = [
        f"{INDICATOR_NAMES.get(k, k)} {v}%"
        for k, v in subject_weights.items()
    ]
    st.caption(f"**{selected_subject} weights:** {' | '.join(weight_parts)}")

    # Collapsible data table
    with st.expander("View raw data"):
        table_data = []
        for uni in universities:
            row = {"University": uni}
            for ind in indicators_in_use:
                row[INDICATOR_NAMES.get(ind, ind)] = f"{contributions[uni].get(ind, 0):.1f}"
            row["Total"] = f"{sum(contributions[uni].values()):.1f}"
            table_data.append(row)
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
```

- [ ] **Step 2: Verify in browser**

```bash
streamlit run app.py
```

Expected: Tab 1 shows a stacked horizontal bar chart with indicator contributions per university, a headline insight, the weight formula, and a collapsible data table.

- [ ] **Step 3: Commit**

```bash
git add tabs/tab1_decomposition.py
git commit -m "feat: Tab 1 Score Decomposition with stacked bar chart and headline insight"
```

---

### Task 10: Tab 2 — Gap Analysis

**Files:**
- Modify: `tabs/tab2_gap_analysis.py`

- [ ] **Step 1: Implement Gap Analysis tab**

```python
# tabs/tab2_gap_analysis.py
"""Tab 2: Gap Analysis (Tier 1 — Subject level)."""

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


def render(qs_data, weights, selected_universities, selected_subject, selected_faculty, selected_year):
    if selected_subject == "(no subjects available)":
        st.warning("No subjects available for this faculty area.")
        return

    # Filter data
    mask = (
        (qs_data["subject"] == selected_subject)
        & (qs_data["year"] == selected_year)
        & (qs_data["institution"].isin(selected_universities))
    )
    df = qs_data[mask].copy()

    if df.empty:
        st.warning(f"No data for {selected_subject} ({selected_year}).")
        return

    # Map to short names
    df["short_name"] = df["institution"].map(UNIVERSITY_SHORT_NAMES)

    # Focus university selector
    available_unis = sorted(df["short_name"].dropna().unique().tolist())
    if not available_unis:
        st.warning("No universities available.")
        return

    focus_uni = st.selectbox("Focus university", available_unis, key="gap_focus")

    # Get weights
    try:
        subject_weights = get_subject_weights(weights, selected_subject, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights defined for {selected_subject}.")
        return

    indicators_in_use = [ind for ind in ["AR", "ER", "CpP", "HI", "IRN"] if ind in subject_weights]

    # Get focus university scores
    focus_row = df[df["short_name"] == focus_uni].iloc[0]
    focus_scores = {ind: (focus_row.get(ind, 0) if pd.notna(focus_row.get(ind)) else 0) for ind in indicators_in_use}

    # Calculate peer average (all other selected universities)
    peers_df = df[df["short_name"] != focus_uni]
    if peers_df.empty:
        st.info("Select at least 2 universities to compare.")
        return

    peer_avg = {}
    for ind in indicators_in_use:
        vals = pd.to_numeric(peers_df[ind], errors="coerce").dropna()
        peer_avg[ind] = vals.mean() if len(vals) > 0 else 0

    # Radar chart
    fig = go.Figure()
    labels = [INDICATOR_NAMES.get(ind, ind) for ind in indicators_in_use]
    focus_values = [focus_scores[ind] for ind in indicators_in_use]
    peer_values = [peer_avg[ind] for ind in indicators_in_use]

    # Close the radar polygon
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
        name="SP Peer Average",
        fillcolor="rgba(255, 127, 14, 0.2)",
        line_color="rgba(255, 127, 14, 1)",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=f"Gap Analysis — {focus_uni} vs. São Paulo Peers in {selected_subject}",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Opportunity table
    opportunities = []
    for ind in indicators_in_use:
        gap = peer_avg[ind] - focus_scores[ind]
        weight = subject_weights.get(ind, 0)
        if gap > 0:
            opportunities.append({
                "indicator": ind,
                "Indicator": INDICATOR_NAMES.get(ind, ind),
                "Your Score": f"{focus_scores[ind]:.1f}",
                "Peer Avg": f"{peer_avg[ind]:.1f}",
                "Gap": f"{gap:.1f}",
                "Weight": f"{weight}%",
                "gap_points": gap * weight / 100,
                "Weighted Impact": f"{gap * weight / 100:.1f} pts",
            })

    opportunities.sort(key=lambda x: x["gap_points"], reverse=True)

    # Headline
    st.markdown(f"**{gap_analysis_insight(focus_uni, selected_subject, opportunities)}**")

    if opportunities:
        opp_df = pd.DataFrame(opportunities)[
            ["Indicator", "Your Score", "Peer Avg", "Gap", "Weight", "Weighted Impact"]
        ]
        st.dataframe(opp_df, use_container_width=True, hide_index=True)
    else:
        st.success(f"{focus_uni} leads or matches peers across all indicators!")
```

- [ ] **Step 2: Verify in browser**

```bash
streamlit run app.py
```

Expected: Tab 2 shows a radar chart comparing focus university vs. peer average, plus an opportunity table sorted by weighted impact.

- [ ] **Step 3: Commit**

```bash
git add tabs/tab2_gap_analysis.py
git commit -m "feat: Tab 2 Gap Analysis with radar chart and opportunity ranking"
```

---

### Task 11: Tab 3 — Bibliometric Deep Dive

**Files:**
- Modify: `tabs/tab3_deep_dive.py`

- [ ] **Step 1: Implement Bibliometric Deep Dive tab**

```python
# tabs/tab3_deep_dive.py
"""Tab 3: Bibliometric Deep Dive (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.constants import UNIVERSITY_SHORT_NAMES, UNIVERSITY_COLORS


# Metric display configs per SciVal export type
CITATIONS_METRICS = [
    ("Scholarly Output (QS)", "Scholarly Output"),
    ("Citations (QS)", "Citations"),
    ("Normalized Total Citation Count (QS)", "Normalized Citations"),
]

IRN_METRICS = [
    ("IRN Scholarly Output (QS)", "IRN Scholarly Output"),
    ("Locations (QS)", "Locations"),
    ("Partners (QS)", "Partners"),
    ("International Research Network (IRN) Index (QS)", "IRN Index"),
]


def render(scival_data, selected_universities, selected_faculty):
    if not scival_data:
        st.warning(
            "No SciVal data loaded. Drop SciVal CSV exports into `data/scival/` "
            "and restart the app."
        )
        return

    st.subheader(f"Bibliometric Deep Dive — {selected_faculty}")

    # Collect data for selected universities and faculty area
    uni_data = {}
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            uni_data[uni_short] = scival_data[uni_full]

    if not uni_data:
        st.warning("No SciVal data available for selected universities.")
        return

    # --- Citations per Faculty section ---
    st.markdown("### Citations per Faculty")
    _render_metric_comparison(
        uni_data, selected_faculty, "citations_per_faculty",
        CITATIONS_METRICS, "citation_per_faculty_score", "Citations per Faculty Score"
    )

    # --- IRN section ---
    st.markdown("### International Research Network")
    _render_metric_comparison(
        uni_data, selected_faculty, "irn",
        IRN_METRICS, "irn_score", "IRN Score"
    )


def _render_metric_comparison(
    uni_data, faculty_area, metric_type, metric_configs, score_key, score_label
):
    """Render a grouped bar chart comparing raw SciVal values across universities."""
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
                    "University": uni_short,
                    "Metric": display_name,
                    "Value": float(row[col_name]),
                })

    if not chart_data:
        st.info(f"No {metric_type} data available for {faculty_area}.")
        return

    chart_df = pd.DataFrame(chart_data)
    metrics_list = [m[1] for m in metric_configs]

    # One chart per metric (different scales)
    cols = st.columns(min(len(metrics_list), 3))
    for i, metric_name in enumerate(metrics_list):
        metric_df = chart_df[chart_df["Metric"] == metric_name]
        if metric_df.empty:
            continue

        col = cols[i % len(cols)]
        with col:
            fig = go.Figure()
            for _, row in metric_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[row["University"]],
                    y=[row["Value"]],
                    name=row["University"],
                    marker_color=UNIVERSITY_COLORS.get(row["University"], "#999"),
                    showlegend=False,
                    hovertemplate=f"<b>{row['University']}</b><br>{metric_name}: %{{y:,.0f}}<extra></extra>",
                ))
            fig.update_layout(
                title=metric_name,
                height=300,
                margin=dict(l=10, r=10, t=40, b=30),
                yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Overall scores
    if any(v is not None for v in overall_scores.values()):
        scores_text = " | ".join(
            f"**{uni}**: {score}" for uni, score in overall_scores.items() if score is not None
        )
        st.caption(f"{score_label}: {scores_text}")
```

- [ ] **Step 2: Verify in browser**

```bash
streamlit run app.py
```

Expected: Tab 3 shows grouped bar charts for Citations and IRN raw values across universities, with overall scores displayed as caption.

- [ ] **Step 3: Commit**

```bash
git add tabs/tab3_deep_dive.py
git commit -m "feat: Tab 3 Bibliometric Deep Dive with SciVal raw value comparison"
```

---

### Task 12: Tab 4 — Simulator

**Files:**
- Modify: `tabs/tab4_simulator.py`

- [ ] **Step 1: Implement Simulator tab**

```python
# tabs/tab4_simulator.py
"""Tab 4: Simulator (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES
from src.weights import get_subject_weights
from src.simulator import simulate_score_change


def render(scival_data, weights, selected_universities, selected_faculty):
    st.subheader(f"Score Simulator — {selected_faculty}")

    if not scival_data:
        st.warning("No SciVal data loaded. Drop SciVal CSV exports into `data/scival/`.")
        return

    # Select focus university
    available = []
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            available.append((uni_short, uni_full))

    if not available:
        st.warning("No SciVal data available for selected universities.")
        return

    focus_short = st.selectbox(
        "Focus university",
        [s for s, _ in available],
        key="sim_focus",
    )
    focus_full = next(f for s, f in available if s == focus_short)

    # Get broad-area weights
    try:
        area_weights = get_subject_weights(weights, selected_faculty, faculty_area=selected_faculty)
    except KeyError:
        st.error(f"No weights for {selected_faculty}.")
        return

    # Extract current QS scores from SciVal data (overall scores per metric type)
    uni_metrics = scival_data[focus_full]
    current_scores = {}
    score_mapping = {
        "citations_per_faculty": "CpP",
        "irn": "IRN",
        "h_index": "HI",
    }

    for metric_type, indicator in score_mapping.items():
        if metric_type in uni_metrics and uni_metrics[metric_type]["overall_score"] is not None:
            current_scores[indicator] = uni_metrics[metric_type]["overall_score"]

    if not current_scores:
        st.warning("No score data available from SciVal exports for simulation.")
        return

    st.markdown("Adjust the sliders to simulate score changes at the faculty area level:")

    # Create sliders for available indicators
    adjusted_scores = {}
    cols = st.columns(len(current_scores))
    for i, (indicator, score) in enumerate(current_scores.items()):
        with cols[i]:
            adjusted_scores[indicator] = st.slider(
                INDICATOR_NAMES.get(indicator, indicator),
                min_value=0.0,
                max_value=100.0,
                value=float(score),
                step=0.5,
                key=f"sim_{indicator}",
            )

    # Add unchanged indicators (AR, ER) — we don't have these from SciVal
    # but they contribute to the total. We note this limitation.
    for indicator in area_weights:
        if indicator not in current_scores and indicator not in adjusted_scores:
            current_scores[indicator] = 0
            adjusted_scores[indicator] = 0

    # Calculate simulation
    result = simulate_score_change(current_scores, adjusted_scores, area_weights)

    # Display results
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Bibliometric Score", f"{result['current_total']:.1f}")
    with col2:
        st.metric("Simulated Score", f"{result['simulated_total']:.1f}")
    with col3:
        st.metric("Delta", f"{result['delta']:+.1f}", delta=f"{result['delta']:+.1f}")

    # Per-indicator breakdown
    if result["indicator_deltas"]:
        st.markdown("**Per-indicator impact:**")
        delta_data = []
        for ind, delta in result["indicator_deltas"].items():
            if ind in current_scores:
                delta_data.append({
                    "Indicator": INDICATOR_NAMES.get(ind, ind),
                    "Weight": f"{area_weights.get(ind, 0)}%",
                    "Current Score": f"{current_scores.get(ind, 0):.1f}",
                    "Adjusted Score": f"{adjusted_scores.get(ind, 0):.1f}",
                    "Weighted Impact": f"{delta:+.1f} pts",
                })
        if delta_data:
            st.dataframe(pd.DataFrame(delta_data), use_container_width=True, hide_index=True)

    st.caption(
        "Note: This simulator operates on QS indicator scores at the faculty area level. "
        "Academic Reputation and Employer Reputation (survey-based) are not included "
        "as they cannot be directly influenced through bibliometric improvements."
    )
```

- [ ] **Step 2: Verify in browser**

```bash
streamlit run app.py
```

Expected: Tab 4 shows sliders for available bibliometric indicators, current/simulated/delta metrics, and per-indicator impact table.

- [ ] **Step 3: Commit**

```bash
git add tabs/tab4_simulator.py
git commit -m "feat: Tab 4 Simulator with interactive sliders and score impact"
```

---

### Task 13: Tab 5 — Peer Benchmarking

**Files:**
- Modify: `tabs/tab5_benchmarking.py`

- [ ] **Step 1: Implement Peer Benchmarking tab**

```python
# tabs/tab5_benchmarking.py
"""Tab 5: Peer Benchmarking (Tier 2 — Faculty area level)."""

import streamlit as st
import pandas as pd

from src.constants import UNIVERSITY_SHORT_NAMES, INDICATOR_NAMES
from src.peers import load_manual_peers, find_structural_peers
from src.insights import benchmarking_insight


def render(qs_data, scival_data, selected_universities, selected_faculty):
    st.subheader(f"Peer Benchmarking — {selected_faculty}")

    if not scival_data:
        st.warning("No SciVal data loaded.")
        return

    # Focus university selector
    available = []
    for uni_full in selected_universities:
        uni_short = UNIVERSITY_SHORT_NAMES.get(uni_full, uni_full)
        if uni_full in scival_data:
            available.append((uni_short, uni_full))

    if not available:
        st.warning("No SciVal data available for selected universities.")
        return

    focus_short = st.selectbox(
        "Focus university",
        [s for s, _ in available],
        key="bench_focus",
    )
    focus_full = next(f for s, f in available if s == focus_short)

    # Load manual peers
    manual_peers = load_manual_peers()
    manual_peer_names = manual_peers.get(focus_full, [])

    # Build comparison table
    # Focus university row
    focus_metrics = _extract_faculty_metrics(scival_data.get(focus_full, {}), selected_faculty)
    if not focus_metrics:
        st.warning(f"No SciVal data for {focus_short} in {selected_faculty}.")
        return

    comparison_rows = [{"University": f"**{focus_short}** (focus)", **focus_metrics}]

    # --- Structural peers (auto-matched by scholarly output) ---
    structural_peer_df = _build_structural_peer_pool(scival_data, selected_faculty)
    if not structural_peer_df.empty:
        matched = find_structural_peers(
            focus_university=focus_full,
            faculty_area=selected_faculty,
            all_data=structural_peer_df,
            output_band=0.3,
            max_rank_improvement=20,
            top_n=5,
        )
        for _, peer_row in matched.iterrows():
            peer_name = peer_row["institution"]
            peer_metrics = _extract_faculty_metrics(scival_data.get(peer_name, {}), selected_faculty)
            if peer_metrics:
                display_name = UNIVERSITY_SHORT_NAMES.get(peer_name, peer_name)
                comparison_rows.append({"University": f"{display_name} (structural peer)", **peer_metrics})

    # --- SP peer rows ---
    peer_deltas = {}
    for uni_full_peer in selected_universities:
        if uni_full_peer == focus_full:
            continue
        uni_short_peer = UNIVERSITY_SHORT_NAMES.get(uni_full_peer, uni_full_peer)
        peer_metrics = _extract_faculty_metrics(scival_data.get(uni_full_peer, {}), selected_faculty)
        if peer_metrics:
            comparison_rows.append({"University": uni_short_peer, **peer_metrics})
            # Calculate deltas for insight
            deltas = {}
            for key in peer_metrics:
                if key in focus_metrics and isinstance(peer_metrics[key], (int, float)) and isinstance(focus_metrics[key], (int, float)):
                    deltas[key] = peer_metrics[key] - focus_metrics[key]
            peer_deltas[uni_short_peer] = deltas

    # --- Manual peer rows ---
    for peer_name in manual_peer_names:
        peer_metrics = _extract_faculty_metrics(scival_data.get(peer_name, {}), selected_faculty)
        if peer_metrics:
            comparison_rows.append({"University": f"{peer_name} (manual peer)", **peer_metrics})
            deltas = {}
            for key in peer_metrics:
                if key in focus_metrics and isinstance(peer_metrics[key], (int, float)) and isinstance(focus_metrics[key], (int, float)):
                    deltas[key] = peer_metrics[key] - focus_metrics[key]
            peer_deltas[peer_name] = deltas

    # Insight
    if peer_deltas:
        st.markdown(f"**{benchmarking_insight(focus_short, selected_faculty, peer_deltas)}**")

    # Comparison table
    comp_df = pd.DataFrame(comparison_rows)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Delta table
    if peer_deltas:
        st.markdown("### Gaps vs. Focus University")
        delta_rows = []
        for peer, deltas in peer_deltas.items():
            row = {"Peer": peer}
            for key, val in deltas.items():
                if isinstance(val, (int, float)):
                    row[key] = f"{val:+,.0f}" if abs(val) >= 10 else f"{val:+.1f}"
            delta_rows.append(row)
        if delta_rows:
            delta_df = pd.DataFrame(delta_rows)
            st.dataframe(delta_df, use_container_width=True, hide_index=True)

    st.caption(
        "To add more institutions to the benchmarking pool, "
        "export their SciVal data and drop into `data/scival/`. "
        "To add manual peers, edit `data/peers.csv`."
    )


def _build_structural_peer_pool(scival_data: dict, faculty_area: str) -> pd.DataFrame:
    """Build a DataFrame of all universities with scholarly output for structural peer matching."""
    rows = []
    for uni_name, metrics in scival_data.items():
        if "citations_per_faculty" not in metrics:
            continue
        df = metrics["citations_per_faculty"]["data"]
        area_row = df[df["faculty_area"] == faculty_area]
        if area_row.empty:
            continue
        output_col = "Scholarly Output (QS)"
        if output_col not in area_row.columns:
            continue
        rows.append({
            "institution": uni_name,
            "faculty_area": faculty_area,
            "scholarly_output": float(area_row[output_col].iloc[0]),
            "overall_rank": 0,  # Placeholder — requires QS rank data
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def _extract_faculty_metrics(uni_scival: dict, faculty_area: str) -> dict:
    """Extract key metrics for a given faculty area from a university's SciVal data."""
    if not uni_scival:
        return {}

    result = {}

    # Citations data
    if "citations_per_faculty" in uni_scival:
        df = uni_scival["citations_per_faculty"]["data"]
        row = df[df["faculty_area"] == faculty_area]
        if not row.empty:
            r = row.iloc[0]
            for col in ["Scholarly Output (QS)", "Citations (QS)", "Normalized Total Citation Count (QS)"]:
                if col in r.index and pd.notna(r[col]):
                    result[col] = r[col]

    # IRN data
    if "irn" in uni_scival:
        df = uni_scival["irn"]["data"]
        row = df[df["faculty_area"] == faculty_area]
        if not row.empty:
            r = row.iloc[0]
            for col in ["Locations (QS)", "Partners (QS)", "International Research Network (IRN) Index (QS)"]:
                if col in r.index and pd.notna(r[col]):
                    result[col] = r[col]

    return result
```

- [ ] **Step 2: Verify in browser**

```bash
streamlit run app.py
```

Expected: Tab 5 shows a comparison table with focus university at top, peers below, delta table, and insight callout.

- [ ] **Step 3: Commit**

```bash
git add tabs/tab5_benchmarking.py
git commit -m "feat: Tab 5 Peer Benchmarking with comparison table and gap display"
```

---

### Task 14: Run Full Test Suite and Final Verification

**Files:**
- No new files

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests PASS (17 tests across 4 test files).

- [ ] **Step 2: Verify app runs end-to-end**

```bash
streamlit run app.py --server.headless true
```

Expected: App starts, sidebar loads, all 5 tabs render without errors. (If no data in `data/qs/`, the app shows the "no data" error message cleanly.)

- [ ] **Step 3: Copy sample data for testing (if available)**

```bash
# If QS data exists in Downloads, copy for testing
cp "/Users/administrador/Downloads/2022 Subject Rankings Results (for qs.com).xlsx" data/qs/
# Copy SciVal samples
cp "/Users/administrador/Downloads/QS Subject 2026/QS_WUR_2026_Citations_per_Faculty_Universidade_de_So_Paulo.csv" data/scival/
cp "/Users/administrador/Downloads/QS Subject 2026/QS_WUR_2026_International_Research_Network_Index_Universidade_de_So_Paulo.csv" data/scival/
```

- [ ] **Step 4: Verify with real data**

```bash
streamlit run app.py
```

Expected: Dashboard loads with real QS subjects in sidebar, charts render with actual university data, SciVal deep dive shows USP bibliometric data.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete QS Subject Rankings dashboard with all 5 tabs"
```
