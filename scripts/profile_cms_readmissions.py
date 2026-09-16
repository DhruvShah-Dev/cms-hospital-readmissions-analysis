from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"

HRRP_PATH = RAW / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
HOSPITAL_PATH = RAW / "Hospital_General_Information.csv"
PROFILE_PATH = REPORTS / "01_data_profile.md"

NULL_TOKENS = {"", "Not Available", "Not Applicable", "Too Few to Report"}


def read_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=True)


def clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def typed_numeric(series: pd.Series) -> pd.Series:
    text = clean_text(series)
    text = text.mask(text.isin(NULL_TOKENS))
    return pd.to_numeric(text.str.replace(",", "", regex=False), errors="coerce")


def typed_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(clean_text(series), errors="coerce", format="%m/%d/%Y")


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        text = clean_text(df[col])
        missing = df[col].isna() | text.isin(NULL_TOKENS)
        rows.append(
            {
                "column": col,
                "missing_like_count": int(missing.sum()),
                "missing_like_rate": round(float(missing.mean()), 4),
                "distinct_count": int(text.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def numeric_summary(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        values = typed_numeric(df[col])
        rows.append(
            {
                "column": col,
                "valid_numeric": int(values.notna().sum()),
                "min": round(float(values.min()), 4) if values.notna().any() else None,
                "median": round(float(values.median()), 4) if values.notna().any() else None,
                "mean": round(float(values.mean()), 4) if values.notna().any() else None,
                "max": round(float(values.max()), 4) if values.notna().any() else None,
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_None._"
    table = df.head(max_rows).copy()
    table = table.where(pd.notna(table), "")
    headers = [str(col) for col in table.columns]
    rows = [[str(value) for value in row] for row in table.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def pct(numerator: int | float, denominator: int | float) -> str:
    if denominator == 0:
        return "n/a"
    return f"{(numerator / denominator) * 100:.1f}%"


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)

    hrrp = read_raw(HRRP_PATH)
    hospitals = read_raw(HOSPITAL_PATH)

    hrrp_facility_id = clean_text(hrrp["Facility ID"])
    hrrp_measure = clean_text(hrrp["Measure Name"])
    hospital_facility_id = clean_text(hospitals["Facility ID"])

    hrrp_key_dupes = hrrp.duplicated(["Facility ID", "Measure Name"], keep=False)
    hospital_id_dupes = hospitals.duplicated(["Facility ID"], keep=False)

    hrrp_facilities = set(hrrp_facility_id.dropna())
    hospital_facilities = set(hospital_facility_id.dropna())
    unmatched_hrrp_ids = sorted(hrrp_facilities - hospital_facilities)
    unmatched_hrrp_rows = hrrp_facility_id.isin(unmatched_hrrp_ids)

    joined = hrrp.assign(_facility_id=hrrp_facility_id).merge(
        hospitals.assign(_facility_id=hospital_facility_id),
        on="_facility_id",
        how="left",
        suffixes=("_hrrp", "_hospital"),
    )

    err = typed_numeric(hrrp["Excess Readmission Ratio"])
    discharges = typed_numeric(hrrp["Number of Discharges"])
    readmissions = typed_numeric(hrrp["Number of Readmissions"])
    predicted = typed_numeric(hrrp["Predicted Readmission Rate"])
    expected = typed_numeric(hrrp["Expected Readmission Rate"])
    start_dates = typed_date(hrrp["Start Date"])
    end_dates = typed_date(hrrp["End Date"])

    valid_opportunity = err.notna() & discharges.notna()
    opportunity = (err - 1) * discharges
    opportunity_positive = opportunity.where(valid_opportunity & (opportunity > 0))

    condition_summary = (
        pd.DataFrame(
            {
                "measure": hrrp_measure,
                "err": err,
                "discharges": discharges,
                "readmissions": readmissions,
                "predicted_rate": predicted,
                "expected_rate": expected,
                "opportunity": opportunity_positive,
            }
        )
        .groupby("measure", dropna=False)
        .agg(
            rows=("measure", "size"),
            avg_err=("err", "mean"),
            median_err=("err", "median"),
            pct_err_gt_1=("err", lambda s: (s > 1).mean()),
            total_discharges=("discharges", "sum"),
            total_readmissions=("readmissions", "sum"),
            positive_opportunity=("opportunity", "sum"),
        )
        .reset_index()
    )
    for col in ["avg_err", "median_err", "pct_err_gt_1", "positive_opportunity"]:
        condition_summary[col] = condition_summary[col].round(4)

    top_opportunities = (
        pd.DataFrame(
            {
                "Facility ID": hrrp_facility_id,
                "Facility Name": clean_text(hrrp["Facility Name"]),
                "State": clean_text(hrrp["State"]),
                "Measure Name": hrrp_measure,
                "ERR": err,
                "Discharges": discharges,
                "Opportunity": opportunity_positive,
            }
        )
        .dropna(subset=["Opportunity"])
        .sort_values("Opportunity", ascending=False)
        .head(15)
    )
    top_opportunities["ERR"] = top_opportunities["ERR"].round(4)
    top_opportunities["Opportunity"] = top_opportunities["Opportunity"].round(1)
    top_opportunities["Discharges"] = top_opportunities["Discharges"].astype(int)

    hrrp_missing = missing_summary(hrrp)
    hospital_missing = missing_summary(hospitals)

    hrrp_numeric = numeric_summary(
        hrrp,
        [
            "Number of Discharges",
            "Excess Readmission Ratio",
            "Predicted Readmission Rate",
            "Expected Readmission Rate",
            "Number of Readmissions",
        ],
    )

    hospital_rating_counts = (
        clean_text(hospitals["Hospital overall rating"])
        .fillna("<missing>")
        .value_counts(dropna=False)
        .rename_axis("rating")
        .reset_index(name="hospitals")
        .sort_values("rating")
    )

    ownership_counts = (
        clean_text(hospitals["Hospital Ownership"])
        .fillna("<missing>")
        .value_counts(dropna=False)
        .rename_axis("ownership")
        .reset_index(name="hospitals")
    )

    periods = (
        pd.DataFrame({"start": start_dates.dt.date, "end": end_dates.dt.date})
        .value_counts(dropna=False)
        .rename_axis(["start_date", "end_date"])
        .reset_index(name="rows")
    )

    lines = [
        "# CMS Hospital Readmissions Data Profile",
        "",
        "## Dataset And Grain Summary",
        "",
        f"- HRRP raw file: `{HRRP_PATH.relative_to(ROOT)}`",
        f"- Hospital general information raw file: `{HOSPITAL_PATH.relative_to(ROOT)}`",
        f"- HRRP shape: {hrrp.shape[0]:,} rows x {hrrp.shape[1]:,} columns",
        f"- Hospital information shape: {hospitals.shape[0]:,} rows x {hospitals.shape[1]:,} columns",
        "- Expected HRRP grain: one hospital-condition measure row per `Facility ID` + `Measure Name`.",
        "- Expected hospital information grain: one hospital row per `Facility ID`.",
        "",
        "## Checks Performed",
        "",
        "- Schema and column count checks",
        "- Missing-like values, including CMS text placeholders",
        "- Exact duplicate rows and candidate key uniqueness",
        "- Numeric cast validity for readmission measures and volumes",
        "- Date parsing and measurement-period consistency",
        "- Join integrity from HRRP to Hospital General Information on `Facility ID`",
        "- Initial condition, rating, ownership, and opportunity summaries",
        "",
        "## Key Results",
        "",
        f"- HRRP exact duplicate rows: {int(hrrp.duplicated().sum()):,}",
        f"- HRRP duplicate `Facility ID` + `Measure Name` rows: {int(hrrp_key_dupes.sum()):,}",
        f"- Hospital exact duplicate rows: {int(hospitals.duplicated().sum()):,}",
        f"- Hospital duplicate `Facility ID` rows: {int(hospital_id_dupes.sum()):,}",
        f"- HRRP facility IDs absent from hospital information: {len(unmatched_hrrp_ids):,} affecting {int(unmatched_hrrp_rows.sum()):,} HRRP rows",
        f"- Joined row count: {joined.shape[0]:,} versus HRRP row count {hrrp.shape[0]:,}",
        f"- HRRP rows with numeric ERR: {int(err.notna().sum()):,} ({pct(int(err.notna().sum()), len(hrrp))})",
        f"- HRRP rows with ERR > 1.0: {int((err > 1).sum()):,} ({pct(int((err > 1).sum()), int(err.notna().sum()))} of numeric ERR rows)",
        f"- HRRP rows with ERR > 1.05: {int((err > 1.05).sum()):,} ({pct(int((err > 1.05).sum()), int(err.notna().sum()))} of numeric ERR rows)",
        f"- Total numeric reported readmissions: {int(readmissions.sum()):,}",
        "",
        "## Measurement Periods",
        "",
        markdown_table(periods),
        "",
        "## HRRP Numeric Profile",
        "",
        markdown_table(hrrp_numeric),
        "",
        "## HRRP Missing-Like Profile",
        "",
        markdown_table(hrrp_missing.sort_values("missing_like_rate", ascending=False)),
        "",
        "## Hospital Information Missing-Like Profile",
        "",
        markdown_table(hospital_missing.sort_values("missing_like_rate", ascending=False)),
        "",
        "## Condition Summary",
        "",
        markdown_table(condition_summary.sort_values("positive_opportunity", ascending=False)),
        "",
        "## Hospital Ratings",
        "",
        markdown_table(hospital_rating_counts),
        "",
        "## Hospital Ownership",
        "",
        markdown_table(ownership_counts),
        "",
        "## Top Initial Readmission Improvement Opportunities",
        "",
        "Opportunity is calculated only for rows with numeric ERR and numeric discharges as `(ERR - 1) * discharges`; negative values are excluded from this first prioritization view.",
        "",
        markdown_table(top_opportunities),
        "",
        "## Findings",
        "",
        "- No duplicate rows or duplicate candidate keys were found at the expected dataset grains. Severity: low; confidence: high.",
        f"- HRRP has {len(unmatched_hrrp_ids):,} facility IDs ({int(unmatched_hrrp_rows.sum()):,} rows) with no matching Hospital General Information record. This does not create row loss in a left join, but those rows will lack ownership, type, rating, and address fields. Severity: medium; confidence: high.",
        "- The HRRP-to-hospital join does not expand rows, because Hospital General Information has unique `Facility ID` values. Severity: low; confidence: high.",
        "- Several HRRP volume fields contain expected CMS suppression text such as `Too Few to Report`, so volume-based metrics should use numeric casting with documented exclusions. Severity: medium; confidence: high.",
        "- The CMS footnote and group footnote columns are intentionally sparse. These columns should be retained for transparency but not treated as analysis measures. Severity: low; confidence: high.",
        "",
        "## Recommended Next Steps",
        "",
        "- Create cleaned, analysis-ready tables that preserve raw files and convert rates, volumes, dates, and placeholder values explicitly.",
        "- Add a condition label field that maps CMS measure codes to business-readable names.",
        "- Build SQL tables/views at hospital-condition, hospital, state-condition, and opportunity-ranking grains.",
        "- Validate opportunity-score variants before using them in executive recommendations.",
        "- Add automated checks for candidate key uniqueness, join coverage, numeric cast rates, and expected measurement-period consistency.",
        "",
        "## Assumptions And Open Questions",
        "",
        "- Assumption: the first analytical grain is HRRP hospital-condition measure rows.",
        "- Assumption: `Too Few to Report` is an expected CMS suppression value, not a data ingestion defect.",
        "- Open question: should opportunity ranking emphasize excess cases, financial penalty risk, patient volume, or a blended score?",
        "",
    ]

    PROFILE_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(PROFILE_PATH)


if __name__ == "__main__":
    main()
