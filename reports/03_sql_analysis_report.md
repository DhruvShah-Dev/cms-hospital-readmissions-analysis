# SQL Analysis Layer Report

- SQLite database: `data\processed\readmissions.db`
- Source tables loaded from `data/processed/`.
- Views defined in `sql/02_analysis_views.sql`.

## Loaded Tables

| table_name | rows | columns |
| --- | --- | --- |
| hrrp_clean | 18330 | 28 |
| hospital_general_info_clean | 5419 | 42 |
| hospital_readmissions_analytic | 18330 | 69 |

## National Summary

| hrrp_rows | hospitals_analyzed | conditions_analyzed | avg_err | pct_rows_err_gt_1 | pct_rows_err_ge_1_05 | total_discharges | total_readmissions | excess_estimate_eligible_rows | estimated_excess_readmissions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11720 | 2833 | 6 | 1.0018 | 48.1 | 21.8 | 2335917 | 391809 | 8037 | 12245.5 |

## Condition Summary

| condition | hrrp_rows | hospitals_analyzed | avg_err | avg_readmission_gap | pct_rows_err_gt_1 | total_readmissions | excess_estimate_eligible_rows | estimated_excess_readmissions | excess_readmissions_per_1000_discharges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Heart Failure | 2621 | 2621 | 1.0014 | 0.0346 | 48.9 | 169065 | 2316 | 4856.1 | 5.65 |
| Pneumonia | 2715 | 2715 | 1.0015 | 0.0388 | 46.8 | 131428 | 2320 | 4525.5 | 5.57 |
| Heart Attack | 1736 | 1736 | 1.0018 | 0.0375 | 49.7 | 36231 | 1240 | 1130.5 | 4.21 |
| COPD | 2323 | 2323 | 1.0011 | 0.0254 | 47.2 | 42934 | 1545 | 1071.7 | 4.77 |
| CABG | 878 | 878 | 1.0018 | 0.0248 | 49.9 | 7153 | 363 | 340.9 | 5.23 |
| Hip/Knee Replacement | 1447 | 1447 | 1.004 | 0.0351 | 47.9 | 4998 | 253 | 320.8 | 2.99 |

## Top States By Estimated Excess Readmissions

| state | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | total_readmissions | excess_estimate_eligible_rows | estimated_excess_readmissions | excess_readmissions_per_1000_discharges |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FL | 164 | 1.0229 | 57.5 | 35222 | 598 | 1421.6 | 7.21 |
| CA | 253 | 1.0101 | 55.2 | 33249 | 699 | 1278.6 | 6.72 |
| NY | 124 | 1.0019 | 52.7 | 23521 | 391 | 871.0 | 6.19 |
| MA | 52 | 1.0344 | 62.5 | 15668 | 200 | 812.6 | 8.8 |
| NJ | 61 | 1.0277 | 65.4 | 15078 | 222 | 707.5 | 8.52 |
| IL | 109 | 1.0194 | 57.8 | 20558 | 369 | 704.9 | 6.06 |
| TX | 244 | 1.0043 | 49.6 | 26324 | 585 | 678.1 | 4.31 |
| PA | 126 | 1.0069 | 51.0 | 18208 | 374 | 637.3 | 5.92 |
| OH | 111 | 1.0085 | 52.0 | 15899 | 358 | 479.7 | 5.28 |
| MI | 83 | 1.0054 | 48.1 | 12337 | 246 | 436.4 | 6.44 |
| VA | 69 | 0.9943 | 44.4 | 12509 | 233 | 317.4 | 4.14 |
| IN | 76 | 0.9976 | 45.2 | 10180 | 219 | 301.4 | 5.05 |
| GA | 88 | 1.0114 | 55.8 | 10771 | 244 | 291.6 | 4.77 |
| TN | 71 | 1.0054 | 50.9 | 9281 | 207 | 251.9 | 4.45 |
| KY | 59 | 1.0101 | 54.2 | 7223 | 162 | 244.3 | 6.01 |

## Ownership Summary

| hospital_ownership | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | estimated_excess_readmissions |
| --- | --- | --- | --- | --- |
| Voluntary non-profit - Private | 1404 | 0.999 | 46.5 | 7237.8 |
| Proprietary | 544 | 1.017 | 54.9 | 2162.8 |
| Voluntary non-profit - Church | 195 | 0.9942 | 43.8 | 868.3 |
| Voluntary non-profit - Other | 229 | 0.9987 | 46.0 | 808.6 |
| Government - Hospital District or Authority | 206 | 0.9998 | 47.5 | 597.7 |
| Government - Local | 129 | 1.0026 | 52.8 | 279.6 |
| Government - State | 37 | 1.0008 | 52.1 | 158.5 |
| Missing Hospital Attributes | 15 | 1.0303 | 61.5 | 49.3 |
| Government - Federal | 13 | 1.0032 | 59.0 | 44.2 |
| Physician | 56 | 0.9535 | 37.9 | 38.7 |
| Tribal | 5 | 0.9756 | 30.0 |  |

## Rating Summary

| hospital_overall_rating | overall_rating_group | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | estimated_excess_readmissions |
| --- | --- | --- | --- | --- | --- |
| 1.0 | Low Rating | 169 | 1.0484 | 72.5 | 1193.6 |
| 2.0 | Low Rating | 567 | 1.0249 | 61.1 | 3630.9 |
| 3.0 | Middle Rating | 840 | 1.0061 | 49.9 | 3967.6 |
| 4.0 | Middle Rating | 758 | 0.9856 | 38.8 | 2533.7 |
| 5.0 | High Rating | 287 | 0.9663 | 30.7 | 817.7 |
| Missing Rating | Missing Rating | 212 | 0.9838 | 42.6 | 102.1 |

