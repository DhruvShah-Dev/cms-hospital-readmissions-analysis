# CMS Hospital Readmissions Prioritization Analysis

Source-backed healthcare analytics case study using CMS data to identify where measured readmissions exceed risk-adjusted expectations. The analysis prioritizes review; it does not claim that excess readmissions are preventable or caused by hospital practices.

## Project Summary

Under the CMS Hospital Readmissions Reduction Program, hospitals with excess readmissions can face Medicare payment reductions. This project analyzes CMS HRRP and Hospital General Information data to answer:

> Which hospitals, conditions, and geographic markets show the greatest opportunities for reducing 30-day readmissions, and what hospital characteristics are associated with better or worse performance?

The project includes a complete analytics workflow: raw data profiling, cleaning, feature engineering, SQL modeling, statistical analysis, and a polished Streamlit dashboard.
An Excel executive workbook is included for stakeholder review and offline analysis.

## Live Dashboard Locally

Run the Streamlit dashboard:

```powershell
python -m streamlit run streamlit_app.py
```

## Key Features

- Source-backed healthcare analytics case study using CMS Provider Data Catalog files
- Cleaned hospital-condition analytic dataset at HRRP measure grain
- Estimated excess-readmissions proxy combining the predicted-versus-expected rate gap with eligible discharge volume
- Total and normalized geographic views that separate burden from performance intensity
- SQL views for national, condition, state, ownership, rating, hospital, and priority analysis
- Statistical tests for rating, ownership, geography, condition, and volume relationships
- Professional Streamlit dashboard with filters, KPI cards, click-to-filter charts, U.S. map, hospital benchmarking, Q&A page, and downloadable detail table
- Excel workbook with executive summary, condition analysis, state analysis, hospital priorities, and model data

## Dashboard Pages

- **Executive Overview**: headline KPIs, top conditions, top states, and initial priority hospitals
- **Condition Analysis**: estimated excess readmissions, readmission volume, and ERR distributions
- **Geography**: total burden versus estimated excess per 1,000 eligible discharges
- **Hospital Benchmarking**: rating and ownership analysis plus hospital-level drilldown
- **Analyst & Business Q&A**: concise answers to data analyst and stakeholder questions
- **Priority Detail**: filtered hospital-condition rows for follow-up and modeling

## Data Sources

- CMS Hospital Readmissions Reduction Program: https://data.cms.gov/provider-data/dataset/9n3s-kdb3
- CMS Hospital General Information: https://data.cms.gov/provider-data/dataset/xubh-q36u

Raw source files are stored unchanged in `data/raw/`.

## Current Findings

- 11,720 hospital-condition rows have numeric ERR values.
- 48.1% of numeric ERR rows are above the CMS benchmark of 1.0.
- Heart Failure and Pneumonia account for most of the estimated excess-readmission burden among rows with reportable volume.
- State totals identify where burden is largest; the normalized per-1,000 view produces a different ranking and is better for performance-intensity comparisons.
- One-star hospitals show higher average ERR than five-star hospitals, but this is descriptive and partly circular because readmission measures contribute to the CMS overall rating.
- Volume has a weak relationship with ERR, so it is more useful for sizing estimated burden than explaining risk-adjusted performance.

## Project Structure

```text
.
|-- .streamlit/
|   `-- config.toml
|-- data/
|   |-- raw/
|   `-- processed/
|-- images/
|-- notebooks/
|-- excel/
|-- reports/
|-- scripts/
|-- sql/
|-- data_dictionary.md
|-- requirements.txt
`-- streamlit_app.py
```

## Reproduce The Analysis

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the pipeline:

```powershell
python scripts/profile_cms_readmissions.py
python scripts/build_clean_dataset.py
python scripts/build_sql_layer.py
python scripts/run_eda_statistical_analysis.py
python scripts/build_excel_workbook.py
```

Launch the dashboard:

```powershell
python -m streamlit run streamlit_app.py
```

## Key Artifacts

- `streamlit_app.py` - interactive dashboard
- `excel/cms_readmissions_executive_workbook.xlsx` - executive Excel workbook
- `data_dictionary.md` - field definitions and derived metric logic
- `reports/01_data_profile.md` - raw data profile
- `reports/02_cleaning_report.md` - cleaning and validation report
- `reports/03_sql_analysis_report.md` - SQL layer output summary
- `reports/04_eda_statistical_analysis_report.md` - EDA and statistical analysis
- `sql/02_analysis_views.sql` - reusable SQL views

## Metric Definitions

**Excess Readmission Ratio (ERR)**  
CMS risk-adjusted performance metric. ERR above 1.0 indicates readmissions are higher than expected; ERR below 1.0 indicates better-than-expected performance.

**Readmission Gap**  
Predicted readmission rate minus expected readmission rate.

**Estimated Excess Readmissions**
Rate-gap-based prioritization proxy:

```text
(Predicted Readmission Rate - Expected Readmission Rate) * Number of Discharges / 100
```

Only positive estimates are used for burden ranking. Missing or suppressed inputs remain missing rather than being converted to zero. The result is not a causal estimate of preventable readmissions or financial penalty exposure.

**Normalized Geographic Intensity**

```text
Estimated Excess Readmissions / Eligible Discharges * 1,000
```

Use totals to locate aggregate burden and the normalized measure to compare intensity across differently sized states.

## Interpretation Limits

- The measurement period is July 1, 2021 through June 30, 2024; this is not live performance.
- CMS suppresses many low-volume rows, so the eligible subset is not a random sample.
- Overall hospital rating is not an independent predictor of readmission performance because readmission measures contribute to the rating.
- State and ownership comparisons are descriptive and do not adjust for hospital or patient mix.
- Local clinical and care-transition data are required before selecting an intervention.

## Tech Stack

- Python
- Pandas
- SQLite
- SQL
- SciPy
- Plotly
- Streamlit
- CMS healthcare data

## Tags

`healthcare-analytics` `cms-data` `hospital-readmissions` `streamlit` `python` `sql` `pandas` `plotly` `healthcare-dashboard` `data-analysis` `portfolio-project`

## Quality Controls

Run `pytest` to validate metric formulas, missing-versus-zero behavior, aggregation, and key dataset invariants. GitHub Actions runs the same checks for proposed changes.
