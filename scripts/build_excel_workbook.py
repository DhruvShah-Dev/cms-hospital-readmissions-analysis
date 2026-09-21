from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "hospital_readmissions_analytic.csv"
EXCEL_DIR = ROOT / "excel"
OUTPUT_PATH = EXCEL_DIR / "cms_readmissions_executive_workbook.xlsx"

NAVY = "#16324F"
TEAL = "#2F7D73"
BLUE = "#2F6F8F"
GOLD = "#C9972B"
CORAL = "#D36B5F"
MINT = "#DFF3EE"
LIGHT_BLUE = "#E8F5F7"
BG = "#F5F8FA"
LINE = "#D8E2E7"
INK = "#1D2733"
MUTED = "#64748B"
WHITE = "#FFFFFF"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_PATH,
        dtype={"facility_id": "string", "zip_code": "string"},
        low_memory=False,
    )
    for col in ["excess_readmission_flag", "high_concern_flag"]:
        df[col] = df[col].map({True: 1, False: 0, "True": 1, "False": 0}).fillna(0)
    df["rating_label"] = df["hospital_overall_rating"].apply(
        lambda value: "Missing" if pd.isna(value) else f"{int(value)} Star"
    )
    df["hospital_ownership"] = df["hospital_ownership"].fillna("Missing")
    df["hospital_type"] = df["hospital_type"].fillna("Missing")
    df["region"] = df["region"].fillna("Missing")
    df["positive_opportunity_score"] = df["positive_opportunity_score"].fillna(0)
    return df


def numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["excess_readmission_ratio"].notna()].copy()


def national_summary(df: pd.DataFrame) -> dict[str, float]:
    numeric = numeric_df(df)
    return {
        "Hospitals": numeric["facility_id"].nunique(),
        "Avg ERR": numeric["excess_readmission_ratio"].mean(),
        "% Above Benchmark": (numeric["excess_readmission_ratio"] > 1).mean(),
        "Readmissions": numeric["number_of_readmissions"].sum(),
        "Opportunity Score": numeric["positive_opportunity_score"].sum(),
    }


def condition_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = numeric_df(df)
    result = (
        numeric.groupby("condition", as_index=False)
        .agg(
            Hospitals=("facility_id", "nunique"),
            Avg_ERR=("excess_readmission_ratio", "mean"),
            Median_ERR=("excess_readmission_ratio", "median"),
            Pct_Above_Benchmark=("excess_readmission_flag", "mean"),
            Discharges=("number_of_discharges", "sum"),
            Readmissions=("number_of_readmissions", "sum"),
            Opportunity_Score=("positive_opportunity_score", "sum"),
        )
        .sort_values("Opportunity_Score", ascending=False)
    )
    return result


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = numeric_df(df)
    result = (
        numeric.groupby("state", as_index=False)
        .agg(
            Hospitals=("facility_id", "nunique"),
            Avg_ERR=("excess_readmission_ratio", "mean"),
            Pct_Above_Benchmark=("excess_readmission_flag", "mean"),
            Discharges=("number_of_discharges", "sum"),
            Readmissions=("number_of_readmissions", "sum"),
            Opportunity_Score=("positive_opportunity_score", "sum"),
        )
        .sort_values("Opportunity_Score", ascending=False)
    )
    return result


def rating_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = numeric_df(df)
    order = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Missing"]
    result = (
        numeric.groupby("rating_label", as_index=False)
        .agg(
            Hospitals=("facility_id", "nunique"),
            Avg_ERR=("excess_readmission_ratio", "mean"),
            Pct_Above_Benchmark=("excess_readmission_flag", "mean"),
            Opportunity_Score=("positive_opportunity_score", "sum"),
        )
    )
    result["rating_label"] = pd.Categorical(result["rating_label"], categories=order, ordered=True)
    return result.sort_values("rating_label")