## Top Hospital Condition Excess-Readmission Priorities

| facility_id | facility_name | state | condition | err | discharges | estimated_excess_readmissions | priority_category | hospital_type | hospital_ownership | hospital_overall_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100007 | ADVENTHEALTH ORLANDO | FL | Heart Failure | 1.1447 | 3487 | 105.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 100007 | ADVENTHEALTH ORLANDO | FL | Pneumonia | 1.1409 | 3588 | 85.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 050030 | OROVILLE HOSPITAL | CA | Pneumonia | 1.4255 | 833 | 60.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | Pneumonia | 1.3011 | 975 | 53.5 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 220100 | SOUTH SHORE HOSPITAL | MA | Pneumonia | 1.1766 | 1883 | 52.1 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 310022 | WEST JERSEY HOSPITAL | NJ | Heart Failure | 1.1999 | 1175 | 45.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 490022 | MARY WASHINGTON HOSPITAL | VA | Pneumonia | 1.238 | 1178 | 45.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Heart Failure | 1.1729 | 1272 | 42.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 330198 | MOUNT SINAI SOUTH NASSAU | NY | Pneumonia | 1.1933 | 1236 | 39.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 230269 | BEAUMONT HOSPITAL, TROY | MI | Heart Failure | 1.1127 | 1649 | 37.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 390115 | JEFFERSON HEALTH- NORTHEAST | PA | Heart Failure | 1.2197 | 839 | 36.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 070025 | HARTFORD HOSPITAL | CT | Heart Failure | 1.1395 | 1305 | 36.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Pneumonia | 1.1412 | 1483 | 34.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 050239 | GLENDALE ADVENTIST MEDICAL CENTER | CA | Pneumonia | 1.1485 | 1336 | 34.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 310086 | JEFFERSON STRATFORD HOSPITAL | NJ | Heart Failure | 1.1389 | 1256 | 34.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 330393 | SUNY/STONY BROOK UNIVERSITY HOSPITAL | NY | Heart Failure | 1.1051 | 1566 | 34.3 | Critical | Acute Care Hospitals | Government - State | 5.0 |
| 210001 | MERITUS MEDICAL CENTER | MD | Pneumonia | 1.2406 | 896 | 33.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 390133 | LEHIGH VALLEY HOSPITAL | PA | Pneumonia | 1.154 | 1329 | 31.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 100075 | ST JOSEPHS HOSPITAL | FL | Heart Failure | 1.1111 | 1386 | 31.5 | Critical | Acute Care Hospitals | Voluntary non-profit - Church | 4.0 |
| 050093 | SAINT AGNES MEDICAL CENTER | CA | Heart Failure | 1.1768 | 916 | 31.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Church | 2.0 |
| 450324 | TEXOMA MEDICAL CENTER | TX | Pneumonia | 1.1744 | 1026 | 31.2 | Critical | Acute Care Hospitals | Proprietary | 4.0 |
| 390231 | JEFFERSON ABINGTON HOSPITAL | PA | Heart Failure | 1.1228 | 1304 | 29.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 220105 | WINCHESTER HOSPITAL | MA | Heart Failure | 1.23 | 685 | 29.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 220090 | MILFORD REGIONAL MEDICAL CENTER | MA | Heart Failure | 1.2135 | 733 | 29.2 | Critical | Acute Care Hospitals | Voluntary non-profit - Other | 4.0 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | Heart Failure | 1.1235 | 1161 | 28.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |

## Unmatched HRRP Facilities

| facility_id | facility_name | state | hrrp_rows | numeric_err_rows |
| --- | --- | --- | --- | --- |
| 010008 | CRENSHAW COMMUNITY HOSPITAL | AL | 6 | 1 |
| 010018 | CALLAHAN EYE HOSPITAL | AL | 6 | 0 |
| 010059 | LAWRENCE MEDICAL CENTER | AL | 6 | 1 |
| 010120 | MONROE COUNTY HOSPITAL | AL | 6 | 2 |
| 040067 | MAGNOLIA REGIONAL MEDICAL HOSPITAL | AR | 6 | 2 |
| 050125 | REGIONAL MEDICAL CENTER OF SAN JOSE | CA | 6 | 5 |
| 050589 | UCI HEALTH - PLACENTIA LINDA | CA | 6 | 2 |
| 070012 | ROCKVILLE GENERAL HOSPITAL | CT | 6 | 0 |
| 100047 | SHOREPOINT HEALTH PUNTA GORDA | FL | 6 | 3 |
| 100092 | ORLANDO HEALTH ROCKLEDGE HOSPITAL | FL | 6 | 5 |
| 240052 | LAKE REGION HEALTHCARE CORPORATION | MN | 6 | 3 |
| 260176 | ST LUKE'S DES PERES HOSPITAL | MO | 6 | 3 |
| 330060 | CARTHAGE AREA HOSPITAL, INC | NY | 6 | 0 |
| 390326 | ST LUKE'S HOSPITAL - ANDERSON CAMPUS | PA | 6 | 4 |
| 390337 | GEISINGER MEDICAL CENTER MUNCY | PA | 6 | 2 |
| 450143 | ASCENSION SETON SMITHVILLE | TX | 6 | 0 |
| 450271 | MEDICAL CITY DECATUR | TX | 6 | 4 |
| 450411 | EASTLAND MEMORIAL HOSPITAL | TX | 6 | 1 |
| 450827 | KELL WEST REGIONAL HOSPITAL | TX | 6 | 1 |
| 520215 | MARSHFIELD MEDICAL CENTER - RIVER REGION | WI | 6 | 0 |