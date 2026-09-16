# CMS Hospital Readmissions Data Profile

## Dataset And Grain Summary

- HRRP raw file: `data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- Hospital general information raw file: `data\raw\Hospital_General_Information.csv`
- HRRP shape: 18,330 rows x 12 columns
- Hospital information shape: 5,419 rows x 38 columns
- Expected HRRP grain: one hospital-condition measure row per `Facility ID` + `Measure Name`.
- Expected hospital information grain: one hospital row per `Facility ID`.

## Checks Performed

- Schema and column count checks
- Missing-like values, including CMS text placeholders
- Exact duplicate rows and candidate key uniqueness
- Numeric cast validity for readmission measures and volumes
- Date parsing and measurement-period consistency
- Join integrity from HRRP to Hospital General Information on `Facility ID`
- Initial condition, rating, ownership, and opportunity summaries

## Key Results

- HRRP exact duplicate rows: 0
- HRRP duplicate `Facility ID` + `Measure Name` rows: 0
- Hospital exact duplicate rows: 0
- Hospital duplicate `Facility ID` rows: 0
- HRRP facility IDs absent from hospital information: 20 affecting 120 HRRP rows
- Joined row count: 18,330 versus HRRP row count 18,330
- HRRP rows with numeric ERR: 11,720 (63.9%)
- HRRP rows with ERR > 1.0: 5,643 (48.1% of numeric ERR rows)
- HRRP rows with ERR > 1.05: 2,546 (21.7% of numeric ERR rows)
- Total numeric reported readmissions: 391,809

## Measurement Periods

| start_date | end_date | rows |
| --- | --- | --- |
| 2021-07-01 | 2024-06-30 | 18330 |

## HRRP Numeric Profile

| column | valid_numeric | min | median | mean | max |
| --- | --- | --- | --- | --- | --- |
| Number of Discharges | 8242 | 0.0 | 198.0 | 283.4163 | 3672.0 |
| Excess Readmission Ratio | 11720 | 0.4698 | 0.9973 | 1.0018 | 1.6297 |
| Predicted Readmission Rate | 11720 | 1.908 | 15.8602 | 14.9815 | 28.1643 |
| Expected Readmission Rate | 11720 | 3.0876 | 15.8565 | 14.948 | 26.8654 |
| Number of Readmissions | 8037 | 11.0 | 31.0 | 48.7507 | 847.0 |

## HRRP Missing-Like Profile

| column | missing_like_count | missing_like_rate | distinct_count |
| --- | --- | --- | --- |
| Footnote | 11343 | 0.6188 | 4 |
| Number of Readmissions | 10293 | 0.5615 | 290 |
| Number of Discharges | 10088 | 0.5504 | 1044 |
| Excess Readmission Ratio | 6610 | 0.3606 | 3252 |
| Predicted Readmission Rate | 6610 | 0.3606 | 11260 |
| Expected Readmission Rate | 6610 | 0.3606 | 11229 |
| Facility ID | 0 | 0.0 | 3055 |
| Facility Name | 0 | 0.0 | 2995 |
| Measure Name | 0 | 0.0 | 6 |
| State | 0 | 0.0 | 51 |
| Start Date | 0 | 0.0 | 1 |
| End Date | 0 | 0.0 | 1 |

## Hospital Information Missing-Like Profile

| column | missing_like_count | missing_like_rate | distinct_count |
| --- | --- | --- | --- |
| TE Group Footnote | 4411 | 0.814 | 5 |
| READM Group Footnote | 4196 | 0.7743 | 5 |
| MORT Group Footnote | 4023 | 0.7424 | 5 |
| Pt Exp Group Footnote | 3403 | 0.628 | 4 |
| Safety Group Footnote | 3270 | 0.6034 | 6 |
| Meets criteria for birthing friendly designation | 3156 | 0.5824 | 1 |
| Hospital overall rating footnote | 3103 | 0.5726 | 8 |
| Hospital overall rating | 2245 | 0.4143 | 6 |
| Count of Facility Safety Measures | 2075 | 0.3829 | 9 |
| Count of Safety Measures Worse | 2075 | 0.3829 | 5 |
| Count of Safety Measures Better | 2075 | 0.3829 | 8 |
| Count of Safety Measures No Different | 2075 | 0.3829 | 10 |
| Count of Facility Pt Exp Measures | 1955 | 0.3608 | 4 |
| Count of Facility MORT Measures | 1323 | 0.2441 | 9 |
| Count of MORT Measures No Different | 1323 | 0.2441 | 10 |
| Count of MORT Measures Worse | 1323 | 0.2441 | 7 |
| Count of MORT Measures Better | 1323 | 0.2441 | 10 |
| Count of READM Measures Worse | 1155 | 0.2131 | 9 |
| Count of Facility READM Measures | 1155 | 0.2131 | 12 |
| Count of READM Measures No Different | 1155 | 0.2131 | 13 |

## Condition Summary

| measure | rows | avg_err | median_err | pct_err_gt_1 | total_discharges | total_readmissions | positive_opportunity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| READM-30-PN-HRRP | 3055 | 1.0015 | 0.9955 | 0.4681 | 811908 | 131428 | 28010.7996 |
| READM-30-HF-HRRP | 3055 | 1.0014 | 0.9983 | 0.4891 | 858817 | 169065 | 24620.8364 |
| READM-30-AMI-HRRP | 3055 | 1.0018 | 0.9994 | 0.4965 | 268260 | 36231 | 8369.2051 |
| READM-30-HIP-KNEE-HRRP | 3055 | 1.004 | 0.9916 | 0.4789 | 107291 | 4998 | 6226.3432 |
| READM-30-COPD-HRRP | 3055 | 1.0011 | 0.9969 | 0.4722 | 224493 | 42934 | 5839.2638 |
| READM-30-CABG-HRRP | 3055 | 1.0018 | 1.0 | 0.4989 | 65148 | 7153 | 3184.9574 |

## Hospital Ratings

| rating | hospitals |
| --- | --- |
| 1 | 198 |
| 2 | 661 |
| 3 | 985 |
| 4 | 946 |
| 5 | 384 |
| Not Available | 2245 |

## Hospital Ownership

| ownership | hospitals |
| --- | --- |
| Voluntary non-profit - Private | 2322 |
| Proprietary | 1063 |
| Government - Hospital District or Authority | 512 |
| Government - Local | 393 |
| Voluntary non-profit - Other | 353 |
| Voluntary non-profit - Church | 264 |
| Government - State | 209 |
| Veterans Health Administration | 132 |
| Physician | 80 |
| Government - Federal | 42 |
| Department of Defense | 32 |
| Tribal | 17 |

## Top Initial Readmission Improvement Opportunities

Opportunity is calculated only for rows with numeric ERR and numeric discharges as `(ERR - 1) * discharges`; negative values are excluded from this first prioritization view.

| Facility ID | Facility Name | State | Measure Name | ERR | Discharges | Opportunity |
| --- | --- | --- | --- | --- | --- | --- |
| 100007 | ADVENTHEALTH ORLANDO | FL | READM-30-PN-HRRP | 1.1409 | 3588 | 505.5 |
| 100007 | ADVENTHEALTH ORLANDO | FL | READM-30-HF-HRRP | 1.1447 | 3487 | 504.6 |
| 050030 | OROVILLE HOSPITAL | CA | READM-30-PN-HRRP | 1.4255 | 833 | 354.4 |
| 220100 | SOUTH SHORE HOSPITAL | MA | READM-30-PN-HRRP | 1.1766 | 1883 | 332.5 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | READM-30-PN-HRRP | 1.3011 | 975 | 293.6 |
| 490022 | MARY WASHINGTON HOSPITAL | VA | READM-30-PN-HRRP | 1.238 | 1178 | 280.4 |
| 100260 | ST LUCIE MEDICAL CENTER | FL | READM-30-HIP-KNEE-HRRP | 1.3249 | 806 | 261.9 |
| 330198 | MOUNT SINAI SOUTH NASSAU | NY | READM-30-PN-HRRP | 1.1933 | 1236 | 238.9 |
| 310022 | WEST JERSEY HOSPITAL | NJ | READM-30-HF-HRRP | 1.1999 | 1175 | 234.9 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | READM-30-HF-HRRP | 1.1729 | 1272 | 219.9 |
| 210001 | MERITUS MEDICAL CENTER | MD | READM-30-PN-HRRP | 1.2406 | 896 | 215.6 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | READM-30-PN-HRRP | 1.1412 | 1483 | 209.4 |
| 390133 | LEHIGH VALLEY HOSPITAL | PA | READM-30-PN-HRRP | 1.154 | 1329 | 204.7 |
| 220077 | BAYSTATE MEDICAL CENTER | MA | READM-30-AMI-HRRP | 1.1792 | 1124 | 201.4 |
| 050239 | GLENDALE ADVENTIST MEDICAL CENTER | CA | READM-30-PN-HRRP | 1.1485 | 1336 | 198.4 |

## Findings

- No duplicate rows or duplicate candidate keys were found at the expected dataset grains. Severity: low; confidence: high.
- HRRP has 20 facility IDs (120 rows) with no matching Hospital General Information record. This does not create row loss in a left join, but those rows will lack ownership, type, rating, and address fields. Severity: medium; confidence: high.
- The HRRP-to-hospital join does not expand rows, because Hospital General Information has unique `Facility ID` values. Severity: low; confidence: high.
- Several HRRP volume fields contain expected CMS suppression text such as `Too Few to Report`, so volume-based metrics should use numeric casting with documented exclusions. Severity: medium; confidence: high.
- The CMS footnote and group footnote columns are intentionally sparse. These columns should be retained for transparency but not treated as analysis measures. Severity: low; confidence: high.

## Recommended Next Steps

- Create cleaned, analysis-ready tables that preserve raw files and convert rates, volumes, dates, and placeholder values explicitly.
- Add a condition label field that maps CMS measure codes to business-readable names.
- Build SQL tables/views at hospital-condition, hospital, state-condition, and opportunity-ranking grains.
- Validate opportunity-score variants before using them in executive recommendations.
- Add automated checks for candidate key uniqueness, join coverage, numeric cast rates, and expected measurement-period consistency.

## Assumptions And Open Questions

- Assumption: the first analytical grain is HRRP hospital-condition measure rows.
- Assumption: `Too Few to Report` is an expected CMS suppression value, not a data ingestion defect.
- Open question: should opportunity ranking emphasize excess cases, financial penalty risk, patient volume, or a blended score?
