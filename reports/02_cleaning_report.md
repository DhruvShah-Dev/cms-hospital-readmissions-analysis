# CMS Hospital Readmissions Cleaning Report

## Inputs

- HRRP raw rows: 18,330
- Hospital information raw rows: 5,419
- Raw files were not modified.

## Outputs

| output | rows | columns |
| --- | --- | --- |
| data\processed\hrrp_clean.csv | 18330 | 25 |
| data\processed\hospital_general_info_clean.csv | 5419 | 42 |
| data\processed\hospital_readmissions_analytic.csv | 18330 | 66 |

## Cleaning Rules Applied

- Standardized column names to snake_case.
- Trimmed text fields and converted CMS placeholders to missing values in processed outputs.
- Converted readmission ratios, rates, counts, discharges, ratings, and quality-count fields to numeric values.
- Parsed HRRP measurement dates as dates.
- Added readable condition labels and condition short names.
- Added U.S. Census-style region labels from state abbreviations.
- Created readmission gap, gap percent, excess-readmission flags, performance categories, and opportunity scores.
- Left joined hospital attributes onto HRRP rows by `facility_id`.

## Validation Checks

- HRRP row count preserved: 18,330 raw rows to 18,330 clean rows.
- Hospital row count preserved: 5,419 raw rows to 5,419 clean rows.
- Analytic row count preserved after left join: 18,330 rows.
- Analytic rows without hospital attributes: 120.
- Numeric ERR rows: 11,720.
- Numeric volume rows: 8,242.
- Positive opportunity score total: 76,251.4.

## Condition Summary

| condition | rows | avg_err | pct_excess | discharges | readmissions | positive_opportunity |
| --- | --- | --- | --- | --- | --- | --- |
| Pneumonia | 3055 | 1.0015 | 0.4681 | 811908 | 131428 | 28010.7996 |
| Heart Failure | 3055 | 1.0014 | 0.4891 | 858817 | 169065 | 24620.8364 |
| Heart Attack | 3055 | 1.0018 | 0.4965 | 268260 | 36231 | 8369.2051 |
| Hip/Knee Replacement | 3055 | 1.004 | 0.4789 | 107291 | 4998 | 6226.3432 |
| COPD | 3055 | 1.0011 | 0.4722 | 224493 | 42934 | 5839.2638 |
| CABG | 3055 | 1.0018 | 0.4989 | 65148 | 7153 | 3184.9574 |

## Priority Category Summary

| priority_category | rows |
| --- | --- |
| Missing ERR or Volume | 10293 |
| Monitor | 3978 |
| No Excess Opportunity | 3722 |
| High | 301 |
| Critical | 36 |

## Top Initial Opportunity Rows

| facility_id | facility_name | state | condition | excess_readmission_ratio | number_of_discharges | positive_opportunity_score | hospital_type | hospital_ownership | hospital_overall_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100007 | ADVENTHEALTH ORLANDO | FL | Pneumonia | 1.1409 | 3588 | 505.5 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 100007 | ADVENTHEALTH ORLANDO | FL | Heart Failure | 1.1447 | 3487 | 504.6 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 050030 | OROVILLE HOSPITAL | CA | Pneumonia | 1.4255 | 833 | 354.4 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 220100 | SOUTH SHORE HOSPITAL | MA | Pneumonia | 1.1766 | 1883 | 332.5 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | Pneumonia | 1.3011 | 975 | 293.6 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 490022 | MARY WASHINGTON HOSPITAL | VA | Pneumonia | 1.238 | 1178 | 280.4 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 100260 | ST LUCIE MEDICAL CENTER | FL | Hip/Knee Replacement | 1.3249 | 806 | 261.9 | Acute Care Hospitals | Proprietary | 1 |
| 330198 | MOUNT SINAI SOUTH NASSAU | NY | Pneumonia | 1.1933 | 1236 | 238.9 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 310022 | WEST JERSEY HOSPITAL | NJ | Heart Failure | 1.1999 | 1175 | 234.9 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Heart Failure | 1.1729 | 1272 | 219.9 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 210001 | MERITUS MEDICAL CENTER | MD | Pneumonia | 1.2406 | 896 | 215.6 | Acute Care Hospitals | Voluntary non-profit - Private | 3 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Pneumonia | 1.1412 | 1483 | 209.4 | Acute Care Hospitals | Voluntary non-profit - Private | 1 |
| 390133 | LEHIGH VALLEY HOSPITAL | PA | Pneumonia | 1.154 | 1329 | 204.7 | Acute Care Hospitals | Voluntary non-profit - Private | 4 |
| 220077 | BAYSTATE MEDICAL CENTER | MA | Heart Attack | 1.1792 | 1124 | 201.4 | Acute Care Hospitals | Voluntary non-profit - Private | 2 |
| 050239 | GLENDALE ADVENTIST MEDICAL CENTER | CA | Pneumonia | 1.1485 | 1336 | 198.4 | Acute Care Hospitals | Voluntary non-profit - Private | 4 |

## Notes

- The opportunity score is directional and should be validated before being used as a formal intervention priority metric.
- Suppressed CMS values remain available as missing values in the processed tables; footnotes should be consulted where suppression matters.
- The 120 analytic rows without hospital attributes should remain in national and condition analysis but be excluded or flagged for ownership, rating, and hospital-type cuts.
