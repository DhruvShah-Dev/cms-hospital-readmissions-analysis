# SQL Analysis Layer Report

- SQLite database: `data\processed\readmissions.db`
- Source tables loaded from `data/processed/`.
- Views defined in `sql/02_analysis_views.sql`.

## Loaded Tables

| table_name | rows | columns |
| --- | --- | --- |
| hrrp_clean | 18330 | 25 |
| hospital_general_info_clean | 5419 | 42 |
| hospital_readmissions_analytic | 18330 | 66 |

## National Summary

| hrrp_rows | hospitals_analyzed | conditions_analyzed | avg_err | pct_rows_err_gt_1 | pct_rows_err_ge_1_05 | total_discharges | total_readmissions | positive_opportunity_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11720 | 2833 | 6 | 1.0018 | 48.1 | 21.8 | 2335917 | 391809 | 76251.4 |

## Condition Summary

| condition | hrrp_rows | hospitals_analyzed | avg_err | avg_readmission_gap | pct_rows_err_gt_1 | total_readmissions | positive_opportunity_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pneumonia | 2715 | 2715 | 1.0015 | 0.0388 | 46.8 | 131428 | 28010.8 |
| Heart Failure | 2621 | 2621 | 1.0014 | 0.0346 | 48.9 | 169065 | 24620.8 |
| Heart Attack | 1736 | 1736 | 1.0018 | 0.0375 | 49.7 | 36231 | 8369.2 |
| Hip/Knee Replacement | 1447 | 1447 | 1.004 | 0.0351 | 47.9 | 4998 | 6226.3 |
| COPD | 2323 | 2323 | 1.0011 | 0.0254 | 47.2 | 42934 | 5839.3 |
| CABG | 878 | 878 | 1.0018 | 0.0248 | 49.9 | 7153 | 3185.0 |

## Top States By Opportunity

| state | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | total_readmissions | positive_opportunity_score |
| --- | --- | --- | --- | --- | --- |
| FL | 164 | 1.0229 | 57.5 | 35222 | 8737.0 |
| CA | 253 | 1.0101 | 55.2 | 33249 | 7433.9 |
| MA | 52 | 1.0344 | 62.5 | 15668 | 5377.0 |
| NY | 124 | 1.0019 | 52.7 | 23521 | 5078.6 |
| IL | 109 | 1.0194 | 57.8 | 20558 | 4530.7 |
| PA | 126 | 1.0069 | 51.0 | 18208 | 4380.1 |
| NJ | 61 | 1.0277 | 65.4 | 15078 | 4222.4 |
| TX | 244 | 1.0043 | 49.6 | 26324 | 4203.1 |
| OH | 111 | 1.0085 | 52.0 | 15899 | 2812.4 |
| MI | 83 | 1.0054 | 48.1 | 12337 | 2428.4 |
| VA | 69 | 0.9943 | 44.4 | 12509 | 1911.9 |
| GA | 88 | 1.0114 | 55.8 | 10771 | 1780.2 |
| IN | 76 | 0.9976 | 45.2 | 10180 | 1712.1 |
| TN | 71 | 1.0054 | 50.9 | 9281 | 1676.1 |
| KY | 59 | 1.0101 | 54.2 | 7223 | 1531.4 |

## Ownership Summary

| hospital_ownership | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | positive_opportunity_score |
| --- | --- | --- | --- | --- |
| Voluntary non-profit - Private | 1404 | 0.999 | 46.5 | 44865.8 |
| Proprietary | 544 | 1.017 | 54.9 | 13842.3 |
| Voluntary non-profit - Church | 195 | 0.9942 | 43.8 | 5425.0 |
| Voluntary non-profit - Other | 229 | 0.9987 | 46.0 | 4930.3 |
| Government - Hospital District or Authority | 206 | 0.9998 | 47.5 | 3540.1 |
| Government - Local | 129 | 1.0026 | 52.8 | 1719.4 |
| Government - State | 37 | 1.0008 | 52.1 | 948.7 |
| Physician | 56 | 0.9535 | 37.9 | 396.9 |
| Missing Hospital Attributes | 15 | 1.0303 | 61.5 | 323.4 |
| Government - Federal | 13 | 1.0032 | 59.0 | 259.5 |
| Tribal | 5 | 0.9756 | 30.0 |  |

## Rating Summary

