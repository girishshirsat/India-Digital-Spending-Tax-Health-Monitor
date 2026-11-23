CREATE OR REPLACE VIEW vw_state_quarter_metrics AS
SELECT
    s.state_name,
    d.year,
    d.quarter,
    u.total_count,
    u.total_amount,
    u.big_drop,
    cp.cpi_yoy

FROM fact_upi_state_quarter u

JOIN dim_state s
    ON s.state_id = u.state_id

JOIN dim_date d
    ON d.date_id = u.date_id

LEFT JOIN fact_cpi_state_quarter cp
    ON cp.state_id = u.state_id
    AND cp.date_id = u.date_id;


