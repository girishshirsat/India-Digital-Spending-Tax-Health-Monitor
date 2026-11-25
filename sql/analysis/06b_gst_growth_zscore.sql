-- the YoY growth % of gstr3b_total_filed for each state.

WITH yoy AS (
    SELECT
        state_name,
        year,
        quarter,
        100.0 * (gstr3b_total_filed - LAG(gstr3b_total_filed, 4) OVER w)/ NULLIF(LAG(gstr3b_total_filed, 4) OVER w, 0) AS gst_yoy_pct
    FROM vw_state_quarter_metrics
    WINDOW w AS (PARTITION BY state_name ORDER BY year, quarter)
)
SELECT
    state_name,
    year,
    quarter,
    ROUND(gst_yoy_pct, 2) AS gst_yoy_pct,
    ROUND(
        (gst_yoy_pct - AVG(gst_yoy_pct) OVER q)/ NULLIF(STDDEV_POP(gst_yoy_pct) OVER q, 0),2) AS gst_z
FROM yoy
-- WHERE year = 2024 AND quarter = 4
WINDOW q AS (PARTITION BY year, quarter)
ORDER BY gst_z DESC;