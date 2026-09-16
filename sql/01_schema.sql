DROP VIEW IF EXISTS v_national_summary;
DROP VIEW IF EXISTS v_condition_summary;
DROP VIEW IF EXISTS v_state_summary;
DROP VIEW IF EXISTS v_region_summary;
DROP VIEW IF EXISTS v_ownership_summary;
DROP VIEW IF EXISTS v_rating_summary;
DROP VIEW IF EXISTS v_hospital_summary;
DROP VIEW IF EXISTS v_opportunity_ranking;
DROP VIEW IF EXISTS v_unmatched_hrrp_facilities;

CREATE INDEX IF NOT EXISTS idx_hrrp_clean_facility_measure
ON hrrp_clean (facility_id, measure_name);

CREATE INDEX IF NOT EXISTS idx_hrrp_clean_condition
ON hrrp_clean (condition);

CREATE INDEX IF NOT EXISTS idx_hospital_info_facility
ON hospital_general_info_clean (facility_id);

CREATE INDEX IF NOT EXISTS idx_analytic_facility_condition
ON hospital_readmissions_analytic (facility_id, condition);

CREATE INDEX IF NOT EXISTS idx_analytic_state_condition
ON hospital_readmissions_analytic (state, condition);

CREATE INDEX IF NOT EXISTS idx_analytic_opportunity
ON hospital_readmissions_analytic (positive_opportunity_score);
