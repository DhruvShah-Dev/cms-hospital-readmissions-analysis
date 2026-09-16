from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

HRRP_PATH = RAW / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
HOSPITAL_PATH = RAW / "Hospital_General_Information.csv"

HRRP_CLEAN_PATH = PROCESSED / "hrrp_clean.csv"
HOSPITAL_CLEAN_PATH = PROCESSED / "hospital_general_info_clean.csv"
ANALYTIC_PATH = PROCESSED / "hospital_readmissions_analytic.csv"
CLEANING_REPORT_PATH = REPORTS / "02_cleaning_report.md"

NULL_TOKENS = {"", "Not Available", "Not Applicable", "Too Few to Report"}

CONDITION_LABELS = {
    "READM-30-AMI-HRRP": "Heart Attack",
    "READM-30-CABG-HRRP": "CABG",
    "READM-30-COPD-HRRP": "COPD",
    "READM-30-HF-HRRP": "Heart Failure",
    "READM-30-HIP-KNEE-HRRP": "Hip/Knee Replacement",
    "READM-30-PN-HRRP": "Pneumonia",
}

CONDITION_SHORT = {
    "READM-30-AMI-HRRP": "AMI",
    "READM-30-CABG-HRRP": "CABG",
    "READM-30-COPD-HRRP": "COPD",
    "READM-30-HF-HRRP": "HF",
    "READM-30-HIP-KNEE-HRRP": "Hip/Knee",
    "READM-30-PN-HRRP": "Pneumonia",
}

HOSPITAL_REGION_BY_STATE = {
    "CT": "Northeast",
    "ME": "Northeast",
    "MA": "Northeast",
    "NH": "Northeast",
    "RI": "Northeast",
    "VT": "Northeast",
    "NJ": "Northeast",
    "NY": "Northeast",
    "PA": "Northeast",
    "IL": "Midwest",
    "IN": "Midwest",
    "MI": "Midwest",
    "OH": "Midwest",
    "WI": "Midwest",
    "IA": "Midwest",
    "KS": "Midwest",
    "MN": "Midwest",
    "MO": "Midwest",
    "NE": "Midwest",
    "ND": "Midwest",
    "SD": "Midwest",
    "DE": "South",
    "FL": "South",
    "GA": "South",
    "MD": "South",
    "NC": "South",
    "SC": "South",
    "VA": "South",
    "DC": "South",
    "WV": "South",
    "AL": "South",
    "KY": "South",
    "MS": "South",
    "TN": "South",
    "AR": "South",
    "LA": "South",
    "OK": "South",
    "TX": "South",
    "AZ": "West",
    "CO": "West",
    "ID": "West",
    "MT": "West",
    "NV": "West",
    "NM": "West",
    "UT": "West",
    "WY": "West",
    "AK": "West",
    "CA": "West",
    "HI": "West",
    "OR": "West",
    "WA": "West",
}


def read_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=True)


def snake_case(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("__", "_")
    )


def strip_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def normalize_nullable_text(series: pd.Series) -> pd.Series:
    text = strip_text(series)
    return text.mask(text.isin(NULL_TOKENS))


def to_number(series: pd.Series) -> pd.Series:
    text = normalize_nullable_text(series)
    return pd.to_numeric(text.str.replace(",", "", regex=False), errors="coerce")


def to_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(normalize_nullable_text(series), errors="coerce", format="%m/%d/%Y")


def performance_category(err: pd.Series) -> pd.Series:
    return pd.cut(
        err,
        bins=[float("-inf"), 0.95, 1.0, 1.05, float("inf")],
        labels=[
            "Strong Performer",
            "Above Expected Performance",
            "Moderate Concern",
            "High Concern",
        ],
        right=False,
    ).astype("string")


def priority_category(opportunity_score: pd.Series) -> pd.Series:
    score = pd.to_numeric(opportunity_score, errors="coerce")
    category = pd.Series(pd.NA, index=score.index, dtype="string")
    category.loc[score.le(0).fillna(False)] = "No Excess Opportunity"
    category.loc[(score.gt(0) & score.lt(50)).fillna(False)] = "Monitor"
    category.loc[(score.ge(50) & score.lt(150)).fillna(False)] = "High"
    category.loc[score.ge(150).fillna(False)] = "Critical"
    return category


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


