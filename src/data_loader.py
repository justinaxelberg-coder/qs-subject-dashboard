"""Load and validate QS Subject Rankings and SciVal data."""

import io
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.constants import TARGET_UNIVERSITIES, QS_COLUMN_TO_INDICATOR


def detect_qs_years(qs_dir: str = "data/qs") -> list[int]:
    years = set()
    for f in Path(qs_dir).glob("*.xlsx"):
        matches = re.findall(r"20\d{2}", f.stem)
        for m in matches:
            year = int(m)
            if 2015 <= year <= 2030:
                years.add(year)
    return sorted(years, reverse=True)


def parse_qs_subject_sheet(filepath: str, sheet_name: str, year: int, faculty_area_map: dict = None) -> pd.DataFrame:
    raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    # Determine faculty area from lookup map or sheet row 1
    faculty_area = None
    if faculty_area_map and sheet_name in faculty_area_map:
        faculty_area = faculty_area_map[sheet_name]

    # Find header row: look for INSTITUTION/Institution and SCORE/Score
    header_row_idx = None
    for idx, row in raw.iterrows():
        vals = [str(v).strip().upper() for v in row.dropna().values]
        if "INSTITUTION" in vals and ("SCORE" in vals or "ACADEMIC" in vals):
            header_row_idx = idx
            break
    if header_row_idx is None:
        return pd.DataFrame()

    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row_idx)
    # Normalize column names to handle case differences
    col_map = {c: c.strip() for c in df.columns}
    df = df.rename(columns=col_map)

    # Find institution column (case-insensitive)
    inst_col = next((c for c in df.columns if c.upper() == "INSTITUTION"), None)
    if inst_col is None:
        return pd.DataFrame()
    df = df.dropna(subset=[inst_col])

    # Find country column
    country_col = next((c for c in df.columns if "COUNTRY" in c.upper()), None)

    # Find score column
    score_col = next((c for c in df.columns if c.upper() == "SCORE"), None)

    n_rows = len(df)
    result = pd.DataFrame()
    result["institution"] = df[inst_col].astype(str).str.strip().values
    result["year"] = [year] * n_rows
    result["subject"] = [sheet_name] * n_rows
    result["faculty_area"] = [faculty_area] * n_rows
    result["country"] = df[country_col].astype(str).str.strip().values if country_col else [None] * n_rows

    # Rank from first column
    rank_col = df.columns[0]
    result["rank"] = pd.to_numeric(
        df[rank_col].astype(str).str.strip().str.replace(r"[^\d]", "", regex=True),
        errors="coerce",
    )

    # Overall score
    if score_col:
        result["overall_score"] = pd.to_numeric(df[score_col], errors="coerce")
    else:
        result["overall_score"] = float("nan")

    # Map indicator columns — handle both old (Academic, Citations, H, International)
    # and new (ACADEMIC, CITATIONS, H, IRN) formats, skipping RANK columns
    indicator_col_patterns = {
        "AR": ["ACADEMIC"],
        "ER": ["EMPLOYER"],
        "CpP": ["CITATIONS"],
        "HI": ["H"],
        "IRN": ["IRN", "INTERNATIONAL"],
    }
    for indicator_code, patterns in indicator_col_patterns.items():
        matched_col = None
        for col in df.columns:
            col_upper = col.upper().strip()
            # Skip rank columns
            if "RANK" in col_upper:
                continue
            for pattern in patterns:
                if col_upper == pattern:
                    matched_col = col
                    break
            if matched_col:
                break
        if matched_col:
            result[indicator_code] = pd.to_numeric(df[matched_col], errors="coerce")
        else:
            result[indicator_code] = float("nan")

    return result


