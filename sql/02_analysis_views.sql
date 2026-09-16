CREATE VIEW v_national_summary AS
SELECT
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    COUNT(DISTINCT condition) AS conditions_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    SUM(CASE WHEN excess_readmission_ratio > 1 THEN 1 ELSE 0 END) AS rows_err_gt_1,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(CASE WHEN excess_readmission_ratio >= 1.05 THEN 1 ELSE 0 END) AS rows_err_ge_1_05,
    AVG(CASE WHEN excess_readmission_ratio >= 1.05 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_ge_1_05,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL;

CREATE VIEW v_condition_summary AS
SELECT
    condition,
    condition_short,
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    AVG(readmission_gap) AS avg_readmission_gap,
    AVG(readmission_gap_pct) AS avg_readmission_gap_pct,
    SUM(CASE WHEN excess_readmission_ratio > 1 THEN 1 ELSE 0 END) AS rows_err_gt_1,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL
GROUP BY condition, condition_short;

CREATE VIEW v_state_summary AS
SELECT
    state,
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    SUM(CASE WHEN excess_readmission_ratio > 1 THEN 1 ELSE 0 END) AS rows_err_gt_1,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL
GROUP BY state;

CREATE VIEW v_region_summary AS
SELECT
    COALESCE(region, 'Missing Hospital Attributes') AS region,
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL
GROUP BY COALESCE(region, 'Missing Hospital Attributes');

CREATE VIEW v_ownership_summary AS
SELECT
    COALESCE(hospital_ownership, 'Missing Hospital Attributes') AS hospital_ownership,
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL
GROUP BY COALESCE(hospital_ownership, 'Missing Hospital Attributes');

CREATE VIEW v_rating_summary AS
SELECT
    COALESCE(CAST(hospital_overall_rating AS TEXT), 'Missing Rating') AS hospital_overall_rating,
    COALESCE(overall_rating_group, 'Missing Rating') AS overall_rating_group,
    COUNT(*) AS hrrp_rows,
    COUNT(DISTINCT facility_id) AS hospitals_analyzed,
    AVG(excess_readmission_ratio) AS avg_err,
    AVG(CASE WHEN excess_readmission_ratio > 1 THEN 1.0 ELSE 0.0 END) AS pct_rows_err_gt_1,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
WHERE excess_readmission_ratio IS NOT NULL
GROUP BY
    COALESCE(CAST(hospital_overall_rating AS TEXT), 'Missing Rating'),
    COALESCE(overall_rating_group, 'Missing Rating');

CREATE VIEW v_hospital_summary AS
SELECT
    facility_id,
    facility_name,
    state,
    city_town,
    county_parish,
    region,
    hospital_type,
    hospital_ownership,
    hospital_overall_rating,
    COUNT(*) AS condition_rows,
    SUM(CASE WHEN excess_readmission_ratio IS NOT NULL THEN 1 ELSE 0 END) AS numeric_err_rows,
    AVG(excess_readmission_ratio) AS avg_err,
    SUM(CASE WHEN excess_readmission_ratio > 1 THEN 1 ELSE 0 END) AS conditions_err_gt_1,
    SUM(CASE WHEN excess_readmission_ratio >= 1.05 THEN 1 ELSE 0 END) AS conditions_err_ge_1_05,
    SUM(number_of_discharges) AS total_discharges,
    SUM(number_of_readmissions) AS total_readmissions,
    SUM(positive_opportunity_score) AS positive_opportunity_score
FROM hospital_readmissions_analytic
GROUP BY
    facility_id,
    facility_name,
    state,
    city_town,
    county_parish,
    region,
    hospital_type,
    hospital_ownership,
    hospital_overall_rating;

CREATE VIEW v_opportunity_ranking AS
SELECT
    facility_id,
    facility_name,
    state,
    city_town,
    region,
    condition,
    condition_short,
    excess_readmission_ratio,
    predicted_readmission_rate,
    expected_readmission_rate,
    readmission_gap,
    readmission_gap_pct,
    number_of_discharges,
    number_of_readmissions,
    positive_opportunity_score,
    priority_category,
    performance_category,
    hospital_type,
    hospital_ownership,
    hospital_overall_rating
FROM hospital_readmissions_analytic
WHERE positive_opportunity_score > 0;

CREATE VIEW v_unmatched_hrrp_facilities AS
SELECT
    facility_id,
    facility_name,
    state,
    COUNT(*) AS hrrp_rows,
    SUM(CASE WHEN excess_readmission_ratio IS NOT NULL THEN 1 ELSE 0 END) AS numeric_err_rows
FROM hospital_readmissions_analytic
WHERE hospital_type IS NULL
GROUP BY facility_id, facility_name, state;