| hospital_overall_rating | overall_rating_group | hospitals_analyzed | avg_err | pct_rows_err_gt_1 | positive_opportunity_score |
| --- | --- | --- | --- | --- | --- |
| 1.0 | Low Rating | 169 | 1.0484 | 72.5 | 7449.0 |
| 2.0 | Low Rating | 567 | 1.0249 | 61.1 | 22068.1 |
| 3.0 | Middle Rating | 840 | 1.0061 | 49.9 | 24906.7 |
| 4.0 | Middle Rating | 758 | 0.9856 | 38.8 | 15847.6 |
| 5.0 | High Rating | 287 | 0.9663 | 30.7 | 5028.1 |
| Missing Rating | Missing Rating | 212 | 0.9838 | 42.6 | 951.9 |

## Top Hospital Condition Opportunities

| facility_id | facility_name | state | condition | err | discharges | opportunity_score | priority_category | hospital_type | hospital_ownership | hospital_overall_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100007 | ADVENTHEALTH ORLANDO | FL | Pneumonia | 1.1409 | 3588 | 505.5 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 100007 | ADVENTHEALTH ORLANDO | FL | Heart Failure | 1.1447 | 3487 | 504.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 050030 | OROVILLE HOSPITAL | CA | Pneumonia | 1.4255 | 833 | 354.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 220100 | SOUTH SHORE HOSPITAL | MA | Pneumonia | 1.1766 | 1883 | 332.5 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 330194 | MAIMONIDES MEDICAL CENTER | NY | Pneumonia | 1.3011 | 975 | 293.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 490022 | MARY WASHINGTON HOSPITAL | VA | Pneumonia | 1.238 | 1178 | 280.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 100260 | ST LUCIE MEDICAL CENTER | FL | Hip/Knee Replacement | 1.3249 | 806 | 261.9 | Critical | Acute Care Hospitals | Proprietary | 1.0 |
| 330198 | MOUNT SINAI SOUTH NASSAU | NY | Pneumonia | 1.1933 | 1236 | 238.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 310022 | WEST JERSEY HOSPITAL | NJ | Heart Failure | 1.1999 | 1175 | 234.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Heart Failure | 1.1729 | 1272 | 219.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 210001 | MERITUS MEDICAL CENTER | MD | Pneumonia | 1.2406 | 896 | 215.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 310041 | COMMUNITY MEDICAL CENTER | NJ | Pneumonia | 1.1412 | 1483 | 209.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 1.0 |
| 390133 | LEHIGH VALLEY HOSPITAL | PA | Pneumonia | 1.154 | 1329 | 204.7 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 220077 | BAYSTATE MEDICAL CENTER | MA | Heart Attack | 1.1792 | 1124 | 201.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 050239 | GLENDALE ADVENTIST MEDICAL CENTER | CA | Pneumonia | 1.1485 | 1336 | 198.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 230269 | BEAUMONT HOSPITAL, TROY | MI | Heart Failure | 1.1127 | 1649 | 185.8 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 390133 | LEHIGH VALLEY HOSPITAL | PA | Hip/Knee Replacement | 1.2876 | 641 | 184.4 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 390115 | JEFFERSON HEALTH- NORTHEAST | PA | Heart Failure | 1.2197 | 839 | 184.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 070025 | HARTFORD HOSPITAL | CT | Heart Failure | 1.1395 | 1305 | 182.0 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 4.0 |
| 450324 | TEXOMA MEDICAL CENTER | TX | Pneumonia | 1.1744 | 1026 | 178.9 | Critical | Acute Care Hospitals | Proprietary | 4.0 |
| 310086 | JEFFERSON STRATFORD HOSPITAL | NJ | Heart Failure | 1.1389 | 1256 | 174.5 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |
| 310022 | WEST JERSEY HOSPITAL | NJ | Pneumonia | 1.1371 | 1271 | 174.3 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 140127 | CARLE BROMENN MEDICAL CENTER | IL | Hip/Knee Replacement | 1.5827 | 292 | 170.1 | Critical | Acute Care Hospitals | Voluntary non-profit - Church | 3.0 |
| 050039 | ENLOE HEALTH | CA | Pneumonia | 1.1497 | 1128 | 168.9 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 3.0 |
| 220077 | BAYSTATE MEDICAL CENTER | MA | Pneumonia | 1.1764 | 939 | 165.6 | Critical | Acute Care Hospitals | Voluntary non-profit - Private | 2.0 |

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