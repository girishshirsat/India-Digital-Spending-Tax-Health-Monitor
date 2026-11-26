-- Business question: how did UPI amount change from the previous quarter,
-- and do the big drops match the big_drop flag?
SELECT
    state_name,
    year,
    quarter,
    total_amount,
    ROUND(100.0 * (total_amount - LAG(total_amount, 1) OVER w)
          / NULLIF(LAG(total_amount, 1) OVER w, 0), 2) AS upi_qoq_pct,
    big_drop
FROM vw_state_quarter_metrics
WINDOW w AS (PARTITION BY state_name ORDER BY year, quarter)
ORDER BY state_name, year, quarter;