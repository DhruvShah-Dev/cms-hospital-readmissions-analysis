from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
IMAGES = ROOT / "images"
NOTEBOOKS = ROOT / "notebooks"

ANALYTIC_PATH = PROCESSED / "hospital_readmissions_analytic.csv"
DB_PATH = PROCESSED / "readmissions.db"
REPORT_PATH = REPORTS / "04_eda_statistical_analysis_report.md"
NOTEBOOK_PATH = NOTEBOOKS / "04_eda_statistical_analysis.ipynb"


def read_analytic() -> pd.DataFrame:
    df = pd.read_csv(
        ANALYTIC_PATH,
        dtype={"facility_id": "string", "zip_code": "string"},
        low_memory=False,
    )
    for col in ["excess_readmission_flag", "high_concern_flag", "has_numeric_volume", "has_numeric_err"]:
        if col in df:
            df[col] = df[col].map({True: 1, False: 0, "True": 1, "False": 0})
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


def save_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output: Path,
    color: str = "#2f6f73",
) -> None:
    fig_height = max(4.5, len(df) * 0.34)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    bars = ax.barh(df[x_col], df[y_col], color=color)
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=9)
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=14, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def save_err_distribution(df: pd.DataFrame, output: Path) -> None:
    err = df["excess_readmission_ratio"].dropna()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(err, bins=50, color="#4c78a8", edgecolor="white")
    ax.axvline(1.0, color="#b23a48", linewidth=2, label="ERR benchmark = 1.0")
    ax.axvline(err.median(), color="#2f6f73", linewidth=2, label=f"Median = {err.median():.4f}")
    ax.set_title("Distribution of Excess Readmission Ratio", loc="left", fontsize=14, pad=12)
    ax.set_xlabel("Excess Readmission Ratio")
    ax.set_ylabel("Hospital-condition rows")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def save_scatter(df: pd.DataFrame, output: Path) -> None:
    plot_df = df.dropna(subset=["number_of_discharges", "excess_readmission_ratio"]).copy()
    plot_df = plot_df[plot_df["number_of_discharges"] > 0]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    hb = ax.hexbin(
        plot_df["number_of_discharges"],
        plot_df["excess_readmission_ratio"],
        xscale="log",
        gridsize=55,
        mincnt=1,
        cmap="Blues",
    )
    ax.axhline(1.0, color="#b23a48", linewidth=1.6)
    fig.colorbar(hb, ax=ax, label="Hospital-condition rows")
    ax.set_title("Volume Has a Weak Relationship With ERR", loc="left", fontsize=14, pad=12)
    ax.set_xlabel("Number of discharges, log scale")
    ax.set_ylabel("Excess Readmission Ratio")
    ax.grid(alpha=0.22)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def save_rating_dot(df: pd.DataFrame, output: Path) -> None:
    plot_df = df.dropna(subset=["overall_rating_group"]).copy()
    plot_df = plot_df[plot_df["rating_label"] != "Missing Rating"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axvline(1.0, color="#5f6b73", linewidth=1.5, label="ERR benchmark = 1.0")
    ax.scatter(
        plot_df["avg_err"],
        plot_df["rating_label"],
        s=90,
        color="#2f6f8f",
        edgecolor="#16324f",
        linewidth=0.8,
        zorder=3,
    )
    for row in plot_df.itertuples():
        ax.annotate(f"{row.avg_err:.4f}", (row.avg_err, row.rating_label), xytext=(8, 0), textcoords="offset points", va="center")
    ax.set_xlim(0.94, 1.06)
    ax.set_title("Average ERR Declines as Overall Rating Rises", loc="left", fontsize=14, pad=12)
    ax.set_xlabel("Average ERR (descriptive; readmission contributes to the overall rating)")
    ax.set_ylabel("Overall rating")
    ax.grid(axis="x", alpha=0.22)
    ax.legend(frameon=False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def kruskal_by_group(df: pd.DataFrame, group_col: str, min_group_size: int = 20) -> dict[str, float | int | str]:
    working = df.dropna(subset=["excess_readmission_ratio", group_col])
    groups = [
        group["excess_readmission_ratio"].to_numpy()
        for _, group in working.groupby(group_col)
        if len(group) >= min_group_size
    ]
    if len(groups) < 2:
        return {
            "grouping": group_col,
            "groups_tested": len(groups),
            "n": len(working),
            "h_statistic": math.nan,
            "p_value": math.nan,
            "epsilon_squared": math.nan,
            "interpretation": "Not enough eligible groups",
        }
    result = stats.kruskal(*groups, nan_policy="omit")
    n = sum(len(group) for group in groups)
    k = len(groups)
    epsilon_squared = max((result.statistic - k + 1) / (n - k), 0) if n > k else math.nan
    return {
        "grouping": group_col,
        "groups_tested": k,
        "n": n,
        "h_statistic": round(float(result.statistic), 4),
        "p_value": float(result.pvalue),
        "epsilon_squared": round(float(epsilon_squared), 4),
        "interpretation": "Statistically different ERR distributions"
        if result.pvalue < 0.05
        else "No statistically significant difference detected",
    }


def spearman_test(df: pd.DataFrame) -> dict[str, float | int | str]:
    working = df.dropna(subset=["number_of_discharges", "excess_readmission_ratio"])
    working = working[working["number_of_discharges"] > 0]
    result = stats.spearmanr(working["number_of_discharges"], working["excess_readmission_ratio"])
    return {
        "comparison": "number_of_discharges vs excess_readmission_ratio",
        "n": len(working),
        "spearman_rho": round(float(result.statistic), 4),
        "p_value": float(result.pvalue),
        "interpretation": "Statistically significant monotonic relationship"
        if result.pvalue < 0.05
        else "No statistically significant monotonic relationship detected",
    }


def hospital_level_err(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse repeated condition rows before hospital-characteristic tests."""
    columns = [
        "facility_id",
        "state",
        "hospital_ownership",
        "hospital_overall_rating",
        "overall_rating_group",
    ]
    return (
        df.dropna(subset=["excess_readmission_ratio"])
        .groupby(columns, dropna=False, as_index=False)
        .agg(excess_readmission_ratio=("excess_readmission_ratio", "mean"))
    )


def p_label(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.4f}"


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    """False-discovery-rate adjustment without an additional dependency."""
    values = pd.to_numeric(p_values, errors="coerce")
    valid = values.dropna().sort_values()
    adjusted = pd.Series(np.nan, index=values.index, dtype="float64")
    if valid.empty:
        return adjusted
    m = len(valid)
    ranked = valid * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked.iloc[::-1])[::-1].clip(upper=1.0)
    adjusted.loc[ranked.index] = ranked
    return adjusted


def build_analysis_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    numeric = df[df["excess_readmission_ratio"].notna()].copy()

    national = pd.DataFrame(
        [
            {
                "metric": "Hospital-condition rows with numeric ERR",
                "value": f"{len(numeric):,}",
            },
            {
                "metric": "Hospitals with at least one numeric ERR",
                "value": f"{numeric['facility_id'].nunique():,}",
            },
            {
                "metric": "Average ERR",
                "value": f"{numeric['excess_readmission_ratio'].mean():.4f}",
            },
            {
                "metric": "Median ERR",
                "value": f"{numeric['excess_readmission_ratio'].median():.4f}",
            },
            {
                "metric": "Rows above ERR benchmark",
                "value": f"{(numeric['excess_readmission_ratio'] > 1).mean() * 100:.1f}%",
            },
            {
                "metric": "Rows at or above ERR 1.05",
                "value": f"{(numeric['excess_readmission_ratio'] >= 1.05).mean() * 100:.1f}%",
            },
            {
                "metric": "Reported numeric readmissions",
                "value": f"{int(numeric['number_of_readmissions'].sum()):,}",
            },
            {
                "metric": "Positive estimated excess readmissions",
                "value": f"{numeric['positive_estimated_excess_readmissions'].sum():,.1f}",
            },
        ]
    )

    condition = (
        numeric.groupby("condition", dropna=False)
        .agg(
            rows=("facility_id", "size"),
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            median_err=("excess_readmission_ratio", "median"),
            pct_err_gt_1=("excess_readmission_flag", "mean"),
            readmissions=("number_of_readmissions", "sum"),
            discharges=("number_of_discharges", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
        )
        .reset_index()
        .sort_values("estimated_excess", ascending=False)
    )
    for col in ["avg_err", "median_err", "pct_err_gt_1", "estimated_excess"]:
        condition[col] = condition[col].round(4)

    state = (
        numeric.groupby("state", dropna=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_err_gt_1=("excess_readmission_flag", "mean"),
            readmissions=("number_of_readmissions", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            discharges=("number_of_discharges", "sum"),
        )
        .reset_index()
        .assign(excess_per_1000=lambda x: 1000 * x["estimated_excess"] / x["discharges"])
        .sort_values("estimated_excess", ascending=False)
        .head(15)
    )
    for col in ["avg_err", "pct_err_gt_1", "estimated_excess", "excess_per_1000"]:
        state[col] = state[col].round(4)

    rating = (
        numeric.assign(
            rating_label=numeric["hospital_overall_rating"].fillna("Missing Rating").astype(str)
        )
        .groupby(["rating_label", "overall_rating_group"], dropna=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            median_err=("excess_readmission_ratio", "median"),
            pct_err_gt_1=("excess_readmission_flag", "mean"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
        )
        .reset_index()
        .sort_values("rating_label")
    )
    for col in ["avg_err", "median_err", "pct_err_gt_1", "estimated_excess"]:
        rating[col] = rating[col].round(4)

    ownership = (
        numeric.assign(
            hospital_ownership=numeric["hospital_ownership"].fillna("Missing Hospital Attributes")
        )
        .groupby("hospital_ownership", dropna=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            median_err=("excess_readmission_ratio", "median"),
            pct_err_gt_1=("excess_readmission_flag", "mean"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
        )
        .reset_index()
        .sort_values("avg_err", ascending=False)
    )
    for col in ["avg_err", "median_err", "pct_err_gt_1", "estimated_excess"]:
        ownership[col] = ownership[col].round(4)

    hospital = (
        numeric.groupby(
            [
                "facility_id",
                "facility_name",
                "state",
                "city_town",
                "hospital_ownership",
                "hospital_overall_rating",
            ],
            dropna=False,
        )
        .agg(
            numeric_conditions=("condition", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            conditions_err_gt_1=("excess_readmission_flag", "sum"),
            conditions_err_ge_1_05=("high_concern_flag", "sum"),
            discharges=("number_of_discharges", "sum"),
            readmissions=("number_of_readmissions", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
        )
        .reset_index()
        .sort_values("estimated_excess", ascending=False)
        .head(20)
    )
    for col in ["avg_err", "estimated_excess"]:
        hospital[col] = hospital[col].round(4)

    top_rows = (
        numeric[numeric["positive_estimated_excess_readmissions"] > 0][
            [
                "facility_id",
                "facility_name",
                "state",
                "condition",
                "excess_readmission_ratio",
                "number_of_discharges",
                "positive_estimated_excess_readmissions",
                "hospital_overall_rating",
                "hospital_ownership",
            ]
        ]
        .sort_values("positive_estimated_excess_readmissions", ascending=False)
        .head(20)
        .copy()
    )
    top_rows["excess_readmission_ratio"] = top_rows["excess_readmission_ratio"].round(4)
    top_rows["positive_estimated_excess_readmissions"] = top_rows[
        "positive_estimated_excess_readmissions"
    ].round(1)

    return {
        "national": national,
        "condition": condition,
        "state": state,
        "rating": rating,
        "ownership": ownership,
        "hospital": hospital,
        "top_rows": top_rows,
    }


def build_report(df: pd.DataFrame, tables: dict[str, pd.DataFrame], tests: pd.DataFrame, volume_test: dict) -> str:
    condition = tables["condition"]
    state = tables["state"]
    rating = tables["rating"]
    top_rows = tables["top_rows"]

    strongest_condition = condition.iloc[0]
    strongest_state = state.iloc[0]
    low_rating = rating[rating["rating_label"] == "1.0"].iloc[0]
    high_rating = rating[rating["rating_label"] == "5.0"].iloc[0]

    lines = [
        "# EDA And Statistical Analysis: CMS Hospital Readmissions",
        "",
        "## Executive Summary",
        "",
        f"- **Estimated excess readmissions are concentrated by condition.** {strongest_condition['condition']} has the largest rate-gap-based estimate ({strongest_condition['estimated_excess']:,.1f}); the estimate is a prioritization proxy, not a count of preventable events.",
        f"- **Total and normalized geography answer different questions.** {strongest_state['state']} has the highest total estimated excess burden ({strongest_state['estimated_excess']:,.1f}), while normalized results identify performance intensity independent of state size.",
        f"- **Overall rating and ERR are descriptively aligned.** One-star hospitals average ERR {low_rating['avg_err']:.4f}, while five-star hospitals average ERR {high_rating['avg_err']:.4f}; this comparison is partly circular because readmission measures contribute to the CMS overall rating.",
        f"- **Volume has only a weak monotonic relationship with ERR.** Spearman rho is {volume_test['spearman_rho']:.4f}, so volume is more useful for sizing estimated burden than explaining risk-adjusted performance.",
        "",
        "## Context And Method",
        "",
        "The analysis uses the cleaned CMS HRRP analytic table at hospital-condition grain. ERR is interpreted as the risk-adjusted readmission performance measure, where values above 1.0 indicate excess readmissions versus expected performance for similar patients.",
        "",
        "Hospital-characteristic comparisons aggregate ERR to one row per hospital before Kruskal-Wallis testing so repeated condition rows are not treated as independent hospitals. Condition comparisons remain hospital-condition analyses and are labeled accordingly. Test p-values include a Benjamini-Hochberg false-discovery-rate adjustment. Volume correlation uses Spearman rank correlation. These tests indicate association, not causality.",
        "",
        "## National Picture",
        "",
        markdown_table(tables["national"]),
        "",
        "![Distribution of ERR](../images/err_distribution.png)",
        "",
        "The national ERR distribution is centered near 1.0, as expected for a risk-adjusted benchmark. Prioritization therefore combines performance with eligible discharge volume while keeping suppressed rows visible as unscored rather than zero.",
        "",
        "## Conditions Driving Estimated Excess Readmissions",
        "",
        "![Condition Opportunity](../images/condition_opportunity.png)",
        "",
        markdown_table(condition),
        "",
        "Heart Failure and Pneumonia dominate the estimated excess-readmission ranking because they combine positive rate gaps with high eligible discharge volume. CABG has similar average ERR but materially lower volume.",
        "",
        "## Geography",
        "",
        "![State Opportunity](../images/state_opportunity.png)",
        "",
        markdown_table(state),
        "",
        "Total estimated burden identifies where the largest number of excess cases may be concentrated; the normalized per-1,000 measure identifies performance intensity. Large-state totals must not be described as uniformly worse performance.",
        "",
        "## Hospital Characteristics",
        "",
        "![Rating And ERR](../images/rating_avg_err.png)",
        "",
        markdown_table(rating),
        "",
        markdown_table(tables["ownership"]),
        "",
        "Lower-rated hospitals have higher average ERR, but this is a descriptive alignment rather than an independent explanatory result because readmission measures contribute to the overall CMS rating. Ownership comparisons remain vulnerable to differences in category size, hospital mix, and case volume.",
        "",
        "## Volume Relationship",
        "",
        "![Volume and ERR](../images/volume_err_scatter.png)",
        "",
        f"Spearman correlation between discharges and ERR is {volume_test['spearman_rho']:.4f} with p-value {p_label(volume_test['p_value'])} across {volume_test['n']:,} eligible rows. The relationship is statistically significant but weak, so volume should size estimated burden rather than imply worse performance.",
        "",
        "## Statistical Tests",
        "",
        markdown_table(tests),
        "",
        "Hospital-level tests reduce repeated-measures inflation but remain descriptive and unadjusted for hospital mix. Effect sizes are reported because statistical significance is not the same as operational importance.",
        "",
        "## Hospital-Condition Review Priorities",
        "",
        markdown_table(top_rows),
        "",
        "These hospital-condition rows are starting points for review because they combine positive rate gaps with enough eligible volume to matter. Local service-line context, discharge planning, payer mix, and care-transition data are required before action plans or preventability claims.",
        "",
        "## Caveats",
        "",
        "- CMS suppresses many low-volume rows, so estimated excess readmissions apply only where predicted rate, expected rate, and discharges are numeric.",
        "- Estimated excess readmissions are a rate-gap proxy, not a causal estimate of preventable cases or financial penalty exposure.",
        "- State totals reflect both performance and population size; use the normalized per-1,000 measure for intensity.",
        "- Overall star-rating comparisons are partly circular because readmission measures contribute to the rating.",
        "- Statistical tests are association tests and do not prove that rating, ownership, geography, or condition causes readmission differences.",
        "- The HRRP measurement period is July 1, 2021 through June 30, 2024; results should not be described as current live performance.",
        "",
        "## Recommended Next Step",
        "",
        "Review high estimated-excess hospital-condition rows, then validate the result with local care-transition and service-line data before selecting interventions.",
        "",
    ]
    return "\n".join(lines)


def write_notebook() -> None:
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## tl;dr\n",
                "\n",
                "Run `python scripts/run_eda_statistical_analysis.py` from the project root to reproduce the executed EDA report, statistical tests, and chart images. This notebook is a companion walkthrough generated from the same project logic.\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Context & Methods\n",
                "\n",
                "The analysis uses the cleaned CMS analytic table at hospital-condition grain. ERR above 1.0 indicates excess readmissions versus CMS expected performance. Statistical tests use Kruskal-Wallis for categorical comparisons and Spearman correlation for volume versus ERR.\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "from scipy import stats\n",
                "\n",
                "ROOT = Path('..').resolve()\n",
                "df = pd.read_csv(ROOT / 'data/processed/hospital_readmissions_analytic.csv', dtype={'facility_id': 'string', 'zip_code': 'string'}, low_memory=False)\n",
                "numeric = df[df['excess_readmission_ratio'].notna()].copy()\n",
                "numeric.shape\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Data\n", "\n", "Check source shape and required metric coverage.\n"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "numeric[['facility_id', 'condition', 'excess_readmission_ratio', 'number_of_discharges', 'positive_estimated_excess_readmissions']].head()\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## Results\n", "\n", "Condition, state, rating, ownership, and volume tests.\n"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "numeric.groupby('condition').agg(\n",
                "    rows=('facility_id', 'size'),\n",
                "    avg_err=('excess_readmission_ratio', 'mean'),\n",
                "    pct_excess=('excess_readmission_flag', 'mean'),\n",
                "    estimated_excess=('positive_estimated_excess_readmissions', 'sum'),\n",
                ").sort_values('estimated_excess', ascending=False)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "groups = [g['excess_readmission_ratio'].to_numpy() for _, g in numeric.dropna(subset=['condition']).groupby('condition')]\n",
                "stats.kruskal(*groups)\n",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Takeaways\n",
                "\n",
                "See `reports/04_eda_statistical_analysis_report.md` for the executed findings and chart outputs.\n",
            ],
        },
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)

    df = read_analytic()
    tables = build_analysis_tables(df)

    hospital_level = hospital_level_err(df)
    tests = pd.DataFrame(
        [
            kruskal_by_group(df, "condition"),
            kruskal_by_group(hospital_level, "state", min_group_size=10),
            kruskal_by_group(hospital_level, "hospital_ownership", min_group_size=10),
            kruskal_by_group(hospital_level, "hospital_overall_rating", min_group_size=10),
            kruskal_by_group(hospital_level, "overall_rating_group", min_group_size=10),
        ]
    )
    tests["p_value_fdr"] = benjamini_hochberg(tests["p_value"])
    tests["p_value"] = tests["p_value"].apply(p_label)
    tests["p_value_fdr"] = tests["p_value_fdr"].apply(p_label)

    volume_test = spearman_test(df)

    save_err_distribution(df, IMAGES / "err_distribution.png")
    condition_chart = tables["condition"][["condition", "estimated_excess"]].copy()
    save_bar(
        condition_chart,
        "condition",
        "estimated_excess",
        "Estimated Excess Readmissions by Condition",
        "Estimated excess readmissions",
        "Condition",
        IMAGES / "condition_opportunity.png",
        color="#2f6f73",
    )
    state_chart = tables["state"][["state", "estimated_excess"]].copy()
    save_bar(
        state_chart,
        "state",
        "estimated_excess",
        "Top States by Estimated Excess Readmissions",
        "Estimated excess readmissions",
        "State",
        IMAGES / "state_opportunity.png",
        color="#9f6b3f",
    )
    save_rating_dot(tables["rating"], IMAGES / "rating_avg_err.png")
    save_scatter(df, IMAGES / "volume_err_scatter.png")

    REPORT_PATH.write_text(build_report(df, tables, tests, volume_test), encoding="utf-8")
    write_notebook()

    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as connection:
            sql_check = pd.read_sql_query("SELECT COUNT(*) AS rows FROM v_opportunity_ranking", connection)
            print(f"SQL priority rows available: {int(sql_check.loc[0, 'rows']):,}")

    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {NOTEBOOK_PATH}")
    print("Wrote images/err_distribution.png")
    print("Wrote images/condition_opportunity.png")
    print("Wrote images/state_opportunity.png")
    print("Wrote images/rating_avg_err.png")
    print("Wrote images/volume_err_scatter.png")


if __name__ == "__main__":
    main()
