# Data Dictionary

## Raw Sources

Raw CMS files are stored unchanged in `data/raw/`.

- `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- `Hospital_General_Information.csv`

## Processed Tables

### `data/processed/hrrp_clean.csv`

Grain: one row per hospital and HRRP condition measure.

Key fields:

| Field | Description |
| --- | --- |
| `facility_id` | CMS hospital identifier. |
| `facility_name` | Hospital name from HRRP. |
| `state` | Hospital state abbreviation. |
| `measure_name` | CMS HRRP measure code. |
| `condition` | Readable condition label. |
| `condition_short` | Short condition label for charts. |
| `number_of_discharges` | Numeric discharge volume where CMS reports it. |
| `excess_readmission_ratio` | CMS ERR: predicted readmissions divided by expected readmissions. |
| `predicted_readmission_rate` | Hospital predicted 30-day readmission rate. |
| `expected_readmission_rate` | Risk-adjusted expected readmission rate. |
| `number_of_readmissions` | Numeric readmission count where CMS reports it. |
| `readmission_gap` | `predicted_readmission_rate - expected_readmission_rate`. |
| `readmission_gap_pct` | Readmission gap divided by expected rate, multiplied by 100. |
| `excess_readmission_flag` | `True` when ERR is greater than 1. |
| `high_concern_flag` | `True` when ERR is at least 1.05. |
| `performance_category` | ERR band for benchmarking. |
| `opportunity_score` | `(ERR - 1) * number_of_discharges` where both inputs are numeric. |
| `positive_opportunity_score` | Opportunity score floored at 0. |
| `priority_category` | Directional prioritization band based on opportunity score. |

### `data/processed/hospital_general_info_clean.csv`

Grain: one row per CMS hospital facility ID.

Key fields:

| Field | Description |
| --- | --- |
| `facility_id` | CMS hospital identifier. |
| `facility_name` | Hospital name from Hospital General Information. |
| `city_town` | Hospital city or town. |
| `state` | State abbreviation. |
| `zip_code` | ZIP code retained as text. |
| `county_parish` | County or parish. |
| `hospital_type` | CMS hospital type. |
| `hospital_ownership` | CMS ownership category. |
| `emergency_services` | Whether the hospital reports emergency services. |
| `hospital_overall_rating` | Numeric CMS overall hospital rating where available. |
| `overall_rating_group` | Low, middle, or high rating group. |
| `region` | U.S. region derived from state abbreviation. |

### `data/processed/hospital_readmissions_analytic.csv`

Grain: one row per hospital and HRRP condition measure, enriched with hospital attributes.

Use this table for EDA, SQL views, statistical testing, and Power BI modeling.

## Derived Categories

`performance_category`:

| Rule | Category |
| --- | --- |
| ERR < 0.95 | Strong Performer |
| 0.95 <= ERR < 1.00 | Above Expected Performance |
| 1.00 <= ERR < 1.05 | Moderate Concern |
| ERR >= 1.05 | High Concern |

`priority_category`:

| Rule | Category |
| --- | --- |
| Missing ERR or discharges | Missing ERR or Volume |
| Opportunity <= 0 | No Excess Opportunity |
| 0 < Opportunity < 50 | Monitor |
| 50 <= Opportunity < 150 | High |
| Opportunity >= 150 | Critical |
