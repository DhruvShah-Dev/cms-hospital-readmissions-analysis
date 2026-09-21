from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "processed" / "hospital_readmissions_analytic.csv"

PAGE_TITLE = "CMS Hospital Readmissions Opportunity"

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
    df["positive_opportunity_score"] = df["positive_opportunity_score"].fillna(0)
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
    note_html = f'<div class="kpi-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color:{border_color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, note: str = "") -> None:
    note_html = f'<div class="section-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def qa_card(tag: str, question: str, answer: str) -> None:
    st.markdown(
        f"""
        <div class="qa-card">
            <div class="qa-tag">{tag}</div>
            <div class="qa-question">{question}</div>
            <div class="qa-answer">{answer}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_interaction_state() -> None:
    defaults = {
        "active_state": None,
        "active_condition": None,
        "chart_filter_version": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_chart_filters() -> None:
    st.session_state["active_state"] = None
    st.session_state["active_condition"] = None
    st.session_state["chart_filter_version"] += 1


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
        chip_html = "".join(f'<span class="filter-chip">{chip}</span>' for chip in chips)
        st.markdown(chip_html, unsafe_allow_html=True)


def filtered_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("### Filters")
    state_options = sorted(df["state"].dropna().unique())
    condition_options = sorted(df["condition"].dropna().unique())
    rating_options = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Missing Rating"]
    ownership_options = sorted(df["ownership_group"].dropna().unique())

    selected_states = st.sidebar.multiselect("State", state_options, default=state_options)
    selected_conditions = st.sidebar.multiselect(
        "Condition", condition_options, default=condition_options
    )
    selected_ratings = st.sidebar.multiselect(
        "Overall rating", rating_options, default=rating_options
    )
    selected_ownership = st.sidebar.multiselect(
        "Ownership", ownership_options, default=ownership_options
    )
    min_discharges = st.sidebar.slider(
        "Minimum reported discharges",
        min_value=0,
        max_value=1000,
        value=0,
        step=25,
        help="Rows with suppressed discharge counts are retained when this is 0.",
    )
    only_positive = st.sidebar.toggle(
        "Show only positive opportunity rows",
        value=False,
        help="Keeps rows where the opportunity score is greater than 0.",
    )
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

    mask = (
        df["state"].isin(selected_states)
        & df["condition"].isin(selected_conditions)
        & df["rating_label"].isin(selected_ratings)
        & df["ownership_group"].isin(selected_ownership)
    )
    if min_discharges > 0:
        mask &= df["number_of_discharges"].fillna(-1) >= min_discharges
    if only_positive:
        mask &= df["positive_opportunity_score"] > 0
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
        "opportunity": numeric["positive_opportunity_score"].sum(),
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
            opportunity=("positive_opportunity_score", "sum"),
        )
        .sort_values("opportunity", ascending=True)
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
            opportunity=("positive_opportunity_score", "sum"),
        )
        .sort_values("opportunity", ascending=False)
    )


def rating_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df[df["excess_readmission_ratio"].notna()]
    order = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Missing Rating"]
    result = (
        numeric.groupby("rating_label", as_index=False)
        .agg(
            hospitals=("facility_id", "nunique"),
            avg_err=("excess_readmission_ratio", "mean"),
            pct_excess=("excess_readmission_flag", "mean"),
            opportunity=("positive_opportunity_score", "sum"),
        )
    )
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
            opportunity=("positive_opportunity_score", "sum"),
        )
        .sort_values("opportunity", ascending=False)
    )


def top_opportunity_rows(df: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    columns = [
        "facility_id",
        "facility_name",
        "state",
        "condition",
        "excess_readmission_ratio",
        "number_of_discharges",
        "number_of_readmissions",
        "positive_opportunity_score",
        "rating_label",
        "ownership_group",
    ]
    top = (
        df[df["positive_opportunity_score"] > 0][columns]
        .sort_values("positive_opportunity_score", ascending=False)
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
            "positive_opportunity_score": "Opportunity Score",
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
            opportunity=("positive_opportunity_score", "sum"),
        )
        .sort_values("opportunity", ascending=False)
    )


def qna_metrics(df: pd.DataFrame) -> dict[str, object]:
    numeric = df[df["excess_readmission_ratio"].notna()].copy()
    cond = condition_summary(df).sort_values("opportunity", ascending=False)
    states = state_summary(df).sort_values("opportunity", ascending=False)
    ratings = rating_summary(df)
    hospitals = hospital_summary(df)
    top_rows = top_opportunity_rows(df, 5)

    top_condition = cond.iloc[0] if not cond.empty else None
    top_state = states.iloc[0] if not states.empty else None
    top_hospital = hospitals.iloc[0] if not hospitals.empty else None

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

    missing_volume_rows = int(numeric["number_of_discharges"].isna().sum())
    numeric_rows = int(len(numeric))
    positive_rows = int((numeric["positive_opportunity_score"] > 0).sum())

    return {
        "numeric_rows": numeric_rows,
        "hospitals": int(numeric["facility_id"].nunique()),
        "top_condition": top_condition,
        "top_state": top_state,
        "top_hospital": top_hospital,
        "rating_spread": rating_spread,
        "low_rating_err": low_rating_err,
        "high_rating_err": high_rating_err,
        "missing_volume_rows": missing_volume_rows,
        "positive_rows": positive_rows,
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
        "Opportunity Score",
        format_number(kpis["opportunity"], 1),
        accent="teal",
    )

overview_tab, condition_tab, geography_tab, hospital_tab, qna_tab, detail_tab = st.tabs(
    [
        "Executive Overview",
        "Condition Analysis",
        "Geography",
        "Hospital Benchmarking",
        "Analyst & Business Q&A",
        "Opportunity Detail",
    ]
)

with overview_tab:
    left, right = st.columns([1.25, 1])
    with left:
        section_header("Opportunity by Condition")
        cond = condition_summary(df_view)
        fig = px.bar(
            cond,
            x="opportunity",
            y="condition",
            orientation="h",
            custom_data=["condition"],
            color_discrete_sequence=[COLORS["teal"]],
            labels={"opportunity": "Positive opportunity score", "condition": "Condition"},
            title="Positive Opportunity Score by Condition",
            hover_data={
                "hospitals": ":,",
                "avg_err": ":.4f",
                "pct_excess": ":.1%",
                "readmissions": ":,.0f",
            },
        )
        fig.update_traces(marker_line_color="#1f5853", marker_line_width=0.5)
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"overview_condition_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_condition", "y")
    with right:
        section_header("Top States by Opportunity")
        states = state_summary(df_view).head(10).sort_values("opportunity", ascending=True)
        fig = px.bar(
            states,
            x="opportunity",
            y="state",
            orientation="h",
            custom_data=["state"],
            color_discrete_sequence=[COLORS["gold"]],
            labels={"opportunity": "Positive opportunity score", "state": "State"},
            title="Top 10 States",
            hover_data={"hospitals": ":,", "avg_err": ":.4f", "pct_excess": ":.1%"},
        )
        event = st.plotly_chart(
            style_plot(fig),
            width="stretch",
            key=f"overview_state_{st.session_state['chart_filter_version']}",
            on_select="rerun",
            selection_mode="points",
        )
        apply_chart_selection(event, "active_state", "y")

    section_header("Initial Hospital-Condition Priorities")
    st.dataframe(
        top_opportunity_rows(df_view, 15),
        width="stretch",
        hide_index=True,
        column_config={
            "ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Readmissions": st.column_config.NumberColumn(format="%,.0f"),
            "Opportunity Score": st.column_config.NumberColumn(format="%,.1f"),
        },
    )

with condition_tab:
    section_header("Condition Performance Profile")
    cond = condition_summary(df_view).sort_values("opportunity", ascending=False)
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.bar(
            cond.sort_values("opportunity"),
            x="opportunity",
            y="condition",
            orientation="h",
            custom_data=["condition"],
            color_discrete_sequence=[COLORS["teal"]],
            labels={"opportunity": "Positive opportunity score", "condition": "Condition"},
            title="Opportunity Score",
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
            custom_data=["condition"],
            color_discrete_sequence=[COLORS["blue"]],
            labels={"readmissions": "Reported readmissions", "condition": "Condition"},
            title="Reported Readmissions",
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
        color="condition",
        color_discrete_sequence=[
            COLORS["teal"],
            COLORS["blue"],
            COLORS["gold"],
            COLORS["coral"],
            "#6d7fb3",
            "#7c8f65",
        ],
        labels={"condition": "Condition", "excess_readmission_ratio": "ERR"},
        title="ERR Distribution by Condition",
    )
    fig.add_hline(y=1.0, line_color=COLORS["coral"], line_width=2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(style_plot(fig, height=520), width="stretch")

with geography_tab:
    section_header("Geographic Opportunity Map")
    states = state_summary(df_view)
    fig = px.choropleth(
        states,
        locations="state",
        locationmode="USA-states",
        color="opportunity",
        custom_data=["state"],
        scope="usa",
        color_continuous_scale=[
            [0.0, "#e8f5f7"],
            [0.45, "#6aa9a5"],
            [1.0, "#16324f"],
        ],
        labels={"opportunity": "Opportunity Score"},
        hover_data={
            "state": False,
            "hospitals": ":,",
            "avg_err": ":.4f",
            "pct_excess": ":.1%",
            "readmissions": ":,.0f",
        },
        title="Opportunity Score by State",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Opportunity"))
    event = st.plotly_chart(
        style_plot(fig, height=560),
        width="stretch",
        key=f"geo_state_{st.session_state['chart_filter_version']}",
        on_select="rerun",
        selection_mode="points",
    )
    apply_chart_selection(event, "active_state", "location")

    st.dataframe(
        states.assign(
            avg_err=states["avg_err"].round(4),
            pct_excess=(states["pct_excess"] * 100).round(1),
            opportunity=states["opportunity"].round(1),
        ).rename(
            columns={
                "state": "State",
                "hospitals": "Hospitals",
                "avg_err": "Average ERR",
                "pct_excess": "% Above Benchmark",
                "readmissions": "Readmissions",
                "discharges": "Discharges",
                "opportunity": "Opportunity Score",
            }
        ),
        width="stretch",
        hide_index=True,
    )

with hospital_tab:
    section_header("Hospital Characteristics")
    c1, c2 = st.columns([1, 1])
    with c1:
        rating = rating_summary(df_view)
        fig = px.bar(
            rating,
            x="rating_label",
            y="avg_err",
            color_discrete_sequence=[COLORS["blue"]],
            labels={"rating_label": "Overall rating", "avg_err": "Average ERR"},
            title="Average ERR by Overall Rating",
            hover_data={"hospitals": ":,", "pct_excess": ":.1%", "opportunity": ":,.1f"},
        )
        fig.add_hline(y=1.0, line_color=COLORS["coral"], line_width=2)
        st.plotly_chart(style_plot(fig), width="stretch")
    with c2:
        ownership = ownership_summary(df_view).head(10).sort_values("opportunity")
        fig = px.bar(
            ownership,
            x="opportunity",
            y="ownership_group",
            orientation="h",
            color_discrete_sequence=[COLORS["teal"]],
            labels={"opportunity": "Opportunity score", "ownership_group": "Ownership"},
            title="Opportunity by Ownership",
            hover_data={"hospitals": ":,", "avg_err": ":.4f", "pct_excess": ":.1%"},
        )
        st.plotly_chart(style_plot(fig), width="stretch")

    section_header("Select a Hospital")
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
            "positive_opportunity_score",
            "performance_category",
        ]
    ].rename(
        columns={
            "condition": "Condition",
            "excess_readmission_ratio": "Hospital ERR",
            "number_of_discharges": "Discharges",
            "positive_opportunity_score": "Opportunity Score",
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
            "Opportunity Score": st.column_config.NumberColumn(format="%,.1f"),
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
            "What data limitation matters most?",
            (
                f"{format_number(qna['missing_volume_rows'])} filtered numeric-ERR rows have suppressed or missing "
                "discharge volume, so volume-based opportunity scoring excludes those rows."
            ),
        )
    with analyst_right:
        qa_card(
            "Business",
            "Which condition should be reviewed first?",
            (
                f"{top_condition['condition']} leads the filtered view with "
                f"{format_number(top_condition['opportunity'], 1)} opportunity score and "
                f"{format_number(top_condition['readmissions'])} reported readmissions."
                if top_condition is not None
                else "No condition has enough numeric data under the current filters."
            ),
        )
        qa_card(
            "Business",
            "Which market has the greatest opportunity?",
            (
                f"{top_state['state']} ranks highest with "
                f"{format_number(top_state['opportunity'], 1)} opportunity score across "
                f"{format_number(top_state['hospitals'])} hospitals."
                if top_state is not None
                else "No state has enough numeric data under the current filters."
            ),
        )
        qa_card(
            "Business",
            "Which hospital should be prioritized?",
            (
                f"{top_hospital['facility_name']} in {top_hospital['state']} has the highest filtered hospital-level "
                f"opportunity score at {format_number(top_hospital['opportunity'], 1)}."
                if top_hospital is not None
                else "No hospital has positive opportunity under the current filters."
            ),
        )

    st.divider()
    insight_cols = st.columns(3)
    with insight_cols[0]:
        qa_card(
            "Business",
            "Do lower-rated hospitals perform worse?",
            (
                f"In this filtered view, 1-star average ERR is {format_number(qna['low_rating_err'], 4)} "
                f"versus 5-star average ERR {format_number(qna['high_rating_err'], 4)} "
                f"(gap: {format_number(qna['rating_spread'], 4)})."
                if not pd.isna(qna["rating_spread"])
                else "The current filters do not include enough 1-star and 5-star data to compare."
            ),
        )
    with insight_cols[1]:
        qa_card(
            "Business",
            "How many rows represent actionable excess opportunity?",
            (
                f"{format_number(qna['positive_rows'])} hospital-condition rows have positive opportunity "
                "under the current filters."
            ),
        )
    with insight_cols[2]:
        qa_card(
            "Business",
            "What is the recommended action?",
            (
                "Start with high-opportunity hospital-condition pairs, then validate local discharge planning, "
                "care-transition workflows, and condition-specific readmission drivers."
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
            "Opportunity Score": st.column_config.NumberColumn(format="%,.1f"),
        },
    )

with detail_tab:
    section_header("Opportunity Detail")
    row_limit = st.slider("Rows to display", min_value=25, max_value=500, value=100, step=25)
    detail = top_opportunity_rows(df_view, row_limit)
    st.dataframe(
        detail,
        width="stretch",
        hide_index=True,
        column_config={
            "ERR": st.column_config.NumberColumn(format="%.4f"),
            "Discharges": st.column_config.NumberColumn(format="%,.0f"),
            "Readmissions": st.column_config.NumberColumn(format="%,.0f"),
            "Opportunity Score": st.column_config.NumberColumn(format="%,.1f"),
        },
    )
    st.download_button(
        "Download filtered opportunity rows",
        data=detail.to_csv(index=False).encode("utf-8"),
        file_name="filtered_readmission_opportunity_rows.csv",
        mime="text/csv",
    )

