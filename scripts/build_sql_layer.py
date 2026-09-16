from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SQL = ROOT / "sql"
REPORTS = ROOT / "reports"

DB_PATH = PROCESSED / "readmissions.db"
SQL_REPORT_PATH = REPORTS / "03_sql_analysis_report.md"

TABLES = {
    "hrrp_clean": PROCESSED / "hrrp_clean.csv",
    "hospital_general_info_clean": PROCESSED / "hospital_general_info_clean.csv",
    "hospital_readmissions_analytic": PROCESSED / "hospital_readmissions_analytic.csv",
}

SQL_FILES = [
    SQL / "01_schema.sql",
    SQL / "02_analysis_views.sql",
]

TEXT_COLUMNS = {
    "hrrp_clean": {"facility_id"},
    "hospital_general_info_clean": {"facility_id", "zip_code"},
    "hospital_readmissions_analytic": {"facility_id", "zip_code"},
}

REPORT_QUERIES = {
    "National Summary": """
        SELECT
            CAST(hrrp_rows AS INTEGER) AS hrrp_rows,
            CAST(hospitals_analyzed AS INTEGER) AS hospitals_analyzed,
            CAST(conditions_analyzed AS INTEGER) AS conditions_analyzed,
            ROUND(avg_err, 4) AS avg_err,
            ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
            ROUND(pct_rows_err_ge_1_05 * 100, 1) AS pct_rows_err_ge_1_05,
            CAST(total_discharges AS INTEGER) AS total_discharges,
            CAST(total_readmissions AS INTEGER) AS total_readmissions,
            ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
        FROM v_national_summary;
    """,
    "Condition Summary": """
        SELECT
            condition,
            hrrp_rows,
            hospitals_analyzed,
            ROUND(avg_err, 4) AS avg_err,
            ROUND(avg_readmission_gap, 4) AS avg_readmission_gap,
            ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
            CAST(total_readmissions AS INTEGER) AS total_readmissions,
            ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
        FROM v_condition_summary
        ORDER BY positive_opportunity_score DESC;
    """,
    "Top States By Opportunity": """
        SELECT
            state,
            hospitals_analyzed,
            ROUND(avg_err, 4) AS avg_err,
            ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
            CAST(total_readmissions AS INTEGER) AS total_readmissions,
            ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
        FROM v_state_summary
        ORDER BY positive_opportunity_score DESC
        LIMIT 15;
    """,
    "Ownership Summary": """
        SELECT
            hospital_ownership,
            hospitals_analyzed,
            ROUND(avg_err, 4) AS avg_err,
            ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
            ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
        FROM v_ownership_summary
        ORDER BY positive_opportunity_score DESC;
    """,
    "Rating Summary": """
        SELECT
            hospital_overall_rating,
            overall_rating_group,
            hospitals_analyzed,
            ROUND(avg_err, 4) AS avg_err,
            ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
            ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
        FROM v_rating_summary
        ORDER BY hospital_overall_rating;
    """,
    "Top Hospital Condition Opportunities": """
        SELECT
            facility_id,
            facility_name,
            state,
            condition,
            ROUND(excess_readmission_ratio, 4) AS err,
            CAST(number_of_discharges AS INTEGER) AS discharges,
            ROUND(positive_opportunity_score, 1) AS opportunity_score,
            priority_category,
            hospital_type,
            hospital_ownership,
            hospital_overall_rating
        FROM v_opportunity_ranking
        ORDER BY positive_opportunity_score DESC
        LIMIT 25;
    """,
    "Unmatched HRRP Facilities": """
        SELECT *
        FROM v_unmatched_hrrp_facilities
        ORDER BY state, facility_id;
    """,
}


def read_processed(table_name: str, path: Path) -> pd.DataFrame:
    dtype = {col: "string" for col in TEXT_COLUMNS.get(table_name, set())}
    df = pd.read_csv(path, dtype=dtype, low_memory=False)
    for col in df.select_dtypes(include=["bool"]).columns:
        df[col] = df[col].astype("Int64")
    return df


def markdown_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "_No rows returned._"
    table = df.head(max_rows).copy()
    table = table.where(pd.notna(table), "")
    headers = [str(col) for col in table.columns]
    rows = [
        [str(row[col]) for col in table.columns]
        for row in table.to_dict(orient="records")
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows:,} of {len(df):,} rows._")
    return "\n".join(lines)


def execute_sql_files(connection: sqlite3.Connection) -> None:
    for path in SQL_FILES:
        connection.executescript(path.read_text(encoding="utf-8"))


def write_report(connection: sqlite3.Connection) -> None:
    lines = [
        "# SQL Analysis Layer Report",
        "",
        f"- SQLite database: `{DB_PATH.relative_to(ROOT)}`",
        "- Source tables loaded from `data/processed/`.",
        "- Views defined in `sql/02_analysis_views.sql`.",
        "",
        "## Loaded Tables",
        "",
    ]

    table_rows = []
    for table_name in TABLES:
        count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        cols = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        table_rows.append(
            {"table_name": table_name, "rows": count, "columns": len(cols)}
        )
    lines.append(markdown_table(pd.DataFrame(table_rows)))

    for title, query in REPORT_QUERIES.items():
        df = pd.read_sql_query(query, connection)
        lines.extend(["", f"## {title}", "", markdown_table(df)])

    SQL_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as connection:
        for table_name, path in TABLES.items():
            df = read_processed(table_name, path)
            df.to_sql(table_name, connection, if_exists="replace", index=False)

        execute_sql_files(connection)
        write_report(connection)

    print(f"Wrote {DB_PATH}")
    print(f"Wrote {SQL_REPORT_PATH}")


if __name__ == "__main__":
    main()
