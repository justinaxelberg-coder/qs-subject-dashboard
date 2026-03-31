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
