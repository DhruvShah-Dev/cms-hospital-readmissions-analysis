# SQL Layer

This folder contains the SQL layer for the CMS hospital readmissions case study.

Run the full SQL build from the project root:

```powershell
python scripts/build_sql_layer.py
```

The script loads the processed CSVs into:

```text
data/processed/readmissions.db
```

## Files

| File | Purpose |
| --- | --- |
| `01_schema.sql` | Drops stale views and creates indexes for the loaded SQLite tables. |
| `02_analysis_views.sql` | Defines reusable analytical views for national, condition, geography, ownership, rating, hospital, and opportunity analysis. |
| `03_analysis_queries.sql` | Example stakeholder-facing SQL queries. |

## Core Views

| View | Grain |
| --- | --- |
| `v_national_summary` | One national summary row. |
| `v_condition_summary` | One row per condition. |
| `v_state_summary` | One row per state. |
| `v_region_summary` | One row per region. |
| `v_ownership_summary` | One row per ownership category. |
| `v_rating_summary` | One row per overall rating group. |
| `v_hospital_summary` | One row per hospital. |
| `v_opportunity_ranking` | One row per positive hospital-condition opportunity. |
| `v_unmatched_hrrp_facilities` | HRRP facility IDs missing hospital attributes. |