def ownership_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = numeric_df(df)
    return (
        numeric.groupby("hospital_ownership", as_index=False)
        .agg(
            Hospitals=("facility_id", "nunique"),
            Avg_ERR=("excess_readmission_ratio", "mean"),
            Pct_Above_Benchmark=("excess_readmission_flag", "mean"),
            Opportunity_Score=("positive_opportunity_score", "sum"),
        )
        .sort_values("Opportunity_Score", ascending=False)
    )


def hospital_priority(df: pd.DataFrame) -> pd.DataFrame:
    numeric = numeric_df(df)
    result = (
        numeric.groupby(
            [
                "facility_id",
                "facility_name",
                "state",
                "city_town",
                "rating_label",
                "hospital_ownership",
            ],
            as_index=False,
        )
        .agg(
            Conditions=("condition", "nunique"),
            Avg_ERR=("excess_readmission_ratio", "mean"),
            Conditions_Above_Benchmark=("excess_readmission_flag", "sum"),
            High_Concern_Conditions=("high_concern_flag", "sum"),
            Discharges=("number_of_discharges", "sum"),
            Readmissions=("number_of_readmissions", "sum"),
            Opportunity_Score=("positive_opportunity_score", "sum"),
        )
        .sort_values("Opportunity_Score", ascending=False)
    )
    return result


def top_detail(df: pd.DataFrame, rows: int = 100) -> pd.DataFrame:
    cols = [
        "facility_id",
        "facility_name",
        "state",
        "condition",
        "excess_readmission_ratio",
        "number_of_discharges",
        "number_of_readmissions",
        "positive_opportunity_score",
        "rating_label",
        "hospital_ownership",
    ]
    result = (
        df[df["positive_opportunity_score"] > 0][cols]
        .sort_values("positive_opportunity_score", ascending=False)
        .head(rows)
        .copy()
    )
    return result.rename(
        columns={
            "facility_id": "Facility ID",
            "facility_name": "Hospital",
            "state": "State",
            "condition": "Condition",
            "excess_readmission_ratio": "ERR",
            "number_of_discharges": "Discharges",
            "number_of_readmissions": "Readmissions",
            "positive_opportunity_score": "Opportunity Score",
            "rating_label": "Rating",
            "hospital_ownership": "Ownership",
        }
    )


def model_data(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "facility_id",
        "facility_name",
        "state",
        "region",
        "condition",
        "measure_name",
        "excess_readmission_ratio",
        "predicted_readmission_rate",
        "expected_readmission_rate",
        "readmission_gap",
        "readmission_gap_pct",
        "number_of_discharges",
        "number_of_readmissions",
        "positive_opportunity_score",
        "performance_category",
        "priority_category",
        "rating_label",
        "hospital_type",
        "hospital_ownership",
    ]
    return df[cols].rename(
        columns={
            "facility_id": "Facility ID",
            "facility_name": "Hospital",
            "state": "State",
            "region": "Region",
            "condition": "Condition",
            "measure_name": "Measure",
            "excess_readmission_ratio": "ERR",
            "predicted_readmission_rate": "Predicted Rate",
            "expected_readmission_rate": "Expected Rate",
            "readmission_gap": "Readmission Gap",
            "readmission_gap_pct": "Readmission Gap %",
            "number_of_discharges": "Discharges",
            "number_of_readmissions": "Readmissions",
            "positive_opportunity_score": "Opportunity Score",
            "performance_category": "Performance Category",
            "priority_category": "Priority Category",
            "rating_label": "Rating",
            "hospital_type": "Hospital Type",
            "hospital_ownership": "Ownership",
        }
    )


def clean_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
    return cleaned


