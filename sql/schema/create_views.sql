
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






CREATE OR REPLACE VIEW vw_divergence_scores AS
WITH upi AS (
    SELECT
        state_name,
        year,
        quarter,
        upi_yoy_pct,
        (
            upi_yoy_pct - AVG(upi_yoy_pct) OVER q) / NULLIF(STDDEV_POP(upi_yoy_pct) OVER q, 0) AS upi_z

    FROM (
        SELECT
            state_name,
            year,
            quarter,
            100.0 * (total_amount - LAG(total_amount, 4) OVER w)/ NULLIF(LAG(total_amount, 4) OVER w, 0)AS upi_yoy_pct

        FROM vw_state_quarter_metrics

        WINDOW w AS (
            PARTITION BY state_name
            ORDER BY year, quarter
        )
    ) yoy

    WINDOW q AS (PARTITION BY year, quarter)
),
gst AS (
    SELECT
        state_name,
        year,
        quarter,
        gst_yoy_pct,
        (gst_yoy_pct - AVG(gst_yoy_pct) OVER q) / NULLIF(STDDEV_POP(gst_yoy_pct) OVER q, 0) AS gst_z

    FROM (
        SELECT
            state_name,
            year,
            quarter,
            100.0 * (gstr3b_total_filed - LAG(gstr3b_total_filed, 4) OVER w) / NULLIF(LAG(gstr3b_total_filed, 4) OVER w, 0)AS gst_yoy_pct

        FROM vw_state_quarter_metrics

        WINDOW w AS (
            PARTITION BY state_name
            ORDER BY year, quarter
        )
    ) yoy

    WINDOW q AS (PARTITION BY year, quarter)
)
SELECT
    u.state_name,
    u.year,
    u.quarter,
    ROUND(u.upi_yoy_pct, 2) AS upi_yoy_pct,
    ROUND(g.gst_yoy_pct, 2) AS gst_yoy_pct,
    ROUND(u.upi_z, 2) AS upi_z,
    ROUND(g.gst_z, 2) AS gst_z,
    ROUND(u.upi_z - g.gst_z, 2) AS divergence_score,
    ABS(u.upi_z - g.gst_z) > 1.5 AS flag

FROM upi u
LEFT JOIN gst g
    ON u.state_name = g.state_name
    AND u.year = g.year
    AND u.quarter = g.quarter;