def clean_hrrp(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns={col: snake_case(col) for col in raw.columns}).copy()

    text_columns = ["facility_name", "facility_id", "state", "measure_name", "footnote"]
    for col in text_columns:
        df[col] = normalize_nullable_text(df[col])

    df["number_of_discharges"] = to_number(df["number_of_discharges"])
    df["excess_readmission_ratio"] = to_number(df["excess_readmission_ratio"])
    df["predicted_readmission_rate"] = to_number(df["predicted_readmission_rate"])
    df["expected_readmission_rate"] = to_number(df["expected_readmission_rate"])
    df["number_of_readmissions"] = to_number(df["number_of_readmissions"])
    df["start_date"] = to_date(df["start_date"])
    df["end_date"] = to_date(df["end_date"])

    df["condition"] = df["measure_name"].map(CONDITION_LABELS).astype("string")
    df["condition_short"] = df["measure_name"].map(CONDITION_SHORT).astype("string")
    df["measurement_year"] = df["end_date"].dt.year.astype("Int64")

    df["readmission_gap"] = df["predicted_readmission_rate"] - df["expected_readmission_rate"]
    df["readmission_gap_pct"] = (
        df["readmission_gap"] / df["expected_readmission_rate"]
    ) * 100
    df["excess_readmission_flag"] = df["excess_readmission_ratio"] > 1
    df["high_concern_flag"] = df["excess_readmission_ratio"] >= 1.05
    df["performance_category"] = performance_category(df["excess_readmission_ratio"])
    df["opportunity_score"] = (
        (df["excess_readmission_ratio"] - 1) * df["number_of_discharges"]
    ).where(
        df["excess_readmission_ratio"].notna() & df["number_of_discharges"].notna()
    )
    df["positive_opportunity_score"] = df["opportunity_score"].clip(lower=0)
    df["priority_category"] = priority_category(df["opportunity_score"])
    df["has_numeric_volume"] = df["number_of_discharges"].notna()
    df["has_numeric_err"] = df["excess_readmission_ratio"].notna()

    return df


def clean_hospital_info(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns={col: snake_case(col) for col in raw.columns}).copy()

    for col in df.columns:
        df[col] = normalize_nullable_text(df[col])

    numeric_columns = [
        "zip_code",
        "hospital_overall_rating",
        "mort_group_measure_count",
        "count_of_facility_mort_measures",
        "count_of_mort_measures_better",
        "count_of_mort_measures_no_different",
        "count_of_mort_measures_worse",
        "safety_group_measure_count",
        "count_of_facility_safety_measures",
        "count_of_safety_measures_better",
        "count_of_safety_measures_no_different",
        "count_of_safety_measures_worse",
        "readm_group_measure_count",
        "count_of_facility_readm_measures",
        "count_of_readm_measures_better",
        "count_of_readm_measures_no_different",
        "count_of_readm_measures_worse",
        "pt_exp_group_measure_count",
        "count_of_facility_pt_exp_measures",
        "te_group_measure_count",
        "count_of_facility_te_measures",
    ]

    for col in numeric_columns:
        df[col] = to_number(raw[col.replace("_", " ").title()]) if col not in df else to_number(df[col])

    df["zip_code"] = normalize_nullable_text(raw["ZIP Code"])
    df["overall_rating_group"] = pd.cut(
        df["hospital_overall_rating"],
        bins=[0, 2, 4, 5],
        labels=["Low Rating", "Middle Rating", "High Rating"],
        include_lowest=True,
    ).astype("string")
    df["region"] = df["state"].map(HOSPITAL_REGION_BY_STATE).astype("string")
    df["emergency_services_flag"] = df["emergency_services"].eq("Yes")
    df["birthing_friendly_flag"] = df[
        "meets_criteria_for_birthing_friendly_designation"
    ].eq("Y")

    return df


