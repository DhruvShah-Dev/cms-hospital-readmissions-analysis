# CMS Hospital Readmissions Opportunity Analysis

Professional healthcare analytics case study using real CMS data to identify hospitals, conditions, and markets with the greatest opportunity to reduce preventable 30-day readmissions.

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
- Opportunity score combining excess readmission performance and patient volume
- SQL views for national, condition, state, ownership, rating, hospital, and opportunity analysis
- Statistical tests for rating, ownership, geography, condition, and volume relationships
- Professional Streamlit dashboard with filters, KPI cards, U.S. map, hospital benchmarking, Q&A page, and downloadable detail table
- Excel workbook with executive summary, condition analysis, state analysis, hospital priorities, and model data

## Dashboard Pages

- **Executive Overview**: headline KPIs, top conditions, top states, and initial priority hospitals
- **Condition Analysis**: condition opportunity, readmission volume, and ERR distributions
- **Geography**: U.S. state opportunity map and state-level performance table
- **Hospital Benchmarking**: rating and ownership analysis plus hospital-level drilldown
- **Analyst & Business Q&A**: concise answers to data analyst and stakeholder questions
- **Opportunity Detail**: filtered detail table for follow-up and Power BI modeling

## Data Sources

- CMS Hospital Readmissions Reduction Program: https://data.cms.gov/provider-data/dataset/9n3s-kdb3
- CMS Hospital General Information: https://data.cms.gov/provider-data/dataset/xubh-q36u

Raw source files are stored unchanged in `data/raw/`.

## Current Findings

- 11,720 hospital-condition rows have numeric ERR values.
- 48.1% of numeric ERR rows are above the CMS benchmark of 1.0.
- Pneumonia has the largest measured positive opportunity score, followed by Heart Failure.
- Florida, California, Massachusetts, New York, and Illinois are the highest-opportunity states in the national view.
- One-star hospitals show meaningfully higher average ERR than five-star hospitals.
- Volume has a weak relationship with ERR, so it is more useful for sizing opportunity than explaining risk-adjusted performance.

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

**Opportunity Score**  
Directional prioritization metric:

```text
(ERR - 1) * Number of Discharges
```

Only positive opportunity is used for ranking intervention targets.

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

## Notes

Power BI artifacts are intentionally not included yet. The dashboard and processed datasets are structured so a Power BI version can be added later.
