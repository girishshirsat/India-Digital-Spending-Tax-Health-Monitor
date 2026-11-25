-- Business question: which states grew UPI amount much faster or slower
-- than other states in the same quarter?

WITH yoy AS (
    SELECT
        state_name,
        year,
        quarter,
        100.0 * (total_amount - LAG(total_amount, 4) OVER w)
            / NULLIF(LAG(total_amount, 4) OVER w, 0) AS upi_yoy_pct
    FROM vw_state_quarter_metrics
    WINDOW w AS (PARTITION BY state_name ORDER BY year, quarter)
)
SELECT
    state_name,
    year,
    quarter,
    ROUND(upi_yoy_pct, 2) AS upi_yoy_pct,
    ROUND(
        (upi_yoy_pct - AVG(upi_yoy_pct) OVER q)
        / NULLIF(STDDEV_POP(upi_yoy_pct) OVER q, 0),
        2
    ) AS upi_z
FROM yoy
-- WHERE year = 2024 AND quarter = 4
WINDOW q AS (PARTITION BY year, quarter)
ORDER BY upi_z DESC;