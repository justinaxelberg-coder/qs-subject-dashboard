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
    parse_scival_csv,
    load_scival_data,
)


def test_filter_target_universities(sample_qs_subject_data):
    result = filter_target_universities(sample_qs_subject_data)
    assert len(result) == 3


def test_filter_target_universities_empty():
    df = pd.DataFrame({"institution": ["MIT", "Stanford"], "rank": [1, 2]})
    result = filter_target_universities(df)
    assert len(result) == 0


def test_get_available_subjects(sample_qs_subject_data):
    result = get_available_subjects(sample_qs_subject_data)
    assert "Chemistry" in result


def test_get_available_subjects_by_faculty_area(sample_qs_subject_data):
    result = get_available_subjects(sample_qs_subject_data, faculty_area="Natural Sciences")
    assert "Chemistry" in result
    result_empty = get_available_subjects(sample_qs_subject_data, faculty_area="Arts & Humanities")
    assert len(result_empty) == 0


def test_parse_scival_citations_csv(tmp_path):
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
    assert len(result["data"]) == 5
    assert result["data"]["faculty_area"].iloc[0] == "Arts & Humanities"


def test_parse_scival_irn_csv(tmp_path):
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
