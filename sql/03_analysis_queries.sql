-- National readmissions picture.
SELECT * FROM v_national_summary;

-- Conditions with the largest estimated excess-readmission burden.
SELECT
    condition,
    hrrp_rows,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    CAST(total_readmissions AS INTEGER) AS total_readmissions,
    excess_estimate_eligible_rows,
    ROUND(estimated_excess_readmissions, 1) AS estimated_excess_readmissions,
    ROUND(excess_readmissions_per_1000_discharges, 2) AS excess_readmissions_per_1000_discharges
FROM v_condition_summary
ORDER BY estimated_excess_readmissions DESC;

-- States with the largest total and normalized estimated excess burden.
SELECT
    state,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    CAST(total_readmissions AS INTEGER) AS total_readmissions,
    excess_estimate_eligible_rows,
    ROUND(estimated_excess_readmissions, 1) AS estimated_excess_readmissions,
    ROUND(excess_readmissions_per_1000_discharges, 2) AS excess_readmissions_per_1000_discharges
FROM v_state_summary
ORDER BY estimated_excess_readmissions DESC
LIMIT 15;

-- Hospital ownership comparison.
SELECT
    hospital_ownership,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    ROUND(estimated_excess_readmissions, 1) AS estimated_excess_readmissions
FROM v_ownership_summary
ORDER BY avg_err DESC;

-- Overall rating comparison.
SELECT
    hospital_overall_rating,
    overall_rating_group,
    hospitals_analyzed,
    ROUND(avg_err, 4) AS avg_err,
    ROUND(pct_rows_err_gt_1 * 100, 1) AS pct_rows_err_gt_1,
    ROUND(estimated_excess_readmissions, 1) AS estimated_excess_readmissions
FROM v_rating_summary
ORDER BY hospital_overall_rating;

-- Top hospital-condition excess-readmission priorities.
SELECT
    facility_id,
    facility_name,
    state,
    condition,
    ROUND(excess_readmission_ratio, 4) AS err,
    CAST(number_of_discharges AS INTEGER) AS discharges,
    ROUND(positive_estimated_excess_readmissions, 1) AS estimated_excess_readmissions,
    priority_category,
    hospital_type,
    hospital_ownership,
    hospital_overall_rating
FROM v_opportunity_ranking
ORDER BY positive_estimated_excess_readmissions DESC
LIMIT 25;