def build_report(
    hrrp_raw: pd.DataFrame,
    hospital_raw: pd.DataFrame,
    hrrp_clean: pd.DataFrame,
    hospital_clean: pd.DataFrame,
    analytic: pd.DataFrame,
) -> str:
    unmatched = analytic["hospital_type"].isna()
    positive_opportunity = analytic["positive_opportunity_score"].fillna(0)

    output_summary = pd.DataFrame(
        [
            {
                "output": str(HRRP_CLEAN_PATH.relative_to(ROOT)),
                "rows": len(hrrp_clean),
                "columns": len(hrrp_clean.columns),
            },
            {
                "output": str(HOSPITAL_CLEAN_PATH.relative_to(ROOT)),
                "rows": len(hospital_clean),
                "columns": len(hospital_clean.columns),
            },
            {
                "output": str(ANALYTIC_PATH.relative_to(ROOT)),
                "rows": len(analytic),
                "columns": len(analytic.columns),
            },
        ]
    )

    condition_summary = (
        analytic.groupby("condition", dropna=False)
        .agg(
            rows=("facility_id", "size"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_excess=("excess_readmission_flag", "mean"),
            discharges=("number_of_discharges", "sum"),
            readmissions=("number_of_readmissions", "sum"),
            positive_opportunity=("positive_opportunity_score", "sum"),
        )
        .reset_index()
        .sort_values("positive_opportunity", ascending=False)
    )
    for col in ["avg_err", "pct_excess", "positive_opportunity"]:
        condition_summary[col] = condition_summary[col].round(4)

    priority_summary = (
        analytic["priority_category"]
        .fillna("Missing ERR or Volume")
        .value_counts(dropna=False)
        .rename_axis("priority_category")
        .reset_index(name="rows")
    )

    top_opportunity = (
        analytic[
            [
                "facility_id",
                "facility_name",
                "state",
                "condition",
                "excess_readmission_ratio",
                "number_of_discharges",
                "positive_opportunity_score",
                "hospital_type",
                "hospital_ownership",
                "hospital_overall_rating",
            ]
        ]
        .dropna(subset=["positive_opportunity_score"])
        .sort_values("positive_opportunity_score", ascending=False)
        .head(15)
        .copy()
    )
    top_opportunity["excess_readmission_ratio"] = top_opportunity[
        "excess_readmission_ratio"
    ].round(4)
    top_opportunity["positive_opportunity_score"] = top_opportunity[
        "positive_opportunity_score"
    ].round(1)

    lines = [
        "# CMS Hospital Readmissions Cleaning Report",
        "",
        "## Inputs",
        "",
        f"- HRRP raw rows: {len(hrrp_raw):,}",
        f"- Hospital information raw rows: {len(hospital_raw):,}",
        "- Raw files were not modified.",
        "",
        "## Outputs",
        "",
        markdown_table(output_summary),
        "",
        "## Cleaning Rules Applied",
        "",
        "- Standardized column names to snake_case.",
        "- Trimmed text fields and converted CMS placeholders to missing values in processed outputs.",
        "- Converted readmission ratios, rates, counts, discharges, ratings, and quality-count fields to numeric values.",
        "- Parsed HRRP measurement dates as dates.",
        "- Added readable condition labels and condition short names.",
        "- Added U.S. Census-style region labels from state abbreviations.",
        "- Created readmission gap, gap percent, excess-readmission flags, performance categories, and opportunity scores.",
        "- Left joined hospital attributes onto HRRP rows by `facility_id`.",
        "",
        "## Validation Checks",
        "",
        f"- HRRP row count preserved: {len(hrrp_raw):,} raw rows to {len(hrrp_clean):,} clean rows.",
        f"- Hospital row count preserved: {len(hospital_raw):,} raw rows to {len(hospital_clean):,} clean rows.",
        f"- Analytic row count preserved after left join: {len(analytic):,} rows.",
        f"- Analytic rows without hospital attributes: {int(unmatched.sum()):,}.",
        f"- Numeric ERR rows: {int(analytic['excess_readmission_ratio'].notna().sum()):,}.",
        f"- Numeric volume rows: {int(analytic['number_of_discharges'].notna().sum()):,}.",
        f"- Positive opportunity score total: {positive_opportunity.sum():,.1f}.",
        "",
        "## Condition Summary",
        "",
        markdown_table(condition_summary),
        "",
        "## Priority Category Summary",
        "",
        markdown_table(priority_summary),
        "",
        "## Top Initial Opportunity Rows",
        "",
        markdown_table(top_opportunity),
        "",
        "## Notes",
        "",
        "- The opportunity score is directional and should be validated before being used as a formal intervention priority metric.",
        "- Suppressed CMS values remain available as missing values in the processed tables; footnotes should be consulted where suppression matters.",
        "- The 120 analytic rows without hospital attributes should remain in national and condition analysis but be excluded or flagged for ownership, rating, and hospital-type cuts.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    hrrp_raw = read_raw(HRRP_PATH)
    hospital_raw = read_raw(HOSPITAL_PATH)

    hrrp_clean = clean_hrrp(hrrp_raw)
    hospital_clean = clean_hospital_info(hospital_raw)

    analytic = hrrp_clean.merge(
        hospital_clean,
        on="facility_id",
        how="left",
        suffixes=("", "_hospital"),
        validate="many_to_one",
    )

    hrrp_clean.to_csv(HRRP_CLEAN_PATH, index=False)
    hospital_clean.to_csv(HOSPITAL_CLEAN_PATH, index=False)
    analytic.to_csv(ANALYTIC_PATH, index=False)
    CLEANING_REPORT_PATH.write_text(
        build_report(hrrp_raw, hospital_raw, hrrp_clean, hospital_clean, analytic),
        encoding="utf-8",
    )

    print(f"Wrote {HRRP_CLEAN_PATH}")
    print(f"Wrote {HOSPITAL_CLEAN_PATH}")
    print(f"Wrote {ANALYTIC_PATH}")
    print(f"Wrote {CLEANING_REPORT_PATH}")


if __name__ == "__main__":
    main()