def write_table(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame, startrow: int = 0) -> None:
    df = clean_for_excel(df)
    df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    rows, cols = df.shape
    table_columns = [{"header": str(col)} for col in df.columns]
    worksheet.add_table(
        startrow,
        0,
        startrow + rows,
        cols - 1,
        {
            "columns": table_columns,
            "style": "Table Style Medium 2",
            "autofilter": True,
        },
    )
    worksheet.freeze_panes(startrow + 1, 0)
    header_format = workbook.add_format(
        {"bold": True, "font_color": WHITE, "bg_color": NAVY, "border": 0}
    )
    for col_idx, col_name in enumerate(df.columns):
        worksheet.write(startrow, col_idx, col_name, header_format)
        max_len = max(
            [len(str(col_name))]
            + [len(str(value)) for value in df.iloc[:500, col_idx].fillna("").tolist()]
        )
        worksheet.set_column(col_idx, col_idx, min(max(max_len + 2, 11), 34))


def add_title(worksheet, workbook, title: str, subtitle: str | None = None) -> None:
    title_fmt = workbook.add_format(
        {"bold": True, "font_color": NAVY, "font_size": 20, "border": 0}
    )
    subtitle_fmt = workbook.add_format({"font_color": MUTED, "font_size": 10})
    worksheet.write("B2", title, title_fmt)
    if subtitle:
        worksheet.write("B3", subtitle, subtitle_fmt)


def make_formats(workbook) -> dict[str, object]:
    return {
        "kpi_label": workbook.add_format(
            {
                "font_color": MUTED,
                "font_size": 9,
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "bg_color": WHITE,
                "top": 1,
                "left": 1,
                "right": 1,
                "border_color": LINE,
            }
        ),
        "kpi_value": workbook.add_format(
            {
                "font_color": NAVY,
                "font_size": 18,
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "bg_color": WHITE,
                "bottom": 1,
                "left": 1,
                "right": 1,
                "border_color": LINE,
            }
        ),
        "section": workbook.add_format(
            {"font_color": NAVY, "font_size": 12, "bold": True, "bg_color": LIGHT_BLUE}
        ),
        "integer": workbook.add_format({"num_format": "#,##0"}),
        "decimal": workbook.add_format({"num_format": "0.0000"}),
        "percent": workbook.add_format({"num_format": "0.0%"}),
        "score": workbook.add_format({"num_format": "#,##0.0"}),
        "text": workbook.add_format({"font_color": INK}),
    }


