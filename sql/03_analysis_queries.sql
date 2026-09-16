-- National readmissions picture.
SELECT * FROM v_national_summary;

-- Conditions with the largest directional improvement opportunity.
SELECT
    condition,
    hrrp_rows,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    CAST(total_readmissions AS INTEGER) AS total_readmissions,
    ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
FROM v_condition_summary
ORDER BY positive_opportunity_score DESC;

-- States with the highest directional improvement opportunity.
SELECT
    state,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    CAST(total_readmissions AS INTEGER) AS total_readmissions,
    ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
FROM v_state_summary
ORDER BY positive_opportunity_score DESC
LIMIT 15;

-- Hospital ownership comparison.
SELECT
    hospital_ownership,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
FROM v_ownership_summary
ORDER BY avg_err DESC;

-- Overall rating comparison.
SELECT
    hospital_overall_rating,
    overall_rating_group,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    ROUND(positive_opportunity_score, 1) AS positive_opportunity_score
FROM v_rating_summary
ORDER BY hospital_overall_rating;

-- Top hospital-condition opportunities.
SELECT
    facility_id,
    facility_name,
    state,
    condition,
    ROUND(excess_readmission_ratio, 4) AS err,
    CAST(number_of_discharges AS INTEGER) AS discharges,
    ROUND(positive_opportunity_score, 1) AS opportunity_score,
    priority_category,
    hospital_type,
    hospital_ownership,
    hospital_overall_rating
FROM v_opportunity_ranking
ORDER BY positive_opportunity_score DESC
LIMIT 25;
