from __future__ import annotations

import html
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "hospital_readmissions_analytic.csv"

PAGE_TITLE = "CMS Hospital Readmissions Prioritization"
MEASUREMENT_PERIOD = "Jul 2021-Jun 2024"

COLORS = {
    "navy": "#16324f",
    "blue": "#2f6f8f",
    "teal": "#2f7d73",
    "mint": "#dff3ee",
    "aqua": "#e8f5f7",
    "gold": "#c9972b",
    "coral": "#d36b5f",
    "ink": "#1d2733",
    "muted": "#64748b",
    "line": "#d8e2e7",
    "panel": "#ffffff",
    "background": "#f5f8fa",
}


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    f"""
    <style>
    :root {{
        --navy: {COLORS["navy"]};
        --blue: {COLORS["blue"]};
        --teal: {COLORS["teal"]};
        --mint: {COLORS["mint"]};
        --aqua: {COLORS["aqua"]};
        --gold: {COLORS["gold"]};
        --coral: {COLORS["coral"]};
        --ink: {COLORS["ink"]};
        --muted: {COLORS["muted"]};
        --line: {COLORS["line"]};
        --panel: {COLORS["panel"]};
        --background: {COLORS["background"]};
    }}
    .stApp {{
        background: var(--background);
        color: var(--ink);
    }}
    section[data-testid="stSidebar"] {{
        background: #ffffff;
        border-right: 1px solid var(--line);
    }}
    .block-container {{
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }}
    .dashboard-title {{
        font-size: 2.15rem;
        font-weight: 760;
        color: var(--navy);
        letter-spacing: 0;
        margin-bottom: .2rem;
    }}
    .dashboard-subtitle {{
        color: var(--muted);
        font-size: 1rem;
        margin-bottom: 1.15rem;
    }}
    .kpi-card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-left: 5px solid var(--teal);
        border-radius: 8px;
        padding: 1rem 1.05rem .95rem;
        min-height: 124px;
        box-shadow: 0 8px 22px rgba(22, 50, 79, 0.055);
    }}
    .kpi-label {{
        color: var(--muted);
        font-size: .78rem;
        line-height: 1.2;
        text-transform: uppercase;
        letter-spacing: .04em;
        font-weight: 720;
    }}
    .kpi-value {{
        color: var(--navy);
        font-size: 1.95rem;
        font-weight: 780;
        margin-top: .45rem;
        line-height: 1.05;
        letter-spacing: 0;
    }}
    .kpi-note {{
        color: var(--muted);
        font-size: .82rem;
        margin-top: .45rem;
        line-height: 1.35;
    }}
    .section-card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1.05rem 1.1rem;
        box-shadow: 0 8px 22px rgba(22, 50, 79, 0.045);
        margin-bottom: .75rem;
    }}
    .section-title {{
        font-size: 1.05rem;
        color: var(--navy);
        font-weight: 760;
        margin-bottom: .2rem;
    }}
    .section-note {{
        color: var(--muted);
        font-size: .9rem;
        margin-bottom: .4rem;
    }}
    .source-note {{
        color: var(--muted);
        font-size: .82rem;
        margin-top: .6rem;
    }}
    .qa-card {{
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 150px;
        box-shadow: 0 8px 22px rgba(22, 50, 79, 0.045);
    }}
    .qa-question {{
        color: var(--navy);
        font-size: .98rem;
        font-weight: 760;
        margin-bottom: .55rem;
        line-height: 1.25;
    }}
    .qa-answer {{
        color: var(--ink);
        font-size: .95rem;
        line-height: 1.45;
    }}
    .qa-tag {{
        color: var(--teal);
        font-size: .72rem;
        font-weight: 760;
        text-transform: uppercase;
        letter-spacing: .04em;
        margin-bottom: .5rem;
    }}
    .filter-chip {{
        display: inline-block;
        background: var(--mint);
        border: 1px solid #a7d6ce;
        color: var(--navy);
        border-radius: 999px;
        padding: .22rem .7rem;
        margin: 0 .35rem .65rem 0;
        font-size: .82rem;
        font-weight: 650;
    }}
    div[data-testid="stMetricValue"] {{
        color: var(--navy);
    }}
    div[data-testid="stTabs"] button p {{
        font-weight: 650;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        dtype={"facility_id": "string", "zip_code": "string"},
        low_memory=False,
    )
    for col in ["excess_readmission_flag", "high_concern_flag"]:
        df[col] = df[col].map({True: 1, False: 0, "True": 1, "False": 0}).fillna(0)
    df["rating_label"] = df["hospital_overall_rating"].apply(
        lambda value: "Missing Rating" if pd.isna(value) else f"{int(value)} Star"
    )
    df["ownership_group"] = df["hospital_ownership"].fillna("Missing Hospital Attributes")
    df["region"] = df["region"].fillna("Missing Hospital Attributes")
    df["hospital_type"] = df["hospital_type"].fillna("Missing Hospital Attributes")
    df["city_town"] = df["city_town"].fillna("")
    if "opportunity_eligibility" not in df:
        df["opportunity_eligibility"] = "Eligible"
        missing_rates = df["predicted_readmission_rate"].isna() | df["expected_readmission_rate"].isna()
        df.loc[missing_rates, "opportunity_eligibility"] = "Missing rate inputs"
        df.loc[df["number_of_discharges"].isna(), "opportunity_eligibility"] = "Missing discharges"
        df.loc[
            missing_rates & df["number_of_discharges"].isna(),
            "opportunity_eligibility",
        ] = "Missing rate inputs and discharges"
    if "positive_estimated_excess_readmissions" not in df:
        eligible = (
            df["predicted_readmission_rate"].notna()
            & df["expected_readmission_rate"].notna()
            & df["number_of_discharges"].notna()
        )
        df["estimated_excess_readmissions"] = (
            (df["predicted_readmission_rate"] - df["expected_readmission_rate"])
            * df["number_of_discharges"]
            / 100
        ).where(eligible)
        df["positive_estimated_excess_readmissions"] = df[
            "estimated_excess_readmissions"
        ].clip(lower=0)
    df["state"] = df["state"].fillna("Unknown")
    return df


def format_number(value: float | int, decimals: int = 0) -> str:
    if pd.isna(value):
        return "n/a"
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.{decimals}f}%"


def metric_card(label: str, value: str, note: str = "", accent: str = "teal") -> None:
    border_color = COLORS.get(accent, COLORS["teal"])
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    note_html = f'<div class="kpi-note">{html.escape(str(note))}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color:{border_color}">
            <div class="kpi-label">{safe_label}</div>
            <div class="kpi-value">{safe_value}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = "") -> None:
    safe_title = html.escape(str(title))
    note_html = f'<div class="section-note">{html.escape(str(note))}</div>' if note else ""
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{safe_title}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def qa_card(tag: str, question: str, answer: str) -> None:
    safe_tag = html.escape(str(tag))
    safe_question = html.escape(str(question))
    safe_answer = html.escape(str(answer))
    st.markdown(
        f"""
        <div class="qa-card">
            <div class="qa-tag">{safe_tag}</div>
            <div class="qa-question">{safe_question}</div>
            <div class="qa-answer">{safe_answer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_interaction_state() -> None:
    defaults = {
        "active_state": None,
        "active_condition": None,
        "chart_filter_version": 0,
        "filter_states": [],
        "filter_conditions": [],
        "filter_ratings": [],
        "filter_ownership": [],
        "filter_min_discharges": 0,
        "filter_positive_only": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chart_filters() -> None:
    st.session_state["active_state"] = None
    st.session_state["active_condition"] = None
    st.session_state["chart_filter_version"] += 1


def clear_map_selection() -> None:
    st.session_state["active_state"] = None
    st.session_state["chart_filter_version"] += 1


def reset_all_filters() -> None:
    st.session_state["filter_states"] = []
    st.session_state["filter_conditions"] = []
    st.session_state["filter_ratings"] = []
    st.session_state["filter_ownership"] = []
    st.session_state["filter_min_discharges"] = 0
    st.session_state["filter_positive_only"] = False
    clear_chart_filters()


def selected_point_value(event: object, fallback_field: str) -> str | None:
    if not event:
        return None
    selection = event.get("selection", {}) if isinstance(event, dict) else getattr(event, "selection", {})
    points = selection.get("points", []) if isinstance(selection, dict) else []
    if not points:
        return None
    point = points[0]
    customdata = point.get("customdata") if isinstance(point, dict) else None
    if customdata:
        return str(customdata[0])
    value = point.get(fallback_field) if isinstance(point, dict) else None
    return None if value is None else str(value)


def apply_chart_selection(event: object, state_key: str, fallback_field: str) -> None:
    selected = selected_point_value(event, fallback_field)
    if selected and st.session_state.get(state_key) != selected:
        st.session_state[state_key] = selected
        st.rerun()


def render_active_filters() -> None:
    chips = []
    if st.session_state.get("active_state"):
        chips.append(f"State: {st.session_state['active_state']}")
    if st.session_state.get("active_condition"):
        chips.append(f"Condition: {st.session_state['active_condition']}")
    if chips:
        chip_html = "".join(
            f'<span class="filter-chip">{html.escape(chip)}</span>' for chip in chips
        )
        st.markdown(chip_html, unsafe_allow_html=True)


def filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("### Filters")
    state_options = sorted(df["state"].dropna().unique())
    condition_options = sorted(df["condition"].dropna().unique())
    rating_options = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Missing Rating"]
    ownership_options = sorted(df["ownership_group"].dropna().unique())

    selected_states = st.sidebar.multiselect(
        "State", state_options, key="filter_states",
        help="Leave empty to include all states."
    )
    selected_conditions = st.sidebar.multiselect(
        "Condition", condition_options, key="filter_conditions",
        help="Leave empty to include all conditions."
    )
    selected_ratings = st.sidebar.multiselect(
        "Overall rating", rating_options, key="filter_ratings",
        help="Leave empty to include all ratings."
    )
    selected_ownership = st.sidebar.multiselect(
        "Ownership", ownership_options, key="filter_ownership",
        help="Leave empty to include all ownership types."
    )
    min_discharges = st.sidebar.slider(
        "Minimum reported discharges",
        min_value=0,
        max_value=1000,
        step=25,
        key="filter_min_discharges",
        help="Rows with suppressed discharge counts are retained when this is 0.",
    )
    only_positive = st.sidebar.toggle(
        "Show only positive estimated excess rows",
        key="filter_positive_only",
        help="Keeps eligible rows whose predicted readmission rate is above the CMS expected rate.",
    )
    st.sidebar.button("Reset all filters", on_click=reset_all_filters, width="stretch")
    has_chart_filters = bool(
        st.session_state.get("active_state") or st.session_state.get("active_condition")
    )
    if has_chart_filters:
        st.sidebar.markdown("### Active Selection")
        if st.session_state.get("active_state"):
            st.sidebar.caption(f"State: {st.session_state['active_state']}")
        if st.session_state.get("active_condition"):
            st.sidebar.caption(f"Condition: {st.session_state['active_condition']}")
        st.sidebar.button("Clear selection", on_click=clear_chart_filters)

    mask = pd.Series(True, index=df.index)
    if selected_states:
        mask &= df["state"].isin(selected_states)
    if selected_conditions:
        mask &= df["condition"].isin(selected_conditions)
    if selected_ratings:
        mask &= df["rating_label"].isin(selected_ratings)
    if selected_ownership:
        mask &= df["ownership_group"].isin(selected_ownership)
    if min_discharges > 0:
        mask &= df["number_of_discharges"].fillna(-1) >= min_discharges
    if only_positive:
        mask &= df["positive_estimated_excess_readmissions"] > 0
    if st.session_state.get("active_state"):
        mask &= df["state"].eq(st.session_state["active_state"])
    if st.session_state.get("active_condition"):
        mask &= df["condition"].eq(st.session_state["active_condition"])
    return df.loc[mask].copy()


def build_kpis(df: pd.DataFrame) -> dict[str, float]:
    numeric = df[df["excess_readmission_ratio"].notna()]
    return {
        "hospitals": numeric["facility_id"].nunique(),
        "rows": len(numeric),
        "avg_err": numeric["excess_readmission_ratio"].mean(),
        "pct_excess": (numeric["excess_readmission_ratio"] > 1).mean(),
        "pct_high": (numeric["excess_readmission_ratio"] >= 1.05).mean(),
        "readmissions": numeric["number_of_readmissions"].sum(),
        "estimated_excess": numeric["positive_estimated_excess_readmissions"].sum(),
    }


def condition_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    return (
        numeric.groupby("condition", as_index=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_excess=("excess_readmission_flag", "mean"),
            readmissions=("number_of_readmissions", "sum"),
            discharges=("number_of_discharges", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            total_rows=("facility_id", "size"),
        )
        .assign(coverage=lambda x: x["eligible_rows"] / x["total_rows"])
        .sort_values("estimated_excess", ascending=True)
    )


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    return (
        numeric.groupby("state", as_index=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_excess=("excess_readmission_flag", "mean"),
            readmissions=("number_of_readmissions", "sum"),
            discharges=("number_of_discharges", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            total_rows=("facility_id", "size"),
        )
        .assign(
            coverage=lambda x: x["eligible_rows"] / x["total_rows"],
            excess_per_1000=lambda x: np.where(
                x["discharges"] > 0,
                1000 * x["estimated_excess"] / x["discharges"],
                np.nan,
            ),
        )
        .sort_values("estimated_excess", ascending=False)
    )


def rating_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    order = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Missing Rating"]
    hospital_level = (
        numeric.groupby(["facility_id", "rating_label"], as_index=False)
        .agg(
            avg_err=("excess_readmission_ratio", "mean"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            total_rows=("facility_id", "size"),
        )
    )
    hospital_level["hospital_above_benchmark"] = hospital_level["avg_err"] > 1
    result = (
        hospital_level.groupby("rating_label", as_index=False)
        .agg(
            hospitals=("facility_id", "size"),
            avg_err=("avg_err", "mean"),
            pct_excess=("hospital_above_benchmark", "mean"),
            estimated_excess=("estimated_excess", "sum"),
            eligible_rows=("eligible_rows", "sum"),
            total_rows=("total_rows", "sum"),
        )
    )
    result["coverage"] = result["eligible_rows"] / result["total_rows"]
    result["rating_label"] = pd.Categorical(result["rating_label"], categories=order, ordered=True)
    return result.sort_values("rating_label")


def ownership_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    return (
        numeric.groupby("ownership_group", as_index=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_excess=("excess_readmission_flag", "mean"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            total_rows=("facility_id", "size"),
        )
        .assign(coverage=lambda x: x["eligible_rows"] / x["total_rows"])
        .sort_values("estimated_excess", ascending=False)
    )


def top_priority_rows(df: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    columns = [
        "facility_id",
        "facility_name",
        "state",
        "condition",
        "excess_readmission_ratio",
        "number_of_discharges",
        "number_of_readmissions",
        "positive_estimated_excess_readmissions",
        "rating_label",
        "ownership_group",
    ]
    top = (
        df[df["positive_estimated_excess_readmissions"] > 0][columns]
        .sort_values("positive_estimated_excess_readmissions", ascending=False)
        .head(limit)
        .copy()
    )
    return top.rename(
        columns={
            "facility_id": "Facility ID",
            "facility_name": "Hospital",
            "state": "State",
            "condition": "Condition",
            "excess_readmission_ratio": "ERR",
            "number_of_discharges": "Discharges",
            "number_of_readmissions": "Readmissions",
            "positive_estimated_excess_readmissions": "Estimated Excess Readmissions",
            "rating_label": "Rating",
            "ownership_group": "Ownership",
        }
    )


def hospital_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    return (
        numeric.groupby(
            [
                "facility_id",
                "facility_name",
                "state",
                "rating_label",
                "ownership_group",
            ],
            as_index=False,
        )
        .agg(
            avg_err=("excess_readmission_ratio", "mean"),
            conditions_above_benchmark=("excess_readmission_flag", "sum"),
            high_concern_conditions=("high_concern_flag", "sum"),
            discharges=("number_of_discharges", "sum"),
            readmissions=("number_of_readmissions", "sum"),
            estimated_excess=("positive_estimated_excess_readmissions", "sum"),
            eligible_rows=("estimated_excess_readmissions", "count"),
            total_rows=("facility_id", "size"),
        )
        .sort_values("estimated_excess", ascending=False)
    )


def qna_metrics(df: pd.DataFrame) -> dict[str, object]:
    numeric = df[df["excess_readmission_ratio"].notna()].copy()
    cond = condition_summary(df).sort_values("estimated_excess", ascending=False)
    states = state_summary(df).sort_values("estimated_excess", ascending=False)
    ratings = rating_summary(df)
    hospitals = hospital_summary(df)
    top_rows = top_priority_rows(df, 5)

    positive_conditions = cond[cond["estimated_excess"] > 0]
    positive_states = states[states["estimated_excess"] > 0]
    positive_hospitals = hospitals[
        (hospitals["eligible_rows"] > 0) & (hospitals["estimated_excess"] > 0)
    ]
    top_condition = positive_conditions.iloc[0] if not positive_conditions.empty else None
    top_state = positive_states.iloc[0] if not positive_states.empty else None
    top_hospital = positive_hospitals.iloc[0] if not positive_hospitals.empty else None

    rating_valid = ratings[
        ratings["rating_label"].astype(str).isin(["1 Star", "2 Star", "3 Star", "4 Star", "5 Star"])
    ].copy()
    rating_spread = np.nan
    low_rating_err = np.nan
    high_rating_err = np.nan
    if not rating_valid.empty:
        low_row = rating_valid[rating_valid["rating_label"].astype(str) == "1 Star"]
        high_row = rating_valid[rating_valid["rating_label"].astype(str) == "5 Star"]
        if not low_row.empty and not high_row.empty:
            low_rating_err = float(low_row.iloc[0]["avg_err"])
            high_rating_err = float(high_row.iloc[0]["avg_err"])
            rating_spread = low_rating_err - high_rating_err

    numeric_rows = int(len(numeric))
    eligible_rows = int(numeric["estimated_excess_readmissions"].notna().sum())
    ineligible_rows = numeric_rows - eligible_rows
    estimate_coverage = eligible_rows / numeric_rows if numeric_rows else np.nan
    positive_rows = int((numeric["positive_estimated_excess_readmissions"] > 0).sum())
    positive_share_eligible = positive_rows / eligible_rows if eligible_rows else np.nan

    return {
        "numeric_rows": numeric_rows,
        "hospitals": int(numeric["facility_id"].nunique()),
        "top_condition": top_condition,
        "top_state": top_state,
        "top_hospital": top_hospital,
        "rating_spread": rating_spread,
        "low_rating_err": low_rating_err,
        "high_rating_err": high_rating_err,
        "eligible_rows": eligible_rows,
        "ineligible_rows": ineligible_rows,
        "estimate_coverage": estimate_coverage,
        "positive_rows": positive_rows,
        "positive_share_eligible": positive_share_eligible,
        "top_rows": top_rows,
    }


def style_plot(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=54, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", color=COLORS["ink"]),
        title=dict(font=dict(size=18, color=COLORS["navy"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=COLORS["line"],
            font=dict(family="Arial", size=13, color=COLORS["ink"]),
            align="left",
        ),
    )
    fig.update_xaxes(gridcolor="#e7eef2", zerolinecolor="#b7c7d0")
    fig.update_yaxes(gridcolor="#e7eef2", zerolinecolor="#b7c7d0")
    return fig


def render_empty_state() -> None:
    st.warning("No rows match the selected filters. Loosen the filters to restore the dashboard.")


init_interaction_state()
df_all = load_data(DATA_PATH)
df_view = filtered_data(df_all)

st.markdown(f'<div class="dashboard-title">{PAGE_TITLE}</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="dashboard-subtitle">
    HRRP performance period: July 2021 - June 2024
    </div>
    """,
    unsafe_allow_html=True,
)
with st.expander("Metric definition, sources, and interpretation limits"):
    st.markdown(
        """
        **Estimated excess readmissions** =
        `max(predicted readmission rate - expected readmission rate, 0) × discharges / 100`.

        This is a rate-gap prioritization proxy—not a causal estimate of preventable readmissions
        or financial penalty exposure. Missing or CMS-suppressed inputs remain unscored rather
        than being treated as zero. State totals measure burden; the per-1,000 view measures
        intensity. Overall-rating comparisons are descriptive because readmission measures
        contribute to the CMS overall rating.

        Sources: [CMS HRRP](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) ·
        [Hospital General Information](https://data.cms.gov/provider-data/dataset/xubh-q36u)
        """
    )
render_active_filters()

if df_view.empty:
    render_empty_state()
    st.stop()

kpis = build_kpis(df_view)

card_cols = st.columns(5)
with card_cols[0]:
    metric_card("Hospitals", format_number(kpis["hospitals"]))
with card_cols[1]:
    metric_card("Average ERR", format_number(kpis["avg_err"], 4), "Benchmark: 1.0000", "blue")
with card_cols[2]:
    metric_card("Above Benchmark", format_pct(kpis["pct_excess"]), accent="gold")
with card_cols[3]:
    metric_card("High Concern", format_pct(kpis["pct_high"]), accent="coral")
with card_cols[4]:
    metric_card(
        "Estimated Excess Readmissions",
        format_number(kpis["estimated_excess"], 1),
        accent="teal",
    )
eligible_rows = int(df_view["estimated_excess_readmissions"].notna().sum())
st.caption(
    f"Excess-readmission estimates use {eligible_rows:,} of {len(df_view):,} filtered hospital-condition rows "
    f"({eligible_rows / len(df_view):.1%} coverage). Missing ERR or discharge values remain unscored; "
    "the metric estimates readmissions above the CMS expected rate and is not a count of preventable events."
)

overview_tab, condition_tab, geography_tab, hospital_tab, qna_tab, detail_tab = st.tabs(
    [
        "Executive Overview",
        "Condition Analysis",
        "Geography",
        "Hospital Benchmarking",
        "Analyst & Business Q&A",
        "Priority Detail",
    ]
)

with overview_tab:
    left, right = st.columns([1.25, 1])
    with left:
        section_header("Heart failure and pneumonia drive most estimated excess readmissions")
        cond = condition_summary(df_view)
        fig = px.bar(
            cond,
            x="estimated_excess",
            y="condition",
            orientation="h",
            custom_data=[
                "condition", "estimated_excess", "readmissions", "discharges",
                "hospitals", "avg_err", "pct_excess", "coverage",
            ],
            color_discrete_sequence=[COLORS["teal"]],
            labels={"estimated_excess": "Estimated excess readmissions", "condition": "Condition"},
            title="Estimated excess readmissions by condition",
            text_auto=".1f",
        )
        fig.update_traces(
            marker_line_color="#1f5853",
            marker_line_width=0.5,
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Estimated excess readmissions: %{customdata[1]:,.1f}<br>"
                "Reported readmissions: %{customdata[2]:,.0f}<br>"
                "Eligible discharges: %{customdata[3]:,.0f}<br>"
                "Hospitals: %{customdata[4]:,}<br>"
                "Average ERR (1.0 = expected): %{customdata[5]:.4f}<br>"
                "Rows above benchmark: %{customdata[6]:.1%}<br>"
                "Estimate coverage: %{customdata[7]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            ),
        )
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"overview_condition_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_condition", "y")
        st.caption("Hover for volume, benchmark, and coverage details. Click a bar to filter the dashboard.")
    with right:
        section_header("Largest total estimated burden is concentrated in a few states")
        states = state_summary(df_view).head(10).sort_values("estimated_excess", ascending=True)
        fig = px.bar(
            states,
            x="estimated_excess",
            y="state",
            orientation="h",
            custom_data=[
                "state", "estimated_excess", "excess_per_1000", "discharges",
                "hospitals", "avg_err", "pct_excess", "coverage",
            ],
            color_discrete_sequence=[COLORS["gold"]],
            labels={"estimated_excess": "Estimated excess readmissions", "state": "State"},
            title="Top 10 states by total estimated excess",
            text_auto=".1f",
        )
        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Estimated excess readmissions: %{customdata[1]:,.1f}<br>"
                "Estimated excess per 1,000 discharges: %{customdata[2]:,.2f}<br>"
                "Eligible discharges: %{customdata[3]:,.0f}<br>"
                "Hospitals: %{customdata[4]:,}<br>"
                "Average ERR (1.0 = expected): %{customdata[5]:.4f}<br>"
                "Rows above benchmark: %{customdata[6]:.1%}<br>"
                "Estimate coverage: %{customdata[7]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            ),
        )
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"overview_state_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_state", "y")
        st.caption("Hover for both total burden and the volume-normalized rate. Click a bar to filter.")

    section_header("Hospital-condition rows to review first")
    st.dataframe(
        top_priority_rows(df_view, 15),
        width="stretch",
        hide_index=True,
        column_config={
            "ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Readmissions": st.column_config.NumberColumn(format="%,.0f"),
            "Estimated Excess Readmissions": st.column_config.NumberColumn(format="%,.1f"),
        },
    )

with condition_tab:
    section_header("Condition performance profile")
    cond = condition_summary(df_view).sort_values("estimated_excess", ascending=False)
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.bar(
            cond.sort_values("estimated_excess"),
            x="estimated_excess",
            y="condition",
            orientation="h",
            custom_data=[
                "condition", "estimated_excess", "readmissions", "discharges",
                "hospitals", "avg_err", "pct_excess", "coverage",
            ],
            color_discrete_sequence=[COLORS["teal"]],
            labels={"estimated_excess": "Estimated excess readmissions", "condition": "Condition"},
            title="Estimated excess readmissions",
            text_auto=".1f",
        )
        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Estimated excess readmissions: %{customdata[1]:,.1f}<br>"
                "Reported readmissions: %{customdata[2]:,.0f}<br>"
                "Eligible discharges: %{customdata[3]:,.0f}<br>"
                "Hospitals: %{customdata[4]:,}<br>"
                "Average ERR (1.0 = expected): %{customdata[5]:.4f}<br>"
                "Rows above benchmark: %{customdata[6]:.1%}<br>"
                "Estimate coverage: %{customdata[7]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            ),
        )
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"condition_opportunity_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_condition", "y")
    with c2:
        fig = px.bar(
            cond.sort_values("readmissions"),
            x="readmissions",
            y="condition",
            orientation="h",
            custom_data=[
                "condition", "readmissions", "estimated_excess", "discharges",
                "hospitals", "avg_err", "pct_excess", "coverage",
            ],
            color_discrete_sequence=[COLORS["blue"]],
            labels={"readmissions": "Reported readmissions", "condition": "Condition"},
        title="Reported readmissions",
            text_auto=",.0f",
        )
        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Reported readmissions: %{customdata[1]:,.0f}<br>"
                "Estimated excess readmissions: %{customdata[2]:,.1f}<br>"
                "Eligible discharges: %{customdata[3]:,.0f}<br>"
                "Hospitals: %{customdata[4]:,}<br>"
                "Average ERR (1.0 = expected): %{customdata[5]:.4f}<br>"
                "Rows above benchmark: %{customdata[6]:.1%}<br>"
                "Estimate coverage: %{customdata[7]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            ),
        )
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"condition_readmissions_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_condition", "y")

    fig = px.box(
        df_view[df_view["excess_readmission_ratio"].notna()],
        x="condition",
        y="excess_readmission_ratio",
        color_discrete_sequence=[COLORS["teal"]],
        labels={"condition": "Condition", "excess_readmission_ratio": "ERR"},
        title="ERR distribution by condition",
    )
    fig.add_hline(y=1.0, line_color=COLORS["coral"], line_width=2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_plot(fig, height=520), width="stretch")
    st.caption(
        "The red line is the CMS expected-performance benchmark (ERR = 1.0). "
        "Hover over a box for distribution statistics."
    )

with geography_tab:
    section_header("Separate total burden from normalized performance intensity")
    states = state_summary(df_view)
    map_metric_col, map_reset_col = st.columns([4, 1], vertical_alignment="bottom")
    with map_metric_col:
        geo_metric_label = st.radio(
            "Map metric",
            ["Total estimated excess readmissions", "Estimated excess per 1,000 discharges"],
            horizontal=True,
        )
    with map_reset_col:
        st.button(
            "Reset map selection",
            on_click=clear_map_selection,
            disabled=not bool(st.session_state.get("active_state")),
            help="Clears the state selected on the map without changing sidebar filters.",
            width="stretch",
        )
    geo_metric = (
        "estimated_excess"
        if geo_metric_label == "Total estimated excess readmissions"
        else "excess_per_1000"
    )
    fig = px.choropleth(
        states,
        locations="state",
        locationmode="USA-states",
        color=geo_metric,
        custom_data=[
            "state", "estimated_excess", "excess_per_1000", "readmissions",
            "discharges", "hospitals", "avg_err", "pct_excess", "coverage",
        ],
        scope="usa",
        color_continuous_scale=[
            [0.0, "#e8f5f7"],
            [0.45, "#6aa9a5"],
            [1.0, "#16324f"],
        ],
        labels={
            "estimated_excess": "Estimated excess readmissions",
            "excess_per_1000": "Estimated excess per 1,000 discharges",
        },
        title=f"{geo_metric_label} by state",
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Estimated excess readmissions: %{customdata[1]:,.1f}<br>"
            "Estimated excess per 1,000 discharges: %{customdata[2]:,.2f}<br>"
            "Reported readmissions: %{customdata[3]:,.0f}<br>"
            "Eligible discharges: %{customdata[4]:,.0f}<br>"
            "Hospitals: %{customdata[5]:,}<br>"
            "Average ERR (1.0 = expected): %{customdata[6]:.4f}<br>"
            "Rows above benchmark: %{customdata[7]:.1%}<br>"
            "Estimate coverage: %{customdata[8]:.1%}<br>"
            f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
        )
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Total" if geo_metric == "estimated_excess" else "Per 1,000"))
    event = st.plotly_chart(
        style_plot(fig, height=560),
        width="stretch",
        key=f"geo_state_{st.session_state['chart_filter_version']}",
        on_select="rerun",
        selection_mode="points",
    )
    apply_chart_selection(event, "active_state", "location")
    st.caption(
        "Hover for total burden, normalized intensity, volume, and coverage. "
        "Click a state to filter the dashboard."
    )

    states_display = states.sort_values(geo_metric, ascending=False)
    st.dataframe(
        states_display.assign(
            avg_err=states_display["avg_err"].round(4),
            pct_excess=(states_display["pct_excess"] * 100).round(1),
            estimated_excess=states_display["estimated_excess"].round(1),
            excess_per_1000=states_display["excess_per_1000"].round(2),
            coverage=(states_display["coverage"] * 100).round(1),
        ).rename(
            columns={
                "state": "State",
                "hospitals": "Hospitals",
                "avg_err": "Average ERR",
                "pct_excess": "% Above Benchmark",
                "readmissions": "Readmissions",
                "discharges": "Discharges",
                "estimated_excess": "Estimated Excess Readmissions",
                "excess_per_1000": "Estimated Excess per 1,000 Discharges",
                "coverage": "Eligible Coverage %",
            }
        ),
        width="stretch",
        hide_index=True,
    )

with hospital_tab:
    section_header("Hospital characteristics")
    c1, c2 = st.columns([1, 1])
    with c1:
        rating = rating_summary(df_view)
        fig = px.scatter(
            rating,
            x="rating_label",
            y="avg_err",
            color_discrete_sequence=[COLORS["blue"]],
            labels={"rating_label": "Overall rating", "avg_err": "Average ERR"},
            title="Average ERR by overall rating (descriptive, partly circular)",
            custom_data=[
                "rating_label", "avg_err", "hospitals", "pct_excess",
                "estimated_excess", "coverage",
            ],
        )
        fig.update_traces(
            marker=dict(size=13, color=COLORS["blue"], line=dict(width=1, color=COLORS["navy"])),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Average ERR (1.0 = expected): %{customdata[1]:.4f}<br>"
                "Hospitals: %{customdata[2]:,}<br>"
                "Hospitals above benchmark: %{customdata[3]:.1%}<br>"
                "Estimated excess readmissions: %{customdata[4]:,.1f}<br>"
                "Estimate coverage: %{customdata[5]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            ),
        )
        fig.add_hline(y=1.0, line_color=COLORS["coral"], line_width=2)
        fig.update_yaxes(range=[0.94, 1.06])
        st.plotly_chart(style_plot(fig), width="stretch")
        st.caption(
            "Descriptive only: readmission measures contribute to the CMS overall rating, "
            "so this is not an independent relationship."
        )
    with c2:
        ownership = ownership_summary(df_view).head(10).sort_values("estimated_excess")
        fig = px.bar(
            ownership,
            x="estimated_excess",
            y="ownership_group",
            orientation="h",
            color_discrete_sequence=[COLORS["teal"]],
            labels={"estimated_excess": "Estimated excess readmissions", "ownership_group": "Ownership"},
            title="Total estimated excess by ownership (size-sensitive)",
            custom_data=[
                "ownership_group", "estimated_excess", "hospitals", "avg_err",
                "pct_excess", "coverage",
            ],
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Estimated excess readmissions: %{customdata[1]:,.1f}<br>"
                "Hospitals: %{customdata[2]:,}<br>"
                "Average ERR (1.0 = expected): %{customdata[3]:.4f}<br>"
                "Rows above benchmark: %{customdata[4]:.1%}<br>"
                "Estimate coverage: %{customdata[5]:.1%}<br>"
                f"Period: {MEASUREMENT_PERIOD}<extra></extra>"
            )
        )
        st.plotly_chart(style_plot(fig), width="stretch")
        st.caption(
            "Totals are size-sensitive: ownership groups with more hospitals or discharges "
            "can rank higher even at similar performance."
        )

    section_header("Select a hospital")
    hospitals = (
        df_view[["facility_id", "facility_name", "state"]]
        .drop_duplicates()
        .sort_values(["facility_name", "state"])
    )
    hospital_labels = (
        hospitals["facility_name"] + " (" + hospitals["state"] + ", " + hospitals["facility_id"] + ")"
    ).tolist()
    selected_label = st.selectbox("Hospital", hospital_labels)
    selected_id = selected_label.rsplit(", ", 1)[-1].replace(")", "")
    hospital_df = df_view[df_view["facility_id"] == selected_id].copy()
    benchmark = (
        df_view[df_view["excess_readmission_ratio"].notna()]
        .groupby("condition", as_index=False)["excess_readmission_ratio"]
        .mean()
        .rename(columns={"excess_readmission_ratio": "Filtered benchmark ERR"})
    )
    comparison = hospital_df.merge(benchmark, on="condition", how="left")
    comparison = comparison[
        [
            "condition",
            "excess_readmission_ratio",
            "Filtered benchmark ERR",
            "number_of_discharges",
            "positive_estimated_excess_readmissions",
            "performance_category",
        ]
    ].rename(
        columns={
            "condition": "Condition",
            "excess_readmission_ratio": "Hospital ERR",
            "number_of_discharges": "Discharges",
            "positive_estimated_excess_readmissions": "Estimated Excess Readmissions",
            "performance_category": "Performance Category",
        }
    )
    st.dataframe(
        comparison,
        width="stretch",
        hide_index=True,
        column_config={
            "Hospital ERR": st.column_config.NumberColumn(format="%.4f"),
            "Filtered benchmark ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Estimated Excess Readmissions": st.column_config.NumberColumn(format="%,.1f"),
        },
    )

with qna_tab:
    section_header("Analyst & Business Q&A")
    qna = qna_metrics(df_view)
    top_condition = qna["top_condition"]
    top_state = qna["top_state"]
    top_hospital = qna["top_hospital"]

    analyst_left, analyst_right = st.columns(2)
    with analyst_left:
        qa_card(
            "Data Analyst",
            "What is the grain of this dashboard?",
            (
                f"{format_number(qna['numeric_rows'])} hospital-condition rows with numeric ERR, "
                f"covering {format_number(qna['hospitals'])} hospitals under the current filters."
            ),
        )
        qa_card(
            "Data Analyst",
            "How should ERR be interpreted?",
            (
                "ERR above 1.0 means readmissions are higher than expected after CMS risk adjustment; "
                "ERR below 1.0 means better-than-expected performance."
            ),
        )
        qa_card(
            "Data Analyst",
            "How complete are the estimated-excess calculations?",
            (
                f"{format_number(qna['eligible_rows'])} of {format_number(qna['numeric_rows'])} filtered "
                f"numeric-ERR rows are eligible ({format_pct(qna['estimate_coverage'])} coverage). "
                f"The remaining {format_number(qna['ineligible_rows'])} rows lack at least one required "
                "rate or discharge-volume input and remain unscored."
            ),
        )
    with analyst_right:
        qa_card(
            "Business",
            "Which condition has the largest total measured burden?",
            (
                f"Under the current filters, {top_condition['condition']} has the largest total with "
                f"{format_number(top_condition['estimated_excess'], 1)} estimated excess readmissions and "
                f"{format_number(top_condition['readmissions'])} reported readmissions. This ranks total burden, "
                "not excess per 1,000 discharges."
                if top_condition is not None
                else "No condition has positive measured estimated excess under the current filters."
            ),
        )
        qa_card(
            "Business",
            "Which market has the largest total estimated burden?",
            (
                f"Under the current filters, {top_state['state']} ranks highest by total burden with "
                f"{format_number(top_state['estimated_excess'], 1)} estimated excess readmissions across "
                f"{format_number(top_state['hospitals'])} hospitals. This is not the per-1,000 intensity ranking."
                if top_state is not None
                else "No state has positive measured estimated excess under the current filters."
            ),
        )
        qa_card(
            "Business",
            "Which hospital has the largest measured burden?",
            (
                f"Under the current filters, {top_hospital['facility_name']} in {top_hospital['state']} has the "
                f"largest measured hospital-level total at {format_number(top_hospital['estimated_excess'], 1)} "
                "estimated excess readmissions. This identifies a review candidate, not proven preventable events."
                if top_hospital is not None
                else "No hospital has positive estimated excess under the current filters."
            ),
        )

    st.divider()
    insight_cols = st.columns(3)
    with insight_cols[0]:
        qa_card(
            "Business",
            "How should the rating comparison be interpreted?",
            (
                f"Using one average ERR per hospital in this filtered view, the 1-star average is "
                f"{format_number(qna['low_rating_err'], 4)} versus {format_number(qna['high_rating_err'], 4)} "
                "for 5-star hospitals "
                f"(gap: {format_number(qna['rating_spread'], 4)}). This is descriptive and partly circular because readmission measures contribute to the CMS overall rating."
                if not pd.isna(qna["rating_spread"])
                else "The current filters do not include enough 1-star and 5-star data to compare."
            ),
        )
    with insight_cols[1]:
        qa_card(
            "Business",
            "How many rows have positive estimated excess?",
            (
                f"{format_number(qna['positive_rows'])} of {format_number(qna['eligible_rows'])} eligible "
                f"hospital-condition rows ({format_pct(qna['positive_share_eligible'])}) have positive estimated "
                "excess under the current filters."
            ),
        )
    with insight_cols[2]:
        qa_card(
            "Business",
            "What is the recommended action?",
            (
                "Use high estimated-excess hospital-condition pairs as a screening list, then validate local "
                "discharge planning, care-transition workflows, and condition-specific drivers. The proxy is "
                "not a causal estimate of preventable readmissions or a financial-penalty calculation."
            ),
        )

    section_header("Top Answers Table")
    st.dataframe(
        qna["top_rows"],
        width="stretch",
        hide_index=True,
        column_config={
            "ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Readmissions": st.column_config.NumberColumn(format="%,.0f"),
            "Estimated Excess Readmissions": st.column_config.NumberColumn(format="%,.1f"),
        },
    )

with detail_tab:
    section_header("Priority Detail")
    row_limit = st.slider("Rows to display", min_value=25, max_value=500, value=100, step=25)
    detail = top_priority_rows(df_view, row_limit)
    st.dataframe(
        detail,
        width="stretch",
        hide_index=True,
        column_config={
            "ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Readmissions": st.column_config.NumberColumn(format="%,.0f"),
            "Estimated Excess Readmissions": st.column_config.NumberColumn(format="%,.1f"),
        },
    )
    st.download_button(
        "Download filtered priority rows",
        data=detail.to_csv(index=False).encode("utf-8"),
        file_name="filtered_readmission_priority_rows.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download all filtered records with eligibility status",
        data=df_view.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_readmissions_with_eligibility.csv",
        mime="text/csv",
    )

