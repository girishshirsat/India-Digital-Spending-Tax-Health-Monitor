
CREATE OR REPLACE VIEW vw_state_quarter_metrics AS
SELECT
    s.state_name,
    d.year,
    d.quarter,
    u.total_count,
    u.total_amount,
    u.big_drop,
    cp.cpi_yoy,

   
    g1.total_filed AS gstr1_total_filed,
    g1.filing_pct AS gstr1_filing_pct,


    g3.total_filed AS gstr3b_total_filed,
    g3.filing_pct AS gstr3b_filing_pct

FROM fact_upi_state_quarter u

JOIN dim_state s
    ON s.state_id = u.state_id

JOIN dim_date d
    ON d.date_id = u.date_id

LEFT JOIN fact_cpi_state_quarter cp
    ON cp.state_id = u.state_id
    AND cp.date_id = u.date_id

LEFT JOIN fact_gst_state_quarter g1
    ON g1.state_id = u.state_id
    AND g1.date_id = u.date_id
    AND g1.return_type_id = 1

LEFT JOIN fact_gst_state_quarter g3
    ON g3.state_id = u.state_id
    AND g3.date_id = u.date_id
    AND g3.return_type_id = 2;


