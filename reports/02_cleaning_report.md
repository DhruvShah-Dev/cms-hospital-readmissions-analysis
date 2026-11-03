# CMS Hospital Readmissions Cleaning Report

## Inputs

- HRRP raw rows: 18,330
- Hospital information raw rows: 5,419
- Raw files were not modified.

## Outputs

| output | rows | columns |
| --- | --- | --- |
| data\processed\hrrp_clean.csv | 18330 | 28 |
| data\processed\hospital_general_info_clean.csv | 5419 | 42 |
| data\processed\hospital_readmissions_analytic.csv | 18330 | 69 |

## Cleaning Rules Applied

- Standardized column names to snake_case.
- Trimmed text fields and converted CMS placeholders to missing values in processed outputs.
- Converted readmission ratios, rates, counts, discharges, ratings, and quality-count fields to numeric values.
- Parsed HRRP measurement dates as dates.
- Added readable condition labels and condition short names.
- Added U.S. Census-style region labels from state abbreviations.
- Created readmission gaps, an estimated excess-readmissions proxy, a legacy sensitivity index, performance categories, and review-priority bands.
- Left joined hospital attributes onto HRRP rows by `facility_id`.

## Validation Checks

- HRRP row count preserved: 18,330 raw rows to 18,330 clean rows.
- Hospital row count preserved: 5,419 raw rows to 5,419 clean rows.
- Analytic row count preserved after left join: 18,330 rows.
- Analytic rows without hospital attributes: 120.
- Numeric ERR rows: 11,720.
- Numeric volume rows: 8,242.
- Excess-readmissions-proxy eligible rows: 8,037 of 18,330 (43.8%).
- `opportunity_eligibility` distinguishes missing rate inputs, missing discharges, both missing, and eligible rows; missing estimates remain blank in exports.
- Positive estimated excess readmissions: 12,245.5.

## Condition Summary

| condition | rows | avg_err | pct_excess | discharges | readmissions | estimated_excess_readmissions | eligible_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Heart Failure | 3055 | 1.0014 | 0.4891 | 858817 | 169065 | 4856.1443 | 2316 |
| Pneumonia | 3055 | 1.0015 | 0.4681 | 811908 | 131428 | 4525.4682 | 2320 |
| Heart Attack | 3055 | 1.0018 | 0.4965 | 268260 | 36231 | 1130.4553 | 1240 |
| COPD | 3055 | 1.0011 | 0.4722 | 224493 | 42934 | 1071.726 | 1545 |
| CABG | 3055 | 1.0018 | 0.4989 | 65148 | 7153 | 340.9224 | 363 |
| Hip/Knee Replacement | 3055 | 1.004 | 0.4789 | 107291 | 4998 | 320.7734 | 253 |

## Priority Category Summary

| priority_category | rows |
| --- | --- |
| Missing ERR or Volume | 10293 |
| No Estimated Excess | 3721 |
| Monitor | 3657 |
| High | 591 |
| Critical | 68 |

## Top Initial Excess-Readmission Priorities

| facility_id | facility_name | state | condition | excess_readmission_ratio | number_of_discharges | positive_estimated_excess_readmissions | hospital_type | hospital_ownership | hospital_overall_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100007 | ADVENTHEALTH ORLANDO | FL | Heart Failure | 1.1447 | 3487 | 105.8 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 100007 | ADVENTHEALTH ORLANDO | FL | Pneumonia | 1.1409 | 3588 | 85.6 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 050030 | OROVILLE HOSPITAL | CA | Pneumonia | 1.4255 | 833 | 60.8 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | Pneumonia | 1.3011 | 975 | 53.5 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 220100 | SOUTH SHORE HOSPITAL | MA | Pneumonia | 1.1766 | 1883 | 52.1 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 310022 | WEST JERSEY HOSPITAL | NJ | Heart Failure | 1.1999 | 1175 | 45.6 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 490022 | MARY WASHINGTON HOSPITAL | VA | Pneumonia | 1.238 | 1178 | 45.4 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Heart Failure | 1.1729 | 1272 | 42.8 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 330198 | MOUNT SINAI SOUTH NASSAU | NY | Pneumonia | 1.1933 | 1236 | 39.8 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 230269 | BEAUMONT HOSPITAL, TROY | MI | Heart Failure | 1.1127 | 1649 | 37.4 | Acute Care Hospitals | Voluntary non-profit - Private | 4 |
| 390115 | JEFFERSON HEALTH- NORTHEAST | PA | Heart Failure | 1.2197 | 839 | 36.6 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 070025 | HARTFORD HOSPITAL | CT | Heart Failure | 1.1395 | 1305 | 36.4 | Acute Care Hospitals | Voluntary non-profit - Private | 4 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Pneumonia | 1.1412 | 1483 | 34.4 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 050239 | GLENDALE ADVENTIST MEDICAL CENTER | CA | Pneumonia | 1.1485 | 1336 | 34.3 | Acute Care Hospitals | Voluntary non-profit - Private | 4 |
| 310086 | JEFFERSON STRATFORD HOSPITAL | NJ | Heart Failure | 1.1389 | 1256 | 34.3 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |

## Notes

- Estimated excess readmissions are a rate-gap prioritization proxy, not a causal estimate of preventable events or financial penalty exposure.
- The legacy `(ERR - 1) * discharges` index is retained only for sensitivity analysis and is not interpreted as a case count.
- Suppressed CMS values remain available as missing values in the processed tables; footnotes should be consulted where suppression matters.
- The 120 analytic rows without hospital attributes should remain in national and condition analysis but be excluded or flagged for ownership, rating, and hospital-type cuts.
