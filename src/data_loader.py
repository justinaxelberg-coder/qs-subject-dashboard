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


def parse_qs_subject_sheet(filepath: str, sheet_name: str, year: int) -> pd.DataFrame:
    raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
    faculty_area = None
    if len(raw) > 2:
        row2 = raw.iloc[2].dropna().tolist()
        if len(row2) >= 2 and row2[0] == "Faculty Area":
            faculty_area = str(row2[1])
    header_row_idx = None
    for idx, row in raw.iterrows():
        vals = [str(v).strip() for v in row.dropna().values]
        if "Institution" in vals and "Score" in vals:
            header_row_idx = idx
            break
    if header_row_idx is None:
        return pd.DataFrame()
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row_idx)
    df = df.dropna(subset=["Institution"])
    result = pd.DataFrame()
    result["year"] = year
    result["subject"] = sheet_name
    result["faculty_area"] = faculty_area
    result["institution"] = df["Institution"].str.strip().values
    result["country"] = df["Country"].str.strip().values if "Country" in df.columns else None
    rank_col = df.columns[0]
    result["rank"] = pd.to_numeric(
        df[rank_col].astype(str).str.strip().str.replace(r"[^\d]", "", regex=True),
        errors="coerce",
    )
    result["overall_score"] = pd.to_numeric(df["Score"], errors="coerce")
    for col_name, indicator_code in QS_COLUMN_TO_INDICATOR.items():
        if col_name in df.columns:
            result[indicator_code] = pd.to_numeric(df[col_name], errors="coerce")
        else:
            result[indicator_code] = float("nan")
    return result


def load_qs_data(qs_dir: str = "data/qs") -> pd.DataFrame:
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
    if df.empty or "institution" not in df.columns:
        return df
    mask = pd.Series(False, index=df.index)
    for target in TARGET_UNIVERSITIES:
        mask |= df["institution"].str.contains(target[:20], case=False, na=False)
    return df[mask].copy()


def get_available_subjects(df: pd.DataFrame, faculty_area: Optional[str] = None) -> list[str]:
    filtered = filter_target_universities(df)
    if faculty_area:
        filtered = filtered[filtered["faculty_area"] == faculty_area]
    return sorted(filtered["subject"].dropna().unique().tolist())


def parse_scival_csv(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
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
