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
| `estimated_excess_readmissions` | `(predicted_readmission_rate - expected_readmission_rate) * number_of_discharges / 100` where all inputs are numeric. A prioritization proxy, not an estimate of preventable cases. |
| `positive_estimated_excess_readmissions` | Estimated excess readmissions floored at 0 for burden ranking. Missing estimates remain missing. |
| `legacy_opportunity_index` | Former `(ERR - 1) * number_of_discharges` index retained only for sensitivity analysis; it is dimensionless and not a case count. |
| `positive_legacy_opportunity_index` | Legacy index floored at 0. |
| `opportunity_eligibility` | Explains whether ERR and discharge inputs are available; suppressed rows remain distinct from measured zero. |
| `priority_category` | Operational review band based on estimated excess readmissions; not a CMS designation. |

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
| Missing rate inputs or discharges | Missing ERR or Volume |
| Estimated excess <= 0 | No Estimated Excess |
| 0 < Estimated excess < 5 | Monitor |
| 5 <= Estimated excess < 20 | High |
| Estimated excess >= 20 | Critical |

The priority thresholds are transparent triage heuristics for this case study. They do not represent CMS policy, financial penalties, causal effects, or preventable readmissions.