def _build_faculty_area_map(filepath: str, sheet_names: list) -> dict:
    """Build a mapping from sheet name to faculty area using the Index sheet or FACULTY_AREAS constant."""
    from src.constants import FACULTY_AREAS

    faculty_area_map = {}
    # Faculty area sheets map to themselves
    for fa in FACULTY_AREAS:
        for sn in sheet_names:
            if sn.strip() == fa.strip():
                faculty_area_map[sn] = fa

    # Try to read Index sheet for subject-to-area mapping
    try:
        raw = pd.read_excel(filepath, sheet_name="Index", header=None)
        # Index sheet has faculty areas in row 4, subjects below
        # Find the row with faculty area headers
        for idx, row in raw.iterrows():
            vals = [str(v).strip() if pd.notna(v) else "" for v in row.values]
            area_cols = {}
            for col_idx, val in enumerate(vals):
                if val in FACULTY_AREAS:
                    area_cols[col_idx] = val
            if area_cols:
                # Read subjects below each faculty area column
                for sub_idx in range(idx + 1, len(raw)):
                    sub_row = raw.iloc[sub_idx]
                    for col_idx, area in area_cols.items():
                        if col_idx < len(sub_row) and pd.notna(sub_row.iloc[col_idx]):
                            subject = str(sub_row.iloc[col_idx]).strip()
                            if subject:
                                # Match truncated sheet names
                                for sn in sheet_names:
                                    if subject.startswith(sn[:25]) or sn.startswith(subject[:25]):
                                        faculty_area_map[sn] = area
                                    elif subject.replace("&", "&").startswith(sn.replace("&", "&")[:25]):
                                        faculty_area_map[sn] = area
                break
    except Exception:
        pass

    return faculty_area_map


def load_qs_data(qs_dir: str = "data/qs") -> pd.DataFrame:
    all_frames = []
    skip_sheets = {"Main", "Index", "methodology"}
    for filepath in Path(qs_dir).glob("*.xlsx"):
        years = re.findall(r"20\d{2}", filepath.stem)
        if not years:
            continue
        year = int(years[0])
        import openpyxl
        wb = openpyxl.load_workbook(str(filepath), read_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        faculty_area_map = _build_faculty_area_map(str(filepath), sheet_names)

        for sheet_name in sheet_names:
            if sheet_name in skip_sheets:
                continue
            try:
                df = parse_qs_subject_sheet(str(filepath), sheet_name, year, faculty_area_map)
                if len(df) > 0:
                    all_frames.append(df)
            except Exception as e:
                print(f"Warning: could not parse sheet '{sheet_name}' from {filepath.name}: {e}")
    if not all_frames:
        return pd.DataFrame()
    return pd.concat(all_frames, ignore_index=True)


def filter_target_universities(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "institution" not in df.columns:
        return df
    mask = df["institution"].isin(TARGET_UNIVERSITIES)
    return df[mask].copy()


def get_available_subjects(df: pd.DataFrame, faculty_area: Optional[str] = None) -> list[str]:
    filtered = filter_target_universities(df)
    if faculty_area:
        filtered = filtered[filtered["faculty_area"] == faculty_area]
    return sorted(filtered["subject"].dropna().unique().tolist())


def parse_scival_csv(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    university = None
    metric_type = None
    overall_score = None
    data_start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Entity,"):
            university = line.split(",", 1)[1].strip().strip('"')
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
        if "Score," in line and any(
            keyword in line
            for keyword in ["Citation per Faculty Score", "IRN) Score", "H-Index Score", "H-index Score"]
        ):
            try:
                score_str = line.strip().rsplit(",", 1)[1].strip()
                overall_score = float(score_str)
            except (ValueError, IndexError):
                pass
        if '"QS metrics"' in line or "QS metrics" in line:
            data_start_idx = i
            break
    if data_start_idx is None:
        return {"university": university, "metric_type": metric_type, "overall_score": overall_score, "data": pd.DataFrame()}
    data_text = "".join(lines[data_start_idx:])
    df = pd.read_csv(io.StringIO(data_text))
    df = df.rename(columns={df.columns[0]: "faculty_area"})
    df = df[~df["faculty_area"].str.contains("Total|Deduplicated", case=False, na=False)].copy()
    df.columns = [c.strip().strip('"') for c in df.columns]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.reset_index(drop=True)
    return {"university": university, "metric_type": metric_type, "overall_score": overall_score, "data": df}


def load_scival_data(scival_dir: str = "data/scival") -> dict:
    result = {}
    for filepath in Path(scival_dir).glob("*.csv"):
        try:
            parsed = parse_scival_csv(str(filepath))
            uni = parsed["university"]
            metric = parsed["metric_type"]
            if uni and metric:
                if uni not in result:
                    result[uni] = {}
                result[uni][metric] = {"overall_score": parsed["overall_score"], "data": parsed["data"]}
        except Exception as e:
            print(f"Warning: could not parse SciVal file {filepath.name}: {e}")
    return result