def build_workbook() -> None:
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    kpis = national_summary(df)
    cond = condition_summary(df)
    states = state_summary(df)
    ratings = rating_summary(df)
    ownership = ownership_summary(df)
    hospitals = hospital_priority(df)
    detail = top_detail(df)
    model = model_data(df)

    with pd.ExcelWriter(OUTPUT_PATH, engine="xlsxwriter") as writer:
        workbook = writer.book
        formats = make_formats(workbook)

        workbook.set_properties(
            {
                "title": "CMS Hospital Readmissions Opportunity Analysis",
                "subject": "Hospital readmissions opportunity analysis",
                "author": "Dhruv Shah",
                "comments": "Built from CMS HRRP and Hospital General Information data.",
            }
        )

        summary_ws = workbook.add_worksheet("Executive Summary")
        writer.sheets["Executive Summary"] = summary_ws
        summary_ws.hide_gridlines(2)
        summary_ws.set_tab_color(TEAL)
        summary_ws.set_column("A:A", 2)
        summary_ws.set_column("B:F", 18)
        summary_ws.set_column("H:M", 14)
        add_title(summary_ws, workbook, "Hospital Readmissions Opportunity", "CMS HRRP | July 2021 - June 2024")

        kpi_items = [
            ("Hospitals", kpis["Hospitals"], "#,##0"),
            ("Avg ERR", kpis["Avg ERR"], "0.0000"),
            ("% Above Benchmark", kpis["% Above Benchmark"], "0.0%"),
            ("Readmissions", kpis["Readmissions"], "#,##0"),
            ("Opportunity Score", kpis["Opportunity Score"], "#,##0.0"),
        ]
        for idx, (label, value, number_format) in enumerate(kpi_items):
            col = 1 + idx
            summary_ws.write(5, col, label, formats["kpi_label"])
            value_fmt = workbook.add_format(
                {
                    "font_color": NAVY,
                    "font_size": 18,
                    "bold": True,
                    "align": "center",
                    "valign": "vcenter",
                    "bg_color": WHITE,
                    "bottom": 1,
                    "left": 1,
                    "right": 1,
                    "border_color": LINE,
                    "num_format": number_format,
                }
            )
            summary_ws.write(6, col, value, value_fmt)

        write_table(writer, "Condition Analysis", cond, startrow=3)
        write_table(writer, "State Analysis", states, startrow=3)
        write_table(writer, "Hospital Benchmark", hospitals, startrow=3)
        write_table(writer, "Priority Detail", detail, startrow=3)
        write_table(writer, "Model Data", model, startrow=0)

        # Supporting summary tables on hidden data sheet for charts.
        data_ws = workbook.add_worksheet("_Chart Data")
        writer.sheets["_Chart Data"] = data_ws
        data_ws.hide()
        cond_chart = cond[["condition", "Opportunity_Score", "Readmissions"]].copy()
        state_chart = states.head(10)[["state", "Opportunity_Score", "Avg_ERR"]].copy()
        rating_chart = ratings[["rating_label", "Avg_ERR", "Pct_Above_Benchmark"]].copy()
        cond_chart.to_excel(writer, sheet_name="_Chart Data", startrow=0, startcol=0, index=False)
        state_chart.to_excel(writer, sheet_name="_Chart Data", startrow=0, startcol=5, index=False)
        rating_chart.to_excel(writer, sheet_name="_Chart Data", startrow=0, startcol=10, index=False)

        # Executive Summary charts.
        cond_chart_obj = workbook.add_chart({"type": "bar"})
        cond_chart_obj.add_series(
            {
                "name": "Opportunity Score",
                "categories": ["_Chart Data", 1, 0, len(cond_chart), 0],
                "values": ["_Chart Data", 1, 1, len(cond_chart), 1],
                "fill": {"color": TEAL},
                "border": {"color": TEAL},
            }
        )
        cond_chart_obj.set_title({"name": "Opportunity by Condition"})
        cond_chart_obj.set_x_axis({"name": "Opportunity Score", "major_gridlines": {"visible": True}})
        cond_chart_obj.set_y_axis({"reverse": True})
        cond_chart_obj.set_legend({"none": True})
        cond_chart_obj.set_style(10)
        summary_ws.insert_chart("B10", cond_chart_obj, {"x_scale": 1.15, "y_scale": 1.15})

        state_chart_obj = workbook.add_chart({"type": "bar"})
        state_chart_obj.add_series(
            {
                "name": "Opportunity Score",
                "categories": ["_Chart Data", 1, 5, len(state_chart), 5],
                "values": ["_Chart Data", 1, 6, len(state_chart), 6],
                "fill": {"color": GOLD},
                "border": {"color": GOLD},
            }
        )
        state_chart_obj.set_title({"name": "Top States"})
        state_chart_obj.set_x_axis({"name": "Opportunity Score", "major_gridlines": {"visible": True}})
        state_chart_obj.set_y_axis({"reverse": True})
        state_chart_obj.set_legend({"none": True})
        state_chart_obj.set_style(10)
        summary_ws.insert_chart("H10", state_chart_obj, {"x_scale": 1.05, "y_scale": 1.15})

        summary_ws.write("B27", "Top Hospital-Condition Priorities", formats["section"])
        detail_preview = detail.head(10)
        for col_idx, col_name in enumerate(detail_preview.columns):
            summary_ws.write(28, 1 + col_idx, col_name, workbook.add_format({"bold": True, "font_color": WHITE, "bg_color": NAVY}))
        for row_idx, (_, row) in enumerate(detail_preview.iterrows(), start=29):
            for col_idx, value in enumerate(row.tolist(), start=1):
                summary_ws.write(row_idx, col_idx, value)

        # Sheet-specific formatting.
        for sheet_name in ["Condition Analysis", "State Analysis", "Hospital Benchmark", "Priority Detail", "Model Data"]:
            ws = writer.sheets[sheet_name]
            ws.hide_gridlines(2)
            ws.set_tab_color(BLUE if sheet_name != "Model Data" else MUTED)
            ws.freeze_panes(4 if sheet_name != "Model Data" else 1, 0)
            if sheet_name != "Model Data":
                add_title(ws, workbook, sheet_name)

        condition_ws = writer.sheets["Condition Analysis"]
        condition_chart = workbook.add_chart({"type": "column"})
        condition_chart.add_series(
            {
                "name": "Opportunity Score",
                "categories": ["Condition Analysis", 4, 0, 4 + len(cond) - 1, 0],
                "values": ["Condition Analysis", 4, 6, 4 + len(cond) - 1, 6],
                "fill": {"color": TEAL},
                "border": {"color": TEAL},
            }
        )
        condition_chart.set_title({"name": "Opportunity Score"})
        condition_chart.set_legend({"none": True})
        condition_ws.insert_chart("J5", condition_chart, {"x_scale": 1.25, "y_scale": 1.1})

        state_ws = writer.sheets["State Analysis"]
        state_ws.conditional_format(
            4,
            6,
            4 + len(states) - 1,
            6,
            {"type": "3_color_scale", "min_color": WHITE, "mid_color": MINT, "max_color": TEAL},
        )

        benchmark_ws = writer.sheets["Hospital Benchmark"]
        benchmark_ws.conditional_format(
            4,
            12,
            4 + len(hospitals) - 1,
            12,
            {"type": "3_color_scale", "min_color": WHITE, "mid_color": MINT, "max_color": CORAL},
        )

        detail_ws = writer.sheets["Priority Detail"]
        detail_ws.conditional_format(
            4,
            7,
            4 + len(detail) - 1,
            7,
            {"type": "3_color_scale", "min_color": WHITE, "mid_color": MINT, "max_color": CORAL},
        )

        dictionary = pd.DataFrame(
            [
                ["ERR", "CMS excess readmission ratio; values above 1.0 are above expected readmissions."],
                ["Readmission Gap", "Predicted readmission rate minus expected readmission rate."],
                ["Opportunity Score", "(ERR - 1) times discharges, floored at zero for ranking."],
                ["Above Benchmark", "ERR greater than 1.0."],
                ["High Concern", "ERR at or above 1.05."],
                ["Grain", "Hospital-condition row."],
            ],
            columns=["Metric", "Definition"],
        )
        write_table(writer, "Data Dictionary", dictionary, startrow=3)
        dict_ws = writer.sheets["Data Dictionary"]
        dict_ws.hide_gridlines(2)
        dict_ws.set_tab_color(NAVY)
        add_title(dict_ws, workbook, "Data Dictionary")

        # Number formats.
        number_format_map = {
            "Avg_ERR": "0.0000",
            "Median_ERR": "0.0000",
            "Pct_Above_Benchmark": "0.0%",
            "Discharges": "#,##0",
            "Readmissions": "#,##0",
            "Opportunity_Score": "#,##0.0",
            "ERR": "0.0000",
            "Opportunity Score": "#,##0.0",
            "Readmission Gap %": "0.0",
        }
        for sheet_name, source_df in {
            "Condition Analysis": cond,
            "State Analysis": states,
            "Hospital Benchmark": hospitals,
            "Priority Detail": detail,
            "Model Data": model,
        }.items():
            ws = writer.sheets[sheet_name]
            for idx, column in enumerate(source_df.columns):
                fmt = number_format_map.get(column)
                if fmt:
                    ws.set_column(idx, idx, None, workbook.add_format({"num_format": fmt}))

        summary_ws.set_landscape()
        summary_ws.fit_to_pages(1, 1)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    build_workbook()
