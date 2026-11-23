-- Business question: how fast is the number of GSTR-3B returns filed growing
-- in a state compared with the same quarter last year?
WITH lagged AS (
    SELECT
        state_name,
        year,
        quarter,
        gstr3b_total_filed,
        LAG(gstr3b_total_filed, 4) OVER (
            PARTITION BY state_name ORDER BY year, quarter
        ) AS filed_last_year
    FROM vw_state_quarter_metrics
)
SELECT
    state_name,
    year,
    quarter,
    gstr3b_total_filed,
    filed_last_year,
    ROUND(
        100.0 * (gstr3b_total_filed - filed_last_year) / NULLIF(filed_last_year, 0),
        2
    ) AS gst_filed_yoy_pct
FROM lagged
ORDER BY state_name, year, quarter;